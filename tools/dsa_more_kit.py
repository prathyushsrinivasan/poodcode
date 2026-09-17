# -*- coding: utf-8 -*-
# ===========================================================================
# Authoring kit for the `dsa_more_*.py` problem batches.
#
# exec'd inside gen_seed.py's namespace before the batches, so DEFS,
# JAVA_STARTERS, PREREQS and EXTRA_REFS are already defined.
#
# WHY A KIT
#
# A stdin/stdout problem needs the same program written five times: a Python
# reference, a Java reference, and Python / Java / JavaScript starters, each
# with its own input-reading preamble. Hand-writing the preamble per problem is
# where the bugs were — a starter reading `n` as the first line when the input
# puts it second. So the preamble belongs to an input SHAPE, written once and
# tested once, and a problem supplies only its `solve` function.
#
# THE EXPECTED OUTPUT IS THE PYTHON REFERENCE, RUN
#
# The older bank files wrote each answer twice: a `sol_*` function to compute
# expected outputs, and a Python reference string for the judge. Two copies can
# disagree. Here the reference *program* is executed in-process to produce the
# expected output, so the thing the judge accepts and the thing the tests expect
# are the same code by construction. The Java reference is an independent second
# implementation, and `verify_seeds` proves the two agree on every case.
# ===========================================================================

import contextlib as _ctx
import io as _io
import sys as _sys

_PY_HEADER = (
    "import sys\n"
    "import heapq\n"
    "from bisect import bisect_left, bisect_right\n"
    "from collections import Counter, defaultdict, deque\n"
)

_JS_NUMS = "const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean);\n"
_JS_LINES = "const L = require('fs').readFileSync(0, 'utf8').split('\\n');\n"

