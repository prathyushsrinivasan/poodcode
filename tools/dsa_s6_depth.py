# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 6 (Trees & Graphs) — the depth layer, part 1: binary trees, BSTs,
# backtracking and graph traversal.
#
# exec'd by tools/dsa_curriculum.py after dsa_s4_help.py, in the same
# namespace; tools/dsa_s6_depth2.py holds the other four units, the rebuilt
# ladders, the stage router and the attach step. For each unit this file
# defines a `_D6_<UNIT>` dict:
#
#   invariant, variants, rewrites, internals, build_it
#   extra skeletons, signals, costs, pitfalls and checks for the new material
#   computed traces and extra Big-O drills
#
# Every trace row is produced by running the algorithm it describes, as in
# dsa_s3_depth.py and dsa_s4_depth.py, so a table cannot disagree with the
# code beside it.
# ---------------------------------------------------------------------------

import heapq as _hq
from collections import deque as _dq


# ============================================================ tiny tree kit

class _TN:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val, self.left, self.right = val, None, None


def _t6_build(line):
    toks = line.split()
    if not toks or toks[0] == "null":
        return None
    root = _TN(int(toks[0]))
    q, i = _dq([root]), 1
    while q and i < len(toks):
        n = q.popleft()
        if i < len(toks) and toks[i] != "null":
            n.left = _TN(int(toks[i]))
            q.append(n.left)
        i += 1
        if i < len(toks) and toks[i] != "null":
            n.right = _TN(int(toks[i]))
            q.append(n.right)
        i += 1
    return root


def _t6_level(root):
    if root is None:
        return "EMPTY"
    out, q, i = [], [root], 0
    while i < len(q):
        n = q[i]
        i += 1
        if n is None:
            out.append("null")
            continue
        out.append(str(n.val))
        q.append(n.left)
        q.append(n.right)
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def _t6_orders(root):
    pre, ino, post = [], [], []

    def go(n):
        if n is None:
            return
        pre.append(n.val)
        go(n.left)
        ino.append(n.val)
        go(n.right)
        post.append(n.val)

    go(root)
    lvl, q = [], _dq([root] if root else [])
    while q:
        n = q.popleft()
        lvl.append(n.val)
        for c in (n.left, n.right):
            if c:
                q.append(c)
    return pre, ino, post, lvl


def _t6_height(n):
    return 0 if n is None else 1 + max(_t6_height(n.left), _t6_height(n.right))


def _t6_bst_insert(root, v):
    if root is None:
        return _TN(v)
    x = root
    while True:
        if v < x.val:
            if x.left is None:
                x.left = _TN(v)
                break
            x = x.left
        else:
            if x.right is None:
                x.right = _TN(v)
                break
            x = x.right
    return root


def _t6_bst(vals):
    root = None
    for v in vals:
        root = _t6_bst_insert(root, v)
    return root


def _j(xs):
    return " ".join(map(str, xs)) if xs else "—"


# ============================================================ computed traces

def _t6_inorder_stack():
    line = "4 2 6 1 3 5"
    root = _t6_build(line)
    rows, st, cur, out, step = [], [], root, [], 0
    while cur or st:
        while cur:
            st.append(cur)
            step += 1
            rows.append([str(step), f"push {cur.val}, go left", _j([x.val for x in st]), _j(out)])
            cur = cur.left
        cur = st.pop()
        out.append(cur.val)
        step += 1
        rows.append([str(step), f"pop {cur.val}, visit it, go right",
                     _j([x.val for x in st]), _j(out)])
        cur = cur.right
    return _trace(
        "Iterative in-order on 4 2 6 1 3 5",
        "The explicit stack holds the nodes whose left subtree is being walked and which have "
        "not been visited yet — exactly the frames a recursive in-order would have on the call "
        "stack.",
        ["Step", "Action", "Stack (bottom → top)", "Visited"],
        rows,
        f"Output {_j(out)} — sorted, because the tree is a BST. The stack never holds more than "
        f"one root-to-leaf path ({_t6_height(root)} nodes here), which is the O(h) memory. Every "
        f"node is pushed once and popped once: {2 * len(out)} stack operations for {len(out)} nodes.",
    )


def _t6_reroot():
    n, edges = 5, [(0, 1), (0, 2), (2, 3), (2, 4)]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    parent, order, seen = [-1] * n, [0], [False] * n
    seen[0] = True
    for u in order:
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                order.append(v)
    size, down = [1] * n, [0] * n
    rows = []
    for u in reversed(order):
        p = parent[u]
        if p >= 0:
            size[p] += size[u]
            down[p] += down[u] + size[u]
    for u in reversed(order):
        rows.append(["1 (bottom-up)", str(u), str(size[u]), str(down[u]), "—"])
    ans = [0] * n
    ans[0] = down[0]
    rows.append(["2 (top-down)", "0", str(size[0]), str(down[0]), f"{ans[0]} = down[0]"])
    for u in order[1:]:
        p = parent[u]
        ans[u] = ans[p] - size[u] + (n - size[u])
        rows.append(["2 (top-down)", str(u), str(size[u]), str(down[u]),
                     f"{ans[p]} − {size[u]} + {n - size[u]} = {ans[u]}"])
    return _trace(
        "Rerooting: the sum of distances from every node",
        "The tree 0-1, 0-2, 2-3, 2-4. Pass 1 walks a BFS order backwards to get subtree sizes "
        "and `down[v]` (distances into v's own subtree); pass 2 walks it forwards, moving the "
        "root across one edge at a time.",
        ["Pass", "Node", "size", "down", "ans"],
        rows,
        f"Answers {_j(ans)}. Moving the root from p to child c brings c's {''}size[c] nodes one "
        f"step closer and pushes the other n − size[c] one step away — so each answer is its "
        f"parent's plus a constant, and n answers cost O(n), not n BFS runs.",
    )


def _t6_cameras():
    line = "0 0 null 0 0 null null 0 0"
    root = _t6_build(line)
    names, k = {}, 0
    q = _dq([root])
    while q:
        x = q.popleft()
        names[id(x)] = chr(ord("A") + k)
        k += 1
        for c in (x.left, x.right):
            if c:
                q.append(c)
    label = {0: "not watched", 1: "GUARD", 2: "watched"}
    rows, guards = [], [0]

    def go(x):
        if x is None:
            return 2
        l, r = go(x.left), go(x.right)
        if l == 0 or r == 0:
            guards[0] += 1
            s, why = 1, "a child is unwatched → must hold a guard"
        elif l == 1 or r == 1:
            s, why = 2, "a child has a guard → watched for free"
        else:
            s, why = 0, "children fine, nobody watches it → leave it to the parent"
        rows.append([names[id(x)], label[l], label[r], label[s], why])
        return s

    top = go(root)
    extra = ""
    if top == 0:
        guards[0] += 1
        extra = " The root came back unwatched, so it takes one more guard."
    return _trace(
        "Guard placement, bottom-up (rooms named A, B, C… in level order)",
        f"The tree {line}. Each room reports one of three states to its parent; an empty child "
        f"counts as \"watched\", so leaves never take a guard.",
        ["Room", "Left child", "Right child", "Room's state", "Why"],
        rows,
        f"{guards[0]} guard(s).{extra} Every guard lands on the parent of the deepest "
        f"unwatched room — the one placement that watches the most rooms still unwatched.",
    )


def _t6_bst_delete():
    vals = [50, 30, 70, 20, 40, 60, 80, 35, 45, 37]
    root = _t6_bst(vals)
    before = _t6_level(root)
    rows = []

    def delete(n, key, depth):
        pad = "· " * depth
        if n is None:
            rows.append([f"{pad}null", f"{key} not found", "—"])
            return None
        if key < n.val:
            rows.append([f"{pad}{n.val}", f"{key} < {n.val}: go left", "—"])
            n.left = delete(n.left, key, depth + 1)
            return n
        if key > n.val:
            rows.append([f"{pad}{n.val}", f"{key} > {n.val}: go right", "—"])
            n.right = delete(n.right, key, depth + 1)
            return n
        if n.left is None:
            rows.append([f"{pad}{n.val}", "found; no left child", "replace it by its right child"])
            return n.right
        if n.right is None:
            rows.append([f"{pad}{n.val}", "found; no right child", "replace it by its left child"])
            return n.left
        s = n.right
        path = [s.val]
        while s.left:
            s = s.left
            path.append(s.val)
        rows.append([f"{pad}{n.val}", "found; two children",
                     f"successor = leftmost of the right subtree ({' → '.join(map(str, path))}); copy {s.val} in"])
        old = n.val
        n.val = s.val
        rows.append([f"{pad}{n.val} (was {old})", f"now delete {s.val} from the right subtree", "—"])
        n.right = delete(n.right, s.val, depth + 1)
        return n

    root = delete(root, 30, 0)
    return _trace(
        "Deleting 30, a node with two children",
        f"The BST built by inserting {', '.join(map(str, vals))} — level order {before}. Indented "
        f"rows are deeper calls.",
        ["At node", "Decision", "Repair"],
        rows,
        f"Afterwards: {_t6_level(root)}. The successor had no left child (it was the leftmost), "
        f"so the second deletion was always the easy case — at most one child. That is why the "
        f"two-child case never recurses into itself.",
    )


