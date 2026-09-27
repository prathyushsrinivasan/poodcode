# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 35 - Design patterns.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# THE ANGLE: not the Gang of Four catalogue recited, but the dozen patterns a
# Java interview actually reaches for, each introduced by the PROBLEM it solves
# and written the way modern Java writes it - a lambda where the pattern is
# really "pass a function", an enum where it is really "one instance", a static
# nested Builder where it is really "named, optional parameters".
#
#   35.1 creational   - static factories, caching factories, Builder
#   35.2 one instance - singleton (holder idiom, enum), and why dependency
#                       injection is usually the better answer
#   35.3 behaviour    - strategy, command, undo, macro commands
#   35.4 observer     - listeners, unsubscribing, and the
#                       ConcurrentModificationException it is famous for
#   35.5 structure    - decorator, adapter, composite
#
# Every earlier feature is fair game (nothing is gated any more): records,
# sealed types and pattern switches from 34, enums and nested classes from 33,
# lambdas from 25, the concurrent collections from 31.
#
# JUDGING NOTES
#   * The holder-idiom lesson PRINTS from a constructor to show when a class is
#     initialised. JLS 12.4.1 fixes that moment (first active use), so the
#     output is deterministic.
#   * The observer CME exercise removes the FIRST of three listeners during
#     iteration, which is the position that deterministically throws (removing
#     the second-to-last one would end the loop silently instead).
# ---------------------------------------------------------------------------

_M35 = []

_IMPORTS35 = ("import java.util.*;\n"
              "import java.util.concurrent.*;\n"
              "import java.util.function.*;\n")


def _j35s(body):
    return _jscan(body, imports=_IMPORTS35)


def _j35t(types, body):
    return _joop(types, body, imports=_IMPORTS35)


def _j35th(types, helpers, body):
    return _jp(
        _IMPORTS35 + "\n"
        + types.strip("\n") + "\n\n"
        + "public class Main {\n"
        + helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }\n}"
    )


def _rows35(rows, out):
    stdin = "\n".join([str(len(rows))] + [" ".join(str(t) for t in r) for r in rows])
    return _case(stdin, out)


def _toks35(ts, out):
    return _case("\n".join([str(len(ts)), " ".join(ts)]), out)


def _body35(src):
    """The inside of the single top-level type in `src` (without its braces)."""
    lines = src.strip("\n").split("\n")
    return "\n".join(lines[1:-1])


# ===========================================================================
# 35.1 Creating objects
# ===========================================================================

_TEMP35 = """
class Temperature {
    private final int celsius;

    private Temperature(int celsius) {
        this.celsius = celsius;
    }

    static Temperature ofCelsius(int c) {
        return new Temperature(c);
    }

    static Temperature ofFahrenheit(int f) {
        return new Temperature((f - 32) * 5 / 9);
    }

    int celsius() {
        return celsius;
    }
}
"""
_TEMPS35 = ([("C", 20), ("F", 212)], [("F", 32)], [("C", -5), ("F", 50), ("F", 0)],
            [("C", 100)], [("F", 98), ("C", 37)])


def _temp35(u, v):
    return v if u == "C" else _jdiv((v - 32) * 5, 9)


_TAG35 = """
class Tag {
    private static final Map<String, Tag> CACHE = new HashMap<>();

    private final String name;

    private Tag(String name) {
        this.name = name;
    }

    static Tag of(String name) {
        return CACHE.computeIfAbsent(name, Tag::new);
    }

    static int created() {
        return CACHE.size();
    }
}
"""
_TAGPAIRS35 = ([("java", "java"), ("java", "rust")], [("x", "y")],
               [("a", "a"), ("b", "b"), ("a", "b")], [("go", "go"), ("go", "go")],
               [("p", "q"), ("q", "r"), ("r", "p")])


def _tags_out35(rows):
    seen = set()
    out = []
    for (a, b) in rows:
        seen.add(a)
        seen.add(b)
        out.append(_jbool(a == b))
    return _nl(*out, f"created {len(seen)}")


_PIZZA35 = """
class Pizza {
    private final String size;
    private final List<String> toppings;
    private final boolean extraCheese;

    private Pizza(Builder b) {
        this.size = b.size;
        this.toppings = List.copyOf(b.toppings);
        this.extraCheese = b.extraCheese;
    }

    @Override
    public String toString() {
        return size + " pizza with "
                + (toppings.isEmpty() ? "no toppings" : String.join(", ", toppings))
                + (extraCheese ? " and extra cheese" : "");
    }

    static class Builder {
        private final String size;
        private final List<String> toppings = new ArrayList<>();
        private boolean extraCheese;

        Builder(String size) {
            this.size = Objects.requireNonNull(size);
        }

        Builder topping(String t) {
            toppings.add(t);
            return this;
        }

        Builder extraCheese() {
            extraCheese = true;
            return this;
        }

        Pizza build() {
            if (toppings.size() > 3) {
                throw new IllegalStateException("too many toppings");
            }
            return new Pizza(this);
        }
    }
}
"""
_PIZZA_REGION35 = _PIZZA35[_PIZZA35.index("    static class Builder {"):].rstrip("\n")
_PIZZA_REGION35 = _PIZZA_REGION35[:_PIZZA_REGION35.rstrip().rfind("}")].rstrip()

_PIZZAS35 = (("large", ["ham", "olive"], "cheese"), ("small", [], "plain"),
             ("medium", ["a", "b", "c", "d"], "cheese"), ("large", ["mushroom"], "plain"),
             ("small", ["x", "y", "z"], "cheese"))


def _pizza_case35(size, tops, flag):
    stdin = f"{size}\n{len(tops)}\n{' '.join(tops)}\n{flag}" if tops else f"{size}\n0\n{flag}"
    if len(tops) > 3:
        out = "rejected: too many toppings"
    else:
        out = (f"{size} pizza with " + (", ".join(tops) if tops else "no toppings")
               + (" and extra cheese" if flag == "cheese" else ""))
    return _case(stdin, out)


_SANDWICH35 = """
class Sandwich {
    private final String bread;
    private final List<String> fillings;

    Sandwich(String bread, List<String> fillings) {
        this.bread = bread;
        this.fillings = fillings;
    }

    @Override
    public String toString() {
        return bread + " " + fillings;
    }

    static class Builder {
        private final String bread;
        private final List<String> fillings = new ArrayList<>();

        Builder(String bread) {
            this.bread = bread;
        }

        Builder add(String filling) {
            fillings.add(filling);
            return this;
        }

        Sandwich build() {
            return new Sandwich(bread, new ArrayList<>(fillings));
        }
    }
}
"""
_SANDWICHES35 = (("rye", ["ham"], ["egg"]), ("white", ["a", "b"], ["c"]), ("wrap", ["x"], ["y", "z"]),
                 ("bagel", ["lox", "caper"], ["onion", "dill"]), ("sub", ["tuna"], ["corn"]))


def _sandwich_case35(bread, first, more):
    stdin = f"{bread}\n{len(first)} {' '.join(first)}\n{len(more)} {' '.join(more)}"
    return _case(stdin, _nl(f"{bread} {_jarr(first)}", f"{bread} {_jarr(first + more)}"))