# Each shape: how Python, JavaScript and Java read the input, and how `solve`
# is called. Java members are written at 4-space indent inside `class Main`.
_SHAPES = {
    # n, then n integers
    "arr": dict(
        py="d = sys.stdin.read().split()\nn = int(d[0])\na = list(map(int, d[1:1 + n]))\n",
        py_params="a",
        js=_JS_NUMS + "const n = Number(d[0]);\nconst a = d.slice(1, 1 + n).map(Number);\n",
        js_params="a",
        java="        int n = sc.nextInt();\n        int[] a = new int[n];\n"
             "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n",
        java_params="int[] a", java_args="a",
    ),
    # n, then n integers, then m, then m integers (either array may be empty)
    "arr2": dict(
        py="d = list(map(int, sys.stdin.read().split()))\nn = d[0]\na = d[1:1 + n]\nm = d[1 + n]\nb = d[2 + n:2 + n + m]\n",
        py_params="a, b",
        js=_JS_NUMS + "const n = Number(d[0]);\nconst a = d.slice(1, 1 + n).map(Number);\n"
           "const m = Number(d[1 + n]);\nconst b = d.slice(2 + n, 2 + n + m).map(Number);\n",
        js_params="a, b",
        java="        int n = sc.nextInt();\n        int[] a = new int[n];\n        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
             "        int m = sc.nextInt();\n        int[] b = new int[m];\n        for (int i = 0; i < m; i++) b[i] = sc.nextInt();\n",
        java_params="int[] a, int[] b", java_args="a, b",
    ),
    # "n k", then n integers
    "arr_k": dict(
        py="d = sys.stdin.read().split()\nn, k = int(d[0]), int(d[1])\na = list(map(int, d[2:2 + n]))\n",
        py_params="a, k",
        js=_JS_NUMS + "const n = Number(d[0]), k = Number(d[1]);\nconst a = d.slice(2, 2 + n).map(Number);\n",
        js_params="a, k",
        java="        int n = sc.nextInt();\n        long k = sc.nextLong();\n        int[] a = new int[n];\n"
             "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n",
        java_params="int[] a, long k", java_args="a, k",
    ),
    # a single token with no spaces
    "str": dict(
        py="s = sys.stdin.readline().strip()\n",
        py_params="s",
        js=_JS_LINES + "const s = L[0].trim();\n",
        js_params="s",
        java="        String s = sc.next();\n",
        java_params="String s", java_args="s",
    ),
    # a whole line, spaces allowed (may be surrounded by spaces)
    "line": dict(
        py="s = sys.stdin.readline().rstrip('\\n').rstrip('\\r')\n",
        py_params="s",
        js=_JS_LINES + "const s = L[0].replace(/\\r$/, '');\n",
        js_params="s",
        java="        String s = sc.hasNextLine() ? sc.nextLine() : \"\";\n",
        java_params="String s", java_args="s",
    ),
    # two tokens on two lines
    "str2": dict(
        py="L = sys.stdin.read().split('\\n')\ns = L[0].strip()\nt = L[1].strip()\n",
        py_params="s, t",
        js=_JS_LINES + "const s = L[0].trim(), t = L[1].trim();\n",
        js_params="s, t",
        java="        String s = sc.next();\n        String t = sc.next();\n",
        java_params="String s, String t", java_args="s, t",
    ),
    # a token, then an integer
    "str_k": dict(
        py="d = sys.stdin.read().split()\ns = d[0]\nk = int(d[1])\n",
        py_params="s, k",
        js=_JS_NUMS + "const s = d[0], k = Number(d[1]);\n",
        js_params="s, k",
        java="        String s = sc.next();\n        int k = sc.nextInt();\n",
        java_params="String s, int k", java_args="s, k",
    ),
    # a single integer
    "n": dict(
        py="n = int(sys.stdin.read().split()[0])\n",
        py_params="n",
        js=_JS_NUMS + "const n = Number(d[0]);\n",
        js_params="n",
        java="        long n = sc.nextLong();\n",
        java_params="long n", java_args="n",
    ),
    # two integers
    "two": dict(
        py="d = sys.stdin.read().split()\nx, y = int(d[0]), int(d[1])\n",
        py_params="x, y",
        js=_JS_NUMS + "const x = Number(d[0]), y = Number(d[1]);\n",
        js_params="x, y",
        java="        long x = sc.nextLong(), y = sc.nextLong();\n",
        java_params="long x, long y", java_args="x, y",
    ),
    # "r c", then r rows of characters with no spaces
    "grid": dict(
        py="d = sys.stdin.read().split()\nr, c = int(d[0]), int(d[1])\ng = [list(row) for row in d[2:2 + r]]\n",
        py_params="g",
        js=_JS_NUMS + "const r = Number(d[0]);\nconst g = d.slice(2, 2 + r).map(row => row.split(''));\n",
        js_params="g",
        java="        int r = sc.nextInt(), c = sc.nextInt();\n        char[][] g = new char[r][];\n"
             "        for (int i = 0; i < r; i++) g[i] = sc.next().toCharArray();\n",
        java_params="char[][] g", java_args="g",
    ),
    # "r c", then r rows of c integers
    "matrix": dict(
        py="d = list(map(int, sys.stdin.read().split()))\nr, c = d[0], d[1]\n"
           "m = [d[2 + i * c:2 + (i + 1) * c] for i in range(r)]\n",
        py_params="m",
        js=_JS_NUMS + "const r = Number(d[0]), c = Number(d[1]);\n"
           "const m = Array.from({ length: r }, (_, i) => d.slice(2 + i * c, 2 + (i + 1) * c).map(Number));\n",
        js_params="m",
        java="        int r = sc.nextInt(), c = sc.nextInt();\n        int[][] m = new int[r][c];\n"
             "        for (int i = 0; i < r; i++) for (int j = 0; j < c; j++) m[i][j] = sc.nextInt();\n",
        java_params="int[][] m", java_args="m",
    ),
    # "r c k", then r rows of c integers
    "matrix_k": dict(
        py="d = list(map(int, sys.stdin.read().split()))\nr, c, k = d[0], d[1], d[2]\n"
           "m = [d[3 + i * c:3 + (i + 1) * c] for i in range(r)]\n",
        py_params="m, k",
        js=_JS_NUMS + "const r = Number(d[0]), c = Number(d[1]), k = Number(d[2]);\n"
           "const m = Array.from({ length: r }, (_, i) => d.slice(3 + i * c, 3 + (i + 1) * c).map(Number));\n",
        js_params="m, k",
        java="        int r = sc.nextInt(), c = sc.nextInt(), k = sc.nextInt();\n        int[][] m = new int[r][c];\n"
             "        for (int i = 0; i < r; i++) for (int j = 0; j < c; j++) m[i][j] = sc.nextInt();\n",
        java_params="int[][] m, int k", java_args="m, k",
    ),
    # "n m", then m lines "u v"
    "graph": dict(
        py="d = list(map(int, sys.stdin.read().split()))\nn, m = d[0], d[1]\n"
           "edges = [(d[2 + 2 * i], d[3 + 2 * i]) for i in range(m)]\n",
        py_params="n, edges",
        js=_JS_NUMS + "const n = Number(d[0]), m = Number(d[1]);\n"
           "const edges = Array.from({ length: m }, (_, i) => [Number(d[2 + 2 * i]), Number(d[3 + 2 * i])]);\n",
        js_params="n, edges",
        java="        int n = sc.nextInt(), m = sc.nextInt();\n        int[][] edges = new int[m][2];\n"
             "        for (int i = 0; i < m; i++) { edges[i][0] = sc.nextInt(); edges[i][1] = sc.nextInt(); }\n",
        java_params="int n, int[][] edges", java_args="n, edges",
    ),
    # "n m", then m lines "u v w"
    "wgraph": dict(
        py="d = list(map(int, sys.stdin.read().split()))\nn, m = d[0], d[1]\n"
           "edges = [(d[2 + 3 * i], d[3 + 3 * i], d[4 + 3 * i]) for i in range(m)]\n",
        py_params="n, edges",
        js=_JS_NUMS + "const n = Number(d[0]), m = Number(d[1]);\n"
           "const edges = Array.from({ length: m }, (_, i) => [0, 1, 2].map(j => Number(d[2 + 3 * i + j])));\n",
        js_params="n, edges",
        java="        int n = sc.nextInt(), m = sc.nextInt();\n        int[][] edges = new int[m][3];\n"
             "        for (int i = 0; i < m; i++) for (int j = 0; j < 3; j++) edges[i][j] = sc.nextInt();\n",
        java_params="int n, int[][] edges", java_args="n, edges",
    ),
    # "n m k", then m lines "u v w"
    "wgraph_k": dict(
        py="d = list(map(int, sys.stdin.read().split()))\nn, m, k = d[0], d[1], d[2]\n"
           "edges = [(d[3 + 3 * i], d[4 + 3 * i], d[5 + 3 * i]) for i in range(m)]\n",
        py_params="n, edges, k",
        js=_JS_NUMS + "const n = Number(d[0]), m = Number(d[1]), k = Number(d[2]);\n"
           "const edges = Array.from({ length: m }, (_, i) => [0, 1, 2].map(j => Number(d[3 + 3 * i + j])));\n",
        js_params="n, edges, k",
        java="        int n = sc.nextInt(), m = sc.nextInt(), k = sc.nextInt();\n        int[][] edges = new int[m][3];\n"
             "        for (int i = 0; i < m; i++) for (int j = 0; j < 3; j++) edges[i][j] = sc.nextInt();\n",
        java_params="int n, int[][] edges, int k", java_args="n, edges, k",
    ),
    # a token, then m, then m lines "a b"
    "str_pairs": dict(
        py="d = sys.stdin.read().split()\ns = d[0]\nm = int(d[1])\n"
           "p = [(int(d[2 + 2 * i]), int(d[3 + 2 * i])) for i in range(m)]\n",
        py_params="s, p",
        js=_JS_NUMS + "const s = d[0], m = Number(d[1]);\n"
           "const p = Array.from({ length: m }, (_, i) => [Number(d[2 + 2 * i]), Number(d[3 + 2 * i])]);\n",
        js_params="s, p",
        java="        String s = sc.next();\n        int m = sc.nextInt();\n        int[][] p = new int[m][2];\n"
             "        for (int i = 0; i < m; i++) { p[i][0] = sc.nextInt(); p[i][1] = sc.nextInt(); }\n",
        java_params="String s, int[][] p", java_args="s, p",
    ),
    # n, then n lines "x y"
    "pairs": dict(
        py="d = list(map(int, sys.stdin.read().split()))\nn = d[0]\n"
           "p = [(d[1 + 2 * i], d[2 + 2 * i]) for i in range(n)]\n",
        py_params="p",
        js=_JS_NUMS + "const n = Number(d[0]);\n"
           "const p = Array.from({ length: n }, (_, i) => [Number(d[1 + 2 * i]), Number(d[2 + 2 * i])]);\n",
        js_params="p",
        java="        int n = sc.nextInt();\n        int[][] p = new int[n][2];\n"
             "        for (int i = 0; i < n; i++) { p[i][0] = sc.nextInt(); p[i][1] = sc.nextInt(); }\n",
        java_params="int[][] p", java_args="p",
    ),
    # "n k", then n lines "x y"
    "pairs_k": dict(
        py="d = list(map(int, sys.stdin.read().split()))\nn, k = d[0], d[1]\n"
           "p = [(d[2 + 2 * i], d[3 + 2 * i]) for i in range(n)]\n",
        py_params="p, k",
        js=_JS_NUMS + "const n = Number(d[0]), k = Number(d[1]);\n"
           "const p = Array.from({ length: n }, (_, i) => [Number(d[2 + 2 * i]), Number(d[3 + 2 * i])]);\n",
        js_params="p, k",
        java="        int n = sc.nextInt(), k = sc.nextInt();\n        int[][] p = new int[n][2];\n"
             "        for (int i = 0; i < n; i++) { p[i][0] = sc.nextInt(); p[i][1] = sc.nextInt(); }\n",
        java_params="int[][] p, int k", java_args="p, k",
    ),
    # n, then n lines "x y", then q, then q integers
    "pairs_q": dict(
        py="d = list(map(int, sys.stdin.read().split()))\nn = d[0]\n"
           "p = [(d[1 + 2 * i], d[2 + 2 * i]) for i in range(n)]\nq = d[1 + 2 * n]\nqs = d[2 + 2 * n:2 + 2 * n + q]\n",
        py_params="p, qs",
        js=_JS_NUMS + "const n = Number(d[0]);\n"
           "const p = Array.from({ length: n }, (_, i) => [Number(d[1 + 2 * i]), Number(d[2 + 2 * i])]);\n"
           "const q = Number(d[1 + 2 * n]);\nconst qs = d.slice(2 + 2 * n, 2 + 2 * n + q).map(Number);\n",
        js_params="p, qs",
        java="        int n = sc.nextInt();\n        int[][] p = new int[n][2];\n"
             "        for (int i = 0; i < n; i++) { p[i][0] = sc.nextInt(); p[i][1] = sc.nextInt(); }\n"
             "        int q = sc.nextInt();\n        int[] qs = new int[q];\n"
             "        for (int i = 0; i < q; i++) qs[i] = sc.nextInt();\n",
        java_params="int[][] p, int[] qs", java_args="p, qs",
    ),
    # n, then n integers, then q, then q lines "l r"
    "arr_q": dict(
        py="d = list(map(int, sys.stdin.read().split()))\nn = d[0]\na = d[1:1 + n]\nq = d[1 + n]\n"
           "queries = [(d[2 + n + 2 * i], d[3 + n + 2 * i]) for i in range(q)]\n",
        py_params="a, queries",
        js=_JS_NUMS + "const n = Number(d[0]);\nconst a = d.slice(1, 1 + n).map(Number);\nconst q = Number(d[1 + n]);\n"
           "const queries = Array.from({ length: q }, (_, i) => [Number(d[2 + n + 2 * i]), Number(d[3 + n + 2 * i])]);\n",
        js_params="a, queries",
        java="        int n = sc.nextInt();\n        int[] a = new int[n];\n"
             "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
             "        int q = sc.nextInt();\n        int[][] queries = new int[q][2];\n"
             "        for (int i = 0; i < q; i++) { queries[i][0] = sc.nextInt(); queries[i][1] = sc.nextInt(); }\n",
        java_params="int[] a, int[][] queries", java_args="a, queries",
    ),
    # q, then q lines, each an operation name followed by its arguments
    "ops": dict(
        py="L = sys.stdin.read().split('\\n')\nq = int(L[0])\nops = [L[1 + i].split() for i in range(q)]\n",
        py_params="ops",
        js=_JS_LINES + "const q = Number(L[0]);\nconst ops = L.slice(1, 1 + q).map(l => l.trim().split(/\\s+/));\n",
        js_params="ops",
        java="        int q = Integer.parseInt(sc.nextLine().trim());\n        String[][] ops = new String[q][];\n"
             "        for (int i = 0; i < q; i++) ops[i] = sc.nextLine().trim().split(\"\\\\s+\");\n",
        java_params="String[][] ops", java_args="ops",
    ),
    # a token, then d, then d tokens (d may be 0)
    "str_list": dict(
        py="d = sys.stdin.read().split()\ns = d[0]\nk = int(d[1])\nwords = d[2:2 + k]\n",
        py_params="s, words",
        js=_JS_NUMS + "const s = d[0], k = Number(d[1]);\nconst words = d.slice(2, 2 + k);\n",
        js_params="s, words",
        java="        String s = sc.next();\n        int k = sc.nextInt();\n        String[] words = new String[k];\n"
             "        for (int i = 0; i < k; i++) words[i] = sc.next();\n",
        java_params="String s, String[] words", java_args="s, words",
    ),
    # "n x y", then n integers
    "arr_xy": dict(
        py="d = sys.stdin.read().split()\nn, x, y = int(d[0]), int(d[1]), int(d[2])\na = list(map(int, d[3:3 + n]))\n",
        py_params="a, x, y",
        js=_JS_NUMS + "const n = Number(d[0]), x = Number(d[1]), y = Number(d[2]);\nconst a = d.slice(3, 3 + n).map(Number);\n",
        js_params="a, x, y",
        java="        int n = sc.nextInt();\n        long x = sc.nextLong(), y = sc.nextLong();\n        int[] a = new int[n];\n"
             "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n",
        java_params="int[] a, long x, long y", java_args="a, x, y",
    ),
    # "n q", then q lines "l r v"
    "updates": dict(
        py="d = list(map(int, sys.stdin.read().split()))\nn, q = d[0], d[1]\n"
           "ups = [(d[2 + 3 * i], d[3 + 3 * i], d[4 + 3 * i]) for i in range(q)]\n",
        py_params="n, ups",
        js=_JS_NUMS + "const n = Number(d[0]), q = Number(d[1]);\n"
           "const ups = Array.from({ length: q }, (_, i) => [0, 1, 2].map(j => Number(d[2 + 3 * i + j])));\n",
        js_params="n, ups",
        java="        int n = sc.nextInt(), q = sc.nextInt();\n        int[][] ups = new int[q][3];\n"
             "        for (int i = 0; i < q; i++) for (int j = 0; j < 3; j++) ups[i][j] = sc.nextInt();\n",
        java_params="int n, int[][] ups", java_args="n, ups",
    ),
}