def _t6_sorted_build():
    a = [3, 8, 11, 15, 19, 24, 30, 42]
    rows = []

    def build(lo, hi, parent, side):
        if lo > hi:
            return None
        m = (lo + hi) // 2
        where = "root" if parent is None else f"{side} child of {parent}"
        rows.append([f"[{lo}, {hi}]", str(m), str(a[m]), where])
        n = _TN(a[m])
        n.left = build(lo, m - 1, a[m], "left")
        n.right = build(m + 1, hi, a[m], "right")
        return n

    root = build(0, len(a) - 1, None, "")
    return _trace(
        f"Building a balanced BST from {_j(a)}",
        "Each call takes an index range, makes its lower middle the node, and hands the two "
        "halves to its children — pre-order, so rows appear root first.",
        ["Range", "mid", "Value", "Becomes"],
        rows,
        f"Level order {_t6_level(root)}, height {_t6_height(root)} = ⌈log₂(8 + 1)⌉. Inserting the "
        f"same values in sorted order would make a chain of height 8.",
    )


def _t6_combo_sum():
    cand, target = [2, 3, 5], 8
    rows, path = [], []

    def dfs(start, rem):
        if rem == 0:
            rows.append([_j(path), str(rem), "—", "**emit**"])
            return
        for i in range(start, len(cand)):
            if cand[i] > rem:
                rows.append([_j(path), str(rem), str(cand[i]),
                             f"{cand[i]} > {rem}: **break** — every later candidate is bigger"])
                return
            path.append(cand[i])
            rows.append([_j(path[:-1]), str(rem), str(cand[i]), f"take {cand[i]}, recurse with start = {i}"])
            dfs(i, rem - cand[i])
            path.pop()

    dfs(0, target)
    emitted = sum(1 for r in rows if r[3] == "**emit**")
    breaks = sum(1 for r in rows if "break" in r[3])
    return _trace(
        f"Combination sum over {_j(cand)}, target {target}, candidates sorted",
        "Reuse is allowed, so each call recurses with start = i (not i + 1). Sorting turns "
        "\"this candidate is too big\" into \"every candidate from here on is too big\".",
        ["Path so far", "Remaining", "Candidate", "Action"],
        rows,
        f"{emitted} combinations, found with {breaks} `break`s. Each break cuts a whole tail of "
        f"the loop, not one iteration — with `continue` the search would still try every larger "
        f"candidate first.",
    )


def _t6_buckets():
    a, k = [5, 4, 3, 3, 2, 1], 3
    t = sum(a) // k
    load = [0] * k
    rows = []
    calls = [0]

    def place(i):
        calls[0] += 1
        if i == len(a):
            rows.append([str(i), "—", "—", _j(load), "all placed: **success**"])
            return True
        for b in range(k):
            if load[b] + a[i] > t:
                rows.append([str(i), str(a[i]), str(b), _j(load), f"{load[b]} + {a[i]} > {t}: skip"])
                continue
            if b > 0 and load[b] == load[b - 1]:
                rows.append([str(i), str(a[i]), str(b), _j(load), f"same load as bucket {b - 1}: **skip (symmetry)**"])
                continue
            load[b] += a[i]
            rows.append([str(i), str(a[i]), str(b), _j(load), "place"])
            if place(i + 1):
                return True
            load[b] -= a[i]
            rows.append([str(i), str(a[i]), str(b), _j(load), "undo"])
            if load[b] == 0:
                rows.append([str(i), str(a[i]), str(b), _j(load), "an empty bucket failed: **stop**"])
                break
        return False

    ok = place(0)
    return _trace(
        f"Three equal buckets from {_j(a)} (target {t} each)",
        "Items largest first, so the big items claim buckets early and the capacity check "
        "rejects most placements outright. The run never backtracks: largest-first ordering "
        "is doing most of the pruning before the symmetry rule is even needed.",
        ["Item #", "Value", "Bucket", "Loads after", "Action"],
        rows,
        f"{'A split found' if ok else 'No split'} in {calls[0]} calls. Without the symmetry rule "
        f"the first item alone would be tried in all three empty buckets — and every partial "
        f"answer would be explored once per relabelling of the buckets, up to 3! = 6 times.",
    )


def _t6_dfs_times():
    n = 6
    edges = [(0, 1), (1, 2), (2, 0), (1, 3), (0, 3), (4, 3), (4, 5)]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    colour = [0] * n
    tin, tout = [0] * n, [0] * n
    clock = [0]
    rows = []

    def dfs(u):
        colour[u] = 1
        clock[0] += 1
        tin[u] = clock[0]
        rows.append([str(clock[0]), f"enter {u}", "—", "—"])
        for v in adj[u]:
            if colour[v] == 0:
                kind = "tree"
                rows.append([str(clock[0]), f"edge {u}→{v}", "white", kind])
                dfs(v)
            elif colour[v] == 1:
                rows.append([str(clock[0]), f"edge {u}→{v}", "grey (on the stack)", "**back** → a cycle"])
            else:
                kind = "forward" if tin[u] < tin[v] else "cross"
                rows.append([str(clock[0]), f"edge {u}→{v}", "black (finished)", kind])
        colour[u] = 2
        clock[0] += 1
        tout[u] = clock[0]
        rows.append([str(clock[0]), f"leave {u}", "—", "—"])

    for s in range(n):
        if colour[s] == 0:
            dfs(s)
    return _trace(
        "DFS with entry/exit times and edge types (directed)",
        "Edges 0→1, 1→2, 2→0, 1→3, 0→3, 4→3, 4→5. White = unseen, grey = on the recursion "
        "stack, black = finished. The colour of v when u→v is examined names the edge.",
        ["Clock", "Event", "Colour of the target", "Edge type"],
        rows,
        "Only a **back** edge (to a grey vertex) closes a cycle — the 2→0 edge here. Forward "
        "and cross edges reach finished vertices and are harmless. That one distinction is the "
        "three-colour cycle check, and why a two-state visited[] cannot do it on a directed graph.",
    )


def _t6_state_bfs():
    g = ["b.A.@.a"]
    r, c = 1, len(g[0])
    si = g[0].index("@")
    K = 2
    ALL = 3
    seen = {(0, si, 0)}
    frontier = [(0, si, 0)]
    rows, steps = [], 0
    while frontier:
        done = any(m == ALL for _, _, m in frontier)
        desc = ", ".join(f"({j}, {'{' + ','.join(ch for b, ch in ((0, 'a'), (1, 'b')) if m >> b & 1) + '}'})"
                         for _, j, m in frontier)
        rows.append([str(steps), desc, "**all keys**" if done else "—"])
        if done:
            break
        nxt = []
        for i, j, m in frontier:
            for dj in (-1, 1):
                nj = j + dj
                if not 0 <= nj < c:
                    continue
                ch = g[0][nj]
                if ch == "#":
                    continue
                if "A" <= ch <= "F" and not m >> (ord(ch) - 65) & 1:
                    continue
                nm = m | (1 << (ord(ch) - 97)) if "a" <= ch <= "f" else m
                if (0, nj, nm) not in seen:
                    seen.add((0, nj, nm))
                    nxt.append((0, nj, nm))
        frontier = nxt
        steps += 1
    return _trace(
        "BFS over (cell, keys) on the corridor b.A.@.a",
        "Cells are numbered 0 to 6 from the left. The door A (cell 2) needs key a (cell 6). "
        "Each row is one BFS layer: every state first reached after that many steps.",
        ["Steps", "States (cell, keys held)", ""],
        rows,
        "Cell 3 appears twice — once without keys (step 1) and once holding a (step 5). Plain "
        "grid BFS would have marked cell 3 visited at step 1 and never let the walker back "
        "through it with the key, answering −1. The visited set is over states.",
    )


# ================================================================ Big-O drills

