# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 11 — extra practice: linked lists and binary trees.
#
# Both units are at the top of their weight band, so these go on optional
# "Extra practice" rungs: reachable, counted once started, never in the way.
#
#   remove-list-elements     a dummy head removes the "delete the head" special case
#   swap-pairs               rewire three pointers per pair, in the right order
#   rotate-list              close the list into a ring, then cut it at n − k mod n
#   partition-list           two tail-appended lists, joined — stable by construction
#   sort-list                merge sort: split with slow/fast, merge like two sorted lists
#   sum-root-to-leaf         carry the number built so far down the path
#   count-good-nodes         carry the maximum on the path down
#   max-width-binary-tree    BFS with heap-style positions, normalised per level
#   house-robber-iii         tree DP returning two values: with and without this node
#   binary-tree-tilt         post-order: return subtree sums, accumulate tilts
# ===========================================================================

_p(
    "remove-list-elements", "Remove Linked List Elements", "Easy",
    topics=["Linked Lists"], subtopics=["Dummy Head"], companies=["Amazon", "Microsoft"],
    shape="list_k", ret="ListNode", todo="put a dummy node before head; unlink every following node whose value is k",
    description=(
        "Remove every node whose value equals `k` from a singly linked list, and return the new "
        "head.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` values (empty if `n` is 0).\n- Line 3: `k`.\n\n"
        "### Output\nThe remaining values separated by spaces, or `EMPTY`."
    ),
    constraints="0 ≤ n ≤ 10^4\n1 ≤ value, k ≤ 50",
    hints=[
        "Deleting a node means pointing its predecessor past it — but the head has no predecessor.",
        "Give it one: a dummy node whose next is head.",
        "Walk with `cur` starting at the dummy. While cur.next matches, skip it; otherwise advance. Return dummy.next.",
    ],
    opt=("O(n)", "O(1)", "One pass relinking in place."),
    editorial=(
        "## The one thing this teaches\n**A dummy head turns a special case into the general "
        "case.** Every deletion is \"make the previous node skip this one\", except deleting the "
        "head, which has no previous node. Put a node in front of the head and the head is no "
        "longer special.\n\n"
        "## Approach\n```java\nListNode dummy = new ListNode(0, head), cur = dummy;\n"
        "while (cur.next != null) {\n"
        "    if (cur.next.val == k) cur.next = cur.next.next;   // unlink; do NOT advance\n"
        "    else cur = cur.next;\n}\nreturn dummy.next;\n```\n\n"
        "## Why not advance after unlinking\nAfter skipping a node, `cur.next` is a *new* node that "
        "has not been checked. Advancing anyway misses consecutive matches: `7 7` would lose only "
        "the first 7.\n\n"
        "## And return `dummy.next`\nNot `head` — if the original head was removed, `head` still "
        "points at it."
    ),
    py='''
def solve(head, k):
    dummy = ListNode(0, head)
    cur = dummy
    while cur.next:
        if cur.next.val == k:
            cur.next = cur.next.next
        else:
            cur = cur.next
    return dummy.next
''',
    java='''
    static ListNode solve(ListNode head, int k) {
        ListNode dummy = new ListNode(0, head), cur = dummy;
        while (cur.next != null) {
            if (cur.next.val == k) cur.next = cur.next.next;
            else cur = cur.next;
        }
        return dummy.next;
    }
''',
    examples=[("Example 1", "7\n1 2 6 3 4 5 6\n6\n"), ("Example 2", "0\n\n1\n")],
    hidden=[
        ("Everything removed", "4\n7 7 7 7\n7\n"),
        ("Nothing removed", "3\n1 2 3\n4\n"),
        ("Alternating", "5\n5 1 5 1 5\n5\n"),
    ],
    expl=[
        "Both 6s go, including the tail.",
        "An empty list stays empty.",
    ],
    prereqs=[
        ("list_basics", "Unlinking a node by pointing its predecessor at its successor."),
        ("design_ds", "A sentinel node that removes the head as a special case."),
    ],
)

