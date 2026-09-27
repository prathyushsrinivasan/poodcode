# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 37 - The JVM: class loading, memory and garbage collection.
# Closes Part 13, and the course.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# THE JUDGING PROBLEM: much of what the JVM does is deliberately unobservable.
# When the garbage collector runs, what the JIT compiles, how deep the stack
# may go - none of it is specified, and a program whose output depended on it
# would pass on one machine and fail on the next. So every exercise here is
# built on behaviour the JLS or the JVM specification FIXES:
#
#   37.1 class initialisation ORDER (JLS 12.4, 12.5) - printed from static
#        blocks, instance initialisers and constructors
#   37.2 the stack - a StackOverflowError is caught or avoided, never
#        measured; stack traces list frames in call order
#   37.3 strings and boxing - the String pool and constant folding (JLS
#        3.10.5, 15.29), the Integer cache (JLS 5.1.7), unboxing null
#   37.4 garbage collection - SIMULATED: mark-and-sweep and reference counting
#        run as algorithms over an object graph read from stdin, plus the one
#        leak you can fix deterministically, an unbounded cache
#   37.5 bytecode - the JVM as a stack machine, as an interpreter you write
#
# The one exercise that relies on a StackOverflowError happening (j37-st-deep)
# recurses three million frames deep, which overflows every default thread
# stack by an order of magnitude.
# ---------------------------------------------------------------------------

_M37 = []

_IMPORTS37 = ("import java.util.*;\n"
              "import java.util.function.*;\n")


def _j37t(types, body, helpers=""):
    return _jp(
        _IMPORTS37 + "\n"
        + (types.strip("\n") + "\n\n" if types.strip() else "")
        + "public class Main {\n"
        + (helpers.rstrip("\n") + "\n\n" if helpers.strip() else "")
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }\n}"
    )


def _toks37(ts, out):
    return _case("\n".join([str(len(ts)), " ".join(ts)]), out)


def _rows37(rows, out):
    stdin = "\n".join([str(len(rows))] + [" ".join(str(t) for t in r) for r in rows])
    return _case(stdin, out)


# ===========================================================================
# 37.1 Class loading and initialisation
# ===========================================================================

_ORDER37 = """
class Parent {
    static {
        System.out.println("static Parent");
    }

    {
        System.out.println("init Parent");
    }

    Parent() {
        System.out.println("ctor Parent");
    }
}

class Child extends Parent {
    static {
        System.out.println("static Child");
    }

    {
        System.out.println("init Child");
    }

    Child() {
        System.out.println("ctor Child");
    }
}
"""


def _order_out37(k):
    lines = ["main starts"]
    for i in range(k):
        if i == 0:
            lines += ["static Parent", "static Child"]
        lines += ["init Parent", "ctor Parent", "init Child", "ctor Child"]
    lines.append("main ends")
    return _nl(*lines)


_BASE37 = """
abstract class Widget {
    Widget() {
        System.out.println("building");
    }

    abstract String describe();

    static <T extends Widget> T announce(T w) {
        System.out.println("created " + w.describe());
        return w;
    }
}

class Button extends Widget {
    private final String label;

    Button(String label) {
        this.label = label;
    }

    String describe() {
        return "button " + label;
    }
}
"""
_BASE_BUGGY37 = _BASE37.replace(
    "    Widget() {\n        System.out.println(\"building\");\n    }",
    "    Widget() {\n        System.out.println(\"building\");\n"
    "        System.out.println(\"created \" + describe());\n    }")
_LABELS37 = (["ok"], ["save", "load"], ["x"], ["yes", "no", "maybe"], ["go"])


def _widget_out37(ls):
    out = []
    for l in ls:
        out += ["building", f"created button {l}"]
    return _nl(*out)


_LIMITS37 = """
class Limits {
    static final int MAX = 10;

    static {
        System.out.println("init Limits");
    }

    static int twice() {
        return MAX * 2;
    }
}
"""
_KS37 = (1, 3, 0, 7, 10)


def _limits_out37(k):
    return _nl(f"max {10 * k}", "init Limits", f"twice {20 * k}")


_CHAIN37 = """
class Engine {
    static int built;

    static {
        System.out.println("load Engine");
    }

    Engine() {
        built++;
        System.out.println("engine " + built);
    }
}

class Car {
    static {
        System.out.println("load Car");
    }

    private final Engine engine = new Engine();

    Car() {
        System.out.println("car ready");
    }
}
"""
_CHAIN_REGION37 = _CHAIN37.strip("\n")


def _chain_out37(k):
    lines = ["start"]
    for i in range(1, k + 1):
        if i == 1:
            lines.append("load Car")
        if i == 1:
            lines.append("load Engine")
        lines += [f"engine {i}", "car ready"]
    lines.append(f"built {k}")
    return _nl(*lines)


_M37.append(_jlesson(
    "m37-loading", "Class loading and initialisation order",
    "When a class is loaded, when it is initialised, and the exact order every "
    "initialiser runs in.",
    """
A Java program does not start with all its classes in memory. The JVM **loads**
a class (finds its bytecode, through a *class loader*) the first time it is
needed, **links** it (verifies the bytecode, prepares its static fields with
default values), and **initialises** it - runs its static initialisers - on its
**first active use**: creating an instance, calling a static method, or reading
or writing a static field.

Module 35's holder idiom leaned on exactly this. Here is the whole of it.

## The order, fixed by the language specification

For `new Child()`, where `Child extends Parent`, the first time:

1. **static initialisers of `Parent`**, then of `Child` - a class's superclass is
   always initialised first. (Static fields and `static { }` blocks run top to
   bottom, in source order.)
2. then, for this object: `Parent`'s **instance initialisers** (field
   initialisers and `{ }` blocks, in source order), then `Parent`'s
   **constructor body**;
3. then `Child`'s instance initialisers, then `Child`'s constructor body.

The static step happens **once per class**. Every later `new Child()` repeats
only steps 2 and 3.

Step 2 happens because every constructor begins with a call to `super(...)` -
written or implied - and field initialisers run just after that call returns.

## Two consequences worth knowing

**A compile-time constant does not initialise its class.** A `static final`
field of primitive or `String` type, initialised with a constant expression, is
copied into every class that reads it when *they* are compiled. Reading
`Limits.MAX` never touches `Limits` at run time - its static block does not run.
Calling `Limits.twice()` does.

**Never call an overridable method from a constructor.** The superclass
constructor runs *before* the subclass's fields are assigned - so if it calls a
method the subclass overrides, that method sees the subclass's fields still at
their defaults: `null`, `0`, `false`.

```java
abstract class Widget {
    Widget() { System.out.println("created " + describe()); }   // too early!
    abstract String describe();
}
class Button extends Widget {
    private final String label;
    Button(String label) { this.label = label; }      // runs AFTER Widget()
    String describe() { return "button " + label; }    // label is still null
}
```

`final` does not help: the field is final, and it is *read* before it is
assigned. The fix is to finish constructing first - a static factory that builds
the object, then announces it.
""",
    warmup=[
        _jq("`new Child()` runs first…",
            ["Parent's static initialiser", "Child's constructor", "Parent's constructor",
             "Child's static initialiser"],
            0,
            "A superclass is initialised before its subclass."),
        _jq("Reading `Limits.MAX`, a `static final int MAX = 10`, initialises `Limits`?",
            ["no - it is a compile-time constant, copied into the reader",
             "yes, always", "only once", "only if Limits is public"],
            0,
            "Constant variables are inlined by the compiler."),
    ],
    exercises=[
        _je("j37-lo-order", "Watching the order",
            "Create `k` children and watch every initialiser announce itself. Replace "
            "`____` with the line inside `Child`'s static initialiser.",
            _j37t(_ORDER37,
                  "        int k = sc.nextInt();\n"
                  "        System.out.println(\"main starts\");\n"
                  "        for (int i = 0; i < k; i++) {\n"
                  "            new Child();\n"
                  "        }\n"
                  "        System.out.println(\"main ends\");"),
            "        System.out.println(\"static Child\");",
            [_case(str(k), _order_out37(k)) for k in (1, 2, 0, 3, 1)],
            hints=["The static block prints the class's static announcement.",
                   "`System.out.println(\"static Child\");`",
                   "Statics run once, on first use - and not at all if `k` is 0.",
                   "Per object: Parent's initialiser and constructor, then Child's."],
            difficulty="Easy"),

        _jfix("j37-lo-overridable", "The label that was not there yet",
              "Every button announces itself as `button null`, because `Widget`'s "
              "constructor calls `describe()` before `Button`'s constructor has assigned "
              "the label. Stop calling it from the constructor; announce through the "
              "static factory `Widget.announce` instead.",
              _j37t(_BASE_BUGGY37,
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            new Button(sc.next());\n"
                    "        }"),
              _j37t(_BASE37,
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            Widget.announce(new Button(sc.next()));\n"
                    "        }"),
              [_toks37(ls, _widget_out37(ls)) for ls in _LABELS37],
              hints=["`Widget()` runs before `Button`'s constructor body.",
                     "So `label` is still `null` when `describe()` is called from it.",
                     "Delete that call from the constructor...",
                     "...and let `main` call `Widget.announce(new Button(...))`, which runs "
                     "after construction has finished."],
              difficulty="Medium"),

        _je("j37-lo-constant", "The constant that did not load its class",
            "Print `MAX * k` by reading the constant, then `twice() * k` by calling the "
            "method - and watch when `Limits` is actually initialised. Replace `____` with "
            "the constant's declaration.",
            _j37t(_LIMITS37,
                  "        int k = sc.nextInt();\n"
                  "        System.out.println(\"max \" + Limits.MAX * k);\n"
                  "        System.out.println(\"twice \" + Limits.twice() * k);"),
            "    static final int MAX = 10;",
            [_case(str(k), _limits_out37(k)) for k in _KS37],
            hints=["It must be a compile-time CONSTANT: `static final`, a primitive, and a "
                   "constant initialiser.",
                   "`static final int MAX = 10;`",
                   "The compiler copies 10 into `main`, so reading it never touches `Limits`.",
                   "Drop `final` and `init Limits` would print first instead - the read "
                   "would then be a real static field access."],
            difficulty="Medium"),

        _jch("j37-lo-compose", "Initialisation across classes", "Hard",
             "Write `Engine` and `Car` so that `main`'s output matches: each class prints "
             "`load <Name>` from a static initialiser; `Car` holds an `Engine` created by "
             "a FIELD initialiser; `Engine`'s constructor counts builds in a static field "
             "and prints `engine N`; `Car`'s constructor prints `car ready`.",
             _j37t(_CHAIN37,
                   "        int k = sc.nextInt();\n"
                   "        System.out.println(\"start\");\n"
                   "        for (int i = 0; i < k; i++) {\n"
                   "            new Car();\n"
                   "        }\n"
                   "        System.out.println(\"built \" + Engine.built);"),
             _CHAIN_REGION37,
             [_case(str(k), _chain_out37(k)) for k in (1, 2, 3, 1, 4)],
             hints=["`load Car` prints first: `new Car()` initialises Car.",
                    "Car's field initialiser `new Engine()` then initialises Engine - so "
                    "`load Engine` comes next, from inside Car's construction.",
                    "Field initialisers run BEFORE the constructor body, so `engine N` "
                    "precedes `car ready`.",
                    "`static int built;` counts across all engines.",
                    "Reading `Engine.built` at the end is a static field read - but Engine "
                    "is already initialised by then."]),
    ],
    quiz=[
        _jq("Instance field initialisers run…",
            ["after super(...) returns, before the rest of the constructor body",
             "before the superclass constructor", "after the constructor",
             "once per class"],
            0,
            "Which is why a superclass constructor sees them unset."),
        _jq("A class's static initialiser runs…",
            ["once, on first active use", "every time an object is created",
             "when the program starts", "when the class is garbage collected"],
            0,
            "Lazily, exactly once, under a lock."),
    ],
))