_BIGO_S6A = {
    "trees": [
        _bigo("""
int total = 0;
for (TreeNode v : allNodes)             // n nodes
    total += distSumByBfs(v);           // one BFS over the tree
""", "O(n²)", ["O(n²)", "O(n log n)", "O(n)", "O(n · h)"],
              """
n BFS runs, each O(n). Rerooting gets every node's distance sum in two O(n) passes, because
moving the root across one edge changes the sum by n − 2 · size[child].
"""),
        _bigo("""
TreeNode cur = root;
while (cur != null) {
    if (cur.left != null) {
        TreeNode p = cur.left;
        while (p.right != null) p = p.right;
        p.right = cur.right; cur.right = cur.left; cur.left = null;
    }
    cur = cur.right;
}
""", "O(n)", ["O(n)", "O(n²)", "O(n log n)", "O(n · h)"],
              """
The inner loop walks the right spine of cur's left subtree. After the splice those nodes sit
*behind* cur on the chain, and cur only moves forward — so no node is on two inner walks.
Total inner steps ≤ n.
"""),
        _bigo("""
TreeNode build(int lo, int hi) {         // inorder range
    if (lo > hi) return null;
    TreeNode root = new TreeNode(post[idx--]);
    int m = lo;
    while (ino[m] != root.val) m++;      // linear search for the split
    root.right = build(m + 1, hi);
    root.left = build(lo, m - 1);
    return root;
}
""", "O(n²) worst case", ["O(n²) worst case", "O(n)", "O(n log n) always", "O(h)"],
              """
Each call scans its range for the root — O(n) per level. On a balanced tree that is
O(n log n); on a chain every scan is long and the total is O(n²). A value → index map makes
each split O(1): O(n) overall.
"""),
    ],
    "bst": [
        _bigo("""
for (int key : keys)                     // k deletions
    root = delete(root, key);            // descent + successor walk
""", "O(k · h)", ["O(k · h)", "O(k · n)", "O(k log n) always", "O(n)"],
              """
A deletion is one descent to the key plus, in the two-child case, one walk down to the
successor — both bounded by the height. h is log n only if the tree stays balanced.
"""),
        _bigo("""
TreeNode trim(TreeNode n) {
    if (n == null) return null;
    if (n.val < lo) return trim(n.right);
    if (n.val > hi) return trim(n.left);
    n.left = trim(n.left); n.right = trim(n.right);
    return n;
}
""", "O(n)", ["O(n)", "O(h)", "O(n log n)", "O(n²)"],
              """
Every node is visited at most once, and the out-of-range cases *skip* a whole subtree without
visiting it — so often far fewer than n. The worst case (everything in range) visits all n.
"""),
        _bigo("""
// merge two BSTs of sizes n and m
List<Integer> a = inorder(r1), b = inorder(r2);
List<Integer> all = new ArrayList<>(a); all.addAll(b);
Collections.sort(all);
""", "O((n + m) log(n + m))", ["O((n + m) log(n + m))", "O(n + m)", "O(n · m)", "O(n log m)"],
              """
The in-orders are O(n + m), but sorting throws away the fact that both lists were already
sorted. Merging the two lists — or two BST iterators — is O(n + m).
"""),
    ],
    "backtracking": [
        _bigo("""
void gen(int i) {                        // n positions
    if (i == n) { out.append(buf).append('\\n'); return; }
    buf[i] = '0'; gen(i + 1);
    buf[i] = '1'; gen(i + 1);
}
""", "O(2ⁿ · n)", ["O(2ⁿ · n)", "O(2ⁿ)", "O(n²)", "O(n!)"],
              """
2ⁿ leaves, and each writes an n-character string. The internal calls add 2ⁿ − 1 more, which
does not change the order.
"""),
        _bigo("""
long count(int i) {                       // n regions, k colours
    if (i == n) return 1;
    long ways = 0;
    for (int c = 0; c < k; c++)
        if (legal(i, c)) { colour[i] = c; ways += count(i + 1); }
    return ways;
}
""", "O(kⁿ · d) worst case", ["O(kⁿ · d) worst case", "O(k · n)", "O(n!)", "O(2ⁿ)"],
              """
With no borders every colouring is legal, so the search visits all kⁿ leaves; each legality
check scans a region's d neighbours. Borders prune — but the worst case is still exponential,
which is why n ≤ 10.
"""),
        _bigo("""
ok[n] = true;
for (int i = n - 1; i >= 0; i--)
    for (String w : dict)
        if (s.startsWith(w, i) && ok[i + w.length()]) { ok[i] = true; break; }
""", "O(n · d · L)", ["O(n · d · L)", "O(2ⁿ)", "O(n²)", "O(d · L)"],
              """
n positions, d words, and `startsWith` compares up to L characters. This feasibility table is
cheap — and it is what stops the sentence-listing search from exploring exponentially many
dead prefixes.
"""),
    ],
    "graph-traversal": [
        _bigo("""
// BFS over (row, col, keys) states
boolean[][][] seen = new boolean[R][C][1 << K];
// ... each state popped once, four moves each
""", "O(R · C · 2ᴷ)", ["O(R · C · 2ᴷ)", "O(R · C)", "O(R · C · K)", "O((R · C)²)"],
              """
The state space is cells × key subsets, and BFS touches each state once with four moves.
With K ≤ 6 that is 64 layers of the grid — fine. With K = 20 it would not be.
"""),
        _bigo("""
for (int s = 1; s <= n; s++)                   // squares of the board
    for (int d = 1; d <= 6 && s + d <= n; d++)
        relax(s, jump(s + d));                 // BFS edges, each once
""", "O(n)", ["O(n)", "O(n log n)", "O(6ⁿ)", "O(n²)"],
              """
An implicit graph still has a size: n vertices with at most six out-edges each, so BFS is
O(6n) = O(n). Nothing is exponential about a game once each square is visited once.
"""),
        _bigo("""
Deque<Integer> q = new ArrayDeque<>();
q.add(src);
while (!q.isEmpty()) {
    int u = q.poll();
    if (seen[u]) continue;       // marked on POP
    seen[u] = true;
    for (int v : adj[u]) if (!seen[v]) q.add(v);
}
""", "O(V + E) time, but O(E) queue", ["O(V + E) time, but O(E) queue", "O(V) queue", "O(V · E)", "O(V²) time"],
              """
Marking on pop lets a vertex be enqueued once per incoming edge before it is ever popped, so
the queue can hold O(E) entries. Still linear time, since each entry is popped once — but
marking on push keeps the queue at O(V) and is the version to write.
"""),
    ],
}


# ================================================================ the depth