_p(
    "swap-pairs", "Swap Nodes in Pairs", "Medium",
    topics=["Linked Lists"], subtopics=["Dummy Head"], companies=["Meta", "Microsoft"],
    shape="list", ret="ListNode", todo="with prev before each pair (a, b): prev.next = b, a.next = b.next, b.next = a",
    description=(
        "Swap every two adjacent nodes of a linked list and return its head. Swap the **nodes**, "
        "not just their values. With an odd length, the last node stays in place.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` values.\n\n"
        "### Output\nThe list after swapping, or `EMPTY`."
    ),
    constraints="0 ≤ n ≤ 100\n0 ≤ value ≤ 100",
    hints=[
        "Swapping a pair changes three pointers: the one into the pair, and the two inside it.",
        "A dummy node before the head means every pair has a predecessor.",
        "For prev → a → b → rest: set prev.next = b, a.next = rest, b.next = a; then prev = a.",
    ],
    opt=("O(n)", "O(1)", "One pass, three pointer writes per pair."),
    editorial=(
        "## The one thing this teaches\n**Pointer surgery in a safe order.** Each pair swap "
        "rewires three links. Write them so that nothing you still need is overwritten first — "
        "`rest` must be captured (or written into `a.next`) before `b.next` is changed.\n\n"
        "## Approach\n```java\nListNode dummy = new ListNode(0, head), prev = dummy;\n"
        "while (prev.next != null && prev.next.next != null) {\n"
        "    ListNode a = prev.next, b = a.next;\n"
        "    prev.next = b;       // into the pair\n    a.next = b.next;     // a takes b's successor\n"
        "    b.next = a;          // b points back at a\n    prev = a;            // a is now the pair's tail\n}\n"
        "return dummy.next;\n```\n\n"
        "## Draw it\nThree boxes and four arrows on paper before typing. Every linked-list bug that "
        "loses half the list is an arrow redrawn before the node it pointed at was saved.\n\n"
        "The recursive version — swap the first two, recurse on the rest — is shorter and uses "
        "O(n) stack."
    ),
    py='''
def solve(head):
    dummy = ListNode(0, head)
    prev = dummy
    while prev.next and prev.next.next:
        a = prev.next
        b = a.next
        prev.next = b
        a.next = b.next
        b.next = a
        prev = a
    return dummy.next
''',
    java='''
    static ListNode solve(ListNode head) {
        ListNode dummy = new ListNode(0, head), prev = dummy;
        while (prev.next != null && prev.next.next != null) {
            ListNode a = prev.next, b = a.next;
            prev.next = b;
            a.next = b.next;
            b.next = a;
            prev = a;
        }
        return dummy.next;
    }
''',
    examples=[("Example 1", "4\n1 2 3 4\n"), ("Example 2", "0\n\n")],
    hidden=[
        ("Single node", "1\n1\n"),
        ("Odd length", "3\n1 2 3\n"),
        ("Six nodes", "6\n1 2 3 4 5 6\n"),
    ],
    expl=[
        "Pairs (1,2) and (3,4) each swap.",
        "Nothing to swap.",
    ],
    prereqs=[
        ("list_basics", "Relinking three pointers per pair without losing the rest of the list."),
        ("list_reversal", "The same save-then-redirect discipline as reversing a list."),
    ],
)

