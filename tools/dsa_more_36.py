# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 36 — the syllabus roadmap, stages 5–6: copying, building, walking.
#
#   copy-list-random-pointer     old → new node map, or weave the copies in
#   flatten-multilevel-list      splice each child list in, before the rest
#   build-tree-preorder-inorder  the preorder names the root; the inorder splits it
#   serialize-tree-preorder      preorder with an explicit marker for every null
#   deserialize-tree-preorder    the same walk, reading instead of writing
#   bst-iterator                 in-order traversal, paused between calls
#   floor-ceiling-queries        an ordered set answers "nearest at or below/above"
#   nearby-almost-duplicate      a sliding window kept as an ordered set
#   clone-graph                  a traversal whose visited set is the old → new map
#   prim-dense-graph             Prim on a complete graph: O(V²), no heap needed
#   mst-critical-edges           exclude an edge, force an edge, compare the weight
#   floyd-warshall-queries       all pairs at once, through every intermediate k
# ===========================================================================

_p(
    "copy-list-random-pointer", "Copy a List with Random Pointers", "Medium",
    topics=["Linked Lists", "Hashing"], subtopics=["Deep Copy", "Pointer Mapping"], companies=["Amazon", "Microsoft", "Bloomberg"],
    shape="random_list", ret="Node", todo="map every original node to a new node, then set each copy's next and random through the map",
    description=(
        "Each node of a singly linked list has a `next` pointer and a `random` pointer, which may "
        "point at any node of the list or be `null`. Return a **deep copy**: new nodes, with the "
        "copies' `next` and `random` pointing at copies, never at the original nodes.\n\n"
        "### Input\nLine 1: `n`.\nNext `n` lines: `val random` — node `i`'s value, and the index "
        "its `random` points at (`-1` for null). Node `i`'s `next` is node `i + 1`.\n\n"
        "### Output\nThe starter prints your copy in the same format, one node per line (`EMPTY` "
        "for an empty list). If your copy shares any node with the original it prints `SHARED`; if "
        "a copy's `random` leads back into the original it prints `RANDOM OUTSIDE COPY`."
    ),
    constraints="0 ≤ n ≤ 1000\n-10^4 ≤ val ≤ 10^4",
    hints=[
        "Copying the `next` chain is easy. The problem is `random`: when you create a node's copy, the copy of its random target may not exist yet.",
        "Separate the two jobs. First pass: create every copy and remember `original → copy` in a map. Second pass: every pointer is now one lookup.",
        "For O(1) extra space, weave each copy directly after its original (A → A' → B → B'). Then `A'.random = A.random.next`, and a final pass unweaves the two lists.",
    ],
    opt=("O(n)", "O(n)", "Two passes with an original → copy map. Weaving the copies into the list makes it O(1) extra space."),
    editorial=(
        "## The one thing this teaches\n**When a copy's pointers can refer forwards, create first "
        "and link second.** A map from each original node to its copy turns every pointer — `next` "
        "or `random` — into a single lookup, regardless of whether its target has been visited.\n\n"
        "## Approach\n```java\nMap<Node, Node> copy = new HashMap<>();\n"
        "for (Node p = head; p != null; p = p.next) copy.put(p, new Node(p.val));\n"
        "for (Node p = head; p != null; p = p.next) {\n    Node c = copy.get(p);\n"
        "    c.next = copy.get(p.next);        // get(null) is null: the tail needs no special case\n"
        "    c.random = copy.get(p.random);\n}\nreturn copy.get(head);\n```\n\n"
        "## The O(1)-space version\nWeave each copy in right after its original, so the map is the "
        "list itself: the copy of `x` is `x.next`. Set `x.next.random = x.random.next`, then unweave. "
        "Restoring the original's `next` pointers is part of the job.\n\n"
        "## The same idea elsewhere\nCloning a graph is this with a traversal: the visited set *is* "
        "the old → new map."
    ),
    py='''
def solve(head):
    if head is None:
        return None
    copy = {}
    p = head
    while p is not None:
        copy[id(p)] = Node(p.val)
        p = p.next
    p = head
    while p is not None:
        c = copy[id(p)]
        c.next = copy[id(p.next)] if p.next is not None else None
        c.random = copy[id(p.random)] if p.random is not None else None
        p = p.next
    return copy[id(head)]
''',
    java='''
    static Node solve(Node head) {
        if (head == null) return null;
        for (Node p = head; p != null; p = p.next.next) {     // weave: A -> A' -> B -> B'
            Node c = new Node(p.val);
            c.next = p.next;
            p.next = c;
        }
        for (Node p = head; p != null; p = p.next.next)
            p.next.random = p.random == null ? null : p.random.next;
        Node copyHead = head.next;
        for (Node p = head; p != null; p = p.next) {           // unweave both lists
            Node c = p.next;
            p.next = c.next;
            c.next = c.next == null ? null : c.next.next;
        }
        return copyHead;
    }
''',
    examples=[("Example 1", "3\n4 -1\n9 0\n6 2\n"), ("Example 2", "0\n")],
    hidden=[
        ("Single node pointing at itself", "1\n5 0\n"),
        ("Randoms pointing forwards", "4\n1 3\n2 2\n3 3\n4 -1\n"),
        ("Everything points at the head", "5\n9 0\n8 0\n7 0\n6 0\n5 0\n"),
        ("Duplicate values", "4\n1 1\n1 0\n1 3\n1 2\n"),
    ],
    expl=[
        "Node 1's random is node 0 and node 2's is itself; the copy has the same shape on new nodes.",
        "An empty list copies to an empty list.",
    ],
    prereqs=[
        ("list_basics", "Walking and relinking `next` pointers."),
        ("hashing", "A map from each original node to its copy."),
    ],
)