# Binary trees arrive as one line in level order, "null" for a missing child —
# the same encoding the bank's function-harness tree problems already use.
_TREE_PY = '''from collections import deque

class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def build(tokens):
    if not tokens or tokens[0] == "null":
        return None
    root = TreeNode(int(tokens[0]))
    q = deque([root])
    i = 1
    while q and i < len(tokens):
        node = q.popleft()
        if i < len(tokens) and tokens[i] != "null":
            node.left = TreeNode(int(tokens[i]))
            q.append(node.left)
        i += 1
        if i < len(tokens) and tokens[i] != "null":
            node.right = TreeNode(int(tokens[i]))
            q.append(node.right)
        i += 1
    return root

L = sys.stdin.read().split('\\n')
root = build(L[0].split())
'''

_TREE_JS = '''class TreeNode { constructor(val) { this.val = val; this.left = null; this.right = null; } }
function build(tokens) {
  if (tokens.length === 0 || tokens[0] === 'null') return null;
  const root = new TreeNode(Number(tokens[0]));
  const q = [root];
  let i = 1, head = 0;
  while (head < q.length && i < tokens.length) {
    const node = q[head++];
    if (i < tokens.length && tokens[i] !== 'null') { node.left = new TreeNode(Number(tokens[i])); q.push(node.left); }
    i++;
    if (i < tokens.length && tokens[i] !== 'null') { node.right = new TreeNode(Number(tokens[i])); q.push(node.right); }
    i++;
  }
  return root;
}
const L = require('fs').readFileSync(0, 'utf8').split('\\n');
const root = build(L[0].trim().split(/\\s+/).filter(Boolean));
'''