_p(
    "rotate-list", "Rotate List", "Medium",
    topics=["Linked Lists"], subtopics=["Two Pointers"], companies=["Microsoft", "LinkedIn"],
    shape="list_k", ret="ListNode", todo="find length and tail; k %= n; link tail to head; cut after node n − k − 1",
    description=(
        "Rotate a linked list to the **right** by `k` places: the last `k` nodes move to the "
        "front, in order.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` values.\n- Line 3: `k`.\n\n"
        "### Output\nThe rotated list, or `EMPTY`."
    ),
    constraints="0 ≤ n ≤ 500\n-100 ≤ value ≤ 100\n0 ≤ k ≤ 2·10^9",
    hints=[
        "Rotating by n does nothing, so only k mod n matters — k can be two billion.",
        "Walk once to find the length n and the tail.",
        "Link the tail to the head, making a ring. The new tail is node n − k − 1 (0-indexed) from the old head: cut after it.",
    ],
    opt=("O(n)", "O(1)", "One pass for the length, one partial pass to the cut point."),
    editorial=(
        "## The one thing this teaches\n**Close the ring, then cut it.** Rotation of an array is "
        "awkward in place; rotation of a *ring* is just choosing where the list starts. Linking "
        "the tail back to the head costs one assignment, and the rotation becomes \"break the ring "
        "after the right node\".\n\n"
        "## Approach\n```java\nif (head == null) return null;\nint n = 1;\nListNode tail = head;\n"
        "while (tail.next != null) { tail = tail.next; n++; }\nk %= n;\nif (k == 0) return head;\n"
        "tail.next = head;                                   // ring\nListNode newTail = head;\n"
        "for (int i = 0; i < n - k - 1; i++) newTail = newTail.next;\n"
        "ListNode newHead = newTail.next;\nnewTail.next = null;                                // cut\nreturn newHead;\n```\n\n"
        "## The modulus first\nWithout `k %= n`, a k of 2·10⁹ walks the ring two billion times. And "
        "`n` must be computed before the modulus, so an empty list is handled before dividing by "
        "zero."
    ),
    py='''
def solve(head, k):
    if not head:
        return None
    n = 1
    tail = head
    while tail.next:
        tail = tail.next
        n += 1
    k %= n
    if k == 0:
        return head
    tail.next = head
    new_tail = head
    for _ in range(n - k - 1):
        new_tail = new_tail.next
    new_head = new_tail.next
    new_tail.next = None
    return new_head
''',
    java='''
    static ListNode solve(ListNode head, int k) {
        if (head == null) return null;
        int n = 1;
        ListNode tail = head;
        while (tail.next != null) { tail = tail.next; n++; }
        k %= n;
        if (k == 0) return head;
        tail.next = head;
        ListNode newTail = head;
        for (int i = 0; i < n - k - 1; i++) newTail = newTail.next;
        ListNode newHead = newTail.next;
        newTail.next = null;
        return newHead;
    }
''',
    examples=[("Example 1", "5\n1 2 3 4 5\n2\n"), ("Example 2", "3\n0 1 2\n4\n")],
    hidden=[
        ("Empty list", "0\n\n5\n"),
        ("Single node", "1\n1\n99\n"),
        ("Full rotation", "4\n1 2 3 4\n4\n"),
        ("Huge k", "4\n1 2 3 4\n2000000001\n"),
    ],
    expl=[
        "The last two nodes, 4 and 5, move to the front.",
        "Rotating 3 nodes by 4 is rotating by 1.",
    ],
    prereqs=[
        ("list_basics", "Finding the length and tail, then relinking the ring at a new point."),
        ("modulo", "Only k mod n rotations have any effect."),
    ],
)

_p(
    "partition-list", "Partition List", "Medium",
    topics=["Linked Lists"], subtopics=["Dummy Head", "Two Pointers"], companies=["Amazon", "Bloomberg"],
    shape="list_k", ret="ListNode", todo="append nodes < k to one dummy-headed list and the rest to another, then join",
    description=(
        "Rearrange a linked list so that every node with value **less than `k`** comes before every "
        "node with value **at least `k`**. Within each group, keep the original order.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` values.\n- Line 3: `k`.\n\n"
        "### Output\nThe partitioned list, or `EMPTY`."
    ),
    constraints="0 ≤ n ≤ 200\n-100 ≤ value ≤ 100\n-200 ≤ k ≤ 200",
    hints=[
        "Swapping values around in place makes keeping the order hard.",
        "Build two lists as you walk: one of the small nodes, one of the rest, each appended at its tail.",
        "Dummy heads for both avoid empty-list checks. Join small's tail to big's head and END the big list with null.",
    ],
    opt=("O(n)", "O(1)", "Nodes are relinked, not copied; two dummy nodes are the only extra space."),
    editorial=(
        "## The one thing this teaches\n**Stability comes free when you append.** Appending each "
        "node at the tail of its group preserves the original relative order, with no bookkeeping. "
        "Two dummy heads make both groups uniform, even when one stays empty.\n\n"
        "## Approach\n```java\nListNode smallHead = new ListNode(0, null), bigHead = new ListNode(0, null);\n"
        "ListNode small = smallHead, big = bigHead;\nfor (ListNode p = head; p != null; p = p.next) {\n"
        "    if (p.val < k) { small.next = p; small = p; }\n    else          { big.next = p;   big = p; }\n}\n"
        "big.next = null;              // essential\nsmall.next = bigHead.next;\nreturn smallHead.next;\n```\n\n"
        "## The line that prevents a cycle\n`big.next = null`. The last big node still points to "
        "whatever followed it in the original list — often a small node that is now earlier in "
        "the result. Leaving it creates a cycle, and printing the list never ends.\n\n"
        "It is the stable-partition step of quicksort, on a list."
    ),
    py='''
def solve(head, k):
    small_head = ListNode(0)
    big_head = ListNode(0)
    small, big = small_head, big_head
    p = head
    while p:
        if p.val < k:
            small.next = p
            small = p
        else:
            big.next = p
            big = p
        p = p.next
    big.next = None
    small.next = big_head.next
    return small_head.next
''',
    java='''
    static ListNode solve(ListNode head, int k) {
        ListNode smallHead = new ListNode(0, null), bigHead = new ListNode(0, null);
        ListNode small = smallHead, big = bigHead;
        for (ListNode p = head; p != null; p = p.next) {
            if (p.val < k) { small.next = p; small = p; }
            else { big.next = p; big = p; }
        }
        big.next = null;
        small.next = bigHead.next;
        return smallHead.next;
    }
''',
    examples=[("Example 1", "6\n1 4 3 2 5 2\n3\n"), ("Example 2", "2\n2 1\n2\n")],
    hidden=[
        ("Empty list", "0\n\n0\n"),
        ("Nothing is small", "3\n5 6 7\n1\n"),
        ("Duplicates of k", "4\n3 1 3 0\n3\n"),
        ("Cycle trap", "4\n5 1 6 2\n3\n"),
    ],
    expl=[
        "Small nodes 1, 2, 2 in order, then 4, 3, 5 in order.",
        "1 moves before 2.",
    ],
    prereqs=[
        ("list_basics", "Appending nodes to the tail of two separate lists and joining them."),
        ("design_ds", "Dummy heads so both groups can start empty."),
    ],
)