_M35.append(_jlesson(
    "m35-create", "Creating objects: factories and builders",
    "When `new` with a parameter list stops being enough.",
    """
A constructor has three limits: it has no name of its own, it must return a
brand-new object of exactly its class, and a long parameter list of the same
types is unreadable at the call site. The creational patterns each lift one.

## Static factory methods

```java
class Temperature {
    private Temperature(int celsius) { ... }            // private: use the factories
    static Temperature ofCelsius(int c)    { return new Temperature(c); }
    static Temperature ofFahrenheit(int f) { return new Temperature((f - 32) * 5 / 9); }
}
```

Two constructors both taking one `int` cannot coexist - but two *named*
factories can, and the call site says which unit it means. A factory can also
**return an existing object** instead of a new one:

```java
static Tag of(String name) {
    return CACHE.computeIfAbsent(name, Tag::new);       // one Tag per name, ever
}
```

The JDK is full of these: `List.of`, `Optional.of`, `LocalDate.of`,
`Integer.valueOf` - which caches every value from -128 to 127, and is why
`Integer a = 100, b = 100; a == b` is `true` while the same with 1000 is `false`.
(The conventional names: `of` and `from` for conversions, `valueOf`, `getInstance`,
`newInstance` when it is always fresh.)

## Builder

```java
Pizza p = new Pizza.Builder("large")
        .topping("ham")
        .topping("olive")
        .extraCheese()
        .build();
```

A builder is a **static nested class** (module 33) that collects the arguments
one named call at a time - each setter returns `this`, so the calls chain - and
`build()` checks the rules and creates the finished, immutable object in one go.
It replaces two bad alternatives: *telescoping constructors*
(`Pizza(size)`, `Pizza(size, toppings)`, `Pizza(size, toppings, cheese)`, ...)
and a setter-based object that exists, half-built and invalid, between its
constructor and its last setter.

The builder is mutable and the product is not - so **`build()` must copy** any
collection it hands over. Otherwise the builder and every object it built share
one list, and adding to the builder quietly changes pizzas already made.

(Records from module 34 cover the simple case: a record with a compact
constructor is often all the "builder" a small value needs.)
""",
    warmup=[
        _jq("Why can't a class have both `Temperature(int celsius)` and "
            "`Temperature(int fahrenheit)`?",
            ["they have the same signature - a static factory can use two names instead",
             "ints cannot be parameters", "constructors cannot be overloaded",
             "it can"],
            0,
            "Overloads are told apart by parameter types, never by names."),
        _jq("Each setter on a Builder returns…",
            ["this, so the calls can be chained", "void", "a new Builder",
             "the finished object"],
            0,
            "`build()` is the only call that returns the product."),
    ],
    exercises=[
        _je("j35-cr-factory", "Named constructors",
            "`Temperature` has a private constructor and two named factories. Build each "
            "reading through the right one and print it in Celsius. Replace `____` with the "
            "Fahrenheit factory call.",
            _j35t(_TEMP35,
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            String unit = sc.next();\n"
                  "            int v = sc.nextInt();\n"
                  "            Temperature t = unit.equals(\"C\") ? Temperature.ofCelsius(v) : Temperature.ofFahrenheit(v);\n"
                  "            System.out.println(t.celsius() + \" C\");\n"
                  "        }"),
            "Temperature.ofFahrenheit(v)",
            [_rows35(rows, _nl(*[f"{_temp35(u, v)} C" for (u, v) in rows])) for rows in _TEMPS35],
            hints=["The constructor is private, so `new Temperature(...)` does not compile "
                   "here.",
                   "Factories are static: call them on the class.",
                   "`Temperature.ofFahrenheit(v)`",
                   "The name says which unit the int is in - a constructor could not."],
            difficulty="Easy"),

        _je("j35-cr-cache", "A factory that remembers",
            "`Tag.of(name)` must return THE SAME object for the same name, so tags can be "
            "compared with `==`. Replace `____` with its one-line body.",
            _j35t(_TAG35,
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            System.out.println(Tag.of(sc.next()) == Tag.of(sc.next()));\n"
                  "        }\n"
                  "        System.out.println(\"created \" + Tag.created());"),
            "        return CACHE.computeIfAbsent(name, Tag::new);",
            [_rows35(rows, _tags_out35(rows)) for rows in _TAGPAIRS35],
            hints=["Look the name up; create a Tag only if it is missing.",
                   "`computeIfAbsent(key, function)` does both in one call.",
                   "`Tag::new` is a constructor reference - allowed here even though the "
                   "constructor is private, because this code is inside Tag.",
                   "`Integer.valueOf` does exactly this for -128..127."],
            difficulty="Medium"),

        _jch("j35-cr-builder", "A pizza builder", "Medium",
             "Write `Pizza.Builder`: a static nested class taking the required size in its "
             "constructor, with chainable `topping(t)` and `extraCheese()`, and a `build()` "
             "that throws `IllegalStateException(\"too many toppings\")` above three.",
             _j35t(_PIZZA35,
                   "        String size = sc.next();\n"
                   "        int n = sc.nextInt();\n"
                   "        Pizza.Builder b = new Pizza.Builder(size);\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            b.topping(sc.next());\n"
                   "        }\n"
                   "        if (sc.next().equals(\"cheese\")) {\n"
                   "            b.extraCheese();\n"
                   "        }\n"
                   "        try {\n"
                   "            System.out.println(b.build());\n"
                   "        } catch (IllegalStateException e) {\n"
                   "            System.out.println(\"rejected: \" + e.getMessage());\n"
                   "        }"),
             _PIZZA_REGION35,
             [_pizza_case35(*p) for p in _PIZZAS35],
             hints=["`static class Builder` - static, because it needs no existing Pizza.",
                    "The required size is a constructor parameter; everything optional is "
                    "a method.",
                    "Each optional method ends `return this;`.",
                    "`Pizza`'s private constructor reads `b.size`, `b.toppings` and "
                    "`b.extraCheese` - so name the fields exactly that.",
                    "`build()` validates, then `return new Pizza(this);`."]),

        _jfix("j35-cr-shared", "Two sandwiches, one list",
              "The builder makes one sandwich, gets two more fillings, and makes another - "
              "but the FIRST sandwich changes too, because `build()` hands over the "
              "builder's own list. Make `build()` hand over a copy.",
              _j35t(_SANDWICH35.replace("new Sandwich(bread, new ArrayList<>(fillings))",
                                        "new Sandwich(bread, fillings)"),
                    "        Sandwich.Builder b = new Sandwich.Builder(sc.next());\n"
                    "        int k = sc.nextInt();\n"
                    "        for (int i = 0; i < k; i++) {\n"
                    "            b.add(sc.next());\n"
                    "        }\n"
                    "        Sandwich first = b.build();\n"
                    "        int m = sc.nextInt();\n"
                    "        for (int i = 0; i < m; i++) {\n"
                    "            b.add(sc.next());\n"
                    "        }\n"
                    "        Sandwich second = b.build();\n"
                    "        System.out.println(first);\n"
                    "        System.out.println(second);"),
              _j35t(_SANDWICH35,
                    "        Sandwich.Builder b = new Sandwich.Builder(sc.next());\n"
                    "        int k = sc.nextInt();\n"
                    "        for (int i = 0; i < k; i++) {\n"
                    "            b.add(sc.next());\n"
                    "        }\n"
                    "        Sandwich first = b.build();\n"
                    "        int m = sc.nextInt();\n"
                    "        for (int i = 0; i < m; i++) {\n"
                    "            b.add(sc.next());\n"
                    "        }\n"
                    "        Sandwich second = b.build();\n"
                    "        System.out.println(first);\n"
                    "        System.out.println(second);"),
              [_sandwich_case35(*s) for s in _SANDWICHES35],
              hints=["Both sandwiches hold a reference to the builder's ONE list.",
                     "Adding to the builder after the first `build()` changes the first "
                     "sandwich.",
                     "`new Sandwich(bread, new ArrayList<>(fillings))` - each product gets "
                     "its own list.",
                     "`List.copyOf(fillings)` would also work, and make the copy "
                     "unmodifiable."],
              difficulty="Medium"),
    ],
    quiz=[
        _jq("`Integer a = 1000, b = 1000; a == b` is false, but with 100 it is true, "
            "because…",
            ["Integer.valueOf caches -128..127 and autoboxing calls it",
             "of a JVM bug", "100 is a constant", "== compares values for small numbers"],
            0,
            "A static factory with a cache. Compare boxed values with equals."),
        _jq("The main advantage of a Builder over a constructor with many parameters is…",
            ["named, optional arguments and a single validation point in build()",
             "speed", "it avoids objects", "it makes the product mutable"],
            0,
            "And the product never exists half-built."),
    ],
))


# ===========================================================================
# 35.2 One instance
# ===========================================================================

_REGISTRY35 = """
enum Registry {
    INSTANCE;

    private final List<String> names = new ArrayList<>();

    void register(String name) {
        if (!names.contains(name)) {
            names.add(name);
        }
    }

    List<String> names() {
        return List.copyOf(names);
    }
}
"""
_SIGNUPS35 = (["ada", "bo", "ada"], ["solo"], ["x", "y", "z", "x", "y"], ["m", "m", "m"],
              ["pear", "fig", "plum"])


def _signups_out35(ts):
    seen = []
    for t in ts:
        if t not in seen:
            seen.append(t)
    return _jarr(seen)


_CONFIG35 = """
class Config {
    private int calls;

    private Config() {
        System.out.println("loading config");
    }

    private static class Holder {
        static final Config INSTANCE = new Config();
    }

    static Config get() {
        return Holder.INSTANCE;
    }

    int next() {
        return ++calls;
    }
}
"""
_CONFIG_REGION35 = (
    "    private static class Holder {\n"
    "        static final Config INSTANCE = new Config();\n"
    "    }\n"
    "\n"
    "    static Config get() {\n"
    "        return Holder.INSTANCE;\n"
    "    }"
)


def _config_out35(n):
    lines = ["start"]
    if n:
        lines.append("loading config")
        lines += [str(i) for i in range(1, n + 1)]
    lines.append("done")
    return _nl(*lines)


_COUNTER35 = """
class Counter {
    static final Counter INSTANCE = new Counter();

    private int count;

    private Counter() {
    }

    void hit() {
        count++;
    }

    int count() {
        return count;
    }
}
"""
_PAGES35 = (["home", "about"], ["home"], ["a", "b", "c", "a"], ["x", "x", "x"], ["one", "two", "three", "four", "five"])

_GREETER35 = """
interface Clock {
    int hour();
}

class FixedClock implements Clock {
    private final int hour;

    FixedClock(int hour) {
        this.hour = hour;
    }

    public int hour() {
        return hour;
    }
}

class Greeter {
    private final Clock clock;

    Greeter(Clock clock) {
        this.clock = clock;
    }

    String greet(String name) {
        int h = clock.hour();
        String part = h < 12 ? "morning" : h < 18 ? "afternoon" : "evening";
        return "Good " + part + ", " + name;
    }
}
"""
_GREETER_REGION35 = _GREETER35[_GREETER35.index("class Greeter {"):].strip("\n")
_HOURS35 = ([(9, "ada")], [(12, "bo"), (17, "cy")], [(18, "di"), (0, "ed")], [(23, "solo")],
            [(11, "x"), (13, "y"), (20, "z")])


def _greet35(h, name):
    part = "morning" if h < 12 else ("afternoon" if h < 18 else "evening")
    return f"Good {part}, {name}"


