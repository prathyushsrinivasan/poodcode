# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 37 practice - the JVM.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[37]`. The last practice
# file in the course.
#
# Same rule as the module: only behaviour the JLS or JVM specification fixes
# reaches the output. Initialisation order is specified; garbage collection is
# SIMULATED; stack depth is avoided (explicit stacks) rather than measured.
# ---------------------------------------------------------------------------


def _p37(eid, title, difficulty, prompt, types, body, region, tests, hints, helpers=""):
    return _jch(eid, title, difficulty, prompt, _j37t(types, body, helpers=helpers),
                region.strip("\n"), tests, hints)


# --- Family A - initialisation ---------------------------------------------------

_COUNTER37 = """
class Ticket {
    static int issued;

    static {
        System.out.println("Ticket loaded");
    }

    final int number;

    Ticket() {
        issued++;
        number = issued;
    }
}
"""
_TICKETS37 = (3, 1, 0, 5, 2)


def _tickets_out37(k):
    lines = ["open"]
    if k:
        lines.append("Ticket loaded")
        lines.append(_sp(list(range(1, k + 1))))
    lines.append(f"close {k}")
    return _nl(*lines)


_STATICORDER37 = """
class Config {
    static int base = 5;
    static int doubled = twice();

    static int twice() {
        return base * 2;
    }
}
"""
_STATICORDER_REGION37 = (
    "    static int base = 5;\n"
    "    static int doubled = twice();"
)

_CHAIN3_37 = """
class Vehicle {
    Vehicle(String kind) {
        System.out.println("vehicle: " + kind);
    }
}

class Car extends Vehicle {
    Car(String model) {
        super("car");
        System.out.println("car: " + model);
    }
}

class SportsCar extends Car {
    SportsCar(String model, int topSpeed) {
        super(model);
        System.out.println("sports car: " + topSpeed + " km/h");
    }
}
"""
_CHAIN3_REGION37 = _CHAIN3_37[_CHAIN3_37.index("class SportsCar"):].strip("\n")
_SPORTS37 = (("gt", 300), ("roadster", 250), ("x", 1), ("zonda", 350), ("mini", 180))

_LAZYF37 = """
class Report {
    static int builds;
    private List<String> lines;

    private List<String> lines() {
        if (lines == null) {
            builds++;
            lines = new ArrayList<>();
            lines.add("header");
        }
        return lines;
    }

    void add(String line) {
        lines().add(line);
    }

    int size() {
        return lines == null ? 0 : lines().size();
    }
}
"""
_LAZYF_REGION37 = (
    "    private List<String> lines() {\n"
    "        if (lines == null) {\n"
    "            builds++;\n"
    "            lines = new ArrayList<>();\n"
    "            lines.add(\"header\");\n"
    "        }\n"
    "        return lines;\n"
    "    }"
)
_LAZYOPS37 = ([2, 0, 3], [0], [1, 1, 1], [0, 0], [5])


def _lazy_out37(adds):
    out = []
    builds = 0
    for a in adds:
        if a > 0:
            builds += 1
            out.append(f"report size {a + 1}")
        else:
            out.append("report size 0")
    out.append(f"builds {builds}")
    return _nl(*out)


_ENUMINIT37 = """
enum Planet {
    MERCURY(1), VENUS(2), EARTH(3);

    final int order;

    Planet(int order) {
        this.order = order;
        System.out.println("constructing " + name());
    }

    static {
        System.out.println("Planet ready");
    }
}
"""
_PLANETQ37 = (["EARTH"], ["VENUS", "MERCURY"], ["MERCURY", "MERCURY"], ["EARTH", "VENUS", "EARTH"], ["VENUS"])


def _planets_out37(qs):
    order = {"MERCURY": 1, "VENUS": 2, "EARTH": 3}
    lines = ["before", "constructing MERCURY", "constructing VENUS", "constructing EARTH",
             "Planet ready"]
    lines += [f"{q} {order[q]}" for q in qs]
    return _nl(*lines)


_P37_A = _jfam(
    "p37-init", "Initialisation",
    "When statics run, in what order fields are set, how constructors chain, and "
    "when an enum's constants are built.",
    """
The rules, once more:

* a class is initialised on first active use, **once**, superclass first;
* static fields and static blocks run **top to bottom**; so do instance field
  initialisers and instance blocks;
* every constructor starts with `super(...)` - so constructors run from the top
  of the hierarchy down;
* an enum's constants are ordinary static fields of the enum, created - in
  declaration order - when the enum class is initialised, before any static
  block written after them.

A static field read before its initialiser has run holds its default value, `0`
or `null` - no exception, just a wrong number.
""",
    [
        _p37("j37-pa-tickets", "Loaded on first use", "Intro",
             "Issue `k` tickets and print their numbers on one line, between `open` and "
             "`close k`. The class announces itself when it is initialised - watch when "
             "(and whether) that happens.",
             _COUNTER37,
             "        int k = sc.nextInt();\n"
             "        System.out.println(\"open\");\n"
             "        StringBuilder out = new StringBuilder();\n"
             "        for (int i = 0; i < k; i++) {\n"
             "            Ticket t = new Ticket();\n"
             "            if (out.length() > 0) out.append(' ');\n"
             "            out.append(t.number);\n"
             "        }\n"
             "        if (k > 0) {\n"
             "            System.out.println(out);\n"
             "        }\n"
             "        System.out.println(\"close \" + k);",
             "        for (int i = 0; i < k; i++) {\n"
             "            Ticket t = new Ticket();\n"
             "            if (out.length() > 0) out.append(' ');\n"
             "            out.append(t.number);\n"
             "        }",
             [_case(str(k), _tickets_out37(k)) for k in _TICKETS37],
             ["The first `new Ticket()` initialises the class.",
              "With k = 0 the class is never used, so it is never initialised.",
              "`issued` is static - shared by every ticket."]),

        _p37("j37-pa-staticorder", "Statics, top to bottom", "Easy",
             "`Config.doubled` should be `base * 2`, but written in the wrong order it "
             "reads `base` before `base` is set - and gets 0. Write the two static fields in "
             "the order that makes `doubled` 10.",
             _STATICORDER37,
             "        int k = sc.nextInt();\n"
             "        System.out.println(\"base \" + Config.base);\n"
             "        System.out.println(\"doubled \" + Config.doubled * k);",
             _STATICORDER_REGION37,
             [_case(str(k), _nl("base 5", f"doubled {10 * k}")) for k in (1, 2, 3, 0, 10)],
             ["Static initialisers run in the order they are written.",
              "`twice()` reads `base`; `base` must already be assigned.",
              "Declare `base` first.",
              "In the wrong order `doubled` is silently 0 - no error at all."]),

        _p37("j37-pa-chain", "Three constructors deep", "Medium",
             "Write `SportsCar(String model, int topSpeed)`: it must pass the model up to "
             "`Car`, then print `sports car: <speed> km/h`. The output shows the "
             "constructors running from the top of the hierarchy down.",
             _CHAIN3_37,
             "        new SportsCar(sc.next(), sc.nextInt());",
             _CHAIN3_REGION37,
             [_case(f"{m} {s}", _nl("vehicle: car", f"car: {m}", f"sports car: {s} km/h"))
              for (m, s) in _SPORTS37],
             ["`class SportsCar extends Car` with the two-argument constructor.",
              "Its first statement must be `super(model);`.",
              "`Car`'s constructor calls `super(\"car\")` in turn - so Vehicle prints first.",
              "`super(...)` has to come before anything that uses the object - so the "
              "parent is always fully built first."]),

        _p37("j37-pa-lazy", "Lazy fields", "Medium",
             "A `Report`'s list of lines is expensive, so it is built only on first use. "
             "Write the private `lines()` accessor that builds it (counting the build and "
             "adding a `header` line) the first time, and returns it thereafter. For each "
             "input number, `main` makes a report, adds that many lines, and prints its "
             "size.",
             _LAZYF37,
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            int adds = sc.nextInt();\n"
             "            Report r = new Report();\n"
             "            for (int j = 0; j < adds; j++) {\n"
             "                r.add(\"line\");\n"
             "            }\n"
             "            System.out.println(\"report size \" + r.size());\n"
             "        }\n"
             "        System.out.println(\"builds \" + Report.builds);",
             _LAZYF_REGION37,
             [_toks37([str(a) for a in adds], _lazy_out37(adds)) for adds in _LAZYOPS37],
             ["`if (lines == null)` - build it only the first time.",
              "Count the build in the static `builds`.",
              "A report that never gets a line never builds its list.",
              "This is the instance-level cousin of the holder idiom - but NOT thread-safe."]),

        _p37("j37-pa-enum", "When enum constants are built", "Hard",
             "Look up planets by name. The constructor and the static block announce "
             "themselves, so the output shows exactly when the constants are created.",
             _ENUMINIT37,
             "        int n = sc.nextInt();\n"
             "        System.out.println(\"before\");\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            Planet p = Planet.valueOf(sc.next());\n"
             "            System.out.println(p + \" \" + p.order);\n"
             "        }",
             "        for (int i = 0; i < n; i++) {\n"
             "            Planet p = Planet.valueOf(sc.next());\n"
             "            System.out.println(p + \" \" + p.order);\n"
             "        }",
             [_toks37(qs, _planets_out37(qs)) for qs in _PLANETQ37],
             ["The first use of `Planet` initialises the whole enum.",
              "Its constants are static fields, created in declaration order - ALL of them, "
              "whichever one you asked for.",
              "They come before the static block, because they are declared first.",
              "An enum constructor cannot read the enum's own static fields for exactly "
              "this reason: they are not set yet."]),
    ],
)


