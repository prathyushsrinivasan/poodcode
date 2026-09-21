# -*- coding: utf-8 -*-
"""Compile every hand-authored Java fragment in the DSA curriculum.

    python tools/verify_snippets.py            # every stage
    python tools/verify_snippets.py patterns   # one stage, while authoring

WHY THIS EXISTS

The curriculum ships hundreds of Java fragments — every `_sk` skeleton and both
halves of every `_rw` rewrite. Unlike the problem bank, none of them is ever
executed: `verify_seeds` proves the *reference solutions* are accepted by the
judge, and says nothing about the code on the teaching pages. So a fragment can
carry a typo, a name that does not resolve, or a shape that is not valid Java at
all, and ship. One did: a rewrite mixed a `for` loop and a method declaration at
the same level, which reads fine to a human and cannot compile.

WHAT IT CAN AND CANNOT PROVE

The fragments are not programs. They reference `n`, `a`, `target` and friends
without declaring them, so each is compiled inside a wrapper that supplies the
missing names — and supplies a name *only* when the fragment does not declare it
itself, since otherwise most fragments fail on "already defined" and the check
quietly stops checking. Two wrappings are tried and a fragment passes if either
compiles:

  * as a **method body**, for fragments that are statements;
  * as **class members**, for fragments that are method declarations.

This cannot prove a fragment implements the right algorithm — that is what the
worked traces and the reference solutions are for. It proves the fragment
parses, that every identifier resolves, and that the types line up, which is
what hand-typed code actually gets wrong.

Fragments that deliberately elide a body (`{ ... }`, `/* … */`) are prose rather
than code and are skipped, and reported as skipped so the number stays honest.

COVERAGE TODAY

`foundations` and `patterns` pass completely, and CI gates on exactly those two
(see .github/workflows/ci.yml). Across the whole curriculum about 80 of 195
fragments still fail, almost all because they assume context the `AMBIENT`
table does not supply — a `Scanner`, a `TreeNode`, a `DSU`, an adjacency list
where the table has an `int[][]`. Those are gaps in this checker rather than
defects in the curriculum, but they have not been verified one by one, so the
gate does not claim them.

To widen it: run `python tools/verify_snippets.py <stage>`, add whatever the
failures actually need to `AMBIENT` / `AMBIENT_TYPES` (or fix the fragment, if
it turns out to be genuinely broken), and add the stage to the CI invocation.

PERFORMANCE

A clean run is two `javac` invocations and takes seconds. A run with failures
recompiles the leftovers one at a time, in parallel, to attribute each error —
about a minute for the whole curriculum. Serially that same path took over an
hour, which is slow enough that nobody would have run it.
"""
import json
from concurrent import futures
import os
import re
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
CURRICULUM = os.path.join(_HERE, "..", "src-tauri", "seeds", "dsa_curriculum.json")