_p(
    "sort-list", "Sort List", "Medium",
    topics=["Linked Lists", "Sorting"], subtopics=["Fast & Slow", "Sorting"], companies=["Meta", "Microsoft", "Apple"],
    shape="list", ret="ListNode", todo="merge sort: split at the middle with slow/fast pointers, sort both halves, merge",
    description=(
        "Sort a linked list in ascending order in O(n log n) time, relinking nodes rather than "
        "copying values into an array.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` values.\n\n"
        "### Output\nThe sorted list, or `EMPTY`."
    ),
    constraints="0 ≤ n ≤ 5·10^4\n-10^5 ≤ value ≤ 10^5",
    hints=[
        "Quicksort needs random access to pick pivots well; merge sort only needs to split and merge — both natural on lists.",
        "Split: slow/fast pointers find the middle; cut the list there.",
        "Merge: the Merge Two Sorted Lists routine, with a dummy head.",
    ],
    opt=("O(n log n)", "O(log n)", "Top-down merge sort; the recursion depth is log n. Bottom-up merging makes it O(1)."),
    editorial=(
        "## The one thing this teaches\n**Merge sort is the list's sort.** Arrays favour quicksort "
        "for its cache behaviour; lists have no cache behaviour to protect and no random access "
        "for pivots, but splitting at the middle and merging two sorted lists are both linear and "
        "in-place. So merge sort gets O(n log n) with no extra array.\n\n"
        "## Approach\n```java\nListNode sort(ListNode head) {\n"
        "    if (head == null || head.next == null) return head;\n"
        "    ListNode slow = head, fast = head.next;          // fast starts one ahead\n"
        "    while (fast != null && fast.next != null) { slow = slow.next; fast = fast.next.next; }\n"
        "    ListNode right = slow.next;\n    slow.next = null;                                // cut\n"
        "    return merge(sort(head), sort(right));\n}\n```\n\n"
        "## Why `fast = head.next`\nWith two nodes and `fast = head`, `slow` advances to the second "
        "node, `right` is null, and the left half is the whole list again — infinite recursion. "
        "Starting `fast` one ahead makes `slow` stop at the *first* middle, so both halves shrink."
    ),
    py='''
def solve(head):
    def merge(a, b):
        dummy = tail = ListNode(0)
        while a and b:
            if a.val <= b.val:
                tail.next, a = a, a.next
            else:
                tail.next, b = b, b.next
            tail = tail.next
        tail.next = a or b
        return dummy.next

    def sort(h):
        if not h or not h.next:
            return h
        slow, fast = h, h.next
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        right = slow.next
        slow.next = None
        return merge(sort(h), sort(right))

    return sort(head)
''',
    java='''
    static ListNode merge(ListNode a, ListNode b) {
        ListNode dummy = new ListNode(0, null), tail = dummy;
        while (a != null && b != null) {
            if (a.val <= b.val) { tail.next = a; a = a.next; }
            else { tail.next = b; b = b.next; }
            tail = tail.next;
        }
        tail.next = a != null ? a : b;
        return dummy.next;
    }

    static ListNode solve(ListNode head) {
        if (head == null || head.next == null) return head;
        ListNode slow = head, fast = head.next;
        while (fast != null && fast.next != null) { slow = slow.next; fast = fast.next.next; }
        ListNode right = slow.next;
        slow.next = null;
        return merge(solve(head), solve(right));
    }
''',
    examples=[("Example 1", "4\n4 2 1 3\n"), ("Example 2", "5\n-1 5 3 4 0\n")],
    hidden=[
        ("Empty list", "0\n\n"),
        ("Single node", "1\n7\n"),
        ("Duplicates", "6\n3 3 1 1 2 2\n"),
        ("Two nodes out of order", "2\n2 1\n"),
    ],
    expl=[
        "Ascending order.",
        "Negatives sort first.",
    ],
    prereqs=[
        ("fast_slow", "Slow and fast pointers find the middle node to split at."),
        ("sorting", "Merge sort's split-and-merge, which needs no random access."),
    ],
)