_D6_TREES = dict(
    invariant=_inv(
        "Every call `f(node)` returns the correct answer **for the subtree rooted at `node`** "
        "(and, for top-down calls, given the context passed in).",
        "The base case: `f(null)` returns the answer for the empty tree — 0 for a height or a "
        "count, `true` for \"is balanced\", \"watched\" for the camera cover. It is chosen so "
        "the combine step is right at a leaf.",
        "Assume both recursive calls return correct answers for their (smaller) subtrees — "
        "that is the induction hypothesis. The combine line builds the node's answer only from "
        "those answers and the node's own value, so it is correct too. The subtrees are "
        "strictly smaller, so the induction reaches the base case.",
        "`f(root)` is correct for the subtree rooted at the root — the whole tree. For level "
        "BFS the invariant is different: at the top of each outer iteration the queue holds "
        "exactly one level, left to right.",
        "Writing the invariant down picks the return value: if you cannot say what `f(child)` "
        "promises, the combine line is a guess. Diameter's `f` promises the height, not the "
        "diameter — which is why the diameter lives in a separate field.",
    ),
    variants=[
        _var("Bottom-up aggregate", "Return a value built from the children's values.",
             "Height, size, sum, balance.", "O(n) time, O(h) stack",
             "Choose the null value so a leaf works without a special case."),
        _var("Top-down parameter", "Pass context down as an argument.",
             "Path sums, depth, ancestor min/max, BST bounds.", "O(n), O(h)",
             "The parameter is the parent's knowledge; the return value can be void."),
        _var("Return one, record another", "Return the local value; update a field with the global answer.",
             "Diameter, max path sum, longest univalue path.", "O(n), O(h)",
             "Only one side can continue upwards; both can meet at the node."),
        _var("Pair recursion", "Recurse on two nodes at once.",
             "Same tree, mirror, subtree check, merge.", "O(min(n1, n2))",
             "Null handling: both null is equal; one null is not."),
        _var("Level-order BFS", "A queue and a frozen `size` per level.",
             "Level lists, right view, zigzag, level sums, min depth.", "O(n), O(width)",
             "Read `q.size()` before the inner loop."),
        _var("Coordinates carried down", "Give each child (row + 1, col ± 1).",
             "Vertical order, top/bottom view, width.", "O(n log n) with sorting",
             "Ties in one row and column need an explicit rule."),
        _var("Rebuild from two orders", "Pre/post-order names the root; in-order splits the rest.",
             "Construct a tree, verify a traversal pair.", "O(n) with an index map",
             "From post-order, build the right subtree first."),
        _var("Backtracking on a tree", "Push the node onto a path; pop after both children.",
             "List root-to-leaf paths, path sums with the path.", "O(n · h)",
             "Record a copy at a leaf, not a reference."),
        _var("Tree DP with states", "Return a small tuple of states instead of one number.",
             "House robber on a tree, camera cover, (take, skip).", "O(n)",
             "Each state must be defined for null."),
        _var("Rerooting", "One bottom-up pass, then a top-down pass moving the root one edge.",
             "An answer for every node as root: distance sums, farthest node.", "O(n)",
             "Needs a formula for how the answer changes across an edge."),
        _var("Iterative traversal", "An explicit `Deque` in place of the call stack.",
             "Very deep trees; pausable walks (iterators).", "O(n), O(h) heap memory",
             "Push the right child before the left for pre-order."),
        _var("In-place splice (Morris)", "Borrow null right pointers of predecessors as threads.",
             "O(1)-space in-order, flatten to a list.", "O(n), O(1)",
             "Restore the threads if the tree must survive."),
    ],
    rewrites=[
        _rw("Balanced check: stop recomputing heights",
            """
static boolean balanced(TreeNode n) {
    if (n == null) return true;
    return Math.abs(height(n.left) - height(n.right)) <= 1   // O(n) each call
        && balanced(n.left) && balanced(n.right);
}
""",
            """
static int check(TreeNode n) {           // height, or -1 if unbalanced below
    if (n == null) return 0;
    int l = check(n.left), r = check(n.right);
    if (l < 0 || r < 0 || Math.abs(l - r) > 1) return -1;
    return 1 + Math.max(l, r);
}
// balanced = check(root) >= 0
""",
            "Return the height from the same recursion, with −1 as \"already failed\".",
            """
The slow version calls `height` at every node, and `height` walks the whole subtree: O(n²) on
a chain. The fast one computes each subtree's height once, bottom-up, and the −1 carries the
failure upwards so nothing is lost by not asking again.
"""),
        _rw("Distance sums: reroot instead of n BFS runs",
            """
long[] ans = new long[n];
for (int s = 0; s < n; s++) ans[s] = bfsDistanceSum(s);     // O(n) each
""",
            """
// pass 1 (bottom-up, root 0): size[v], down[v]
// pass 2 (top-down):
ans[0] = down[0];
for (int c : bfsOrderExceptRoot)
    ans[c] = ans[parent[c]] - size[c] + (n - size[c]);
""",
            "Replace the per-root BFS with one formula per edge.",
            """
Moving the root from p to its child c changes every distance by exactly ±1: the size[c]
nodes on c's side get closer, the rest get farther. So ans[c] follows from ans[p] in O(1),
and no answer is lost — each is computed from a correct neighbour.
"""),
        _rw("Rebuild: look up, do not scan",
            """
int m = lo;
while (ino[m] != root.val) m++;          // O(n) per node on a skewed tree
""",
            """
Map<Integer, Integer> pos = new HashMap<>();
for (int i = 0; i < n; i++) pos.put(ino[i], i);
int m = pos.get(root.val);                // O(1)
""",
            "Precompute value → in-order index once.",
            """
Values are distinct, so the map is exact. The recursion is unchanged; only the search for the
split point moves from O(range) to O(1), taking the rebuild from O(n²) worst case to O(n).
"""),
        _rw("Deep trees: recursion → explicit stack",
            """
void inorder(TreeNode n) {               // StackOverflowError at depth ~10^4+
    if (n == null) return;
    inorder(n.left); visit(n); inorder(n.right);
}
""",
            """
Deque<TreeNode> st = new ArrayDeque<>();
for (TreeNode cur = root; cur != null || !st.isEmpty(); ) {
    while (cur != null) { st.push(cur); cur = cur.left; }
    cur = st.pop();
    visit(cur);
    cur = cur.right;
}
""",
            "The call stack becomes a `Deque` on the heap.",
            """
The same nodes are pushed in the same order — the stack holds exactly the frames the
recursion would. Only where the frames live changes, and the heap has room for 10⁶ of them.
"""),
    ],
    build_it="""
### A `Trees` toolkit, property-tested

Write one class and a `main` that checks each property on 1,000 random trees (sizes 0 to 50,
including chains and full trees):

**1. `build(String levelOrder)` and `level(TreeNode)`.** Property: `level(build(s)) == s` for
every canonical string (trailing `null`s trimmed).

**2. `pre`, `in`, `post`, `levelOrder` — recursive and iterative.** Property: both versions
agree; all four have n elements; pre-order starts with the root and post-order ends with it.

**3. `height`, `size`, `leaves`.** Properties: `height ≤ size`; a chain has height = size;
`leaves ≥ 1` for a non-empty tree; `size = 2 · (nodes with two children) + (nodes with one
child) + 1` counts edges two ways.

**4. `rebuild(pre, in)` and `rebuild2(post, in)`** for distinct values. Property: both return a
tree whose `level` equals the original's.

**5. `diameter`.** Property: equals the brute force "max over all pairs of the path length".

**6. `serialize` / `deserialize` with `#` for null.** Property: round trip is the identity,
including for trees that repeat values.

**7. `flatten`.** Property: afterwards every `left` is null and walking `right` gives the old
pre-order.
""",
    skeletons=[
        _sk("Carry the path's extremes",
            "Ancestor–descendant differences, \"good nodes\", bounds.",
            """
static int best(TreeNode n, int lo, int hi) {
    if (n == null) return hi - lo;
    lo = Math.min(lo, n.val);
    hi = Math.max(hi, n.val);
    return Math.max(best(n.left, lo, hi), best(n.right, lo, hi));
}
""",
            "The min and max of one root path are ancestor and descendant of each other."),
        _sk("Rerooting in two passes",
            "An answer for every node as the root.",
            """
// BFS order from 0, parent[] filled
for (int i = n - 1; i >= 1; i--) {           // bottom-up
    int u = order[i], p = parent[u];
    size[p] += size[u];
    down[p] += down[u] + size[u];
}
ans[0] = down[0];
for (int i = 1; i < n; i++) {                // top-down
    int u = order[i];
    ans[u] = ans[parent[u]] - size[u] + (n - size[u]);
}
""",
            "No recursion: a BFS order gives parents before children."),
        _sk("Three-state cover",
            "Cameras, guards, dominating sets on trees.",
            """
int dfs(TreeNode n) {                        // 0 unwatched, 1 guard, 2 watched
    if (n == null) return 2;
    int l = dfs(n.left), r = dfs(n.right);
    if (l == 0 || r == 0) { guards++; return 1; }
    return (l == 1 || r == 1) ? 2 : 0;
}
// guards + (dfs(root) == 0 ? 1 : 0)
""",
            "Null returns \"watched\", so leaves never take a guard."),
    ],
    signals=[
        _sig("“for every node, as if it were the root”", "Rerooting",
             "Two linear passes instead of n traversals."),
        _sig("“columns”, “vertical”, “top view”", "Carry (row, col) down; group by col",
             "A TreeMap keeps the columns ordered."),
        _sig("“minimum cameras / guards / monitors”", "Greedy post-order with states",
             "Cover the deepest uncovered node from its parent."),
        _sig("“list every root-to-leaf path”", "Backtracking on the tree",
             "Push, recurse both ways, pop."),
    ],
    costs=[
        _cost("Rerooting (all roots)", "O(n)", "O(n)", "Two passes over a BFS order."),
        _cost("Vertical order", "O(n log n)", "O(n)", "Sorting within columns."),
        _cost("Flatten in place", "O(n)", "O(1)", "The Morris-style splice."),
    ],
    pitfalls=[
        _pit("A post-order rebuild produces a different tree",
             "The left subtree was built first while consuming the post-order backwards.",
             "Backwards, post-order is root, right, left — build the right subtree first."),
        _pit("Every leaf gets a camera",
             "`null` returned \"not watched\", so every leaf's parent… and every leaf itself looked uncovered.",
             "Return \"watched\" for null: an empty child needs nothing."),
        _pit("Recorded paths are all empty or all identical",
             "The shared path list was stored instead of a copy.",
             "Record `new ArrayList<>(path)` or the joined string at the leaf."),
    ],
    checks=[
        _chk("Why does rerooting change the answer by n − 2 · size[c] when the root moves to child c?",
             "size[c] nodes (c's subtree) get one step closer and the other n − size[c] one step "
             "farther: −size[c] + (n − size[c])."),
        _chk("Why must the right subtree be built first when rebuilding from post-order?",
             "Read backwards, post-order is root, right subtree, left subtree. A shared index "
             "walking backwards reaches the right subtree's values first."),
        _chk("In the camera greedy, why is a leaf never given a guard?",
             "Its parent watches everything the leaf would (the leaf itself and the parent) and "
             "also the parent's parent and sibling — never worse."),
    ],
    traces=[_t6_inorder_stack(), _t6_reroot(), _t6_cameras()],
)