# Name -> the declaration to emit when a fragment uses it without declaring it.
#
# Deliberately a fixed table rather than anything inferred: a fragment that
# reaches for a name not listed here is usually a fragment that should have
# declared it, and the resulting "cannot find symbol" is the report we want.
AMBIENT = {
    "n": "static int n = 10;",
    "m": "static int m = 5;",
    "k": "static int k = 2;",
    "target": "static int target = 7;",
    "W": "static int W = 100;",
    "MAX_VALUE": "static final int MAX_VALUE = 1000;",
    "best": "static long best = 0;",
    "count": "static long count = 0;",
    "sum": "static long sum = 0;",
    "a": "static int[] a = new int[10];",
    "b": "static int[] b = new int[10];",
    # `s` is a String in most fragments and a char[] in the in-place ones
    # (`s[l]`, `s.length`). Resolved by `_ambient_for`, which looks at how the
    # fragment indexes it — there is no one declaration that suits both.
    "s": 'static String s = "";',
    "t": 'static String t = "";',
    "first": 'static String first = "";',
    "out": "static int[] out = new int[20];",
    "part": 'static String part(int idx) { return ""; }',
    "parts": "static String[] parts = new String[0];",
    "words": "static String[] words = new String[0];",
    "list": "static List<Integer> list = new ArrayList<>();",
    "seenList": "static List<Integer> seenList = new ArrayList<>();",
    "set": "static Set<Integer> set = new HashSet<>();",
    "seen": "static Map<Long, Integer> seen = new HashMap<>();",
    "freq": "static Map<Character, Integer> freq = new HashMap<>();",
    "groups": "static Map<String, List<String>> groups = new HashMap<>();",
    "queries": "static int[][] queries = new int[0][0];",
    "updates": "static int[][] updates = new int[0][0];",
    "g": "static int[][] g = new int[10][10];",
    "r": "static int r = 5;",
    "c": "static int c = 5;",
    "prefix": "static long[] prefix = new long[11];",
    "pre": "static long[] pre = new long[11];",
    "diff": "static int[] diff = new int[11];",
    "dq": "static Deque<Integer> dq = new ArrayDeque<>();",
    "st": "static Deque<Integer> st = new ArrayDeque<>();",
    "sb": "static StringBuilder sb = new StringBuilder();",
    "rng": "static Random rng = new Random();",
    "slot": "static int[] slot = new int[4];",
    "lo": "static int lo = 0;",
    "hi": "static int hi = 0;",
    "l": "static int l = 0;",
    "i": "static int i = 0;",
    "j": "static int j = 0;",
    "input": "static int[] input = new int[10];",
    "sc": "static Scanner sc = new Scanner(System.in);",
    "keep": "static boolean keep(int x) { return x != 0; }",
    "valid": "static boolean valid() { return true; }",
    "shouldPop": "static boolean shouldPop(int top, int x) { return false; }",
    "nextUniform": "static long nextUniform(long cap) { return 0; }",
    "windowIsInvalid": "static boolean windowIsInvalid() { return false; }",
    "add": "static void add(int x) { }",
    "remove": "static void remove(int x) { }",
    "absorb": "static void absorb(int x) { }",
    "release": "static void release(int x) { }",
    "rows": "static int rows = 5;",
    "cols": "static int cols = 5;",
    "result": "static List<List<Integer>> result = new ArrayList<>();",
    "cur": "static List<Integer> cur = new ArrayList<>();",
    "memo": "static long[] memo = new long[64];",
    "preIdx": "static int preIdx = 0;",
    "powMod": "static long powMod(long base, long e, long mod) { return 1; }",
    "mulMod": "static long mulMod(long x, long y, long mod) { return 0; }",
    "apply": "static void apply(int node, int lo, int hi, long v) { }",
    "push": "static void push(int node, int lo, int hi) { }",
    "lazy": "static boolean[] lazy = new boolean[64];",
    "lazyVal": "static long[] lazyVal = new long[64];",
    "visited": "static boolean[] visited = new boolean[64];",
    "dist": "static long[] dist = new long[64];",
    "parent": "static int[] parent = new int[64];",
}

# Helper *types* the fragments assume, emitted as nested classes when a
# fragment names one. Kept apart from AMBIENT because these are declarations of
# a different kind, and because a class body cannot be a one-liner in a dict of
# field declarations.
AMBIENT_TYPES = {
    "TreeNode": (
        "    static class TreeNode { int val; TreeNode left, right;\n"
        "        TreeNode(int v) { val = v; } }"
    ),
    "ListNode": (
        "    static class ListNode { int val; ListNode next;\n"
        "        ListNode(int v) { val = v; } }"
    ),
    "Node": (
        "    static class Node { int val; Node[] next = new Node[26];\n"
        "        boolean end; Node child, prev; }"
    ),
    "DSU": (
        "    static class DSU { DSU(int n) { }\n"
        "        boolean union(int a, int b) { return true; }\n"
        "        int find(int a) { return a; } }"
    ),
}

# What a fragment declares for itself: `int x`, `long[] y`, `for (int i`,
# `Map<…> z`, `static void f(`. Loose on purpose — a false positive costs one
# ambient declaration, and the compiler then reports the truth.
_DECL = re.compile(
    r"\b(?:static\s+)?(?:final\s+)?"
    r"(?:int|long|double|boolean|char|String|var|Integer|Character|Long|"
    r"[A-Z]\w*(?:<[^>;=]*>)?)"
    r"(?:\s*\[\s*\]\s*|\s+)([a-zA-Z_]\w*)"
)