_p(
    "sum-root-to-leaf", "Sum Root to Leaf Numbers", "Medium",
    topics=["Trees"], subtopics=["Tree DFS"], companies=["Google", "Meta"],
    shape="tree", ret="long", todo="DFS carrying value = value × 10 + node.val; add it at each leaf",
    description=(
        "Every node holds a digit `0`–`9`. Each root-to-leaf path spells a number (root digit "
        "first). Print the sum of all those numbers.\n\n"
        "### Input\nOne line: the tree in level order, `null` for a missing child.\n\n### Output\nThe sum."
    ),
    constraints="1 ≤ nodes ≤ 1000\n0 ≤ value ≤ 9\nThe depth is at most 10.",
    hints=[
        "The number at a node is (number at its parent) × 10 + its digit.",
        "Pass that number down the recursion instead of building strings.",
        "Add it to the total only at a leaf — a node with no children.",
    ],
    opt=("O(n)", "O(h)", "Each node visited once, carrying one number."),
    editorial=(
        "## The one thing this teaches\n**Pass state down, not up.** Most tree recursions return a "
        "value from the children. Here the useful value flows the other way: each node needs the "
        "number built by its ancestors, so it is an argument.\n\n"
        "## Approach\n```java\nlong dfs(TreeNode t, long above) {\n    if (t == null) return 0;\n"
        "    long cur = above * 10 + t.val;\n"
        "    if (t.left == null && t.right == null) return cur;     // leaf: a finished number\n"
        "    return dfs(t.left, cur) + dfs(t.right, cur);\n}\n```\n\n"
        "## Only leaves count\nA node with one child is not the end of a path. Adding `cur` at every "
        "node, or at every null, double-counts or counts paths that stop early — for `1 → 0`, the "
        "answer is 10, not 11."
    ),
    py='''
def solve(root):
    total = 0
    st = [(root, 0)]
    while st:
        t, above = st.pop()
        cur = above * 10 + t.val
        if not t.left and not t.right:
            total += cur
        if t.left:
            st.append((t.left, cur))
        if t.right:
            st.append((t.right, cur))
    return total
''',
    java='''
    static long dfs(TreeNode t, long above) {
        if (t == null) return 0;
        long cur = above * 10 + t.val;
        if (t.left == null && t.right == null) return cur;
        return dfs(t.left, cur) + dfs(t.right, cur);
    }

    static long solve(TreeNode root) {
        return dfs(root, 0);
    }
''',
    examples=[("Example 1", "1 2 3\n"), ("Example 2", "4 9 0 5 1\n")],
    hidden=[
        ("Single node", "5\n"),
        ("Zeros matter", "1 0 null 0\n"),
        ("Only one child", "1 0\n"),
        ("Deep path", "9 9 null 9 null 9 null 9\n"),
    ],
    expl=[
        "12 + 13 = 25.",
        "495 + 491 + 40 = 1026.",
    ],
    prereqs=[
        ("tree_traversal", "A DFS that passes the number built so far down to each child."),
        ("math_digits", "Appending a digit with value × 10 + d."),
    ],
)