_D6_BST = dict(
    invariant=_inv(
        "Every node carries an open interval **(lo, hi)** it must lie in, and its value does: "
        "`lo < node.val < hi`.",
        "The root's interval is (−∞, +∞), which any value satisfies.",
        "Descending to the left child sets `hi = node.val`; to the right child sets "
        "`lo = node.val`. If every node satisfies its interval, every value in a node's left "
        "subtree is below it and every value in its right subtree is above it — and inserting "
        "a new value at the leaf the descent falls off keeps it true, because the descent "
        "narrowed the interval exactly as the new node's ancestors require.",
        "At a search's end the target is either at the node found or in no interval the tree "
        "has — it is absent. For a validity check, a node outside its interval is the "
        "counterexample, with the ancestor that set the violated bound.",
        "The interval view explains three things at once: why validation needs bounds, why "
        "trimming can discard whole subtrees, and why the in-order successor is the only value "
        "that can replace a deleted two-child node.",
    ),
    variants=[
        _var("Search / insert", "Descend by comparison; attach at the null you fall off.",
             "Lookup, insert, floor and ceiling.", "O(h)", "Decide where duplicates go, once."),
        _var("Delete", "0/1 child → splice; 2 children → copy the successor, delete it below.",
             "Removing keys.", "O(h)", "Return the new subtree root to the parent."),
        _var("Range-pruned walk", "Skip a subtree when its interval misses [lo, hi].",
             "Range sums, range counts, trim.", "O(h + k)", "Prune on both sides."),
        _var("Validate by bounds", "Pass (lo, hi) down.",
             "Is it a BST?", "O(n)", "Use long bounds."),
        _var("Validate by in-order", "In-order must be strictly increasing.",
             "Is it a BST? Recover two swapped nodes.", "O(n)", "Compare with the previous value only."),
        _var("Order statistics", "Iterative in-order, stop at k.",
             "k-th smallest, median of a BST.", "O(h + k)", "Recursion cannot stop early cleanly."),
        _var("Split point", "Descend while both targets are on one side.",
             "LCA in a BST.", "O(h)", "A target may be the split point itself."),
        _var("Iterator", "A stack of the left spine; pop, then push the right child's spine.",
             "Next-smallest one at a time; merging two BSTs.", "O(1) amortised, O(h) memory",
             "Push the spine of `n.right`, not `n.right` alone."),
        _var("Balanced build", "The middle of a sorted range is the root.",
             "Sorted array → BST; rebalance a degenerate tree.", "O(n)", "Pass indices, not copies."),
        _var("Runs in in-order", "Equal values are adjacent in in-order.",
             "Modes, duplicates, minimum difference.", "O(n), O(h)", "Reset the run on a new value."),
        _var("Trim", "Out of range → return the trimmed child on the in-range side.",
             "Keep only [lo, hi].", "O(n)", "The replacement keeps the ancestors' order."),
    ],
    rewrites=[
        _rw("Range sum: prune, do not visit everything",
            """
int rangeSum(TreeNode n, int lo, int hi) {
    if (n == null) return 0;
    int self = (lo <= n.val && n.val <= hi) ? n.val : 0;
    return self + rangeSum(n.left, lo, hi) + rangeSum(n.right, lo, hi);
}
""",
            """
int rangeSum(TreeNode n, int lo, int hi) {
    if (n == null) return 0;
    if (n.val < lo) return rangeSum(n.right, lo, hi);   // left side all < lo
    if (n.val > hi) return rangeSum(n.left, lo, hi);    // right side all > hi
    return n.val + rangeSum(n.left, lo, hi) + rangeSum(n.right, lo, hi);
}
""",
            "Two early returns that skip a subtree the invariant rules out.",
            """
If n.val < lo, everything in n's left subtree is smaller still — below lo — so skipping it
loses nothing. The work drops from O(n) to O(h + number of nodes in range).
"""),
        _rw("k-th smallest: stop at k",
            """
List<Integer> all = new ArrayList<>();
inorder(root, all);                     // O(n) always
return all.get(k - 1);
""",
            """
Deque<TreeNode> st = new ArrayDeque<>();
for (TreeNode cur = root; ; ) {
    while (cur != null) { st.push(cur); cur = cur.left; }
    cur = st.pop();
    if (--k == 0) return cur.val;
    cur = cur.right;
}
""",
            "Replace collect-then-index with an in-order that counts down and returns.",
            """
In-order visits values in increasing order, so the k-th visit *is* the k-th smallest. Nothing
after it can change the answer: O(h + k) instead of O(n).
"""),
        _rw("Merging two BSTs: merge, do not sort",
            """
List<Integer> all = inorder(a);
all.addAll(inorder(b));
Collections.sort(all);                  // O((n + m) log(n + m))
""",
            """
// two iterators; always advance the smaller head
while (!s1.isEmpty() || !s2.isEmpty()) {
    Deque<TreeNode> s = s2.isEmpty() || (!s1.isEmpty() && s1.peek().val <= s2.peek().val) ? s1 : s2;
    TreeNode n = s.pop();
    out.add(n.val);
    pushLeft(s, n.right);
}
""",
            "Replace the sort with a two-pointer merge of two in-order streams.",
            """
Both in-orders are already sorted. Merging two sorted sequences only ever compares their heads,
and the smaller head is the next value overall — the merge step of merge sort, O(n + m).
"""),
        _rw("Sorted data: build, do not insert",
            """
TreeNode root = null;
for (int v : sorted) root = insert(root, v);    // a chain: O(n²)
""",
            """
TreeNode build(int lo, int hi) {
    if (lo > hi) return null;
    int mid = (lo + hi) >>> 1;
    TreeNode n = new TreeNode(sorted[mid]);
    n.left = build(lo, mid - 1);
    n.right = build(mid + 1, hi);
    return n;
}
""",
            "Choose the root instead of accepting the first value as the root.",
            """
Inserting sorted keys makes each new key the rightmost node: a chain of height n, and n
inserts cost O(n²). The middle-first build produces the same in-order (the same set) with
height ⌈log₂(n + 1)⌉ in O(n).
"""),
    ],
    internals="""
### `TreeMap` is a red-black tree

Java's `TreeMap` and `TreeSet` are **red-black trees**: a BST where every node has a colour bit
and four rules (the root is black, a red node has black children, every root-to-null path has
the same number of black nodes). Those rules cap the height at **2 · log₂(n + 1)** — at most
twice the perfect height — and inserts and deletes restore them with at most a few
**rotations**, each O(1):

```
    x                 y
   / \\     rotate    / \\
  a   y    ─────→    x   c
     / \\    left    / \\
    b   c          a   b
```

A rotation re-parents three subtrees and keeps the in-order sequence `a x b y c` unchanged —
which is why it can rebalance without breaking the BST invariant.

### Why deletion needs the successor

Removing a node with two children leaves two subtrees that both need a parent. Whatever value
fills the hole must be larger than everything on the left and smaller than everything on the
right. Exactly two values qualify: the in-order predecessor (max of the left subtree) and the
in-order **successor** (min of the right subtree). Each sits at the end of a spine, so it has
at most one child and can itself be removed by the easy case.

### Why sorted inserts degenerate

A plain BST's shape is decided by insertion order. Sorted input makes every key the new
maximum, so each goes to the right of the last one — a linked list of height n. Random order
gives expected height about 2.99 · log₂ n; adversarial order gives n. Self-balancing trees
(`TreeMap`) remove the dependence on order, at the price of the colour bit and rotations.

### What the API gives you, and what it costs

| Operation | `TreeMap` | Hand-rolled BST |
| --- | --- | --- |
| `get`, `put`, `remove` | O(log n) guaranteed | O(h) |
| `floorKey`, `ceilingKey`, `higherKey`, `lowerKey` | O(log n) | O(h), one descent |
| `firstKey`, `lastKey`, `pollFirstEntry` | O(log n) | O(h) |
| `headMap`, `tailMap`, `subMap` | O(log n) to create a *view* | — |
| rank ("how many keys < x") | **not supported** | O(h) with subtree sizes |

The last row is the reason to write your own: `TreeMap` cannot say how many keys are below x.
An **order-statistic tree** — a BST storing each subtree's size — can, in O(h).
""",
    build_it="""
### A `BST` class, tested against `TreeSet`

Implement, over `int` keys with no duplicates:

**1. `insert`, `contains`, `delete`** (the three cases, successor for two children).

**2. `floor(x)`, `ceiling(x)`** — one descent each, remembering the best candidate seen.

**3. `rank(x)`** — the number of keys < x, by storing `size` in every node and updating it on
insert and delete.

**4. `kth(k)`** — the k-th smallest, by comparing k with `size(left) + 1` at each node.

**5. An iterator** with `hasNext` / `next`, using a stack of the left spine.

**6. A `main`** that performs 100,000 random operations on both your BST and a `TreeSet`, and
after each one checks that `contains`, `floor`, `ceiling` and a full iteration agree
(`rank` against `headSet(x).size()`). Then run it again with keys inserted in sorted order,
time both, and watch the chain appear.
""",
    skeletons=[
        _sk("Delete with the successor",
            "Removing a key, all three cases.",
            """
TreeNode delete(TreeNode n, int key) {
    if (n == null) return null;
    if (key < n.val) n.left = delete(n.left, key);
    else if (key > n.val) n.right = delete(n.right, key);
    else {
        if (n.left == null) return n.right;
        if (n.right == null) return n.left;
        TreeNode s = n.right;
        while (s.left != null) s = s.left;
        n.val = s.val;
        n.right = delete(n.right, s.val);
    }
    return n;
}
""",
            "Every call returns the new root of its subtree."),
        _sk("Trim to a range",
            "Keep only [lo, hi].",
            """
TreeNode trim(TreeNode n, int lo, int hi) {
    if (n == null) return null;
    if (n.val < lo) return trim(n.right, lo, hi);
    if (n.val > hi) return trim(n.left, lo, hi);
    n.left = trim(n.left, lo, hi);
    n.right = trim(n.right, lo, hi);
    return n;
}
""",
            "An out-of-range node is replaced by its trimmed in-range side."),
        _sk("Balanced build from sorted",
            "Sorted array → height-balanced BST.",
            """
TreeNode build(int[] a, int lo, int hi) {
    if (lo > hi) return null;
    int mid = (lo + hi) >>> 1;
    TreeNode n = new TreeNode(a[mid]);
    n.left = build(a, lo, mid - 1);
    n.right = build(a, mid + 1, hi);
    return n;
}
""",
            "Lower middle: `(lo + hi) >>> 1`."),
    ],
    signals=[
        _sig("“delete a key” from a BST", "Descend, then 0/1/2-child cases",
             "Two children: the in-order successor fills the hole."),
        _sig("“keep only values in [lo, hi]”", "Trim by the invariant",
             "A node out of range condemns one whole subtree."),
        _sig("“sorted array / list → balanced tree”", "Middle-first build",
             "The middle splits the rest evenly."),
        _sig("“most frequent value” / “duplicates” in a BST", "Count runs in in-order",
             "Equal values are adjacent."),
    ],
    costs=[
        _cost("Delete", "O(h)", "O(h) recursive", "One descent plus a successor walk."),
        _cost("Balanced build", "O(n)", "O(log n)", "One node per element."),
        _cost("Merge two BSTs", "O(n + m)", "O(h1 + h2)", "Two iterators."),
    ],
    pitfalls=[
        _pit("Deleting the root does nothing",
             "The function changed a local variable instead of returning the new subtree root.",
             "Return the new root from every call and assign it: `root = delete(root, key)`."),
        _pit("A deleted two-child node's value reappears",
             "The successor's value was copied in, but the successor node itself was not removed.",
             "After copying, delete the successor's value from the right subtree."),
        _pit("Trim keeps a node outside the range",
             "Only the children were checked, not the node itself before recursing.",
             "Test the node first: out of range means it is replaced, not kept."),
    ],
    checks=[
        _chk("Which two values can replace a deleted node with two children, and why those?",
             "Its in-order predecessor or successor — the only values larger than everything "
             "left of it and smaller than everything right of it (or vice versa)."),
        _chk("Why does the successor never have a left child?",
             "It is the leftmost node of the right subtree; a left child would be smaller and "
             "further left."),
        _chk("What does `TreeMap` not support that a size-augmented BST does?",
             "Rank queries — how many keys are below x — and selecting the k-th key in O(log n)."),
    ],
    traces=[_t6_bst_delete(), _t6_sorted_build()],
)