# --- Family B - the stack, made explicit -----------------------------------------

_FACTN37 = (3, 1, 4, 2, 5)


def _fact_trace37(n):
    out = []

    def rec(k, depth):
        out.append("  " * depth + f"enter {k}")
        r = 1 if k <= 1 else k * rec(k - 1, depth + 1)
        out.append("  " * depth + f"exit {k} = {r}")
        return r

    rec(n, 0)
    return _nl(*out)


_FACTTRACE37 = (
    "    static long fact(int n, int depth) {\n"
    "        String pad = \"  \".repeat(depth);\n"
    "        System.out.println(pad + \"enter \" + n);\n"
    "        long result = n <= 1 ? 1 : n * fact(n - 1, depth + 1);\n"
    "        System.out.println(pad + \"exit \" + n + \" = \" + result);\n"
    "        return result;\n"
    "    }"
)

_FIBS37 = (10, 1, 50, 90, 2)


def _fib37(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


_GRAPHSB37 = (
    ({1: [2, 3], 2: [4], 3: [4], 4: []}, 1),
    ({1: [], 2: [1]}, 2),
    ({1: [2], 2: [3], 3: [1]}, 1),
    ({5: [3, 1], 3: [2], 1: [2], 2: []}, 5),
    ({1: [4, 2], 2: [3], 3: [], 4: [3]}, 1),
)


def _dfs37(adj, start):
    seen, order, stack = set(), [], [start]
    while stack:
        v = stack.pop()
        if v in seen:
            continue
        seen.add(v)
        order.append(v)
        for w in sorted(adj[v], reverse=True):
            if w not in seen:
                stack.append(w)
    return order


def _graph_case37(adj, start):
    edges = [(a, b) for a in sorted(adj) for b in adj[a]]
    stdin = "\n".join([f"{len(adj)} {len(edges)}"] + [f"{a} {b}" for (a, b) in edges] + [str(start)])
    return _case(stdin, _sp(_dfs37(adj, start)))


_BSTS37 = ([5, 3, 8, 1, 4], [1], [10, 5, 15, 5, 12], [3, 2, 1], [7, 9, 8, 10, 6])

_HANOI37 = (1, 2, 3, 4, 2)


def _hanoi37(n, a="A", b="B", c="C"):
    if n == 0:
        return []
    return _hanoi37(n - 1, a, c, b) + [f"{n}: {a} -> {c}"] + _hanoi37(n - 1, b, a, c)


_P37_B = _jfam(
    "p37-stack", "The stack, made explicit",
    "Watch frames push and pop, then replace the call stack with one of your own.",
    """
Every recursive algorithm uses the thread's stack to remember "where was I?".
Making that stack explicit - an `ArrayDeque` on the heap - removes the depth
limit and often makes the algorithm clearer:

```java
Deque<Integer> stack = new ArrayDeque<>();
stack.push(start);
while (!stack.isEmpty()) {
    int v = stack.pop();
    ...                          // what the recursive call's body did
    stack.push(next);            // what the recursive call did
}
```

When the recursion does work *after* the call returns (in-order traversal,
Towers of Hanoi), the explicit stack must also remember *which part* of the body
to resume - exactly what a real stack frame's return address records.
""",
    [
        _p37("j37-pb-trace", "Frames in and out", "Intro",
             "Print a trace of recursive factorial: `enter n` as each call starts and `exit n "
             "= result` as it returns, indented two spaces per level.",
             "",
             "        fact(sc.nextInt(), 0);",
             _FACTTRACE37,
             [_case(str(n), _fact_trace37(n)) for n in _FACTN37],
             ["Each call prints on the way in and again on the way out.",
              "`\"  \".repeat(depth)` indents by level (`String.repeat`, Java 11).",
              "The exits come in reverse order of the entries - last in, first out.",
              "That is the stack of frames, printed."],
             helpers=_FACTTRACE37),

        _p37("j37-pb-fib", "No frames at all", "Easy",
             "Print Fibonacci `F(n)` for `n` up to 90 with a loop - the naive recursion "
             "would take longer than the universe has left for `F(90)`.",
             "",
             "        int n = sc.nextInt();\n"
             "        long a = 0;\n"
             "        long b = 1;\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            long next = a + b;\n"
             "            a = b;\n"
             "            b = next;\n"
             "        }\n"
             "        System.out.println(a);",
             "        long a = 0;\n"
             "        long b = 1;\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            long next = a + b;\n"
             "            a = b;\n"
             "            b = next;\n"
             "        }\n"
             "        System.out.println(a);",
             [_case(str(n), _fib37(n)) for n in _FIBS37],
             ["Keep the last two values; step `n` times.",
              "`F(90)` needs a `long`.",
              "One frame, `n` steps - versus ~2^n calls for the naive version."]),

        _p37("j37-pb-dfs", "Depth-first, without recursion", "Medium",
             "Print the depth-first visiting order of a directed graph from a start node, "
             "using an explicit stack. Visit smaller neighbours first - so push them in "
             "DESCENDING order.",
             "",
             "        int n = sc.nextInt();\n"
             "        int m = sc.nextInt();\n"
             "        Map<Integer, List<Integer>> adj = new TreeMap<>();\n"
             "        for (int i = 0; i < m; i++) {\n"
             "            adj.computeIfAbsent(sc.nextInt(), k -> new ArrayList<>()).add(sc.nextInt());\n"
             "        }\n"
             "        int start = sc.nextInt();\n"
             "        Deque<Integer> stack = new ArrayDeque<>();\n"
             "        Set<Integer> seen = new HashSet<>();\n"
             "        List<Integer> order = new ArrayList<>();\n"
             "        stack.push(start);\n"
             "        while (!stack.isEmpty()) {\n"
             "            int v = stack.pop();\n"
             "            if (!seen.add(v)) {\n"
             "                continue;\n"
             "            }\n"
             "            order.add(v);\n"
             "            List<Integer> next = new ArrayList<>(adj.getOrDefault(v, List.of()));\n"
             "            next.sort(Comparator.reverseOrder());\n"
             "            for (int w : next) {\n"
             "                if (!seen.contains(w)) {\n"
             "                    stack.push(w);\n"
             "                }\n"
             "            }\n"
             "        }\n"
             "        StringBuilder out = new StringBuilder();\n"
             "        for (int v : order) {\n"
             "            if (out.length() > 0) out.append(' ');\n"
             "            out.append(v);\n"
             "        }\n"
             "        System.out.println(out);",
             "        stack.push(start);\n"
             "        while (!stack.isEmpty()) {\n"
             "            int v = stack.pop();\n"
             "            if (!seen.add(v)) {\n"
             "                continue;\n"
             "            }\n"
             "            order.add(v);\n"
             "            List<Integer> next = new ArrayList<>(adj.getOrDefault(v, List.of()));\n"
             "            next.sort(Comparator.reverseOrder());\n"
             "            for (int w : next) {\n"
             "                if (!seen.contains(w)) {\n"
             "                    stack.push(w);\n"
             "                }\n"
             "            }\n"
             "        }",
             [_graph_case37(adj, s) for (adj, s) in _GRAPHSB37],
             ["Pop a node; skip it if already seen; otherwise record it.",
              "Push its unseen neighbours - largest first, so the smallest is on top.",
              "`seen.add(v)` returning false means 'already visited'.",
              "A cycle cannot loop forever: its nodes are all seen the second time round."]),

        _p37("j37-pb-inorder", "In-order, without recursion", "Medium",
             "Insert the numbers into a binary search tree (duplicates ignored), then print "
             "an in-order traversal using an explicit stack.",
             """
class Node {
    final int value;
    Node left;
    Node right;

    Node(int value) {
        this.value = value;
    }
}
""",
             "        int n = sc.nextInt();\n"
             "        Node root = null;\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            root = insert(root, sc.nextInt());\n"
             "        }\n"
             "        List<Integer> out = new ArrayList<>();\n"
             "        Deque<Node> stack = new ArrayDeque<>();\n"
             "        Node cur = root;\n"
             "        while (cur != null || !stack.isEmpty()) {\n"
             "            while (cur != null) {\n"
             "                stack.push(cur);\n"
             "                cur = cur.left;\n"
             "            }\n"
             "            cur = stack.pop();\n"
             "            out.add(cur.value);\n"
             "            cur = cur.right;\n"
             "        }\n"
             "        System.out.println(out);",
             "        while (cur != null || !stack.isEmpty()) {\n"
             "            while (cur != null) {\n"
             "                stack.push(cur);\n"
             "                cur = cur.left;\n"
             "            }\n"
             "            cur = stack.pop();\n"
             "            out.add(cur.value);\n"
             "            cur = cur.right;\n"
             "        }",
             [_acase(xs, _jarr(sorted(set(xs)))) for xs in _BSTS37],
             ["Go left as far as possible, pushing every node on the way.",
              "Pop one: that is the next value in order.",
              "Then move to its right subtree and repeat.",
              "The stack holds exactly the nodes a recursive version would still have "
              "frames for."],
             helpers="    static Node insert(Node root, int v) {\n"
                     "        Node fresh = new Node(v);\n"
                     "        if (root == null) {\n"
                     "            return fresh;\n"
                     "        }\n"
                     "        Node cur = root;\n"
                     "        while (true) {\n"
                     "            if (v == cur.value) {\n"
                     "                return root;\n"
                     "            }\n"
                     "            Node next = v < cur.value ? cur.left : cur.right;\n"
                     "            if (next == null) {\n"
                     "                if (v < cur.value) {\n"
                     "                    cur.left = fresh;\n"
                     "                } else {\n"
                     "                    cur.right = fresh;\n"
                     "                }\n"
                     "                return root;\n"
                     "            }\n"
                     "            cur = next;\n"
                     "        }\n"
                     "    }"),

        _p37("j37-pb-hanoi", "Hanoi with hand-made frames", "Hard",
             "Solve the Towers of Hanoi for `n` discs (A to C) WITHOUT recursion, by "
             "simulating frames: each frame is `(n, from, to, via, stage)`. Stage 0 means "
             "'move n-1 out of the way', stage 1 'move disc n', stage 2 'move n-1 on top'. "
             "Print each move as `disc: from -> to`.",
             """
class Frame {
    final int n;
    final char from;
    final char to;
    final char via;
    int stage;

    Frame(int n, char from, char to, char via) {
        this.n = n;
        this.from = from;
        this.to = to;
        this.via = via;
    }
}
""",
             "        int n = sc.nextInt();\n"
             "        Deque<Frame> stack = new ArrayDeque<>();\n"
             "        stack.push(new Frame(n, 'A', 'C', 'B'));\n"
             "        while (!stack.isEmpty()) {\n"
             "            Frame f = stack.peek();\n"
             "            if (f.n == 0) {\n"
             "                stack.pop();\n"
             "            } else if (f.stage == 0) {\n"
             "                f.stage = 1;\n"
             "                stack.push(new Frame(f.n - 1, f.from, f.via, f.to));\n"
             "            } else if (f.stage == 1) {\n"
             "                System.out.println(f.n + \": \" + f.from + \" -> \" + f.to);\n"
             "                f.stage = 2;\n"
             "                stack.push(new Frame(f.n - 1, f.via, f.to, f.from));\n"
             "            } else {\n"
             "                stack.pop();\n"
             "            }\n"
             "        }",
             "        while (!stack.isEmpty()) {\n"
             "            Frame f = stack.peek();\n"
             "            if (f.n == 0) {\n"
             "                stack.pop();\n"
             "            } else if (f.stage == 0) {\n"
             "                f.stage = 1;\n"
             "                stack.push(new Frame(f.n - 1, f.from, f.via, f.to));\n"
             "            } else if (f.stage == 1) {\n"
             "                System.out.println(f.n + \": \" + f.from + \" -> \" + f.to);\n"
             "                f.stage = 2;\n"
             "                stack.push(new Frame(f.n - 1, f.via, f.to, f.from));\n"
             "            } else {\n"
             "                stack.pop();\n"
             "            }\n"
             "        }",
             [_case(str(n), _nl(*_hanoi37(n))) for n in _HANOI37],
             ["`peek`, don't `pop`: a frame stays until its stage 2 is done.",
              "Stage 0: set stage to 1, push the frame for 'move n-1 from `from` to `via`'.",
              "Stage 1: print the move of disc n, set stage 2, push 'move n-1 from `via` to "
              "`to`'.",
              "Stage 2: done - pop.",
              "`stage` is the frame's return address: where to resume when the 'call' it "
              "made comes back."]),
    ],
)


# --- Family C - identity -----------------------------------------------------------

_WORDPAIRS37 = ([("java", "java")], [("a", "b")], [("pool", "pool"), ("x", "y")], [("same", "same")],
                [("hi", "hi"), ("hi", "ho")])


def _wp_out37(rows):
    return _nl(*[f"{a} {b}: == false, equals {_jbool(a == b)}, interned == {_jbool(a == b)}"
                 for (a, b) in rows])


_BIGCOUNTS37 = ([("a", 5), ("b", 5)], [("a", 200), ("b", 200)], [("x", 127), ("y", 127)],
                [("p", 128), ("q", 128)], [("m", 300), ("n", 299)])


def _bigcount_out37(rows):
    return _nl(*[f"{a}={ca} {b}={cb} same {_jbool(ca == cb)}" for ((a, ca), (b, cb)) in
                 [(rows[0], rows[1])]])


_IDENT37 = (["a", "b", "a"], ["x"], ["dup", "dup", "dup"], ["p", "q", "r", "p"], ["one", "two", "one", "two"])

_NULLSUM37 = ([("a", "3"), ("b", "-"), ("c", "4")], [("x", "-")], [("p", "1"), ("q", "2")],
              [("m", "-"), ("n", "-"), ("o", "10")], [("z", "0")])


def _nullsum_out37(rows):
    total = sum(int(v) for (_k, v) in rows if v != "-")
    missing = sum(1 for (_k, v) in rows if v == "-")
    return _nl(f"total {total}", f"missing {missing}")


_MIXED37 = ([1, 2], [5], [127, 1000], [0, -1, 2], [42, 42])


def _mixed_out37(xs):
    # Each x is added as an Integer AND as a Long: two elements per distinct value.
    distinct_ints = len(set(xs))
    return _nl(f"mixed set size {2 * distinct_ints}", f"by value {distinct_ints}")


_P37_C = _jfam(
    "p37-identity", "Identity and boxing",
    "When `==` lies, when unboxing throws, and when a `Set<Number>` holds 1 twice.",
    """
```java
sc.next() == sc.next()                  // never true: two new String objects
a.intern() == b.intern()                // true iff a.equals(b)
Integer x = 200, y = 200;  x == y       // false - outside the cache
int n = map.get(k);                     // NPE if the value is null
Set<Number> s;  s.add(1); s.add(1L);    // TWO elements: Integer(1) and Long(1)
```

Identity (`==`) and equality (`equals`) coincide only where the JVM *chooses* to
share objects - pooled strings, cached small boxes, enum constants. Everywhere
else, `equals` is the question you meant.
""",
    [
        _p37("j37-pc-read", "Strings from the input", "Intro",
             "For each pair of words read from input, print whether they are `==`, whether "
             "they are `equals`, and whether their interned forms are `==`.",
             "",
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            String a = sc.next();\n"
             "            String b = sc.next();\n"
             "            System.out.println(a + \" \" + b + \": == \" + (a == b) + \", equals \" + a.equals(b)\n"
             "                    + \", interned == \" + (a.intern() == b.intern()));\n"
             "        }",
             "            System.out.println(a + \" \" + b + \": == \" + (a == b) + \", equals \" + a.equals(b)\n"
             "                    + \", interned == \" + (a.intern() == b.intern()));",
             [_rows37(rows, _wp_out37(rows)) for rows in _WORDPAIRS37],
             ["Every token `Scanner` returns is a new String object.",
              "So `==` is false even for the same word.",
              "`intern()` maps equal strings to one pooled object - so their `==` agrees "
              "with `equals`."]),

        _p37("j37-pc-counts", "Counts compared with `==`", "Easy",
             "Two words are added to a frequency map the given number of times each. Print "
             "both counts and whether they are the same - comparing the `Integer` values "
             "correctly, which `==` does not do above 127.",
             "",
             "        Map<String, Integer> counts = new HashMap<>();\n"
             "        String a = sc.next();\n"
             "        int ca = sc.nextInt();\n"
             "        String b = sc.next();\n"
             "        int cb = sc.nextInt();\n"
             "        for (int i = 0; i < ca; i++) {\n"
             "            counts.merge(a, 1, Integer::sum);\n"
             "        }\n"
             "        for (int i = 0; i < cb; i++) {\n"
             "            counts.merge(b, 1, Integer::sum);\n"
             "        }\n"
             "        boolean same = counts.get(a).equals(counts.get(b));\n"
             "        System.out.println(a + \"=\" + counts.get(a) + \" \" + b + \"=\" + counts.get(b) + \" same \" + same);",
             "        boolean same = counts.get(a).equals(counts.get(b));",
             [_case(f"{rows[0][0]} {rows[0][1]} {rows[1][0]} {rows[1][1]}", _bigcount_out37(rows))
              for rows in _BIGCOUNTS37],
             ["`counts.get(a) == counts.get(b)` compares two `Integer` objects.",
              "Up to 127 they come from the cache and `==` happens to work.",
              "At 128 and above they are separate objects: use `equals`.",
              "Tests that only use small numbers never catch this."]),

        _p37("j37-pc-identity", "An identity map of interned strings", "Medium",
             "Count distinct words two ways: with a `HashSet` (equality) and with an "
             "`IdentityHashMap` keyed by each word's INTERNED form (identity). Both must "
             "agree - interning turns equality into identity.",
             "",
             "        int n = sc.nextInt();\n"
             "        Set<String> byEquals = new HashSet<>();\n"
             "        Map<String, Boolean> byIdentity = new IdentityHashMap<>();\n"
             "        Map<String, Boolean> raw = new IdentityHashMap<>();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            String w = sc.next();\n"
             "            byEquals.add(w);\n"
             "            byIdentity.put(w.intern(), true);\n"
             "            raw.put(w, true);\n"
             "        }\n"
             "        System.out.println(\"equals \" + byEquals.size());\n"
             "        System.out.println(\"interned identity \" + byIdentity.size());\n"
             "        System.out.println(\"raw identity \" + raw.size());",
             "            byEquals.add(w);\n"
             "            byIdentity.put(w.intern(), true);\n"
             "            raw.put(w, true);",
             [_toks37(ws, _nl(f"equals {len(set(ws))}", f"interned identity {len(set(ws))}",
                              f"raw identity {len(ws)}")) for ws in _IDENT37],
             ["`IdentityHashMap` compares keys with `==`, not `equals`.",
              "Raw tokens are all different objects, so every one counts.",
              "Interned tokens are one object per distinct word.",
              "`IdentityHashMap` is rare in application code - but it is how serialisers "
              "track which objects they have already written."]),

        _p37("j37-pc-nulls", "Unboxing with care", "Medium",
             "A map from names to scores may hold `null` for 'no score yet' (`-` in the "
             "input). Total the real scores and count the missing ones - without unboxing a "
             "null.",
             "",
             "        int n = sc.nextInt();\n"
             "        Map<String, Integer> scores = new LinkedHashMap<>();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            String name = sc.next();\n"
             "            String v = sc.next();\n"
             "            scores.put(name, v.equals(\"-\") ? null : Integer.valueOf(v));\n"
             "        }\n"
             "        int total = 0;\n"
             "        int missing = 0;\n"
             "        for (Integer s : scores.values()) {\n"
             "            if (s == null) {\n"
             "                missing++;\n"
             "            } else {\n"
             "                total += s;\n"
             "            }\n"
             "        }\n"
             "        System.out.println(\"total \" + total);\n"
             "        System.out.println(\"missing \" + missing);",
             "        for (Integer s : scores.values()) {\n"
             "            if (s == null) {\n"
             "                missing++;\n"
             "            } else {\n"
             "                total += s;\n"
             "            }\n"
             "        }",
             [_rows37(rows, _nullsum_out37(rows)) for rows in _NULLSUM37],
             ["Iterate as `Integer`, not `int` - `for (int s : ...)` would unbox every "
              "element, nulls included.",
              "Check for null before the `+=`.",
              "A `HashMap` accepts null values; `Map.of` does not."]),

        _p37("j37-pc-mixed", "One, twice", "Hard",
             "Each number is added to a `Set<Number>` as an `Integer` AND as a `Long`. Print "
             "the set's size, then the number of distinct VALUES - normalising every element "
             "to a `long` in a second set.",
             "",
             "        int n = sc.nextInt();\n"
             "        Set<Number> mixed = new HashSet<>();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            int x = sc.nextInt();\n"
             "            mixed.add(x);\n"
             "            mixed.add((long) x);\n"
             "        }\n"
             "        Set<Long> values = new HashSet<>();\n"
             "        for (Number num : mixed) {\n"
             "            values.add(num.longValue());\n"
             "        }\n"
             "        System.out.println(\"mixed set size \" + mixed.size());\n"
             "        System.out.println(\"by value \" + values.size());",
             "        Set<Long> values = new HashSet<>();\n"
             "        for (Number num : mixed) {\n"
             "            values.add(num.longValue());\n"
             "        }",
             [_acase(xs, _mixed_out37(xs)) for xs in _MIXED37],
             ["`mixed.add(x)` boxes to `Integer`; `mixed.add((long) x)` to `Long`.",
              "`Integer.equals(Long)` is false, so both stay in the set.",
              "`num.longValue()` normalises either kind.",
              "Mixing boxed types in one collection is almost always a bug."]),
    ],
)


# --- Family D - garbage collection, simulated ------------------------------------------


def _reach_case37(objs, edges, roots):
    live = _reach37(objs, edges, roots)
    return _case(_graph_stdin37(objs, edges, roots),
                 _nl(f"reachable {len(live)}", f"garbage {len(objs) - len(live)}"))


# Heap slots for mark-compact: (slots, live ids). "." is a free slot.
_HEAPS37 = ((["a", "b", ".", "c", "d"], ["a", "d"]),
            (["x", ".", ".", "y"], ["y"]),
            (["p", "q", "r"], ["p", "q", "r"]),
            ([".", "m", "n", "o", "."], []),
            (["s", "t", "u", "v", "w", "z"], ["t", "w", "z"]))


def _compact37(slots, live):
    out, nxt = [], 0
    for i, s in enumerate(slots):
        if s != "." and s in live:
            out.append(f"{s}: {i} -> {nxt}")
            nxt += 1
    heap = [s for s in slots if s != "." and s in live] + ["."] * (len(slots) - nxt)
    return _nl(*(out or ["nothing live"]), "heap " + " ".join(heap))


def _heap_case37(slots, live):
    stdin = "\n".join([str(len(slots)), " ".join(slots), str(len(live))
                       + ("" if not live else " " + " ".join(live))])
    return _case(stdin, _compact37(slots, live))


_ACCESS37 = ((2, ["a", "b", "a", "c", "b", "a"]), (3, ["x", "y", "z", "x", "y", "z"]),
             (1, ["p", "p", "q", "p"]), (2, ["m", "n", "o", "m", "n", "o"]), (3, ["a", "b", "c", "d", "a", "b"]))


def _lrustats37(cap, seq):
    order, hits, misses = [], 0, 0
    for k in seq:
        if k in order:
            hits += 1
            order.remove(k)
            order.append(k)
        else:
            misses += 1
            order.append(k)
            if len(order) > cap:
                order.pop(0)
    return _nl(f"hits {hits}", f"misses {misses}", f"final {_jarr(order)}")


_TRICOLOR37 = _GRAPHS37


def _tricolor37(objs, edges, roots):
    adj = {o: sorted(b for (a, b) in edges if a == o) for o in objs}
    grey = sorted(set(roots))
    black, seen = [], set(grey)
    steps = []
    while grey:
        o = grey.pop(0)
        for t in adj[o]:
            if t not in seen:
                seen.add(t)
                grey.append(t)
        black.append(o)
        steps.append(f"blacken {o}")
    white = sorted(o for o in objs if o not in seen)
    return _nl(*steps, f"white {_jarr(white)}")


_GENS37 = (
    [("a", 0), ("b", 3), ("c", 1)],
    [("x", 5)],
    [("p", 0), ("q", 0), ("r", 2), ("s", 4)],
    [("m", 1), ("n", 1)],
    [("t", 2), ("u", 0), ("v", 6)],
)


def _gens37(objs):
    young = [(n, life, 0) for (n, life) in objs]
    old, dead, lines, rnd = [], [], [], 0
    while young:
        rnd += 1
        survivors = []
        for (n, life, age) in young:
            if life <= age:
                dead.append(n)
            elif age + 1 >= 2:
                old.append(n)
            else:
                survivors.append((n, life, age + 1))
        young = survivors
        lines.append(f"minor gc {rnd}: young {_jarr([n for (n, _l, _a) in young])} old {_jarr(old)}")
    lines.append(f"collected young {_jarr(dead)}")
    return _nl(*lines)


_P37_D = _jfam(
    "p37-gc", "Garbage collection, simulated",
    "Reachability, mark-compact, tri-colour marking, LRU statistics and a "
    "generational heap - the algorithms, run on data you can see.",
    """
Real collections cannot be watched deterministically, so these drills run the
collectors' *algorithms* on object graphs read from the input - which is also
how you would be asked about them in an interview.

* **Mark-compact** slides every live object to the start of the heap, recording a
  *forwarding address* for each, so free space is one contiguous block and
  allocation is just bumping a pointer.
* **Tri-colour marking** is how concurrent collectors track progress: *white*
  (not yet seen), *grey* (seen, references not yet scanned), *black* (done).
  Whatever is still white at the end is garbage.
* **Generational** collection promotes objects that survive a couple of minor
  collections to the old generation, where they are left alone.
""",
    [
        _p37("j37-pd-reach", "How much is garbage?", "Intro",
             "Read an object graph and its roots, and print how many objects are reachable "
             "and how many are garbage.",
             "",
             _READGRAPH37
             + "        Set<String> seen = new HashSet<>();\n"
               "        Deque<String> work = new ArrayDeque<>(roots);\n"
               "        while (!work.isEmpty()) {\n"
               "            String o = work.pop();\n"
               "            if (seen.add(o)) {\n"
               "                work.addAll(refs.get(o));\n"
               "            }\n"
               "        }\n"
               "        System.out.println(\"reachable \" + seen.size());\n"
               "        System.out.println(\"garbage \" + (objects.size() - seen.size()));",
             "        Set<String> seen = new HashSet<>();\n"
             "        Deque<String> work = new ArrayDeque<>(roots);\n"
             "        while (!work.isEmpty()) {\n"
             "            String o = work.pop();\n"
             "            if (seen.add(o)) {\n"
             "                work.addAll(refs.get(o));\n"
             "            }\n"
             "        }",
             [_reach_case37(*g) for g in _GRAPHS37],
             ["A work queue starting from the roots.",
              "`seen.add(o)` is false for an object already visited - so cycles end.",
              "Garbage is everything not reached."]),

        _p37("j37-pd-compact", "Mark-compact", "Medium",
             "The heap is a row of slots (`.` is free). Given the live objects, slide each "
             "live one, in heap order, to the lowest free address: print `id: old -> new` "
             "for each, then the compacted heap.",
             "",
             "        int n = sc.nextInt();\n"
             "        String[] heap = new String[n];\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            heap[i] = sc.next();\n"
             "        }\n"
             "        int k = sc.nextInt();\n"
             "        Set<String> live = new HashSet<>();\n"
             "        for (int i = 0; i < k; i++) {\n"
             "            live.add(sc.next());\n"
             "        }\n"
             "        String[] compacted = new String[n];\n"
             "        Arrays.fill(compacted, \".\");\n"
             "        int next = 0;\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            if (!heap[i].equals(\".\") && live.contains(heap[i])) {\n"
             "                System.out.println(heap[i] + \": \" + i + \" -> \" + next);\n"
             "                compacted[next++] = heap[i];\n"
             "            }\n"
             "        }\n"
             "        if (next == 0) {\n"
             "            System.out.println(\"nothing live\");\n"
             "        }\n"
             "        System.out.println(\"heap \" + String.join(\" \", compacted));",
             "        int next = 0;\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            if (!heap[i].equals(\".\") && live.contains(heap[i])) {\n"
             "                System.out.println(heap[i] + \": \" + i + \" -> \" + next);\n"
             "                compacted[next++] = heap[i];\n"
             "            }\n"
             "        }",
             [_heap_case37(s, l) for (s, l) in _HEAPS37],
             ["Keep a 'next free address' that starts at 0.",
              "Walk the heap in order; each live object moves to `next`, which then "
              "advances.",
              "Dead objects and free slots are simply skipped.",
              "Order is preserved - which keeps objects allocated together close together."]),

        _p37("j37-pd-lru", "Hits and misses", "Medium",
             "Run an access sequence through an LRU cache of the given capacity (a "
             "`LinkedHashMap` in access order with `removeEldestEntry`). Print the hits, the "
             "misses and the final contents.",
             "",
             "        int capacity = sc.nextInt();\n"
             "        int n = sc.nextInt();\n"
             "        Map<String, Boolean> cache = new LinkedHashMap<>(16, 0.75f, true) {\n"
             "            @Override\n"
             "            protected boolean removeEldestEntry(Map.Entry<String, Boolean> eldest) {\n"
             "                return size() > capacity;\n"
             "            }\n"
             "        };\n"
             "        int hits = 0;\n"
             "        int misses = 0;\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            String key = sc.next();\n"
             "            if (cache.get(key) != null) {\n"
             "                hits++;\n"
             "            } else {\n"
             "                misses++;\n"
             "                cache.put(key, true);\n"
             "            }\n"
             "        }\n"
             "        System.out.println(\"hits \" + hits);\n"
             "        System.out.println(\"misses \" + misses);\n"
             "        System.out.println(\"final \" + cache.keySet());",
             "        Map<String, Boolean> cache = new LinkedHashMap<>(16, 0.75f, true) {\n"
             "            @Override\n"
             "            protected boolean removeEldestEntry(Map.Entry<String, Boolean> eldest) {\n"
             "                return size() > capacity;\n"
             "            }\n"
             "        };",
             [_case(f"{c}\n{len(seq)}\n{' '.join(seq)}", _lrustats37(c, seq)) for (c, seq) in _ACCESS37],
             ["`new LinkedHashMap<>(16, 0.75f, true)` - access order.",
              "Override `removeEldestEntry` in an anonymous subclass.",
              "`get` on a present key moves it to the most-recent end - that is the 'used' "
              "in least-recently-used.",
              "A cyclic pattern one larger than the cache misses every time - LRU's known "
              "weakness."]),

        _p37("j37-pd-tricolor", "Tri-colour marking", "Medium",
             "Start with the roots grey (sorted). Repeatedly take the FIRST grey object, "
             "turn each of its white referents grey (in sorted order, appended), and turn it "
             "black - printing `blacken x`. Finally print the objects still white.",
             "",
             _READGRAPH37
             + "        for (List<String> targets : refs.values()) {\n"
               "            Collections.sort(targets);\n"
               "        }\n"
               "        Deque<String> grey = new ArrayDeque<>(new TreeSet<>(roots));\n"
               "        Set<String> seen = new HashSet<>(grey);\n"
               "        while (!grey.isEmpty()) {\n"
               "            String o = grey.pollFirst();\n"
               "            for (String t : refs.get(o)) {\n"
               "                if (seen.add(t)) {\n"
               "                    grey.addLast(t);\n"
               "                }\n"
               "            }\n"
               "            System.out.println(\"blacken \" + o);\n"
               "        }\n"
               "        List<String> white = new ArrayList<>();\n"
               "        for (String o : objects) {\n"
               "            if (!seen.contains(o)) {\n"
               "                white.add(o);\n"
               "            }\n"
               "        }\n"
               "        Collections.sort(white);\n"
               "        System.out.println(\"white \" + white);",
             "        while (!grey.isEmpty()) {\n"
             "            String o = grey.pollFirst();\n"
             "            for (String t : refs.get(o)) {\n"
             "                if (seen.add(t)) {\n"
             "                    grey.addLast(t);\n"
             "                }\n"
             "            }\n"
             "            System.out.println(\"blacken \" + o);\n"
             "        }",
             [_case(_graph_stdin37(*g), _tricolor37(*g)) for g in _TRICOLOR37],
             ["Grey is a queue: take from the front, add to the back.",
              "`seen` holds everything grey or black - anything not in it is white.",
              "An object turns black once its references have all been scanned.",
              "Concurrent collectors keep exactly this invariant while the program keeps "
              "running: no black object may point at a white one."]),

        _p37("j37-pd-gens", "A generational heap", "Hard",
             "Objects are allocated young with an age of 0 and a lifespan (the number of "
             "minor collections they will survive). At each minor GC, a young object whose "
             "age has reached its lifespan dies; one that has now survived two collections "
             "is PROMOTED to old; the rest age by one. Print the generations after each GC "
             "until the young generation is empty, then the objects collected young.",
             "",
             "        int n = sc.nextInt();\n"
             "        List<String> names = new ArrayList<>();\n"
             "        List<int[]> young = new ArrayList<>();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            names.add(sc.next());\n"
             "            young.add(new int[] {i, sc.nextInt(), 0});\n"
             "        }\n"
             "        List<String> old = new ArrayList<>();\n"
             "        List<String> dead = new ArrayList<>();\n"
             "        int round = 0;\n"
             "        while (!young.isEmpty()) {\n"
             "            round++;\n"
             "            List<int[]> survivors = new ArrayList<>();\n"
             "            for (int[] obj : young) {\n"
             "                if (obj[1] <= obj[2]) {\n"
             "                    dead.add(names.get(obj[0]));\n"
             "                } else if (obj[2] + 1 >= 2) {\n"
             "                    old.add(names.get(obj[0]));\n"
             "                } else {\n"
             "                    survivors.add(new int[] {obj[0], obj[1], obj[2] + 1});\n"
             "                }\n"
             "            }\n"
             "            young = survivors;\n"
             "            List<String> youngNames = new ArrayList<>();\n"
             "            for (int[] obj : young) {\n"
             "                youngNames.add(names.get(obj[0]));\n"
             "            }\n"
             "            System.out.println(\"minor gc \" + round + \": young \" + youngNames + \" old \" + old);\n"
             "        }\n"
             "        System.out.println(\"collected young \" + dead);",
             "            List<int[]> survivors = new ArrayList<>();\n"
             "            for (int[] obj : young) {\n"
             "                if (obj[1] <= obj[2]) {\n"
             "                    dead.add(names.get(obj[0]));\n"
             "                } else if (obj[2] + 1 >= 2) {\n"
             "                    old.add(names.get(obj[0]));\n"
             "                } else {\n"
             "                    survivors.add(new int[] {obj[0], obj[1], obj[2] + 1});\n"
             "                }\n"
             "            }\n"
             "            young = survivors;",
             [_rows37(o, _gens37(o)) for o in _GENS37],
             ["Each young object is `{index, lifespan, age}`.",
              "Dies if `lifespan <= age`; otherwise it survives this collection.",
              "A survivor whose new age would reach 2 is promoted to old instead of aging.",
              "Promoted objects are never examined again by a minor GC - that is the saving.",
              "Most objects in real programs have lifespan 0: they die before their first "
              "collection, which is why young-generation GCs are so cheap."]),
    ],
)


# --- Family E - bytecode ---------------------------------------------------------------

_PFX37 = ("2 3 +", "5 1 2 + 4 * + 3 -", "7 2 /", "9", "4 2 3 * -")


def _pfx_eval37(e):
    return _postfix37(e)[1]


_MAXSTACK37 = (["push 1", "push 2", "add", "print"],
               ["push 1", "push 2", "push 3", "mul", "add", "print"],
               ["load 0", "dup", "mul", "store 1"],
               ["push 5", "print"],
               ["push 1", "push 2", "push 3", "push 4", "add", "add", "add", "dup", "print", "print"])
_EFFECT37 = {"push": 1, "load": 1, "dup": 1, "store": -1, "print": -1, "add": -1, "sub": -1,
             "mul": -1, "div": -1}


def _maxstack37(code):
    depth = best = 0
    for ins in code:
        depth += _EFFECT37[ins.split()[0]]
        best = max(best, depth)
    return best


_GCDPROGS37 = (
    # gcd(a, b) with a, b in locals 0 and 1: while b != 0: (a, b) = (b, a % b)
    ["push 48", "store 0", "push 18", "store 1",
     "load 1", "push 0", "jeq 16",
     "load 0", "load 1", "rem", "load 1", "store 0", "store 1", "jmp 4", "halt", "halt",
     "load 0", "print"],
    ["push 17", "store 0", "push 5", "store 1",
     "load 1", "push 0", "jeq 16",
     "load 0", "load 1", "rem", "load 1", "store 0", "store 1", "jmp 4", "halt", "halt",
     "load 0", "print"],
    # parity: print n % 2 for n = 7, then 10
    ["push 7", "push 2", "rem", "print", "push 10", "push 2", "rem", "print"],
    # jeq taken and not taken
    ["push 3", "push 3", "jeq 5", "push 111", "print", "push 222", "print"],
    ["push 100", "push 75", "rem", "print", "push 4", "push 5", "jeq 9", "push 9", "print"],
)

_VM2_37 = (
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
    "                case \"load\" -> stack.push(locals[Integer.parseInt(ins[1])]);\n"
    "                case \"store\" -> locals[Integer.parseInt(ins[1])] = stack.pop();\n"
    "                case \"jmp\" -> pc = Integer.parseInt(ins[1]);\n"
    "                case \"print\" -> out.add(String.valueOf(stack.pop()));\n"
    "                case \"halt\" -> pc = code.size();\n"
    "                case \"rem\" -> {\n"
    "                    int b = stack.pop();\n"
    "                    int a = stack.pop();\n"
    "                    stack.push(a % b);\n"
    "                }\n"
    "                case \"jeq\" -> {\n"
    "                    int b = stack.pop();\n"
    "                    int a = stack.pop();\n"
    "                    if (a == b) {\n"
    "                        pc = Integer.parseInt(ins[1]);\n"
    "                    }\n"
    "                }\n"
    "                default -> throw new IllegalStateException(\"bad instruction \" + ins[0]);\n"
    "            }\n"
    "        }\n"
    "        return out;\n"
    "    }"
)
_VM2_REGION37 = (
    "                case \"rem\" -> {\n"
    "                    int b = stack.pop();\n"
    "                    int a = stack.pop();\n"
    "                    stack.push(a % b);\n"
    "                }\n"
    "                case \"jeq\" -> {\n"
    "                    int b = stack.pop();\n"
    "                    int a = stack.pop();\n"
    "                    if (a == b) {\n"
    "                        pc = Integer.parseInt(ins[1]);\n"
    "                    }\n"
    "                }"
)


def _vm2_37(code):
    stack, loc, out, pc = [], [0] * 8, [], 0
    while pc < len(code):
        ins = code[pc].split()
        pc += 1
        op = ins[0]
        if op == "push":
            stack.append(int(ins[1]))
        elif op == "load":
            stack.append(loc[int(ins[1])])
        elif op == "store":
            loc[int(ins[1])] = stack.pop()
        elif op == "jmp":
            pc = int(ins[1])
        elif op == "print":
            out.append(str(stack.pop()))
        elif op == "halt":
            pc = len(code)
        elif op == "rem":
            b, a = stack.pop(), stack.pop()
            stack.append(a - _jdiv(a, b) * b)
        elif op == "jeq":
            b, a = stack.pop(), stack.pop()
            if a == b:
                pc = int(ins[1])
    return out


_INFIX37 = ("1 + 2 * 3", "( 1 + 2 ) * 3", "8 - 3 - 2", "2 * ( 3 + 4 ) - 5", "7 / 2 + 1")

_SHUNT37 = (
    "    static List<String> toPostfix(String[] tokens) {\n"
    "        Map<String, Integer> prec = Map.of(\"+\", 1, \"-\", 1, \"*\", 2, \"/\", 2);\n"
    "        List<String> out = new ArrayList<>();\n"
    "        Deque<String> ops = new ArrayDeque<>();\n"
    "        for (String t : tokens) {\n"
    "            if (prec.containsKey(t)) {\n"
    "                while (!ops.isEmpty() && prec.containsKey(ops.peek())\n"
    "                        && prec.get(ops.peek()) >= prec.get(t)) {\n"
    "                    out.add(ops.pop());\n"
    "                }\n"
    "                ops.push(t);\n"
    "            } else if (t.equals(\"(\")) {\n"
    "                ops.push(t);\n"
    "            } else if (t.equals(\")\")) {\n"
    "                while (!ops.peek().equals(\"(\")) {\n"
    "                    out.add(ops.pop());\n"
    "                }\n"
    "                ops.pop();\n"
    "            } else {\n"
    "                out.add(t);\n"
    "            }\n"
    "        }\n"
    "        while (!ops.isEmpty()) {\n"
    "            out.add(ops.pop());\n"
    "        }\n"
    "        return out;\n"
    "    }"
)


def _shunt37(tokens):
    prec = {"+": 1, "-": 1, "*": 2, "/": 2}
    out, ops = [], []
    for t in tokens:
        if t in prec:
            while ops and ops[-1] in prec and prec[ops[-1]] >= prec[t]:
                out.append(ops.pop())
            ops.append(t)
        elif t == "(":
            ops.append(t)
        elif t == ")":
            while ops[-1] != "(":
                out.append(ops.pop())
            ops.pop()
        else:
            out.append(t)
    while ops:
        out.append(ops.pop())
    return out


def _infix_case37(src):
    pf = _shunt37(src.split())
    return _lcase(src, _nl(" ".join(pf), _pfx_eval37(" ".join(pf))))


_VARPROGS37 = (("a 3 b 4", "( a + b ) * a"), ("x 10", "x * x - 1"), ("p 2 q 5 r 1", "p * q + r * 7"),
               ("n 6", "n / 4"), ("u 1 v 2", "u - v - v"))

_COMPILEVARS37 = (
    "    static List<String[]> compile(String[] tokens, Map<String, Integer> slots) {\n"
    "        Map<String, String> ops = Map.of(\"+\", \"add\", \"-\", \"sub\", \"*\", \"mul\", \"/\", \"div\");\n"
    "        List<String[]> code = new ArrayList<>();\n"
    "        for (String t : toPostfix(tokens)) {\n"
    "            if (ops.containsKey(t)) {\n"
    "                code.add(new String[] {ops.get(t)});\n"
    "            } else if (slots.containsKey(t)) {\n"
    "                code.add(new String[] {\"load\", String.valueOf(slots.get(t))});\n"
    "            } else {\n"
    "                code.add(new String[] {\"push\", t});\n"
    "            }\n"
    "        }\n"
    "        code.add(new String[] {\"print\"});\n"
    "        return code;\n"
    "    }"
)


def _varprog_case37(assigns, expr):
    toks = assigns.split()
    names = toks[0::2]
    vals = [int(v) for v in toks[1::2]]
    slots = {n: i for i, n in enumerate(names)}
    pf = _shunt37(expr.split())
    listing = []
    for t in pf:
        if t in ("+", "-", "*", "/"):
            listing.append({"+": "add", "-": "sub", "*": "mul", "/": "div"}[t])
        elif t in slots:
            listing.append(f"load {slots[t]}")
        else:
            listing.append(f"push {t}")
    code = []
    for i, v in enumerate(vals):
        code += [f"push {v}", f"store {i}"]
    code += listing + ["print"]
    result = _vm37(code)[0]
    return _case(f"{len(names)} {assigns}\n{expr}\n", _nl("; ".join(listing + ["print"]), result))


_P37_E = _jfam(
    "p37-bytecode", "Bytecode and stack machines",
    "Evaluate postfix, size the operand stack, add instructions, and compile infix "
    "expressions the way javac does.",
    """
javac turns an infix expression into postfix instructions; the JVM runs them on
an operand stack. Every drill here is one piece of that pipeline:

* **postfix evaluation** - the stack machine itself;
* **max stack** - the class file records each method's maximum operand-stack
  depth (`max_stack`), which the verifier checks; it is computed exactly as here;
* **new instructions** - `rem` and `jeq`, like the JVM's `irem` and `if_icmpeq`;
* **the shunting-yard algorithm** - Dijkstra's infix-to-postfix conversion,
  respecting precedence, left associativity and parentheses;
* **compilation with variables** - names become `load` of a local slot.
""",
    [
        _p37("j37-pe-postfix", "A postfix calculator", "Intro",
             "Evaluate a postfix expression of integers and `+ - * /` (integer division) "
             "with an explicit stack.",
             "",
             "        String[] tokens = sc.nextLine().trim().split(\" \");\n"
             "        Deque<Integer> stack = new ArrayDeque<>();\n"
             "        for (String t : tokens) {\n"
             "            switch (t) {\n"
             "                case \"+\", \"-\", \"*\", \"/\" -> {\n"
             "                    int b = stack.pop();\n"
             "                    int a = stack.pop();\n"
             "                    stack.push(switch (t) {\n"
             "                        case \"+\" -> a + b;\n"
             "                        case \"-\" -> a - b;\n"
             "                        case \"*\" -> a * b;\n"
             "                        default -> a / b;\n"
             "                    });\n"
             "                }\n"
             "                default -> stack.push(Integer.parseInt(t));\n"
             "            }\n"
             "        }\n"
             "        System.out.println(stack.pop());",
             "        for (String t : tokens) {\n"
             "            switch (t) {\n"
             "                case \"+\", \"-\", \"*\", \"/\" -> {\n"
             "                    int b = stack.pop();\n"
             "                    int a = stack.pop();\n"
             "                    stack.push(switch (t) {\n"
             "                        case \"+\" -> a + b;\n"
             "                        case \"-\" -> a - b;\n"
             "                        case \"*\" -> a * b;\n"
             "                        default -> a / b;\n"
             "                    });\n"
             "                }\n"
             "                default -> stack.push(Integer.parseInt(t));\n"
             "            }\n"
             "        }",
             [_lcase(e, _pfx_eval37(e)) for e in _PFX37],
             ["A number is pushed; an operator pops two and pushes one.",
              "Pop `b` first - it is the right-hand operand.",
              "A switch expression can sit inside `push(...)`.",
              "At the end, exactly one value is left: the answer."]),

        _p37("j37-pe-maxstack", "Sizing the operand stack", "Easy",
             "Compute the maximum operand-stack depth a straight-line instruction list "
             "reaches: `push`, `load` and `dup` add one; `store`, `print` and every "
             "arithmetic instruction remove one (net).",
             "",
             "        int n = sc.nextInt();\n"
             "        sc.nextLine();\n"
             "        Map<String, Integer> effect = Map.of(\"push\", 1, \"load\", 1, \"dup\", 1, \"store\", -1,\n"
             "                \"print\", -1, \"add\", -1, \"sub\", -1, \"mul\", -1, \"div\", -1);\n"
             "        int depth = 0;\n"
             "        int max = 0;\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            String op = sc.nextLine().trim().split(\" \")[0];\n"
             "            depth += effect.get(op);\n"
             "            max = Math.max(max, depth);\n"
             "        }\n"
             "        System.out.println(\"max_stack \" + max);",
             "        int depth = 0;\n"
             "        int max = 0;\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            String op = sc.nextLine().trim().split(\" \")[0];\n"
             "            depth += effect.get(op);\n"
             "            max = Math.max(max, depth);\n"
             "        }",
             [_case("\n".join([str(len(c))] + c) + "\n", f"max_stack {_maxstack37(c)}") for c in _MAXSTACK37],
             ["Track the running depth and its maximum.",
              "Arithmetic pops two and pushes one: a net of -1.",
              "This is the number javac writes into every method's `max_stack`.",
              "For code with jumps, the verifier does the same along every path."]),

        _p37("j37-pe-jeq", "Two more instructions", "Medium",
             "Add `rem` (pop `b`, pop `a`, push `a % b`) and `jeq L` (pop `b`, pop `a`, jump "
             "to `L` if equal) to the machine. The programs compute greatest common divisors "
             "and remainders.",
             "",
             _READCODE37
             + "        for (String line : run(code)) {\n"
               "            System.out.println(line);\n"
               "        }",
             _VM2_REGION37,
             [_case("\n".join([str(len(p))] + p) + "\n", _nl(*_vm2_37(p))) for p in _GCDPROGS37],
             ["Both follow the operand-order rule: the first pop is `b`.",
              "`rem` is Java's `%`.",
              "`jeq` is `if_icmpeq`: compare, and overwrite `pc` only when equal.",
              "Euclid's algorithm is a loop: `while (b != 0) { t = a % b; a = b; b = t; }`."],
             helpers=_VM2_37),

        _p37("j37-pe-shunt", "Infix to postfix", "Medium",
             "Write `toPostfix(tokens)` - the shunting-yard algorithm for `+ - * /` and "
             "parentheses, all left-associative. `main` prints the postfix and its value.",
             "",
             "        String[] tokens = sc.nextLine().trim().split(\" \");\n"
             "        List<String> pf = toPostfix(tokens);\n"
             "        System.out.println(String.join(\" \", pf));\n"
             "        List<String[]> code = new ArrayList<>();\n"
             "        Map<String, String> ops = Map.of(\"+\", \"add\", \"-\", \"sub\", \"*\", \"mul\", \"/\", \"div\");\n"
             "        for (String t : pf) {\n"
             "            code.add(ops.containsKey(t) ? new String[] {ops.get(t)} : new String[] {\"push\", t});\n"
             "        }\n"
             "        code.add(new String[] {\"print\"});\n"
             "        System.out.println(run(code).get(0));",
             _SHUNT37,
             [_infix_case37(s) for s in _INFIX37],
             ["Numbers go straight to the output.",
              "Before pushing an operator, pop every operator of GREATER OR EQUAL "
              "precedence - `>=` is what makes `8 - 3 - 2` left-associative.",
              "`(` is pushed; `)` pops operators until the matching `(`, which is discarded.",
              "At the end, pop whatever operators remain.",
              "`Map.of` holds the precedences: `*` and `/` bind tighter."],
             helpers=_VM37 + "\n\n" + _SHUNT37),

        _p37("j37-pe-compile", "A compiler for expressions with variables", "Hard",
             "Write `compile(tokens, slots)`: turn an infix expression into instructions via "
             "`toPostfix` - operators become `add sub mul div`, a variable becomes `load "
             "<slot>`, a number `push N` - ending with `print`. `main` stores each variable "
             "in its slot first, then runs the compiled code.",
             "",
             "        int k = sc.nextInt();\n"
             "        Map<String, Integer> slots = new HashMap<>();\n"
             "        List<String[]> code = new ArrayList<>();\n"
             "        for (int i = 0; i < k; i++) {\n"
             "            String name = sc.next();\n"
             "            slots.put(name, i);\n"
             "            code.add(new String[] {\"push\", sc.next()});\n"
             "            code.add(new String[] {\"store\", String.valueOf(i)});\n"
             "        }\n"
             "        sc.nextLine();\n"
             "        List<String[]> body = compile(sc.nextLine().trim().split(\" \"), slots);\n"
             "        List<String> listing = new ArrayList<>();\n"
             "        for (String[] ins : body) {\n"
             "            listing.add(String.join(\" \", ins));\n"
             "        }\n"
             "        System.out.println(String.join(\"; \", listing));\n"
             "        code.addAll(body);\n"
             "        System.out.println(run(code).get(0));",
             _COMPILEVARS37,
             [_varprog_case37(a, e) for (a, e) in _VARPROGS37],
             ["Run the tokens through `toPostfix` first - it is given.",
              "Then one instruction per postfix token.",
              "A variable's slot comes from the `slots` map: `load 0`, `load 1`...",
              "End with `print`.",
              "This is javac in miniature: locals get slots, expressions become stack "
              "code."],
             helpers=_VM37 + "\n\n" + _SHUNT37 + "\n\n" + _COMPILEVARS37),
    ],
)


_PRACTICE[37] = [_P37_A, _P37_B, _P37_C, _P37_D, _P37_E]