_M35.append(_jlesson(
    "m35-single", "One instance: singletons, and the better answer",
    "How to guarantee exactly one object - and why you usually should not.",
    """
Some things there should be exactly one of in a program: a configuration, a
registry, a connection pool. The **singleton** pattern guarantees it.

## Three ways to write one

```java
// 1. Eager: created when the class is initialised.
class Counter {
    static final Counter INSTANCE = new Counter();
    private Counter() { }            // private: nobody else can make one
}

// 2. Lazy, with the holder idiom: created on first use, thread-safe for free.
class Config {
    private Config() { ... }
    private static class Holder {
        static final Config INSTANCE = new Config();
    }
    static Config get() { return Holder.INSTANCE; }
}

// 3. An enum with one constant.
enum Registry {
    INSTANCE;
    void register(String name) { ... }
}
```

The **holder idiom** leans on a JVM guarantee: a class is initialised the first
time it is actually used, exactly once, with the JVM holding a lock while it
does so. `Holder` is not touched until `get()` runs, so `Config` is built lazily
- and no `synchronized`, no double-checked locking, no `volatile` is needed.

The **enum** version is the one *Effective Java* recommends: the JVM guarantees
one instance, and it cannot be broken by reflection or by serialisation (both of
which can create a second instance of a class with a private constructor).

## Why a singleton is usually the wrong answer

A singleton is a global variable with good manners. Code that calls
`Config.get()` from deep inside a method has a **hidden dependency**: nothing in
its signature says it needs a configuration, and a test cannot hand it a
different one.

The alternative is **dependency injection** - pass the collaborator in:

```java
class Greeter {
    private final Clock clock;
    Greeter(Clock clock) { this.clock = clock; }          // the dependency is visible
    String greet(String name) { int h = clock.hour(); ... }
}

new Greeter(new SystemClock());      // in the program
new Greeter(new FixedClock(9));      // in a test: 9 o'clock, every time
```

The program may still create only one `SystemClock` - but that is now a decision
made in one place, not a restriction baked into the class. Frameworks such as
Spring are, at heart, machinery for doing exactly this at scale.
""",
    warmup=[
        _jq("The holder idiom creates its instance…",
            ["the first time get() is called", "when the program starts",
             "every time get() is called", "when the outer class is loaded"],
            0,
            "Holder is only initialised on its first active use."),
        _jq("The biggest practical problem with a singleton is…",
            ["hidden global state that tests cannot substitute", "memory use",
             "it is slow", "it cannot have methods"],
            0,
            "Pass the dependency in instead, and the problem disappears."),
    ],
    exercises=[
        _je("j35-si-enum", "The enum singleton",
            "Every sign-up goes to the one `Registry`, which ignores repeats. Replace "
            "`____` with the call inside `signUp`.",
            _j35th(_REGISTRY35,
                   "    static void signUp(String name) {\n"
                   "        Registry.INSTANCE.register(name);\n"
                   "    }",
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            signUp(sc.next());\n"
                   "        }\n"
                   "        System.out.println(Registry.INSTANCE.names());"),
            "        Registry.INSTANCE.register(name);",
            [_toks35(ts, _signups_out35(ts)) for ts in _SIGNUPS35],
            hints=["The single instance is the enum constant `INSTANCE`.",
                   "`Registry.INSTANCE.register(name);`",
                   "There is no way to make a second Registry - not even with reflection.",
                   "`names()` returns a copy, so callers cannot change the registry behind "
                   "its back."],
            difficulty="Easy"),

        _jch("j35-si-holder", "Lazy, by the holder idiom", "Medium",
             "Make `Config` a lazily created singleton using a private static nested "
             "`Holder` class and a static `get()`. Its constructor announces itself, so the "
             "output shows exactly when - and how often - it runs.",
             _j35t(_CONFIG35,
                   "        int n = sc.nextInt();\n"
                   "        System.out.println(\"start\");\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            System.out.println(Config.get().next());\n"
                   "        }\n"
                   "        System.out.println(\"done\");"),
             _CONFIG_REGION35,
             [_case(str(n), _config_out35(n)) for n in (3, 0, 1, 5, 2)],
             hints=["`private static class Holder { static final Config INSTANCE = new "
                    "Config(); }`",
                    "`static Config get() { return Holder.INSTANCE; }`",
                    "`loading config` appears AFTER `start` - Holder is not initialised "
                    "until `get()` first touches it.",
                    "With zero calls it never appears at all.",
                    "The JVM initialises a class once, under a lock - that is the thread "
                    "safety, for free."]),

        _jfix("j35-si-public", "The second counter",
              "Every page visit should go to the one `Counter`, but `visit` creates a fresh "
              "counter each time, so the total stays 0 - which the constructor being "
              "non-private allowed. Make the constructor private and route visits through "
              "the instance.",
              _j35th(_COUNTER35.replace("    private Counter() {", "    Counter() {"),
                     "    static void visit(String page) {\n"
                     "        new Counter().hit();\n"
                     "    }",
                     "        int n = sc.nextInt();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            visit(sc.next());\n"
                     "        }\n"
                     "        System.out.println(Counter.INSTANCE.count());"),
              _j35th(_COUNTER35,
                     "    static void visit(String page) {\n"
                     "        Counter.INSTANCE.hit();\n"
                     "    }",
                     "        int n = sc.nextInt();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            visit(sc.next());\n"
                     "        }\n"
                     "        System.out.println(Counter.INSTANCE.count());"),
              [_toks35(ts, len(ts)) for ts in _PAGES35],
              hints=["A singleton's constructor must be private - or anyone can make "
                     "another.",
                     "Each `new Counter()` is counted and then thrown away.",
                     "`Counter.INSTANCE.hit();`",
                     "With the constructor private, the bug would not even have compiled."],
              difficulty="Easy"),

        _jch("j35-si-inject", "Inject the clock", "Medium",
             "Write `Greeter`: it receives a `Clock` in its constructor and greets with "
             "`Good morning` before 12, `Good afternoon` before 18, and `Good evening` "
             "after that. `main` injects a `FixedClock`, so every run is repeatable.",
             _j35t(_GREETER35,
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            int hour = sc.nextInt();\n"
                   "            Greeter g = new Greeter(new FixedClock(hour));\n"
                   "            System.out.println(g.greet(sc.next()));\n"
                   "        }"),
             _GREETER_REGION35,
             [_rows35(rows, _nl(*[_greet35(h, nm) for (h, nm) in rows])) for rows in _HOURS35],
             hints=["The Greeter never asks what time it is - it is told, through `Clock`.",
                    "Store the clock in a `private final` field from the constructor.",
                    "`h < 12 ? \"morning\" : h < 18 ? \"afternoon\" : \"evening\"`",
                    "In the real program you would pass a clock reading the system time; "
                    "here a fixed one makes the output testable."]),
    ],
    quiz=[
        _jq("Why is an enum the safest singleton?",
            ["the JVM guarantees one instance, even against reflection and serialisation",
             "enums are faster", "enums are lazy", "enums have no fields"],
            0,
            "A private constructor alone can be defeated by both."),
        _jq("Dependency injection means…",
            ["passing collaborators in, usually through the constructor",
             "a framework is required", "using static fields", "using reflection"],
            0,
            "Frameworks help at scale; the idea is just a constructor parameter."),
    ],
))


# ===========================================================================
# 35.3 Strategy and command
# ===========================================================================

_PRICES35 = ([(100, "none"), (100, "half")], [(55, "minus10")], [(5, "minus10"), (9, "half"), (0, "none")],
             [(1000, "half"), (1000, "minus10")], [(37, "none"), (37, "half"), (37, "minus10")])