_D6_BACKTRACK = dict(
    invariant=_inv(
        "On entry to `dfs`, the shared state (the `path`, the `used[]` flags, the bucket "
        "loads, the grid marks) holds **exactly the choices on the path from the search "
        "tree's root to this call** — nothing more, nothing less.",
        "The first call is the root of the search tree: no choices made, and the state is "
        "empty (or the unmodified input).",
        "Before each recursive call, `apply` adds one choice, so the child's state is the "
        "parent's plus that choice — the child's root path. After the call returns, `undo` "
        "removes exactly that choice, so the parent's state is restored before the next "
        "choice is tried. `apply` and `undo` must be exact mirrors for this to hold.",
        "When the search returns to the root, the state is back to empty — and every leaf was "
        "reached with the state equal to its own root path, so every recorded answer is correct.",
        "Every classic bug violates this sentence: a missing undo leaks a finished branch's "
        "choice into its siblings; storing a reference to `path` records a state that is later "
        "changed; restoring a grid cell only on the failure path leaves marks behind on success.",
    ),
    variants=[
        _var("Subsets", "Loop from `start`; recurse with `i + 1`.", "All subsets; subset sums.",
             "O(2ⁿ · n)", "Record at every node, not only at leaves."),
        _var("k-combinations", "Subsets, plus stop at size k.", "Choose k of n.",
             "O(C(n, k) · k)", "Prune when fewer than k − size items remain."),
        _var("Permutations", "Loop over every index; skip `used[i]`.", "Orderings.",
             "O(n! · n)", "Undo both the flag and the list."),
        _var("Combination sum (reuse)", "Recurse with `i`, not `i + 1`.", "Coin combinations, sums with repetition.",
             "Exponential in target / min", "Sort to `break` early."),
        _var("Dedup by sort + skip", "`if (i > start && a[i] == a[i-1]) continue;`",
             "Inputs with repeated values, distinct answers.", "Fewer branches", "Only at the same depth."),
        _var("Grid mark / unmark", "Overwrite the cell; restore on every return.",
             "Word search, simple paths on a grid.", "O(r · c · 3ᴸ)", "Restore on the success path too."),
        _var("Constraint placement", "Check feasibility before placing (queens, colours).",
             "N-queens, Sudoku, graph colouring.", "Pruned exponential", "Make the check O(1) with sets."),
        _var("Partition into k buckets", "Place each item into a bucket; skip equal loads.",
             "Equal-sum split, job assignment.", "O(kⁿ) worst, far less pruned", "Largest items first."),
        _var("Split a string", "Choose where the next piece ends.",
             "Palindrome partitions, IP addresses, word break.", "O(2ⁿ⁻¹ · n)", "Prune with a feasibility table."),
        _var("Operators between digits", "Choose the next operand's end and its operator; carry (value, last).",
             "Expression targets.", "O(4ⁿ⁻¹)", "No leading zeros; use long."),
        _var("Count instead of list", "Return a number; no path to copy.",
             "\"How many ways\" — and a hint that DP might apply.", "Same tree, less output", "Memoise if states repeat."),
    ],
    rewrites=[
        _rw("Prune on the partial, not on the finished answer",
            """
void dfs(int i, int sum) {
    if (i == n) { if (sum == target) count++; return; }   // checks only at leaves
    dfs(i + 1, sum + a[i]);
    dfs(i + 1, sum);
}
""",
            """
Arrays.sort(a);                                    // positive values
void dfs(int start, int rem) {
    if (rem == 0) { count++; return; }
    for (int i = start; i < n; i++) {
        if (a[i] > rem) break;                     // nothing later can fit
        dfs(i + 1, rem - a[i]);
    }
}
""",
            "Check the constraint before descending, and sort so the check can `break`.",
            """
With positive values, once a[i] exceeds what remains, so does every a[j] for j > i — that
whole suffix of choices can only overshoot. Cutting there removes branches that could never
reach a leaf equal to the target; no answer lives below them.
"""),
        _rw("Conflicts in O(1): sets, not scans",
            """
boolean safe(int row, int col) {
    for (int r = 0; r < row; r++)               // O(n) per placement
        if (queen[r] == col || Math.abs(queen[r] - col) == row - r) return false;
    return true;
}
""",
            """
boolean[] cols = new boolean[n], diag = new boolean[2 * n], anti = new boolean[2 * n];
boolean safe(int row, int col) {                 // O(1)
    return !cols[col] && !diag[row - col + n] && !anti[row + col];
}
// apply: set all three; undo: clear all three
""",
            "Replace the scan over placed queens with three occupancy arrays.",
            """
A diagonal is a line where row − col (or row + col) is constant, so \"is this diagonal taken?\"
is one array lookup. The arrays must be set in `apply` and cleared in `undo` — they are part of
the shared state the invariant talks about.
"""),
        _rw("k buckets: never try two interchangeable buckets",
            """
for (int b = 0; b < k; b++) {
    if (load[b] + a[i] > t) continue;
    load[b] += a[i];
    if (place(i + 1)) return true;
    load[b] -= a[i];
}
""",
            """
for (int b = 0; b < k; b++) {
    if (load[b] + a[i] > t) continue;
    if (b > 0 && load[b] == load[b - 1]) continue;   // same situation as bucket b-1
    load[b] += a[i];
    if (place(i + 1)) return true;
    load[b] -= a[i];
    if (load[b] == 0) break;                          // an empty bucket failed
}
""",
            "Skip a bucket whose load equals the previous bucket's.",
            """
Buckets are unlabelled: putting the item in bucket 3 or bucket 5 when both hold the same load
leads to the same sub-search with the labels swapped. Exploring one of them loses no answer —
and removes up to k! duplicate copies of every partial assignment.
"""),
        _rw("Listing splits: prune dead suffixes first",
            """
void dfs(int i) {                          // explores every prefix, even hopeless ones
    if (i == n) { out.add(join(path)); return; }
    for (String w : dict) if (s.startsWith(w, i)) { push(w); dfs(i + w.length()); pop(); }
}
""",
            """
// ok[i] = the suffix from i can be split (right-to-left DP)
void dfs(int i) {
    if (i == n) { out.add(join(path)); return; }
    for (String w : dict)
        if (s.startsWith(w, i) && ok[i + w.length()]) { push(w); dfs(i + w.length()); pop(); }
}
""",
            "Add `&& ok[i + w.length()]` — descend only where a sentence can still be finished.",
            """
A branch whose remaining suffix cannot be split produces no sentence, however deep it goes.
The DP identifies those suffixes in O(n · d · L) up front, so every call the search makes
leads to at least one output — the search becomes output-bound.
"""),
    ],
    internals="""
### The recursion tree is the cost

Backtracking's running time is the **size of its search tree** — the number of calls — times
the work per call. The shapes to know:

| Search | Leaves | Why |
| --- | --- | --- |
| subsets of n | 2ⁿ | two choices per element |
| k-combinations | C(n, k) | subsets of size k only |
| permutations | n! | n, then n − 1, then … choices |
| combination sum | depends on target / smallest | reuse lets depth reach target / min |
| k-colouring n regions | ≤ kⁿ | pruned by borders |

Internal nodes add at most a constant factor for subsets (a full binary tree has one fewer
internal node than leaves) and about e · n! for permutations. **Pruning** removes whole
subtrees, so its value is measured in *leaves not visited* — which is why a check that runs
before the recursive call is worth far more than the same check at the leaf.

### Stack depth

The recursion is as deep as the number of decisions — n for subsets and permutations, the
string length for splits. That is small in every backtracking problem (n ≤ 20 is the tell),
so unlike tree recursion, `StackOverflowError` is not the risk here. The risk is time.

### Where the `· n` comes from

Recording an answer copies the current path: `new ArrayList<>(path)` or a joined string is
O(length). Across 2ⁿ subsets that is O(2ⁿ · n) — and it is unavoidable when the output itself
has that size. Counting instead of listing drops the factor, and if different branches reach
the same state (same index, same remaining sum), memoising the count turns the search into a DP.

### Shared state versus copies

Passing a *new* list to each call (`dfs(i + 1, path + [x])`) needs no undo, but allocates at
every node — O(n) per call. One shared, mutated list with an exact undo costs O(1) per call
and O(n) memory in total. The shared version is the standard; the copying version is easier to
get right, and fine when n is tiny.
""",
    build_it="""
### A generic `Search` harness

Write one recursive engine and plug in the variants:

```java
interface Problem {
    boolean complete(State s);
    List<Choice> choices(State s);         // already filtered by feasibility
    void apply(State s, Choice c);
    void undo(State s, Choice c);
    void record(State s);
}
```

**1. Subsets, k-combinations, permutations** as three `Problem`s over the same engine.
Properties: 2ⁿ, C(n, k) and n! answers; all distinct; each answer valid.

**2. Combination sum with reuse.** Property: equals a coin-change DP count for 200 random
(candidates, target) pairs.

**3. A call counter** in the engine. Print calls with and without the sorted `break` for
combination sum, and with and without symmetry breaking for k-bucket partition — the numbers
are the lesson.

**4. N-queens counts for n = 1…10** (1, 0, 0, 2, 10, 4, 40, 92, 352, 724) as a regression test.

**5. Break it deliberately**: delete one `undo`, run the property tests, and read the failure —
it is always an answer containing a choice from a branch that already finished.
""",
    skeletons=[
        _sk("Partition into k equal buckets",
            "Equal-sum split, fair assignment.",
            """
boolean place(int i) {                          // items sorted descending
    if (i == n) return true;
    for (int b = 0; b < k; b++) {
        if (load[b] + a[i] > target) continue;
        if (b > 0 && load[b] == load[b - 1]) continue;
        load[b] += a[i];
        if (place(i + 1)) return true;
        load[b] -= a[i];
        if (load[b] == 0) break;
    }
    return false;
}
""",
            "Check total % k and max ≤ target before starting."),
        _sk("Operators between digits",
            "Count or list expressions reaching a target.",
            """
long count(int i, long value, long last) {
    if (i == n) return value == target ? 1 : 0;
    long ways = 0, x = 0;
    for (int j = i; j < n; j++) {
        if (j > i && s.charAt(i) == '0') break;
        x = x * 10 + (s.charAt(j) - '0');
        if (i == 0) ways += count(j + 1, x, x);
        else ways += count(j + 1, value + x, x) + count(j + 1, value - x, -x)
                   + count(j + 1, value - last + last * x, last * x);
    }
    return ways;
}
""",
            "`last` is what `*` must take back out."),
        _sk("Constraint colouring",
            "Graph colouring, scheduling into slots.",
            """
long count(int i) {
    if (i == n) return 1;
    long ways = 0;
    for (int c = 0; c < k; c++) {
        boolean ok = true;
        for (int j : adj[i]) if (j < i && colour[j] == c) { ok = false; break; }
        if (!ok) continue;
        colour[i] = c;
        ways += count(i + 1);
    }
    return ways;
}
""",
            "Only already-coloured neighbours constrain the choice."),
    ],
    signals=[
        _sig("“split into k groups with equal sum”", "k-bucket backtracking with symmetry pruning",
             "n ≤ 16 says exponential is expected; a bitmask DP also fits."),
        _sig("“insert + − × between digits”", "Operand-end recursion carrying (value, last)",
             "Precedence handled by undoing the last term."),
        _sig("“list all ways to segment”", "Backtracking pruned by a word-break DP",
             "The DP says which suffixes are dead."),
        _sig("“colour so that no neighbours match”", "Constraint backtracking",
             "Check only already-assigned neighbours."),
    ],
    costs=[
        _cost("k-bucket partition", "O(kⁿ) worst", "O(n + k)", "Symmetry pruning cuts it drastically."),
        _cost("Operators between digits", "O(4ⁿ⁻¹)", "O(n)", "Three operators or glue at each gap."),
        _cost("Listing splits with a DP prune", "O(n · d · L + output)", "O(n)", "Output-bound."),
    ],
    pitfalls=[
        _pit("k-bucket search times out on 16 items",
             "Equal buckets were each tried, so every partial answer was explored k! times.",
             "Skip a bucket whose load equals the previous one, and break after an empty one fails."),
        _pit("An expression count includes `05`",
             "Multi-digit operands starting with 0 were allowed.",
             "Break the operand loop when j > i and s[i] == '0'."),
        _pit("`2 + 3 * 4` evaluated as 20",
             "The running value was multiplied instead of undoing the last term.",
             "value − last + last · x, and the new last is last · x."),
    ],
    checks=[
        _chk("Why may the k-bucket search skip a bucket whose load equals the previous bucket's?",
             "Buckets are unlabelled; placing the item in either leads to the same sub-search "
             "with two labels swapped, so exploring one loses nothing."),
        _chk("In the operator search, what is `last` for?",
             "The value of the last term added. `*` binds tighter, so it must be subtracted out "
             "and replaced by last · x."),
        _chk("What does a precomputed `ok[i]` table buy a sentence-listing search?",
             "Every branch it enters can still finish, so no time is spent on prefixes that "
             "produce no sentence — the search becomes proportional to its output."),
    ],
    traces=[_t6_combo_sum(), _t6_buckets()],
)