_p(
    "flatten-multilevel-list", "Flatten a Multilevel List", "Medium",
    topics=["Linked Lists"], subtopics=["Pointer Manipulation", "Depth-First Search"], companies=["Meta", "Bloomberg"],
    shape="multilevel", ret="Node", todo="walk the list; at a node with a child, splice the (flattened) child list in between the node and its next",
    description=(
        "A doubly linked list's nodes may also have a `child` pointer to the head of another doubly "
        "linked list, whose nodes may have children too. Flatten it **in place** into one doubly "
        "linked list: each child list goes immediately after its parent node and before the "
        "parent's `next`. Every `child` must end up `null`.\n\n"
        "### Input\nLine 1: `n`.\nNext `n` lines: `val next child` — node `i`'s value and the "
        "indices of its `next` and `child` (`-1` for none). Node 0 is the head; `prev` pointers "
        "follow from the `next` links.\n\n"
        "### Output\nThe starter prints the flattened values in order. It prints `CHILD LEFT AT v` "
        "if a node still has a child, or `BAD PREV AT v` if a `prev` pointer is wrong."
    ),
    constraints="0 ≤ n ≤ 1000\nEvery node belongs to exactly one level list",
    hints=[
        "Draw it with three levels. The order you want is a depth-first walk: a node, then everything below it, then its next.",
        "Splicing a child list in needs its **tail**: parent → child head … child tail → parent's old next.",
        "Recursion that returns the tail of the flattened list gives you both at once. Or keep a stack of the `next` nodes you still owe.",
    ],
    opt=("O(n)", "O(depth)", "Each node is visited once; recursion (or an explicit stack) holds one frame per level."),
    editorial=(
        "## The one thing this teaches\n**A splice needs both ends.** Inserting a list between two "
        "nodes updates four pointers, and two of them live at the inserted list's tail. Have the "
        "recursive flatten return that tail, and each splice becomes constant work.\n\n"
        "## Approach\n```java\n// Flattens the list starting at h, in place; returns its last node.\n"
        "static Node flatten(Node h) {\n    Node p = h, last = h;\n    while (p != null) {\n"
        "        Node next = p.next;\n        if (p.child != null) {\n"
        "            Node tail = flatten(p.child);\n"
        "            p.next = p.child;  p.child.prev = p;  p.child = null;\n"
        "            tail.next = next;  if (next != null) next.prev = tail;\n"
        "            last = tail;\n        } else {\n            last = p;\n        }\n"
        "        p = next;\n    }\n    return last;\n}\n```\n\n"
        "## The three pointers people forget\n- `child.prev = p` — the child head's `prev` was null.\n"
        "- `p.child = null` — a flattened list with children left over is not flat.\n"
        "- `next.prev = tail` — the old next now follows the child tail, not `p`."
    ),
    py='''
def solve(head):
    stack = []
    p = head
    while p is not None:
        if p.child is not None:
            if p.next is not None:
                stack.append(p.next)
            p.next = p.child
            p.child.prev = p
            p.child = None
        if p.next is None and stack:
            nxt = stack.pop()
            p.next = nxt
            nxt.prev = p
        p = p.next
    return head
''',
    java='''
    static Node solve(Node head) {
        flatten(head);
        return head;
    }

    static Node flatten(Node h) {
        Node p = h, last = h;
        while (p != null) {
            Node next = p.next;
            if (p.child != null) {
                Node tail = flatten(p.child);
                p.next = p.child;
                p.child.prev = p;
                p.child = null;
                tail.next = next;
                if (next != null) next.prev = tail;
                last = tail;
            } else {
                last = p;
            }
            p = next;
        }
        return last;
    }
''',
    examples=[
        ("Example 1", "7\n1 1 -1\n2 2 4\n3 3 -1\n4 -1 -1\n5 5 -1\n6 -1 6\n7 -1 -1\n"),
        ("Example 2", "0\n"),
    ],
    hidden=[
        ("No children", "3\n10 1 -1\n20 2 -1\n30 -1 -1\n"),
        ("Child on the last node", "3\n1 1 -1\n2 -1 2\n3 -1 -1\n"),
        ("Child on the head, three levels deep", "4\n1 -1 1\n2 -1 2\n3 -1 3\n4 -1 -1\n"),
        ("Two children on one level", "6\n1 1 3\n2 2 -1\n3 -1 4\n8 -1 -1\n9 5 -1\n10 -1 -1\n"),
    ],
    expl=[
        "Level one is 1 2 3 4; node 2's child list is 5 6, and node 6's child is 7. Flattened: 1 2 5 6 7 3 4.",
        "An empty list.",
    ],
    prereqs=[
        ("list_basics", "Relinking `next` and `prev` without losing the rest of the list."),
        ("recursion", "A recursive call that returns the tail of what it flattened."),
    ],
)

_p(
    "build-tree-preorder-inorder", "Build a Tree from Preorder and Inorder", "Medium",
    topics=["Trees", "Hashing"], subtopics=["Tree Construction", "Divide and Conquer"], companies=["Amazon", "Microsoft", "Google"],
    shape="two_orders", ret="TreeNode", todo="the next preorder value is the root; its inorder position splits the range into left and right subtrees",
    description=(
        "A binary tree with **distinct** values was walked twice. Rebuild it from its preorder and "
        "inorder sequences.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: the preorder (`n` values).\nLine 3: the inorder (`n` values).\n\n"
        "### Output\nThe starter prints the rebuilt tree in level order, `null` for a missing child, "
        "with trailing `null`s removed."
    ),
    constraints="1 ≤ n ≤ 3000\nValues are distinct",
    hints=[
        "The first preorder value is the root. Where is it in the inorder?",
        "Everything left of the root in the inorder is the left subtree; everything right is the right subtree. The sizes tell you how to split the preorder too.",
        "A map from value to inorder index makes each split O(1). Consume the preorder with one shared index: root, then all of the left subtree, then the right.",
    ],
    opt=("O(n)", "O(n)", "A value → inorder-index map, and one shared pointer into the preorder."),
    editorial=(
        "## The one thing this teaches\n**Each traversal tells you something different.** Preorder "
        "tells you *which* node is the root; inorder tells you *what is on each side* of it. Neither "
        "alone determines the tree; together, with distinct values, they do.\n\n"
        "## Approach\n```java\nint preIdx = 0;\nMap<Integer, Integer> pos = new HashMap<>();   // value -> inorder index\n\n"
        "TreeNode build(int[] pre, int lo, int hi) {          // inorder range [lo, hi]\n"
        "    if (lo > hi) return null;\n    TreeNode root = new TreeNode(pre[preIdx++]);\n"
        "    int m = pos.get(root.val);\n    root.left = build(pre, lo, m - 1);   // left first: preorder order\n"
        "    root.right = build(pre, m + 1, hi);\n    return root;\n}\n```\n\n"
        "## Why left must be built first\nThe shared preorder index moves root → left subtree → "
        "right subtree. Building the right side first reads the left subtree's values as if they "
        "were the right's.\n\n"
        "## The slow version\nSearching the inorder for each root instead of using a map is O(n²) "
        "on a skewed tree."
    ),
    py='''
def solve(pre, ino):
    pos = {v: i for i, v in enumerate(ino)}
    idx = 0

    def build(lo, hi):
        nonlocal idx
        if lo > hi:
            return None
        node = TreeNode(pre[idx])
        idx += 1
        m = pos[node.val]
        node.left = build(lo, m - 1)
        node.right = build(m + 1, hi)
        return node

    return build(0, len(ino) - 1)
''',
    java='''
    static TreeNode solve(int[] pre, int[] ino) {
        // Iterative: a stack of nodes still waiting for a right child.
        if (pre.length == 0) return null;
        TreeNode root = new TreeNode(pre[0]);
        ArrayDeque<TreeNode> st = new ArrayDeque<>();
        st.push(root);
        int j = 0;
        for (int i = 1; i < pre.length; i++) {
            TreeNode node = new TreeNode(pre[i]);
            TreeNode parent = null;
            while (!st.isEmpty() && st.peek().val == ino[j]) { parent = st.pop(); j++; }
            if (parent != null) parent.right = node;
            else st.peek().left = node;
            st.push(node);
        }
        return root;
    }
''',
    examples=[("Example 1", "5\n8 4 12 10 14\n4 8 10 12 14\n"), ("Example 2", "1\n-1\n-1\n")],
    hidden=[
        ("Left chain", "4\n4 3 2 1\n1 2 3 4\n"),
        ("Right chain", "4\n1 2 3 4\n1 2 3 4\n"),
        ("Full tree", "7\n1 2 4 5 3 6 7\n4 2 5 1 6 3 7\n"),
        ("Zig-zag", "5\n10 20 30 40 50\n20 40 50 30 10\n"),
    ],
    expl=[
        "8 is the root; 4 is left of it in the inorder, and 10 12 14 are right of it, rooted at 12.",
        "A single node.",
    ],
    prereqs=[
        ("tree_traversal", "What preorder and inorder each reveal about the root."),
        ("hashing", "A value → inorder-index map, so each split is O(1)."),
    ],
)