# Diagnostics the wrapper itself provokes. The guarded-body wrapping removes
# the two that used to matter (missing return / unreachable statement), so this
# is now empty -- kept as the place to put the next one rather than deleted,
# since success is judged by the class file and a stray note here would be a
# way to hide a real error.
_HARNESS_NOISE = re.compile(r"(?!)")  # matches nothing

# Skeletons that are deliberately MIXED FORM: a field or method declaration
# *and* the statements that use it, in one block.
#
# That is not valid Java anywhere — a method cannot be declared inside a method
# body, and a loop cannot sit at class level — so neither wrapping can accept
# them. It is still the right way to present these, because the point of the
# skeleton is the declaration together with its use; splitting them into two
# code blocks would teach worse.
#
# Listed explicitly rather than detected, so the exemption is a decision with a
# name against it and a *new* fragment that fails still fails. If one of these
# is ever rewritten into a single form, delete its line and the checker will
# confirm it.
MIXED_FORM = {
    ("recursion", "skeleton: Memoised recursion"),
    ("math-number-theory", "skeleton: nCr modulo a prime"),
    ("simulation-and-matrix", "skeleton: Neighbour scan"),
    ("backtracking", "skeleton: Prune with a sorted input"),
    ("range-queries", "skeleton: Iterative segment tree (min)"),
    ("range-queries", "skeleton: Sparse table (static range min)"),
    ("advanced-bits", "skeleton: Gray code, both directions"),
    ("flows-and-matching", "skeleton: Kuhn's algorithm"),
    ("randomized", "skeleton: Weighted sampling"),
}


_IMPORT = re.compile(r"^\s*import\s+[\w.*]+\s*;\s*$", re.M)


def _split_imports(code):
    """Pull a fragment's own `import` lines out.

    A few skeletons open with `import java.util.*;` because they are shown as
    complete programs. Left in place they land inside the wrapper class, where
    an import is a syntax error — so they are hoisted to the top of the
    generated file and the rest of the fragment is wrapped as usual.
    """
    imports = _IMPORT.findall(code)
    return imports, _IMPORT.sub("", code).strip("\n")


def _is_indexed(name, code):
    """Whether the fragment uses `name` as an array rather than a scalar.

    Several short names are a scalar in one skeleton and an array in another
    (`a` is the input array almost everywhere and three separate ints in "max
    of three"; `s` is a String usually and a char[] in the in-place ones).
    There is no single declaration that suits both, so the wrapper reads how
    the fragment actually uses it.

    Indexing is not the only array usage, and assuming it was made this *worse*
    than a fixed guess — `for (int x : a)`, `Arrays.sort(a)` and `a.clone()`
    all use an array without a single `[`. Everything array-shaped is listed
    here, and the scalar reading is the fallback.
    """
    n = re.escape(name)
    return bool(
        re.search(r"\b%s\s*\[" % n, code)                    # a[i]
        or re.search(r"\b%s\s*\.\s*length\b(?!\s*\()" % n, code)  # a.length
        or re.search(r":\s*%s\s*\)" % n, code)               # for (int x : a)
        or re.search(r"\b%s\s*\.\s*clone\s*\(" % n, code)    # a.clone()
        or re.search(r"\b(?:Arrays|System)\.\w+\([^)]*\b%s\b" % n, code)
    )


# Names whose declaration flips between a scalar and an array by usage.
_SCALAR_IF_NOT_INDEXED = {
    "a": ("static int a = 1;", "static int[] a = new int[10];"),
    "b": ("static int b = 2;", "static int[] b = new int[10];"),
    "s": ('static String s = "";', "static char[] s = new char[10];"),
}


# `g.get(u)` means the fragment treats the graph as an adjacency *list* rather
# than the `int[][]` most fragments use.
_G_IS_LIST = re.compile(r"\bg\s*\.\s*get\s*\(")


