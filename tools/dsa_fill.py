# -*- coding: utf-8 -*-
# ===========================================================================
# Fill problems — the last four units under their weight band.
#
# exec'd inside gen_seed.py's namespace right after dsa_depth.py, extending
# DEFS / JAVA_STARTERS / PREREQS in place and defining FILL_REFS (merged into
# REFERENCE_SOLUTIONS, so `verify_seeds` proves each is judged correctly in
# both shipped languages).
#
# After dsa_depth.py the generator's ledger still listed four thin units:
#
#   complexity   3 problems, band 5-9   — and none where the quadratic idea is
#                                         wrong rather than merely slow
#   sorting      4, band 5-9            — and no comparator with a tie-break
#   stacks       6, band 8-14           — no stack of characters, no evaluator
#   recursion    3, band 5-9            — nothing with two recursive calls
#
# Seven problems, each chosen for the idea its unit was missing rather than as
# another instance of one it had:
#
#   sum-of-pair-products        carry what the inner loop recomputes
#   sum-abs-differences         sort first, and the absolute value disappears
#   leaderboard-ranks           a comparator with a tie-break, and shared ranks
#   remove-adjacent-duplicates  the stack as "the part of the string still alive"
#   evaluate-rpn                the stack as an evaluator
#   binomial-coefficient        a recurrence with two terms, straight from Pascal
#   tower-of-hanoi              two recursive calls, and output that is 2ⁿ − 1 long
# ===========================================================================


def _fl(inp):
    return inp.strip().split("\n")


def _fnums(line):
    return list(map(int, line.split()))


# ---------------------------------------------------------------------------
# Reference solutions (raw stdin string -> exact stdout string)
# ---------------------------------------------------------------------------

def sol_sum_of_pair_products(inp):
    ls = _fl(inp)
    a = _fnums(ls[1])
    total = 0
    before = 0
    for x in a:
        total += x * before
        before += x
    return str(total)


def sol_sum_abs_differences(inp):
    ls = _fl(inp)
    a = sorted(_fnums(ls[1]))
    total = 0
    before = 0
    for j, x in enumerate(a):
        total += x * j - before
        before += x
    return str(total)


def sol_leaderboard_ranks(inp):
    ls = _fl(inp)
    n = int(ls[0])
    rows = []
    for i in range(n):
        name, score = ls[1 + i].split()
        rows.append((name, int(score)))
    rows.sort(key=lambda r: (-r[1], r[0]))
    out = []
    rank = 0
    for i, (name, score) in enumerate(rows):
        if i == 0 or score != rows[i - 1][1]:
            rank = i + 1
        out.append(f"{rank} {name} {score}")
    return "\n".join(out)


def sol_remove_adjacent_duplicates(inp):
    s = inp.strip()
    st = []
    for ch in s:
        if st and st[-1] == ch:
            st.pop()
        else:
            st.append(ch)
    return "".join(st) if st else "EMPTY"


def _trunc_div(a, b):
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


def sol_evaluate_rpn(inp):
    ls = _fl(inp)
    tokens = ls[1].split()
    st = []
    for t in tokens:
        if t in ("+", "-", "*", "/"):
            b = st.pop()
            a = st.pop()
            if t == "+":
                st.append(a + b)
            elif t == "-":
                st.append(a - b)
            elif t == "*":
                st.append(a * b)
            else:
                st.append(_trunc_div(a, b))
        else:
            st.append(int(t))
    return str(st[-1])


def sol_binomial_coefficient(inp):
    n, k = _fnums(_fl(inp)[0])

    def c(n, k):
        if k == 0 or k == n:
            return 1
        return c(n - 1, k - 1) + c(n - 1, k)

    return str(c(n, k))


def sol_tower_of_hanoi(inp):
    n = int(_fl(inp)[0])
    moves = []

    def move(k, src, dst, via):
        if k == 0:
            return
        move(k - 1, src, via, dst)
        moves.append(f"{k} {src} {dst}")
        move(k - 1, via, dst, src)

    move(n, "A", "C", "B")
    return "\n".join([str(len(moves))] + moves)


# ---------------------------------------------------------------------------
# Problems
# ---------------------------------------------------------------------------

