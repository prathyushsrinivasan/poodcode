# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 35 practice - design patterns.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[35]`.
#
# One family per lesson. Each drill is a small, complete use of a pattern with a
# deterministic output - listeners run in subscription order, maps are printed
# through TreeMap or LinkedHashMap, and the one "random" drill injects a
# SEEDED Random (module 32's mirror computes its rolls).
# ---------------------------------------------------------------------------


def _p35s(eid, title, difficulty, prompt, body, tests, hints):
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _j35s(body), body, tests, hints)


def _p35t(eid, title, difficulty, prompt, types, body, region, tests, hints):
    return _jch(eid, title, difficulty, prompt, _j35t(types, body), region.strip("\n"),
                tests, hints)


def _p35h(eid, title, difficulty, prompt, types, helpers, body, region, tests, hints):
    return _jch(eid, title, difficulty, prompt, _j35th(types, helpers, body),
                region.strip("\n"), tests, hints)


def _after35(src, marker):
    """Everything in `src` from the line containing `marker` to the end."""
    return src[src.index(marker):].strip("\n")


# --- Family A - factories and builders -------------------------------------------

_POINTF35 = """
class Point {
    private static final Point ORIGIN = new Point(0, 0);

    private final int x;
    private final int y;

    private Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    static Point of(int x, int y) {
        return x == 0 && y == 0 ? ORIGIN : new Point(x, y);
    }

    @Override
    public String toString() {
        return "(" + x + ", " + y + ")";
    }
}
"""
_PPAIRS35 = ([(0, 0, 0, 0)], [(1, 2, 1, 2)], [(0, 0, 1, 1), (0, 0, 0, 0)], [(3, 3, 3, 3), (0, 0, 0, 0)],
             [(5, 0, 0, 5)])


def _ppairs_out35(rows):
    return _nl(*[f"({a}, {b}) ({c}, {d}) {_jbool(a == b == c == d == 0)}" for (a, b, c, d) in rows])


_FRACP35 = """
class Fraction {
    private final int num;
    private final int den;

    private Fraction(int num, int den) {
        this.num = num;
        this.den = den;
    }

    static Fraction parse(String text) {
        String[] parts = text.split("/");
        if (parts.length == 1) {
            return new Fraction(Integer.parseInt(parts[0]), 1);
        }
        return new Fraction(Integer.parseInt(parts[0]), Integer.parseInt(parts[1]));
    }

    double value() {
        return (double) num / den;
    }

    @Override
    public String toString() {
        return num + "/" + den;
    }
}
"""
_FRACP_REGION35 = (
    "    static Fraction parse(String text) {\n"
    "        String[] parts = text.split(\"/\");\n"
    "        if (parts.length == 1) {\n"
    "            return new Fraction(Integer.parseInt(parts[0]), 1);\n"
    "        }\n"
    "        return new Fraction(Integer.parseInt(parts[0]), Integer.parseInt(parts[1]));\n"
    "    }"
)
_FTEXTS35 = (["1/2", "3"], ["5/4"], ["7", "1/8", "3/2"], ["-1/4"], ["9/3", "2/5"])


def _fparse35(t):
    if "/" in t:
        a, b = (int(x) for x in t.split("/"))
    else:
        a, b = int(t), 1
    return f"{a}/{b} {_jd32(a / b)}"


_CACHEINTS35 = ([(100, 100)], [(1000, 1000)], [(127, 127), (128, 128)], [(-128, -128), (-129, -129)],
                [(5, 6), (0, 0)])


def _cacheints_out35(rows):
    return _nl(*[f"{a} {b} == {_jbool(a == b and -128 <= a <= 127)} equals {_jbool(a == b)}"
                 for (a, b) in rows])


_REQUEST35 = """
class Request {
    private final String method;
    private final String url;
    private final Map<String, String> headers;
    private final String body;

    private Request(Builder b) {
        this.method = b.method;
        this.url = b.url;
        this.headers = new TreeMap<>(b.headers);
        this.body = b.body;
    }

    @Override
    public String toString() {
        return method + " " + url + " " + headers + (body == null ? "" : " body=" + body);
    }

    static class Builder {
        private final String url;
        private String method = "GET";
        private final Map<String, String> headers = new TreeMap<>();
        private String body;

        Builder(String url) {
            this.url = url;
        }

        Builder method(String m) {
            method = m;
            return this;
        }

        Builder header(String name, String value) {
            headers.put(name, value);
            return this;
        }

        Builder body(String b) {
            body = b;
            return this;
        }

        Request build() {
            if (method.equals("GET") && body != null) {
                throw new IllegalStateException("GET cannot have a body");
            }
            return new Request(this);
        }
    }
}
"""
_REQUEST_REGION35 = _after35(_REQUEST35, "    static class Builder {")
_REQUEST_REGION35 = _REQUEST_REGION35[:_REQUEST_REGION35.rfind("}")].rstrip()

_REQS35 = (
    ("/users", [], None, None),
    ("/login", [("method", "POST"), ("header", "type", "json")], "pw", None),
    ("/items", [("header", "b", "2"), ("header", "a", "1")], None, None),
    ("/oops", [], "data", None),
    ("/put", [("method", "PUT"), ("header", "x", "y")], "v", None),
)


def _req_case35(url, ops, body, _unused):
    method, headers = "GET", {}
    lines = [url]
    toks = []
    for op in ops:
        if op[0] == "method":
            method = op[1]
            toks.append(f"method {op[1]}")
        else:
            headers[op[1]] = op[2]
            toks.append(f"header {op[1]} {op[2]}")
    if body is not None:
        toks.append(f"body {body}")
    stdin = url + "\n" + str(len(toks)) + ("\n" + "\n".join(toks) if toks else "")
    if method == "GET" and body is not None:
        out = "rejected: GET cannot have a body"
    else:
        hdr = "{" + ", ".join(f"{k}={headers[k]}" for k in sorted(headers)) + "}"
        out = f"{method} {url} {hdr}" + ("" if body is None else f" body={body}")
    return _case(stdin, out)


_ORDERB35 = """
class Order {
    private final String item;
    private final int quantity;
    private final boolean gift;

    private Order(Builder b) {
        this.item = b.item;
        this.quantity = b.quantity;
        this.gift = b.gift;
    }

    Builder toBuilder() {
        return new Builder(item).quantity(quantity).gift(gift);
    }

    @Override
    public String toString() {
        return quantity + " x " + item + (gift ? " (gift)" : "");
    }

    static class Builder {
        private final String item;
        private int quantity = 1;
        private boolean gift;

        Builder(String item) {
            this.item = item;
        }

        Builder quantity(int q) {
            quantity = q;
            return this;
        }

        Builder gift(boolean g) {
            gift = g;
            return this;
        }

        Order build() {
            return new Order(this);
        }
    }
}
"""
_TOB_REGION35 = (
    "    Builder toBuilder() {\n"
    "        return new Builder(item).quantity(quantity).gift(gift);\n"
    "    }"
)
_TOBS35 = (("book", 2, "yes"), ("pen", 10, "no"), ("mug", 1, "yes"), ("lamp", 3, "no"), ("cake", 7, "yes"))


def _tob_out35(item, q, g):
    first = f"1 x {item}"
    second = f"{q} x {item}"
    third = f"{q} x {item}" + (" (gift)" if g == "yes" else "")
    return _nl(first, second, third)