_TREE_JAVA_MEMBERS = '''    static class TreeNode {
        int val;
        TreeNode left, right;
        TreeNode(int v) { val = v; }
    }

    static TreeNode build(String line) {
        String t = line.trim();
        if (t.isEmpty()) return null;
        String[] a = t.split("\\\\s+");
        if (a[0].equals("null")) return null;
        TreeNode root = new TreeNode(Integer.parseInt(a[0]));
        ArrayDeque<TreeNode> q = new ArrayDeque<>();
        q.add(root);
        int i = 1;
        while (!q.isEmpty() && i < a.length) {
            TreeNode node = q.poll();
            if (i < a.length && !a[i].equals("null")) { node.left = new TreeNode(Integer.parseInt(a[i])); q.add(node.left); }
            i++;
            if (i < a.length && !a[i].equals("null")) { node.right = new TreeNode(Integer.parseInt(a[i])); q.add(node.right); }
            i++;
        }
        return root;
    }
'''

_TREE_JAVA_READ = '        TreeNode root = build(sc.hasNextLine() ? sc.nextLine() : "");\n'

_SHAPES["tree"] = dict(
    py=_TREE_PY, py_params="root",
    js=_TREE_JS, js_params="root",
    java_members=_TREE_JAVA_MEMBERS, java=_TREE_JAVA_READ,
    java_params="TreeNode root", java_args="root",
)
# a tree line, then one integer
_SHAPES["tree_k"] = dict(
    py=_TREE_PY + "k = int(L[1])\n", py_params="root, k",
    js=_TREE_JS + "const k = Number(L[1]);\n", js_params="root, k",
    java_members=_TREE_JAVA_MEMBERS,
    java=_TREE_JAVA_READ + "        int k = Integer.parseInt(sc.nextLine().trim());\n",
    java_params="TreeNode root, int k", java_args="root, k",
)
# a tree line, then two integers
_SHAPES["tree_xy"] = dict(
    py=_TREE_PY + "x, y = map(int, L[1].split())\n", py_params="root, x, y",
    js=_TREE_JS + "const [x, y] = L[1].trim().split(/\\s+/).map(Number);\n", js_params="root, x, y",
    java_members=_TREE_JAVA_MEMBERS,
    java=_TREE_JAVA_READ + "        int x = sc.nextInt(), y = sc.nextInt();\n",
    java_params="TreeNode root, int x, int y", java_args="root, x, y",
)