FILL_DEFS = [
    # =======================================================================
    # complexity
    # =======================================================================
    dict(
        slug="sum-of-pair-products", title="Sum of Pair Products", difficulty="Easy",
        topics=["Arrays", "Math"], subtopics=["Counting", "Prefix Sum"], companies=["Amazon"],
        description=(
            "Given `n` integers, compute the sum of `a[i] · a[j]` over every pair of indices "
            "`i < j`.\n\n"
            "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
            "### Output\nA single integer: the sum over all pairs."
        ),
        constraints="1 ≤ n ≤ 10^5\n-10^4 ≤ a[i] ≤ 10^4\nThe answer fits in a signed 64-bit integer.",
        hints=[
            "The two nested loops are correct. With n = 10⁵ they are about 5·10⁹ multiplications — too many.",
            "Fix j. The pairs ending at j contribute a[j]·a[0] + a[j]·a[1] + … + a[j]·a[j−1].",
            "That is a[j] times the sum of everything before it — and that sum can be carried, not recomputed.",
            "Use `long` for both the running sum and the total: eight values of 10⁴ already overflow an `int`.",
        ],
        opt=("O(n)", "O(1)",
             "One pass carrying the sum of the elements seen so far; each pair is counted exactly "
             "once, at the moment its later element arrives."),
        editorial=(
            "## The one thing this teaches\n**Carry what the inner loop recomputes.** The "
            "quadratic version is\n\n"
            "```java\nfor (int i = 0; i < n; i++)\n    for (int j = i + 1; j < n; j++)\n"
            "        total += (long) a[i] * a[j];\n```\n\n"
            "Swap the roles and read it from the other side: for each `j`, the inner loop adds "
            "`a[j] · (a[0] + … + a[j−1])`. That bracket is a prefix sum, and a prefix sum grows "
            "by one element per step — so it does not need a loop at all.\n\n"
            "## Approach\n```java\nlong before = 0, total = 0;\n"
            "for (int j = 0; j < n; j++) {\n    total += a[j] * before;\n    before += a[j];\n}\n```\n\n"
            "The order of the two lines is the correctness argument: `before` must not yet include "
            "`a[j]`, or every element would be paired with itself.\n\n"
            "## A second route to the same answer\n(Σa)² counts every ordered pair plus each "
            "`a[i]²` once, so the answer is `((Σa)² − Σa²) / 2`. It is also O(n), but it "
            "squares a sum that can reach 10⁹: 10¹⁸ still fits in a `long`, with less than a "
            "factor of ten to spare. The running version's values stay below about 5·10¹⁷ — "
            "prefer the formulation whose intermediates are smallest.\n\n"
            "## Why it is in the complexity unit\nNothing here is a data structure or a named "
            "technique. The only move is noticing that a loop's work is a quantity you can keep "
            "— which is the move behind prefix sums, Kadane, and most of what comes later."
        ),
        ref=sol_sum_of_pair_products,
        starter_py=(
            "import sys\n\nd = sys.stdin.read().split()\n"
            "n = int(d[0])\na = list(map(int, d[1:1 + n]))\n\n"
            "def solve(a):\n"
            "    # TODO: for each element, add it times the sum of everything before it\n"
            "    return 0\n\nprint(solve(a))\n"
        ),
        starter_js=(
            "const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);\n"
            "const n = d[0], a = d.slice(1, 1 + n);\n\n"
            "function solve(a) {\n"
            "  // TODO: carry the sum of everything before; use BigInt for the total\n"
            "  return 0n;\n}\n\nconsole.log(solve(a).toString());\n"
        ),
        cases=[
            ("example", "Example 1", "4\n1 2 3 4\n"),
            ("example", "Example 2", "3\n-1 2 -3\n"),
            ("hidden", "Single element", "1\n7\n"),
            ("hidden", "Overflows an int", "8\n10000 10000 10000 10000 10000 10000 10000 10000\n"),
            ("hidden", "Mostly zeros", "5\n0 0 5 0 0\n"),
            ("hidden", "Alternating signs", "4\n-10000 10000 -10000 10000\n"),
        ],
        example_expl=[
            "1·2 + 1·3 + 1·4 + 2·3 + 2·4 + 3·4 = 2 + 3 + 4 + 6 + 8 + 12 = 35.",
            "(−1)·2 + (−1)·(−3) + 2·(−3) = −2 + 3 − 6 = −5.",
        ],
    ),
    dict(
        slug="sum-abs-differences", title="Sum of Pairwise Distances", difficulty="Medium",
        topics=["Arrays", "Math"], subtopics=["Sorting", "Prefix Sum"], companies=["Google"],
        description=(
            "Given `n` integers, compute the sum of `|a[i] − a[j]|` over every pair of indices "
            "`i < j`.\n\n"
            "### Input\n- Line 1: `n`.\n- Line 2: `n` non-negative integers.\n\n"
            "### Output\nA single integer: the sum of all pairwise distances."
        ),
        constraints="1 ≤ n ≤ 10^5\n0 ≤ a[i] ≤ 10^6",
        hints=[
            "The absolute value is what stops the pair-products trick from working directly.",
            "The sum over pairs does not depend on the order of the array — so you are free to reorder it.",
            "Once sorted, a[j] ≥ a[i] for every i < j, and |a[j] − a[i]| is just a[j] − a[i].",
            "For each j that is a[j]·j minus the sum of the j elements before it. Carry that sum.",
        ],
        opt=("O(n log n)", "O(1)",
             "The sort dominates; the pass after it is linear. Counting sort over the value range "
             "would make it O(n + max a), which is not better at these limits."),
        editorial=(
            "## The one thing this teaches\n**When the answer does not depend on order, choose "
            "the order.** A sum over all pairs is the same whichever way the array is arranged, "
            "and sorted is the arrangement where `|a[j] − a[i]|` loses its absolute value.\n\n"
            "## Approach\nAfter sorting, every earlier element is ≤ `a[j]`, so the pairs ending "
            "at `j` contribute\n\n"
            "`(a[j] − a[0]) + (a[j] − a[1]) + … + (a[j] − a[j−1]) = a[j]·j − (a[0] + … + a[j−1])`\n\n"
            "```java\nArrays.sort(a);\nlong before = 0, total = 0;\n"
            "for (int j = 0; j < n; j++) {\n    total += (long) a[j] * j - before;\n"
            "    before += a[j];\n}\n```\n\n"
            "## Pricing it\nThe brute force is Θ(n²) — 5·10⁹ pairs at the limit. The sort costs "
            "O(n log n) and the rest is the pair-products pass again. Paying n log n to make an "
            "n² problem linear is one of the most common trades there is, and it is only allowed "
            "because the question is about the *set* of values, not their positions.\n\n"
            "## Overflow\n`a[j] * j` is up to 10⁶ · 10⁵ = 10¹¹, so cast before multiplying. The "
            "total is at most about 5·10¹⁵, comfortably inside a `long`."
        ),
        ref=sol_sum_abs_differences,
        starter_py=(
            "import sys\n\nd = sys.stdin.read().split()\n"
            "n = int(d[0])\na = list(map(int, d[1:1 + n]))\n\n"
            "def solve(a):\n"
            "    # TODO: sort, then add a[j] * j minus the sum of the elements before j\n"
            "    return 0\n\nprint(solve(a))\n"
        ),
        starter_js=(
            "const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);\n"
            "const n = d[0], a = d.slice(1, 1 + n);\n\n"
            "function solve(a) {\n"
            "  // TODO: sort numerically, then carry the prefix sum; use BigInt for the total\n"
            "  return 0n;\n}\n\nconsole.log(solve(a).toString());\n"
        ),
        cases=[
            ("example", "Example 1", "3\n1 4 2\n"),
            ("example", "Example 2", "4\n5 5 5 5\n"),
            ("hidden", "Single element", "1\n9\n"),
            ("hidden", "One wide pair", "2\n0 1000000\n"),
            ("hidden", "Unsorted with repeats", "5\n3 1 4 1 5\n"),
            ("hidden", "Two clusters", "6\n1000000 0 1000000 0 1000000 0\n"),
        ],
        example_expl=[
            "|1 − 4| + |1 − 2| + |4 − 2| = 3 + 1 + 2 = 6.",
            "Every pair is at distance 0.",
        ],
    ),
    # =======================================================================
    # sorting
    # =======================================================================
    dict(
        slug="leaderboard-ranks", title="Leaderboard With Shared Ranks", difficulty="Easy",
        topics=["Sorting", "Strings"], subtopics=["Sorting"], companies=["Microsoft"],
        description=(
            "Print a leaderboard. Players are ordered by **score, highest first**; players with "
            "equal scores are ordered by **name, alphabetically**.\n\n"
            "Ranks are shared on ties and then skip: scores `90, 80, 80, 70` get ranks "
            "`1, 2, 2, 4`.\n\n"
            "### Input\n- Line 1: `n`.\n- Next `n` lines: `name score`.\n\n"
            "### Output\n`n` lines, each `rank name score`, in leaderboard order."
        ),
        constraints="1 ≤ n ≤ 10^4\nNames are distinct, 1-20 lowercase letters.\n0 ≤ score ≤ 10^6",
        hints=[
            "Sort once with a comparator that compares scores first and names only when the scores are equal.",
            "Descending score: compare b's score to a's, not a's to b's.",
            "A player's rank is their 1-based position — unless they tie the player above, in which case they copy that player's rank.",
            "Use `Integer.compare`, not subtraction, in the comparator.",
        ],
        opt=("O(n log n)", "O(n)",
             "One sort with a two-key comparator, then one pass to assign ranks."),
        editorial=(
            "## The one thing this teaches\n**A comparator is a list of tie-breaks.** Compare "
            "the most important key; only if it is equal, compare the next.\n\n"
            "```java\nplayers.sort((a, b) -> {\n"
            "    if (a.score != b.score) return Integer.compare(b.score, a.score);  // high first\n"
            "    return a.name.compareTo(b.name);                                  // then A→Z\n"
            "});\n```\n\n"
            "or, with the library: `Comparator.comparingInt((P p) -> -p.score).thenComparing(p -> p.name)`.\n\n"
            "## Assigning ranks\nWalk the sorted list. The rank is `i + 1`, except when the score "
            "equals the previous player's, in which case it stays what it was:\n\n"
            "```java\nint rank = 0;\nfor (int i = 0; i < n; i++) {\n"
            "    if (i == 0 || players.get(i).score != players.get(i - 1).score) rank = i + 1;\n"
            "    System.out.println(rank + \" \" + players.get(i).name + \" \" + players.get(i).score);\n}\n```\n\n"
            "Using `rank + 1` instead of `i + 1` gives *dense* ranking (1, 2, 2, 3) — a "
            "different, also common, convention. Read which one the statement asks for.\n\n"
            "## The bug to avoid\n`return b.score - a.score` works for these limits and is a "
            "habit that overflows the day scores can be negative or near `Integer.MAX_VALUE`. "
            "`Integer.compare` costs nothing and never overflows."
        ),
        ref=sol_leaderboard_ranks,
        starter_py=(
            "import sys\n\nL = sys.stdin.read().strip().split('\\n')\n"
            "n = int(L[0])\nplayers = []\n"
            "for i in range(n):\n"
            "    name, score = L[1 + i].split()\n    players.append((name, int(score)))\n\n"
            "def solve(players):\n"
            "    # TODO: sort by score desc, then name asc; return lines 'rank name score'\n"
            "    return []\n\nprint('\\n'.join(solve(players)))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
            "const n = Number(L[0]);\n"
            "const players = L.slice(1, 1 + n).map(l => { const [name, s] = l.trim().split(/\\s+/); return { name, score: Number(s) }; });\n\n"
            "function solve(players) {\n"
            "  // TODO: sort by score desc, then name asc; return lines 'rank name score'\n"
            "  return [];\n}\n\nconsole.log(solve(players).join('\\n'));\n"
        ),
        cases=[
            ("example", "Example 1", "4\nzoe 80\namy 90\nbob 80\ncal 70\n"),
            ("example", "Example 2", "3\nkai 50\nana 50\nmei 50\n"),
            ("hidden", "Single player", "1\nsolo 0\n"),
            ("hidden", "Already in order, no ties", "3\na 3\nb 2\nc 1\n"),
            ("hidden", "Tie at the bottom", "4\ndan 100\neve 40\nfay 40\ngus 99\n"),
            ("hidden", "Two tie groups", "6\nf 5\ne 5\nd 7\nc 7\nb 7\na 1\n"),
        ],
        example_expl=[
            "amy leads with 90. bob and zoe tie on 80 and share rank 2, listed alphabetically. "
            "cal is fourth, not third — two players are ahead of the tie.",
            "Everyone ties, so everyone is rank 1, in alphabetical order.",
        ],
    ),
    # =======================================================================
    # stacks
    # =======================================================================
    dict(
        slug="remove-adjacent-duplicates", title="Remove Adjacent Duplicates", difficulty="Easy",
        topics=["Stack", "Strings"], subtopics=["Stack"], companies=["Meta"],
        description=(
            "Repeatedly delete two **adjacent, equal** letters from the string until no such pair "
            "remains. The final result is unique whichever pair you delete first.\n\n"
            "### Input\nOne line: the string `s`.\n\n"
            "### Output\nThe final string, or `EMPTY` if nothing is left."
        ),
        constraints="1 ≤ |s| ≤ 10^5\ns consists of lowercase English letters.",
        hints=[
            "Deleting a pair can make two letters that were apart become adjacent — `abba` → `aa` → nothing.",
            "Rescanning the string after every deletion is O(n²).",
            "Keep the letters that have survived so far in a stack. A new letter either cancels the top or goes on top.",
            "A `StringBuilder` is a perfectly good stack of characters: `charAt(length-1)`, `append`, `setLength(length-1)`.",
        ],
        opt=("O(n)", "O(n)",
             "Each letter is pushed once and popped at most once."),
        editorial=(
            "## The one thing this teaches\n**The stack is the part of the input still alive.** "
            "A letter can only ever cancel against the most recent surviving letter — the one "
            "directly to its left after all the deletions so far — and \"most recent surviving\" "
            "is exactly what the top of a stack is.\n\n"
            "## Approach\n```java\nStringBuilder st = new StringBuilder();\n"
            "for (char c : s.toCharArray()) {\n"
            "    int len = st.length();\n"
            "    if (len > 0 && st.charAt(len - 1) == c) st.setLength(len - 1);   // cancel\n"
            "    else st.append(c);                                                // survive\n}\n"
            "System.out.println(st.length() == 0 ? \"EMPTY\" : st);\n```\n\n"
            "Because the stack's contents are in left-to-right order, the survivors print "
            "directly — no reversal needed, which is the advantage of a builder over a `Deque`.\n\n"
            "## Why cascades come for free\n`abba`: push `a`, push `b`, `b` cancels `b`, and now "
            "the top is `a` again, so the final `a` cancels it. The \"deletion made new neighbours\" "
            "case that forces a rescan in the naive version is just the stack's top changing.\n\n"
            "## Recognising it\nAny rule of the form \"X cancels / merges with the previous "
            "surviving X\" — brackets, asteroid collisions, backspace characters in a typed "
            "string — is this stack."
        ),
        ref=sol_remove_adjacent_duplicates,
        starter_py=(
            "import sys\n\ns = sys.stdin.readline().strip()\n\n"
            "def solve(s):\n"
            "    # TODO: keep survivors on a stack; a letter equal to the top cancels it\n"
            "    return 'EMPTY'\n\nprint(solve(s))\n"
        ),
        starter_js=(
            "const s = require('fs').readFileSync(0, 'utf8').trim();\n\n"
            "function solve(s) {\n"
            "  // TODO: keep survivors on a stack; a letter equal to the top cancels it\n"
            "  return 'EMPTY';\n}\n\nconsole.log(solve(s));\n"
        ),
        cases=[
            ("example", "Example 1", "abbaca\n"),
            ("example", "Example 2", "azxxzy\n"),
            ("hidden", "One pair", "aa\n"),
            ("hidden", "Nothing to remove", "abc\n"),
            ("hidden", "Full cascade", "abccba\n"),
            ("hidden", "Odd run", "aaa\n"),
        ],
        example_expl=[
            "`bb` goes, leaving `aaca`; then `aa` goes, leaving `ca`.",
            "`xx` goes, which makes `zz` adjacent; that goes too, leaving `ay`.",
        ],
    ),
    dict(
        slug="evaluate-rpn", title="Evaluate Reverse Polish Notation", difficulty="Medium",
        topics=["Stack", "Strings"], subtopics=["Stack"], companies=["LinkedIn", "Amazon"],
        description=(
            "Evaluate an arithmetic expression written in **reverse Polish notation**, where "
            "every operator follows its two operands: `2 1 + 3 *` means `(2 + 1) * 3`.\n\n"
            "Operators are `+`, `-`, `*` and `/`. Division truncates toward zero, as Java's "
            "integer division does.\n\n"
            "### Input\n- Line 1: the number of tokens `n`.\n- Line 2: `n` tokens separated by "
            "spaces.\n\n### Output\nThe value of the expression."
        ),
        constraints=(
            "1 ≤ n ≤ 10^4\nEach number is an integer with |x| ≤ 10^4 (it may be negative, e.g. `-11`).\n"
            "The expression is valid, never divides by zero, and every intermediate value fits in a 64-bit integer."
        ),
        hints=[
            "Numbers wait; operators consume. Push every number.",
            "An operator pops two values. The FIRST pop is the RIGHT operand.",
            "`-11` is a number, not the operator `-` — check whether the token is exactly one of the four operator strings.",
            "When the tokens run out, the one value left on the stack is the answer.",
        ],
        opt=("O(n)", "O(n)",
             "One push or one pop-pop-push per token; the stack holds at most the numbers not yet consumed."),
        editorial=(
            "## The one thing this teaches\n**A stack evaluates what nesting describes.** Reverse "
            "Polish notation needs no brackets and no precedence rules, because the order of the "
            "tokens already says which operation happens first — and the stack is the machine "
            "that reads that order.\n\n"
            "## Approach\n```java\nDeque<Long> st = new ArrayDeque<>();\n"
            "for (String t : tokens) {\n"
            "    switch (t) {\n"
            "        case \"+\": { long b = st.pop(), a = st.pop(); st.push(a + b); break; }\n"
            "        case \"-\": { long b = st.pop(), a = st.pop(); st.push(a - b); break; }\n"
            "        case \"*\": { long b = st.pop(), a = st.pop(); st.push(a * b); break; }\n"
            "        case \"/\": { long b = st.pop(), a = st.pop(); st.push(a / b); break; }\n"
            "        default:  st.push(Long.parseLong(t));\n"
            "    }\n}\nSystem.out.println(st.pop());\n```\n\n"
            "## The two bugs\n- **Operand order.** `b` is popped first because it was pushed "
            "last, so `4 13 5 /` is `13 / 5`, not `5 / 13`. Addition and multiplication hide "
            "this bug; subtraction and division expose it.\n"
            "- **Negative numbers.** Testing `t.charAt(0) == '-'` to detect the operator "
            "misreads `-11`. Compare the whole token.\n\n"
            "## Where this goes next\nConverting ordinary infix (`(2 + 1) * 3`) into this form is "
            "the shunting-yard algorithm — a second stack, of operators. A calculator is those "
            "two stacks run one after the other."
        ),
        ref=sol_evaluate_rpn,
        starter_py=(
            "import sys\n\nL = sys.stdin.read().strip().split('\\n')\n"
            "tokens = L[1].split()\n\n"
            "def solve(tokens):\n"
            "    # TODO: push numbers; for an operator pop b, then a, push a op b\n"
            "    # (Python's // floors — Java's / truncates toward zero)\n"
            "    return 0\n\nprint(solve(tokens))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
            "const tokens = L[1].trim().split(/\\s+/);\n\n"
            "function solve(tokens) {\n"
            "  // TODO: push numbers; for an operator pop b, then a, push a op b (Math.trunc for /)\n"
            "  return 0;\n}\n\nconsole.log(solve(tokens));\n"
        ),
        cases=[
            ("example", "Example 1", "5\n2 1 + 3 *\n"),
            ("example", "Example 2", "5\n4 13 5 / +\n"),
            ("hidden", "Long expression with a negative", "13\n10 6 9 3 + -11 * / * 17 + 5 +\n"),
            ("hidden", "A lone number", "1\n42\n"),
            ("hidden", "Negative division truncates toward zero", "3\n-7 2 /\n"),
            ("hidden", "Operand order for subtraction", "3\n3 5 -\n"),
        ],
        example_expl=[
            "`2 1 +` is 3, then `3 3 *` is 9.",
            "`13 5 /` is 2 (truncated), then `4 2 +` is 6.",
        ],
    ),
    # =======================================================================
    # recursion
    # =======================================================================
    dict(
        slug="binomial-coefficient", title="Binomial Coefficient", difficulty="Easy",
        topics=["Math", "Recursion"], subtopics=["Recurrence"], companies=["Adobe"],
        description=(
            "Compute `C(n, k)` — the number of ways to choose `k` items from `n` — using "
            "**Pascal's rule**:\n\n"
            "`C(n, k) = C(n − 1, k − 1) + C(n − 1, k)`, with `C(n, 0) = C(n, n) = 1`.\n\n"
            "### Input\nOne line: `n k`.\n\n### Output\nThe value of `C(n, k)`."
        ),
        constraints="0 ≤ k ≤ n ≤ 20",
        hints=[
            "The rule is already a recursive function; write it down almost word for word.",
            "Two base cases: k == 0 and k == n. Both return 1.",
            "Pascal's rule says: either the n-th item is chosen (then pick k−1 of the rest) or it is not (pick k of the rest).",
            "At n ≤ 20 the plain recursion is fast enough. Ask yourself what would break at n = 60.",
        ],
        opt=("O(C(n, k))", "O(n)",
             "The plain recursion makes about 2·C(n, k) calls, at most ~370 000 for n = 20. A memo "
             "table makes it O(n·k); the multiplicative formula makes it O(k)."),
        editorial=(
            "## The one thing this teaches\n**A recurrence with two terms, read as a sentence.** "
            "To choose k of n items, look at the last item: either it is in the choice — pick "
            "k − 1 from the other n − 1 — or it is not — pick k from the other n − 1. Those "
            "cases are disjoint and cover everything, so the counts add.\n\n"
            "## Approach\n```java\nstatic long c(int n, int k) {\n"
            "    if (k == 0 || k == n) return 1;\n"
            "    return c(n - 1, k - 1) + c(n - 1, k);\n}\n```\n\n"
            "## Pricing it honestly\nEvery call either returns 1 or splits in two, and the leaves "
            "that return 1 add up to the answer. So the number of calls is about twice the answer: "
            "C(20, 10) = 184 756, and ~370 000 calls is nothing. But C(60, 30) is 1.2·10¹⁷ — the "
            "same code would never finish.\n\n"
            "The calls repeat: `c(18, 9)` is reached from both `c(19, 9)` and `c(19, 10)`. Storing "
            "each `(n, k)` the first time it is computed turns the exponential call tree into a "
            "table of n·k entries — Pascal's triangle — which is the first step from recursion "
            "into dynamic programming.\n\n"
            "## Why not the factorial formula\n`n! / (k! (n−k)!)` overflows a `long` at 21!. The "
            "additive rule never holds a value larger than the answer."
        ),
        ref=sol_binomial_coefficient,
        starter_py=(
            "import sys\n\nn, k = map(int, sys.stdin.read().split()[:2])\n\n"
            "def c(n, k):\n"
            "    # TODO: base cases k == 0 or k == n, else Pascal's rule\n"
            "    return 0\n\nprint(c(n, k))\n"
        ),
        starter_js=(
            "const [n, k] = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);\n\n"
            "function c(n, k) {\n"
            "  // TODO: base cases k == 0 or k == n, else Pascal's rule\n"
            "  return 0;\n}\n\nconsole.log(c(n, k));\n"
        ),
        cases=[
            ("example", "Example 1", "5 2\n"),
            ("example", "Example 2", "4 0\n"),
            ("hidden", "Largest input", "20 10\n"),
            ("hidden", "k equals n", "1 1\n"),
            ("hidden", "Ten choose three", "10 3\n"),
            ("hidden", "Zero choose zero", "0 0\n"),
        ],
        example_expl=[
            "C(5, 2) = C(4, 1) + C(4, 2) = 4 + 6 = 10 — the ten pairs from five items.",
            "There is exactly one way to choose nothing.",
        ],
    ),
    dict(
        slug="tower-of-hanoi", title="Tower of Hanoi", difficulty="Medium",
        topics=["Recursion"], subtopics=[], companies=["Microsoft"],
        description=(
            "`n` disks of distinct sizes sit on peg `A`, largest at the bottom. Move the whole "
            "tower to peg `C`, using `B` as a spare. One disk moves at a time, and a larger disk "
            "may never be placed on a smaller one.\n\n"
            "Print the **minimum** sequence of moves. Disks are numbered `1` (smallest) to `n`.\n\n"
            "### Input\nOne line: `n`.\n\n"
            "### Output\nThe number of moves on the first line, then one move per line as "
            "`disk from to`, e.g. `1 A C`."
        ),
        constraints="1 ≤ n ≤ 10",
        hints=[
            "Disk n must move from A to C at some point, and at that moment every other disk must be on B.",
            "So: move the top n−1 disks A → B, move disk n A → C, move the n−1 disks B → C.",
            "The two inner moves are the same problem with the pegs relabelled — pass the pegs as parameters.",
            "The move count satisfies T(n) = 2T(n−1) + 1. What is T(n)?",
        ],
        opt=("O(2ⁿ)", "O(n)",
             "The minimum solution has 2ⁿ − 1 moves, so no algorithm that prints it can be faster; "
             "the recursion depth is n."),
        editorial=(
            "## The one thing this teaches\n**Trust the recursive call.** You cannot hold a "
            "10-disk solution in your head, and you do not need to. Assume `move(k − 1, …)` "
            "correctly moves a smaller tower between any two pegs; then moving k disks is three "
            "lines, and the base case (zero disks, do nothing) makes the assumption true.\n\n"
            "## Approach\n```java\nstatic void move(int k, char from, char to, char via, StringBuilder out) {\n"
            "    if (k == 0) return;\n"
            "    move(k - 1, from, via, to, out);                         // clear the way\n"
            "    out.append(k).append(' ').append(from).append(' ').append(to).append('\\n');\n"
            "    move(k - 1, via, to, from, out);                         // restack on top\n}\n```\n\n"
            "The count is printed first, so either collect the moves before printing, or use the "
            "formula below.\n\n"
            "## Why it is 2ⁿ − 1, and why that is optimal\nT(n) = 2T(n − 1) + 1 with T(0) = 0 "
            "gives 1, 3, 7, 15, … = 2ⁿ − 1. It is also a lower bound: disk n has to move at least "
            "once, and before its first move the other n − 1 disks must all be stacked on one "
            "peg, and after its last move stacked again on another — at least T(n − 1) moves "
            "each.\n\n"
            "## Two calls, not one\nFactorial and Fibonacci-with-a-memo recurse once per level. "
            "This recurses twice on a problem only one smaller, which is what exponential call "
            "trees look like — here unavoidable, because the output itself is exponential. Being "
            "able to tell that case apart from an exponential tree full of *repeated* calls (which "
            "a memo fixes) is the skill."
        ),
        ref=sol_tower_of_hanoi,
        starter_py=(
            "import sys\n\nn = int(sys.stdin.read().split()[0])\n\n"
            "moves = []\n\n"
            "def move(k, src, dst, via):\n"
            "    # TODO: move k-1 out of the way, move disk k, move k-1 back on top\n"
            "    pass\n\n"
            "move(n, 'A', 'C', 'B')\n"
            "print(len(moves))\nfor m in moves:\n    print(m)\n"
        ),
        starter_js=(
            "const n = Number(require('fs').readFileSync(0, 'utf8').trim());\n"
            "const moves = [];\n\n"
            "function move(k, src, dst, via) {\n"
            "  // TODO: move k-1 out of the way, move disk k, move k-1 back on top\n"
            "}\n\nmove(n, 'A', 'C', 'B');\nconsole.log([String(moves.length), ...moves].join('\\n'));\n"
        ),
        cases=[
            ("example", "Example 1", "1\n"),
            ("example", "Example 2", "2\n"),
            ("hidden", "Three disks", "3\n"),
            ("hidden", "Four disks", "4\n"),
            ("hidden", "Five disks", "5\n"),
        ],
        example_expl=[
            "One disk goes straight across.",
            "Disk 1 steps aside to B, disk 2 crosses to C, disk 1 lands on top of it.",
        ],
    ),
]