def _ambient_for(code):
    declared = set(_DECL.findall(code))
    lines = []
    for name, body in AMBIENT_TYPES.items():
        # A helper type is emitted whenever the fragment names it and does not
        # declare it, exactly like a variable.
        if re.search(r"\b%s\b" % re.escape(name), code) and (
            "class %s" % name not in code
        ):
            lines.append(body)
    for name, decl in AMBIENT.items():
        if name in declared or not re.search(r"\b%s\b" % re.escape(name), code):
            continue
        if name in _SCALAR_IF_NOT_INDEXED:
            scalar, indexed = _SCALAR_IF_NOT_INDEXED[name]
            decl = indexed if _is_indexed(name, code) else scalar
        elif name == "g" and _G_IS_LIST.search(code):
            decl = "static List<List<Integer>> g = new ArrayList<>();"
        lines.append("    " + decl)
    return "\n".join(lines)


def _as_body(name, code):
    """As a method body.

    Three details, each forced by a way this went wrong:

    * The return type is `Object`, so a fragment ending in `return true;` or
      `return -1;` type-checks by autoboxing.
    * The fragment sits inside `if (GUARD) { … }` with a non-constant `GUARD`,
      and the method ends `return null;`. Without the guard, a fragment that
      falls off the end fails with "missing return statement" — a *real* error,
      so javac writes no class file and the artefact check calls it broken; and
      a fragment ending in `return` would make an unguarded trailing
      `return null;` unreachable, which is also an error. The guard makes both
      shapes legal at once, because javac cannot prove the branch is taken.
    * The class is named per fragment, so a whole batch compiles in one `javac`
      call and every error still attributes to its own file.
    """
    imports, code = _split_imports(code)
    body = "\n".join("            " + line for line in code.rstrip().split("\n"))
    return (
        "import java.util.*;\n%s\n\npublic class %s {\n"
        "    static boolean GUARD = true;          // not a constant, on purpose\n"
        "%s\n\n"
        "    static Object body() {\n        if (GUARD) {\n%s\n        }\n"
        "        return null;\n    }\n\n"
        "    public static void main(String[] x) { }\n}\n"
        % ("\n".join(imports), name, _ambient_for(code), body)
    )


def _as_members(name, code):
    imports, code = _split_imports(code)
    members = "\n".join("    " + line for line in code.rstrip().split("\n"))
    return (
        "import java.util.*;\n%s\n\npublic class %s {\n%s\n\n%s\n\n"
        "    public static void main(String[] x) { }\n}\n"
        % ("\n".join(imports), name, _ambient_for(code), members)
    )


def _real_errors(stderr):
    blocks = re.split(r"(?=^\S.*?:\d+: error: )", stderr, flags=re.M)
    return [
        b.strip()
        for b in blocks
        if b.strip() and "error:" in b and not _HARNESS_NOISE.search(b)
    ]


def _javac(work, sources):
    """Run one `javac` over `sources` (class name -> source text).

    Returns `(stderr, compiled)` where `compiled` is the set of class names
    that produced a `.class` file. The directory is fresh for every call, so a
    class left by an earlier run cannot be mistaken for this one's output.
    """
    sub = tempfile.mkdtemp(prefix="batch", dir=work)
    paths = []
    for name, text in sources.items():
        path = os.path.join(sub, name + ".java")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        paths.append(path)

    # javac stops reporting after 100 errors by default, which would truncate a
    # batch this size the moment a few fragments break.
    p = subprocess.run(
        ["javac", "-nowarn", "-Xmaxerrs", "10000", "-d", sub] + paths,
        capture_output=True, text=True,
    )
    compiled = {
        f[:-6] for f in os.listdir(sub) if f.endswith(".class") and "$" not in f
    }
    return p.stderr, compiled


# A top-level method or constructor declaration: `static long gcd(long a, …) {`
# at indent 0. Its presence means the fragment is a set of class members rather
# than a sequence of statements.
_MEMBER_DECL = re.compile(
    r"^(?:(?:public|private|protected|static|final|abstract)\s+)*"
    r"[A-Za-z_][\w<>\[\], .]*\s+\w+\s*\([^;{)]*\)\s*\{",
    re.M,
)


def _wrap(name, code):
    """The right wrapping for this fragment, chosen by shape.

    Trying the body wrapping first and the members wrapping on failure is the
    obvious approach and destroys the batching: a method-declaration fragment
    is a *parse* error as a body, javac abandons the whole batch on the first
    of those, and every fragment then has to be compiled individually. Choosing
    up front keeps the common case to one `javac` call.
    """
    return (_as_members(name, code) if _MEMBER_DECL.search(code)
            else _as_body(name, code))