# Singly linked lists arrive as `n` then the `n` values, and a list answer is
# printed as its values separated by spaces, or EMPTY — the program wraps
# `solve`'s returned head in `dump`, so a solution returns a list, not a string.
_LIST_PY = '''class ListNode:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

def build(vals):
    head = None
    for v in reversed(vals):
        head = ListNode(v, head)
    return head

def dump(head):
    out = []
    while head:
        out.append(str(head.val))
        head = head.next
    return " ".join(out) if out else "EMPTY"

d = sys.stdin.read().split()
n = int(d[0])
head = build([int(x) for x in d[1:1 + n]])
'''

_LIST_JS = '''class ListNode { constructor(val, next = null) { this.val = val; this.next = next; } }
function build(vals) { let head = null; for (let i = vals.length - 1; i >= 0; i--) head = new ListNode(vals[i], head); return head; }
function dump(head) { const out = []; for (let p = head; p; p = p.next) out.push(p.val); return out.length ? out.join(' ') : 'EMPTY'; }
const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);
const n = d[0];
const head = build(d.slice(1, 1 + n));
'''

_LIST_JAVA_MEMBERS = '''    static class ListNode {
        int val;
        ListNode next;
        ListNode(int val, ListNode next) { this.val = val; this.next = next; }
    }

    static ListNode build(int[] vals) {
        ListNode head = null;
        for (int i = vals.length - 1; i >= 0; i--) head = new ListNode(vals[i], head);
        return head;
    }

    static String dump(ListNode head) {
        StringBuilder sb = new StringBuilder();
        for (ListNode p = head; p != null; p = p.next) { if (sb.length() > 0) sb.append(' '); sb.append(p.val); }
        return sb.length() == 0 ? "EMPTY" : sb.toString();
    }
'''