# ===========================================================================
# 37.2 The stack and the heap
# ===========================================================================

_TRACE37 = (
    "    static void load(String what) {\n"
    "        parse(what);\n"
    "    }\n"
    "\n"
    "    static void parse(String what) {\n"
    "        validate(what);\n"
    "    }\n"
    "\n"
    "    static void validate(String what) {\n"
    "        if (what.startsWith(\"bad\")) {\n"
    "            throw new IllegalArgumentException(what);\n"
    "        }\n"
    "    }"
)
_TRACEIN37 = (["ok", "bad1"], ["bad"], ["fine", "good"], ["badger", "x", "bad"], ["y"])


def _trace_out37(ts):
    out = []
    for t in ts:
        if t.startswith("bad"):
            out.append(f"{t}: validate <- parse <- load <- main")
        else:
            out.append(f"{t}: ok")
    return _nl(*out)


_SUMREC37 = (
    "    static long sum(long n) {\n"
    "        return n == 0 ? 0 : n + sum(n - 1);\n"
    "    }"
)
_SUMIT37 = (
    "    static long sum(long n) {\n"
    "        long total = 0;\n"
    "        for (long i = 1; i <= n; i++) {\n"
    "            total += i;\n"
    "        }\n"
    "        return total;\n"
    "    }"
)
_SUMNS37 = (10, 3000000, 1, 5000000, 100)

_CHAINNODES37 = (5, 1000000, 1, 2000000, 7)


def _chainlist_out37(n):
    return _nl(f"length {n}", f"sum {n * (n + 1) // 2}", f"last {n}")


