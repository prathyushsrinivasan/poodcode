# -*- coding: utf-8 -*-
# ===========================================================================
# Authoring kit, part 2 — the input shapes the syllabus roadmap needed.
#
# exec'd after tools/dsa_more_kit.py, into the same namespace, so `_SHAPES`,
# `_DEFAULTS`, `_TREE_PY` and friends are defined. Each shape below is written
# once for Python, JavaScript and Java, exactly like the originals.
#
# COPY PROBLEMS CHECK THAT THEY COPIED
#
# "Clone a graph" and "copy a list with random pointers" have an answer that
# looks identical to the input, so a solution that returns the original would
# print the right text. The printers here therefore also check identity: if any
# node reachable from the returned structure *is* an input node, they print
# `SHARED` instead of the structure. The judge still only compares text, but the
# text now depends on whether a copy was made.
# ===========================================================================

_DEFAULTS["Node"] = ("null", "None", "null")
_DEFAULTS["TreeNode"] = ("null", "None", "null")


# ---------------------------------------------------------------------------
# Level-order printer for problems whose answer is a tree. Trailing `null`s are
# trimmed, so the output is the same encoding the tree problems read.
# ---------------------------------------------------------------------------

_TREE_CLASS_PY = '''class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def level(root):
    if root is None:
        return "EMPTY"
    out, q, i = [], [root], 0
    while i < len(q):
        node = q[i]
        i += 1
        if node is None:
            out.append("null")
            continue
        out.append(str(node.val))
        q.append(node.left)
        q.append(node.right)
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)
'''

_TREE_CLASS_JS = '''class TreeNode { constructor(val) { this.val = val; this.left = null; this.right = null; } }
function level(root) {
  if (!root) return 'EMPTY';
  const out = [], q = [root];
  for (let i = 0; i < q.length; i++) {
    const node = q[i];
    if (!node) { out.push('null'); continue; }
    out.push(String(node.val));
    q.push(node.left, node.right);
  }
  while (out.length && out[out.length - 1] === 'null') out.pop();
  return out.join(' ');
}
'''

_TREE_CLASS_JAVA = '''    static class TreeNode {
        int val;
        TreeNode left, right;
        TreeNode(int v) { val = v; }
    }

    static String level(TreeNode root) {
        if (root == null) return "EMPTY";
        List<String> out = new ArrayList<>();
        LinkedList<TreeNode> q = new LinkedList<>();   // LinkedList: ArrayDeque rejects null
        q.add(root);
        while (!q.isEmpty()) {
            TreeNode node = q.poll();
            if (node == null) { out.add("null"); continue; }
            out.add(String.valueOf(node.val));
            q.add(node.left);
            q.add(node.right);
        }
        while (!out.isEmpty() && out.get(out.size() - 1).equals("null")) out.remove(out.size() - 1);
        return String.join(" ", out);
    }
'''

# One line of preorder tokens, `#` for a missing child. The answer is a tree.
_SHAPES["preorder_tokens"] = dict(
    py=_TREE_CLASS_PY + "\ntokens = sys.stdin.readline().split()\n",
    py_params="tokens",
    js=_TREE_CLASS_JS + "const tokens = require('fs').readFileSync(0, 'utf8').split('\\n')[0].trim().split(/\\s+/).filter(Boolean);\n",
    js_params="tokens",
    java_members=_TREE_CLASS_JAVA,
    java="        String line = sc.hasNextLine() ? sc.nextLine().trim() : \"\";\n"
         "        String[] tokens = line.isEmpty() ? new String[0] : line.split(\"\\\\s+\");\n",
    java_params="String[] tokens", java_args="tokens", wrap="level",
)

# n, then the preorder (n values), then the inorder (n values). The answer is a tree.
_SHAPES["two_orders"] = dict(
    py=_TREE_CLASS_PY + "\nd = list(map(int, sys.stdin.read().split()))\nn = d[0]\n"
       "pre = d[1:1 + n]\nino = d[1 + n:1 + 2 * n]\n",
    py_params="pre, ino",
    js=_TREE_CLASS_JS + _JS_NUMS + "const n = Number(d[0]);\n"
       "const pre = d.slice(1, 1 + n).map(Number);\nconst ino = d.slice(1 + n, 1 + 2 * n).map(Number);\n",
    js_params="pre, ino",
    java_members=_TREE_CLASS_JAVA,
    java="        int n = sc.nextInt();\n        int[] pre = new int[n], ino = new int[n];\n"
         "        for (int i = 0; i < n; i++) pre[i] = sc.nextInt();\n"
         "        for (int i = 0; i < n; i++) ino[i] = sc.nextInt();\n",
    java_params="int[] pre, int[] ino", java_args="pre, ino", wrap="level",
)