_p(
    "serialize-tree-preorder", "Serialize a Tree", "Easy",
    topics=["Trees"], subtopics=["Serialization", "Preorder Traversal"], companies=["Google", "LinkedIn"],
    shape="tree", ret="String", todo="preorder walk: write the value, or # for a null child, so the shape can be rebuilt",
    description=(
        "Write a binary tree as a single line that records its **shape** as well as its values: a "
        "preorder walk that writes each node's value and writes `#` for every missing child.\n\n"
        "For the tree `1` with left child `2` and no right child, the line is `1 2 # # #`.\n\n"
        "### Input\nOne line: the tree in level order, `null` for a missing child.\n\n"
        "### Output\nThe preorder tokens with `#` markers, separated by spaces."
    ),
    constraints="0 ≤ nodes ≤ 10^4\n-1000 ≤ value ≤ 1000",
    hints=[
        "A plain preorder `1 2` could be 2-as-left-child or 2-as-right-child. What extra information removes the ambiguity?",
        "Write something for every null child too. Then each node is followed by exactly its whole left subtree, then its whole right subtree.",
        "Recursive: `if (node == null) write #; else write val, recurse left, recurse right`. An empty tree is just `#`.",
    ],
    opt=("O(n)", "O(h)", "One preorder walk writing n values and n + 1 markers."),
    editorial=(
        "## The one thing this teaches\n**Nulls are data.** A traversal of values alone loses the "
        "shape; a traversal that also writes every null child is unambiguous, because each subtree "
        "then says where it ends.\n\n"
        "## Approach\n```java\nvoid write(TreeNode node, StringBuilder sb) {\n"
        "    if (sb.length() > 0) sb.append(' ');\n"
        "    if (node == null) { sb.append('#'); return; }\n    sb.append(node.val);\n"
        "    write(node.left, sb);\n    write(node.right, sb);\n}\n```\n\n"
        "## Why it can be read back\nA tree with n nodes has exactly n + 1 null children, so the "
        "line always has 2n + 1 tokens and a reader always knows when a subtree is finished. "
        "*Deserialize a Tree* is that reader.\n\n"
        "## Why preorder\nThe root comes first, so a reader can create a node before it knows "
        "anything about its children — exactly the order a recursive builder wants."
    ),
    py='''
def solve(root):
    out, st = [], [root]
    while st:
        node = st.pop()
        if node is None:
            out.append("#")
            continue
        out.append(str(node.val))
        st.append(node.right)
        st.append(node.left)
    return " ".join(out)
''',
    java='''
    static String solve(TreeNode root) {
        StringBuilder sb = new StringBuilder();
        write(root, sb);
        return sb.toString();
    }

    static void write(TreeNode node, StringBuilder sb) {
        if (sb.length() > 0) sb.append(' ');
        if (node == null) { sb.append('#'); return; }
        sb.append(node.val);
        write(node.left, sb);
        write(node.right, sb);
    }
''',
    examples=[("Example 1", "5 3 8 null 4 7\n"), ("Example 2", "null\n")],
    hidden=[
        ("Single node", "7\n"),
        ("Left child only", "1 2\n"),
        ("Right child only", "1 null 2\n"),
        ("Negative values", "-5 -3 8 null -1\n"),
    ],
    expl=[
        "5, then its left subtree `3 # 4 # #`, then its right subtree `8 7 # # #`.",
        "An empty tree is a single null.",
    ],
    prereqs=[
        ("tree_traversal", "Preorder: node, left subtree, right subtree."),
        ("recursion", "A walk that writes something for the base case too."),
    ],
)

_p(
    "deserialize-tree-preorder", "Deserialize a Tree", "Medium",
    topics=["Trees"], subtopics=["Serialization", "Tree Construction"], companies=["Google", "LinkedIn", "Uber"],
    shape="preorder_tokens", ret="TreeNode", todo="read tokens in order: # is null; a value is a node whose left and right subtrees are read next",
    description=(
        "Rebuild a binary tree from its serialization: a preorder walk where every missing child is "
        "written as `#` (the output of *Serialize a Tree*).\n\n"
        "### Input\nOne line of tokens: integers and `#`.\n\n"
        "### Output\nThe starter prints the rebuilt tree in level order (`null` for a missing "
        "child, trailing `null`s removed), or `EMPTY` for an empty tree."
    ),
    constraints="1 ≤ tokens ≤ 2·10^4\nThe input is a valid serialization",
    hints=[
        "The first token is the root, or `#` for an empty tree. What comes straight after the root?",
        "After a node come *all* the tokens of its left subtree, then all of its right subtree. The `#` markers tell each subtree where it ends.",
        "Keep one shared position in the token list. `build()`: read a token; if `#` return null; else make a node, set left = build(), right = build().",
    ],
    opt=("O(n)", "O(h)", "Each token is read once; recursion depth is the tree height."),
    editorial=(
        "## The one thing this teaches\n**Reading mirrors writing.** The serializer was a preorder "
        "walk that wrote a token per call; the deserializer is the same walk that *reads* a token "
        "per call. Because the stream records every null, no lookahead or counting is needed.\n\n"
        "## Approach\n```java\nint pos = 0;\n\nTreeNode build(String[] t) {\n"
        "    String tok = t[pos++];\n    if (tok.equals(\"#\")) return null;\n"
        "    TreeNode node = new TreeNode(Integer.parseInt(tok));\n"
        "    node.left = build(t);       // consumes exactly the left subtree's tokens\n"
        "    node.right = build(t);\n    return node;\n}\n```\n\n"
        "## Why one shared position works\nEach call consumes exactly its own subtree's tokens, so "
        "after `node.left = build(t)` returns, `pos` sits at the first token of the right subtree. "
        "No subtree sizes are needed.\n\n"
        "## Deep trees\nA chain of 10^4 nodes recurses 10^4 deep, which can overflow Java's default "
        "stack. An explicit stack of nodes waiting for a child avoids that."
    ),
    py='''
def solve(tokens):
    pos = 0

    def build():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        if tok == "#":
            return None
        node = TreeNode(int(tok))
        node.left = build()
        node.right = build()
        return node

    return build()
''',
    java='''
    static TreeNode solve(String[] tokens) {
        // Iterative: each stack entry is a node plus how many children it has been given.
        if (tokens.length == 0 || tokens[0].equals("#")) return null;
        TreeNode root = new TreeNode(Integer.parseInt(tokens[0]));
        ArrayDeque<Object[]> st = new ArrayDeque<>();
        st.push(new Object[]{root, 0});
        for (int i = 1; i < tokens.length && !st.isEmpty(); i++) {
            Object[] top = st.peek();
            TreeNode parent = (TreeNode) top[0];
            int filled = (Integer) top[1];
            TreeNode child = tokens[i].equals("#") ? null : new TreeNode(Integer.parseInt(tokens[i]));
            if (filled == 0) parent.left = child; else parent.right = child;
            top[1] = filled + 1;
            if (filled + 1 == 2) st.pop();
            if (child != null) st.push(new Object[]{child, 0});
        }
        return root;
    }
''',
    examples=[("Example 1", "5 3 # 4 # # 8 7 # # #\n"), ("Example 2", "#\n")],
    hidden=[
        ("Single node", "7 # #\n"),
        ("Left chain", "3 2 1 # # # #\n"),
        ("Right chain", "1 # 2 # 3 # #\n"),
        ("Negative values", "-5 -3 # -1 # # 8 # #\n"),
    ],
    expl=[
        "5 has left subtree `3 # 4 # #` and right subtree `8 7 # # #`.",
        "A single `#` is the empty tree.",
    ],
    prereqs=[
        ("tree_traversal", "Preorder, read instead of written."),
        ("recursion", "Each call consumes exactly its own subtree."),
    ],
)

