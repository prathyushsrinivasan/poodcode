# -*- coding: utf-8 -*-
# ===========================================================================
# Authoring kit, part 3 — the input shapes the 107-topic roadmap needed.
#
# exec'd after tools/dsa_more_kit2.py, into the same namespace, so `_SHAPES`,
# `_JS_NUMS` and friends are defined. Each shape is written once for Python,
# JavaScript and Java, exactly like the originals.
#
# WHY THESE THREE
#
# The existing graph shapes all read "n m" and then m edges, which is right for
# a general graph and wrong for the two structures this round needs:
#
#   * A TREE always has exactly n - 1 edges, so `m` is not input, it is a
#     derivable fact. Making the author write it into every test case is an
#     invitation to write a case that is not a tree — and the reference would
#     then hang or crash at generation time rather than fail a lint.
#   * A BIPARTITE graph has two vertex sets, and "n" alone cannot say where the
#     split is. Encoding it as one number and a convention ("the first L are on
#     the left") pushes a silent invariant into every problem statement.
#
# So: the tree shapes take "n q" and read n - 1 edges; the bipartite shape takes
# both side sizes. In each the query block comes last, which keeps the arity
# check happy (see the gotcha in tools/dsa_more_kit2.py: a shape whose last
# block can be empty collapses the input to one line).
# ===========================================================================

# "n q", then n - 1 lines "u v" (an unrooted tree on 0 .. n-1), then q lines "a b".
_SHAPES["tree_q"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn, q = d[0], d[1]\n"
       "edges = [(d[2 + 2 * i], d[3 + 2 * i]) for i in range(n - 1)]\n"
       "_b = 2 + 2 * (n - 1)\n"
       "queries = [(d[_b + 2 * i], d[_b + 1 + 2 * i]) for i in range(q)]\n",
    py_params="n, edges, queries",
    js=_JS_NUMS + "const n = Number(d[0]), q = Number(d[1]);\n"
       "const edges = Array.from({ length: n - 1 }, (_, i) => [Number(d[2 + 2 * i]), Number(d[3 + 2 * i])]);\n"
       "const qb = 2 + 2 * (n - 1);\n"
       "const queries = Array.from({ length: q }, (_, i) => [Number(d[qb + 2 * i]), Number(d[qb + 1 + 2 * i])]);\n",
    js_params="n, edges, queries",
    java="        int n = sc.nextInt(), q = sc.nextInt();\n        int[][] edges = new int[n - 1][2];\n"
         "        for (int i = 0; i < n - 1; i++) { edges[i][0] = sc.nextInt(); edges[i][1] = sc.nextInt(); }\n"
         "        int[][] queries = new int[q][2];\n"
         "        for (int i = 0; i < q; i++) { queries[i][0] = sc.nextInt(); queries[i][1] = sc.nextInt(); }\n",
    java_params="int n, int[][] edges, int[][] queries", java_args="n, edges, queries",
)

# "n q", then n - 1 lines "u v w" (a weighted tree), then q lines "a b".
_SHAPES["wtree_q"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn, q = d[0], d[1]\n"
       "edges = [(d[2 + 3 * i], d[3 + 3 * i], d[4 + 3 * i]) for i in range(n - 1)]\n"
       "_b = 2 + 3 * (n - 1)\n"
       "queries = [(d[_b + 2 * i], d[_b + 1 + 2 * i]) for i in range(q)]\n",
    py_params="n, edges, queries",
    js=_JS_NUMS + "const n = Number(d[0]), q = Number(d[1]);\n"
       "const edges = Array.from({ length: n - 1 }, (_, i) => [0, 1, 2].map(j => Number(d[2 + 3 * i + j])));\n"
       "const qb = 2 + 3 * (n - 1);\n"
       "const queries = Array.from({ length: q }, (_, i) => [Number(d[qb + 2 * i]), Number(d[qb + 1 + 2 * i])]);\n",
    js_params="n, edges, queries",
    java="        int n = sc.nextInt(), q = sc.nextInt();\n        int[][] edges = new int[n - 1][3];\n"
         "        for (int i = 0; i < n - 1; i++) for (int j = 0; j < 3; j++) edges[i][j] = sc.nextInt();\n"
         "        int[][] queries = new int[q][2];\n"
         "        for (int i = 0; i < q; i++) { queries[i][0] = sc.nextInt(); queries[i][1] = sc.nextInt(); }\n",
    java_params="int n, int[][] edges, int[][] queries", java_args="n, edges, queries",
)

# n, then n integers that do NOT fit in 32 bits. The `arr` shape reads with
# `sc.nextInt()`, which silently refuses anything past 2·10⁹ — so a problem
# whose values reach 10¹⁸ needs its own shape rather than a cast.
_SHAPES["larr"] = dict(
    py="d = sys.stdin.read().split()\nn = int(d[0])\na = [int(t) for t in d[1:1 + n]]\n",
    py_params="a",
    js=_JS_NUMS + "const n = Number(d[0]);\nconst a = d.slice(1, 1 + n).map(BigInt);\n",
    js_params="a",
    java="        int n = sc.nextInt();\n        long[] a = new long[n];\n"
         "        for (int i = 0; i < n; i++) a[i] = sc.nextLong();\n",
    java_params="long[] a", java_args="a",
)

# "nl nr m", then m lines "u v" — u on the left side, v on the right side.
_SHAPES["bipartite"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nnl, nr, m = d[0], d[1], d[2]\n"
       "edges = [(d[3 + 2 * i], d[4 + 2 * i]) for i in range(m)]\n",
    py_params="nl, nr, edges",
    js=_JS_NUMS + "const nl = Number(d[0]), nr = Number(d[1]), m = Number(d[2]);\n"
       "const edges = Array.from({ length: m }, (_, i) => [Number(d[3 + 2 * i]), Number(d[4 + 2 * i])]);\n",
    js_params="nl, nr, edges",
    java="        int nl = sc.nextInt(), nr = sc.nextInt(), m = sc.nextInt();\n        int[][] edges = new int[m][2];\n"
         "        for (int i = 0; i < m; i++) { edges[i][0] = sc.nextInt(); edges[i][1] = sc.nextInt(); }\n",
    java_params="int nl, int nr, int[][] edges", java_args="nl, nr, edges",
)