_LIST_JAVA_READ = (
    "        int n = sc.nextInt();\n        int[] vals = new int[n];\n"
    "        for (int i = 0; i < n; i++) vals[i] = sc.nextInt();\n        ListNode head = build(vals);\n"
)

_SHAPES["list"] = dict(
    py=_LIST_PY, py_params="head",
    js=_LIST_JS, js_params="head",
    java_members=_LIST_JAVA_MEMBERS, java=_LIST_JAVA_READ,
    java_params="ListNode head", java_args="head", wrap="dump",
)
# a list, then one integer
_SHAPES["list_k"] = dict(
    py=_LIST_PY + "k = int(d[1 + n])\n", py_params="head, k",
    js=_LIST_JS + "const k = d[1 + n];\n", js_params="head, k",
    java_members=_LIST_JAVA_MEMBERS, java=_LIST_JAVA_READ + "        int k = sc.nextInt();\n",
    java_params="ListNode head, int k", java_args="head, k", wrap="dump",
)

# n, then n tokens
_SHAPES["words"] = dict(
    py="d = sys.stdin.read().split()\nn = int(d[0])\nwords = d[1:1 + n]\n",
    py_params="words",
    js=_JS_NUMS + "const n = Number(d[0]);\nconst words = d.slice(1, 1 + n);\n",
    js_params="words",
    java="        int n = sc.nextInt();\n        String[] words = new String[n];\n"
         "        for (int i = 0; i < n; i++) words[i] = sc.next();\n",
    java_params="String[] words", java_args="words",
)
# "r c", then r rows of characters, then k, then k tokens
_SHAPES["grid_words"] = dict(
    py="d = sys.stdin.read().split()\nr, c = int(d[0]), int(d[1])\ng = [list(row) for row in d[2:2 + r]]\n"
       "k = int(d[2 + r])\nwords = d[3 + r:3 + r + k]\n",
    py_params="g, words",
    js=_JS_NUMS + "const r = Number(d[0]);\nconst g = d.slice(2, 2 + r).map(row => row.split(''));\n"
       "const k = Number(d[2 + r]);\nconst words = d.slice(3 + r, 3 + r + k);\n",
    js_params="g, words",
    java="        int r = sc.nextInt(), c = sc.nextInt();\n        char[][] g = new char[r][];\n"
         "        for (int i = 0; i < r; i++) g[i] = sc.next().toCharArray();\n"
         "        int k = sc.nextInt();\n        String[] words = new String[k];\n"
         "        for (int i = 0; i < k; i++) words[i] = sc.next();\n",
    java_params="char[][] g, String[] words", java_args="g, words",
)
# "r c", then r rows of c integers, then q, then q lines "r1 c1 r2 c2"
_SHAPES["matrix_q"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nr, c = d[0], d[1]\n"
       "m = [d[2 + i * c:2 + (i + 1) * c] for i in range(r)]\nq = d[2 + r * c]\n"
       "queries = [tuple(d[3 + r * c + 4 * i:7 + r * c + 4 * i]) for i in range(q)]\n",
    py_params="m, queries",
    js=_JS_NUMS + "const r = Number(d[0]), c = Number(d[1]);\n"
       "const m = Array.from({ length: r }, (_, i) => d.slice(2 + i * c, 2 + (i + 1) * c).map(Number));\n"
       "const q = Number(d[2 + r * c]);\n"
       "const queries = Array.from({ length: q }, (_, i) => d.slice(3 + r * c + 4 * i, 7 + r * c + 4 * i).map(Number));\n",
    js_params="m, queries",
    java="        int r = sc.nextInt(), c = sc.nextInt();\n        int[][] m = new int[r][c];\n"
         "        for (int i = 0; i < r; i++) for (int j = 0; j < c; j++) m[i][j] = sc.nextInt();\n"
         "        int q = sc.nextInt();\n        int[][] queries = new int[q][4];\n"
         "        for (int i = 0; i < q; i++) for (int j = 0; j < 4; j++) queries[i][j] = sc.nextInt();\n",
    java_params="int[][] m, int[][] queries", java_args="m, queries",
)