_p(
    "bst-iterator", "BST Iterator", "Medium",
    topics=["Trees", "Design"], subtopics=["BST", "Controlled Recursion", "Stack"], companies=["Meta", "Google", "Microsoft"],
    shape="tree_ops", ret="String", todo="keep a stack of the left spine; next() pops a node and pushes the left spine of its right child",
    description=(
        "Design an iterator over a binary search tree that returns its values in ascending order, "
        "one per call:\n\n- `next` — the next smallest value.\n- `hasNext` — `true` if values remain.\n\n"
        "Both must be O(1) amortised, and memory O(h) where h is the height — so no copying the "
        "whole tree into a list.\n\n"
        "### Input\nLine 1: the BST in level order, `null` for a missing child.\nLine 2: `q`.\n"
        "Next `q` lines: `next` or `hasNext`. `next` is only called when a value remains.\n\n"
        "### Output\nOne line per operation: the value, or `true` / `false`."
    ),
    constraints="1 ≤ nodes ≤ 10^5\n1 ≤ q ≤ 10^5",
    hints=[
        "An in-order traversal gives the values sorted. The difficulty is stopping it after one value and resuming later.",
        "The recursive walk keeps its place on the call stack. An explicit stack can hold the same information between calls.",
        "Push the whole left spine from the root. `next`: pop a node, then push the left spine of its right child. The stack never holds more than one path.",
    ],
    opt=("O(1) amortised", "O(h)", "Each node is pushed once and popped once across all calls; the stack holds one root-to-leaf path."),
    editorial=(
        "## The one thing this teaches\n**An explicit stack lets a recursion pause.** Recursive "
        "in-order keeps its place in call frames and cannot stop halfway. Holding those frames in a "
        "`Deque` means the traversal can return one value, and resume exactly where it was.\n\n"
        "## Approach\n```java\nclass BSTIterator {\n    private final Deque<TreeNode> st = new ArrayDeque<>();\n\n"
        "    BSTIterator(TreeNode root) { pushLeft(root); }\n\n"
        "    private void pushLeft(TreeNode n) { for (; n != null; n = n.left) st.push(n); }\n\n"
        "    boolean hasNext() { return !st.isEmpty(); }\n\n"
        "    int next() {\n        TreeNode n = st.pop();\n        pushLeft(n.right);        // the successor's subtree\n"
        "        return n.val;\n    }\n}\n```\n\n"
        "## Why it is amortised O(1)\nA single `next` can push a long spine, but every node is "
        "pushed once and popped once over the whole iteration: 2n operations for n calls.\n\n"
        "## Why not flatten first\nCopying the in-order values into a list makes every call O(1) "
        "but costs O(n) memory up front — the thing the O(h) requirement rules out."
    ),
    py='''
def solve(root, ops):
    st = []

    def push_left(node):
        while node is not None:
            st.append(node)
            node = node.left

    push_left(root)
    out = []
    for op in ops:
        if op == "hasNext":
            out.append("true" if st else "false")
        else:
            node = st.pop()
            push_left(node.right)
            out.append(str(node.val))
    return "\\n".join(out)
''',
    java='''
    static class BSTIterator {
        private final ArrayDeque<TreeNode> st = new ArrayDeque<>();
        BSTIterator(TreeNode root) { pushLeft(root); }
        private void pushLeft(TreeNode n) { for (; n != null; n = n.left) st.push(n); }
        boolean hasNext() { return !st.isEmpty(); }
        int next() {
            TreeNode n = st.pop();
            pushLeft(n.right);
            return n.val;
        }
    }

    static String solve(TreeNode root, String[] ops) {
        BSTIterator it = new BSTIterator(root);
        StringBuilder sb = new StringBuilder();
        for (String op : ops) {
            if (sb.length() > 0) sb.append('\\n');
            if (op.equals("hasNext")) sb.append(it.hasNext());
            else sb.append(it.next());
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "10 5 14 null 8 12 20\n7\nnext\nnext\nhasNext\nnext\nnext\nnext\nhasNext\n"),
        ("Example 2", "1\n3\nhasNext\nnext\nhasNext\n"),
    ],
    hidden=[
        ("Left chain", "4 3 null 2 null 1\n5\nnext\nnext\nnext\nhasNext\nnext\n"),
        ("Right chain", "1 null 2 null 3\n4\nnext\nnext\nhasNext\nnext\n"),
        ("Full tree, interleaved", "8 4 12 2 6 10 14\n9\nhasNext\nnext\nnext\nnext\nnext\nhasNext\nnext\nnext\nhasNext\n"),
    ],
    expl=[
        "In order the tree is 5 8 10 12 14 20. After five values one is left, so the last hasNext is still true.",
        "A single node: true, 1, then false.",
    ],
    prereqs=[
        ("bst", "In-order traversal of a BST is sorted order."),
        ("stack", "An explicit stack standing in for the call stack."),
    ],
)

_p(
    "floor-ceiling-queries", "Floor and Ceiling Queries", "Easy",
    topics=["Trees", "Binary Search"], subtopics=["Ordered Set", "TreeMap"], companies=["Amazon", "Uber"],
    shape="arr2", ret="String", todo="put the values in a TreeSet; each query is floor(q) and ceiling(q)",
    description=(
        "Given a collection of integers and a list of queries, answer each query `x` with its "
        "**floor** — the largest value `≤ x` — and its **ceiling** — the smallest value `≥ x`. "
        "Print `none` for one that does not exist.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` values (duplicates allowed).\nLine 3: `m`.\n"
        "Line 4: `m` queries.\n\n"
        "### Output\nOne line per query: `floor ceiling`."
    ),
    constraints="1 ≤ n, m ≤ 10^5\n-10^9 ≤ values, queries ≤ 10^9",
    hints=[
        "Scanning every value per query is O(n·m).",
        "In sorted order, the floor and ceiling of x sit next to each other, around where x would be inserted.",
        "Java's `TreeSet` answers both directly: `floor(x)` and `ceiling(x)`, each O(log n), returning null when absent.",
    ],
    opt=("O((n + m) log n)", "O(n)", "A balanced BST (TreeSet) built once, then two O(log n) lookups per query."),
    editorial=(
        "## The one thing this teaches\n**A `TreeMap` or `TreeSet` is a balanced BST you do not "
        "have to write.** A `HashSet` knows *whether* x is present; an ordered set also knows what "
        "is *nearest* to it, in O(log n).\n\n"
        "## Approach\n```java\nTreeSet<Integer> set = new TreeSet<>();\nfor (int v : a) set.add(v);\n"
        "for (int x : queries) {\n    Integer lo = set.floor(x), hi = set.ceiling(x);   // null when absent\n"
        "    out.append(lo == null ? \"none\" : lo).append(' ')\n"
        "       .append(hi == null ? \"none\" : hi).append('\\n');\n}\n```\n\n"
        "## The family\n| Method | Returns |\n| --- | --- |\n| `floor(x)` | largest ≤ x |\n"
        "| `ceiling(x)` | smallest ≥ x |\n| `lower(x)` | largest < x |\n| `higher(x)` | smallest > x |\n\n"
        "`TreeMap` has the same four as `floorKey` … `higherKey`, plus `floorEntry` and friends.\n\n"
        "## Without a TreeSet\nSort once and binary-search for the insertion point: the ceiling is "
        "there and the floor is just before it. Same bounds, when the values never change — the "
        "TreeSet also allows inserts and deletes between queries."
    ),
    py='''
def solve(a, b):
    s = sorted(set(a))
    out = []
    for x in b:
        i = bisect_right(s, x)
        lo = str(s[i - 1]) if i > 0 else "none"
        j = bisect_left(s, x)
        hi = str(s[j]) if j < len(s) else "none"
        out.append(lo + " " + hi)
    return "\\n".join(out)
''',
    java='''
    static String solve(int[] a, int[] b) {
        TreeSet<Integer> set = new TreeSet<>();
        for (int v : a) set.add(v);
        StringBuilder sb = new StringBuilder();
        for (int x : b) {
            if (sb.length() > 0) sb.append('\\n');
            Integer lo = set.floor(x), hi = set.ceiling(x);
            sb.append(lo == null ? "none" : lo.toString()).append(' ').append(hi == null ? "none" : hi.toString());
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "5\n10 4 25 17 4\n4\n12 4 30 1\n"), ("Example 2", "1\n0\n2\n-5 5\n")],
    hidden=[
        ("Exact hits", "3\n1 2 3\n3\n1 2 3\n"),
        ("Extremes", "2\n-1000000000 1000000000\n3\n0 -1000000000 1000000000\n"),
        ("Duplicates only", "4\n7 7 7 7\n3\n6 7 8\n"),
    ],
    expl=[
        "12 lies between 10 and 17; 4 is present, so it is its own floor and ceiling; nothing is ≥ 30; nothing is ≤ 1.",
        "0 is the only value: above −5, below 5.",
    ],
    prereqs=[
        ("bst", "An ordered set is a balanced BST: nearest-value queries in O(log n)."),
        ("binary_search", "The insertion point of x separates its floor from its ceiling."),
    ],
)