def _price35(p, s):
    return p if s == "none" else (p // 2 if s == "half" else max(0, p - 10))


_SHIP35 = """
interface ShippingPolicy {
    int cost(int kilos);
}

class FlatRate implements ShippingPolicy {
    public int cost(int kilos) {
        return 500;
    }
}

class PerKilo implements ShippingPolicy {
    private final int rate;

    PerKilo(int rate) {
        this.rate = rate;
    }

    public int cost(int kilos) {
        return rate * kilos;
    }
}

class FreeOver implements ShippingPolicy {
    private final int threshold;
    private final ShippingPolicy otherwise;

    FreeOver(int threshold, ShippingPolicy otherwise) {
        this.threshold = threshold;
        this.otherwise = otherwise;
    }

    public int cost(int kilos) {
        return kilos >= threshold ? 0 : otherwise.cost(kilos);
    }
}
"""
_SHIP_REGION35 = _SHIP35[_SHIP35.index("class FlatRate"):].strip("\n")
_SHIPROWS35 = ([("flat", 3), ("perkilo", 3)], [("free", 12)], [("free", 2), ("perkilo", 0)],
               [("flat", 50), ("free", 10), ("free", 9)], [("perkilo", 7)])


def _ship35(p, k):
    if p == "flat":
        return 500
    if p == "perkilo":
        return 120 * k
    return 0 if k >= 10 else 120 * k


_CMD35 = """
interface Command {
    void execute();

    void undo();
}

class Append implements Command {
    private final StringBuilder text;
    private final String piece;

    Append(StringBuilder text, String piece) {
        this.text = text;
        this.piece = piece;
    }

    public void execute() {
        text.append(piece);
    }

    public void undo() {
        text.setLength(text.length() - piece.length());
    }
}
"""
_EDITS35 = ([("add", "ab"), ("add", "cd"), ("undo",)], [("undo",), ("add", "x")],
            [("add", "a"), ("add", "b"), ("add", "c"), ("undo",), ("undo",), ("add", "z")],
            [("add", "hello"), ("undo",), ("undo",)], [("add", "q"), ("add", "rs"), ("undo",), ("add", "t")])


def _edits_out35(ops):
    text, hist, out = "", [], []
    for op in ops:
        if op[0] == "add":
            text += op[1]
            hist.append(op[1])
        elif hist:
            text = text[:len(text) - len(hist.pop())]
        out.append(text or "(empty)")
    return _nl(*out)


_WRAP35 = """
class Wrap implements Command {
    private final StringBuilder text;

    Wrap(StringBuilder text) {
        this.text = text;
    }

    public void execute() {
        text.insert(0, '[').append(']');
    }

    public void undo() {
        text.deleteCharAt(text.length() - 1).deleteCharAt(0);
    }
}

class Macro implements Command {
    private final List<Command> steps;

    Macro(List<Command> steps) {
        this.steps = List.copyOf(steps);
    }

    public void execute() {
        for (Command c : steps) {
            c.execute();
        }
    }

    public void undo() {
        for (int i = steps.size() - 1; i >= 0; i--) {
            steps.get(i).undo();
        }
    }
}
"""
_MACRO_REGION35 = _WRAP35[_WRAP35.index("class Macro"):].strip("\n")
_MACROS35 = ([["+a", "w"], ["+b"]], [["w", "w"]], [["+x", "+y", "w"], ["+z", "w"]],
             [["+hi"]], [["w", "+a"], ["+b", "w", "+c"]])


def _apply35(text, op):
    return text + op[1:] if op[0] == "+" else "[" + text + "]"


def _unapply35(text, op):
    return text[:len(text) - len(op) + 1] if op[0] == "+" else text[1:-1]


def _macros_out35(macros):
    text, out = "", []
    for m in macros:
        for op in m:
            text = _apply35(text, op)
        out.append(text)
    for m in reversed(macros):
        for op in reversed(m):
            text = _unapply35(text, op)
        out.append(text or "(empty)")
    return _nl(*out)


def _macro_case35(macros):
    stdin = "\n".join([str(len(macros))] + [" ".join([str(len(m))] + m) for m in macros])
    return _case(stdin, _macros_out35(macros))


_M35.append(_jlesson(
    "m35-behaviour", "Strategy and command: behaviour as an object",
    "Choose an algorithm at run time; record an action so it can be undone.",
    """
## Strategy

A **strategy** is an interchangeable algorithm behind one interface. You have
used one since module 20 - a `Comparator` is a sorting strategy - and module
33's `Op` enum was one too. When the strategy is a single method, a lambda is
the whole pattern:

```java
Map<String, IntUnaryOperator> discounts = new HashMap<>();
discounts.put("none", p -> p);
discounts.put("half", p -> p / 2);
int price = discounts.get(name).applyAsInt(base);      // chosen at run time
```

When a strategy has state or several methods, it is a class implementing the
interface - and strategies **compose**, because one can hold another:

```java
new FreeOver(10, new PerKilo(120))    // free above 10 kg, otherwise 120 per kilo
```

The payoff is the **open/closed principle**: add a new discount or shipping rule
by adding a class or a map entry, without editing the code that uses them. The
tell-tale smell a strategy removes is a growing `if/else` or `switch` on a
"type" string, repeated in several places.

## Command

A **command** turns an action into an object - so it can be stored, queued,
logged, replayed, or **undone**:

```java
interface Command { void execute(); void undo(); }

Deque<Command> history = new ArrayDeque<>();
Command c = new Append(text, "ab");
c.execute();
history.push(c);
...
history.pop().undo();          // the most recent action, reversed
```

Each command remembers enough to reverse itself. A stack of executed commands
is an undo history; a second stack of undone ones is redo.

A **macro command** is a command made of commands. Executing it runs the steps
in order; undoing it must run their undos in **reverse** order - the last thing
done is the first thing undone, exactly as with the history stack.
""",
    warmup=[
        _jq("`Comparator` is an example of…",
            ["the strategy pattern", "the singleton pattern", "the builder pattern",
             "the observer pattern"],
            0,
            "An interchangeable algorithm behind one interface."),
        _jq("A macro command undoes its steps in…",
            ["reverse order", "the same order", "any order", "parallel"],
            0,
            "The last step done is the first to be undone."),
    ],
    exercises=[
        _je("j35-st-map", "Discounts chosen at run time",
            "Each line is a price and a discount name. Look the discount up in the map and "
            "apply it. Replace `____` with the lookup-and-apply.",
            _j35s("        Map<String, IntUnaryOperator> discounts = new HashMap<>();\n"
                  "        discounts.put(\"none\", p -> p);\n"
                  "        discounts.put(\"half\", p -> p / 2);\n"
                  "        discounts.put(\"minus10\", p -> Math.max(0, p - 10));\n"
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            int price = sc.nextInt();\n"
                  "            String name = sc.next();\n"
                  "            System.out.println(name + \" \" + discounts.get(name).applyAsInt(price));\n"
                  "        }"),
            "discounts.get(name).applyAsInt(price)",
            [_rows35(rows, _nl(*[f"{s} {_price35(p, s)}" for (p, s) in rows])) for rows in _PRICES35],
            hints=["The map's values ARE the strategies.",
                   "`discounts.get(name)` returns an `IntUnaryOperator`.",
                   "Its single method is `applyAsInt`.",
                   "A new discount is one `put` - no `if` anywhere changes."],
            difficulty="Easy"),

        _jch("j35-st-policy", "Shipping strategies that compose", "Medium",
             "Write three `ShippingPolicy` classes: `FlatRate` (always 500), `PerKilo` (a "
             "rate times the kilos) and `FreeOver` (free at or above a threshold, otherwise "
             "whatever the policy it WRAPS charges).",
             _j35t(_SHIP35,
                   "        Map<String, ShippingPolicy> policies = new HashMap<>();\n"
                   "        policies.put(\"flat\", new FlatRate());\n"
                   "        policies.put(\"perkilo\", new PerKilo(120));\n"
                   "        policies.put(\"free\", new FreeOver(10, new PerKilo(120)));\n"
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            String name = sc.next();\n"
                   "            int kilos = sc.nextInt();\n"
                   "            System.out.println(name + \" \" + kilos + \" \" + policies.get(name).cost(kilos));\n"
                   "        }"),
             _SHIP_REGION35,
             [_rows35(rows, _nl(*[f"{p} {k} {_ship35(p, k)}" for (p, k) in rows])) for rows in _SHIPROWS35],
             hints=["Each class `implements ShippingPolicy` with a `public int cost(int kilos)`.",
                    "Interface methods are public, so the implementations must be too.",
                    "`FreeOver` holds another `ShippingPolicy` and delegates to it below the "
                    "threshold.",
                    "That is composition: a strategy built from a strategy."]),

        _je("j35-co-undo", "Undo",
            "Run `add <text>` and `undo` operations on a text, printing it after each (or "
            "`(empty)`). An `undo` with nothing to undo does nothing. Replace `____` with "
            "the undo line.",
            _j35t(_CMD35,
                  "        int n = sc.nextInt();\n"
                  "        StringBuilder text = new StringBuilder();\n"
                  "        Deque<Command> history = new ArrayDeque<>();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            if (sc.next().equals(\"add\")) {\n"
                  "                Command c = new Append(text, sc.next());\n"
                  "                c.execute();\n"
                  "                history.push(c);\n"
                  "            } else if (!history.isEmpty()) {\n"
                  "                history.pop().undo();\n"
                  "            }\n"
                  "            System.out.println(text.length() == 0 ? \"(empty)\" : text.toString());\n"
                  "        }"),
            "                history.pop().undo();",
            [_rows35(ops, _edits_out35(ops)) for ops in _EDITS35],
            hints=["The history is a stack: the most recent command is on top.",
                   "`pop()` removes it; `undo()` reverses it.",
                   "`history.pop().undo();`",
                   "Each `Append` remembers its own piece, so it knows how much to remove."],
            difficulty="Easy"),

        _jch("j35-co-macro", "Macro commands", "Hard",
             "Write `Macro`: a `Command` made of a list of commands. `execute()` runs them in "
             "order; `undo()` undoes them in REVERSE. `main` runs each macro (steps are "
             "`+text` to append or `w` to wrap in brackets), then undoes them all.",
             _j35t(_CMD35 + _WRAP35,
                   "        int n = sc.nextInt();\n"
                   "        StringBuilder text = new StringBuilder();\n"
                   "        Deque<Command> history = new ArrayDeque<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            int k = sc.nextInt();\n"
                   "            List<Command> steps = new ArrayList<>();\n"
                   "            for (int j = 0; j < k; j++) {\n"
                   "                String op = sc.next();\n"
                   "                steps.add(op.equals(\"w\") ? new Wrap(text) : new Append(text, op.substring(1)));\n"
                   "            }\n"
                   "            Command macro = new Macro(steps);\n"
                   "            macro.execute();\n"
                   "            history.push(macro);\n"
                   "            System.out.println(text);\n"
                   "        }\n"
                   "        while (!history.isEmpty()) {\n"
                   "            history.pop().undo();\n"
                   "            System.out.println(text.length() == 0 ? \"(empty)\" : text.toString());\n"
                   "        }"),
             _MACRO_REGION35,
             [_macro_case35(m) for m in _MACROS35],
             hints=["`class Macro implements Command` holding a `List<Command>`.",
                    "Copy the list in the constructor - the caller's list is not yours.",
                    "`execute()`: a for-each over the steps.",
                    "`undo()`: an index loop from the end down to 0.",
                    "Undoing in forward order would remove a `]` where it expected the text "
                    "you appended - try it and watch the output go wrong.",
                    "The macro is itself a Command, so the history treats it like any other."]),
    ],
    quiz=[
        _jq("A strategy pattern typically replaces…",
            ["a switch on a type string repeated in several places", "a constructor",
             "a loop", "an exception"],
            0,
            "New behaviour becomes a new class or entry, not an edited switch."),
        _jq("What must a command remember to support undo?",
            ["enough state to reverse its own effect", "nothing", "the whole program state",
             "the time it ran"],
            0,
            "Append remembers its piece; a delete would remember what it removed."),
    ],
))


# ===========================================================================
# 35.4 Observer
# ===========================================================================

_BUS35 = """
class EventBus {
    private final List<Consumer<String>> listeners = new ArrayList<>();

    Runnable subscribe(Consumer<String> listener) {
        listeners.add(listener);
        return () -> listeners.remove(listener);
    }

    void publish(String event) {
        for (Consumer<String> l : listeners) {
            l.accept(event);
        }
    }
}
"""
_BUS_SAFE35 = _BUS35.replace("for (Consumer<String> l : listeners) {",
                             "for (Consumer<String> l : new ArrayList<>(listeners)) {")

_EVENTS35 = (["login", "error disk", "logout"], ["hello"], ["error a", "error b"], ["x", "y", "z", "w"],
             ["boot", "error net", "retry", "ok"])


def _bus_out35(evs):
    out, total = [], 0
    for e in evs:
        out.append(f"log: {e}")
        total += len(e)
        if e.startswith("error"):
            out.append(f"ALERT {e}")
    out.append(f"chars {total}")
    return _nl(*out)


_UNSUBS35 = (
    [("pub", "a"), ("drop", "A"), ("pub", "b")],
    [("drop", "B"), ("pub", "x")],
    [("pub", "one"), ("pub", "two"), ("drop", "A"), ("drop", "B"), ("pub", "three")],
    [("pub", "p")],
    [("drop", "A"), ("pub", "q"), ("drop", "A"), ("pub", "r")],
)


def _unsub_out35(ops):
    live = ["A", "B"]
    out = []
    for op in ops:
        if op[0] == "pub":
            for who in live:
                out.append(f"{who} got {op[1]}")
        elif op[1] in live:
            live.remove(op[1])
    assert out, "every case must publish to someone"
    return _nl(*out)


def _unsub_case35(ops):
    stdin = "\n".join([str(len(ops))] + [" ".join(op) for op in ops])
    return _case(stdin, _unsub_out35(ops))


_ONCE35 = (["a", "b"], ["solo"], ["x", "y", "z"], ["p", "q", "r", "s"], ["m", "n"])


def _once_out35(evs):
    out = []
    for i, e in enumerate(evs):
        if i == 0:
            out.append(f"first event: {e}")
        out.append(f"audit {e}")
        out.append(f"count {i + 1}")
    return _nl(*out)


_TOPICS35 = (
    [("sub", "news", "A"), ("pub", "news", "hi"), ("pub", "sport", "goal")],
    [("pub", "x", "lost")],
    [("sub", "a", "L1"), ("sub", "a", "L2"), ("sub", "b", "L3"), ("pub", "a", "m1"), ("pub", "b", "m2")],
    [("sub", "t", "Z"), ("sub", "t", "Y"), ("pub", "t", "v")],
    [("sub", "q", "A"), ("pub", "q", "1"), ("sub", "q", "B"), ("pub", "q", "2")],
)


def _topics_out35(ops):
    subs, out = {}, []
    for op in ops:
        if op[0] == "sub":
            subs.setdefault(op[1], []).append(op[2])
        else:
            for who in subs.get(op[1], []):
                out.append(f"{who} <- {op[1]}: {op[2]}")
    return _nl(*out) if out else "(nothing)"


def _topics_case35(ops):
    stdin = "\n".join([str(len(ops))] + [" ".join(op) for op in ops])
    return _case(stdin, _topics_out35(ops))


_M35.append(_jlesson(
    "m35-observer", "Observer: telling whoever is listening",
    "Publish an event without knowing who cares - and unsubscribe without breaking the loop.",
    """
The **observer** pattern decouples the thing that notices an event from the
things that react to it. The subject keeps a list of listeners and calls each
one; it neither knows nor cares what they do.

```java
class EventBus {
    private final List<Consumer<String>> listeners = new ArrayList<>();

    Runnable subscribe(Consumer<String> listener) {
        listeners.add(listener);
        return () -> listeners.remove(listener);      // the unsubscribe handle
    }

    void publish(String event) {
        for (Consumer<String> l : listeners) {
            l.accept(event);
        }
    }
}

bus.subscribe(e -> System.out.println("log: " + e));
bus.subscribe(e -> { if (e.startsWith("error")) alert(e); });
bus.publish("error disk");
```

Listeners are module 25's `Consumer`s, so any lambda can listen. Returning a
`Runnable` from `subscribe` is a neat way to hand back "the ability to stop
listening" without exposing the list.

Things to decide deliberately:

* **Order.** Listeners run in subscription order here - which callers will come
  to rely on, so document it or randomise it.
* **A listener that throws** stops every listener after it. Real buses catch and
  report per listener.
* **Memory.** A subscribed listener is referenced by the bus, so an object whose
  listener is never removed can never be garbage collected - the classic
  "lapsed listener" leak. Unsubscribe when you are done.

## The bug it is famous for

A listener that **unsubscribes itself** (a "run once" listener) removes an
element from the list *while `publish` is iterating over it* - module 17's
`ConcurrentModificationException`, in its most common real-world form. The
fixes:

```java
for (Consumer<String> l : new ArrayList<>(listeners)) { ... }   // iterate a snapshot
private final List<Consumer<String>> listeners = new CopyOnWriteArrayList<>();
```

`CopyOnWriteArrayList` (module 31) copies on every change, which makes
iteration always safe and is exactly right for a listener list: read on every
event, changed rarely.
""",
    warmup=[
        _jq("A listener removes itself during `publish`'s for-each loop over an "
            "ArrayList. The likely result is…",
            ["ConcurrentModificationException", "the listener runs twice",
             "nothing unusual", "a deadlock"],
            0,
            "Iterate a snapshot, or use CopyOnWriteArrayList."),
        _jq("The 'lapsed listener' problem is…",
            ["a memory leak from listeners that are never unsubscribed",
             "a listener that runs too late", "a listener that throws", "a race"],
            0,
            "The bus keeps every subscribed listener reachable."),
    ],
    exercises=[
        _je("j35-ob-publish", "Publishing to every listener",
            "Three listeners log each event, total the characters, and raise an alert for "
            "errors. Replace `____` with the line inside `publish` that notifies one "
            "listener.",
            _j35t(_BUS35,
                  "        EventBus bus = new EventBus();\n"
                  "        int[] chars = {0};\n"
                  "        bus.subscribe(e -> System.out.println(\"log: \" + e));\n"
                  "        bus.subscribe(e -> chars[0] += e.length());\n"
                  "        bus.subscribe(e -> {\n"
                  "            if (e.startsWith(\"error\")) {\n"
                  "                System.out.println(\"ALERT \" + e);\n"
                  "            }\n"
                  "        });\n"
                  "        int n = sc.nextInt();\n"
                  "        sc.nextLine();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            bus.publish(sc.nextLine());\n"
                  "        }\n"
                  "        System.out.println(\"chars \" + chars[0]);"),
            "            l.accept(event);",
            [_case("\n".join([str(len(evs))] + evs) + "\n", _bus_out35(evs)) for evs in _EVENTS35],
            hints=["A `Consumer<String>`'s method is `accept`.",
                   "`l.accept(event);`",
                   "Listeners run in the order they subscribed - logging before alerting.",
                   "`chars` is a one-element array because a lambda can only capture "
                   "effectively final variables (module 25)."],
            difficulty="Easy"),

        _jch("j35-ob-unsub", "Unsubscribing", "Medium",
             "Write `subscribe`: add the listener, and return a `Runnable` that removes it "
             "again. `main` subscribes A and B, then runs `pub <event>` and `drop <A|B>` "
             "operations.",
             _j35t(_BUS35,
                   "        EventBus bus = new EventBus();\n"
                   "        Map<String, Runnable> handles = new HashMap<>();\n"
                   "        handles.put(\"A\", bus.subscribe(e -> System.out.println(\"A got \" + e)));\n"
                   "        handles.put(\"B\", bus.subscribe(e -> System.out.println(\"B got \" + e)));\n"
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            String op = sc.next();\n"
                   "            String arg = sc.next();\n"
                   "            if (op.equals(\"pub\")) {\n"
                   "                bus.publish(arg);\n"
                   "            } else {\n"
                   "                handles.get(arg).run();\n"
                   "            }\n"
                   "        }"),
             "    Runnable subscribe(Consumer<String> listener) {\n"
             "        listeners.add(listener);\n"
             "        return () -> listeners.remove(listener);\n"
             "    }",
             [_unsub_case35(ops) for ops in _UNSUBS35],
             hints=["Add first, then return the handle.",
                    "The handle is a lambda: `() -> listeners.remove(listener)`.",
                    "It captures `listener`, so it removes exactly the one it was made for.",
                    "Running a handle twice is harmless: `remove` just returns false."]),

        _jfix("j35-ob-cme", "The listener that removed itself",
              "A run-once listener unsubscribes itself inside `publish`'s loop, and the next "
              "step of the loop throws `ConcurrentModificationException`. Make `publish` "
              "iterate over a snapshot of the listeners.",
              _j35t(_BUS35,
                    "        EventBus bus = new EventBus();\n"
                    "        int[] count = {0};\n"
                    "        Runnable[] once = new Runnable[1];\n"
                    "        once[0] = bus.subscribe(e -> {\n"
                    "            System.out.println(\"first event: \" + e);\n"
                    "            once[0].run();\n"
                    "        });\n"
                    "        bus.subscribe(e -> System.out.println(\"audit \" + e));\n"
                    "        bus.subscribe(e -> System.out.println(\"count \" + (++count[0])));\n"
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            bus.publish(sc.next());\n"
                    "        }"),
              _j35t(_BUS_SAFE35,
                    "        EventBus bus = new EventBus();\n"
                    "        int[] count = {0};\n"
                    "        Runnable[] once = new Runnable[1];\n"
                    "        once[0] = bus.subscribe(e -> {\n"
                    "            System.out.println(\"first event: \" + e);\n"
                    "            once[0].run();\n"
                    "        });\n"
                    "        bus.subscribe(e -> System.out.println(\"audit \" + e));\n"
                    "        bus.subscribe(e -> System.out.println(\"count \" + (++count[0])));\n"
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            bus.publish(sc.next());\n"
                    "        }"),
              [_toks35(evs, _once_out35(evs)) for evs in _ONCE35],
              hints=["The for-each loop's iterator notices the list changed under it.",
                     "Iterate over a copy: `for (Consumer<String> l : new ArrayList<>(listeners))`.",
                     "Removals then change the real list, not the snapshot being walked.",
                     "`CopyOnWriteArrayList` for the field would fix it too - it makes the "
                     "snapshot on every write instead."],
              difficulty="Medium"),

        _je("j35-ob-topics", "Topics",
            "Listeners subscribe to a TOPIC, and a message goes only to that topic's "
            "listeners, in subscription order. Replace `____` with the line in `subscribe` "
            "that files the listener under its topic.",
            _j35t("""
class TopicBus {
    private final Map<String, List<Consumer<String>>> topics = new HashMap<>();

    void subscribe(String topic, Consumer<String> listener) {
        topics.computeIfAbsent(topic, t -> new ArrayList<>()).add(listener);
    }

    void publish(String topic, String message) {
        for (Consumer<String> l : topics.getOrDefault(topic, List.of())) {
            l.accept(message);
        }
    }
}
""",
                  "        TopicBus bus = new TopicBus();\n"
                  "        int n = sc.nextInt();\n"
                  "        boolean[] any = {false};\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            String op = sc.next();\n"
                  "            String topic = sc.next();\n"
                  "            String arg = sc.next();\n"
                  "            if (op.equals(\"sub\")) {\n"
                  "                bus.subscribe(topic, m -> {\n"
                  "                    any[0] = true;\n"
                  "                    System.out.println(arg + \" <- \" + topic + \": \" + m);\n"
                  "                });\n"
                  "            } else {\n"
                  "                bus.publish(topic, arg);\n"
                  "            }\n"
                  "        }\n"
                  "        if (!any[0]) {\n"
                  "            System.out.println(\"(nothing)\");\n"
                  "        }"),
            "        topics.computeIfAbsent(topic, t -> new ArrayList<>()).add(listener);",
            [_topics_case35(ops) for ops in _TOPICS35],
            hints=["One list of listeners per topic, created the first time it is needed.",
                   "`computeIfAbsent(topic, t -> new ArrayList<>())` returns that list.",
                   "Then `.add(listener)` to it.",
                   "A message to a topic nobody subscribed to reaches nobody - "
                   "`getOrDefault(topic, List.of())`."],
            difficulty="Easy"),
    ],
    quiz=[
        _jq("Why is `CopyOnWriteArrayList` a good fit for a listener list?",
            ["it is read on every event and changed rarely, and iteration is always safe",
             "it is the fastest list", "it sorts listeners", "it removes duplicates"],
            0,
            "Copying on write is cheap when writes are rare."),
        _jq("Returning a `Runnable` from `subscribe` gives the caller…",
            ["a way to unsubscribe without access to the listener list",
             "a thread", "the event", "the bus"],
            0,
            "It captures the listener it will remove."),
    ],
))


# ===========================================================================
# 35.5 Decorator, adapter, composite
# ===========================================================================

_TEXT35 = """
interface Text {
    String render();
}

class Plain implements Text {
    private final String word;

    Plain(String word) {
        this.word = word;
    }

    public String render() {
        return word;
    }
}

class Upper implements Text {
    private final Text inner;

    Upper(Text inner) {
        this.inner = inner;
    }

    public String render() {
        return inner.render().toUpperCase();
    }
}

class Bracket implements Text {
    private final Text inner;

    Bracket(Text inner) {
        this.inner = inner;
    }

    public String render() {
        return "[" + inner.render() + "]";
    }
}

class Stars implements Text {
    private final Text inner;

    Stars(Text inner) {
        this.inner = inner;
    }

    public String render() {
        return "*" + inner.render() + "*";
    }
}
"""
_DECOS35 = (("hi", ["upper", "bracket"]), ("java", ["stars", "bracket", "stars"]), ("x", []),
            ("word", ["bracket", "upper"]), ("ok", ["stars", "stars", "upper"]))


def _deco35(word, ops):
    s = word
    for op in ops:
        s = s.upper() if op == "upper" else (f"[{s}]" if op == "bracket" else f"*{s}*")
    return s


_STORE35 = """
interface Store {
    String get(String key);
}

class SlowStore implements Store {
    private final Map<String, String> data;
    private int lookups;

    SlowStore(Map<String, String> data) {
        this.data = data;
    }

    public String get(String key) {
        lookups++;
        return data.getOrDefault(key, "?");
    }

    int lookups() {
        return lookups;
    }
}

class CachingStore implements Store {
    private final Store inner;
    private final Map<String, String> cache = new HashMap<>();
    private int hits;
    private int misses;

    CachingStore(Store inner) {
        this.inner = inner;
    }

    public String get(String key) {
        if (cache.containsKey(key)) {
            hits++;
            return cache.get(key);
        }
        misses++;
        String value = inner.get(key);
        cache.put(key, value);
        return value;
    }

    String stats() {
        return "hits " + hits + " misses " + misses;
    }
}
"""
_STORE_REGION35 = _STORE35[_STORE35.index("class CachingStore"):].strip("\n")
_STORECASES35 = (
    ([("a", "1"), ("b", "2")], ["a", "a", "b", "c", "a"]),
    ([("k", "v")], ["k"]),
    ([("x", "10")], ["y", "y", "x", "y"]),
    ([("p", "P"), ("q", "Q"), ("r", "R")], ["p", "q", "r", "p", "q", "r"]),
    ([("m", "0")], ["m", "m", "m", "m"]),
)


def _store_case35(data, qs):
    d = dict(data)
    cache, hits, misses, out = {}, 0, 0, []
    for q in qs:
        if q in cache:
            hits += 1
        else:
            misses += 1
            cache[q] = d.get(q, "?")
        out.append(f"{q}={cache[q]}")
    stdin = "\n".join([str(len(data))] + [f"{k} {v}" for (k, v) in data]
                      + [str(len(qs)), " ".join(qs)])
    return _case(stdin, _nl(" ".join(out), f"hits {hits} misses {misses}", f"inner lookups {misses}"))


_LOGGER35 = """
interface Logger {
    void log(String level, String message);
}

class OldConsole {
    private int lines;

    void write(String text) {
        lines++;
        System.out.println(lines + ": " + text);
    }
}

class ConsoleLogger implements Logger {
    private final OldConsole console;

    ConsoleLogger(OldConsole console) {
        this.console = console;
    }

    public void log(String level, String message) {
        console.write("[" + level.toUpperCase(Locale.ROOT) + "] " + message);
    }
}
"""
_LOGGER_REGION35 = _LOGGER35[_LOGGER35.index("class ConsoleLogger"):].strip("\n")
_LOGS35 = ([("info", "started"), ("warn", "slow")], [("error", "boom")],
           [("debug", "x"), ("info", "y"), ("Error", "z")], [("info", "only")],
           [("warn", "a"), ("warn", "b"), ("info", "c")])


def _logs_out35(rows):
    return _nl(*[f"{i}: [{lv.upper()}] {m}" for i, (lv, m) in enumerate(rows, start=1)])


_TREE35 = """
interface Node {
    String name();

    int size();

    void print(String indent);
}

class FileNode implements Node {
    private final String name;
    private final int size;

    FileNode(String name, int size) {
        this.name = name;
        this.size = size;
    }

    public String name() {
        return name;
    }

    public int size() {
        return size;
    }

    public void print(String indent) {
        System.out.println(indent + name + " " + size);
    }
}

class Folder implements Node {
    private final String name;
    private final List<Node> children = new ArrayList<>();

    Folder(String name) {
        this.name = name;
    }

    void add(Node child) {
        children.add(child);
    }

    public String name() {
        return name;
    }

    public int size() {
        int total = 0;
        for (Node c : children) {
            total += c.size();
        }
        return total;
    }

    public void print(String indent) {
        System.out.println(indent + name + "/ " + size());
        for (Node c : children) {
            c.print(indent + "  ");
        }
    }
}
"""
_TREE_REGION35 = _TREE35[_TREE35.index("class Folder"):].strip("\n")
_PARSETREE35 = (
    "    static Node parse(Scanner sc) {\n"
    "        String kind = sc.next();\n"
    "        String name = sc.next();\n"
    "        if (kind.equals(\"file\")) {\n"
    "            return new FileNode(name, sc.nextInt());\n"
    "        }\n"
    "        Folder f = new Folder(name);\n"
    "        int k = sc.nextInt();\n"
    "        for (int i = 0; i < k; i++) {\n"
    "            f.add(parse(sc));\n"
    "        }\n"
    "        return f;\n"
    "    }"
)
_FS35 = ("folder root 2 file a 10 folder sub 1 file b 5",
         "file solo 7",
         "folder empty 0",
         "folder docs 3 file x 1 file y 2 folder old 2 file z 3 folder deep 1 file w 4",
         "folder top 1 folder mid 1 folder low 1 file leaf 9")


def _fs_parse35(tokens):
    kind, name = tokens.pop(0), tokens.pop(0)
    if kind == "file":
        return ("file", name, int(tokens.pop(0)))
    k = int(tokens.pop(0))
    return ("folder", name, [_fs_parse35(tokens) for _ in range(k)])


def _fs_size35(n):
    return n[2] if n[0] == "file" else sum(_fs_size35(c) for c in n[2])


def _fs_print35(n, indent=""):
    if n[0] == "file":
        return [f"{indent}{n[1]} {n[2]}"]
    lines = [f"{indent}{n[1]}/ {_fs_size35(n)}"]
    for c in n[2]:
        lines += _fs_print35(c, indent + "  ")
    return lines


def _fs_case35(src):
    tree = _fs_parse35(src.split())
    return _case(src, _nl(*_fs_print35(tree), f"total {_fs_size35(tree)}"))


_M35.append(_jlesson(
    "m35-structure", "Decorator, adapter and composite",
    "Wrap an object to add behaviour, wrap it to change its shape, or build a tree "
    "that looks like a leaf.",
    """
Three structural patterns, all built from the same move - **an object that holds
another object of a related type** - and told apart by *why* it holds it.

## Decorator: same interface, more behaviour

```java
interface Text { String render(); }
class Upper implements Text {
    private final Text inner;
    Upper(Text inner) { this.inner = inner; }
    public String render() { return inner.render().toUpperCase(); }
}

Text t = new Bracket(new Upper(new Plain("hi")));   // "[HI]"
```

A decorator implements the interface it wraps and adds something before or
after delegating. Because it *is* a `Text`, decorators stack in any order - and
the order matters. You have met the JDK's most famous decorators already:
`new BufferedReader(new InputStreamReader(System.in))`, and module 34's
`Collections.unmodifiableList(list)`. Caching, logging, retrying and timing
wrappers are all decorators; they add a concern without touching the class.

## Adapter: a different interface, same behaviour

```java
class ConsoleLogger implements Logger {        // the interface we want
    private final OldConsole console;          // the class we have
    public void log(String level, String msg) {
        console.write("[" + level + "] " + msg);
    }
}
```

An adapter makes an existing class fit an interface it was not written for -
typically legacy or third-party code you cannot change. `Arrays.asList` is an
adapter (an array seen as a `List`).

## Composite: a tree that looks like a leaf

```java
interface Node { int size(); }
class FileNode implements Node { ... return size; }
class Folder implements Node {
    private final List<Node> children = new ArrayList<>();
    public int size() { int t = 0; for (Node c : children) t += c.size(); return t; }
}
```

A folder holds nodes, and *is* a node - so code asking for `size()` never needs
to know whether it has a file or a whole directory tree. Recursion does the
work (module 10). File systems, UI component trees, organisation charts and
module 34's expression trees are all composites.

**How to tell them apart:** a decorator keeps the interface and adds behaviour;
an adapter changes the interface and keeps behaviour; a composite holds *many*
of its own kind.
""",
    warmup=[
        _jq("`new BufferedReader(new InputStreamReader(System.in))` is an example of…",
            ["decorators", "a singleton", "a builder", "an observer"],
            0,
            "Each wrapper adds behaviour behind the same kind of interface."),
        _jq("An adapter…",
            ["makes an existing class fit an interface it was not written for",
             "adds caching", "creates objects", "notifies listeners"],
            0,
            "It changes the shape, not the behaviour."),
    ],
    exercises=[
        _je("j35-de-wrap", "Stacking decorators",
            "Start from a plain word and apply each decorator named in the input, in "
            "order: `upper`, `bracket` or `stars`. Replace `____` with the `upper` arm.",
            _j35t(_TEXT35,
                  "        Text t = new Plain(sc.next());\n"
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            t = switch (sc.next()) {\n"
                  "                case \"upper\" -> new Upper(t);\n"
                  "                case \"bracket\" -> new Bracket(t);\n"
                  "                default -> new Stars(t);\n"
                  "            };\n"
                  "        }\n"
                  "        System.out.println(t.render());"),
            "                case \"upper\" -> new Upper(t);",
            [_case(f"{w}\n{len(ops)}" + (f"\n{' '.join(ops)}" if ops else ""), _deco35(w, ops))
             for (w, ops) in _DECOS35],
            hints=["Each decorator wraps the CURRENT text.",
                   "`case \"upper\" -> new Upper(t);`",
                   "Order matters: bracket-then-stars is `*[x]*`, stars-then-bracket is `[*x*]`.",
                   "Upper-casing after bracketing still works - the brackets have no case."],
            difficulty="Easy"),

        _jch("j35-de-cache", "A caching decorator", "Medium",
             "Write `CachingStore`: a `Store` that wraps another `Store`, answers repeat "
             "keys from its own map, and counts hits and misses. `main` shows the inner "
             "store is consulted only on misses.",
             _j35t(_STORE35,
                   "        int n = sc.nextInt();\n"
                   "        Map<String, String> data = new HashMap<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            data.put(sc.next(), sc.next());\n"
                   "        }\n"
                   "        SlowStore slow = new SlowStore(data);\n"
                   "        CachingStore store = new CachingStore(slow);\n"
                   "        int q = sc.nextInt();\n"
                   "        StringBuilder out = new StringBuilder();\n"
                   "        for (int i = 0; i < q; i++) {\n"
                   "            String key = sc.next();\n"
                   "            if (out.length() > 0) out.append(' ');\n"
                   "            out.append(key).append('=').append(store.get(key));\n"
                   "        }\n"
                   "        System.out.println(out);\n"
                   "        System.out.println(store.stats());\n"
                   "        System.out.println(\"inner lookups \" + slow.lookups());"),
             _STORE_REGION35,
             [_store_case35(d, q) for (d, q) in _STORECASES35],
             hints=["`class CachingStore implements Store` holding the inner `Store`.",
                    "`cache.containsKey(key)` - not `cache.get(key) != null`, which would "
                    "treat a cached null as a miss.",
                    "On a miss, ask the inner store, remember the answer, return it.",
                    "The inner store's lookup count equals the number of misses.",
                    "Callers cannot tell a caching store from a plain one - that is the "
                    "decorator's whole point."]),

        _jch("j35-ad-adapter", "Adapting a legacy console", "Medium",
             "`OldConsole` only has `write(String)`, and cannot be changed. Write "
             "`ConsoleLogger`, an adapter implementing `Logger`, which writes "
             "`[LEVEL] message` with the level upper-cased (locale-proof).",
             _j35t(_LOGGER35,
                   "        Logger log = new ConsoleLogger(new OldConsole());\n"
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            log.log(sc.next(), sc.next());\n"
                   "        }"),
             _LOGGER_REGION35,
             [_rows35(rows, _logs_out35(rows)) for rows in _LOGS35],
             hints=["`class ConsoleLogger implements Logger` holding an `OldConsole`.",
                    "`log` builds the text and hands it to `console.write`.",
                    "`level.toUpperCase(Locale.ROOT)` - module 32's rule.",
                    "`main` only ever sees a `Logger`; the legacy class is hidden behind "
                    "it."]),

        _jch("j35-co-composite", "Files and folders", "Hard",
             "Write `Folder`, the composite: it holds child `Node`s, its `size()` is the sum "
             "of theirs, and `print(indent)` prints `name/ size` and then each child "
             "indented by two more spaces. Input is a pre-order description.",
             _j35th(_TREE35, _PARSETREE35,
                    "        Node root = parse(sc);\n"
                    "        root.print(\"\");\n"
                    "        System.out.println(\"total \" + root.size());"),
             _TREE_REGION35,
             [_fs_case35(src) for src in _FS35],
             hints=["`class Folder implements Node` with a `List<Node> children`.",
                    "`size()` sums `c.size()` over the children - each of which may itself "
                    "be a folder.",
                    "`print` prints its own line, then calls `c.print(indent + \"  \")`.",
                    "An empty folder has size 0.",
                    "Nothing outside the tree ever checks whether a node is a file or a "
                    "folder."]),
    ],
    quiz=[
        _jq("Decorator vs adapter: which keeps the interface and adds behaviour?",
            ["decorator", "adapter", "both", "neither"],
            0,
            "An adapter changes the interface instead."),
        _jq("In a composite, a `Folder` both holds `Node`s and…",
            ["is a Node itself", "extends FileNode", "is a singleton", "is immutable"],
            0,
            "That is what lets callers treat one file and a whole tree the same way."),
    ],
))


# ===========================================================================
# Capstone - the coffee counter
# ===========================================================================

_COFFEE35 = """
interface Drink {
    int cents();

    String describe();
}

class Espresso implements Drink {
    public int cents() {
        return 200;
    }

    public String describe() {
        return "espresso";
    }
}

class Tea implements Drink {
    public int cents() {
        return 150;
    }

    public String describe() {
        return "tea";
    }
}

abstract class Extra implements Drink {
    private final Drink base;
    private final String name;
    private final int price;

    Extra(Drink base, String name, int price) {
        this.base = base;
        this.name = name;
        this.price = price;
    }

    public int cents() {
        return base.cents() + price;
    }

    public String describe() {
        return base.describe() + " + " + name;
    }
}

class Milk extends Extra {
    Milk(Drink base) {
        super(base, "milk", 50);
    }
}

class Syrup extends Extra {
    Syrup(Drink base) {
        super(base, "syrup", 60);
    }
}

class Shot extends Extra {
    Shot(Drink base) {
        super(base, "shot", 80);
    }
}
"""
_COFFEE_REGION35 = _COFFEE35[_COFFEE35.index("abstract class Extra"):].strip("\n")

_ORDERS35 = (
    [("espresso", ["milk", "syrup"], "none"), ("tea", [], "tenoff")],
    [("espresso", ["shot", "shot"], "happyhour")],
    [("tea", ["milk"], "loyalty"), ("espresso", [], "loyalty"), ("tea", ["syrup", "milk", "shot"], "tenoff")],
    [("tea", [], "none")],
    [("espresso", ["milk"], "happyhour"), ("espresso", ["milk"], "tenoff"), ("espresso", ["milk"], "loyalty")],
)
_BASE35 = {"espresso": 200, "tea": 150}
_EXTRA35 = {"milk": 50, "syrup": 60, "shot": 80}


def _disc35(name, p):
    if name == "none":
        return p
    if name == "tenoff":
        return p - p // 10
    if name == "happyhour":
        return p // 2
    return max(0, p - 100)


def _coffee_out35(orders):
    out, total = [], 0
    for (base, extras, disc) in orders:
        price = _BASE35[base] + sum(_EXTRA35[e] for e in extras)
        desc = " + ".join([base] + extras)
        paid = _disc35(disc, price)
        total += paid
        out.append(f"{desc}: {price // 100}.{price % 100:02d} -> {paid // 100}.{paid % 100:02d} ({disc})")
    out.append(f"kitchen saw {len(orders)} orders")
    out.append(f"takings {total // 100}.{total % 100:02d}")
    return _nl(*out)


def _coffee_case35(orders):
    stdin = "\n".join([str(len(orders))]
                      + [" ".join([b, str(len(ex))] + ex + [d]) for (b, ex, d) in orders])
    return _case(stdin, _coffee_out35(orders))


_M35_CAP = _jcap(
    "The coffee counter",
    """
Three patterns, one counter:

* **Decorator** - a drink is an `Espresso` (2.00) or a `Tea` (1.50), and every
  extra wraps it: `Milk` +0.50, `Syrup` +0.60, `Shot` +0.80. Write an abstract
  `Extra` that implements `Drink` by delegating to the drink it wraps and adding
  its own name and price, and the three one-line subclasses.
* **Strategy** - the discount is chosen at run time by name from a map of
  `IntUnaryOperator`s (`none`, `tenoff`, `happyhour`, `loyalty`); already written.
* **Observer** - every finished order is published to listeners: the kitchen
  counts orders and the till adds up takings; already written.

Your part is the decorator hierarchy. `main` builds each drink by wrapping it in
the requested extras, prices it, applies the discount, and publishes it.
""",
    _jch("j35-cap-coffee", "The coffee counter", "Hard",
         "Write the abstract `Extra` decorator and its `Milk`, `Syrup` and `Shot` "
         "subclasses, as the brief describes.",
         _j35t(_COFFEE35,
               "        Map<String, IntUnaryOperator> discounts = new HashMap<>();\n"
               "        discounts.put(\"none\", p -> p);\n"
               "        discounts.put(\"tenoff\", p -> p - p / 10);\n"
               "        discounts.put(\"happyhour\", p -> p / 2);\n"
               "        discounts.put(\"loyalty\", p -> Math.max(0, p - 100));\n"
               "        List<IntConsumer> listeners = new ArrayList<>();\n"
               "        int[] orders = {0};\n"
               "        int[] takings = {0};\n"
               "        listeners.add(paid -> orders[0]++);\n"
               "        listeners.add(paid -> takings[0] += paid);\n"
               "        int n = sc.nextInt();\n"
               "        for (int i = 0; i < n; i++) {\n"
               "            Drink d = sc.next().equals(\"tea\") ? new Tea() : new Espresso();\n"
               "            int k = sc.nextInt();\n"
               "            for (int j = 0; j < k; j++) {\n"
               "                d = switch (sc.next()) {\n"
               "                    case \"milk\" -> new Milk(d);\n"
               "                    case \"syrup\" -> new Syrup(d);\n"
               "                    default -> new Shot(d);\n"
               "                };\n"
               "            }\n"
               "            String disc = sc.next();\n"
               "            int price = d.cents();\n"
               "            int paid = discounts.get(disc).applyAsInt(price);\n"
               "            System.out.println(String.format(Locale.ROOT, \"%s: %d.%02d -> %d.%02d (%s)\",\n"
               "                    d.describe(), price / 100, price % 100, paid / 100, paid % 100, disc));\n"
               "            for (IntConsumer l : listeners) {\n"
               "                l.accept(paid);\n"
               "            }\n"
               "        }\n"
               "        System.out.println(\"kitchen saw \" + orders[0] + \" orders\");\n"
               "        System.out.println(String.format(Locale.ROOT, \"takings %d.%02d\", takings[0] / 100, takings[0] % 100));"),
         _COFFEE_REGION35,
         [_coffee_case35(o) for o in _ORDERS35],
         hints=["`abstract class Extra implements Drink` with three final fields: the wrapped "
                "drink, a name and a price.",
                "`cents()` is `base.cents() + price`; `describe()` is `base.describe() + \" + "
                "\" + name`.",
                "Both must be `public` - they implement interface methods.",
                "Each subclass is a constructor calling `super(base, \"milk\", 50)` and "
                "nothing else.",
                "Extras wrap extras: `new Syrup(new Milk(new Espresso()))` costs 2.00 + 0.50 "
                "+ 0.60.",
                "The discount and listeners never learn how the drink was built - they only "
                "see a `Drink` and a price."]),
    example_io="stdin:  1\n        espresso 2 milk syrup none\n\n"
               "stdout: espresso + milk + syrup: 3.10 -> 3.10 (none)\n"
               "        kitchen saw 1 orders\n        takings 3.10",
    rubric=[
        "`Extra` implements `Drink` and delegates to the drink it wraps.",
        "Each extra adds its own price and name on top of the wrapped drink's.",
        "`Milk`, `Syrup` and `Shot` contain nothing but a constructor.",
        "Extras can wrap extras to any depth.",
        "No code outside the decorators knows which extras a drink has.",
    ],
)


_MODULES.append(_jmod(
    35, 13, "Advanced Java",
    "Design patterns",
    "The dozen patterns Java interviews actually reach for - each introduced by the "
    "problem it solves, and written the way modern Java writes it.",
    """
Patterns are names for solutions that keep recurring. Knowing the names lets you
say in one word what would otherwise take a paragraph - and recognising the
*problem* each solves is what lets you use them without over-using them.

* **Creational.** Static factories (named, cacheable constructors - `List.of`,
  `Integer.valueOf`) and the **Builder** (named optional arguments, one
  validation point, an immutable product - and a `build()` that must copy).
* **One instance.** Singletons by eager field, **holder idiom** or **enum** - and
  **dependency injection**, which is usually the better answer because it makes
  the dependency visible and replaceable.
* **Behaviour as an object.** **Strategy** (an interchangeable algorithm, often
  just a lambda, and composable) and **Command** (an action as an object: queued,
  logged, undone; macro commands undo in reverse).
* **Observer.** Listeners as `Consumer`s, an unsubscribe handle, and the
  `ConcurrentModificationException` a self-removing listener causes - fixed with a
  snapshot or `CopyOnWriteArrayList`.
* **Structure.** **Decorator** (same interface, added behaviour, stackable),
  **adapter** (a different interface over the same behaviour) and **composite** (a
  tree whose nodes and leaves share one interface).
""",
    _M35,
    capstone=_M35_CAP,
    objectives=[
        "Replace constructors with named static factories, including caching ones.",
        "Explain why `Integer` values compare with `==` only between -128 and 127.",
        "Write a Builder as a static nested class, and explain why `build()` must copy.",
        "Write a singleton three ways, and explain the holder idiom's laziness and thread safety.",
        "Explain why dependency injection usually beats a singleton, and inject a fake for testing.",
        "Implement strategies as lambdas in a map and as composable classes.",
        "Implement commands with undo, and a macro command that undoes in reverse.",
        "Build an observer with unsubscribe handles, and fix the self-removal ConcurrentModificationException.",
        "Distinguish decorator, adapter and composite, and implement each.",
    ],
    why="\"Which design patterns have you used?\" is asked in nearly every Java interview "
        "past junior level, and the follow-ups are practical: write a thread-safe "
        "singleton, why is a singleton hard to test, what does a builder buy you over a "
        "constructor, how would you add undo, what is the difference between a decorator "
        "and an adapter. Low-level design rounds - a parking lot, a vending machine, a "
        "notification service - are graded largely on reaching for the right one of these "
        "and explaining why.",
    est_minutes=330,
    glossary=[
        _jg("Static factory method", "A static method that returns an instance, with a "
                                     "name, possibly a cached object, possibly a "
                                     "subtype."),
        _jg("Builder", "A mutable helper that collects arguments by name and produces an "
                       "immutable object in `build()`."),
        _jg("Singleton", "A class with exactly one instance, reached through a static "
                         "field or method."),
        _jg("Holder idiom", "A lazy singleton kept in a private static nested class, "
                            "created on first use by the JVM's class initialisation."),
        _jg("Dependency injection", "Passing an object its collaborators (usually through "
                                    "the constructor) instead of letting it find them."),
        _jg("Strategy", "An interchangeable algorithm behind one interface, chosen at run "
                        "time."),
        _jg("Command", "An action represented as an object, so it can be stored, queued, "
                       "logged or undone."),
        _jg("Macro command", "A command made of commands; undoes its steps in reverse "
                             "order."),
        _jg("Observer", "A subject notifies a list of listeners of events without knowing "
                        "what they do."),
        _jg("Lapsed listener", "A memory leak caused by a listener that is never "
                               "unsubscribed."),
        _jg("Decorator", "A wrapper implementing the same interface as what it wraps, "
                         "adding behaviour."),
        _jg("Adapter", "A wrapper that makes an existing class fit an interface it was "
                       "not written for."),
        _jg("Composite", "A tree in which containers and leaves share one interface."),
        _jg("Open/closed principle", "Open for extension, closed for modification: add "
                                     "behaviour by adding code, not by editing it."),
    ],
    cheatsheet="""
```java
// --- creational ----------------------------------------------------------------
private Temperature(int c) { ... }
static Temperature ofFahrenheit(int f) { return new Temperature((f - 32) * 5 / 9); }
static Tag of(String name) { return CACHE.computeIfAbsent(name, Tag::new); }

Pizza p = new Pizza.Builder("large").topping("ham").extraCheese().build();
static class Builder {                     // static nested
    Builder topping(String t) { toppings.add(t); return this; }   // chainable
    Pizza build() { validate(); return new Pizza(this); }          // COPY lists
}

// --- one instance -------------------------------------------------------------
enum Registry { INSTANCE; ... }            // safest
private static class Holder { static final Config INSTANCE = new Config(); }
static Config get() { return Holder.INSTANCE; }                    // lazy, thread-safe
Greeter(Clock clock) { this.clock = clock; }                       // usually better: inject

// --- behaviour ------------------------------------------------------------------
Map<String, IntUnaryOperator> discounts = Map.of("half", p -> p / 2, ...);
new FreeOver(10, new PerKilo(120))         // strategies compose
interface Command { void execute(); void undo(); }
history.push(c);  history.pop().undo();    // undo stack
for (int i = steps.size() - 1; i >= 0; i--) steps.get(i).undo();   // macro: reverse

// --- observer -------------------------------------------------------------------
Runnable subscribe(Consumer<String> l) { listeners.add(l); return () -> listeners.remove(l); }
for (Consumer<String> l : new ArrayList<>(listeners)) l.accept(e);   // snapshot
List<Consumer<String>> listeners = new CopyOnWriteArrayList<>();     // or this

// --- structure -------------------------------------------------------------------
class Upper implements Text { Text inner; String render() { return inner.render().toUpperCase(); } }
class ConsoleLogger implements Logger { OldConsole c; void log(...) { c.write(...); } }  // adapter
class Folder implements Node { List<Node> kids; int size() { /* sum kids */ } }        // composite
```
""",
    self_check=[
        "Can you give two things a static factory can do that a constructor cannot?",
        "Can you explain why `Integer a = 1000, b = 1000; a == b` is false?",
        "Can you write a Builder, and say why `build()` must copy its collections?",
        "Can you write a lazy, thread-safe singleton without `synchronized`, and explain why it works?",
        "Can you say why an enum singleton is safer than a private constructor?",
        "Can you explain what makes a singleton hard to test, and what to do instead?",
        "Can you implement strategies both as lambdas and as composable classes?",
        "Can you add undo to an editor with commands, including macro commands?",
        "Can you explain and fix the ConcurrentModificationException a self-removing listener causes?",
        "Can you tell a decorator, an adapter and a composite apart in one sentence each?",
    ],
    review=[
        _jq("A Builder's `build()` passes its own `List` to the product. Building a second "
            "product after adding more items…",
            ["changes the first product too", "is harmless", "throws",
             "does not compile"],
            0,
            "Both products share the builder's list. Copy it."),
        _jq("The holder idiom's thread safety comes from…",
            ["the JVM initialising a class once, under a lock", "synchronized on get()",
             "volatile", "an AtomicReference"],
            0,
            "Class initialisation is already guaranteed to be safe."),
        _jq("`if (type.equals(\"flat\")) ... else if (type.equals(\"perkilo\")) ...` "
            "repeated in five places suggests…",
            ["the strategy pattern", "the singleton pattern", "the builder pattern",
             "the adapter pattern"],
            0,
            "Each branch becomes a class; the five switches become one lookup."),
        _jq("A macro command of [append \"a\", wrap in brackets] is undone by…",
            ["unwrapping, then removing \"a\"", "removing \"a\", then unwrapping",
             "either order", "re-executing it"],
            0,
            "Reverse order: last done, first undone."),
        _jq("`Collections.unmodifiableList(list)` is a…",
            ["decorator", "adapter", "composite", "builder"],
            0,
            "Same interface, added behaviour (refusing changes)."),
    ],
    milestone="You can reach for the right pattern by the problem in front of you - a "
              "builder for optional arguments, injection instead of a global, a strategy "
              "instead of a repeated switch, commands for undo, listeners that can leave "
              "safely, and wrappers that add behaviour, change shape or form a tree - and "
              "say why each one earns its place.",
))