def _compile_all(work, kept):
    """Compile every fragment, fast when they all pass.

    `kept` is a list of `(class name, unit key, description, code)`.

    One `javac` per fragment is the obvious implementation and takes minutes —
    a couple of hundred fragments, each dominated by a JVM start. So the whole
    set goes through javac at once. But **javac abandons the entire batch when
    any file fails to parse**, emitting no class files even for the good ones,
    so a batch result cannot attribute a failure; reading "no error mentioned
    my file" as success under-reported by a factor of three when this was first
    written.

    Hence: one batch call, and only if it did not compile everything, a
    per-file pass over the leftovers to find out which are actually broken —
    trying *both* wrappings there, in case the shape heuristic guessed wrong.
    The slow path costs about a second per leftover and is only reached when
    something is already wrong.

    Returns a list of `(unit key, description, errors)` for the failures.
    """
    if not kept:
        return []

    _, compiled = _javac(work, {n: _wrap(n, c) for n, _, _, c in kept})
    leftovers = [f for f in kept if f[0] not in compiled]
    if not leftovers:
        return []

    def check_one(frag):
        name, key, what, code = frag
        err_body, ok = _javac(work, {name: _as_body(name, code)})
        if name in ok:
            return None
        err_mem, ok = _javac(work, {name + "M": _as_members(name + "M", code)})
        if (name + "M") in ok:
            return None
        # Report whichever wrapping got closer, by error volume.
        a = "\n".join(_real_errors(err_body))
        b = "\n".join(_real_errors(err_mem))
        return (key, what, (a if len(a) <= len(b) else b)
                or "(javac produced no class file and no diagnostic)")

    # In parallel: each call is an independent javac process on its own
    # directory, and serially this path took over an hour on a curriculum with
    # a hundred broken fragments — slow enough that nobody would run it.
    with futures.ThreadPoolExecutor(max_workers=min(16, (os.cpu_count() or 4) * 2)) as pool:
        return [r for r in pool.map(check_one, leftovers) if r]


def _fragments(cur, only=None):
    for stage in cur["stages"]:
        if only and stage["key"] not in only:
            continue
        for u in stage["units"]:
            for sk in u.get("skeletons", []):
                yield u["key"], "skeleton: " + sk["name"], sk["code"]
            for rw in u.get("rewrites", []):
                yield u["key"], "rewrite: %s (before)" % rw["title"], rw["slow"]
                yield u["key"], "rewrite: %s (after)" % rw["title"], rw["fast"]


def main(argv):
    only = set(argv[1:]) or None
    with open(CURRICULUM, encoding="utf-8") as f:
        cur = json.load(f)

    work = tempfile.mkdtemp(prefix="dsa-frag")
    skipped = mixed = 0
    kept = []        # (class name, unit key, description, code)
    seen_mixed = set()
    for i, (key, what, code) in enumerate(_fragments(cur, only)):
        if "..." in code or "…" in code:
            skipped += 1
            continue
        if (key, what) in MIXED_FORM:
            mixed += 1
            seen_mixed.add((key, what))
            continue
        kept.append(("Frag%04d" % i, key, what, code))
    checked = len(kept)

    bad = _compile_all(work, kept)

    # An exemption for a fragment that no longer exists is a stale exemption,
    # and a stale exemption is how an allowlist stops meaning anything. Only
    # checked on a full run, since a stage filter hides most of the list.
    stale = sorted(MIXED_FORM - seen_mixed) if not only else []

    scope = ("stage " + ", ".join(sorted(only))) if only else "every stage"
    # ASCII only: this goes to a console whose encoding is not ours to choose.
    print(
        "Java fragments (%s): %d checked, %d compiled, %d elided, "
        "%d mixed-form (exempt), %d FAILED"
        % (scope, checked, checked - len(bad), skipped, mixed, len(bad))
    )
    for key, what, err in bad:
        print("\n--- %s / %s" % (key, what))
        print(err[:900])
    for key, what in stale:
        print("\nstale MIXED_FORM entry: %s / %s no longer exists" % (key, what))
    return 1 if (bad or stale) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