DEFS += FILL_DEFS


JAVA_STARTERS.update({
    "sum-of-pair-products": _java_main(
        "        int n = sc.nextInt();\n"
        "        long[] a = new long[n];\n"
        "        for (int i = 0; i < n; i++) a[i] = sc.nextLong();\n"
        "        long total = 0;\n"
        "        // TODO: carry the sum of the elements before j; add a[j] times it\n"
        "        System.out.println(total);\n"
    ),
    "sum-abs-differences": _java_main(
        "        int n = sc.nextInt();\n"
        "        long[] a = new long[n];\n"
        "        for (int i = 0; i < n; i++) a[i] = sc.nextLong();\n"
        "        long total = 0;\n"
        "        // TODO: sort, then add a[j] * j minus the sum of the elements before j\n"
        "        System.out.println(total);\n"
    ),
    "leaderboard-ranks": _java_main(
        "        int n = sc.nextInt();\n"
        "        String[] names = new String[n];\n"
        "        int[] scores = new int[n];\n"
        "        for (int i = 0; i < n; i++) { names[i] = sc.next(); scores[i] = sc.nextInt(); }\n"
        "        // TODO: sort indices by score desc, then name asc; print 'rank name score'\n"
    ),
    "remove-adjacent-duplicates": _java_main(
        "        String s = sc.next();\n"
        "        StringBuilder st = new StringBuilder();\n"
        "        // TODO: a letter equal to the last survivor cancels it; otherwise it survives\n"
        "        System.out.println(st.length() == 0 ? \"EMPTY\" : st.toString());\n"
    ),
    "evaluate-rpn": _java_main(
        "        int n = sc.nextInt();\n"
        "        Deque<Long> st = new ArrayDeque<>();\n"
        "        for (int i = 0; i < n; i++) {\n"
        "            String t = sc.next();\n"
        "            // TODO: push numbers; for an operator pop b, then a, push a op b\n"
        "        }\n"
        "        System.out.println(st.isEmpty() ? 0 : st.pop());\n"
    ),
    "binomial-coefficient": (
        "import java.util.*;\n\n"
        "public class Main {\n"
        "    static long c(int n, int k) {\n"
        "        // TODO: base cases k == 0 or k == n, else Pascal's rule\n"
        "        return 0;\n"
        "    }\n\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int n = sc.nextInt(), k = sc.nextInt();\n"
        "        System.out.println(c(n, k));\n"
        "    }\n"
        "}\n"
    ),
    "tower-of-hanoi": (
        "import java.util.*;\n\n"
        "public class Main {\n"
        "    static int count = 0;\n\n"
        "    static void move(int k, char from, char to, char via, StringBuilder out) {\n"
        "        // TODO: move k-1 out of the way, move disk k, move k-1 back on top\n"
        "    }\n\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int n = sc.nextInt();\n"
        "        StringBuilder out = new StringBuilder();\n"
        "        move(n, 'A', 'C', 'B', out);\n"
        "        System.out.println(count);\n"
        "        System.out.print(out);\n"
        "    }\n"
        "}\n"
    ),
})