# A tree line, then q, then q lines each holding one operation name.
_SHAPES["tree_ops"] = dict(
    py=_TREE_PY + "q = int(L[1])\nops = [L[2 + i].strip() for i in range(q)]\n",
    py_params="root, ops",
    js=_TREE_JS + "const q = Number(L[1]);\nconst ops = L.slice(2, 2 + q).map(s => s.trim());\n",
    js_params="root, ops",
    java_members=_TREE_JAVA_MEMBERS,
    java=_TREE_JAVA_READ + "        int q = Integer.parseInt(sc.nextLine().trim());\n"
         "        String[] ops = new String[q];\n"
         "        for (int i = 0; i < q; i++) ops[i] = sc.nextLine().trim();\n",
    java_params="TreeNode root, String[] ops", java_args="root, ops",
)


# ---------------------------------------------------------------------------
# Clone graph: "n m", then m undirected edges "u v". `solve` receives node 0
# and returns its copy; the printer lists every node reachable from the copy.
# ---------------------------------------------------------------------------

_SHAPES["graph_nodes"] = dict(
    py='''class Node:
    def __init__(self, val):
        self.val = val
        self.neighbors = []

d = list(map(int, sys.stdin.read().split()))
n, m = d[0], d[1]
nodes = [Node(i) for i in range(n)]
for i in range(m):
    u, v = d[2 + 2 * i], d[3 + 2 * i]
    nodes[u].neighbors.append(nodes[v])
    nodes[v].neighbors.append(nodes[u])
node = nodes[0]

def dump(copy):
    if copy is None:
        return "NULL"
    originals = set(id(x) for x in nodes)
    seen = {id(copy)}
    order = [copy]
    i = 0
    while i < len(order):
        for nb in order[i].neighbors:
            if id(nb) not in seen:
                seen.add(id(nb))
                order.append(nb)
        i += 1
    if any(id(x) in originals for x in order):
        return "SHARED"
    order.sort(key=lambda x: x.val)
    return "\\n".join(str(x.val) + ":" + "".join(" " + str(v) for v in sorted(nb.val for nb in x.neighbors))
                     for x in order)
''',
    py_params="node",
    js='''class Node { constructor(val) { this.val = val; this.neighbors = []; } }
const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);
const n = d[0], m = d[1];
const nodes = Array.from({ length: n }, (_, i) => new Node(i));
for (let i = 0; i < m; i++) {
  const u = d[2 + 2 * i], v = d[3 + 2 * i];
  nodes[u].neighbors.push(nodes[v]);
  nodes[v].neighbors.push(nodes[u]);
}
const node = nodes[0];
function dump(copy) {
  if (!copy) return 'NULL';
  const originals = new Set(nodes);
  const seen = new Set([copy]), order = [copy];
  for (let i = 0; i < order.length; i++)
    for (const nb of order[i].neighbors) if (!seen.has(nb)) { seen.add(nb); order.push(nb); }
  if (order.some(x => originals.has(x))) return 'SHARED';
  order.sort((a, b) => a.val - b.val);
  return order.map(x => x.val + ':' + x.neighbors.map(nb => nb.val).sort((a, b) => a - b).map(v => ' ' + v).join('')).join('\\n');
}
''',
    js_params="node",
    java_members='''    static class Node {
        int val;
        List<Node> neighbors = new ArrayList<>();
        Node(int val) { this.val = val; }
    }

    static Node[] originals;

    static String dump(Node copy) {
        if (copy == null) return "NULL";
        Set<Node> orig = Collections.newSetFromMap(new IdentityHashMap<>());
        orig.addAll(Arrays.asList(originals));
        Set<Node> seen = Collections.newSetFromMap(new IdentityHashMap<>());
        List<Node> order = new ArrayList<>();
        order.add(copy);
        seen.add(copy);
        for (int i = 0; i < order.size(); i++)
            for (Node nb : order.get(i).neighbors)
                if (seen.add(nb)) order.add(nb);
        for (Node x : order) if (orig.contains(x)) return "SHARED";
        order.sort(Comparator.comparingInt(x -> x.val));
        StringBuilder sb = new StringBuilder();
        for (Node x : order) {
            if (sb.length() > 0) sb.append('\\n');
            sb.append(x.val).append(':');
            List<Integer> vs = new ArrayList<>();
            for (Node nb : x.neighbors) vs.add(nb.val);
            Collections.sort(vs);
            for (int v : vs) sb.append(' ').append(v);
        }
        return sb.toString();
    }
''',
    java="        int n = sc.nextInt(), m = sc.nextInt();\n        originals = new Node[n];\n"
         "        for (int i = 0; i < n; i++) originals[i] = new Node(i);\n"
         "        for (int i = 0; i < m; i++) {\n"
         "            int u = sc.nextInt(), v = sc.nextInt();\n"
         "            originals[u].neighbors.add(originals[v]);\n"
         "            originals[v].neighbors.add(originals[u]);\n"
         "        }\n        Node node = originals[0];\n",
    java_params="Node node", java_args="node", wrap="dump",
)