_p(
    "count-good-nodes", "Count Good Nodes in a Binary Tree", "Medium",
    topics=["Trees"], subtopics=["Tree DFS"], companies=["Microsoft", "Amazon"],
    shape="tree", ret="int", todo="DFS carrying the maximum value on the path from the root",
    description=(
        "A node is **good** if no node on the path from the root to it has a **greater** value. "
        "Count the good nodes.\n\n"
        "### Input\nOne line: the tree in level order, `null` for a missing child.\n\n"
        "### Output\nThe number of good nodes."
    ),
    constraints="1 ≤ nodes ≤ 10^5\n-10^4 ≤ value ≤ 10^4",
    hints=[
        "Whether a node is good depends only on the largest value above it.",
        "Carry that maximum down the DFS.",
        "A node is good when its value ≥ the maximum so far; the maximum passed to its children includes it.",
    ],
    opt=("O(n)", "O(h)", "One traversal carrying one value."),
    editorial=(
        "## The one thing this teaches\n**Summarise the path in one number.** \"No ancestor is "
        "greater\" sounds like it needs the whole path, but only its maximum matters. A single "
        "value passed down replaces a list of ancestors.\n\n"
        "## Approach\n```java\nint dfs(TreeNode t, int maxAbove) {\n    if (t == null) return 0;\n"
        "    int good = t.val >= maxAbove ? 1 : 0;\n    int m = Math.max(maxAbove, t.val);\n"
        "    return good + dfs(t.left, m) + dfs(t.right, m);\n}\n// call with dfs(root, Integer.MIN_VALUE)\n```\n\n"
        "## Equal counts as good\nThe condition is \"no node is *greater*\", so equal values are "
        "fine — `>=`. And the root is always good, which starting from `MIN_VALUE` gives for free, "
        "even with negative values."
    ),
    py='''
def solve(root):
    good = 0
    st = [(root, -10 ** 9)]
    while st:
        t, m = st.pop()
        if t.val >= m:
            good += 1
        m = max(m, t.val)
        if t.left:
            st.append((t.left, m))
        if t.right:
            st.append((t.right, m))
    return good
''',
    java='''
    static int solve(TreeNode root) {
        int good = 0;
        ArrayDeque<Object[]> st = new ArrayDeque<>();
        st.push(new Object[]{root, Integer.MIN_VALUE});
        while (!st.isEmpty()) {
            Object[] top = st.pop();
            TreeNode t = (TreeNode) top[0];
            int m = (Integer) top[1];
            if (t.val >= m) good++;
            m = Math.max(m, t.val);
            if (t.left != null) st.push(new Object[]{t.left, m});
            if (t.right != null) st.push(new Object[]{t.right, m});
        }
        return good;
    }
''',
    examples=[("Example 1", "3 1 4 3 null 1 5\n"), ("Example 2", "3 3 null 4 2\n")],
    hidden=[
        ("Single node", "1\n"),
        ("Mixed", "5 4 6 3 null null 7\n"),
        ("All negative", "-1 -2 -3\n"),
    ],
    expl=[
        "The root 3, the 3 below its left child, 4, and 5 are good.",
        "3, the second 3 (equal is fine) and 4.",
    ],
    prereqs=[
        ("tree_traversal", "A DFS that carries the maximum value on the current path."),
        ("prefix_max", "A running maximum, along a root-to-node path instead of an array."),
    ],
)

_p(
    "max-width-binary-tree", "Maximum Width of a Binary Tree", "Medium",
    topics=["Trees"], subtopics=["Tree BFS"], companies=["Amazon", "Google"],
    shape="tree", ret="long", todo="BFS with positions (children of p are 2p and 2p+1); width = last − first + 1 per level",
    description=(
        "The width of a level is the distance between its leftmost and rightmost **non-null** "
        "nodes, counting the null positions between them as if the tree were complete. Find the "
        "maximum width over all levels.\n\n"
        "### Input\nOne line: the tree in level order, `null` for a missing child.\n\n"
        "### Output\nThe maximum width."
    ),
    constraints="1 ≤ nodes ≤ 3000\nThe answer fits in a signed 32-bit integer.",
    hints=[
        "Number positions as in a heap: the children of position p are 2p and 2p + 1.",
        "BFS level by level; a level's width is (last position − first position + 1).",
        "Positions double per level and overflow in a deep chain. Subtract the level's first position before computing children.",
    ],
    opt=("O(n)", "O(w)", "One BFS; the queue holds one level."),
    editorial=(
        "## The one thing this teaches\n**Index the tree as if it were an array.** A complete "
        "binary tree stored in an array puts node p's children at 2p and 2p + 1. Giving every "
        "real node that index measures gaps without ever creating null nodes.\n\n"
        "## Approach\n```java\nqueue of (node, pos), starting (root, 0)\nwhile (queue not empty) {\n"
        "    size = queue.size(); first = pos of the first entry;\n"
        "    for each entry in this level:\n        last = pos;\n"
        "        rel = pos - first;                       // normalise\n"
        "        add (left, 2*rel), (right, 2*rel + 1)\n    best = max(best, last - first + 1);\n}\n```\n\n"
        "## Why normalise\nOn a 3000-node chain of right children, the raw position at the bottom "
        "is 2³⁰⁰⁰ — no integer type holds it. Subtracting the level's first position keeps every "
        "position below the level's width, which the statement promises fits in 32 bits, so the "
        "children fit in a `long`."
    ),
    py='''
def solve(root):
    best = 0
    level = [(root, 0)]
    while level:
        first = level[0][1]
        last = level[-1][1]
        best = max(best, last - first + 1)
        nxt = []
        for node, pos in level:
            rel = pos - first
            if node.left:
                nxt.append((node.left, 2 * rel))
            if node.right:
                nxt.append((node.right, 2 * rel + 1))
        level = nxt
    return best
''',
    java='''
    static long solve(TreeNode root) {
        long best = 0;
        ArrayDeque<TreeNode> nodes = new ArrayDeque<>();
        ArrayDeque<Long> pos = new ArrayDeque<>();
        nodes.add(root);
        pos.add(0L);
        while (!nodes.isEmpty()) {
            int size = nodes.size();
            long first = pos.peekFirst(), last = first;
            for (int i = 0; i < size; i++) {
                TreeNode t = nodes.poll();
                long p = pos.poll();
                last = p;
                long rel = p - first;
                if (t.left != null) { nodes.add(t.left); pos.add(2 * rel); }
                if (t.right != null) { nodes.add(t.right); pos.add(2 * rel + 1); }
            }
            best = Math.max(best, last - first + 1);
        }
        return best;
    }
''',
    examples=[("Example 1", "1 3 2 5 3 null 9\n"), ("Example 2", "1 3 2 5 null null 9 6 null 7\n")],
    hidden=[
        ("Single node", "1\n"),
        ("One child", "1 2\n"),
        ("Gap in the middle", "1 2 3 4 null null 5\n"),
        ("Right chain", "1 null 2 null 3 null 4 null 5\n"),
    ],
    expl=[
        "The third level spans positions 0 to 3: width 4.",
        "The fourth level spans from 6 to 7 with six null positions between: width 7.",
    ],
    prereqs=[
        ("tree_traversal", "Level-order BFS, processing one level at a time."),
        ("overflow", "Heap-style positions double per level, so they are normalised to stay bounded."),
    ],
)