_DEFAULTS = {
    "long": ("0", "0", "0"),
    "int": ("0", "0", "0"),
    "String": ('""', "''", "''"),
    "ListNode": ("null", "None", "null"),
}


def _call(sh, params):
    """`solve(...)`, wrapped in the shape's printer when the answer is a structure."""
    call = f"solve({params})"
    return f"{sh['wrap']}({call})" if sh.get("wrap") else call


def _program_py(shape, solve_src):
    sh = _SHAPES[shape]
    return (_PY_HEADER + "\n" + sh["py"] + "\n" + solve_src.strip("\n") + "\n\n"
            f"print({_call(sh, sh['py_params'])})\n")


def _program_java(shape, members):
    sh = _SHAPES[shape]
    return (
        "import java.util.*;\n\n"
        "public class Main {\n"
        + (sh["java_members"] + "\n" if sh.get("java_members") else "")
        + members.strip("\n") + "\n\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        + sh["java"] +
        f"        System.out.println({_call(sh, sh['java_args'])});\n"
        "    }\n"
        "}\n"
    )


def _run_py(program):
    """The Python reference as a `ref(stdin) -> stdout` function, run in-process."""
    compiled = compile(program, "<reference>", "exec")

    def run(inp):
        saved = _sys.stdin
        _sys.stdin = _io.StringIO(inp)
        buf = _io.StringIO()
        try:
            with _ctx.redirect_stdout(buf):
                exec(compiled, {"__name__": "__main__"})
        finally:
            _sys.stdin = saved
        return buf.getvalue().rstrip("\n")

    return run