# ---------------------------------------------------------------------------
# Copy a list with random pointers: n, then n lines "val random", where random
# is the index of the node it points at or -1. Node i's `next` is node i + 1.
# ---------------------------------------------------------------------------

_SHAPES["random_list"] = dict(
    py='''class Node:
    def __init__(self, val):
        self.val = val
        self.next = None
        self.random = None

d = list(map(int, sys.stdin.read().split()))
n = d[0]
nodes = [Node(d[1 + 2 * i]) for i in range(n)]
for i in range(n):
    if i + 1 < n:
        nodes[i].next = nodes[i + 1]
    r = d[2 + 2 * i]
    nodes[i].random = nodes[r] if r >= 0 else None
head = nodes[0] if n else None

def dump(copy):
    originals = set(id(x) for x in nodes)
    order = []
    p = copy
    while p is not None:
        if id(p) in originals:
            return "SHARED"
        order.append(p)
        p = p.next
    if not order:
        return "EMPTY"
    index = {id(x): i for i, x in enumerate(order)}
    out = []
    for x in order:
        if x.random is None:
            out.append(str(x.val) + " -1")
        elif id(x.random) in index:
            out.append(str(x.val) + " " + str(index[id(x.random)]))
        else:
            return "RANDOM OUTSIDE COPY"
    return "\\n".join(out)
''',
    py_params="head",
    js='''class Node { constructor(val) { this.val = val; this.next = null; this.random = null; } }
const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);
const n = d[0];
const nodes = Array.from({ length: n }, (_, i) => new Node(d[1 + 2 * i]));
for (let i = 0; i < n; i++) {
  if (i + 1 < n) nodes[i].next = nodes[i + 1];
  const r = d[2 + 2 * i];
  nodes[i].random = r >= 0 ? nodes[r] : null;
}
const head = n ? nodes[0] : null;
function dump(copy) {
  const originals = new Set(nodes), order = [];
  for (let p = copy; p; p = p.next) { if (originals.has(p)) return 'SHARED'; order.push(p); }
  if (!order.length) return 'EMPTY';
  const index = new Map(order.map((x, i) => [x, i])), out = [];
  for (const x of order) {
    if (!x.random) out.push(x.val + ' -1');
    else if (index.has(x.random)) out.push(x.val + ' ' + index.get(x.random));
    else return 'RANDOM OUTSIDE COPY';
  }
  return out.join('\\n');
}
''',
    js_params="head",
    java_members='''    static class Node {
        int val;
        Node next, random;
        Node(int val) { this.val = val; }
    }

    static Node[] originals;

    static String dump(Node copy) {
        Set<Node> orig = Collections.newSetFromMap(new IdentityHashMap<>());
        orig.addAll(Arrays.asList(originals));
        List<Node> order = new ArrayList<>();
        for (Node p = copy; p != null; p = p.next) {
            if (orig.contains(p)) return "SHARED";
            order.add(p);
        }
        if (order.isEmpty()) return "EMPTY";
        Map<Node, Integer> index = new IdentityHashMap<>();
        for (int i = 0; i < order.size(); i++) index.put(order.get(i), i);
        StringBuilder sb = new StringBuilder();
        for (Node x : order) {
            if (sb.length() > 0) sb.append('\\n');
            if (x.random == null) sb.append(x.val).append(" -1");
            else if (index.containsKey(x.random)) sb.append(x.val).append(' ').append(index.get(x.random));
            else return "RANDOM OUTSIDE COPY";
        }
        return sb.toString();
    }
''',
    java="        int n = sc.nextInt();\n        originals = new Node[n];\n        int[] rnd = new int[n];\n"
         "        for (int i = 0; i < n; i++) { originals[i] = new Node(sc.nextInt()); rnd[i] = sc.nextInt(); }\n"
         "        for (int i = 0; i < n; i++) {\n"
         "            if (i + 1 < n) originals[i].next = originals[i + 1];\n"
         "            originals[i].random = rnd[i] >= 0 ? originals[rnd[i]] : null;\n"
         "        }\n        Node head = n > 0 ? originals[0] : null;\n",
    java_params="Node head", java_args="head", wrap="dump",
)