PREREQS.update({
    "sum-of-pair-products": [
        ("big_o", "The nested loop is correct and too slow; the fix is noticing its inner sum can be carried."),
        ("overflow", "Pair products add up past 2³¹ quickly, so both accumulators are `long`."),
    ],
    "sum-abs-differences": [
        ("sorting", "A sum over all pairs does not depend on order, so sorting is free — and removes the absolute value."),
        ("prefix_sum", "After sorting, each element's contribution needs the sum of everything before it."),
    ],
    "leaderboard-ranks": [
        ("sorting", "A comparator that compares the main key and falls back to a tie-break only on equality."),
        ("iteration", "Shared ranks come from comparing each row with the one above it in sorted order."),
    ],
    "remove-adjacent-duplicates": [
        ("stack", "The top of the stack is the most recent surviving letter — the only one a new letter can cancel."),
        ("string_basics", "A `StringBuilder` doubles as a stack of characters that prints in the right order."),
    ],
    "evaluate-rpn": [
        ("stack", "Numbers wait on the stack until an operator consumes the top two."),
        ("arithmetic", "Operand order and Java's truncating division are where the wrong answers come from."),
    ],
    "binomial-coefficient": [
        ("recursion", "Pascal's rule is a recursive definition with two base cases."),
        ("recurrence", "The two terms are the two disjoint cases: the last item chosen or not."),
    ],
    "tower-of-hanoi": [
        ("recursion", "Trust the smaller call: moving n−1 disks between any two pegs is assumed solved."),
        ("big_o", "T(n) = 2T(n−1) + 1 = 2ⁿ − 1, and the output alone forces that cost."),
    ],
})