_P35_A = _jfam(
    "p35-create", "Factories and builders",
    "Named creation, cached creation, and builders - including one made from an "
    "existing object.",
    """
```java
static Point of(int x, int y) { return x == 0 && y == 0 ? ORIGIN : new Point(x, y); }
static Fraction parse(String text) { ... }               // a named conversion
Request r = new Request.Builder("/login").method("POST").header("type", "json").build();
Order bigger = order.toBuilder().quantity(5).build();   // copy with changes
```

A factory that sometimes returns a shared object makes `==` unreliable - which is
exactly why `Integer` values must be compared with `equals`. And `toBuilder()`
is the builder's answer to "the same, but different in one field": a builder
pre-filled from an existing object.
""",
    [
        _p35t("j35-pa-origin", "A shared origin", "Intro",
              "`Point.of` returns one shared `ORIGIN` for (0, 0) and a fresh point "
              "otherwise. For each pair print both points and whether `==` says they are "
              "the same object.",
              _POINTF35,
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            Point p = Point.of(sc.nextInt(), sc.nextInt());\n"
              "            Point q = Point.of(sc.nextInt(), sc.nextInt());\n"
              "            System.out.println(p + \" \" + q + \" \" + (p == q));\n"
              "        }",
              "        for (int i = 0; i < n; i++) {\n"
              "            Point p = Point.of(sc.nextInt(), sc.nextInt());\n"
              "            Point q = Point.of(sc.nextInt(), sc.nextInt());\n"
              "            System.out.println(p + \" \" + q + \" \" + (p == q));\n"
              "        }",
              [_rows35(rows, _ppairs_out35(rows)) for rows in _PPAIRS35],
              ["Only the origin is shared; `(1, 2)` twice is two objects.",
               "`p == q` compares identity, not coordinates.",
               "This is why `==` on objects from a factory is unreliable."]),

        _p35t("j35-pa-parse", "A parsing factory", "Easy",
              "Write `Fraction.parse(text)`: `3/4` is three quarters and a bare `3` is "
              "three over one. The constructor is private.",
              _FRACP35,
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            Fraction f = Fraction.parse(sc.next());\n"
              "            System.out.println(f + \" \" + f.value());\n"
              "        }",
              _FRACP_REGION35,
              [_toks35(ts, _nl(*[_fparse35(t) for t in ts])) for ts in _FTEXTS35],
              ["`text.split(\"/\")` gives one part or two.",
               "One part means a whole number: denominator 1.",
               "`parse` is static and named for what it does - the JDK's convention "
               "(`Integer.parseInt`, `LocalDate.parse`)."]),

        _p35s("j35-pa-valueof", "The Integer cache", "Easy",
              "For each pair, box both numbers with `Integer.valueOf` and print whether "
              "`==` and `equals` consider them the same.",
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            int x = sc.nextInt();\n"
              "            int y = sc.nextInt();\n"
              "            Integer a = Integer.valueOf(x);\n"
              "            Integer b = Integer.valueOf(y);\n"
              "            System.out.println(x + \" \" + y + \" == \" + (a == b) + \" equals \" + a.equals(b));\n"
              "        }",
              [_rows35(rows, _cacheints_out35(rows)) for rows in _CACHEINTS35],
              ["`Integer.valueOf` returns a cached object for -128..127.",
               "Outside that range each call creates a new Integer.",
               "So `==` is true for 127 and false for 128 - `equals` is true for both.",
               "Always compare boxed numbers with `equals`."]),

        _p35t("j35-pa-request", "A request builder", "Medium",
              "Write `Request.Builder`: the URL is required; `method` defaults to GET; "
              "`header(name, value)` may be called repeatedly; `body` is optional; and "
              "`build()` refuses a GET with a body (`IllegalStateException(\"GET cannot "
              "have a body\")`).",
              _REQUEST35,
              "        Request.Builder b = new Request.Builder(sc.next());\n"
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            switch (sc.next()) {\n"
              "                case \"method\" -> b.method(sc.next());\n"
              "                case \"header\" -> b.header(sc.next(), sc.next());\n"
              "                default -> b.body(sc.next());\n"
              "            }\n"
              "        }\n"
              "        try {\n"
              "            System.out.println(b.build());\n"
              "        } catch (IllegalStateException e) {\n"
              "            System.out.println(\"rejected: \" + e.getMessage());\n"
              "        }",
              _REQUEST_REGION35,
              [_req_case35(*r) for r in _REQS35],
              ["Fields: `url` (final, from the constructor), `method` defaulting to "
               "`\"GET\"`, a `headers` map, and a nullable `body`.",
               "Every setter returns `this`.",
               "A `TreeMap` keeps the headers sorted, so the output is predictable.",
               "`build()` checks the one cross-field rule, then `return new Request(this);`."]),

        _p35t("j35-pa-tobuilder", "The same, but different", "Hard",
              "Write `Order.toBuilder()`: a builder pre-filled with this order's values. "
              "`main` builds a default order, then a copy with a new quantity, then a copy "
              "of THAT with the gift flag - leaving each earlier order untouched.",
              _ORDERB35,
              "        String item = sc.next();\n"
              "        int q = sc.nextInt();\n"
              "        boolean gift = sc.next().equals(\"yes\");\n"
              "        Order first = new Order.Builder(item).build();\n"
              "        Order second = first.toBuilder().quantity(q).build();\n"
              "        Order third = second.toBuilder().gift(gift).build();\n"
              "        System.out.println(first);\n"
              "        System.out.println(second);\n"
              "        System.out.println(third);",
              _TOB_REGION35,
              [_case(f"{i} {q} {g}", _tob_out35(i, q, g)) for (i, q, g) in _TOBS35],
              ["Start a new Builder with the same item...",
               "...then chain `quantity(quantity)` and `gift(gift)` with this order's "
               "values.",
               "The builder is a new, separate object, so changing it cannot touch the "
               "original order.",
               "This is the builder's version of module 34's withers."]),
    ],
)


# --- Family B - one instance ------------------------------------------------------

_IDGEN35 = """
class IdGenerator {
    static final IdGenerator INSTANCE = new IdGenerator();

    private int next = 1;

    private IdGenerator() {
    }

    String next(String prefix) {
        return prefix + "-" + (next++);
    }
}
"""
_IDKINDS35 = (["user", "order", "user"], ["x"], ["a", "b", "c", "d"], ["order", "order"], ["item", "user"])

_SETTINGS35 = """
enum Settings {
    INSTANCE;

    private final Map<String, String> values = new TreeMap<>();

    void set(String key, String value) {
        values.put(key, value);
    }

    String get(String key) {
        return values.getOrDefault(key, "(unset)");
    }

    Map<String, String> all() {
        return Collections.unmodifiableMap(values);
    }
}
"""
_SETOPS35 = ([("set", "theme", "dark"), ("get", "theme"), ("get", "font")],
             [("get", "a")],
             [("set", "b", "2"), ("set", "a", "1"), ("set", "b", "3"), ("get", "b")],
             [("set", "k", "v")],
             [("set", "z", "last"), ("get", "z"), ("set", "y", "mid")])


def _setops_out35(ops):
    vals, out = {}, []
    for op in ops:
        if op[0] == "set":
            vals[op[1]] = op[2]
        else:
            out.append(f"{op[1]}={vals.get(op[1], '(unset)')}")
    out.append("{" + ", ".join(f"{k}={vals[k]}" for k in sorted(vals)) + "}")
    return _nl(*out)


def _setops_case35(ops):
    return _case("\n".join([str(len(ops))] + [" ".join(op) for op in ops]), _setops_out35(ops))


_LAZY35 = """
class Alpha {
    private Alpha() {
        System.out.println("init Alpha");
    }

    private static class Holder {
        static final Alpha INSTANCE = new Alpha();
    }

    static Alpha get() {
        return Holder.INSTANCE;
    }
}

class Beta {
    private Beta() {
        System.out.println("init Beta");
    }

    private static class Holder {
        static final Beta INSTANCE = new Beta();
    }

    static Beta get() {
        return Holder.INSTANCE;
    }
}
"""
_LAZYSEQS35 = (["B", "A", "B"], ["A"], ["A", "A", "A"], ["B", "B"], ["B", "A", "A", "B"])


def _lazy_out35(seq):
    done, out = set(), []
    for s in seq:
        name = "Alpha" if s == "A" else "Beta"
        if s not in done:
            out.append(f"init {name}")
            done.add(s)
        out.append(f"use {name}")
    return _nl(*out)


_DICE35 = """
class Dice {
    private final Random rnd;

    Dice(Random rnd) {
        this.rnd = rnd;
    }

    int roll() {
        return rnd.nextInt(6) + 1;
    }
}
"""
_DICE_REGION35 = _body35(_DICE35)

_MAILER35 = """
interface Mailer {
    void send(String to, String text);
}

class RecordingMailer implements Mailer {
    final List<String> sent = new ArrayList<>();

    public void send(String to, String text) {
        sent.add(to + ": " + text);
    }
}

class Signup {
    private final Mailer mailer;
    private final Set<String> users = new HashSet<>();

    Signup(Mailer mailer) {
        this.mailer = mailer;
    }

    boolean register(String email) {
        if (!users.add(email)) {
            return false;
        }
        mailer.send(email, "welcome!");
        return true;
    }
}
"""
_MAILER_REGION35 = _after35(_MAILER35, "class Signup {")
_EMAILS35 = (["a@x", "b@x", "a@x"], ["solo@x"], ["m@x", "m@x", "m@x"], ["p@x", "q@x", "r@x"],
             ["z@x", "y@x", "z@x", "y@x"])


def _mail_out35(ems):
    seen, out, sent = set(), [], []
    for e in ems:
        if e in seen:
            out.append(f"{e} duplicate")
        else:
            seen.add(e)
            out.append(f"{e} registered")
            sent.append(f"{e}: welcome!")
    return _nl(*out, f"sent {len(sent)}", *sent)


_P35_B = _jfam(
    "p35-single", "One instance, or an injected one",
    "Eager, enum and holder singletons - and constructor injection, which makes the "
    "same code testable.",
    """
```java
static final IdGenerator INSTANCE = new IdGenerator();   // eager
enum Settings { INSTANCE; ... }                          // enum
private static class Holder { static final Alpha INSTANCE = new Alpha(); }   // lazy

Dice(Random rnd) { this.rnd = rnd; }                     // injected
new Dice(new Random(42))                                 // ...so a test can fix the seed
```

The last line is the real lesson. A `Dice` that called `new Random()` inside
itself could never be tested; one that *receives* its `Random` can be handed a
seeded one, and module 32's rolls come out the same every time.
""",
    [
        _p35h("j35-pb-eager", "One id generator", "Intro",
              "Every id in the program comes from the one `IdGenerator`, so numbers never "
              "repeat - even across different prefixes. Write `newId` using it.",
              _IDGEN35,
              "    static String newId(String kind) {\n"
              "        return IdGenerator.INSTANCE.next(kind);\n"
              "    }",
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            System.out.println(newId(sc.next()));\n"
              "        }",
              "    static String newId(String kind) {\n"
              "        return IdGenerator.INSTANCE.next(kind);\n"
              "    }",
              [_toks35(ts, _nl(*[f"{t}-{i}" for i, t in enumerate(ts, start=1)])) for ts in _IDKINDS35],
              ["`IdGenerator.INSTANCE` is the only instance.",
               "`next(prefix)` returns `prefix-N` and advances the counter.",
               "One counter for everything: `user-1`, `order-2`, `user-3`."]),

        _p35t("j35-pb-enum", "Settings as an enum singleton", "Easy",
              "Run `set key value` and `get key` operations against the one `Settings`, "
              "printing each `get` as `key=value`, then all settings at the end.",
              _SETTINGS35,
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            if (sc.next().equals(\"set\")) {\n"
              "                Settings.INSTANCE.set(sc.next(), sc.next());\n"
              "            } else {\n"
              "                String key = sc.next();\n"
              "                System.out.println(key + \"=\" + Settings.INSTANCE.get(key));\n"
              "            }\n"
              "        }\n"
              "        System.out.println(Settings.INSTANCE.all());",
              "        for (int i = 0; i < n; i++) {\n"
              "            if (sc.next().equals(\"set\")) {\n"
              "                Settings.INSTANCE.set(sc.next(), sc.next());\n"
              "            } else {\n"
              "                String key = sc.next();\n"
              "                System.out.println(key + \"=\" + Settings.INSTANCE.get(key));\n"
              "            }\n"
              "        }\n"
              "        System.out.println(Settings.INSTANCE.all());",
              [_setops_case35(ops) for ops in _SETOPS35],
              ["Every call goes through `Settings.INSTANCE`.",
               "`get` falls back to `(unset)`.",
               "`all()` hands out a read-only view - a decorator from lesson 35.5."]),

        _p35t("j35-pb-lazy", "Initialised on first use", "Medium",
              "`Alpha` and `Beta` are holder-idiom singletons whose constructors announce "
              "themselves. For each letter print `use Alpha` or `use Beta` after getting "
              "the instance - and watch each `init` appear exactly once, at first use, in "
              "whatever order the input asks.",
              _LAZY35,
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            if (sc.next().equals(\"A\")) {\n"
              "                Alpha.get();\n"
              "                System.out.println(\"use Alpha\");\n"
              "            } else {\n"
              "                Beta.get();\n"
              "                System.out.println(\"use Beta\");\n"
              "            }\n"
              "        }",
              "        for (int i = 0; i < n; i++) {\n"
              "            if (sc.next().equals(\"A\")) {\n"
              "                Alpha.get();\n"
              "                System.out.println(\"use Alpha\");\n"
              "            } else {\n"
              "                Beta.get();\n"
              "                System.out.println(\"use Beta\");\n"
              "            }\n"
              "        }",
              [_toks35(seq, _lazy_out35(seq)) for seq in _LAZYSEQS35],
              ["Calling `get()` is what triggers each Holder's initialisation.",
               "The JVM initialises each Holder once, so each `init` line appears once.",
               "Asking for Beta first initialises Beta first - declaration order is "
               "irrelevant.",
               "A singleton that is never used is never created."]),

        _p35t("j35-pb-dice", "Injecting the randomness", "Medium",
              "Write `Dice`'s body: it RECEIVES a `Random` in its constructor and rolls "
              "1..6 with it. `main` injects a seeded generator, so the rolls are "
              "reproducible.",
              _DICE35,
              "        long seed = sc.nextLong();\n"
              "        int n = sc.nextInt();\n"
              "        Dice dice = new Dice(new Random(seed));\n"
              "        StringBuilder out = new StringBuilder();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            if (i > 0) out.append(' ');\n"
              "            out.append(dice.roll());\n"
              "        }\n"
              "        System.out.println(out);",
              _DICE_REGION35,
              [_case(f"{s} {n}", _sp(_dice32(s, n))) for (s, n) in _SEEDS32],
              ["A `private final Random rnd` set from the constructor.",
               "`roll()` returns `rnd.nextInt(6) + 1`.",
               "`Dice` never creates its own `Random` - that decision belongs to whoever "
               "builds it.",
               "In production you would pass `new Random()`; in a test, a seeded one."]),

        _p35t("j35-pb-fake", "Testing with a fake", "Hard",
              "Write `Signup`: it receives a `Mailer`, registers each email once, and sends "
              "`welcome!` to new users only (`register` returns whether it was new). `main` "
              "injects a `RecordingMailer` fake and prints what WOULD have been sent.",
              _MAILER35,
              "        RecordingMailer mailer = new RecordingMailer();\n"
              "        Signup signup = new Signup(mailer);\n"
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String email = sc.next();\n"
              "            System.out.println(email + (signup.register(email) ? \" registered\" : \" duplicate\"));\n"
              "        }\n"
              "        System.out.println(\"sent \" + mailer.sent.size());\n"
              "        for (String s : mailer.sent) {\n"
              "            System.out.println(s);\n"
              "        }",
              _MAILER_REGION35,
              [_toks35(e, _mail_out35(e)) for e in _EMAILS35],
              ["`Signup` depends on the `Mailer` INTERFACE, never on a real mail class.",
               "`users.add(email)` returns false for a repeat - a Set does the "
               "de-duplication.",
               "Only new users get `mailer.send(email, \"welcome!\")`.",
               "The fake records instead of sending, so the test can check exactly what "
               "happened."]),
    ],
)


# --- Family C - strategy and command ----------------------------------------------

_SORTS35 = ((["pear", "fig", "banana", "kiwi"], "alpha"), (["pear", "fig", "banana", "kiwi"], "length"),
            (["b", "a", "c"], "reverse"), (["ccc", "a", "bb", "aa"], "length"), (["x"], "alpha"))


def _sorted35(ws, how):
    if how == "alpha":
        return sorted(ws)
    if how == "reverse":
        return sorted(ws, reverse=True)
    return sorted(ws, key=lambda w: (len(w), w))


_ROUNDING35 = """
enum Rounding {
    DOWN((v, step) -> Math.floorDiv(v, step) * step),
    UP((v, step) -> -Math.floorDiv(-v, step) * step),
    NEAREST((v, step) -> Math.floorDiv(v + step / 2, step) * step);

    private final IntBinaryOperator rule;

    Rounding(IntBinaryOperator rule) {
        this.rule = rule;
    }

    int apply(int value, int step) {
        return rule.applyAsInt(value, step);
    }
}
"""
_ROUNDING_REGION35 = (
    "    DOWN((v, step) -> Math.floorDiv(v, step) * step),\n"
    "    UP((v, step) -> -Math.floorDiv(-v, step) * step),\n"
    "    NEAREST((v, step) -> Math.floorDiv(v + step / 2, step) * step);"
)
_ROUNDS35 = ([(17, 5)], [(20, 5), (-7, 5)], [(1, 10), (99, 10)], [(-15, 10)], [(0, 3), (4, 3)])


def _round35(v, s):
    return (v // s * s, -((-v) // s) * s, (v + s // 2) // s * s)


_RULES35 = (["abc", "hello1", "Password9"], ["x"], ["ALLCAPS", "12345678", "Mixed1"],
            ["goodPass1"], ["", "a1"])


def _rules_out35(ws):
    out = []
    for w in ws:
        fails = []
        if len(w) < 6:
            fails.append("length")
        if not any(c.isdigit() for c in w):
            fails.append("digit")
        if not any(c.isupper() for c in w):
            fails.append("upper")
        shown = w if w else "(empty)"
        out.append(f"{shown}: ok" if not fails else f"{shown}: " + ", ".join(fails))
    return _nl(*out)


_REDO35 = ([("add", 5), ("add", 3), ("undo",), ("redo",)], [("undo",), ("redo",)],
           [("add", 1), ("undo",), ("add", 10), ("redo",)], [("add", 2), ("add", 2), ("undo",), ("undo",), ("redo",), ("redo",), ("redo",)],
           [("add", -4), ("undo",), ("undo",), ("redo",)])


def _redo_out35(ops):
    val, undo, redo, out = 0, [], [], []
    for op in ops:
        if op[0] == "add":
            val += op[1]
            undo.append(op[1])
            redo.clear()
        elif op[0] == "undo":
            if undo:
                k = undo.pop()
                val -= k
                redo.append(k)
        else:
            if redo:
                k = redo.pop()
                val += k
                undo.append(k)
        out.append(str(val))
    return _sp(out)


def _redo_case35(ops):
    return _case("\n".join([str(len(ops))] + [" ".join(str(x) for x in op) for op in ops]),
                 _redo_out35(ops))


_BATCH35 = """
interface Step {
    void run(Map<String, Integer> accounts);

    void undo(Map<String, Integer> accounts);
}

class Deposit implements Step {
    private final String who;
    private final int amount;

    Deposit(String who, int amount) {
        this.who = who;
        this.amount = amount;
    }

    public void run(Map<String, Integer> accounts) {
        accounts.merge(who, amount, Integer::sum);
    }

    public void undo(Map<String, Integer> accounts) {
        accounts.merge(who, -amount, Integer::sum);
    }
}

class Withdraw implements Step {
    private final String who;
    private final int amount;

    Withdraw(String who, int amount) {
        this.who = who;
        this.amount = amount;
    }

    public void run(Map<String, Integer> accounts) {
        if (accounts.getOrDefault(who, 0) < amount) {
            throw new IllegalStateException("insufficient funds for " + who);
        }
        accounts.merge(who, -amount, Integer::sum);
    }

    public void undo(Map<String, Integer> accounts) {
        accounts.merge(who, amount, Integer::sum);
    }
}
"""
_RUNBATCH35 = (
    "    static boolean runAll(List<Step> steps, Map<String, Integer> accounts) {\n"
    "        Deque<Step> done = new ArrayDeque<>();\n"
    "        for (Step s : steps) {\n"
    "            try {\n"
    "                s.run(accounts);\n"
    "                done.push(s);\n"
    "            } catch (IllegalStateException e) {\n"
    "                System.out.println(\"failed: \" + e.getMessage());\n"
    "                while (!done.isEmpty()) {\n"
    "                    done.pop().undo(accounts);\n"
    "                }\n"
    "                return false;\n"
    "            }\n"
    "        }\n"
    "        return true;\n"
    "    }"
)
_BATCHES35 = (
    [("dep", "ada", 100), ("wd", "ada", 30), ("wd", "ada", 80)],
    [("dep", "bo", 5)],
    [("dep", "x", 10), ("dep", "y", 20), ("wd", "y", 20), ("wd", "x", 10)],
    [("wd", "z", 1), ("dep", "z", 50)],
    [("dep", "a", 7), ("dep", "b", 8), ("wd", "a", 3), ("wd", "b", 9)],
)


def _batch_out35(steps):
    acc, done, out = {}, [], []
    ok = True
    for (k, who, amt) in steps:
        if k == "dep":
            acc[who] = acc.get(who, 0) + amt
            done.append((k, who, amt))
        else:
            if acc.get(who, 0) < amt:
                out.append(f"failed: insufficient funds for {who}")
                for (k2, w2, a2) in reversed(done):
                    acc[w2] = acc.get(w2, 0) + (-a2 if k2 == "dep" else a2)
                ok = False
                break
            acc[who] = acc.get(who, 0) - amt
            done.append((k, who, amt))
    out.append("committed" if ok else "rolled back")
    out.append("{" + ", ".join(f"{k}={acc[k]}" for k in sorted(acc)) + "}")
    return _nl(*out)


def _batch_case35(steps):
    return _case("\n".join([str(len(steps))] + [f"{k} {w} {a}" for (k, w, a) in steps]),
                 _batch_out35(steps))


_P35_C = _jfam(
    "p35-behaviour", "Strategies and commands",
    "Behaviour chosen by name, behaviour carried by an enum, and actions that can be "
    "undone, redone or rolled back.",
    """
```java
Map<String, Comparator<String>> orders = Map.of("alpha", Comparator.naturalOrder(), ...);
enum Rounding { DOWN((v, s) -> ...), UP(...), NEAREST(...); }   // strategies as constants

Deque<Command> undo = new ArrayDeque<>(), redo = new ArrayDeque<>();
// do:   execute, push on undo, CLEAR redo
// undo: pop undo, reverse it, push on redo
// redo: pop redo, execute again, push on undo
```

The rollback drill is the command pattern doing real work: run a batch of steps,
and if one fails part-way, undo the ones that already ran - in reverse - so the
batch is all-or-nothing.
""",
    [
        _p35s("j35-pc-sort", "Sort orders by name", "Intro",
              "Sort the words by the named strategy: `alpha`, `reverse`, or `length` "
              "(then alphabetical). Keep the strategies in a map.",
              "        Map<String, Comparator<String>> orders = new HashMap<>();\n"
              "        orders.put(\"alpha\", Comparator.naturalOrder());\n"
              "        orders.put(\"reverse\", Comparator.reverseOrder());\n"
              "        orders.put(\"length\", Comparator.comparing(String::length).thenComparing(Comparator.naturalOrder()));\n"
              "        int n = sc.nextInt();\n"
              "        List<String> words = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            words.add(sc.next());\n"
              "        }\n"
              "        words.sort(orders.get(sc.next()));\n"
              "        System.out.println(words);",
              [_case(f"{len(ws)}\n{' '.join(ws)}\n{how}", _jarr(_sorted35(ws, how))) for (ws, how) in _SORTS35],
              ["A `Comparator` IS a strategy.",
               "`Comparator.naturalOrder()` and `Comparator.reverseOrder()`.",
               "`Comparator.comparing(String::length).thenComparing(Comparator.naturalOrder())`.",
               "Choosing is one `get`: no `if` on the name."]),

        _p35t("j35-pc-round", "Rounding strategies as enum constants", "Easy",
              "Write `Rounding`'s three constants, each passing its rule as a lambda: DOWN "
              "and UP round to a multiple of `step` below or above; NEAREST rounds halves "
              "up. Use `Math.floorDiv` so negatives work.",
              _ROUNDING35,
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            int v = sc.nextInt();\n"
              "            int step = sc.nextInt();\n"
              "            StringBuilder out = new StringBuilder(v + \":\");\n"
              "            for (Rounding r : Rounding.values()) {\n"
              "                out.append(' ').append(r).append('=').append(r.apply(v, step));\n"
              "            }\n"
              "            System.out.println(out);\n"
              "        }",
              _ROUNDING_REGION35,
              [_rows35(rows, _nl(*[f"{v}: DOWN={_round35(v, s)[0]} UP={_round35(v, s)[1]} "
                                   f"NEAREST={_round35(v, s)[2]}" for (v, s) in rows]))
               for rows in _ROUNDS35],
              ["DOWN: `Math.floorDiv(v, step) * step`.",
               "UP is DOWN of the negation, negated: `-Math.floorDiv(-v, step) * step`.",
               "NEAREST: add half a step, then round down.",
               "Module 33's `Op` enum was this same pattern."]),

        _p35s("j35-pc-rules", "A list of validation rules", "Medium",
              "Check each password against three named rules, in order: at least 6 "
              "characters (`length`), a digit (`digit`), an upper-case letter (`upper`). "
              "Print `ok` or the names of the rules it fails. Keep the rules in a "
              "`LinkedHashMap<String, Predicate<String>>`.",
              "        Map<String, Predicate<String>> rules = new LinkedHashMap<>();\n"
              "        rules.put(\"length\", p -> p.length() >= 6);\n"
              "        rules.put(\"digit\", p -> p.chars().anyMatch(Character::isDigit));\n"
              "        rules.put(\"upper\", p -> p.chars().anyMatch(Character::isUpperCase));\n"
              "        int n = sc.nextInt();\n"
              "        sc.nextLine();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String p = sc.nextLine();\n"
              "            List<String> failed = new ArrayList<>();\n"
              "            for (Map.Entry<String, Predicate<String>> rule : rules.entrySet()) {\n"
              "                if (!rule.getValue().test(p)) {\n"
              "                    failed.add(rule.getKey());\n"
              "                }\n"
              "            }\n"
              "            String shown = p.isEmpty() ? \"(empty)\" : p;\n"
              "            System.out.println(shown + \": \" + (failed.isEmpty() ? \"ok\" : String.join(\", \", failed)));\n"
              "        }",
              [_case("\n".join([str(len(ws))] + ws) + "\n", _rules_out35(ws)) for ws in _RULES35],
              ["Each rule is a `Predicate<String>` - a strategy with a name.",
               "`LinkedHashMap` keeps the rules in the order you added them.",
               "`p.chars().anyMatch(Character::isDigit)` checks for a digit.",
               "A new rule is one more `put`; the checking loop never changes.",
               "Read with `nextLine()` so an empty password is still a line."]),

        _p35s("j35-pc-redo", "Undo and redo", "Medium",
              "Keep a running total. `add k` adds; `undo` reverses the last add; `redo` "
              "re-applies the last undone one. A new `add` clears the redo history. Print "
              "the total after every operation, on one line.",
              "        int n = sc.nextInt();\n"
              "        Deque<Integer> undo = new ArrayDeque<>();\n"
              "        Deque<Integer> redo = new ArrayDeque<>();\n"
              "        int total = 0;\n"
              "        StringBuilder out = new StringBuilder();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String op = sc.next();\n"
              "            if (op.equals(\"add\")) {\n"
              "                int k = sc.nextInt();\n"
              "                total += k;\n"
              "                undo.push(k);\n"
              "                redo.clear();\n"
              "            } else if (op.equals(\"undo\") && !undo.isEmpty()) {\n"
              "                int k = undo.pop();\n"
              "                total -= k;\n"
              "                redo.push(k);\n"
              "            } else if (op.equals(\"redo\") && !redo.isEmpty()) {\n"
              "                int k = redo.pop();\n"
              "                total += k;\n"
              "                undo.push(k);\n"
              "            }\n"
              "            if (i > 0) out.append(' ');\n"
              "            out.append(total);\n"
              "        }\n"
              "        System.out.println(out);",
              [_redo_case35(ops) for ops in _REDO35],
              ["Two stacks: what can be undone, and what can be redone.",
               "Undo moves an action from the undo stack to the redo stack; redo moves it "
               "back.",
               "A NEW action invalidates the redo history - clear it.",
               "Here each 'command' is just the amount added, which is all it needs to "
               "reverse itself."]),

        _p35h("j35-pc-rollback", "All or nothing", "Hard",
              "Write `runAll`: run each step, remembering the ones that succeeded; if a step "
              "throws `IllegalStateException`, print `failed: <message>`, undo every "
              "completed step in REVERSE order, and return false. `main` prints "
              "`committed` or `rolled back` and the balances.",
              _BATCH35, _RUNBATCH35,
              "        int n = sc.nextInt();\n"
              "        List<Step> steps = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String kind = sc.next();\n"
              "            String who = sc.next();\n"
              "            int amount = sc.nextInt();\n"
              "            steps.add(kind.equals(\"dep\") ? new Deposit(who, amount) : new Withdraw(who, amount));\n"
              "        }\n"
              "        Map<String, Integer> accounts = new TreeMap<>();\n"
              "        System.out.println(runAll(steps, accounts) ? \"committed\" : \"rolled back\");\n"
              "        System.out.println(accounts);",
              _RUNBATCH35,
              [_batch_case35(s) for s in _BATCHES35],
              ["Push each successful step on a `Deque` - it is the undo history.",
               "Catch the failure around each `run`.",
               "`while (!done.isEmpty()) done.pop().undo(accounts);` reverses in the right "
               "order.",
               "Undoing a deposit leaves a zero balance behind rather than removing the "
               "account - the output shows it.",
               "This is how a database transaction's rollback behaves, in miniature."]),
    ],
)


# --- Family D - observers ----------------------------------------------------------

_KINDEVS35 = (["click", "scroll", "click"], ["key"], ["a", "b", "a", "c", "a"], ["x", "x"], ["load", "click", "load"])

_FILTERBUS35 = """
class Bus {
    private final List<Consumer<String>> listeners = new ArrayList<>();

    void subscribe(Predicate<String> filter, Consumer<String> listener) {
        listeners.add(e -> {
            if (filter.test(e)) {
                listener.accept(e);
            }
        });
    }

    void publish(String event) {
        for (Consumer<String> l : listeners) {
            l.accept(event);
        }
    }
}
"""
_FILTER_REGION35 = (
    "    void subscribe(Predicate<String> filter, Consumer<String> listener) {\n"
    "        listeners.add(e -> {\n"
    "            if (filter.test(e)) {\n"
    "                listener.accept(e);\n"
    "            }\n"
    "        });\n"
    "    }"
)
_FEVS35 = (["error:disk", "info:ok", "error:net"], ["info:x"], ["warn:a", "error:b"], ["error:z"],
           ["info:1", "warn:2", "error:3", "info:4"])


def _filter_out35(evs):
    out = []
    for e in evs:
        if e.startswith("error"):
            out.append(f"pager {e}")
        out.append(f"log {e}")
    return _nl(*out)


_PROPERTY35 = """
class Property<T> {
    private T value;
    private final List<BiConsumer<T, T>> listeners = new ArrayList<>();

    Property(T initial) {
        this.value = initial;
    }

    void onChange(BiConsumer<T, T> listener) {
        listeners.add(listener);
    }

    void set(T newValue) {
        if (Objects.equals(value, newValue)) {
            return;
        }
        T old = value;
        value = newValue;
        for (BiConsumer<T, T> l : listeners) {
            l.accept(old, newValue);
        }
    }

    T get() {
        return value;
    }
}
"""
_PROPERTY_REGION35 = (
    "    void set(T newValue) {\n"
    "        if (Objects.equals(value, newValue)) {\n"
    "            return;\n"
    "        }\n"
    "        T old = value;\n"
    "        value = newValue;\n"
    "        for (BiConsumer<T, T> l : listeners) {\n"
    "            l.accept(old, newValue);\n"
    "        }\n"
    "    }"
)
_PROPS35 = (["red", "red", "blue"], ["x"], ["a", "b", "b", "a"], ["same", "same"], ["p", "q", "r", "q"])


def _props_out35(vals):
    cur, out, changes = "none", [], 0
    for v in vals:
        if v != cur:
            out.append(f"{cur} -> {v}")
            changes += 1
            cur = v
    out.append(f"final {cur}, {changes} changes")
    return _nl(*out)


_SAFEBUS35 = """
class SafeBus {
    private final List<Consumer<String>> listeners = new ArrayList<>();
    private int failures;

    void subscribe(Consumer<String> l) {
        listeners.add(l);
    }

    void publish(String event) {
        for (Consumer<String> l : listeners) {
            try {
                l.accept(event);
            } catch (RuntimeException e) {
                failures++;
            }
        }
    }

    int failures() {
        return failures;
    }
}
"""
_SAFE_REGION35 = (
    "    void publish(String event) {\n"
    "        for (Consumer<String> l : listeners) {\n"
    "            try {\n"
    "                l.accept(event);\n"
    "            } catch (RuntimeException e) {\n"
    "                failures++;\n"
    "            }\n"
    "        }\n"
    "    }"
)
_SAFEEVS35 = (["hello", "boom", "ok"], ["boom"], ["a", "b"], ["boom", "boom"], ["x", "boom", "y", "boom"])


def _safe_out35(evs):
    out, fails = [], 0
    for e in evs:
        out.append(f"first {e}")
        if e == "boom":
            fails += 1
        else:
            out.append(f"second {e}")
        out.append(f"third {e}")
    out.append(f"failures {fails}")
    return _nl(*out)


_ONCEBUS35 = """
class OnceBus {
    private final List<Consumer<String>> listeners = new CopyOnWriteArrayList<>();

    void subscribe(Consumer<String> l) {
        listeners.add(l);
    }

    void subscribeOnce(Consumer<String> l) {
        Consumer<String>[] self = new Consumer[1];
        self[0] = e -> {
            listeners.remove(self[0]);
            l.accept(e);
        };
        listeners.add(self[0]);
    }

    void publish(String event) {
        for (Consumer<String> l : listeners) {
            l.accept(event);
        }
    }
}
"""
_ONCEBUS_REGION35 = (
    "    void subscribeOnce(Consumer<String> l) {\n"
    "        Consumer<String>[] self = new Consumer[1];\n"
    "        self[0] = e -> {\n"
    "            listeners.remove(self[0]);\n"
    "            l.accept(e);\n"
    "        };\n"
    "        listeners.add(self[0]);\n"
    "    }"
)
_ONCEEVS35 = (["a", "b", "c"], ["solo"], ["x", "y"], ["p", "q", "r", "s"], ["m", "n", "o"])


def _oncebus_out35(evs):
    out = []
    for i, e in enumerate(evs):
        if i == 0:
            out.append(f"welcome {e}")
        out.append(f"always {e}")
        if i == 0:
            out.append(f"also once {e}")
    return _nl(*out)


_P35_D = _jfam(
    "p35-observer", "Observers",
    "Counting, filtering, reacting to change, surviving a failing listener, and "
    "listeners that run once.",
    """
```java
bus.subscribe(e -> e.startsWith("error"), e -> page(e));    // filtered
property.onChange((old, now) -> log(old + " -> " + now));   // change listener
try { l.accept(event); } catch (RuntimeException e) { failures++; }   // isolate
new CopyOnWriteArrayList<>()                                 // safe self-removal
```

A property that notifies only on *actual* change (`Objects.equals`, module 32)
is the observer pattern at the heart of every UI framework. And isolating each
listener in its own `try` is what stops one buggy subscriber from silencing all
the others.
""",
    [
        _p35s("j35-pd-count", "A counting listener", "Intro",
              "Subscribe one listener that counts events by name into a `TreeMap`, publish "
              "every event to it, and print the counts.",
              "        List<Consumer<String>> listeners = new ArrayList<>();\n"
              "        Map<String, Integer> counts = new TreeMap<>();\n"
              "        listeners.add(e -> counts.merge(e, 1, Integer::sum));\n"
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String event = sc.next();\n"
              "            for (Consumer<String> l : listeners) {\n"
              "                l.accept(event);\n"
              "            }\n"
              "        }\n"
              "        System.out.println(counts);",
              [_toks35(evs, "{" + ", ".join(f"{k}={evs.count(k)}" for k in sorted(set(evs))) + "}")
               for evs in _KINDEVS35],
              ["A listener is just a `Consumer<String>`.",
               "`counts.merge(e, 1, Integer::sum)` inside the lambda.",
               "`counts` is effectively final - the lambda mutates the map, not the "
               "variable."]),

        _p35t("j35-pd-filter", "A filtered subscription", "Easy",
              "Write `subscribe(filter, listener)`: store a wrapper that calls the listener "
              "only for events the filter accepts. `main` pages on errors and logs "
              "everything.",
              _FILTERBUS35,
              "        Bus bus = new Bus();\n"
              "        bus.subscribe(e -> e.startsWith(\"error\"), e -> System.out.println(\"pager \" + e));\n"
              "        bus.subscribe(e -> true, e -> System.out.println(\"log \" + e));\n"
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            bus.publish(sc.next());\n"
              "        }",
              _FILTER_REGION35,
              [_toks35(evs, _filter_out35(evs)) for evs in _FEVS35],
              ["The bus still stores plain `Consumer`s.",
               "Wrap: `listeners.add(e -> { if (filter.test(e)) listener.accept(e); });`",
               "The wrapper is itself a decorator around the listener.",
               "The pager subscribed first, so its line comes first."]),

        _p35t("j35-pd-property", "An observable property", "Medium",
              "Write `Property.set`: ignore a value equal to the current one; otherwise "
              "store it and notify every listener with the old and new values. `main` "
              "prints each change and a summary.",
              _PROPERTY35,
              "        Property<String> colour = new Property<>(\"none\");\n"
              "        int[] changes = {0};\n"
              "        colour.onChange((old, now) -> System.out.println(old + \" -> \" + now));\n"
              "        colour.onChange((old, now) -> changes[0]++);\n"
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            colour.set(sc.next());\n"
              "        }\n"
              "        System.out.println(\"final \" + colour.get() + \", \" + changes[0] + \" changes\");",
              _PROPERTY_REGION35,
              [_toks35(v, _props_out35(v)) for v in _PROPS35],
              ["`Objects.equals(value, newValue)` - null-safe, and true means 'no change'.",
               "Remember the old value BEFORE overwriting it.",
               "Then call `l.accept(old, newValue)` on every listener.",
               "Setting the same colour twice notifies nobody."]),

        _p35t("j35-pd-safe", "One bad listener", "Medium",
              "The second listener throws on `boom`. Write `publish` so each listener runs "
              "in its own `try`, a failure is counted, and the listeners after it still run.",
              _SAFEBUS35,
              "        SafeBus bus = new SafeBus();\n"
              "        bus.subscribe(e -> System.out.println(\"first \" + e));\n"
              "        bus.subscribe(e -> {\n"
              "            if (e.equals(\"boom\")) {\n"
              "                throw new IllegalArgumentException(e);\n"
              "            }\n"
              "            System.out.println(\"second \" + e);\n"
              "        });\n"
              "        bus.subscribe(e -> System.out.println(\"third \" + e));\n"
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            bus.publish(sc.next());\n"
              "        }\n"
              "        System.out.println(\"failures \" + bus.failures());",
              _SAFE_REGION35,
              [_toks35(evs, _safe_out35(evs)) for evs in _SAFEEVS35],
              ["Put the `try` INSIDE the loop, around one listener's call.",
               "Catch `RuntimeException` - a listener cannot throw a checked one through "
               "`Consumer`.",
               "Count it and carry on to the next listener.",
               "With the `try` outside the loop, `third` would be silenced on every "
               "`boom`."]),

        _p35t("j35-pd-once", "Run once", "Hard",
              "Write `subscribeOnce`: register a wrapper that removes ITSELF and then calls "
              "the listener. The list is a `CopyOnWriteArrayList`, so removing during "
              "`publish` is safe.",
              _ONCEBUS35,
              "        OnceBus bus = new OnceBus();\n"
              "        bus.subscribeOnce(e -> System.out.println(\"welcome \" + e));\n"
              "        bus.subscribe(e -> System.out.println(\"always \" + e));\n"
              "        bus.subscribeOnce(e -> System.out.println(\"also once \" + e));\n"
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            bus.publish(sc.next());\n"
              "        }",
              _ONCEBUS_REGION35,
              [_toks35(evs, _oncebus_out35(evs)) for evs in _ONCEEVS35],
              ["The wrapper has to refer to itself to remove itself - a lambda cannot "
               "name itself directly.",
               "A one-element array does it: `Consumer<String>[] self = new "
               "Consumer[1];` then `self[0] = e -> { ... };`.",
               "(That array creation is an unchecked warning - generic arrays, module 24 - "
               "and harmless here.)",
               "Inside: `listeners.remove(self[0]);` then `l.accept(e);`.",
               "A CopyOnWriteArrayList iterates over a snapshot, so the removal cannot "
               "disturb the loop in progress."]),
    ],
)


# --- Family E - structural ----------------------------------------------------------

_GREET35 = """
interface Greeting {
    String say(String name);
}

class Hello implements Greeting {
    public String say(String name) {
        return "hello " + name;
    }
}

class Polite implements Greeting {
    private final Greeting inner;

    Polite(Greeting inner) {
        this.inner = inner;
    }

    public String say(String name) {
        return inner.say(name) + ", please";
    }
}

class Loud implements Greeting {
    private final Greeting inner;

    Loud(Greeting inner) {
        this.inner = inner;
    }

    public String say(String name) {
        return inner.say(name).toUpperCase() + "!";
    }
}
"""
_GREET_REGION35 = _after35(_GREET35, "class Polite")
_GREETS35 = (("ada", "pl"), ("bo", "lp"), ("cy", ""), ("di", "ll"), ("ed", "plp"))


def _greets35(name, spec):
    s = f"hello {name}"
    for c in spec:
        s = s + ", please" if c == "p" else s.upper() + "!"
    return s


_COUNTED35 = (
    "    static IntUnaryOperator counted(IntUnaryOperator f, int[] calls) {\n"
    "        return x -> {\n"
    "            calls[0]++;\n"
    "            return f.applyAsInt(x);\n"
    "        };\n"
    "    }"
)
_CALLS35 = ([3, 4], [0], [1, 2, 3, 4, 5], [-2, 10], [7])

_SENSOR35 = """
interface Thermometer {
    int celsius();
}

class FahrenheitSensor {
    private final int reading;

    FahrenheitSensor(int reading) {
        this.reading = reading;
    }

    int readFahrenheit() {
        return reading;
    }
}

class SensorAdapter implements Thermometer {
    private final FahrenheitSensor sensor;

    SensorAdapter(FahrenheitSensor sensor) {
        this.sensor = sensor;
    }

    public int celsius() {
        return (sensor.readFahrenheit() - 32) * 5 / 9;
    }
}
"""
_SENSOR_REGION35 = _after35(_SENSOR35, "class SensorAdapter")
_SENSORS35 = ([("c", 21), ("f", 212)], [("f", 32)], [("f", 98), ("c", -3), ("f", 0)], [("c", 100)],
              [("f", 50), ("f", 51)])

_MENU35 = """
interface MenuEntry {
    int price();

    int items();

    void print(String indent);
}

class Dish implements MenuEntry {
    private final String name;
    private final int price;

    Dish(String name, int price) {
        this.name = name;
        this.price = price;
    }

    public int price() {
        return price;
    }

    public int items() {
        return 1;
    }

    public void print(String indent) {
        System.out.println(indent + name + " " + price);
    }
}

class Section implements MenuEntry {
    private final String name;
    private final List<MenuEntry> entries = new ArrayList<>();

    Section(String name) {
        this.name = name;
    }

    void add(MenuEntry e) {
        entries.add(e);
    }

    public int price() {
        int total = 0;
        for (MenuEntry e : entries) {
            total += e.price();
        }
        return total;
    }

    public int items() {
        int total = 0;
        for (MenuEntry e : entries) {
            total += e.items();
        }
        return total;
    }

    public void print(String indent) {
        System.out.println(indent + name + " (" + items() + " items)");
        for (MenuEntry e : entries) {
            e.print(indent + "  ");
        }
    }
}
"""
_MENU_REGION35 = _after35(_MENU35, "class Section")
_PARSEMENU35 = (
    "    static MenuEntry parse(Scanner sc) {\n"
    "        String kind = sc.next();\n"
    "        String name = sc.next();\n"
    "        if (kind.equals(\"dish\")) {\n"
    "            return new Dish(name, sc.nextInt());\n"
    "        }\n"
    "        Section s = new Section(name);\n"
    "        int k = sc.nextInt();\n"
    "        for (int i = 0; i < k; i++) {\n"
    "            s.add(parse(sc));\n"
    "        }\n"
    "        return s;\n"
    "    }"
)
_MENUS35 = ("section menu 2 dish soup 5 section mains 2 dish fish 12 dish pie 9",
            "dish toast 3",
            "section drinks 0",
            "section all 3 dish a 1 dish b 2 section more 1 dish c 3",
            "section x 1 section y 1 section z 2 dish p 4 dish q 6")


def _menu_parse35(tokens):
    kind, name = tokens.pop(0), tokens.pop(0)
    if kind == "dish":
        return ("dish", name, int(tokens.pop(0)))
    k = int(tokens.pop(0))
    return ("section", name, [_menu_parse35(tokens) for _ in range(k)])


def _menu_price35(n):
    return n[2] if n[0] == "dish" else sum(_menu_price35(c) for c in n[2])


def _menu_items35(n):
    return 1 if n[0] == "dish" else sum(_menu_items35(c) for c in n[2])


def _menu_print35(n, indent=""):
    if n[0] == "dish":
        return [f"{indent}{n[1]} {n[2]}"]
    lines = [f"{indent}{n[1]} ({_menu_items35(n)} items)"]
    for c in n[2]:
        lines += _menu_print35(c, indent + "  ")
    return lines


def _menu_case35(src):
    t = _menu_parse35(src.split())
    return _case(src, _nl(*_menu_print35(t), f"total {_menu_price35(t)}"))


_ORG35 = """
interface Staff {
    int payroll();

    int headcount();

    int depth();
}

class Employee implements Staff {
    private final int salary;

    Employee(int salary) {
        this.salary = salary;
    }

    public int payroll() {
        return salary;
    }

    public int headcount() {
        return 1;
    }

    public int depth() {
        return 1;
    }
}

class Manager implements Staff {
    private final int salary;
    private final List<Staff> reports = new ArrayList<>();

    Manager(int salary) {
        this.salary = salary;
    }

    void add(Staff s) {
        reports.add(s);
    }

    public int payroll() {
        int total = salary;
        for (Staff s : reports) {
            total += s.payroll();
        }
        return total;
    }

    public int headcount() {
        int total = 1;
        for (Staff s : reports) {
            total += s.headcount();
        }
        return total;
    }

    public int depth() {
        int deepest = 0;
        for (Staff s : reports) {
            deepest = Math.max(deepest, s.depth());
        }
        return 1 + deepest;
    }
}
"""
_ORG_REGION35 = _after35(_ORG35, "class Manager")
_PARSEORG35 = (
    "    static Staff parse(Scanner sc) {\n"
    "        String kind = sc.next();\n"
    "        int salary = sc.nextInt();\n"
    "        if (kind.equals(\"emp\")) {\n"
    "            return new Employee(salary);\n"
    "        }\n"
    "        Manager m = new Manager(salary);\n"
    "        int k = sc.nextInt();\n"
    "        for (int i = 0; i < k; i++) {\n"
    "            m.add(parse(sc));\n"
    "        }\n"
    "        return m;\n"
    "    }"
)
_ORGS35 = ("mgr 100 2 emp 50 emp 60", "emp 40", "mgr 200 1 mgr 120 2 emp 70 mgr 90 1 emp 30",
           "mgr 10 0", "mgr 300 3 emp 1 emp 2 mgr 50 1 emp 3")


def _org_parse35(tokens):
    kind, sal = tokens.pop(0), int(tokens.pop(0))
    if kind == "emp":
        return (sal, [])
    k = int(tokens.pop(0))
    return (sal, [_org_parse35(tokens) for _ in range(k)], True)


def _org_stats35(n):
    pay = n[0] + sum(_org_stats35(c)[0] for c in n[1])
    head = 1 + sum(_org_stats35(c)[1] for c in n[1])
    depth = 1 + max([_org_stats35(c)[2] for c in n[1]] or [0])
    return pay, head, depth


def _org_case35(src):
    p, h, d = _org_stats35(_org_parse35(src.split()))
    return _case(src, f"payroll {p}, headcount {h}, depth {d}")


_P35_E = _jfam(
    "p35-structure", "Decorators, adapters and composites",
    "Wrappers that add behaviour, wrappers that change shape, and trees that look "
    "like leaves.",
    """
```java
new Loud(new Polite(new Hello()))                  // decorators stack
static IntUnaryOperator counted(IntUnaryOperator f, int[] calls) {  // a decorator
    return x -> { calls[0]++; return f.applyAsInt(x); };             // as a lambda
}
class SensorAdapter implements Thermometer { ... }  // adapter
class Section implements MenuEntry { List<MenuEntry> entries; ... }  // composite
```

A decorator does not have to be a class: a function that takes a function and
returns a wrapped one - `counted(f)` - is a decorator too, and is how timing,
logging and retry wrappers are usually written today.
""",
    [
        _p35t("j35-pe-greet", "Stacked greetings", "Intro",
              "Write the `Polite` (appends `, please`) and `Loud` (upper-cases and appends "
              "`!`) decorators. `main` applies them in the order given (`p` and `l`).",
              _GREET35,
              "        String name = sc.next();\n"
              "        String spec = sc.hasNext() ? sc.next() : \"\";\n"
              "        Greeting g = new Hello();\n"
              "        for (char c : spec.toCharArray()) {\n"
              "            g = c == 'p' ? new Polite(g) : new Loud(g);\n"
              "        }\n"
              "        System.out.println(g.say(name));",
              _GREET_REGION35,
              [_case(f"{n} {s}" if s else f"{n}\n", _greets35(n, s)) for (n, s) in _GREETS35],
              ["Each decorator implements `Greeting` and holds a `Greeting`.",
               "`Polite.say`: `inner.say(name) + \", please\"`.",
               "`Loud.say`: `inner.say(name).toUpperCase() + \"!\"`.",
               "Order matters: polite-then-loud shouts the please too."]),

        _p35h("j35-pe-counted", "A decorator made of a lambda", "Easy",
              "Write `counted(f, calls)`: return a function that increments `calls[0]` and "
              "then delegates to `f`. `main` wraps a squaring function and reports the "
              "results and how many calls went through.",
              "", _COUNTED35,
              "        int[] calls = {0};\n"
              "        IntUnaryOperator square = counted(x -> x * x, calls);\n"
              "        int n = sc.nextInt();\n"
              "        StringBuilder out = new StringBuilder();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            if (i > 0) out.append(' ');\n"
              "            out.append(square.applyAsInt(sc.nextInt()));\n"
              "        }\n"
              "        System.out.println(out);\n"
              "        System.out.println(\"calls \" + calls[0]);",
              _COUNTED35,
              [_acase(xs, _nl(_sp([x * x for x in xs]), f"calls {len(xs)}")) for xs in _CALLS35],
              ["Return a lambda: `x -> { calls[0]++; return f.applyAsInt(x); }`.",
               "It has the same type as `f`, so callers cannot tell it is wrapped.",
               "The counter lives in a one-element array because the lambda must capture "
               "an effectively final variable."]),

        _p35t("j35-pe-adapter", "Adapting a Fahrenheit sensor", "Medium",
              "The rest of the program speaks `Thermometer` (Celsius). Write `SensorAdapter`, "
              "which makes a legacy `FahrenheitSensor` look like one - `(f - 32) * 5 / 9`.",
              _SENSOR35,
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String kind = sc.next();\n"
              "            int v = sc.nextInt();\n"
              "            Thermometer t = kind.equals(\"c\") ? () -> v : new SensorAdapter(new FahrenheitSensor(v));\n"
              "            System.out.println(t.celsius() + \" C\");\n"
              "        }",
              _SENSOR_REGION35,
              [_rows35(rows, _nl(*[f"{v if k == 'c' else _jdiv((v - 32) * 5, 9)} C" for (k, v) in rows]))
               for rows in _SENSORS35],
              ["`class SensorAdapter implements Thermometer` holding a `FahrenheitSensor`.",
               "`celsius()` reads Fahrenheit and converts.",
               "A Celsius reading needs no adapter: `Thermometer` has one method, so a "
               "lambda implements it directly.",
               "The rest of the program never learns the sensor speaks Fahrenheit."]),

        _p35h("j35-pe-menu", "A menu as a composite", "Medium",
              "Write `Section`: it holds `MenuEntry`s (dishes or other sections); its price "
              "and item count are sums over its entries; `print` shows `name (N items)` "
              "and then each entry indented two more spaces.",
              _MENU35, _PARSEMENU35,
              "        MenuEntry menu = parse(sc);\n"
              "        menu.print(\"\");\n"
              "        System.out.println(\"total \" + menu.price());",
              _MENU_REGION35,
              [_menu_case35(src) for src in _MENUS35],
              ["`class Section implements MenuEntry` with a `List<MenuEntry> entries`.",
               "`price()` and `items()` loop and add - each entry may be another section.",
               "`print` prints its header, then `e.print(indent + \"  \")` for each entry.",
               "An empty section has 0 items and costs 0."]),

        _p35h("j35-pe-org", "An organisation chart", "Hard",
              "Write `Manager`, the composite: a manager has a salary and direct reports "
              "(employees or managers). `payroll` includes everyone below; `headcount` "
              "counts the manager too; `depth` is the number of levels from this person "
              "down to the deepest report.",
              _ORG35, _PARSEORG35,
              "        Staff top = parse(sc);\n"
              "        System.out.println(\"payroll \" + top.payroll() + \", headcount \" + top.headcount()\n"
              "                + \", depth \" + top.depth());",
              _ORG_REGION35,
              [_org_case35(src) for src in _ORGS35],
              ["`payroll`: own salary plus every report's payroll.",
               "`headcount`: 1 plus every report's headcount.",
               "`depth`: 1 plus the deepest report's depth - 0 extra if there are no "
               "reports.",
               "Nothing checks whether a report is an Employee or a Manager: both are "
               "`Staff`."]),
    ],
)


_PRACTICE[35] = [_P35_A, _P35_B, _P35_C, _P35_D, _P35_E]