_p(
    "house-robber-iii", "House Robber III (Houses in a Tree)", "Medium",
    topics=["Trees", "Dynamic Programming"], subtopics=["Tree DP", "Tree DFS"], companies=["Uber", "Google"],
    shape="tree", ret="long", todo="post-order returning (best if robbed, best if skipped) for each subtree",
    description=(
        "Houses form a binary tree; robbing two houses joined by an edge (a parent and its child) "
        "sets off the alarm. What is the most money you can take?\n\n"
        "### Input\nOne line: the tree in level order, `null` for a missing child.\n\n"
        "### Output\nThe maximum total."
    ),
    constraints="1 ≤ nodes ≤ 10^4\n0 ≤ value ≤ 10^4",
    hints=[
        "Greedy by level (all even levels or all odd levels) fails: the best set can mix levels.",
        "For each node, compute two values: the best of its subtree if it is robbed, and if it is not.",
        "rob(t) = t.val + skip(left) + skip(right); skip(t) = best(left) + best(right), where best = max(rob, skip).",
    ],
    opt=("O(n)", "O(h)", "One post-order traversal returning a pair per node."),
    editorial=(
        "## The one thing this teaches\n**Tree DP returns more than one value.** A single \"best "
        "for this subtree\" is not enough to decide the parent, because the parent needs to know "
        "what the child's subtree is worth *without* the child. Returning both states makes each "
        "subtree self-describing.\n\n"
        "## Approach\n```java\nlong[] dfs(TreeNode t) {                 // {robbed, skipped}\n"
        "    if (t == null) return new long[]{0, 0};\n"
        "    long[] l = dfs(t.left), r = dfs(t.right);\n"
        "    long robbed = t.val + l[1] + r[1];\n"
        "    long skipped = Math.max(l[0], l[1]) + Math.max(r[0], r[1]);\n"
        "    return new long[]{robbed, skipped};\n}\nanswer = max(dfs(root))\n```\n\n"
        "## Why levels fail\nIn `4 → 1 → 2 → 3` (a chain), the best is 4 + 3 = 7: two nodes at "
        "depths 0 and 3, neither \"all even\" nor \"all odd\" levels.\n\n"
        "The memoised version that recurses into grandchildren also works, but visits each node "
        "several times; the pair return visits each once."
    ),
    py='''
def solve(root):
    import sys
    sys.setrecursionlimit(20000)

    def dfs(t):
        if not t:
            return (0, 0)
        l = dfs(t.left)
        r = dfs(t.right)
        robbed = t.val + l[1] + r[1]
        skipped = max(l) + max(r)
        return (robbed, skipped)

    return max(dfs(root))
''',
    java='''
    static long[] dfs(TreeNode t) {
        if (t == null) return new long[]{0, 0};
        long[] l = dfs(t.left), r = dfs(t.right);
        long robbed = t.val + l[1] + r[1];
        long skipped = Math.max(l[0], l[1]) + Math.max(r[0], r[1]);
        return new long[]{robbed, skipped};
    }

    static long solve(TreeNode root) {
        long[] res = dfs(root);
        return Math.max(res[0], res[1]);
    }
''',
    examples=[("Example 1", "3 2 3 null 3 null 1\n"), ("Example 2", "3 4 5 1 3 null 1\n")],
    hidden=[
        ("Single house", "5\n"),
        ("Chain mixes levels", "4 1 null 2 null 3\n"),
        ("Children beat the root", "2 1 3 null 4\n"),
    ],
    expl=[
        "Rob the root and both grandchildren: 3 + 3 + 1 = 7.",
        "Rob the two children: 4 + 5 = 9.",
    ],
    prereqs=[
        ("tree_dp", "Each subtree returns its best total with and without its root."),
        ("dp", "House Robber's take-or-skip choice, applied on a tree."),
    ],
)