def _p(slug, title, difficulty, *, topics, subtopics, companies, shape, ret, todo,
       description, constraints, hints, opt, editorial, py, java, examples, hidden,
       expl, prereqs):
    """Author one problem. `py` is the Python `def solve(...)`; `java` is the
    Java `static ... solve(...)` plus any helper members."""
    sh = _SHAPES[shape]
    java_default, py_default, js_default = _DEFAULTS[ret]
    py_program = _program_py(shape, py)
    cases = [("example", name, inp) for name, inp in examples] + \
            [("hidden", name, inp) for name, inp in hidden]
    DEFS.append(dict(
        slug=slug, title=title, difficulty=difficulty,
        topics=list(topics), subtopics=list(subtopics), companies=list(companies),
        description=description, constraints=constraints, hints=list(hints),
        opt=opt, editorial=editorial, ref=_run_py(py_program),
        starter_py=(
            "import sys\n\n" + sh["py"] + "\n"
            f"def solve({sh['py_params']}):\n    # TODO: {todo}\n    return {py_default}\n\n"
            f"print({_call(sh, sh['py_params'])})\n"
        ),
        starter_js=(
            sh["js"] + "\n"
            f"function solve({sh['js_params']}) {{\n  // TODO: {todo}\n  return {js_default};\n}}\n\n"
            f"console.log(String({_call(sh, sh['js_params'])}));\n"
        ),
        cases=cases,
        example_expl=list(expl),
    ))
    JAVA_STARTERS[slug] = _program_java(
        shape,
        f"    static {ret} solve({sh['java_params']}) {{\n"
        f"        // TODO: {todo}\n        return {java_default};\n    }}\n",
    )
    PREREQS[slug] = list(prereqs)
    EXTRA_REFS[slug] = {"python": py_program, "java": _program_java(shape, java)}