# ---------------------------------------------------------------------------
# Multilevel doubly linked list: n, then n lines "val next child" (indices or
# -1). Node 0 is the head; `prev` is set from the `next` links. The printer
# walks the returned list and checks that it really is flat.
# ---------------------------------------------------------------------------

_SHAPES["multilevel"] = dict(
    py='''class Node:
    def __init__(self, val):
        self.val = val
        self.prev = None
        self.next = None
        self.child = None

d = list(map(int, sys.stdin.read().split()))
n = d[0]
nodes = [Node(d[1 + 3 * i]) for i in range(n)]
for i in range(n):
    nx, ch = d[2 + 3 * i], d[3 + 3 * i]
    if nx >= 0:
        nodes[i].next = nodes[nx]
        nodes[nx].prev = nodes[i]
    if ch >= 0:
        nodes[i].child = nodes[ch]
head = nodes[0] if n else None

def dump(h):
    if h is None:
        return "EMPTY"
    out, prev, p = [], None, h
    while p is not None:
        if p.child is not None:
            return "CHILD LEFT AT " + str(p.val)
        if p.prev is not prev:
            return "BAD PREV AT " + str(p.val)
        out.append(str(p.val))
        prev, p = p, p.next
    return " ".join(out)
''',
    py_params="head",
    js='''class Node { constructor(val) { this.val = val; this.prev = null; this.next = null; this.child = null; } }
const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);
const n = d[0];
const nodes = Array.from({ length: n }, (_, i) => new Node(d[1 + 3 * i]));
for (let i = 0; i < n; i++) {
  const nx = d[2 + 3 * i], ch = d[3 + 3 * i];
  if (nx >= 0) { nodes[i].next = nodes[nx]; nodes[nx].prev = nodes[i]; }
  if (ch >= 0) nodes[i].child = nodes[ch];
}
const head = n ? nodes[0] : null;
function dump(h) {
  if (!h) return 'EMPTY';
  const out = [];
  let prev = null;
  for (let p = h; p; prev = p, p = p.next) {
    if (p.child) return 'CHILD LEFT AT ' + p.val;
    if (p.prev !== prev) return 'BAD PREV AT ' + p.val;
    out.push(p.val);
  }
  return out.join(' ');
}
''',
    js_params="head",
    java_members='''    static class Node {
        int val;
        Node prev, next, child;
        Node(int val) { this.val = val; }
    }

    static String dump(Node h) {
        if (h == null) return "EMPTY";
        StringBuilder sb = new StringBuilder();
        Node prev = null;
        for (Node p = h; p != null; prev = p, p = p.next) {
            if (p.child != null) return "CHILD LEFT AT " + p.val;
            if (p.prev != prev) return "BAD PREV AT " + p.val;
            if (sb.length() > 0) sb.append(' ');
            sb.append(p.val);
        }
        return sb.toString();
    }
''',
    java="        int n = sc.nextInt();\n        Node[] nodes = new Node[n];\n        int[] nx = new int[n], ch = new int[n];\n"
         "        for (int i = 0; i < n; i++) { nodes[i] = new Node(sc.nextInt()); nx[i] = sc.nextInt(); ch[i] = sc.nextInt(); }\n"
         "        for (int i = 0; i < n; i++) {\n"
         "            if (nx[i] >= 0) { nodes[i].next = nodes[nx[i]]; nodes[nx[i]].prev = nodes[i]; }\n"
         "            if (ch[i] >= 0) nodes[i].child = nodes[ch[i]];\n"
         "        }\n        Node head = n > 0 ? nodes[0] : null;\n",
    java_params="Node head", java_args="head", wrap="dump",
)