_p(
    "nearby-almost-duplicate", "Nearby Almost-Duplicate", "Medium",
    topics=["Sliding Window", "Trees"], subtopics=["Ordered Set", "Bucketing"], companies=["Airbnb", "Google"],
    shape="arr_xy", ret="String", todo="slide a window of the last k values kept in a TreeSet; for each new value ask for the ceiling of value − t",
    description=(
        "Is there a pair of indices `i < j` with `j − i ≤ k` **and** `|a[i] − a[j]| ≤ t`? Print "
        "`true` or `false`.\n\n"
        "### Input\nLine 1: `n k t`.\nLine 2: `n` integers.\n\n"
        "### Output\n`true` or `false`."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ k ≤ 10^5\n0 ≤ t ≤ 2·10^9\n-2^31 ≤ a[i] ≤ 2^31 − 1",
    hints=[
        "Checking every pair within distance k is O(n·k).",
        "Only the last k values can pair with a[j] — a sliding window. The question is then: does the window hold anything in [a[j] − t, a[j] + t]?",
        "Keep the window in a TreeSet. `ceiling(a[j] − t)` is the smallest candidate ≥ a[j] − t; check it is ≤ a[j] + t. Use `long`: a[j] − t can overflow `int`.",
    ],
    opt=("O(n log k)", "O(k)", "A sliding window of at most k values kept in an ordered set."),
    editorial=(
        "## The one thing this teaches\n**A window you need to *search* is an ordered set.** A hash "
        "set answers \"is this exact value in the window?\"; the question here is \"is any value "
        "*close*?\", and that is a `ceiling` query.\n\n"
        "## Approach\n```java\nTreeSet<Long> window = new TreeSet<>();\nfor (int j = 0; j < n; j++) {\n"
        "    long x = a[j];\n    Long c = window.ceiling(x - t);           // smallest value >= x - t\n"
        "    if (c != null && c <= x + t) return true;\n    window.add(x);\n"
        "    if (j >= k) window.remove((long) a[j - k]);  // keep only the last k\n}\nreturn false;\n```\n\n"
        "## Two traps\n- **Overflow.** `x - t` with x near −2^31 and t up to 2·10^9 does not fit in "
        "`int`. Work in `long`.\n- **Duplicates.** If the window already holds x, `ceiling` finds "
        "it and returns true before the add — so a set is enough.\n\n"
        "## O(n) with buckets\nBuckets of width t + 1 hold at most one window value each (two would "
        "already be an answer), and a match can only be in the same bucket or a neighbour."
    ),
    py='''
def solve(a, x, y):
    k, t = x, y
    w = t + 1
    buckets = {}
    for j, v in enumerate(a):
        b = v // w
        if b in buckets:
            return "true"
        if b - 1 in buckets and v - buckets[b - 1] <= t:
            return "true"
        if b + 1 in buckets and buckets[b + 1] - v <= t:
            return "true"
        buckets[b] = v
        if j >= k:
            del buckets[a[j - k] // w]
    return "false"
''',
    java='''
    static String solve(int[] a, long k, long t) {
        TreeSet<Long> window = new TreeSet<>();
        for (int j = 0; j < a.length; j++) {
            long x = a[j];
            Long c = window.ceiling(x - t);
            if (c != null && c <= x + t) return "true";
            window.add(x);
            if (j >= k) window.remove((long) a[(int) (j - k)]);
        }
        return "false";
    }
''',
    examples=[("Example 1", "5 2 1\n4 9 5 20 7\n"), ("Example 2", "5 1 2\n1 10 4 20 7\n")],
    hidden=[
        ("Zero distance allowed", "3 0 100\n1 2 3\n"),
        ("Close values too far apart", "5 1 1\n1 10 20 2 30\n"),
        ("Overflow edges", "2 1 2000000000\n-2147483648 2147483647\n"),
        ("Just inside", "5 2 2\n10 20 30 32 50\n"),
        ("Negative neighbours", "4 1 1\n-3 -1 -7 -8\n"),
    ],
    expl=[
        "Indices 0 and 2 hold 4 and 5: two apart, and differing by 1.",
        "Only neighbours count when k = 1, and every neighbouring pair differs by 6 or more.",
    ],
    prereqs=[
        ("sliding_window", "Only the last k values can pair with the current one."),
        ("bst", "An ordered set answers \"is any value within t?\" with one ceiling query."),
    ],
)

_p(
    "clone-graph", "Clone a Graph", "Medium",
    topics=["Graphs", "Hashing"], subtopics=["Deep Copy", "BFS"], companies=["Meta", "Google", "Amazon"],
    shape="graph_nodes", ret="Node", todo="traverse from the given node; the map from original to copy is also the visited set",
    description=(
        "You are given a node of an undirected graph; each node has a value and a list of "
        "neighbours. Return a **deep copy** of every node reachable from it: new nodes, whose "
        "neighbour lists point at copies.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: an undirected edge `u v`. Nodes are 0 … n − 1 "
        "and you receive node 0.\n\n"
        "### Output\nThe starter prints each node reachable from your copy, in value order, as "
        "`v: neighbours…`. If the copy shares any node with the original it prints `SHARED`."
    ),
    constraints="1 ≤ n ≤ 100\n0 ≤ m ≤ n(n − 1)/2\nNo self-loops or repeated edges",
    hints=[
        "Copying a node means copying its neighbours, which means copying *their* neighbours — and the graph has cycles.",
        "Keep a map from each original node to its copy. Before copying a node, check the map: if it is there, reuse that copy.",
        "BFS: copy the start node and queue it. For each dequeued node, for each neighbour, create its copy if missing (and queue it), then add that copy to the current copy's list.",
    ],
    opt=("O(V + E)", "O(V)", "One traversal; the original → copy map doubles as the visited set."),
    editorial=(
        "## The one thing this teaches\n**In a copy, the visited set and the old → new map are the "
        "same thing.** A traversal needs to know whether a node has been seen; a copy needs to know "
        "which new node stands for an old one. One map answers both, and it is what stops a cycle "
        "from copying forever.\n\n"
        "## Approach\n```java\nMap<Node, Node> copy = new HashMap<>();\n"
        "copy.put(start, new Node(start.val));\nDeque<Node> q = new ArrayDeque<>(List.of(start));\n"
        "while (!q.isEmpty()) {\n    Node u = q.poll();\n    for (Node v : u.neighbors) {\n"
        "        if (!copy.containsKey(v)) {               // first sight: create and visit\n"
        "            copy.put(v, new Node(v.val));\n            q.add(v);\n        }\n"
        "        copy.get(u).neighbors.add(copy.get(v));\n    }\n}\nreturn copy.get(start);\n```\n\n"
        "## The bug that loops forever\nRecursing on neighbours without recording the copy *before* "
        "the recursion: node A clones B, B clones A, A clones B …\n\n"
        "## Compare\n*Copy a List with Random Pointers* is the same map on a structure without a "
        "traversal problem, because a list can be walked in one line."
    ),
    py='''
def solve(node):
    if node is None:
        return None
    copy = {id(node): Node(node.val)}
    q = deque([node])
    while q:
        u = q.popleft()
        for v in u.neighbors:
            if id(v) not in copy:
                copy[id(v)] = Node(v.val)
                q.append(v)
            copy[id(u)].neighbors.append(copy[id(v)])
    return copy[id(node)]
''',
    java='''
    static Map<Node, Node> made = new IdentityHashMap<>();

    static Node solve(Node node) {
        if (node == null) return null;
        Node have = made.get(node);
        if (have != null) return have;
        Node c = new Node(node.val);
        made.put(node, c);                  // record BEFORE recursing, or a cycle never ends
        for (Node nb : node.neighbors) c.neighbors.add(solve(nb));
        return c;
    }
''',
    examples=[("Example 1", "4 4\n0 1\n1 2\n2 0\n2 3\n"), ("Example 2", "1 0\n")],
    hidden=[
        ("Two nodes", "2 1\n0 1\n"),
        ("Unreachable nodes are not copied", "5 2\n0 1\n3 4\n"),
        ("Complete graph", "4 6\n0 1\n0 2\n0 3\n1 2\n1 3\n2 3\n"),
        ("Star", "5 4\n0 1\n0 2\n0 3\n0 4\n"),
    ],
    expl=[
        "A triangle 0–1–2 with node 3 hanging off node 2. The copy must reproduce the cycle on new nodes.",
        "A single node with no neighbours.",
    ],
    prereqs=[
        ("bfs", "A traversal from one node that visits each reachable node once."),
        ("visited_set", "The map that prevents a cycle from being copied forever."),
    ],
)

_p(
    "prim-dense-graph", "Wire Every Site (Dense Prim)", "Medium",
    topics=["Graphs"], subtopics=["Minimum Spanning Tree", "Prim's Algorithm"], companies=["Amazon", "Google"],
    shape="matrix", ret="long", todo="Prim without a heap: keep each site's cheapest link to the tree in an array; add the cheapest site, then relax its row",
    description=(
        "`n` sites must all be connected by cables. The cost of a cable between sites `i` and `j` "
        "is given for **every** pair. Print the minimum total cost that connects all sites "
        "(directly or through other sites).\n\n"
        "### Input\nLine 1: `n n`.\nNext `n` lines: `n` integers — the symmetric cost matrix, "
        "with 0 on the diagonal.\n\n"
        "### Output\nThe minimum total cable cost."
    ),
    constraints="1 ≤ n ≤ 1000\n1 ≤ cost ≤ 10^6 off the diagonal",
    hints=[
        "This is a minimum spanning tree. Kruskal would sort all n²/2 edges — O(n² log n).",
        "Prim grows one tree: repeatedly add the cheapest site not yet connected. Keep best[v] = the cheapest cable from v to any site already in the tree.",
        "With every pair an edge, a heap does not help. Scan the array for the minimum (O(n)), add it, and update best[] from its row (O(n)): O(n²) in total.",
    ],
    opt=("O(V²)", "O(V)", "Array-based Prim: V rounds of an O(V) scan and an O(V) update."),
    editorial=(
        "## The one thing this teaches\n**Pick the MST algorithm by density.** Kruskal is "
        "O(E log E) and Prim with a heap is O(E log V) — both O(V² log V) when E ≈ V². Prim with a "
        "plain array is O(V²), which is optimal for a dense graph because reading the input is "
        "already O(V²).\n\n"
        "## Approach\n```java\nlong[] best = new long[n];\nboolean[] in = new boolean[n];\n"
        "Arrays.fill(best, Long.MAX_VALUE);\nbest[0] = 0;\nlong total = 0;\n"
        "for (int round = 0; round < n; round++) {\n    int u = -1;\n"
        "    for (int v = 0; v < n; v++)                       // cheapest site not yet in\n"
        "        if (!in[v] && (u == -1 || best[v] < best[u])) u = v;\n"
        "    in[u] = true;\n    total += best[u];\n"
        "    for (int v = 0; v < n; v++)                       // its row may be cheaper\n"
        "        if (!in[v] && cost[u][v] < best[v]) best[v] = cost[u][v];\n}\n```\n\n"
        "## Why the cheapest link is safe\nThe cut property: for any split of the sites into "
        "\"connected\" and \"not yet\", the cheapest cable across the split belongs to some minimum "
        "spanning tree. Prim takes exactly that cable every round.\n\n"
        "## When to use the heap version\nSparse graphs, E ≈ V: a heap makes each round "
        "O(log V) instead of O(V)."
    ),
    py='''
def solve(m):
    n = len(m)
    edges = sorted((m[i][j], i, j) for i in range(n) for j in range(i + 1, n))
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = used = 0
    for w, i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj
            total += w
            used += 1
            if used == n - 1:
                break
    return total
''',
    java='''
    static long solve(int[][] m) {
        int n = m.length;
        long[] best = new long[n];
        boolean[] in = new boolean[n];
        Arrays.fill(best, Long.MAX_VALUE);
        best[0] = 0;
        long total = 0;
        for (int round = 0; round < n; round++) {
            int u = -1;
            for (int v = 0; v < n; v++)
                if (!in[v] && (u == -1 || best[v] < best[u])) u = v;
            in[u] = true;
            total += best[u];
            for (int v = 0; v < n; v++)
                if (!in[v] && m[u][v] < best[v]) best[v] = m[u][v];
        }
        return total;
    }
''',
    examples=[("Example 1", "4 4\n0 1 4 3\n1 0 2 6\n4 2 0 5\n3 6 5 0\n"), ("Example 2", "1 1\n0\n")],
    hidden=[
        ("Two sites", "2 2\n0 9\n9 0\n"),
        ("All equal", "4 4\n0 5 5 5\n5 0 5 5\n5 5 0 5\n5 5 5 0\n"),
        ("Through a hub is cheaper", "5 5\n0 1 1 1 1\n1 0 100 100 100\n1 100 0 100 100\n1 100 100 0 100\n1 100 100 100 0\n"),
        ("Large costs", "3 3\n0 1000000 999999\n1000000 0 1000000\n999999 1000000 0\n"),
    ],
    expl=[
        "Cables 0–1 (1), 1–2 (2) and 0–3 (3) connect everything for 6.",
        "One site needs no cable.",
    ],
    prereqs=[
        ("mst", "The cut property: the cheapest edge across any cut is safe."),
        ("greedy", "Grow the tree one cheapest connection at a time."),
    ],
)

_p(
    "mst-critical-edges", "Critical Edges of a Spanning Tree", "Hard",
    topics=["Graphs"], subtopics=["Minimum Spanning Tree", "Union-Find"], companies=["Amazon", "Google"],
    shape="wgraph", ret="String", todo="MST weight with Kruskal; an edge is critical if excluding it raises the weight, pseudo-critical if forcing it keeps the weight",
    description=(
        "A connected, undirected, weighted graph has edges numbered `0 … m − 1` in input order. "
        "Classify its edges:\n\n"
        "- **Critical** — in *every* minimum spanning tree: removing it makes the MST heavier (or "
        "disconnects the graph).\n"
        "- **Pseudo-critical** — in *some* minimum spanning trees but not all.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v w`.\n\n"
        "### Output\nLine 1: the critical edge indices in increasing order, or `none`.\n"
        "Line 2: the pseudo-critical edge indices in increasing order, or `none`."
    ),
    constraints="2 ≤ n ≤ 100\nn − 1 ≤ m ≤ 200\n1 ≤ w ≤ 1000\nThe graph is connected; no self-loops or repeated edges",
    hints=[
        "Compute the MST weight W once with Kruskal.",
        "Edge e is critical exactly when the best spanning tree *without* e weighs more than W (or does not exist). Run Kruskal skipping e.",
        "If e is not critical, it is pseudo-critical exactly when some MST *contains* it: union e's endpoints first, add its weight, run Kruskal on the rest, and compare with W.",
    ],
    opt=("O(m² · α(n))", "O(n + m)", "Sort once; then two Kruskal passes per edge over the pre-sorted list."),
    editorial=(
        "## The one thing this teaches\n**Ask a spanning-tree question by changing the input and "
        "re-running.** \"Is this edge in every MST?\" has no direct formula, but \"what is the best "
        "tree without it?\" and \"what is the best tree that is forced to use it?\" are each one "
        "Kruskal pass.\n\n"
        "## Approach\n```java\nint base = kruskal(-1, -1);             // (skip, force)\n"
        "for (int e = 0; e < m; e++) {\n    if (kruskal(e, -1) > base) critical.add(e);            // needed by every MST\n"
        "    else if (kruskal(-1, e) == base) pseudo.add(e);     // usable by some MST\n}\n\n"
        "int kruskal(int skip, int force) {\n    DSU d = new DSU(n);\n    int w = 0, used = 0;\n"
        "    if (force >= 0) { d.union(u[force], v[force]); w += wt[force]; used++; }\n"
        "    for (int e : byWeight) {                          // indices sorted by weight, once\n"
        "        if (e == skip) continue;\n        if (d.union(u[e], v[e])) { w += wt[e]; used++; }\n    }\n"
        "    return used == n - 1 ? w : Integer.MAX_VALUE;     // disconnected = infinitely heavy\n}\n```\n\n"
        "## Why the order of the two tests matters\nA critical edge also passes the forced test "
        "(forcing an edge every MST uses changes nothing), so check critical first.\n\n"
        "## Sort once\nThe edge order does not change between runs; sorting inside `kruskal` "
        "turns O(m²) into O(m² log m)."
    ),
    py='''
def solve(n, edges):
    m = len(edges)
    order = sorted(range(m), key=lambda e: edges[e][2])

    def kruskal(skip, force):
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        weight = used = 0
        if force >= 0:
            u, v, w = edges[force]
            parent[find(u)] = find(v)
            weight += w
            used += 1
        for e in order:
            if e == skip:
                continue
            u, v, w = edges[e]
            ru, rv = find(u), find(v)
            if ru != rv:
                parent[ru] = rv
                weight += w
                used += 1
        return weight if used == n - 1 else float("inf")

    base = kruskal(-1, -1)
    critical, pseudo = [], []
    for e in range(m):
        if kruskal(e, -1) > base:
            critical.append(e)
        elif kruskal(-1, e) == base:
            pseudo.append(e)
    fmt = lambda xs: " ".join(map(str, xs)) if xs else "none"
    return fmt(critical) + "\\n" + fmt(pseudo)
''',
    java='''
    static int n, m;
    static int[][] E;
    static Integer[] order;
    static int[] parent;

    static int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    static long kruskal(int skip, int force) {
        parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        long w = 0;
        int used = 0;
        if (force >= 0) { parent[find(E[force][0])] = find(E[force][1]); w += E[force][2]; used++; }
        for (int e : order) {
            if (e == skip) continue;
            int a = find(E[e][0]), b = find(E[e][1]);
            if (a != b) { parent[a] = b; w += E[e][2]; used++; }
        }
        return used == n - 1 ? w : Long.MAX_VALUE;
    }

    static String solve(int nn, int[][] edges) {
        n = nn; E = edges; m = edges.length;
        order = new Integer[m];
        for (int i = 0; i < m; i++) order[i] = i;
        Arrays.sort(order, Comparator.comparingInt(e -> E[e][2]));
        long base = kruskal(-1, -1);
        StringBuilder crit = new StringBuilder(), pseudo = new StringBuilder();
        for (int e = 0; e < m; e++) {
            if (kruskal(e, -1) > base) crit.append(crit.length() > 0 ? " " : "").append(e);
            else if (kruskal(-1, e) == base) pseudo.append(pseudo.length() > 0 ? " " : "").append(e);
        }
        return (crit.length() > 0 ? crit.toString() : "none") + "\\n" + (pseudo.length() > 0 ? pseudo.toString() : "none");
    }
''',
    examples=[
        ("Example 1", "4 5\n0 1 1\n1 2 2\n0 2 2\n2 3 3\n1 3 4\n"),
        ("Example 2", "5 5\n0 1 2\n1 2 2\n2 3 2\n3 4 2\n4 0 2\n"),
    ],
    hidden=[
        ("A tree: every edge critical", "4 3\n0 1 5\n1 2 3\n2 3 4\n"),
        ("Triangle with one heavy edge", "3 3\n0 1 1\n1 2 1\n0 2 2\n"),
        ("Triangle, all equal", "3 3\n0 1 7\n1 2 7\n0 2 7\n"),
        ("Bridge plus a cycle", "5 6\n0 1 1\n1 2 2\n2 0 2\n2 3 5\n3 4 1\n4 2 1\n"),
    ],
    expl=[
        "The MST weighs 6. Without edge 0 (0–1) or edge 3 (2–3) the best tree weighs 7, so both are critical. Either weight-2 edge will do, so 1 and 2 are pseudo-critical. Forcing edge 4 costs 7, so it is in no MST.",
        "A 5-cycle of equal weights: dropping any one edge leaves an MST, so all five are pseudo-critical and none is critical.",
    ],
    prereqs=[
        ("mst", "Kruskal's algorithm and what makes an edge safe."),
        ("union_find", "Fast repeated Kruskal passes."),
    ],
)

_p(
    "floyd-warshall-queries", "All-Pairs Distances", "Medium",
    topics=["Graphs", "Dynamic Programming"], subtopics=["Floyd–Warshall", "All-Pairs Shortest Paths"], companies=["Google", "Uber"],
    shape="wgraph_q", ret="String", todo="dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]) for every intermediate k in the outer loop",
    description=(
        "A directed graph has weighted edges, some of them **negative**, but no negative cycle. "
        "Answer `q` queries: the shortest distance from `a` to `b`, or `INF` if `b` is unreachable.\n\n"
        "### Input\nLine 1: `n m q`.\nNext `m` lines: a directed edge `u v w` (repeated edges "
        "possible).\nNext `q` lines: `a b`.\n\n"
        "### Output\nOne line per query."
    ),
    constraints="1 ≤ n ≤ 400\n0 ≤ m ≤ n²\n1 ≤ q ≤ 10^5\n-1000 ≤ w ≤ 1000\nNo negative cycles",
    hints=[
        "Many queries and a small n: compute every pair once, then answer each query in O(1).",
        "Negative weights rule out Dijkstra. Let dist_k[i][j] be the best path using only intermediate nodes 0..k−1. Adding node k either helps or it does not.",
        "Put k in the OUTER loop: for k, for i, for j, relax through k. Skip i→k when it is unreachable, or INF + negative looks like a real path.",
    ],
    opt=("O(n³ + q)", "O(n²)", "Three nested loops over the nodes, updating one matrix in place."),
    editorial=(
        "## The one thing this teaches\n**Floyd–Warshall is a DP over which nodes a path may pass "
        "through.** After the k-th outer iteration, `dist[i][j]` is the best path that uses only "
        "nodes 0 … k as stops. Allowing node k as well either improves a path by going through it, "
        "or it does not.\n\n"
        "## Approach\n```java\nlong INF = Long.MAX_VALUE / 4;\nfor (long[] row : dist) Arrays.fill(row, INF);\n"
        "for (int i = 0; i < n; i++) dist[i][i] = 0;\n"
        "for (int[] e : edges) dist[e[0]][e[1]] = Math.min(dist[e[0]][e[1]], e[2]);   // repeated edges\n\n"
        "for (int k = 0; k < n; k++)                 // k OUTERMOST\n    for (int i = 0; i < n; i++) {\n"
        "        if (dist[i][k] == INF) continue;\n        for (int j = 0; j < n; j++)\n"
        "            if (dist[k][j] != INF && dist[i][k] + dist[k][j] < dist[i][j])\n"
        "                dist[i][j] = dist[i][k] + dist[k][j];\n    }\n```\n\n"
        "## The loop-order bug\nWith k innermost, `dist[i][j]` is finalised before the paths through "
        "later nodes have been computed. The code still runs and gives wrong answers.\n\n"
        "## When to use it\nn up to a few hundred and all pairs needed. For one source, Dijkstra "
        "(non-negative) or Bellman-Ford (negative) is far cheaper."
    ),
    py='''
def solve(n, edges, queries):
    INF = float("inf")
    cache = {}

    def from_source(s):
        dist = [INF] * n
        dist[s] = 0
        for _ in range(n - 1):
            changed = False
            for u, v, w in edges:
                if dist[u] != INF and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    changed = True
            if not changed:
                break
        return dist

    out = []
    for a, b in queries:
        if a not in cache:
            cache[a] = from_source(a)
        d = cache[a][b]
        out.append("INF" if d == INF else str(d))
    return "\\n".join(out)
''',
    java='''
    static String solve(int n, int[][] edges, int[][] queries) {
        final long INF = Long.MAX_VALUE / 4;
        long[][] dist = new long[n][n];
        for (long[] row : dist) Arrays.fill(row, INF);
        for (int i = 0; i < n; i++) dist[i][i] = 0;
        for (int[] e : edges) dist[e[0]][e[1]] = Math.min(dist[e[0]][e[1]], e[2]);
        for (int k = 0; k < n; k++)
            for (int i = 0; i < n; i++) {
                if (dist[i][k] == INF) continue;
                for (int j = 0; j < n; j++)
                    if (dist[k][j] != INF && dist[i][k] + dist[k][j] < dist[i][j])
                        dist[i][j] = dist[i][k] + dist[k][j];
            }
        StringBuilder sb = new StringBuilder();
        for (int[] q : queries) {
            if (sb.length() > 0) sb.append('\\n');
            long d = dist[q[0]][q[1]];
            sb.append(d == INF ? "INF" : String.valueOf(d));
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "4 5 4\n0 1 4\n0 2 1\n2 1 2\n1 3 1\n2 3 5\n0 3\n0 1\n3 0\n2 2\n"),
        ("Example 2", "3 3 3\n0 1 5\n1 2 -3\n0 2 4\n0 2\n1 2\n2 1\n"),
    ],
    hidden=[
        ("No edges", "3 0 3\n0 1\n1 1\n2 0\n"),
        ("Repeated edges keep the cheapest", "2 3 2\n0 1 9\n0 1 2\n0 1 5\n0 1\n1 0\n"),
        ("Negative chain", "5 4 3\n0 1 -1\n1 2 -2\n2 3 -3\n3 4 -4\n0 4\n1 3\n4 0\n"),
        ("Cycle without negative total", "4 5 4\n0 1 2\n1 2 -1\n2 0 1\n2 3 3\n3 1 -2\n0 3\n3 0\n2 1\n1 0\n"),
    ],
    expl=[
        "0→2→1→3 costs 1 + 2 + 1 = 4; 0→2→1 costs 3; nothing leaves 3; a node is 0 from itself.",
        "0→1→2 costs 5 − 3 = 2, beating the direct edge of 4; nothing reaches 1 from 2.",
    ],
    prereqs=[
        ("dp", "A table indexed by which intermediate nodes are allowed."),
        ("bellman_ford", "Negative edges, and why Dijkstra cannot handle them."),
    ],
)