_D6_GRAPH = dict(
    invariant=_inv(
        "BFS from s: **the queue holds vertices in non-decreasing order of distance, and the "
        "distances in it differ by at most one**; every vertex marked so far has its final "
        "distance.",
        "At the start the queue is [s] with dist 0, and s's distance is final — nothing is "
        "closer than 0 steps.",
        "Pop u at distance d (the smallest in the queue). Every unmarked neighbour v gets "
        "d + 1 and goes to the back. The queue held only d and d + 1, so appending d + 1 keeps "
        "it sorted with a spread of one. And d + 1 is v's true distance: a shorter path would "
        "pass through a vertex at distance < d, which was popped earlier and would already have "
        "marked v.",
        "When the queue empties, every vertex reachable from s is marked with its shortest "
        "distance, and every unmarked vertex is unreachable.",
        "For DFS the invariant is about colours instead: a vertex is grey exactly while it is "
        "on the recursion stack. That is why a grey neighbour means a cycle in a directed graph.",
    ),
    variants=[
        _var("Adjacency-list BFS", "Queue, dist[] = −1 as the visited set.",
             "Shortest hops, reachability.", "O(V + E)", "Mark on push."),
        _var("Grid BFS / DFS", "Neighbours are four offsets; bounds before access.",
             "Islands, flood fill, mazes.", "O(r · c)", "Flatten (i, j) to i · c + j if you store it."),
        _var("Multi-source BFS", "Seed the queue with every source at distance 0.",
             "Rotting, distance to nearest X.", "O(V + E)", "Mark all sources before the loop."),
        _var("Components by DFS", "Outer loop over vertices; one DFS per unvisited one.",
             "Count / label components, sizes.", "O(V + E)", "Iterative on big grids."),
        _var("Two-colouring", "Colour a neighbour the opposite colour; a clash is an odd cycle.",
             "Bipartite check.", "O(V + E)", "Every component, not just one."),
        _var("Three-colour DFS", "White / grey / black; a grey neighbour is a back edge.",
             "Cycle in a directed graph.", "O(V + E)", "Two states are not enough when directed."),
        _var("Augmented-state BFS", "State = (vertex, extra) — keys, walls broken, fuel.",
             "Keys and doors, k obstacles, parity.", "O(V · |extra|)", "Visited is over states."),
        _var("Implicit-graph BFS", "Generate neighbours by a rule when popping.",
             "Board games, lock wheels, word ladders.", "O(states · moves)", "Build nothing up front."),
        _var("Level-by-level BFS", "Drain `size` items per round.",
             "\"Minutes until\", layers, step counts.", "O(V + E)", "Snapshot the size."),
        _var("Bidirectional BFS", "Expand the smaller frontier from both ends.",
             "Huge implicit graphs with one target.", "≈ O(b^(d/2))", "Stop when the frontiers meet."),
        _var("Clone with a map", "old → new map doubles as the visited set.",
             "Copy a graph with cycles.", "O(V + E)", "Create before recursing."),
    ],
    rewrites=[
        _rw("Mark on push, not on pop",
            """
q.add(s);
while (!q.isEmpty()) {
    int u = q.poll();
    if (seen[u]) continue;          // duplicates were queued
    seen[u] = true;
    for (int v : adj[u]) if (!seen[v]) q.add(v);
}
""",
            """
seen[s] = true;
q.add(s);
while (!q.isEmpty()) {
    int u = q.poll();
    for (int v : adj[u])
        if (!seen[v]) { seen[v] = true; q.add(v); }
}
""",
            "Move `seen[v] = true` to the moment v is discovered.",
            """
A vertex's distance is decided when it is first discovered (the invariant), so marking then
loses nothing. It stops the same vertex being queued once per incoming edge, keeping the
queue at O(V) instead of O(E).
"""),
        _rw("Nearest source: one BFS, not one per source",
            """
for (int s : sources) {                         // k BFS runs
    int[] d = bfs(s);
    for (int v = 0; v < n; v++) best[v] = Math.min(best[v], d[v]);
}
""",
            """
Arrays.fill(dist, -1);
for (int s : sources) { dist[s] = 0; q.add(s); }  // all at distance 0
// ... one ordinary BFS
""",
            "Seed the queue with every source.",
            """
It is BFS from a virtual vertex joined to every source by a free edge. The queue's order
invariant still holds (every source is at 0), so each vertex is first reached from its
nearest source: O(V + E) instead of O(k · (V + E)).
"""),
        _rw("When the cell is not enough: widen the state",
            """
boolean[][] seen = new boolean[R][C];            // wrong: ignores keys held
// a cell visited without key a can never be revisited holding it
""",
            """
boolean[][][] seen = new boolean[R][C][1 << K];  // (cell, keys) states
if (!seen[nr][nc][mask]) { seen[nr][nc][mask] = true; q.add(new int[]{nr, nc, mask}); }
""",
            "Add the extra information to the visited set.",
            """
BFS is correct when \"first time this state is reached\" means \"reached optimally\". Two
arrivals at one cell with different keys have different futures, so they must be different
states. The cost grows by the number of values of the extra field.
"""),
        _rw("Adjacency matrix → adjacency list",
            """
for (int u = 0; u < V; u++)                     // O(V²) regardless of E
    for (int v = 0; v < V; v++)
        if (matrix[u][v]) visit(u, v);
""",
            """
List<Integer>[] adj = new List[V];
for (int[] e : edges) adj[e[0]].add(e[1]);      // O(V + E) to build and walk
for (int u = 0; u < V; u++)
    for (int v : adj[u]) visit(u, v);
""",
            "Store only the edges that exist.",
            """
A sparse graph (E ≈ V) spends almost all of the O(V²) scan reading zeros. The list holds
exactly the E edges, so any traversal becomes O(V + E) — the difference between 10¹⁰ and
2 · 10⁵ at V = 10⁵.
"""),
    ],
    internals="""
### Three ways to store a graph

| Layout | Memory | "Neighbours of u" | "Is u–v an edge?" | Use when |
| --- | --- | --- | --- | --- |
| Adjacency matrix `boolean[V][V]` | V² | O(V) | O(1) | V ≤ ~2000, dense |
| Adjacency list `List<Integer>[]` | V + E objects | O(deg) | O(deg) | the default |
| CSR arrays `start[V + 1]`, `to[E]` | V + E ints | O(deg), contiguous | O(deg) | 10⁶ edges, speed matters |

**CSR** (compressed sparse row) is the list with the objects removed: count degrees, prefix-sum
them into `start[]`, then fill `to[]` so u's neighbours are `to[start[u] .. start[u+1])`. No
`Integer` boxing, one allocation, cache-friendly — the difference between a traversal that
fits the time limit at 10⁶ edges and one that does not.

### `ArrayDeque`, not `LinkedList`

`ArrayDeque` is a circular array: `add` and `poll` are O(1) amortised with no per-element
allocation. `LinkedList` allocates a node per element and chases pointers. Both are
`Queue`s; use `ArrayDeque` — except that it **rejects `null`**, which matters only if you ever
queue nulls (tree serialisation does, graph traversal does not).

### Recursion depth on grids

A DFS flood fill on a 1000 × 1000 grid can recurse 10⁶ deep along a snake-shaped region —
far past the default thread stack. Either use BFS (a queue has no depth), an explicit stack,
or run the solver in a thread with a bigger stack:
`new Thread(null, task, "main", 1 << 28).start()`.

### Why BFS finds shortest paths and DFS does not

BFS explores in rings of equal distance, so the first time it reaches a vertex is along a
shortest path. DFS dives down one branch; the first path it finds to a vertex is simply the
first one in adjacency order, which may be long. DFS is for *structure* (components, cycles,
orderings); BFS is for *distance* in unweighted graphs.
""",
    build_it="""
### A `Graph` class

**1. Build both layouts** from an edge list: `List<Integer>[]` and CSR (`start[]`, `to[]`).
Property: for every vertex, the two neighbour lists are the same multiset.

**2. `bfs(src)` → `int[] dist`** (−1 unreachable), and **`multiBfs(int[] srcs)`**.
Property: `multiBfs` equals the element-wise minimum of single BFS runs.

**3. `components()` → labels**, iterative DFS. Property: u and v share a label iff
`bfs(u)[v] ≥ 0` (undirected graphs).

**4. `bipartite()`** → a colouring or null. Property: agrees with a brute force over all
2ⁿ colourings for n ≤ 12.

**5. `hasCycleDirected()`** with three colours. Property: agrees with "Kahn's algorithm outputs
fewer than V vertices".

**6. A timing test**: 10⁶ edges, list vs CSR, and a recursive vs iterative DFS on a 1000 × 1000
snake grid (catch the `StackOverflowError`).
""",
    skeletons=[
        _sk("BFS over augmented states",
            "Keys and doors, walls to break, parity of steps.",
            """
boolean[][][] seen = new boolean[R][C][EXTRA];
q.add(new int[]{sr, sc, 0});
seen[sr][sc][0] = true;
for (int steps = 0; !q.isEmpty(); steps++)
    for (int size = q.size(); size-- > 0; ) {
        int[] s = q.poll();
        if (isGoal(s)) return steps;
        for (int[] d : DIRS) {
            int nr = s[0] + d[0], nc = s[1] + d[1];
            if (!inside(nr, nc) || blocked(nr, nc, s[2])) continue;
            int nx = nextExtra(nr, nc, s[2]);
            if (!seen[nr][nc][nx]) { seen[nr][nc][nx] = true; q.add(new int[]{nr, nc, nx}); }
        }
    }
return -1;
""",
            "The goal may be a condition on the extra field (all keys held)."),
        _sk("BFS on an implicit graph",
            "Board games, locks, puzzles: neighbours by rule.",
            """
dist[start] = 0;
q.add(start);
while (!q.isEmpty()) {
    int s = q.poll();
    for (int t : moves(s))                  // generated, not stored
        if (dist[t] == -1) { dist[t] = dist[s] + 1; q.add(t); }
}
""",
            "Encode states as ints so dist[] can be an array."),
    ],
    signals=[
        _sig("“keys and doors”, “at most k walls”, “with fuel f”", "BFS over (cell, extra)",
             "The same cell with different extra is a different state."),
        _sig("“fewest turns / moves / rolls” in a game", "BFS on the implicit graph",
             "Every move costs one."),
        _sig("“distance of every vertex from s”", "One BFS, print dist[]",
             "−1 as unvisited doubles as the visited set."),
    ],
    costs=[
        _cost("Augmented-state BFS", "O(V · X)", "O(V · X)", "X = values of the extra field."),
        _cost("Implicit board BFS", "O(n · moves)", "O(n)", "Each square once."),
    ],
    pitfalls=[
        _pit("The walker never goes back through a cell after picking up a key",
             "The visited set was per cell, not per (cell, keys).",
             "Mark `seen[r][c][mask]`."),
        _pit("A game BFS lands on a ladder's foot and stays there",
             "The shortcut was not applied before marking the square.",
             "Resolve the jump first; mark and enqueue the square you end up on."),
        _pit("A direct walk is ignored when k is large",
             "Nothing special — but the state space is huge and the run is slow.",
             "If k ≥ r + c − 2, the Manhattan path is always possible: return it."),
    ],
    checks=[
        _chk("When must a BFS state include more than the vertex?",
             "When two arrivals at the same vertex can have different futures — different keys "
             "held, walls left, fuel — so reaching it first is not reaching it best."),
        _chk("Why is marking on push enough to guarantee each vertex's distance is right?",
             "BFS discovers vertices in non-decreasing distance order, so the first discovery "
             "is along a shortest path; later discoveries can only be as long or longer."),
        _chk("What does a grey neighbour mean during a directed DFS?",
             "It is on the current recursion stack, so the edge closes a cycle (a back edge)."),
    ],
    traces=[_t6_dfs_times(), _t6_state_bfs()],
)
