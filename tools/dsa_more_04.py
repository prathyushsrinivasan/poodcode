# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 4 — stacks, queues and deques.
#
#   backspace-string-compare     a stack of survivors — or two pointers from the back
#   simplify-path                a stack of directory names; ".." pops
#   decode-string                two stacks: repeat counts and the text built before each "["
#   asteroid-collision           a stack that the incoming element fights
#   sum-subarray-minimums        each element's contribution, bounded by monotonic stacks
#   recent-calls                 a queue that expires from the front
#   first-unique-in-stream       a queue plus counts, cleaned lazily
#   jump-game-vi                 DP whose max over a sliding range is a monotonic deque
#   shortest-subarray-at-least-k a monotonic deque of prefix sums, with negatives
# ===========================================================================

_p(
    "backspace-string-compare", "Backspace String Compare", "Easy",
    topics=["Stack", "Strings"], subtopics=["Stack", "Two Pointers"], companies=["Google", "Meta"],
    shape="str2", ret="String", todo="build each typed result with a stack (or compare from the back), then compare",
    description=(
        "Two strings are typed into editors where `#` is a **backspace**. Backspace on an empty "
        "line does nothing. Are the two final texts equal?\n\n"
        "### Input\n- Line 1: `s`.\n- Line 2: `t`.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ |s|, |t| ≤ 200\nBoth consist of lowercase letters and '#'.",
    hints=[
        "A backspace deletes the most recent surviving character — that is a stack's pop.",
        "Build both results with a StringBuilder used as a stack, then compare.",
        "O(1) space: walk both strings from the END, counting pending backspaces to skip characters.",
    ],
    opt=("O(|s| + |t|)", "O(1)", "Two pointers from the back, each skipping characters erased by later backspaces."),
    editorial=(
        "## The one thing this teaches\n**A stack of survivors — and when you can do without "
        "it.** Reading forwards, a `#` erases the top of what you have typed, so a stack models "
        "the editor exactly. Reading *backwards*, you know how many backspaces are pending before "
        "you meet the characters they erase, so a counter replaces the stack.\n\n"
        "## Approach — from the back\n```java\nint i = s.length() - 1, j = t.length() - 1;\n"
        "while (i >= 0 || j >= 0) {\n    i = nextKept(s, i);\n    j = nextKept(t, j);\n"
        "    if (i < 0 || j < 0) return i == j ? \"YES\" : \"NO\";\n"
        "    if (s.charAt(i) != t.charAt(j)) return \"NO\";\n    i--; j--;\n}\nreturn \"YES\";\n```\n\n"
        "`nextKept` walks left from `i`: a `#` adds one to a skip count, a letter with a positive "
        "skip count is erased, and the first letter with no skip pending is returned.\n\n"
        "## The trap\nComparing as soon as one string runs out: `a#` and `` are equal, and so are "
        "`ab##` and `c#d#`. Both pointers must be advanced past erased characters *before* "
        "deciding that one side is empty."
    ),
    py='''
def solve(s, t):
    def typed(x):
        st = []
        for ch in x:
            if ch == "#":
                if st:
                    st.pop()
            else:
                st.append(ch)
        return "".join(st)
    return "YES" if typed(s) == typed(t) else "NO"
''',
    java='''
    static int nextKept(String s, int i) {
        int skip = 0;
        while (i >= 0) {
            if (s.charAt(i) == '#') { skip++; i--; }
            else if (skip > 0) { skip--; i--; }
            else break;
        }
        return i;
    }

    static String solve(String s, String t) {
        int i = s.length() - 1, j = t.length() - 1;
        while (i >= 0 || j >= 0) {
            i = nextKept(s, i);
            j = nextKept(t, j);
            if (i < 0 || j < 0) return i == j ? "YES" : "NO";
            if (s.charAt(i) != t.charAt(j)) return "NO";
            i--; j--;
        }
        return "YES";
    }
''',
    examples=[("Example 1", "ab#c\nad#c\n"), ("Example 2", "ab##\nc#d#\n")],
    hidden=[
        ("Different survivors", "a#c\nb\n"),
        ("Leading backspace does nothing", "a##c\n#a#c\n"),
        ("Long equal", "bxj##tw\nbxo#j##tw\n"),
        ("One erased character differs", "bbbextm\nbbb#extm\n"),
    ],
    expl=[
        "Both become `ac`.",
        "Both become empty.",
    ],
    prereqs=[
        ("stack", "A backspace pops the most recent surviving character."),
        ("two_pointers", "Scanning both strings from the end with a pending-backspace count instead of a stack."),
    ],
)

_p(
    "simplify-path", "Simplify Path", "Medium",
    topics=["Stack", "Strings"], subtopics=["Stack"], companies=["Meta", "Microsoft"],
    shape="str", ret="String", todo="split on '/', push names, pop on '..', ignore '' and '.'",
    description=(
        "Simplify an absolute Unix path. `.` means the current directory, `..` the parent (the "
        "root's parent is the root), and repeated slashes count as one. Any other name — "
        "including `...` — is a directory.\n\n"
        "### Input\nOne line: the path, starting with `/`.\n\n"
        "### Output\nThe canonical path: starts with `/`, no trailing slash (unless it is `/`)."
    ),
    constraints="1 ≤ |path| ≤ 3000\nThe path contains letters, digits, '.', '_' and '/', and starts with '/'.",
    hints=[
        "Split on '/'. Empty parts come from repeated or trailing slashes and are ignored, like '.'.",
        "Each real name is pushed. '..' pops, if there is anything to pop.",
        "Join the stack from bottom to top with '/' between names and one in front.",
    ],
    opt=("O(n)", "O(n)", "One split and one pass; the stack holds at most n/2 names."),
    editorial=(
        "## The one thing this teaches\n**A stack of context you can back out of.** Walking into "
        "a directory pushes it; `..` leaves the most recent one. That is the same last-in, "
        "first-out shape as brackets — only the tokens are words.\n\n"
        "## Approach\n```java\nDeque<String> st = new ArrayDeque<>();\n"
        "for (String part : path.split(\"/\")) {\n"
        "    if (part.isEmpty() || part.equals(\".\")) continue;\n"
        "    if (part.equals(\"..\")) { if (!st.isEmpty()) st.pollLast(); }\n"
        "    else st.addLast(part);\n}\n"
        "StringBuilder out = new StringBuilder();\nfor (String d : st) out.append('/').append(d);\n"
        "return out.length() == 0 ? \"/\" : out.toString();\n```\n\n"
        "Using the deque's *last* end as the top means iterating it front-to-back yields the path "
        "in order — no reversal.\n\n"
        "## The cases that decide it\n- `..` at the root stays at the root.\n"
        "- `...` and `..a` are ordinary names: compare whole tokens, never prefixes.\n"
        "- An empty result is `/`, not the empty string."
    ),
    py='''
def solve(s):
    st = []
    for part in s.split("/"):
        if part == "" or part == ".":
            continue
        if part == "..":
            if st:
                st.pop()
        else:
            st.append(part)
    return "/" + "/".join(st)
''',
    java='''
    static String solve(String path) {
        Deque<String> st = new ArrayDeque<>();
        for (String part : path.split("/")) {
            if (part.isEmpty() || part.equals(".")) continue;
            if (part.equals("..")) { if (!st.isEmpty()) st.pollLast(); }
            else st.addLast(part);
        }
        StringBuilder out = new StringBuilder();
        for (String d : st) out.append('/').append(d);
        return out.length() == 0 ? "/" : out.toString();
    }
''',
    examples=[("Example 1", "/home/\n"), ("Example 2", "/a/./b/../../c/\n")],
    hidden=[
        ("Above the root", "/../\n"),
        ("Repeated slashes", "/home//foo/\n"),
        ("Three dots is a name", "/.../a/../b\n"),
        ("Back to the root", "/a/b/../../\n"),
        ("Mixed", "/a/../../b/../c//.//\n"),
    ],
    expl=[
        "The trailing slash goes.",
        "Into `a`, into `b`, out twice, into `c`.",
    ],
    prereqs=[
        ("stack", "Directory names pushed on entry and popped by '..'."),
        ("string_basics", "Splitting on '/' and comparing whole tokens, so '...' is a name and not a parent."),
    ],
)

_p(
    "decode-string", "Decode String", "Medium",
    topics=["Stack", "Strings"], subtopics=["Stack"], companies=["Google", "Amazon", "Bloomberg"],
    shape="str", ret="String", todo="on '[' push the count and the text so far; on ']' pop and repeat",
    description=(
        "Decode a string where `k[text]` means `text` repeated `k` times. Encodings can be "
        "**nested**: `3[a2[c]]` is `accaccacc`.\n\n"
        "### Input\nOne line: the encoded string.\n\n### Output\nThe decoded string."
    ),
    constraints=(
        "1 ≤ |s| ≤ 30\ns contains lowercase letters, digits and square brackets, and is valid.\n"
        "1 ≤ k ≤ 300. Digits only appear as repeat counts. The decoded length is at most 10^5."
    ),
    hints=[
        "When you meet '[', the text built so far must be put aside until the matching ']'.",
        "Keep two stacks: one of repeat counts, one of the text that came before each '['.",
        "On ']': pop the count and the earlier text; the new current text is earlier + current repeated. Counts can have several digits.",
    ],
    opt=("O(output)", "O(output)", "Each character of the decoded string is written a bounded number of times per nesting level."),
    editorial=(
        "## The one thing this teaches\n**A stack saves the context you are about to leave.** "
        "Entering `[` starts a new, inner piece of text; the outer text and its repeat count must "
        "survive until the matching `]`. Pushing both, and popping them back, is recursion done "
        "by hand.\n\n"
        "## Approach\n```java\nDeque<Integer> counts = new ArrayDeque<>();\n"
        "Deque<StringBuilder> outer = new ArrayDeque<>();\nStringBuilder cur = new StringBuilder();\nint k = 0;\n"
        "for (char c : s.toCharArray()) {\n"
        "    if (Character.isDigit(c)) k = k * 10 + (c - '0');\n"
        "    else if (c == '[') { counts.push(k); outer.push(cur); cur = new StringBuilder(); k = 0; }\n"
        "    else if (c == ']') {\n"
        "        StringBuilder prev = outer.pop();\n"
        "        prev.append(cur.toString().repeat(counts.pop()));\n"
        "        cur = prev;\n    }\n    else cur.append(c);\n}\n```\n\n"
        "## The two bugs\n- Reading only one digit: `10[a]` is ten `a`s, so accumulate `k` until the `[`.\n"
        "- Forgetting to reset `k` after pushing it, which makes the next count start from the old value.\n\n"
        "The recursive version — parse a sequence until `]`, returning where you stopped — is "
        "equally good, and is what this stack simulates."
    ),
    py='''
def solve(s):
    counts, outer = [], []
    cur = []
    k = 0
    for ch in s:
        if ch.isdigit():
            k = k * 10 + int(ch)
        elif ch == "[":
            counts.append(k)
            outer.append(cur)
            cur = []
            k = 0
        elif ch == "]":
            rep = counts.pop()
            prev = outer.pop()
            prev.append("".join(cur) * rep)
            cur = prev
        else:
            cur.append(ch)
    return "".join(cur)
''',
    java='''
    static String solve(String s) {
        Deque<Integer> counts = new ArrayDeque<>();
        Deque<StringBuilder> outer = new ArrayDeque<>();
        StringBuilder cur = new StringBuilder();
        int k = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c >= '0' && c <= '9') k = k * 10 + (c - '0');
            else if (c == '[') { counts.push(k); outer.push(cur); cur = new StringBuilder(); k = 0; }
            else if (c == ']') {
                StringBuilder prev = outer.pop();
                String inner = cur.toString();
                int rep = counts.pop();
                for (int r = 0; r < rep; r++) prev.append(inner);
                cur = prev;
            }
            else cur.append(c);
        }
        return cur.toString();
    }
''',
    examples=[("Example 1", "3[a]2[bc]\n"), ("Example 2", "3[a2[c]]\n")],
    hidden=[
        ("Text around groups", "2[abc]3[cd]ef\n"),
        ("No encoding", "abc\n"),
        ("Two-digit count", "10[a]\n"),
        ("Nested with a tail", "2[b3[a]]c\n"),
    ],
    expl=[
        "`aaa` then `bcbc`.",
        "`2[c]` is `cc`, so the group is `acc`, three times.",
    ],
    prereqs=[
        ("stack", "Two stacks save the repeat count and the outer text at each '['."),
        ("recursion", "The stack simulates a recursive parse of a nested structure."),
    ],
)

_p(
    "asteroid-collision", "Asteroid Collision", "Medium",
    topics=["Stack", "Arrays"], subtopics=["Stack", "Simulation"], companies=["Amazon", "Lyft", "Uber"],
    shape="arr", ret="String", todo="push right-movers; a left-mover destroys smaller right-movers on top of the stack",
    description=(
        "Asteroids move along a line at the same speed: a positive value moves right, a negative "
        "one left, and the absolute value is its size. When two meet, the smaller explodes; equal "
        "sizes both explode. Asteroids moving the same way never meet.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` non-zero integers, left to right.\n\n"
        "### Output\nThe surviving asteroids in order, separated by spaces, or `EMPTY`."
    ),
    constraints="1 ≤ n ≤ 10^4\n-1000 ≤ a[i] ≤ 1000, a[i] ≠ 0",
    hints=[
        "A collision only happens when a right-mover is to the LEFT of a left-mover.",
        "Process left to right, keeping survivors on a stack. Only a new left-mover can hit anything — the right-movers on top.",
        "A left-mover keeps destroying smaller right-movers until it meets a bigger or equal one, a left-mover, or an empty stack.",
    ],
    opt=("O(n)", "O(n)", "Each asteroid is pushed once and popped at most once."),
    editorial=(
        "## The one thing this teaches\n**The newcomer fights the top of the stack.** Survivors so "
        "far are settled among themselves; a new asteroid can only collide with the most recent "
        "right-mover, and if it wins, with the one beneath it — which is exactly a pop loop.\n\n"
        "## Approach\n```java\nDeque<Integer> st = new ArrayDeque<>();   // use the last end as top\n"
        "for (int x : a) {\n    boolean alive = true;\n"
        "    while (alive && x < 0 && !st.isEmpty() && st.peekLast() > 0) {\n"
        "        if (st.peekLast() < -x) { st.pollLast(); continue; }   // top explodes, keep fighting\n"
        "        if (st.peekLast() == -x) st.pollLast();                // both explode\n"
        "        alive = false;                                         // newcomer is gone\n    }\n"
        "    if (alive) st.addLast(x);\n}\n```\n\n"
        "## The cases that decide it\n- `-2 -1 1 2`: nothing collides — left-movers on the left "
        "are moving *away*.\n"
        "- `1 -2 -2 -2`: the first `-2` destroys the `1` and survives; the next `-2`s find a "
        "left-mover on top and simply join the stack."
    ),
    py='''
def solve(a):
    st = []
    for x in a:
        alive = True
        while alive and x < 0 and st and st[-1] > 0:
            if st[-1] < -x:
                st.pop()
                continue
            if st[-1] == -x:
                st.pop()
            alive = False
        if alive:
            st.append(x)
    return " ".join(map(str, st)) if st else "EMPTY"
''',
    java='''
    static String solve(int[] a) {
        Deque<Integer> st = new ArrayDeque<>();
        for (int x : a) {
            boolean alive = true;
            while (alive && x < 0 && !st.isEmpty() && st.peekLast() > 0) {
                if (st.peekLast() < -x) { st.pollLast(); continue; }
                if (st.peekLast() == -x) st.pollLast();
                alive = false;
            }
            if (alive) st.addLast(x);
        }
        if (st.isEmpty()) return "EMPTY";
        StringBuilder sb = new StringBuilder();
        for (int v : st) { if (sb.length() > 0) sb.append(' '); sb.append(v); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "3\n5 10 -5\n"), ("Example 2", "2\n8 -8\n")],
    hidden=[
        ("Chain reaction", "3\n10 2 -5\n"),
        ("Moving apart", "4\n-2 -1 1 2\n"),
        ("Winner joins the left-movers", "4\n1 -2 -2 -2\n"),
        ("Mixed", "5\n-2 2 -1 -2 3\n"),
    ],
    expl=[
        "`-5` meets `10` and explodes; `5` and `10` never meet.",
        "Equal sizes: both explode.",
    ],
    prereqs=[
        ("stack", "Survivors on a stack; the incoming asteroid pops what it destroys."),
        ("simulation", "Only an opposite-direction pair with the right-mover on the left ever collides."),
    ],
)

_p(
    "sum-subarray-minimums", "Sum of Subarray Minimums", "Hard",
    topics=["Stack", "Arrays"], subtopics=["Monotonic Stack"], companies=["Amazon", "Google"],
    shape="arr", ret="long", todo="for each a[i], count subarrays where it is the minimum using previous-less and next-less-or-equal",
    description=(
        "Sum the **minimum** of every contiguous subarray. Print the sum modulo `10^9 + 7`.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` positive integers.\n\n"
        "### Output\nThe sum of all subarray minimums, mod `10^9 + 7`."
    ),
    constraints="1 ≤ n ≤ 3·10^4\n1 ≤ a[i] ≤ 3·10^4",
    hints=[
        "Turn it around: for each element, in how many subarrays is it the minimum?",
        "a[i] is the minimum of subarrays that start after the previous smaller element and end before the next smaller one: left × right of them.",
        "With equal values, count each subarray once: stop at a strictly smaller element on one side and at a smaller-or-equal one on the other.",
    ],
    opt=("O(n)", "O(n)", "Two monotonic-stack passes find each element's boundaries; then one pass sums contributions."),
    editorial=(
        "## The one thing this teaches\n**Contribution counting.** Summing over n² subarrays "
        "directly is too slow; summing over n elements \"how much does this one contribute\" is "
        "not. Element `a[i]` is the minimum of exactly `left[i] × right[i]` subarrays, where "
        "`left[i]` is how far it can extend left before meeting something smaller, and likewise "
        "right.\n\n"
        "## Approach\n```java\n// left[i]: distance to the previous STRICTLY smaller element\n"
        "for (int i = 0; i < n; i++) {\n"
        "    while (!st.isEmpty() && a[st.peek()] >= a[i]) st.pop();\n"
        "    left[i] = i - (st.isEmpty() ? -1 : st.peek());\n    st.push(i);\n}\n"
        "// right[i]: distance to the next smaller-OR-EQUAL element\n"
        "for (int i = n - 1; i >= 0; i--) {\n"
        "    while (!st.isEmpty() && a[st.peek()] > a[i]) st.pop();\n"
        "    right[i] = (st.isEmpty() ? n : st.peek()) - i;\n    st.push(i);\n}\n"
        "sum = Σ a[i] · left[i] · right[i]   (mod 1e9+7)\n```\n\n"
        "## Why the asymmetric comparison\nIn `[2, 2]`, the subarray `[2, 2]` has two equal "
        "minimums. Using \"strictly smaller\" on both sides credits it to both, and using "
        "\"smaller-or-equal\" on both credits it to neither. Strict on one side and non-strict on "
        "the other assigns every subarray to exactly one element — the leftmost or rightmost of "
        "the tied minimums.\n\n"
        "## Overflow\n`a[i] · left · right` reaches 3·10⁴ · 3·10⁴ · 3·10⁴ ≈ 2.7·10¹³: a `long` "
        "holds it, then take the modulus."
    ),
    py='''
def solve(a):
    MOD = 10 ** 9 + 7
    n = len(a)
    left = [0] * n
    right = [0] * n
    st = []
    for i in range(n):
        while st and a[st[-1]] >= a[i]:
            st.pop()
        left[i] = i - (st[-1] if st else -1)
        st.append(i)
    st = []
    for i in range(n - 1, -1, -1):
        while st and a[st[-1]] > a[i]:
            st.pop()
        right[i] = (st[-1] if st else n) - i
        st.append(i)
    return sum(a[i] * left[i] * right[i] for i in range(n)) % MOD
''',
    java='''
    static long solve(int[] a) {
        final long MOD = 1_000_000_007L;
        int n = a.length;
        int[] left = new int[n], right = new int[n];
        int[] st = new int[n];
        int top = 0;
        for (int i = 0; i < n; i++) {
            while (top > 0 && a[st[top - 1]] >= a[i]) top--;
            left[i] = i - (top == 0 ? -1 : st[top - 1]);
            st[top++] = i;
        }
        top = 0;
        for (int i = n - 1; i >= 0; i--) {
            while (top > 0 && a[st[top - 1]] > a[i]) top--;
            right[i] = (top == 0 ? n : st[top - 1]) - i;
            st[top++] = i;
        }
        long sum = 0;
        for (int i = 0; i < n; i++) sum = (sum + (long) a[i] * left[i] % MOD * right[i]) % MOD;
        return sum;
    }
''',
    examples=[("Example 1", "4\n3 1 2 4\n"), ("Example 2", "5\n11 81 94 43 3\n")],
    hidden=[
        ("Single element", "1\n5\n"),
        ("All equal", "3\n2 2 2\n"),
        ("Increasing", "4\n1 2 3 4\n"),
        ("Decreasing", "4\n4 3 2 1\n"),
    ],
    expl=[
        "Minimums of the 10 subarrays: 3 1 2 4, 1 1 2, 1 1, 1 — they sum to 17.",
        "The 15 subarray minimums sum to 444.",
    ],
    prereqs=[
        ("stack", "Monotonic stacks find each element's previous smaller and next smaller-or-equal element."),
        ("modulo", "Reducing the running sum modulo 1e9+7 after each contribution."),
    ],
)

_p(
    "recent-calls", "Number of Recent Calls", "Easy",
    topics=["Data Structures", "Arrays"], subtopics=["Queue"], companies=["Yandex", "Google"],
    shape="arr", ret="String", todo="append each time; drop times older than t − 3000 from the front; report the size",
    description=(
        "Calls arrive at strictly increasing times (in milliseconds). After each call at time `t`, "
        "report how many calls happened in the window `[t − 3000, t]`, including this one.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` strictly increasing times.\n\n"
        "### Output\nThe `n` counts, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 10^4\n1 ≤ t ≤ 10^9, strictly increasing",
    hints=[
        "Times only increase, so once a call is too old it stays too old forever.",
        "Keep recent calls in a queue: add at the back, expire from the front.",
        "After expiring, the queue's size is the answer. Note the window includes t − 3000 itself.",
    ],
    opt=("O(n)", "O(W)", "Each time is added once and removed once; the queue holds only the calls in the current window."),
    editorial=(
        "## The one thing this teaches\n**A queue is a window over time.** When events arrive in "
        "order and expire in the same order, the oldest event is always the next to expire — "
        "first in, first out.\n\n"
        "## Approach\n```java\nDeque<Integer> q = new ArrayDeque<>();\n"
        "for (int t : times) {\n    q.addLast(t);\n"
        "    while (q.peekFirst() < t - 3000) q.pollFirst();\n    out.add(q.size());\n}\n```\n\n"
        "Amortised O(1) per call: a call can be polled many times *in total* only once.\n\n"
        "## Boundaries\nThe window is inclusive, so a call at exactly `t − 3000` still counts — "
        "the condition to expire is `< t − 3000`, not `<=`. With times that were not sorted, the "
        "front would not be the oldest and a heap or a sorted structure would be needed."
    ),
    py='''
def solve(a):
    q = deque()
    out = []
    for t in a:
        q.append(t)
        while q[0] < t - 3000:
            q.popleft()
        out.append(len(q))
    return " ".join(map(str, out))
''',
    java='''
    static String solve(int[] times) {
        Deque<Integer> q = new ArrayDeque<>();
        StringBuilder sb = new StringBuilder();
        for (int t : times) {
            q.addLast(t);
            while (q.peekFirst() < t - 3000) q.pollFirst();
            if (sb.length() > 0) sb.append(' ');
            sb.append(q.size());
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "4\n1 100 3001 3002\n"), ("Example 2", "3\n1 5000 9000\n")],
    hidden=[
        ("Single call", "1\n7\n"),
        ("Burst", "5\n1 2 3 4 5\n"),
        ("Exactly on the boundary", "4\n3000 6000 6001 9001\n"),
    ],
    expl=[
        "At 3001 the window is [1, 3001], which still includes the call at 1. At 3002 that call has expired.",
        "The calls are more than 3000 ms apart.",
    ],
    prereqs=[
        ("queue", "Recent calls in arrival order, expiring from the front."),
        ("sliding_window", "A window defined by time rather than by index."),
    ],
)

_p(
    "first-unique-in-stream", "First Unique Number in a Stream", "Medium",
    topics=["Data Structures", "Hashing"], subtopics=["Queue", "Hashing"], companies=["Amazon", "Bloomberg"],
    shape="arr", ret="String", todo="count arrivals; queue candidates; before answering, drop the front while its count exceeds 1",
    description=(
        "Numbers arrive one at a time. After each arrival, report the **earliest-arrived** value "
        "that has so far occurred exactly once, or `-1` if every value has repeated.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` values in arrival order.\n\n"
        "### Output\nThe `n` answers, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 10^5\n-10^8 ≤ a[i] ≤ 10^8",
    hints=[
        "Scanning all values after every arrival is O(n²).",
        "Unique values in arrival order form a queue — and a value, once repeated, never becomes unique again.",
        "Enqueue each first arrival. Before answering, pop from the front while the front's count is above 1. Popped values never need to return.",
    ],
    opt=("O(n)", "O(n)", "Each value enters and leaves the queue at most once; counts are a hash map."),
    editorial=(
        "## The one thing this teaches\n**Lazy deletion from a queue.** A value stops being "
        "unique somewhere in the *middle* of the queue, and queues cannot delete from the middle. "
        "They do not need to: the value is harmless until it reaches the front, and when it does, "
        "one count check discards it.\n\n"
        "## Approach\n```java\nMap<Integer, Integer> count = new HashMap<>();\n"
        "Deque<Integer> q = new ArrayDeque<>();\nfor (int x : a) {\n"
        "    if (count.merge(x, 1, Integer::sum) == 1) q.addLast(x);\n"
        "    while (!q.isEmpty() && count.get(q.peekFirst()) > 1) q.pollFirst();\n"
        "    out.add(q.isEmpty() ? -1 : q.peekFirst());\n}\n```\n\n"
        "## Why it is correct\nUniqueness is monotone here: a count only grows, so a value that "
        "has repeated can never be the answer again, and discarding it permanently loses nothing. "
        "Without that property — if values could also be *removed* — lazy deletion would not be "
        "enough, and an ordered map from value to arrival time would take its place."
    ),
    py='''
def solve(a):
    count = defaultdict(int)
    q = deque()
    out = []
    for x in a:
        count[x] += 1
        if count[x] == 1:
            q.append(x)
        while q and count[q[0]] > 1:
            q.popleft()
        out.append(q[0] if q else -1)
    return " ".join(map(str, out))
''',
    java='''
    static String solve(int[] a) {
        Map<Integer, Integer> count = new HashMap<>();
        Deque<Integer> q = new ArrayDeque<>();
        StringBuilder sb = new StringBuilder();
        for (int x : a) {
            if (count.merge(x, 1, Integer::sum) == 1) q.addLast(x);
            while (!q.isEmpty() && count.get(q.peekFirst()) > 1) q.pollFirst();
            if (sb.length() > 0) sb.append(' ');
            sb.append(q.isEmpty() ? -1 : q.peekFirst());
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "6\n2 3 5 5 2 3\n"), ("Example 2", "4\n7 7 7 7\n")],
    hidden=[
        ("Single value", "1\n4\n"),
        ("Front changes twice", "5\n1 2 1 3 2\n"),
        ("Negative values and -1 answers", "6\n-1 0 -1 0 5 5\n"),
    ],
    expl=[
        "2 stays first until it repeats, then 3, which repeats at the end, leaving nothing.",
        "The second 7 makes the only value non-unique.",
    ],
    prereqs=[
        ("queue", "Candidates in arrival order, with non-unique ones discarded lazily at the front."),
        ("hashing", "A count per value, checked when a candidate reaches the front."),
    ],
)

_p(
    "jump-game-vi", "Jump Game VI (Max Score)", "Medium",
    topics=["Data Structures", "Dynamic Programming"], subtopics=["Queue", "1D DP"], companies=["Google", "Amazon"],
    shape="arr_k", ret="long", todo="dp[i] = a[i] + max(dp[i−k..i−1]); keep that max in a monotonic deque of indices",
    description=(
        "Start at index 0. From index `i` you may jump to any index from `i + 1` to `i + k`. Your "
        "score is the sum of the values at every index you land on, including 0 and the last "
        "index. Reach index `n − 1` with the **maximum** score.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` integers.\n\n### Output\nThe maximum score."
    ),
    constraints="1 ≤ n, k ≤ 10^5\n-10^4 ≤ a[i] ≤ 10^4",
    hints=[
        "dp[i] = a[i] + max(dp[j]) over j in [i − k, i − 1]. Computing that max by scanning is O(n·k).",
        "The range slides forward by one each step: a sliding-window maximum.",
        "Keep indices in a deque with decreasing dp values; drop the front when it falls out of range.",
    ],
    opt=("O(n)", "O(k)", "Each index enters and leaves the deque once; the deque spans at most k indices."),
    editorial=(
        "## The one thing this teaches\n**DP + sliding window maximum.** The recurrence is easy; "
        "its transition asks for the max over the last k states, and a window that slides by one "
        "is exactly what the monotonic deque from *Sliding Window Maximum* answers in O(1) "
        "amortised.\n\n"
        "## Approach\n```java\nlong[] dp = new long[n];\nDeque<Integer> dq = new ArrayDeque<>();\n"
        "dp[0] = a[0];\ndq.addLast(0);\nfor (int i = 1; i < n; i++) {\n"
        "    while (dq.peekFirst() < i - k) dq.pollFirst();          // out of reach\n"
        "    dp[i] = a[i] + dp[dq.peekFirst()];\n"
        "    while (!dq.isEmpty() && dp[dq.peekLast()] <= dp[i]) dq.pollLast();  // dominated\n"
        "    dq.addLast(i);\n}\nreturn dp[n - 1];\n```\n\n"
        "## Why dominated states can go\nIf `j < i` and `dp[j] ≤ dp[i]`, then every future index "
        "that can reach `j` can also reach `i` (it is later), and `i` is at least as good. So `j` "
        "will never be the best choice again.\n\n"
        "## Greedy does not work\nJumping to the next non-negative value, or to the largest "
        "value in reach, fails on inputs where a small loss now avoids a large one later — which "
        "is what makes this DP."
    ),
    py='''
def solve(a, k):
    n = len(a)
    dp = [0] * n
    dp[0] = a[0]
    dq = deque([0])
    for i in range(1, n):
        while dq[0] < i - k:
            dq.popleft()
        dp[i] = a[i] + dp[dq[0]]
        while dq and dp[dq[-1]] <= dp[i]:
            dq.pop()
        dq.append(i)
    return dp[n - 1]
''',
    java='''
    static long solve(int[] a, long k) {
        int n = a.length;
        long[] dp = new long[n];
        int[] dq = new int[n];
        int head = 0, tail = 0;
        dp[0] = a[0];
        dq[tail++] = 0;
        for (int i = 1; i < n; i++) {
            while (dq[head] < i - k) head++;
            dp[i] = a[i] + dp[dq[head]];
            while (tail > head && dp[dq[tail - 1]] <= dp[i]) tail--;
            dq[tail++] = i;
        }
        return dp[n - 1];
    }
''',
    examples=[("Example 1", "6 2\n1 -1 -2 4 -7 3\n"), ("Example 2", "6 3\n10 -5 -2 4 0 3\n")],
    hidden=[
        ("Single index", "1 1\n5\n"),
        ("Must step on everything", "5 1\n1 -1 -1 -1 1\n"),
        ("Avoid the big losses", "8 2\n1 -5 -20 4 -1 3 -6 -3\n"),
        ("Reach covers the end", "3 5\n-3 -3 -3\n"),
    ],
    expl=[
        "0 → 1 → 3 → 5: 1 − 1 + 4 + 3 = 7.",
        "0 → 3 → 5 jumps over both negatives: 10 + 4 + 3 = 17.",
    ],
    prereqs=[
        ("dp", "dp[i] is the best score landing on i, built from the best of the previous k states."),
        ("queue", "A monotonic deque keeps the maximum of a sliding range of dp values."),
    ],
)

_p(
    "shortest-subarray-at-least-k", "Shortest Subarray With Sum at Least K", "Hard",
    topics=["Data Structures", "Prefix Sum"], subtopics=["Queue", "Prefix Sum"], companies=["Google", "Goldman Sachs"],
    shape="arr_k", ret="long", todo="over prefix sums, keep a deque of increasing prefixes; pop the front while it forms a valid subarray",
    description=(
        "Find the length of the shortest non-empty contiguous subarray whose sum is **at least** "
        "`k`. The array may contain **negative** numbers.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe shortest length, or `-1` if no subarray qualifies."
    ),
    constraints="1 ≤ n ≤ 10^5\n-10^5 ≤ a[i] ≤ 10^5\n1 ≤ k ≤ 10^9",
    hints=[
        "With negatives, the two-pointer window breaks: shrinking can increase the sum. Work with prefix sums P.",
        "You want, for each j, the latest i < j with P[j] − P[i] ≥ k. Keep candidate i's in a deque with increasing P.",
        "From the front: while P[j] − P[front] ≥ k, record j − front and pop it (a later j would only be longer). From the back: pop any i with P[i] ≥ P[j].",
    ],
    opt=("O(n)", "O(n)", "Every prefix index enters and leaves the deque at most once."),
    editorial=(
        "## The one thing this teaches\n**When the window breaks, keep the candidates that could "
        "still win.** With non-negative numbers this is a sliding window. Negatives destroy the "
        "monotonicity the window relies on — but a deque of prefix-sum indices restores it by "
        "discarding starts that can never be the best.\n\n"
        "## Approach\n```java\nlong[] P = new long[n + 1];\nfor (int i = 0; i < n; i++) P[i + 1] = P[i] + a[i];\n"
        "Deque<Integer> dq = new ArrayDeque<>();\nint best = n + 1;\nfor (int j = 0; j <= n; j++) {\n"
        "    while (!dq.isEmpty() && P[j] - P[dq.peekFirst()] >= k) best = Math.min(best, j - dq.pollFirst());\n"
        "    while (!dq.isEmpty() && P[dq.peekLast()] >= P[j]) dq.pollLast();\n    dq.addLast(j);\n}\n"
        "return best <= n ? best : -1;\n```\n\n"
        "## The two pruning rules\n- **Back:** if `i < j` and `P[i] ≥ P[j]`, then `j` is a better "
        "start than `i` for every future end — it is later (shorter) and its prefix is no larger "
        "(bigger sum). `i` can go.\n"
        "- **Front:** once `front` pairs validly with `j`, pairing it with any later end is longer. "
        "Record it and pop.\n\n"
        "Together they keep the deque's prefix sums strictly increasing, which is what lets the "
        "front test stop at the first failure."
    ),
    py='''
def solve(a, k):
    n = len(a)
    P = [0] * (n + 1)
    for i, x in enumerate(a):
        P[i + 1] = P[i] + x
    dq = deque()
    best = n + 1
    for j in range(n + 1):
        while dq and P[j] - P[dq[0]] >= k:
            best = min(best, j - dq.popleft())
        while dq and P[dq[-1]] >= P[j]:
            dq.pop()
        dq.append(j)
    return best if best <= n else -1
''',
    java='''
    static long solve(int[] a, long k) {
        int n = a.length;
        long[] P = new long[n + 1];
        for (int i = 0; i < n; i++) P[i + 1] = P[i] + a[i];
        int[] dq = new int[n + 1];
        int head = 0, tail = 0, best = n + 1;
        for (int j = 0; j <= n; j++) {
            while (tail > head && P[j] - P[dq[head]] >= k) best = Math.min(best, j - dq[head++]);
            while (tail > head && P[dq[tail - 1]] >= P[j]) tail--;
            dq[tail++] = j;
        }
        return best <= n ? best : -1;
    }
''',
    examples=[("Example 1", "3 3\n2 -1 2\n"), ("Example 2", "2 4\n1 2\n")],
    hidden=[
        ("Single element", "1 1\n1\n"),
        ("Negative in the middle", "6 10\n1 2 3 -10 4 6\n"),
        ("All negative", "3 100\n-1 -2 -3\n"),
        ("Large first element", "4 5\n84 -37 32 40\n"),
        ("Dip then climb", "7 9\n5 -20 3 3 3 -1 4\n"),
    ],
    expl=[
        "Only the whole array reaches 3.",
        "The total is 3.",
    ],
    prereqs=[
        ("prefix_sum", "Subarray sums as differences of prefix sums, which negatives do not break."),
        ("queue", "A monotonic deque of prefix indices, pruned from both ends."),
    ],
)