# ---------------------------------------------------------------------------
# Reference solutions, merged into REFERENCE_SOLUTIONS so `verify_seeds` proves
# each of these is judged correctly in both shipped languages.
# ---------------------------------------------------------------------------

FILL_REFS = {
    "sum-of-pair-products": {
        "python": (
            "import sys\nd = sys.stdin.read().split()\n"
            "n = int(d[0])\na = list(map(int, d[1:1 + n]))\n"
            "before = 0\ntotal = 0\n"
            "for x in a:\n    total += x * before\n    before += x\n"
            "print(total)\n"
        ),
        "java": _java_main(
            "        int n = sc.nextInt();\n"
            "        long before = 0, total = 0;\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            long x = sc.nextLong();\n"
            "            total += x * before;\n"
            "            before += x;\n"
            "        }\n"
            "        System.out.println(total);\n"
        ),
    },
    "sum-abs-differences": {
        "python": (
            "import sys\nd = sys.stdin.read().split()\n"
            "n = int(d[0])\na = sorted(map(int, d[1:1 + n]))\n"
            "before = 0\ntotal = 0\n"
            "for j, x in enumerate(a):\n    total += x * j - before\n    before += x\n"
            "print(total)\n"
        ),
        "java": _java_main(
            "        int n = sc.nextInt();\n"
            "        long[] a = new long[n];\n"
            "        for (int i = 0; i < n; i++) a[i] = sc.nextLong();\n"
            "        Arrays.sort(a);\n"
            "        long before = 0, total = 0;\n"
            "        for (int j = 0; j < n; j++) {\n"
            "            total += a[j] * j - before;\n"
            "            before += a[j];\n"
            "        }\n"
            "        System.out.println(total);\n"
        ),
    },
    "leaderboard-ranks": {
        "python": (
            "import sys\nL = sys.stdin.read().strip().split('\\n')\n"
            "n = int(L[0])\nrows = []\n"
            "for i in range(n):\n"
            "    name, score = L[1 + i].split()\n    rows.append((name, int(score)))\n"
            "rows.sort(key=lambda r: (-r[1], r[0]))\n"
            "rank = 0\nout = []\n"
            "for i, (name, score) in enumerate(rows):\n"
            "    if i == 0 or score != rows[i - 1][1]:\n        rank = i + 1\n"
            "    out.append(f'{rank} {name} {score}')\n"
            "print('\\n'.join(out))\n"
        ),
        "java": _java_main(
            "        int n = sc.nextInt();\n"
            "        String[] names = new String[n];\n"
            "        int[] scores = new int[n];\n"
            "        Integer[] idx = new Integer[n];\n"
            "        for (int i = 0; i < n; i++) { names[i] = sc.next(); scores[i] = sc.nextInt(); idx[i] = i; }\n"
            "        Arrays.sort(idx, (x, y) -> scores[x] != scores[y]\n"
            "                ? Integer.compare(scores[y], scores[x])\n"
            "                : names[x].compareTo(names[y]));\n"
            "        StringBuilder out = new StringBuilder();\n"
            "        int rank = 0;\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            if (i == 0 || scores[idx[i]] != scores[idx[i - 1]]) rank = i + 1;\n"
            "            out.append(rank).append(' ').append(names[idx[i]]).append(' ').append(scores[idx[i]]).append('\\n');\n"
            "        }\n"
            "        System.out.print(out);\n"
        ),
    },
    "remove-adjacent-duplicates": {
        "python": (
            "import sys\ns = sys.stdin.readline().strip()\n"
            "st = []\n"
            "for ch in s:\n"
            "    if st and st[-1] == ch:\n        st.pop()\n"
            "    else:\n        st.append(ch)\n"
            "print(''.join(st) if st else 'EMPTY')\n"
        ),
        "java": _java_main(
            "        String s = sc.next();\n"
            "        StringBuilder st = new StringBuilder();\n"
            "        for (int i = 0; i < s.length(); i++) {\n"
            "            char c = s.charAt(i);\n"
            "            int len = st.length();\n"
            "            if (len > 0 && st.charAt(len - 1) == c) st.setLength(len - 1);\n"
            "            else st.append(c);\n"
            "        }\n"
            "        System.out.println(st.length() == 0 ? \"EMPTY\" : st.toString());\n"
        ),
    },
    "evaluate-rpn": {
        "python": (
            "import sys\nL = sys.stdin.read().strip().split('\\n')\n"
            "st = []\n"
            "for t in L[1].split():\n"
            "    if t in ('+', '-', '*', '/'):\n"
            "        b = st.pop(); a = st.pop()\n"
            "        if t == '+': st.append(a + b)\n"
            "        elif t == '-': st.append(a - b)\n"
            "        elif t == '*': st.append(a * b)\n"
            "        else:\n"
            "            q = abs(a) // abs(b)\n"
            "            st.append(q if (a >= 0) == (b >= 0) else -q)\n"
            "    else:\n        st.append(int(t))\n"
            "print(st[-1])\n"
        ),
        "java": _java_main(
            "        int n = sc.nextInt();\n"
            "        Deque<Long> st = new ArrayDeque<>();\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            String t = sc.next();\n"
            "            if (t.equals(\"+\") || t.equals(\"-\") || t.equals(\"*\") || t.equals(\"/\")) {\n"
            "                long b = st.pop(), a = st.pop();\n"
            "                switch (t) {\n"
            "                    case \"+\": st.push(a + b); break;\n"
            "                    case \"-\": st.push(a - b); break;\n"
            "                    case \"*\": st.push(a * b); break;\n"
            "                    default: st.push(a / b);\n"
            "                }\n"
            "            } else {\n"
            "                st.push(Long.parseLong(t));\n"
            "            }\n"
            "        }\n"
            "        System.out.println(st.pop());\n"
        ),
    },
    "binomial-coefficient": {
        "python": (
            "import sys\nn, k = map(int, sys.stdin.read().split()[:2])\n"
            "def c(n, k):\n"
            "    if k == 0 or k == n:\n        return 1\n"
            "    return c(n - 1, k - 1) + c(n - 1, k)\n"
            "print(c(n, k))\n"
        ),
        "java": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    static long c(int n, int k) {\n"
            "        if (k == 0 || k == n) return 1;\n"
            "        return c(n - 1, k - 1) + c(n - 1, k);\n"
            "    }\n\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = sc.nextInt(), k = sc.nextInt();\n"
            "        System.out.println(c(n, k));\n"
            "    }\n"
            "}\n"
        ),
    },
    "tower-of-hanoi": {
        "python": (
            "import sys\nn = int(sys.stdin.read().split()[0])\n"
            "moves = []\n"
            "def move(k, src, dst, via):\n"
            "    if k == 0:\n        return\n"
            "    move(k - 1, src, via, dst)\n"
            "    moves.append(f'{k} {src} {dst}')\n"
            "    move(k - 1, via, dst, src)\n"
            "move(n, 'A', 'C', 'B')\n"
            "print(len(moves))\nprint('\\n'.join(moves))\n"
        ),
        "java": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    static int count = 0;\n\n"
            "    static void move(int k, char from, char to, char via, StringBuilder out) {\n"
            "        if (k == 0) return;\n"
            "        move(k - 1, from, via, to, out);\n"
            "        out.append(k).append(' ').append(from).append(' ').append(to).append('\\n');\n"
            "        count++;\n"
            "        move(k - 1, via, to, from, out);\n"
            "    }\n\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = sc.nextInt();\n"
            "        StringBuilder out = new StringBuilder();\n"
            "        move(n, 'A', 'C', 'B', out);\n"
            "        System.out.println(count);\n"
            "        System.out.print(out);\n"
            "    }\n"
            "}\n"
        ),
    },
}