_p(
    "binary-tree-tilt", "Binary Tree Tilt", "Easy",
    topics=["Trees"], subtopics=["Tree DFS"], companies=["Indeed"],
    shape="tree", ret="long", todo="post-order: return each subtree's sum, adding |left sum − right sum| to a total",
    description=(
        "A node's **tilt** is the absolute difference between the sum of its left subtree and the "
        "sum of its right subtree (an empty subtree sums to 0). Print the sum of every node's "
        "tilt.\n\n"
        "### Input\nOne line: the tree in level order, `null` for a missing child.\n\n"
        "### Output\nThe total tilt."
    ),
    constraints="1 ≤ nodes ≤ 10^4\n-1000 ≤ value ≤ 1000",
    hints=[
        "Computing each subtree's sum from scratch at every node is O(n²).",
        "A post-order traversal can return the subtree sum, which the parent needs anyway.",
        "Return sum = left + right + val, and add |left − right| to an accumulator on the way.",
    ],
    opt=("O(n)", "O(h)", "One post-order traversal."),
    editorial=(
        "## The one thing this teaches\n**Return one thing, accumulate another.** The recursion "
        "returns what the parent needs (the subtree sum) while adding what the answer needs (the "
        "tilt) to a total on the side. Mixing the two into one return value is where these "
        "solutions go wrong.\n\n"
        "## Approach\n```java\nlong total = 0;\nlong sum(TreeNode t) {\n    if (t == null) return 0;\n"
        "    long l = sum(t.left), r = sum(t.right);\n    total += Math.abs(l - r);\n"
        "    return l + r + t.val;\n}\n```\n\n"
        "## The quadratic trap\nCalling a separate `subtreeSum` for each node's two children "
        "recomputes the same sums at every ancestor: O(n²) on a chain. The same shape as Balanced "
        "Binary Tree calling `height` at every node."
    ),
    py='''
def solve(root):
    import sys
    sys.setrecursionlimit(30000)
    total = 0

    def s(t):
        nonlocal total
        if not t:
            return 0
        l = s(t.left)
        r = s(t.right)
        total += abs(l - r)
        return l + r + t.val

    s(root)
    return total
''',
    java='''
    static long total = 0;

    static long sum(TreeNode t) {
        if (t == null) return 0;
        long l = sum(t.left), r = sum(t.right);
        total += Math.abs(l - r);
        return l + r + t.val;
    }

    static long solve(TreeNode root) {
        total = 0;
        sum(root);
        return total;
    }
''',
    examples=[("Example 1", "1 2 3\n"), ("Example 2", "4 2 9 3 5 null 7\n")],
    hidden=[
        ("Full tree", "21 7 14 1 1 2 2 3 3\n"),
        ("Single node", "5\n"),
        ("Left chain", "1 2 null 3\n"),
        ("Negative values", "-5 3 -4\n"),
    ],
    expl=[
        "Only the root tilts: |2 − 3| = 1.",
        "Node 2 tilts |3 − 5| = 2, node 9 tilts |0 − 7| = 7, and the root |10 − 16| = 6: 15.",
    ],
    prereqs=[
        ("tree_traversal", "A post-order traversal returning subtree sums."),
        ("tree_dp", "Returning one value to the parent while accumulating another answer."),
    ],
)