# "n m q", then m directed weighted edges "u v w", then q queries "a b".
_SHAPES["wgraph_q"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn, m, q = d[0], d[1], d[2]\n"
       "edges = [(d[3 + 3 * i], d[4 + 3 * i], d[5 + 3 * i]) for i in range(m)]\n"
       "queries = [(d[3 + 3 * m + 2 * i], d[4 + 3 * m + 2 * i]) for i in range(q)]\n",
    py_params="n, edges, queries",
    js=_JS_NUMS + "const n = Number(d[0]), m = Number(d[1]), q = Number(d[2]);\n"
       "const edges = Array.from({ length: m }, (_, i) => [0, 1, 2].map(j => Number(d[3 + 3 * i + j])));\n"
       "const queries = Array.from({ length: q }, (_, i) => [Number(d[3 + 3 * m + 2 * i]), Number(d[4 + 3 * m + 2 * i])]);\n",
    js_params="n, edges, queries",
    java="        int n = sc.nextInt(), m = sc.nextInt(), q = sc.nextInt();\n        int[][] edges = new int[m][3];\n"
         "        for (int i = 0; i < m; i++) for (int j = 0; j < 3; j++) edges[i][j] = sc.nextInt();\n"
         "        int[][] queries = new int[q][2];\n"
         "        for (int i = 0; i < q; i++) { queries[i][0] = sc.nextInt(); queries[i][1] = sc.nextInt(); }\n",
    java_params="int n, int[][] edges, int[][] queries", java_args="n, edges, queries",
)

# n, then the n values on one line, then q, then q lines of operation tokens.
_SHAPES["arr_ops"] = dict(
    py="L = sys.stdin.read().split('\\n')\nn = int(L[0])\na = list(map(int, L[1].split()))[:n]\n"
       "q = int(L[2])\nops = [L[3 + i].split() for i in range(q)]\n",
    py_params="a, ops",
    js=_JS_LINES + "const n = Number(L[0]);\nconst a = L[1].trim().split(/\\s+/).filter(Boolean).map(Number).slice(0, n);\n"
       "const q = Number(L[2]);\nconst ops = L.slice(3, 3 + q).map(l => l.trim().split(/\\s+/));\n",
    js_params="a, ops",
    java="        int n = Integer.parseInt(sc.nextLine().trim());\n        int[] a = new int[n];\n"
         "        String[] row = sc.nextLine().trim().split(\"\\\\s+\");\n"
         "        for (int i = 0; i < n; i++) a[i] = Integer.parseInt(row[i]);\n"
         "        int q = Integer.parseInt(sc.nextLine().trim());\n        String[][] ops = new String[q][];\n"
         "        for (int i = 0; i < q; i++) ops[i] = sc.nextLine().trim().split(\"\\\\s+\");\n",
    java_params="int[] a, String[][] ops", java_args="a, ops",
)

# m, then m lines "FROM TO".
_SHAPES["tickets"] = dict(
    py="d = sys.stdin.read().split()\nm = int(d[0])\ntickets = [(d[1 + 2 * i], d[2 + 2 * i]) for i in range(m)]\n",
    py_params="tickets",
    js=_JS_NUMS + "const m = Number(d[0]);\nconst tickets = Array.from({ length: m }, (_, i) => [d[1 + 2 * i], d[2 + 2 * i]]);\n",
    js_params="tickets",
    java="        int m = sc.nextInt();\n        String[][] tickets = new String[m][2];\n"
         "        for (int i = 0; i < m; i++) { tickets[i][0] = sc.next(); tickets[i][1] = sc.next(); }\n",
    java_params="String[][] tickets", java_args="tickets",
)