_M37.append(_jlesson(
    "m37-stack", "The stack and the heap",
    "Every call gets a frame; every object lives on the heap. What that means for "
    "recursion, errors and stack traces.",
    """
The JVM's memory has two parts every Java programmer should picture.

**Each thread has a stack** of *frames*, one per method call in progress. A frame
holds that call's parameters, local variables and working values. Calling a
method pushes a frame; returning pops it. That is why local variables are
private to each call, why recursion works (module 10), and why a thread's stack
is cheap to create but limited in size.

**The heap** holds every object - every `new`, every array, every string - shared
by all threads (module 29). A local variable of a reference type lives in a
frame, but only as a *reference*; the object it refers to is on the heap, and
outlives the frame if anything else still refers to it.

Module 9's "Java is always pass-by-value" is this picture in one sentence: a
call copies each argument's value into the new frame - and for an object, that
value is the reference.

## Stack traces are the stack

An exception records the stack at the moment it was created:
`e.getStackTrace()` returns one `StackTraceElement` per frame, **innermost
first** - the method that threw, then its caller, and so on down to `main`. That
is exactly what a stack trace in the console is, and why reading one bottom-up
tells you how the program got there.

## `StackOverflowError`

A thread's stack has a fixed maximum size - typically hundreds of kilobytes to a
few megabytes. Recursion that goes too deep fills it and throws
`StackOverflowError`. It is an `Error`, not an `Exception`: catching it is
possible (the stack has unwound by the time the catch runs), but it signals a
bug or an algorithm that should not be recursive.

HotSpot does **not** eliminate tail calls, so even `return n + sum(n - 1)`
consumes one frame per step. For inputs that may be deep - a long linked list, a
degenerate tree, a big number - write the loop, or manage an explicit stack
(an `ArrayDeque`) on the heap, where millions of entries cost nothing special.

(`-Xss` sets the thread stack size, and `new Thread(group, runnable, name,
stackSize)` requests one per thread - both are workarounds, not fixes.)
""",
    warmup=[
        _jq("A local variable holding a `List` lives…",
            ["in the stack frame, as a reference; the list itself is on the heap",
             "entirely on the heap", "entirely on the stack", "in the class"],
            0,
            "The reference is local; the object is shared."),
        _jq("`e.getStackTrace()[0]` is…",
            ["the method where the exception was created", "main",
             "the outermost call", "always Thread.run"],
            0,
            "Innermost frame first."),
    ],
    exercises=[
        _je("j37-st-trace", "Reading the stack",
            "`load` calls `parse` calls `validate`, which throws for names starting with "
            "`bad`. Catch it in `main` and print the chain of `Main` methods from the "
            "stack trace, innermost first. Replace `____` with the frames.",
            _j37t("",
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            String what = sc.next();\n"
                  "            try {\n"
                  "                load(what);\n"
                  "                System.out.println(what + \": ok\");\n"
                  "            } catch (IllegalArgumentException e) {\n"
                  "                List<String> frames = new ArrayList<>();\n"
                  "                for (StackTraceElement f : e.getStackTrace()) {\n"
                  "                    if (f.getClassName().equals(\"Main\")) {\n"
                  "                        frames.add(f.getMethodName());\n"
                  "                    }\n"
                  "                }\n"
                  "                System.out.println(what + \": \" + String.join(\" <- \", frames));\n"
                  "            }\n"
                  "        }",
                  helpers=_TRACE37),
            "e.getStackTrace()",
            [_toks37(ts, _trace_out37(ts)) for ts in _TRACEIN37],
            hints=["`getStackTrace()` returns one element per frame.",
                   "The first element is where the exception was created: `validate`.",
                   "Filtering on the class name `Main` leaves just this program's frames.",
                   "This is the same list a console stack trace prints."],
            difficulty="Easy"),

        _jfix("j37-st-deep", "Three million frames",
              "`sum(n)` adds `1..n` recursively - one stack frame per step - and throws "
              "`StackOverflowError` for the large inputs. Rewrite it as a loop.",
              _j37t("",
                    "        int q = sc.nextInt();\n"
                    "        for (int i = 0; i < q; i++) {\n"
                    "            System.out.println(sum(sc.nextLong()));\n"
                    "        }",
                    helpers=_SUMREC37),
              _j37t("",
                    "        int q = sc.nextInt();\n"
                    "        for (int i = 0; i < q; i++) {\n"
                    "            System.out.println(sum(sc.nextLong()));\n"
                    "        }",
                    helpers=_SUMIT37),
              [_case(f"1\n{n}", str(n * (n + 1) // 2)) for n in _SUMNS37],
              hints=["Each recursive call pushes a frame; three million of them do not fit "
                     "in any default stack.",
                     "HotSpot does not turn the tail call into a loop for you.",
                     "A `for` loop uses one frame, whatever `n` is.",
                     "The result needs a `long`: 5,000,000 × 5,000,001 / 2 is far past "
                     "`int`."],
              difficulty="Easy"),

        _je("j37-st-catch", "Surviving an overflow",
            "`dive` recurses with no base case. Catch the `StackOverflowError` it causes, "
            "print `overflow caught`, and show the program carries on. Replace `____` with "
            "the catch clause's header.",
            _j37t("",
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            try {\n"
                  "                dive(0);\n"
                  "            } catch (StackOverflowError e) {\n"
                  "                System.out.println(\"overflow caught\");\n"
                  "            }\n"
                  "        }\n"
                  "        System.out.println(\"still running after \" + n);",
                  helpers="    static int dive(int depth) {\n"
                          "        return dive(depth + 1) + 1;\n"
                          "    }"),
            "            } catch (StackOverflowError e) {",
            [_case(str(n), _nl(*(["overflow caught"] * n), f"still running after {n}"))
             for n in (1, 2, 3, 1, 4)],
            hints=["It is an `Error`, so `catch (Exception e)` would NOT catch it.",
                   "`catch (StackOverflowError e)`",
                   "By the time the catch runs, the frames have been popped - there is room "
                   "again.",
                   "Catching it is a demonstration, not a design: the fix is a loop."],
            difficulty="Easy"),

        _jch("j37-st-explicit", "An explicit stack", "Hard",
             "A linked list of `n` nodes is built (values 1..n). Write `stats(head)` WITHOUT "
             "recursion - walk it with a loop - returning the length, the sum and the last "
             "value. The inputs include lists a million nodes long.",
             _j37t("""
class Node {
    final int value;
    Node next;

    Node(int value) {
        this.value = value;
    }
}
""",
                   "        int n = sc.nextInt();\n"
                   "        Node head = new Node(1);\n"
                   "        Node tail = head;\n"
                   "        for (int i = 2; i <= n; i++) {\n"
                   "            tail.next = new Node(i);\n"
                   "            tail = tail.next;\n"
                   "        }\n"
                   "        long[] s = stats(head);\n"
                   "        System.out.println(\"length \" + s[0]);\n"
                   "        System.out.println(\"sum \" + s[1]);\n"
                   "        System.out.println(\"last \" + s[2]);",
                   helpers="    static long[] stats(Node head) {\n"
                           "        long length = 0;\n"
                           "        long sum = 0;\n"
                           "        long last = 0;\n"
                           "        for (Node cur = head; cur != null; cur = cur.next) {\n"
                           "            length++;\n"
                           "            sum += cur.value;\n"
                           "            last = cur.value;\n"
                           "        }\n"
                           "        return new long[] {length, sum, last};\n"
                           "    }"),
             "    static long[] stats(Node head) {\n"
             "        long length = 0;\n"
             "        long sum = 0;\n"
             "        long last = 0;\n"
             "        for (Node cur = head; cur != null; cur = cur.next) {\n"
             "            length++;\n"
             "            sum += cur.value;\n"
             "            last = cur.value;\n"
             "        }\n"
             "        return new long[] {length, sum, last};\n"
             "    }",
             [_case(str(n), _chainlist_out37(n)) for n in _CHAINNODES37],
             hints=["A `for` loop over `cur = cur.next` visits every node with one frame.",
                    "The nodes themselves are on the heap - a million of them is a few "
                    "tens of megabytes, not a problem.",
                    "A recursive `stats(head.next)` would need a million frames.",
                    "Keep the sum in a `long`.",
                    "Return the three results in a `long[]`."]),
    ],
    quiz=[
        _jq("`StackOverflowError` is a subclass of…",
            ["Error", "RuntimeException", "Exception", "IOException"],
            0,
            "`catch (Exception e)` does not catch it."),
        _jq("Does HotSpot eliminate tail calls?",
            ["no - every call gets a frame", "yes, always", "only in static methods",
             "only with -O"],
            0,
            "Deep recursion must become a loop by hand."),
    ],
))


# ===========================================================================
# 37.3 Strings, boxing and identity
# ===========================================================================

_WORDS37 = ("java", "pool", "hello", "x", "intern")


def _pool_out37(w):
    return _nl("literal == new: false", "literal == intern: true", "new == new: false",
               f"equals: true ({w})")


_UNBOX37 = (("apple", "apple", "pear"), ("kiwi",), ("a", "b", "a", "c"), ("x", "x", "x"),
            ("fig", "plum"))
_STOCK37 = {"apple": 3, "pear": 0, "a": 5, "b": 2}


def _stock_out37(items):
    return _nl(*[f"{i}: {_STOCK37.get(i, 0)}" for i in items])


_SAME37 = ([(127, 127), (128, 128)], [(1, 1)], [(-129, -129), (0, 0)], [(1000, 1001)], [(-128, -128)])


def _same_out37(rows):
    out = []
    for (a, b) in rows:
        out.append(f"Integer {a} vs Long {b}: equals false, same value {_jbool(a == b)}")
    return _nl(*out)


_M37.append(_jlesson(
    "m37-identity", "Strings, boxing and identity",
    "The String pool, constant folding, the Integer cache, and the NullPointerException "
    "hiding in every unboxing.",
    """
`==` on references asks "is this the same object?" - and three JVM mechanisms
decide, behind your back, when two equal values *are* the same object.

## The String pool

String **literals** are interned: every `"java"` in every class refers to one
shared object in the pool. Strings built **at run time** are new objects:

```java
String a = "java";
String b = new String("java");     // always a new object
String c = b.intern();             // the pooled one
a == b      // false
a == c      // true
a.equals(b) // true - the only comparison you should be writing
```

**Constant folding** blurs the line. An expression made only of compile-time
constants is computed by the compiler and interned:

```java
"ja" + "va" == "java"              // true: folded at compile time
final String p = "ja";  p + "va" == "java"   // true: p is a constant variable
String q = "ja";        q + "va" == "java"   // false: built at run time
```

That is why a `==` comparison of strings can pass in a test and fail in
production - it depends on *how* the string was produced. `intern()` exists, and
was once used to save memory; modern JVMs deduplicate strings in the garbage
collector instead.

## The Integer cache

Module 35 showed `Integer.valueOf` caching -128..127, and autoboxing calls
`valueOf`. So `Integer a = 127, b = 127; a == b` is true and the same with 128 is
false. `Long`, `Short`, `Byte` and `Character` cache small values the same way.

## Two boxing traps

```java
Map<String, Integer> stock = ...;
int n = stock.get("kiwi");         // NullPointerException if "kiwi" is absent
```

Unboxing `null` throws. The line looks like arithmetic and fails like a
dereference - use `getOrDefault`, or keep the `Integer` and check it.

```java
Long big = 1L;  Integer small = 1;
big.equals(small)                  // false! different classes
big.longValue() == small.longValue()   // true
```

`equals` on wrapper types compares the *class* as well as the value, so a `Long`
never equals an `Integer`. Mixed boxed types need explicit primitive
comparison.
""",
    warmup=[
        _jq("`\"ja\" + \"va\" == \"java\"` is…",
            ["true - the compiler folds the constants and interns the result",
             "false", "a compile error", "undefined"],
            0,
            "Constant expressions are computed at compile time."),
        _jq("`Long.valueOf(5).equals(Integer.valueOf(5))` is…",
            ["false - different classes", "true", "an exception", "a compile error"],
            0,
            "Wrapper equals checks the type too."),
    ],
    exercises=[
        _je("j37-id-intern", "Where the strings live",
            "Compare a literal, a `new String`, and an interned copy with `==`, then with "
            "`equals`. Replace `____` with the call that returns the pooled string.",
            _j37t("",
                  "        String word = sc.next();\n"
                  "        String literal = word.intern();\n"
                  "        String fresh = new String(word);\n"
                  "        String another = new String(word);\n"
                  "        String pooled = fresh.intern();\n"
                  "        System.out.println(\"literal == new: \" + (literal == fresh));\n"
                  "        System.out.println(\"literal == intern: \" + (literal == pooled));\n"
                  "        System.out.println(\"new == new: \" + (fresh == another));\n"
                  "        System.out.println(\"equals: \" + literal.equals(fresh) + \" (\" + word + \")\");"),
            "        String pooled = fresh.intern();",
            [_case(w, _pool_out37(w)) for w in _WORDS37],
            hints=["`intern()` returns THE pooled string with the same contents.",
                   "`String pooled = fresh.intern();`",
                   "Two `new String(...)` objects are never `==`, however equal.",
                   "`equals` is true in every case - it is the comparison to use."],
            difficulty="Easy"),

        _jfix("j37-id-unbox", "The null in the arithmetic",
              "Looking up an item that is not in stock throws `NullPointerException` - "
              "`int count = stock.get(item)` unboxes a `null`. Use a default of zero "
              "instead.",
              _j37t("",
                    "        Map<String, Integer> stock = new HashMap<>();\n"
                    "        stock.put(\"apple\", 3);\n"
                    "        stock.put(\"pear\", 0);\n"
                    "        stock.put(\"a\", 5);\n"
                    "        stock.put(\"b\", 2);\n"
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String item = sc.next();\n"
                    "            int count = stock.get(item);\n"
                    "            System.out.println(item + \": \" + count);\n"
                    "        }"),
              _j37t("",
                    "        Map<String, Integer> stock = new HashMap<>();\n"
                    "        stock.put(\"apple\", 3);\n"
                    "        stock.put(\"pear\", 0);\n"
                    "        stock.put(\"a\", 5);\n"
                    "        stock.put(\"b\", 2);\n"
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String item = sc.next();\n"
                    "            int count = stock.getOrDefault(item, 0);\n"
                    "            System.out.println(item + \": \" + count);\n"
                    "        }"),
              [_toks37(list(items), _stock_out37(items)) for items in _UNBOX37],
              hints=["`stock.get(\"kiwi\")` returns `null`.",
                     "Assigning `null` to an `int` unboxes it - and unboxing null throws.",
                     "`stock.getOrDefault(item, 0)`",
                     "The line looks like arithmetic and fails like a dereference, which is "
                     "why it is so easy to miss."],
              difficulty="Easy"),

        _je("j37-id-constant", "When concatenation is free",
            "Build `java` two ways - from a `final` constant and from a plain variable - "
            "and compare each with the literal using `==`. Replace `____` with the "
            "declaration that makes the first one a compile-time constant.",
            _j37t("",
                  "        int n = sc.nextInt();\n"
                  "        final String prefix = \"ja\";\n"
                  "        String plain = \"ja\";\n"
                  "        String folded = prefix + \"va\";\n"
                  "        String built = plain + \"va\";\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            System.out.println(\"folded == literal: \" + (folded == \"java\"));\n"
                  "            System.out.println(\"built == literal: \" + (built == \"java\"));\n"
                  "            System.out.println(\"built equals literal: \" + built.equals(\"java\"));\n"
                  "        }"),
            "        final String prefix = \"ja\";",
            [_case(str(n), _nl(*(["folded == literal: true", "built == literal: false",
                                  "built equals literal: true"] * n))) for n in (1, 2, 1, 3, 1)],
            hints=["A `final` local initialised with a constant is a *constant variable*.",
                   "`final String prefix = \"ja\";`",
                   "`prefix + \"va\"` is then folded by the compiler into the literal "
                   "`\"java\"`.",
                   "`plain + \"va\"` is computed at run time into a new object."],
            difficulty="Medium"),

        _jch("j37-id-same", "Comparing mixed boxes", "Medium",
             "Write `sameValue(Number a, Number b)` so it compares the numeric VALUES of any "
             "two boxed integers - an `Integer` and a `Long` included. `main` shows that "
             "`equals` says false for every pair, and your method gets it right.",
             _j37t("",
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            Integer a = sc.nextInt();\n"
                   "            Long b = sc.nextLong();\n"
                   "            System.out.println(\"Integer \" + a + \" vs Long \" + b + \": equals \" + a.equals(b)\n"
                   "                    + \", same value \" + sameValue(a, b));\n"
                   "        }",
                   helpers="    static boolean sameValue(Number a, Number b) {\n"
                           "        return a.longValue() == b.longValue();\n"
                           "    }"),
             "    static boolean sameValue(Number a, Number b) {\n"
             "        return a.longValue() == b.longValue();\n"
             "    }",
             [_rows37(rows, _same_out37(rows)) for rows in _SAME37],
             hints=["`Integer` and `Long` both extend `Number`.",
                    "`longValue()` widens either to a primitive `long`.",
                    "Primitive `==` compares values, never identity.",
                    "`Integer.equals` returns false for any non-Integer argument - that is "
                    "its contract."]),
    ],
    quiz=[
        _jq("`String q = \"ja\"; (q + \"va\") == \"java\"` is…",
            ["false - q is not a constant, so the concatenation happens at run time",
             "true", "a compile error", "true only with -O"],
            0,
            "Make q final and the answer changes."),
        _jq("`int n = map.get(key);` with a missing key throws…",
            ["NullPointerException", "NoSuchElementException", "ClassCastException",
             "nothing - n is 0"],
            0,
            "Unboxing null."),
    ],
))


# ===========================================================================
# 37.4 Garbage collection
# ===========================================================================

# (objects, edges, roots)
_GRAPHS37 = (
    (["a", "b", "c", "d"], [("a", "b"), ("c", "d")], ["a"]),
    (["x", "y", "z"], [("x", "y"), ("y", "z"), ("z", "x")], []),
    (["r", "s", "t", "u", "v"], [("r", "s"), ("s", "t"), ("u", "v"), ("v", "u")], ["r"]),
    (["m"], [], ["m"]),
    (["p", "q", "w", "e"], [("p", "q"), ("q", "p"), ("w", "e")], ["w"]),
)


def _reach37(objs, edges, roots):
    adj = {o: [] for o in objs}
    for (a, b) in edges:
        adj[a].append(b)
    seen, stack = set(), list(roots)
    while stack:
        o = stack.pop()
        if o in seen:
            continue
        seen.add(o)
        stack.extend(adj[o])
    return seen


def _graph_stdin37(objs, edges, roots):
    return "\n".join([str(len(objs)), " ".join(objs), str(len(edges))]
                     + [f"{a} {b}" for (a, b) in edges]
                     + [str(len(roots)) + ("" if not roots else " " + " ".join(roots))])


def _mark_out37(objs, edges, roots):
    live = _reach37(objs, edges, roots)
    dead = sorted(o for o in objs if o not in live)
    return _nl(f"live {_jarr(sorted(live))}", f"collected {_jarr(dead)}")


def _rc_out37(objs, edges, roots):
    """Reference counting as it really behaves: free every object whose count is
    zero, decrement what IT referred to, and cascade. What survives but is
    unreachable is exactly the cycles."""
    counts = {o: 0 for o in objs}
    for (_a, b) in edges:
        counts[b] += 1
    for r in roots:
        counts[r] += 1
    initial = dict(counts)
    adj = {o: [b for (a, b) in edges if a == o] for o in objs}
    zero = [o for o in sorted(objs) if counts[o] == 0]
    freed = set()
    while zero:
        o = zero.pop(0)
        if o in freed:
            continue
        freed.add(o)
        for t in adj[o]:
            counts[t] -= 1
            if counts[t] == 0:
                zero.append(t)
    kept = sorted(o for o in objs if o not in freed)
    live = _reach37(objs, edges, roots)
    leaked = [o for o in kept if o not in live]
    return _nl("counts " + " ".join(f"{o}={initial[o]}" for o in sorted(objs)),
               f"refcount keeps {_jarr(kept)}", f"leaked {_jarr(leaked)}")


_READGRAPH37 = (
    "        int n = sc.nextInt();\n"
    "        List<String> objects = new ArrayList<>();\n"
    "        Map<String, List<String>> refs = new HashMap<>();\n"
    "        for (int i = 0; i < n; i++) {\n"
    "            String o = sc.next();\n"
    "            objects.add(o);\n"
    "            refs.put(o, new ArrayList<>());\n"
    "        }\n"
    "        int e = sc.nextInt();\n"
    "        for (int i = 0; i < e; i++) {\n"
    "            refs.get(sc.next()).add(sc.next());\n"
    "        }\n"
    "        int r = sc.nextInt();\n"
    "        List<String> roots = new ArrayList<>();\n"
    "        for (int i = 0; i < r; i++) {\n"
    "            roots.add(sc.next());\n"
    "        }\n"
)
_MARK37 = (
    "    static Set<String> mark(List<String> roots, Map<String, List<String>> refs) {\n"
    "        Set<String> marked = new TreeSet<>();\n"
    "        Deque<String> work = new ArrayDeque<>(roots);\n"
    "        while (!work.isEmpty()) {\n"
    "            String o = work.pop();\n"
    "            if (marked.add(o)) {\n"
    "                work.addAll(refs.get(o));\n"
    "            }\n"
    "        }\n"
    "        return marked;\n"
    "    }"
)

_CACHE_OPS37 = ((5, 3), (10, 4), (3, 3), (7, 1), (12, 5))


def _lru_insert_out37(n, cap):
    keys = [f"k{i}" for i in range(1, n + 1)]
    kept = keys[-cap:]
    return _nl(f"size {len(kept)}", _jarr(kept))


_LRU37 = """
class LruCache<K, V> {
    private final int capacity;
    private final LinkedHashMap<K, V> map;

    LruCache(int capacity) {
        this.capacity = capacity;
        this.map = new LinkedHashMap<>(16, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
                return size() > LruCache.this.capacity;
            }
        };
    }

    V get(K key) {
        return map.get(key);
    }

    void put(K key, V value) {
        map.put(key, value);
    }

    Set<K> keys() {
        return map.keySet();
    }
}
"""
_LRU_REGION37 = "\n".join(_LRU37.strip("\n").split("\n")[1:-1])
_LRUOPS37 = (
    (2, [("put", "a"), ("put", "b"), ("get", "a"), ("put", "c")]),
    (3, [("put", "x"), ("put", "y"), ("put", "z"), ("put", "w")]),
    (1, [("put", "p"), ("get", "p"), ("put", "q"), ("get", "p")]),
    (2, [("get", "nope"), ("put", "m"), ("put", "n"), ("get", "m"), ("put", "o"), ("get", "n")]),
    (3, [("put", "a"), ("put", "b"), ("put", "c"), ("get", "a"), ("get", "b"), ("put", "d")]),
)


def _lru_out37(cap, ops):
    order, vals, out = [], {}, []
    for op in ops:
        k = op[1]
        if op[0] == "put":
            if k in order:
                order.remove(k)
            order.append(k)
            vals[k] = k.upper()
            if len(order) > cap:
                old = order.pop(0)
                del vals[old]
        else:
            if k in order:
                order.remove(k)
                order.append(k)
                out.append(f"get {k} = {vals[k]}")
            else:
                out.append(f"get {k} = null")
    out.append(f"keys {_jarr(order)}")
    return _nl(*out)


def _lru_case37(cap, ops):
    stdin = "\n".join([str(cap), str(len(ops))] + [" ".join(op) for op in ops])
    return _case(stdin, _lru_out37(cap, ops))


_M37.append(_jlesson(
    "m37-gc", "Garbage collection",
    "What makes an object garbage, how collectors find it, and the leaks a garbage "
    "collector cannot fix.",
    """
Java has no `free`. An object stays alive for as long as it is **reachable** and
the garbage collector reclaims it some time after it is not - *some time*,
because when a collection runs is entirely the JVM's decision. That is why no
exercise here waits for a real collection: instead, you implement the algorithms.

## Reachability, not reference counts

The **roots** are the references the program can use directly: local variables
in every live stack frame, static fields, and a few JVM internals. An object is
**live** if a chain of references leads to it from a root. Everything else is
garbage - *including groups of objects that refer to each other*.

That last point is the difference from **reference counting** (used by CPython
and Swift): counting how many references point at each object and freeing it at
zero. Reference counting is simple and immediate, but a **cycle** - `a → b → a`,
with nothing else pointing in - keeps every count above zero forever. Tracing
collectors, like every JVM collector, never have that problem.

## Mark and sweep

The classic tracing algorithm:

1. **mark** - starting from the roots, follow every reference, marking each
   object reached (a graph traversal: module 31's work queue, or DFS/BFS);
2. **sweep** - every unmarked object is garbage.

Real JVM collectors are refinements of this. **Generational** collection
observes that most objects die young, so it collects a small *young generation*
often and cheaply, promoting survivors to an *old generation* collected rarely.
**G1** (the default) splits the heap into regions and collects the most garbage-
filled ones first; **ZGC** and **Shenandoah** do most of their work concurrently,
keeping pauses to milliseconds. You choose between them with a flag - the code
does not change.

## The leaks a collector cannot fix

A collector frees what is unreachable. A **memory leak** in Java is therefore an
object that is still reachable but will never be used again:

* an ever-growing **static collection** - a cache with no eviction;
* **listeners** never unsubscribed (module 35's lapsed listener);
* a long-lived inner-class object pinning its outer object (module 33).

The fix for the first is a **bounded** cache. `LinkedHashMap` can be one in a few
lines: constructed with `accessOrder = true` it keeps entries in
least-recently-*used* order, and overriding `removeEldestEntry` evicts the oldest
once it grows past a capacity - an **LRU cache**, a favourite interview question
in its own right.

(`System.gc()` only *requests* a collection, and `finalize()` is deprecated -
never rely on either. `try`-with-resources, module 16, is how Java releases
non-memory resources deterministically.)
""",
    warmup=[
        _jq("Two objects refer only to each other, and nothing else refers to either. A "
            "JVM garbage collector…",
            ["can reclaim both - they are unreachable", "can never reclaim them",
             "reclaims one", "throws OutOfMemoryError"],
            0,
            "Tracing collectors handle cycles; reference counting does not."),
        _jq("A memory leak in Java is…",
            ["an object still reachable that will never be used", "an unreachable object",
             "a missing free()", "impossible"],
            0,
            "The collector cannot know you are finished with it."),
    ],
    exercises=[
        _jch("j37-gc-mark", "Mark and sweep", "Medium",
             "An object graph is read from stdin: the objects, the references between them, "
             "and the roots. Write `mark(roots, refs)`: every object reachable from a root. "
             "`main` then sweeps, printing the live and collected objects.",
             _j37t("",
                   _READGRAPH37
                   + "        Set<String> live = mark(roots, refs);\n"
                     "        List<String> collected = new ArrayList<>();\n"
                     "        for (String o : objects) {\n"
                     "            if (!live.contains(o)) {\n"
                     "                collected.add(o);\n"
                     "            }\n"
                     "        }\n"
                     "        Collections.sort(collected);\n"
                     "        System.out.println(\"live \" + live);\n"
                     "        System.out.println(\"collected \" + collected);",
                   helpers=_MARK37),
             _MARK37,
             [_case(_graph_stdin37(*g), _mark_out37(*g)) for g in _GRAPHS37],
             hints=["Start a work queue with the roots.",
                    "Pop an object; if it was not yet marked, mark it and push everything it "
                    "refers to.",
                    "`marked.add(o)` returns false for an object already marked - that "
                    "check is what stops cycles looping forever.",
                    "A `TreeSet` prints the live objects in order.",
                    "`x → y → z → x` with no roots is all garbage - a cycle is no "
                    "protection."]),

        _je("j37-gc-refcount", "Why reference counting leaks",
            "Count the references to each object (from other objects, plus one per root), "
            "then run reference counting: free each object whose count is zero, decrement "
            "what it pointed to, and cascade. Compare what survives with what is actually "
            "reachable. Replace `____` with the line that counts a reference from one "
            "object to another.",
            _j37t("",
                  _READGRAPH37
                  + "        Map<String, Integer> counts = new TreeMap<>();\n"
                    "        for (String o : objects) {\n"
                    "            counts.put(o, 0);\n"
                    "        }\n"
                    "        for (List<String> targets : refs.values()) {\n"
                    "            for (String t : targets) {\n"
                    "                counts.merge(t, 1, Integer::sum);\n"
                    "            }\n"
                    "        }\n"
                    "        for (String root : roots) {\n"
                    "            counts.merge(root, 1, Integer::sum);\n"
                    "        }\n"
                    "        StringBuilder line = new StringBuilder(\"counts\");\n"
                    "        Deque<String> zero = new ArrayDeque<>();\n"
                    "        for (Map.Entry<String, Integer> en : counts.entrySet()) {\n"
                    "            line.append(' ').append(en.getKey()).append('=').append(en.getValue());\n"
                    "            if (en.getValue() == 0) {\n"
                    "                zero.add(en.getKey());\n"
                    "            }\n"
                    "        }\n"
                    "        Set<String> freed = new HashSet<>();\n"
                    "        while (!zero.isEmpty()) {\n"
                    "            String o = zero.pop();\n"
                    "            if (!freed.add(o)) {\n"
                    "                continue;\n"
                    "            }\n"
                    "            for (String t : refs.get(o)) {\n"
                    "                if (counts.merge(t, -1, Integer::sum) == 0) {\n"
                    "                    zero.add(t);\n"
                    "                }\n"
                    "            }\n"
                    "        }\n"
                    "        List<String> kept = new ArrayList<>();\n"
                    "        for (String o : counts.keySet()) {\n"
                    "            if (!freed.contains(o)) {\n"
                    "                kept.add(o);\n"
                    "            }\n"
                    "        }\n"
                    "        Set<String> live = mark(roots, refs);\n"
                    "        List<String> leaked = new ArrayList<>();\n"
                    "        for (String o : kept) {\n"
                    "            if (!live.contains(o)) {\n"
                    "                leaked.add(o);\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(line);\n"
                    "        System.out.println(\"refcount keeps \" + kept);\n"
                    "        System.out.println(\"leaked \" + leaked);",
                  helpers=_MARK37),
            "                counts.merge(t, 1, Integer::sum);",
            [_case(_graph_stdin37(*g), _rc_out37(*g)) for g in _GRAPHS37],
            hints=["Every reference TO an object adds one to its count.",
                   "`counts.merge(t, 1, Integer::sum);`",
                   "An object in a cycle is referenced by the cycle itself, so its count "
                   "never falls to zero.",
                   "`leaked` is what reference counting keeps but a tracing collector "
                   "frees."],
            difficulty="Medium"),

        _jfix("j37-gc-leak", "The cache that never forgot",
              "This cache is a plain `HashMap` that only ever grows - reachable forever, so no "
              "collector can help. Bound it: make it a `LinkedHashMap` that evicts its "
              "eldest entry once it holds more than `capacity`, and print its size and "
              "keys after inserting `k1..kn`.",
              _j37t("",
                    "        int n = sc.nextInt();\n"
                    "        int capacity = sc.nextInt();\n"
                    "        Map<String, Integer> cache = new LinkedHashMap<>();\n"
                    "        for (int i = 1; i <= n; i++) {\n"
                    "            cache.put(\"k\" + i, i);\n"
                    "        }\n"
                    "        System.out.println(\"size \" + cache.size());\n"
                    "        System.out.println(cache.keySet());"),
              _j37t("",
                    "        int n = sc.nextInt();\n"
                    "        int capacity = sc.nextInt();\n"
                    "        Map<String, Integer> cache = new LinkedHashMap<>() {\n"
                    "            @Override\n"
                    "            protected boolean removeEldestEntry(Map.Entry<String, Integer> eldest) {\n"
                    "                return size() > capacity;\n"
                    "            }\n"
                    "        };\n"
                    "        for (int i = 1; i <= n; i++) {\n"
                    "            cache.put(\"k\" + i, i);\n"
                    "        }\n"
                    "        System.out.println(\"size \" + cache.size());\n"
                    "        System.out.println(cache.keySet());"),
              [_case(f"{n} {c}", _lru_insert_out37(n, c)) for (n, c) in _CACHE_OPS37],
              hints=["Every entry in the map is reachable, so the collector keeps it all.",
                     "`LinkedHashMap` calls `removeEldestEntry` after every `put`.",
                     "Override it in an anonymous subclass (module 33): `return size() > "
                     "capacity;`",
                     "`capacity` is captured from `main` - it is effectively final.",
                     "Only the most recent `capacity` keys survive."],
              difficulty="Medium"),

        _jch("j37-gc-lru", "An LRU cache", "Hard",
             "Write the body of `LruCache<K, V>`: a `LinkedHashMap` in ACCESS order (the "
             "three-argument constructor with `true`) that evicts its least recently used "
             "entry once it holds more than `capacity`; plus `get`, `put` and `keys`.",
             _j37t(_LRU37,
                   "        int capacity = sc.nextInt();\n"
                   "        LruCache<String, String> cache = new LruCache<>(capacity);\n"
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            String op = sc.next();\n"
                   "            String key = sc.next();\n"
                   "            if (op.equals(\"put\")) {\n"
                   "                cache.put(key, key.toUpperCase());\n"
                   "            } else {\n"
                   "                System.out.println(\"get \" + key + \" = \" + cache.get(key));\n"
                   "            }\n"
                   "        }\n"
                   "        System.out.println(\"keys \" + cache.keys());"),
             _LRU_REGION37,
             [_lru_case37(c, ops) for (c, ops) in _LRUOPS37],
             hints=["`new LinkedHashMap<>(16, 0.75f, true)` - the `true` switches to access "
                    "order.",
                    "In access order, a `get` moves the entry to the end.",
                    "Override `removeEldestEntry` in an anonymous subclass.",
                    "Inside it, `capacity` is the LruCache's field - spell it "
                    "`LruCache.this.capacity` to be unambiguous (module 33).",
                    "`keys()` lists least to most recently used."]),
    ],
    quiz=[
        _jq("Which are garbage-collection roots?",
            ["local variables in live frames and static fields",
             "every object with a reference to it", "only main's variables",
             "objects created with new"],
            0,
            "Everything reachable from them is live."),
        _jq("A `LinkedHashMap` built with `accessOrder = true` orders its entries by…",
            ["least recently used first", "insertion", "key", "hash"],
            0,
            "Which, with removeEldestEntry, makes an LRU cache."),
    ],
))


# ===========================================================================
# 37.5 Bytecode
# ===========================================================================

_VM37 = (
    "    static List<String> run(List<String[]> code) {\n"
    "        Deque<Integer> stack = new ArrayDeque<>();\n"
    "        int[] locals = new int[8];\n"
    "        List<String> out = new ArrayList<>();\n"
    "        int pc = 0;\n"
    "        while (pc < code.size()) {\n"
    "            String[] ins = code.get(pc);\n"
    "            pc++;\n"
    "            switch (ins[0]) {\n"
    "                case \"push\" -> stack.push(Integer.parseInt(ins[1]));\n"
    "                case \"add\" -> stack.push(stack.pop() + stack.pop());\n"
    "                case \"mul\" -> stack.push(stack.pop() * stack.pop());\n"
    "                case \"sub\" -> {\n"
    "                    int b = stack.pop();\n"
    "                    int a = stack.pop();\n"
    "                    stack.push(a - b);\n"
    "                }\n"
    "                case \"div\" -> {\n"
    "                    int b = stack.pop();\n"
    "                    int a = stack.pop();\n"
    "                    stack.push(a / b);\n"
    "                }\n"
    "                case \"dup\" -> stack.push(stack.peek());\n"
    "                case \"print\" -> out.add(String.valueOf(stack.pop()));\n"
    "                case \"load\" -> stack.push(locals[Integer.parseInt(ins[1])]);\n"
    "                case \"store\" -> locals[Integer.parseInt(ins[1])] = stack.pop();\n"
    "                case \"jmp\" -> pc = Integer.parseInt(ins[1]);\n"
    "                case \"jlt\" -> {\n"
    "                    int b = stack.pop();\n"
    "                    int a = stack.pop();\n"
    "                    if (a < b) {\n"
    "                        pc = Integer.parseInt(ins[1]);\n"
    "                    }\n"
    "                }\n"
    "                default -> throw new IllegalStateException(\"bad instruction \" + ins[0]);\n"
    "            }\n"
    "        }\n"
    "        return out;\n"
    "    }"
)

_READCODE37 = (
    "        int n = sc.nextInt();\n"
    "        sc.nextLine();\n"
    "        List<String[]> code = new ArrayList<>();\n"
    "        for (int i = 0; i < n; i++) {\n"
    "            code.add(sc.nextLine().trim().split(\" \"));\n"
    "        }\n"
)


def _vm37(code):
    stack, locals_, out, pc = [], [0] * 8, [], 0
    while pc < len(code):
        ins = code[pc].split()
        pc += 1
        op = ins[0]
        if op == "push":
            stack.append(int(ins[1]))
        elif op == "load":
            stack.append(locals_[int(ins[1])])
        elif op == "store":
            locals_[int(ins[1])] = stack.pop()
        elif op == "add":
            b, a = stack.pop(), stack.pop()
            stack.append(a + b)
        elif op == "mul":
            b, a = stack.pop(), stack.pop()
            stack.append(a * b)
        elif op == "sub":
            b, a = stack.pop(), stack.pop()
            stack.append(a - b)
        elif op == "div":
            b, a = stack.pop(), stack.pop()
            stack.append(_jdiv(a, b))
        elif op == "dup":
            stack.append(stack[-1])
        elif op == "jmp":
            pc = int(ins[1])
        elif op == "jlt":
            b, a = stack.pop(), stack.pop()
            if a < b:
                pc = int(ins[1])
        elif op == "print":
            out.append(str(stack.pop()))
    return out


def _code_case37(code):
    return _case("\n".join([str(len(code))] + code) + "\n", _nl(*_vm37(code)))


# Straight-line programs.
_PROGS37 = (
    ["push 2", "push 3", "add", "print"],
    ["push 7", "push 5", "sub", "print", "push 10", "push 4", "sub", "print"],
    ["push 6", "push 7", "mul", "push 2", "add", "print"],
    ["push 3", "dup", "mul", "dup", "print", "push 1", "sub", "print"],
    ["push 100", "push 7", "div", "print", "push 9", "push 12", "sub", "print"],
)

# Programs with locals and jumps: a loop printing 1..3, factorial 5, countdown,
# sum of 1..10, and powers of two below 50.
_LOOPS37 = (
    ["push 1", "store 0", "load 0", "print", "load 0", "push 1", "add", "store 0",
     "load 0", "push 4", "jlt 2"],
    ["push 1", "store 0", "push 1", "store 1", "load 0", "load 1", "mul", "store 0",
     "load 1", "push 1", "add", "store 1", "load 1", "push 6", "jlt 4", "load 0", "print"],
    ["push 3", "store 0", "load 0", "print", "load 0", "push 1", "sub", "store 0",
     "push 0", "load 0", "jlt 2"],
    ["push 0", "store 0", "push 1", "store 1", "load 0", "load 1", "add", "store 0",
     "load 1", "push 1", "add", "store 1", "load 1", "push 11", "jlt 4", "load 0", "print"],
    ["push 1", "store 0", "load 0", "print", "load 0", "push 2", "mul", "store 0",
     "load 0", "push 50", "jlt 2"],
)

_POSTFIX37 = ("3 4 + 2 *", "10 2 - 3 -", "2 3 4 * +", "7", "100 5 / 3 2 * -")


def _postfix37(expr):
    toks = expr.split()
    code = [f"push {t}" if t.lstrip("-").isdigit() else
            {"+": "add", "-": "sub", "*": "mul", "/": "div"}[t] for t in toks]
    return code, _vm37(code + ["print"])[0]


_M37.append(_jlesson(
    "m37-bytecode", "Bytecode: the JVM is a stack machine",
    "What `javac` actually produces - and a small interpreter that runs it.",
    """
`javac` does not produce machine code. It produces **bytecode**: instructions
for an imaginary machine - the Java Virtual Machine - which is why one class file
runs unchanged on any operating system with a JVM.

The JVM is a **stack machine**. Instead of registers, each frame (lesson 37.2)
has an **operand stack** and an array of **local variables**, and instructions
push and pop:

```java
int c = a + b * 2;
```

compiles to (you can see it yourself with `javap -c Main.class`):

```
iload_1        // push local 1 (a)
iload_2        // push local 2 (b)
iconst_2       // push the constant 2
imul           // pop two, push b * 2
iadd           // pop two, push a + b * 2
istore_3       // pop into local 3 (c)
```

Notice what the stack does for free: the expression's precedence became the
*order* of the instructions - `b * 2` is computed first because its instructions
come first. The code is exactly the expression in **postfix** notation.

## Order matters on a stack

For `a - b`, the JVM pushes `a` then `b`. So when `isub` pops, it gets **`b`
first**, then `a` - and must compute `a - b`, the second value popped minus the
first. Getting that backwards is the classic bug in every stack-machine
interpreter; it hides for `add` and `mul`, which do not care about order.

## Control flow is jumps

There are no `if` or `while` instructions - only **conditional jumps** to an
instruction index. `if_icmplt 12` pops two ints and jumps to instruction 12 if
the first pushed is less than the second; `goto` jumps unconditionally. Every
loop you have ever written compiles to a comparison and a backward jump.

## And then the JIT

The JVM starts by *interpreting* bytecode, much as this lesson's exercises do. A
method that runs often enough is compiled by the **just-in-time compiler** into
native machine code - first quickly (C1), then, if it stays hot, with heavy
optimisation (C2): inlining, escape analysis that keeps short-lived objects off
the heap entirely, and loop optimisations. That warm-up is why a Java program
gets faster as it runs, and why a microbenchmark that measures the first few
thousand iterations measures the interpreter.

The exercises use a small, readable instruction set - `push`, `load`, `store`,
`add`, `sub`, `mul`, `div`, `dup`, `jmp`, `jlt`, `print` - with the same
semantics as the JVM's `iconst`, `iload`, `istore`, `iadd`... and `if_icmplt`.
""",
    warmup=[
        _jq("`a - b` on a stack machine pushes a, then b. `sub` must compute…",
            ["the second value popped minus the first", "the first popped minus the second",
             "either - subtraction commutes", "a + b"],
            0,
            "The first pop is b."),
        _jq("`int c = a + b * 2;` compiles to instructions in which order?",
            ["a, b, 2, multiply, add, store", "a, b, add, 2, multiply, store",
             "multiply, add, a, b", "store, add, multiply"],
            0,
            "Postfix: operands first, operators when their operands are ready."),
    ],
    exercises=[
        _je("j37-bc-add", "The operand stack",
            "The interpreter runs straight-line programs. Replace `____` with the `add` "
            "case - pop two, push their sum.",
            _j37t("",
                  _READCODE37
                  + "        for (String line : run(code)) {\n"
                    "            System.out.println(line);\n"
                    "        }",
                  helpers=_VM37),
            "                case \"add\" -> stack.push(stack.pop() + stack.pop());",
            [_code_case37(p) for p in _PROGS37],
            hints=["An arrow arm in the switch statement: `case \"add\" -> ...;`",
                   "Pop two values, add them, push the result.",
                   "`stack.push(stack.pop() + stack.pop());`",
                   "Order does not matter for `add` - it does for `sub`."],
            difficulty="Easy"),

        _jfix("j37-bc-sub", "Backwards subtraction",
              "`sub` and `div` pop their operands the wrong way round, so `7 5 sub` gives "
              "-2. On a stack the FIRST value popped is the right-hand operand. Fix both.",
              _j37t("",
                    _READCODE37
                    + "        for (String line : run(code)) {\n"
                      "            System.out.println(line);\n"
                      "        }",
                    helpers=_VM37.replace(
                        "                    int b = stack.pop();\n"
                        "                    int a = stack.pop();\n"
                        "                    stack.push(a - b);",
                        "                    int a = stack.pop();\n"
                        "                    int b = stack.pop();\n"
                        "                    stack.push(a - b);").replace(
                        "                    int b = stack.pop();\n"
                        "                    int a = stack.pop();\n"
                        "                    stack.push(a / b);",
                        "                    int a = stack.pop();\n"
                        "                    int b = stack.pop();\n"
                        "                    stack.push(a / b);")),
              _j37t("",
                    _READCODE37
                    + "        for (String line : run(code)) {\n"
                      "            System.out.println(line);\n"
                      "        }",
                    helpers=_VM37),
              [_code_case37(p) for p in _PROGS37 if any(x in ("sub", "div") for x in p)]
              + [_code_case37(["push 20", "push 4", "div", "push 3", "sub", "print"])],
              hints=["`push 7`, `push 5`: the stack has 5 on top.",
                     "The first `pop()` is therefore 5 - the RIGHT operand.",
                     "Pop `b` first, then `a`, then compute `a - b`.",
                     "The same for `div`. `add` and `mul` hid the bug because they commute."],
              difficulty="Easy"),

        _jch("j37-bc-postfix", "Compiling an expression", "Medium",
             "Write `compile(expr)`: turn a postfix expression (`3 4 + 2 *`) into "
             "instructions - a number becomes `push N`, and `+ - * /` become `add sub mul "
             "div` - followed by `print`. `main` shows the code and runs it.",
             _j37t("",
                   "        String expr = sc.nextLine();\n"
                   "        List<String[]> code = compile(expr);\n"
                   "        List<String> listing = new ArrayList<>();\n"
                   "        for (String[] ins : code) {\n"
                   "            listing.add(String.join(\" \", ins));\n"
                   "        }\n"
                   "        System.out.println(String.join(\"; \", listing));\n"
                   "        System.out.println(run(code).get(0));",
                   helpers=_VM37 + "\n\n"
                   "    static List<String[]> compile(String expr) {\n"
                   "        List<String[]> code = new ArrayList<>();\n"
                   "        for (String t : expr.trim().split(\" \")) {\n"
                   "            switch (t) {\n"
                   "                case \"+\" -> code.add(new String[] {\"add\"});\n"
                   "                case \"-\" -> code.add(new String[] {\"sub\"});\n"
                   "                case \"*\" -> code.add(new String[] {\"mul\"});\n"
                   "                case \"/\" -> code.add(new String[] {\"div\"});\n"
                   "                default -> code.add(new String[] {\"push\", t});\n"
                   "            }\n"
                   "        }\n"
                   "        code.add(new String[] {\"print\"});\n"
                   "        return code;\n"
                   "    }"),
             "    static List<String[]> compile(String expr) {\n"
             "        List<String[]> code = new ArrayList<>();\n"
             "        for (String t : expr.trim().split(\" \")) {\n"
             "            switch (t) {\n"
             "                case \"+\" -> code.add(new String[] {\"add\"});\n"
             "                case \"-\" -> code.add(new String[] {\"sub\"});\n"
             "                case \"*\" -> code.add(new String[] {\"mul\"});\n"
             "                case \"/\" -> code.add(new String[] {\"div\"});\n"
             "                default -> code.add(new String[] {\"push\", t});\n"
             "            }\n"
             "        }\n"
             "        code.add(new String[] {\"print\"});\n"
             "        return code;\n"
             "    }",
             [_lcase(e, _nl("; ".join(_postfix37(e)[0] + ["print"]), _postfix37(e)[1]))
              for e in _POSTFIX37],
             hints=["Postfix is already in instruction order - no reordering needed.",
                    "Each token becomes exactly one instruction.",
                    "An instruction is a `String[]`: `{\"push\", \"3\"}` or `{\"add\"}`.",
                    "End with `print` so the result is popped and shown.",
                    "This is, in miniature, what javac does to `a + b * 2`."]),

        _jch("j37-bc-loops", "Locals and jumps", "Hard",
             "Extend the machine with LOCAL VARIABLES and JUMPS: `load i` pushes local `i`; "
             "`store i` pops into it; `jmp L` jumps to instruction `L`; `jlt L` pops `b` "
             "then `a` and jumps to `L` if `a < b`. The programs count, compute a factorial, "
             "sum a range and more.",
             _j37t("",
                   _READCODE37
                   + "        for (String line : run(code)) {\n"
                     "            System.out.println(line);\n"
                     "        }",
                   helpers=_VM37),
             "                case \"load\" -> stack.push(locals[Integer.parseInt(ins[1])]);\n"
             "                case \"store\" -> locals[Integer.parseInt(ins[1])] = stack.pop();\n"
             "                case \"jmp\" -> pc = Integer.parseInt(ins[1]);\n"
             "                case \"jlt\" -> {\n"
             "                    int b = stack.pop();\n"
             "                    int a = stack.pop();\n"
             "                    if (a < b) {\n"
             "                        pc = Integer.parseInt(ins[1]);\n"
             "                    }\n"
             "                }",
             [_code_case37(p) for p in _LOOPS37],
             hints=["`locals` is the frame's local-variable array; the index is the "
                    "instruction's argument.",
                    "`case \"load\" -> stack.push(locals[Integer.parseInt(ins[1])]);`",
                    "`store` pops INTO the array.",
                    "The loops are a comparison and a backward `jlt` - there is no `while` "
                    "instruction.",
                    "`pc` has already moved on by the time an instruction runs, so a jump "
                    "simply overwrites it."]),
    ],
    quiz=[
        _jq("Why does a Java program usually get faster after it has been running a while?",
            ["the JIT compiles hot methods to optimised machine code",
             "the garbage collector frees memory", "class loading finishes",
             "the stack grows"],
            0,
            "It starts interpreted, and compiles what is hot."),
        _jq("A `while` loop compiles to…",
            ["a comparison and a conditional backward jump", "a while instruction",
             "recursion", "a native call"],
            0,
            "Bytecode has only jumps."),
    ],
))


# ===========================================================================
# Capstone - a tiny virtual machine with calls
# ===========================================================================

_CAPVM37 = (
    "    static List<String> execute(List<String[]> code) {\n"
    "        Deque<Integer> stack = new ArrayDeque<>();\n"
    "        Deque<int[]> frames = new ArrayDeque<>();\n"
    "        Deque<Integer> returns = new ArrayDeque<>();\n"
    "        frames.push(new int[8]);\n"
    "        int deepest = 1;\n"
    "        List<String> out = new ArrayList<>();\n"
    "        int pc = 0;\n"
    "        while (pc < code.size()) {\n"
    "            String[] ins = code.get(pc);\n"
    "            pc++;\n"
    "            int[] locals = frames.peek();\n"
    "            switch (ins[0]) {\n"
    "                case \"push\" -> stack.push(Integer.parseInt(ins[1]));\n"
    "                case \"load\" -> stack.push(locals[Integer.parseInt(ins[1])]);\n"
    "                case \"store\" -> locals[Integer.parseInt(ins[1])] = stack.pop();\n"
    "                case \"add\" -> stack.push(stack.pop() + stack.pop());\n"
    "                case \"mul\" -> stack.push(stack.pop() * stack.pop());\n"
    "                case \"sub\" -> {\n"
    "                    int b = stack.pop();\n"
    "                    int a = stack.pop();\n"
    "                    stack.push(a - b);\n"
    "                }\n"
    "                case \"jmp\" -> pc = Integer.parseInt(ins[1]);\n"
    "                case \"jlt\" -> {\n"
    "                    int b = stack.pop();\n"
    "                    int a = stack.pop();\n"
    "                    if (a < b) {\n"
    "                        pc = Integer.parseInt(ins[1]);\n"
    "                    }\n"
    "                }\n"
    "                case \"call\" -> {\n"
    "                    int[] fresh = new int[8];\n"
    "                    fresh[0] = stack.pop();\n"
    "                    frames.push(fresh);\n"
    "                    deepest = Math.max(deepest, frames.size());\n"
    "                    returns.push(pc);\n"
    "                    pc = Integer.parseInt(ins[1]);\n"
    "                }\n"
    "                case \"ret\" -> {\n"
    "                    frames.pop();\n"
    "                    pc = returns.pop();\n"
    "                }\n"
    "                case \"print\" -> out.add(String.valueOf(stack.pop()));\n"
    "                case \"halt\" -> pc = code.size();\n"
    "                default -> throw new IllegalStateException(\"bad instruction \" + ins[0]);\n"
    "            }\n"
    "        }\n"
    "        out.add(\"max frames \" + deepest);\n"
    "        return out;\n"
    "    }"
)


def _capvm37(code):
    stack, frames, rets, out, pc, deepest = [], [[0] * 8], [], [], 0, 1
    while pc < len(code):
        ins = code[pc].split()
        pc += 1
        loc = frames[-1]
        op = ins[0]
        if op == "push":
            stack.append(int(ins[1]))
        elif op == "load":
            stack.append(loc[int(ins[1])])
        elif op == "store":
            loc[int(ins[1])] = stack.pop()
        elif op == "add":
            b, a = stack.pop(), stack.pop()
            stack.append(a + b)
        elif op == "mul":
            b, a = stack.pop(), stack.pop()
            stack.append(a * b)
        elif op == "sub":
            b, a = stack.pop(), stack.pop()
            stack.append(a - b)
        elif op == "jmp":
            pc = int(ins[1])
        elif op == "jlt":
            b, a = stack.pop(), stack.pop()
            if a < b:
                pc = int(ins[1])
        elif op == "call":
            fresh = [0] * 8
            fresh[0] = stack.pop()
            frames.append(fresh)
            deepest = max(deepest, len(frames))
            rets.append(pc)
            pc = int(ins[1])
        elif op == "ret":
            frames.pop()
            pc = rets.pop()
        elif op == "print":
            out.append(str(stack.pop()))
        elif op == "halt":
            pc = len(code)
    out.append(f"max frames {deepest}")
    return out


# Programs: a "square" subroutine called twice; recursive factorial (the
# subroutine calls itself); recursive countdown; a subroutine that calls
# another; and a sum of squares 1..4 using a loop that calls a subroutine.
_CAPPROGS37 = (
    # square(4) and square(9): the subroutine starts at instruction 7
    ["push 4", "call 7", "print", "push 9", "call 7", "print", "halt",
     "load 0", "load 0", "mul", "ret"],
    # factorial(5): fact(n) = n < 2 ? 1 : n * fact(n - 1)
    ["push 5", "call 4", "print", "halt",
     "load 0", "push 2", "jlt 15",
     "load 0", "load 0", "push 1", "sub", "call 4", "mul", "ret", "halt",
     "push 1", "ret"],
    # countdown(3): print n; if 0 < n: countdown(n - 1)
    ["push 3", "call 3", "halt",
     "load 0", "print", "push 0", "load 0", "jlt 9", "ret",
     "load 0", "push 1", "sub", "call 3", "ret"],
    # quad(x) = square(square(x)) with x = 3
    ["push 3", "call 4", "print", "halt",
     "load 0", "call 8", "call 8", "ret",
     "load 0", "load 0", "mul", "ret"],
    # sum of squares 1..4 via a loop in main (locals 1 and 2) calling square
    ["push 1", "store 1", "push 0", "store 2",
     "load 2", "load 1", "call 19", "add", "store 2",
     "load 1", "push 1", "add", "store 1",
     "load 1", "push 5", "jlt 4",
     "load 2", "print", "halt",
     "load 0", "load 0", "mul", "ret"],
)

# A simplification worth knowing about: the JVM gives every frame its own
# operand stack, but this machine shares ONE operand stack and keeps only the
# locals per frame. That keeps the interpreter small, and the programs rely on
# it - the factorial pushes `n` before calling itself, and `n` is still waiting
# underneath when the call returns its result for `mul`.
for _p in _CAPPROGS37:
    _capvm37(_p)   # every capstone program must run to completion in the mirror


_M37_CAP = _jcap(
    "A virtual machine with calls",
    """
Extend lesson 37.5's machine with **method calls** - the one thing it lacks to run
real programs, and the reason a JVM has *frames*.

`execute(code)` keeps an operand stack (shared) and a **stack of frames**, each an
`int[8]` of local variables. It supports every lesson instruction (`push`,
`load`, `store`, `add`, `sub`, `mul`, `jmp`, `jlt`, `print`) plus:

* `call L` - pop one argument, push a **new frame** whose local 0 is that
  argument, remember where to come back to, and jump to `L`;
* `ret` - pop the current frame and jump back to just after the call (the return
  value, if any, is simply left on the operand stack);
* `halt` - stop.

Finally, append `max frames N`: the deepest the frame stack reached (main's frame
counts as 1).

The test programs include subroutines called twice, a subroutine calling another,
a loop calling a subroutine, and **recursion** - a factorial and a countdown -
where the frame depth grows with the input. Recursion is nothing but `call`
landing on its own code with a fresh frame.
""",
    _jch("j37-cap-vm", "A virtual machine with calls", "Hard",
         "Write `execute` as the brief describes.",
         _j37t("",
               _READCODE37
               + "        for (String line : execute(code)) {\n"
                 "            System.out.println(line);\n"
                 "        }",
               helpers=_CAPVM37),
         _CAPVM37,
         [_case("\n".join([str(len(p))] + p) + "\n", _nl(*_capvm37(p))) for p in _CAPPROGS37],
         hints=["Keep frames in a `Deque<int[]>`; the current frame is `frames.peek()`.",
                "`call`: pop the argument into a fresh frame's local 0, push the frame, push "
                "the return address (`pc`, which already points past the call), jump.",
                "`ret`: pop the frame, pop the return address into `pc`.",
                "Read `locals` from `frames.peek()` at the top of every step - a call or "
                "return changes which frame is current.",
                "Track the deepest `frames.size()` after every push.",
                "`halt` can just set `pc` past the end."]),
    example_io="stdin:  11\n        push 4\n        call 7\n        print\n        push 9\n"
               "        call 7\n        print\n        halt\n        load 0\n        load 0\n"
               "        mul\n        ret\n\n"
               "stdout: 16\n        81\n        max frames 2",
    rubric=[
        "Each call gets its own locals array; a callee cannot see its caller's locals.",
        "The return address is saved on `call` and restored on `ret`.",
        "Recursive programs work because each recursive call gets a fresh frame.",
        "`sub` pops the right-hand operand first.",
        "The maximum frame depth is tracked, with main's frame counted.",
    ],
)


_MODULES.append(_jmod(
    37, 13, "Advanced Java",
    "The JVM: class loading, memory and garbage collection",
    "What happens underneath your program - class initialisation, the stack and the "
    "heap, identity, garbage collection and bytecode - learned through the parts "
    "that are guaranteed.",
    """
The last module looks under the language, at the machine that runs it. Much of
what the JVM does is deliberately unspecified - when the collector runs, what the
JIT compiles - so the module teaches through what *is* guaranteed, and simulates
the rest.

* **Class loading and initialisation.** Classes load lazily and initialise on
  first active use: superclass statics, then subclass statics (once), then per
  object each class's instance initialisers and constructor, parent first.
  Compile-time constants never trigger initialisation, and a constructor must
  never call an overridable method.
* **The stack and the heap.** A frame per call; objects on the shared heap.
  Stack traces list frames innermost first. Deep recursion throws
  `StackOverflowError` - an `Error` - and HotSpot does not eliminate tail calls, so
  deep inputs need loops or an explicit stack.
* **Identity.** The String pool, constant folding and `intern`; the Integer cache;
  unboxing `null`; and why a `Long` never equals an `Integer`.
* **Garbage collection.** Reachability from roots, mark and sweep, why reference
  counting leaks cycles, generational and concurrent collectors - and the leaks no
  collector can fix, with an LRU cache as the cure for the commonest one.
* **Bytecode.** The JVM is a stack machine: postfix instruction order, operand
  order, jumps instead of loops, frames for calls - and the JIT that compiles the
  hot parts.
""",
    _M37,
    capstone=_M37_CAP,
    objectives=[
        "Describe loading, linking and initialisation, and when a class is initialised.",
        "Predict the order of static initialisers, instance initialisers and constructors across a hierarchy.",
        "Explain why reading a compile-time constant does not initialise its class.",
        "Explain why a constructor must not call an overridable method, and fix it.",
        "Describe stack frames and the heap, and read a stack trace as a list of frames.",
        "Explain StackOverflowError, and replace deep recursion with a loop or an explicit stack.",
        "Predict `==` results for pooled, interned, folded and runtime-built strings.",
        "Explain the Integer cache, unboxing NullPointerException, and cross-type wrapper equality.",
        "Define reachability, implement mark-and-sweep, and show why reference counting leaks cycles.",
        "Identify memory leaks in a garbage-collected language, and build an LRU cache with LinkedHashMap.",
        "Explain the JVM as a stack machine, and write an interpreter with locals, jumps and calls.",
        "Describe what the JIT does, and why warm-up matters for benchmarks.",
    ],
    why="Senior Java interviews almost always reach below the language: in what order "
        "does this print, why is this string comparison true, how does garbage "
        "collection decide what to free, can Java leak memory, what is on the stack and "
        "what is on the heap, what is bytecode, why is my benchmark wrong. An LRU cache "
        "and a stack-machine interpreter are also both standard coding questions in their "
        "own right - here they arrive with the understanding of why the JVM needs them.",
    est_minutes=330,
    glossary=[
        _jg("Class loader", "Finds a class's bytecode and defines the class in the JVM, "
                            "on first need."),
        _jg("Class initialisation", "Running a class's static initialisers - once, on "
                                    "first active use, superclass first."),
        _jg("Instance initialiser", "A `{ }` block or field initialiser, run after "
                                    "`super(...)` returns and before the constructor body."),
        _jg("Constant variable", "A final primitive or String initialised with a constant "
                                 "expression; its value is inlined by the compiler."),
        _jg("Stack frame", "The per-call record of parameters, locals and the operand "
                           "stack."),
        _jg("Heap", "The shared memory where every object and array lives."),
        _jg("StackOverflowError", "Thrown when a thread's stack is exhausted, usually by "
                                  "runaway or too-deep recursion."),
        _jg("String pool", "The JVM's table of interned strings; every literal is "
                           "pooled."),
        _jg("Constant folding", "The compiler computing a constant expression - such as "
                                "`\"ja\" + \"va\"` - at compile time."),
        _jg("GC roots", "Local variables of live frames, static fields and JVM "
                        "internals - where reachability starts."),
        _jg("Mark and sweep", "Mark every object reachable from the roots; free the rest."),
        _jg("Reference counting", "Freeing an object when its count of incoming "
                                  "references reaches zero; leaks cycles."),
        _jg("Generational GC", "Collecting young objects often and old ones rarely, "
                               "because most objects die young."),
        _jg("LRU cache", "A bounded cache evicting the least recently used entry."),
        _jg("Bytecode", "The JVM's instruction set - portable instructions for a stack "
                        "machine."),
        _jg("JIT compiler", "Compiles frequently run bytecode to optimised native code "
                            "while the program runs."),
    ],
    cheatsheet="""
```java
// --- initialisation order (first `new Child()`) -------------------------------
// static Parent, static Child                 (once per class, superclass first)
// Parent field inits + { } blocks, Parent()   (per object)
// Child  field inits + { } blocks, Child()
static final int MAX = 10;     // constant: reading it does NOT initialise the class
Widget() { describe(); }       // NEVER: subclass fields are still default here

// --- stack and heap ------------------------------------------------------------
e.getStackTrace()              // frames, innermost first
catch (StackOverflowError e)   // an Error: catch (Exception) misses it
// no tail-call elimination: deep input -> loop, or an explicit ArrayDeque

// --- identity -----------------------------------------------------------------------
"java" == "java"                    // true  (pooled literals)
new String("java") == "java"        // false
new String("java").intern() == "java"   // true
"ja" + "va" == "java"               // true  (folded)
final String p = "ja"; p + "va" == "java"   // true;  without final: false
Integer a = 127, b = 127; a == b    // true; 128: false  (cache)
int n = map.get(k);                 // NPE if absent: getOrDefault
Long.valueOf(1).equals(1)           // false: compare longValue()

// --- GC ---------------------------------------------------------------------------------
// live = reachable from roots; cycles with no root path are garbage
// leaks = reachable but useless: static caches, listeners, inner-class pins
Map<K, V> lru = new LinkedHashMap<>(16, 0.75f, true) {
    protected boolean removeEldestEntry(Map.Entry<K, V> e) { return size() > cap; }
};

// --- bytecode (javap -c) --------------------------------------------------------------
// a + b * 2  ->  iload a, iload b, iconst_2, imul, iadd     (postfix)
// isub: pop b, pop a, push a - b                             (order matters)
// loops: compare + conditional backward jump (if_icmplt / goto)
```
""",
    self_check=[
        "Can you give the full initialisation order for the first and second `new Child()`?",
        "Can you explain why reading `Limits.MAX` may not run `Limits`'s static block?",
        "Can you explain what goes wrong when a constructor calls an overridable method?",
        "Can you say what lives in a stack frame and what lives on the heap?",
        "Can you read a stack trace, and say which end is where the exception was thrown?",
        "Can you explain why deep recursion overflows even when it is a tail call?",
        "Can you predict `==` for literals, `new String`, `intern`, and constant versus runtime concatenation?",
        "Can you explain why `int n = map.get(k)` can throw NullPointerException?",
        "Can you implement mark-and-sweep, and show a cycle reference counting cannot free?",
        "Can you name three kinds of memory leak in Java, and build an LRU cache?",
        "Can you translate an expression into stack-machine instructions, and interpret them?",
        "Can you explain why a Java program speeds up as it runs?",
    ],
    review=[
        _jq("```java\nclass A { static { System.out.print(\"A\"); } }\nclass B extends A { static { System.out.print(\"B\"); } }\n```\n`new B(); new B();` prints (statics only)…",
            ["AB", "ABAB", "BA", "B"],
            0,
            "Each class is initialised once, superclass first."),
        _jq("A superclass constructor calls a method the subclass overrides. The override "
            "sees the subclass's fields…",
            ["at their default values", "fully initialised", "as null only if static",
             "as a compile error"],
            0,
            "Subclass field initialisers have not run yet."),
        _jq("`String s = \"a\"; String t = s + \"b\"; t == \"ab\"` is…",
            ["false", "true", "a compile error", "an exception"],
            0,
            "`s` is not a constant, so the concatenation runs at run time."),
        _jq("A reference-counting collector cannot reclaim…",
            ["a cycle of objects no root can reach", "an object with no references",
             "a large array", "a String"],
            0,
            "Tracing collectors can."),
        _jq("The JVM's `isub` pops `x` and then `y`. It pushes…",
            ["y - x", "x - y", "x + y", "|x - y|"],
            0,
            "The first pop is the right-hand operand."),
    ],
    milestone="You can explain what the JVM does beneath your code - when classes "
              "initialise, what lives on the stack and the heap, why two equal strings "
              "may or may not be the same object, how garbage is found, and what bytecode "
              "a line of Java becomes - and you have built an LRU cache, a mark-and-sweep "
              "pass and a small virtual machine to prove it. That closes Part 13, and the "
              "Java course.",
))
