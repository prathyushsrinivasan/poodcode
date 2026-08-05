#!/usr/bin/env python3
"""Generate src-tauri/seeds/problems.json.

Every problem carries a *reference solution* used to COMPUTE the expected output
for each test case. This guarantees the bundled hidden tests are correct instead
of being eyeballed by hand. All problem statements are original to this app.

IO model (app-wide): programs read from stdin and write to stdout. Each problem
documents its own input/output contract.
"""

import json
import math
import os
from collections import defaultdict, deque, Counter
from heapq import heappush, heappop

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "src-tauri", "seeds", "problems.json")

problems = []


def add(**kw):
    problems.append(kw)


def lines(s):
    return s.split("\n")


# ---------------------------------------------------------------------------
# Reference solutions (each takes the raw stdin string, returns stdout string)
# ---------------------------------------------------------------------------

def sol_array_sum(inp):
    ls = lines(inp.strip())
    nums = list(map(int, ls[1].split()))
    return str(sum(nums))


def sol_reverse_string(inp):
    return inp.strip("\n").rstrip("\n")[::-1] if False else inp.strip()[::-1]


def sol_count_vowels(inp):
    s = inp.strip()
    return str(sum(1 for c in s if c in "aeiou"))


def sol_gcd(inp):
    a, b = map(int, inp.split())
    return str(math.gcd(a, b))


def sol_palindrome_number(inp):
    n = inp.strip()
    if n.startswith("-"):
        return "false"
    return "true" if n == n[::-1] else "false"


def sol_fibonacci(inp):
    n = int(inp.strip())
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return str(a)


def sol_two_sum_exists(inp):
    ls = lines(inp.strip())
    nums = list(map(int, ls[1].split()))
    target = int(ls[2])
    seen = set()
    for x in nums:
        if target - x in seen:
            return "YES"
        seen.add(x)
    return "NO"


def sol_two_sum_indices(inp):
    ls = lines(inp.strip())
    nums = list(map(int, ls[1].split()))
    target = int(ls[2])
    pos = {}
    for i, x in enumerate(nums):
        if target - x in pos:
            return f"{pos[target - x] + 1} {i + 1}"
        pos[x] = i
    return "-1"


def sol_longest_unique(inp):
    s = inp.strip("\n")
    last = {}
    start = 0
    best = 0
    for i, c in enumerate(s):
        if c in last and last[c] >= start:
            start = last[c] + 1
        last[c] = i
        best = max(best, i - start + 1)
    return str(best)


def sol_valid_parens(inp):
    s = inp.strip()
    pairs = {")": "(", "]": "[", "}": "{"}
    st = []
    for c in s:
        if c in "([{":
            st.append(c)
        elif c in pairs:
            if not st or st.pop() != pairs[c]:
                return "false"
    return "true" if not st else "false"


def sol_binary_search_first(inp):
    ls = lines(inp.strip())
    arr = list(map(int, ls[1].split()))
    target = int(ls[2])
    lo, hi, res = 0, len(arr) - 1, -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] >= target:
            if arr[mid] == target:
                res = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return str(res)


def sol_kadane(inp):
    ls = lines(inp.strip())
    nums = list(map(int, ls[1].split()))
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return str(best)


def sol_climbing_stairs(inp):
    n = int(inp.strip())
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return str(a)


def sol_rotate_array(inp):
    ls = lines(inp.strip())
    n = int(ls[0])
    arr = list(map(int, ls[1].split()))
    k = int(ls[2]) % n if n else 0
    res = arr[-k:] + arr[:-k] if k else arr
    return " ".join(map(str, res))


def sol_num_islands(inp):
    ls = lines(inp.strip("\n"))
    r, c = map(int, ls[0].split())
    grid = [list(ls[1 + i]) for i in range(r)]
    seen = [[False] * c for _ in range(r)]
    count = 0

    def bfs(sr, sc):
        q = deque([(sr, sc)])
        seen[sr][sc] = True
        while q:
            i, j = q.popleft()
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ni, nj = i + di, j + dj
                if 0 <= ni < r and 0 <= nj < c and not seen[ni][nj] and grid[ni][nj] == "1":
                    seen[ni][nj] = True
                    q.append((ni, nj))

    for i in range(r):
        for j in range(c):
            if grid[i][j] == "1" and not seen[i][j]:
                count += 1
                bfs(i, j)
    return str(count)


def sol_group_anagrams(inp):
    ls = lines(inp.strip("\n"))
    n = int(ls[0])
    words = [ls[1 + i] for i in range(n)]
    groups = set("".join(sorted(w)) for w in words)
    return str(len(groups))


def sol_course_schedule(inp):
    ls = lines(inp.strip("\n"))
    n, m = map(int, ls[0].split())
    indeg = [0] * n
    adj = defaultdict(list)
    for i in range(m):
        a, b = map(int, ls[1 + i].split())  # need b before a
        adj[b].append(a)
        indeg[a] += 1
    q = deque(i for i in range(n) if indeg[i] == 0)
    done = 0
    while q:
        u = q.popleft()
        done += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return "true" if done == n else "false"


def sol_lis(inp):
    ls = lines(inp.strip())
    nums = list(map(int, ls[1].split()))
    import bisect
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return str(len(tails))


def sol_edit_distance(inp):
    ls = lines(inp.strip("\n"))
    a, b = ls[0], ls[1]
    dp = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, len(b) + 1):
            cur = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j - 1])
            prev = cur
    return str(dp[len(b)])


def sol_trapping_rain(inp):
    ls = lines(inp.strip())
    h = list(map(int, ls[1].split()))
    l, r = 0, len(h) - 1
    lm = rm = total = 0
    while l < r:
        if h[l] < h[r]:
            lm = max(lm, h[l])
            total += lm - h[l]
            l += 1
        else:
            rm = max(rm, h[r])
            total += rm - h[r]
            r -= 1
    return str(total)


def sol_dijkstra(inp):
    ls = lines(inp.strip("\n"))
    n, m = map(int, ls[0].split())
    adj = defaultdict(list)
    for i in range(m):
        u, v, w = map(int, ls[1 + i].split())
        adj[u].append((v, w))
        adj[v].append((u, w))
    s, t = map(int, ls[1 + m].split())
    dist = [math.inf] * n
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, u = heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heappush(pq, (nd, v))
    return str(dist[t]) if dist[t] != math.inf else "-1"


# ---------------------------------------------------------------------------
# Problem definitions
# ---------------------------------------------------------------------------
# Each: slug/title/difficulty/topics.../statement fields, `ref`, and `cases`
# as a list of (kind, name, input). Expected outputs are computed by `ref`.

def PY(code):  # helper for readable python starter blocks
    return code


DEFS = [
    dict(
        slug="array-sum", title="Array Sum", difficulty="Easy",
        topics=["Arrays"], subtopics=["Traversal"], companies=["Amazon"],
        description=(
            "Given an integer array, return the sum of all its elements.\n\n"
            "### Input\n- Line 1: integer `n` — the number of elements.\n"
            "- Line 2: `n` space-separated integers.\n\n"
            "### Output\nA single integer: the sum of the array."
        ),
        constraints="1 ≤ n ≤ 10^5\n-10^9 ≤ a[i] ≤ 10^9",
        hints=[
            "You only need to look at each element once.",
            "Keep a running total as you scan left to right.",
            "Watch out for negative numbers — they reduce the sum.",
            "Sum all elements: `total += a[i]`.",
        ],
        opt=("O(n)", "O(1)", "A single pass accumulating a running total is optimal; every element must be read at least once."),
        editorial=(
            "## Approach\nInitialize an accumulator to 0 and add each element. "
            "Because you must read every element to know the sum, O(n) time is optimal, "
            "and only a single accumulator is needed, giving O(1) extra space."
        ),
        ref=sol_array_sum,
        starter_py="import sys\n\ndef solve(nums):\n    # TODO: return the sum of nums\n    return 0\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1+n]))\nprint(solve(nums))\n",
        starter_js="const data = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);\nconst n = data[0];\nconst nums = data.slice(1, 1 + n);\n\nfunction solve(nums) {\n  // TODO: return the sum of nums\n  return 0;\n}\n\nconsole.log(solve(nums));\n",
        cases=[
            ("example", "Example 1", "3\n1 2 3\n"),
            ("example", "Example 2", "5\n-1 -2 -3 -4 -5\n"),
            ("hidden", "Single element", "1\n1000000000\n"),
            ("hidden", "All zeros", "4\n0 0 0 0\n"),
            ("hidden", "Mixed", "6\n10 -4 3 -3 100 -1\n"),
        ],
        example_expl=["1 + 2 + 3 = 6.", "The values sum to -15."],
    ),
    dict(
        slug="reverse-string", title="Reverse String", difficulty="Easy",
        topics=["Strings"], subtopics=["Two Pointers"], companies=["Microsoft"],
        description=(
            "Return the input string reversed.\n\n"
            "### Input\nA single line containing a string `s` of visible characters (no spaces).\n\n"
            "### Output\nThe reversed string."
        ),
        constraints="1 ≤ |s| ≤ 10^5",
        hints=[
            "Think about the first and last characters swapping places.",
            "Two pointers moving toward each other work well in-place.",
            "Or build the result from the end to the start.",
            "Swap s[i] and s[n-1-i] for i in [0, n/2).",
        ],
        opt=("O(n)", "O(n)", "Each character is moved once; the output itself needs O(n) space."),
        editorial="## Approach\nUse two indices, one at each end, swapping and moving inward until they meet.",
        ref=sol_reverse_string,
        starter_py="s = input()\n\ndef solve(s):\n    # TODO: return s reversed\n    return s\n\nprint(solve(s))\n",
        starter_js="const s = require('fs').readFileSync(0, 'utf8').replace(/\\n$/, '');\n\nfunction solve(s) {\n  // TODO: return s reversed\n  return s;\n}\n\nconsole.log(solve(s));\n",
        cases=[
            ("example", "Example 1", "hello\n"),
            ("example", "Example 2", "racecar\n"),
            ("hidden", "Single char", "a\n"),
            ("hidden", "Even length", "abcd\n"),
            ("hidden", "Digits", "12345\n"),
        ],
        example_expl=["'hello' reversed is 'olleh'.", "A palindrome reversed is itself."],
    ),
    dict(
        slug="count-vowels", title="Count Vowels", difficulty="Easy",
        topics=["Strings"], subtopics=["Counting"], companies=["Adobe"],
        description=(
            "Count how many vowels (a, e, i, o, u) appear in a lowercase string.\n\n"
            "### Input\nA single line: a lowercase string `s`.\n\n### Output\nThe number of vowels."
        ),
        constraints="1 ≤ |s| ≤ 10^5\ns consists of lowercase English letters",
        hints=[
            "A set of vowels makes membership tests easy.",
            "Scan once and increment a counter.",
            "`c in {'a','e','i','o','u'}`.",
            "Return the counter.",
        ],
        opt=("O(n)", "O(1)", "One pass; the vowel set is constant size."),
        editorial="## Approach\nIterate the string and increment a counter whenever the character is in the vowel set.",
        ref=sol_count_vowels,
        starter_py="s = input()\nVOWELS = set('aeiou')\n\ndef solve(s):\n    # TODO: count vowels\n    return 0\n\nprint(solve(s))\n",
        starter_js="const s = require('fs').readFileSync(0, 'utf8').replace(/\\n$/, '');\n\nfunction solve(s) {\n  // TODO: count vowels\n  return 0;\n}\n\nconsole.log(solve(s));\n",
        cases=[
            ("example", "Example 1", "hello\n"),
            ("example", "Example 2", "aeiou\n"),
            ("hidden", "No vowels", "sky\n"),
            ("hidden", "Longer", "programming\n"),
            ("hidden", "Repeated", "banana\n"),
        ],
        example_expl=["'e' and 'o' are vowels → 2.", "All five characters are vowels → 5."],
    ),
    dict(
        slug="gcd", title="Greatest Common Divisor", difficulty="Easy",
        topics=["Math"], subtopics=["Number Theory"], companies=["Bloomberg"],
        description=(
            "Compute the greatest common divisor of two non-negative integers.\n\n"
            "### Input\nTwo space-separated integers `a b` on one line.\n\n### Output\ngcd(a, b)."
        ),
        constraints="0 ≤ a, b ≤ 10^9 (not both zero)",
        hints=[
            "The Euclidean algorithm is the classic tool.",
            "gcd(a, b) = gcd(b, a mod b).",
            "Recurse/loop until b becomes 0.",
            "When b == 0, the answer is a.",
        ],
        opt=("O(log(min(a,b)))", "O(1)", "The Euclidean algorithm reduces the arguments logarithmically."),
        editorial="## Approach\nRepeatedly replace (a, b) with (b, a mod b) until b is 0; a is then the gcd.",
        ref=sol_gcd,
        starter_py="a, b = map(int, input().split())\n\ndef solve(a, b):\n    # TODO: return gcd(a, b)\n    return 0\n\nprint(solve(a, b))\n",
        starter_js="const [a, b] = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n\nfunction solve(a, b) {\n  // TODO: return gcd(a, b)\n  return 0;\n}\n\nconsole.log(solve(a, b));\n",
        cases=[
            ("example", "Example 1", "12 18\n"),
            ("example", "Example 2", "17 5\n"),
            ("hidden", "Divisible", "100 10\n"),
            ("hidden", "Zero operand", "0 7\n"),
            ("hidden", "Large", "1000000000 8\n"),
        ],
        example_expl=["6 divides both 12 and 18.", "17 and 5 are coprime → 1."],
    ),
    dict(
        slug="palindrome-number", title="Palindrome Number", difficulty="Easy",
        topics=["Math"], subtopics=["Digits"], companies=["Amazon"],
        description=(
            "Determine whether an integer reads the same forwards and backwards. "
            "Negative numbers are never palindromes.\n\n"
            "### Input\nA single integer `n`.\n\n### Output\n`true` or `false`."
        ),
        constraints="-10^18 ≤ n ≤ 10^18",
        hints=[
            "Negative numbers start with '-', which can't match the end.",
            "You can compare the decimal string with its reverse.",
            "Or reverse the number arithmetically and compare.",
            "Return whether str(n) == reverse(str(n)).",
        ],
        opt=("O(d)", "O(1)", "d = number of digits; reversing half the digits is optimal."),
        editorial="## Approach\nReject negatives immediately, then compare the digit string to its reverse.",
        ref=sol_palindrome_number,
        starter_py="n = input().strip()\n\ndef solve(n):\n    # n is the string form of the integer\n    # TODO: return 'true' or 'false'\n    return 'false'\n\nprint(solve(n))\n",
        starter_js="const n = require('fs').readFileSync(0, 'utf8').trim();\n\nfunction solve(n) {\n  // n is the string form of the integer\n  // TODO: return 'true' or 'false'\n  return 'false';\n}\n\nconsole.log(solve(n));\n",
        cases=[
            ("example", "Example 1", "121\n"),
            ("example", "Example 2", "-121\n"),
            ("hidden", "Not palindrome", "10\n"),
            ("hidden", "Zero", "0\n"),
            ("hidden", "Long palindrome", "123454321\n"),
        ],
        example_expl=["121 reversed is 121 → true.", "Negatives are never palindromes → false."],
    ),
    dict(
        slug="nth-fibonacci", title="Nth Fibonacci", difficulty="Easy",
        topics=["Dynamic Programming"], subtopics=["Recurrence"], companies=["Google"],
        description=(
            "Return the n-th Fibonacci number, where F(0)=0, F(1)=1, and "
            "F(k)=F(k-1)+F(k-2).\n\n### Input\nA single integer `n`.\n\n### Output\nF(n)."
        ),
        constraints="0 ≤ n ≤ 90 (fits in a 64-bit integer)",
        hints=[
            "You only need the two previous values at any time.",
            "Iterate from the bottom up.",
            "Keep variables a=F(i-1), b=F(i).",
            "Advance (a, b) → (b, a+b), n times.",
        ],
        opt=("O(n)", "O(1)", "Bottom-up iteration with two rolling variables."),
        editorial="## Approach\nAvoid exponential naive recursion. Iterate keeping only the last two values, which is O(n) time and O(1) space.",
        ref=sol_fibonacci,
        starter_py="n = int(input())\n\ndef solve(n):\n    # TODO: return F(n)\n    return 0\n\nprint(solve(n))\n",
        starter_js="const n = Number(require('fs').readFileSync(0, 'utf8').trim());\n\nfunction solve(n) {\n  // TODO: return F(n) (use BigInt-safe logic; n <= 90)\n  return 0;\n}\n\nconsole.log(solve(n));\n",
        cases=[
            ("example", "Example 1", "10\n"),
            ("example", "Example 2", "0\n"),
            ("hidden", "One", "1\n"),
            ("hidden", "Twenty", "20\n"),
            ("hidden", "Large", "50\n"),
        ],
        example_expl=["F(10) = 55.", "F(0) = 0 by definition."],
    ),
    dict(
        slug="two-sum-exists", title="Two Sum — Exists", difficulty="Easy",
        topics=["Hashing", "Arrays"], subtopics=["Complement Lookup"], companies=["Amazon", "Meta"],
        description=(
            "Given an array and a target, decide whether any two distinct positions sum to the target.\n\n"
            "### Input\n- Line 1: `n`\n- Line 2: `n` integers\n- Line 3: `target`\n\n"
            "### Output\n`YES` if such a pair exists, otherwise `NO`."
        ),
        constraints="1 ≤ n ≤ 10^5\n-10^9 ≤ a[i], target ≤ 10^9",
        hints=[
            "For each value x, you're looking for target - x.",
            "A hash set of values seen so far answers that in O(1).",
            "Check the complement BEFORE inserting the current value.",
            "If target - x was seen, answer YES.",
        ],
        opt=("O(n)", "O(n)", "A single pass with a hash set of previously seen values."),
        editorial="## Approach\nScan once. For each element check whether its complement `target - x` was already seen; if so, a pair exists.",
        ref=sol_two_sum_exists,
        starter_py="import sys\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1+n]))\ntarget = int(data[1+n])\n\ndef solve(nums, target):\n    # TODO: return 'YES' or 'NO'\n    return 'NO'\n\nprint(solve(nums, target))\n",
        starter_js="const d = require('fs').readFileSync(0,'utf8').split(/\\s+/).filter(Boolean).map(Number);\nconst n = d[0], nums = d.slice(1, 1+n), target = d[1+n];\n\nfunction solve(nums, target) {\n  // TODO: return 'YES' or 'NO'\n  return 'NO';\n}\n\nconsole.log(solve(nums, target));\n",
        cases=[
            ("example", "Example 1", "4\n2 7 11 15\n9\n"),
            ("example", "Example 2", "3\n1 2 3\n7\n"),
            ("hidden", "Duplicate values", "2\n3 3\n6\n"),
            ("hidden", "Middle pair", "5\n1 5 3 8 2\n10\n"),
            ("hidden", "No pair", "4\n1 2 3 4\n8\n"),
        ],
        example_expl=["2 + 7 = 9 → YES.", "No two of 1,2,3 sum to 7 → NO."],
    ),
    dict(
        slug="two-sum-indices", title="Two Sum — Indices", difficulty="Medium",
        topics=["Hashing", "Arrays"], subtopics=["Complement Lookup"], companies=["Amazon", "Google", "Meta"],
        description=(
            "Return the 1-based indices of the two elements that add up to the target. "
            "Exactly one solution exists and you may not use the same element twice.\n\n"
            "### Input\n- Line 1: `n`\n- Line 2: `n` integers\n- Line 3: `target`\n\n"
            "### Output\nThe two indices in increasing order, space-separated."
        ),
        constraints="2 ≤ n ≤ 10^5\nExactly one valid pair exists.",
        hints=[
            "Map each value to the index where you saw it.",
            "For value x, look up target - x in the map.",
            "Because indices are 1-based, add 1 when printing.",
            "Return the earlier index first.",
        ],
        opt=("O(n)", "O(n)", "One pass storing value → index in a hash map."),
        editorial="## Approach\nStore each value's index in a map. For each new value, if its complement is already mapped, output both indices (1-based, smaller first).",
        ref=sol_two_sum_indices,
        starter_py="import sys\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1+n]))\ntarget = int(data[1+n])\n\ndef solve(nums, target):\n    # TODO: return two 1-based indices as 'i j'\n    return '-1'\n\nprint(solve(nums, target))\n",
        starter_js="const d = require('fs').readFileSync(0,'utf8').split(/\\s+/).filter(Boolean).map(Number);\nconst n = d[0], nums = d.slice(1, 1+n), target = d[1+n];\n\nfunction solve(nums, target) {\n  // TODO: return 'i j' (1-based)\n  return '-1';\n}\n\nconsole.log(solve(nums, target));\n",
        cases=[
            ("example", "Example 1", "4\n2 7 11 15\n9\n"),
            ("example", "Example 2", "3\n3 2 4\n6\n"),
            ("hidden", "Duplicates", "2\n3 3\n6\n"),
            ("hidden", "End pair", "5\n1 2 3 4 5\n9\n"),
            ("hidden", "Negatives", "4\n-3 4 3 90\n0\n"),
        ],
        example_expl=["nums[1]+nums[2] = 2+7 = 9 → '1 2'.", "nums[2]+nums[3] = 2+4 = 6 → '2 3'."],
    ),
    dict(
        slug="longest-unique-substring", title="Longest Substring Without Repeating Characters",
        difficulty="Medium", topics=["Sliding Window", "Strings"], subtopics=["Two Pointers"],
        companies=["Amazon", "Google", "Bloomberg"],
        description=(
            "Find the length of the longest substring that contains no repeated character.\n\n"
            "### Input\nA single line: string `s`.\n\n### Output\nThe length of the longest substring without repeating characters."
        ),
        constraints="1 ≤ |s| ≤ 10^5",
        hints=[
            "A window [start, i] should always hold distinct characters.",
            "Track the last index at which each character appeared.",
            "When you see a repeat inside the window, jump `start` past it.",
            "Answer is the maximum window width seen.",
        ],
        opt=("O(n)", "O(min(n, Σ))", "Each index enters and leaves the window at most once."),
        editorial="## Approach\nSlide a window while recording the last seen index of each character. On a repeat inside the window, advance the left edge to one past the previous occurrence, and track the max width.",
        ref=sol_longest_unique,
        starter_py="s = input()\n\ndef solve(s):\n    # TODO: length of longest substring without repeats\n    return 0\n\nprint(solve(s))\n",
        starter_js="const s = require('fs').readFileSync(0,'utf8').replace(/\\n$/, '');\n\nfunction solve(s) {\n  // TODO: length of longest substring without repeats\n  return 0;\n}\n\nconsole.log(solve(s));\n",
        cases=[
            ("example", "Example 1", "abcabcbb\n"),
            ("example", "Example 2", "pwwkew\n"),
            ("hidden", "All same", "bbbbb\n"),
            ("hidden", "All distinct", "abcdef\n"),
            ("hidden", "Two chars", "au\n"),
        ],
        example_expl=["'abc' has length 3.", "'wke' has length 3."],
    ),
    dict(
        slug="valid-parentheses", title="Valid Parentheses", difficulty="Medium",
        topics=["Stack", "Strings"], subtopics=["Matching"], companies=["Microsoft", "Amazon"],
        description=(
            "Given a string of brackets `()[]{}`, decide whether every bracket is correctly "
            "opened and closed in the right order.\n\n"
            "### Input\nA single line containing only the characters ()[]{}\n\n### Output\n`true` or `false`."
        ),
        constraints="1 ≤ |s| ≤ 10^5",
        hints=[
            "A closing bracket must match the most recently opened one.",
            "That 'most recent' behavior is a stack.",
            "Push opens; on a close, pop and compare.",
            "Valid iff the stack is empty at the end and never mismatches.",
        ],
        opt=("O(n)", "O(n)", "Each character is pushed/popped at most once."),
        editorial="## Approach\nPush opening brackets. For a closing bracket, the stack top must be its matching opener; otherwise it's invalid. The string is valid only if the stack ends empty.",
        ref=sol_valid_parens,
        starter_py="s = input()\n\ndef solve(s):\n    # TODO: return 'true' or 'false'\n    return 'false'\n\nprint(solve(s))\n",
        starter_js="const s = require('fs').readFileSync(0,'utf8').replace(/\\n$/, '');\n\nfunction solve(s) {\n  // TODO: return 'true' or 'false'\n  return 'false';\n}\n\nconsole.log(solve(s));\n",
        cases=[
            ("example", "Example 1", "()[]{}\n"),
            ("example", "Example 2", "([)]\n"),
            ("hidden", "Nested", "{[]}\n"),
            ("hidden", "Unclosed", "(((\n"),
            ("hidden", "Single pair", "()\n"),
        ],
        example_expl=["All brackets match in order → true.", "']' does not match the open '(' → false."],
    ),
    dict(
        slug="binary-search-first", title="First Occurrence", difficulty="Medium",
        topics=["Binary Search", "Arrays"], subtopics=["Lower Bound"], companies=["Google", "Adobe"],
        description=(
            "In a non-decreasing array, return the index (0-based) of the FIRST occurrence of a "
            "target value, or -1 if absent.\n\n"
            "### Input\n- Line 1: `n`\n- Line 2: `n` non-decreasing integers\n- Line 3: `target`\n\n"
            "### Output\nThe first index of `target`, or -1."
        ),
        constraints="1 ≤ n ≤ 10^5\nArray is sorted non-decreasing.",
        hints=[
            "Plain linear scan is O(n); the sorted order lets you do better.",
            "Binary search, but don't stop at the first match.",
            "When you find the target, keep searching the left half.",
            "Track the best (leftmost) index found.",
        ],
        opt=("O(log n)", "O(1)", "Binary search narrowing to the lower bound."),
        editorial="## Approach\nBinary search for the target; whenever `a[mid] >= target` move `hi` left, recording `mid` when it equals the target. This converges on the leftmost occurrence.",
        ref=sol_binary_search_first,
        starter_py="import sys\nd = sys.stdin.read().split()\nn = int(d[0]); arr = list(map(int, d[1:1+n])); target = int(d[1+n])\n\ndef solve(arr, target):\n    # TODO: return first index of target or -1\n    return -1\n\nprint(solve(arr, target))\n",
        starter_js="const d = require('fs').readFileSync(0,'utf8').split(/\\s+/).filter(Boolean).map(Number);\nconst n=d[0], arr=d.slice(1,1+n), target=d[1+n];\n\nfunction solve(arr, target) {\n  // TODO: return first index of target or -1\n  return -1;\n}\n\nconsole.log(solve(arr, target));\n",
        cases=[
            ("example", "Example 1", "5\n1 2 2 2 3\n2\n"),
            ("example", "Example 2", "5\n1 2 3 4 5\n6\n"),
            ("hidden", "All equal", "6\n1 1 1 1 1 1\n1\n"),
            ("hidden", "Single", "1\n5\n5\n"),
            ("hidden", "Last element", "4\n2 4 6 8\n8\n"),
        ],
        example_expl=["First '2' is at index 1.", "6 is not present → -1."],
    ),
    dict(
        slug="maximum-subarray", title="Maximum Subarray Sum", difficulty="Medium",
        topics=["Dynamic Programming", "Arrays"], subtopics=["Kadane"], companies=["Amazon", "Bloomberg", "Microsoft"],
        description=(
            "Return the largest possible sum of a non-empty contiguous subarray.\n\n"
            "### Input\n- Line 1: `n`\n- Line 2: `n` integers (may be negative)\n\n"
            "### Output\nThe maximum subarray sum."
        ),
        constraints="1 ≤ n ≤ 10^5\n-10^9 ≤ a[i] ≤ 10^9",
        hints=[
            "At each index, ask: best sum ENDING here?",
            "Either extend the previous best or start fresh at a[i].",
            "cur = max(a[i], cur + a[i]).",
            "Track the global maximum of `cur`.",
        ],
        opt=("O(n)", "O(1)", "Kadane's algorithm: a single pass with two running values."),
        editorial="## Approach\nKadane's algorithm. Maintain the best subarray sum ending at the current index (`cur = max(a[i], cur + a[i])`) and the global best across all positions.",
        ref=sol_kadane,
        starter_py="import sys\nd = sys.stdin.read().split()\nn = int(d[0]); nums = list(map(int, d[1:1+n]))\n\ndef solve(nums):\n    # TODO: return maximum subarray sum\n    return 0\n\nprint(solve(nums))\n",
        starter_js="const d = require('fs').readFileSync(0,'utf8').split(/\\s+/).filter(Boolean).map(Number);\nconst n=d[0], nums=d.slice(1,1+n);\n\nfunction solve(nums) {\n  // TODO: return maximum subarray sum\n  return 0;\n}\n\nconsole.log(solve(nums));\n",
        cases=[
            ("example", "Example 1", "9\n-2 1 -3 4 -1 2 1 -5 4\n"),
            ("example", "Example 2", "5\n1 2 3 4 5\n"),
            ("hidden", "All negative", "4\n-1 -2 -3 -4\n"),
            ("hidden", "Single negative", "1\n-7\n"),
            ("hidden", "Peak in middle", "7\n-2 -1 5 6 -3 4 -8\n"),
        ],
        example_expl=["[4,-1,2,1] sums to 6.", "The whole array sums to 15."],
    ),
    dict(
        slug="climbing-stairs", title="Climbing Stairs", difficulty="Medium",
        topics=["Dynamic Programming"], subtopics=["Counting"], companies=["Amazon", "Adobe"],
        description=(
            "You climb a staircase of `n` steps, taking 1 or 2 steps at a time. "
            "How many distinct ways can you reach the top?\n\n"
            "### Input\nA single integer `n`.\n\n### Output\nThe number of distinct ways."
        ),
        constraints="0 ≤ n ≤ 45",
        hints=[
            "To reach step n you came from n-1 or n-2.",
            "So ways(n) = ways(n-1) + ways(n-2).",
            "That's the Fibonacci recurrence with ways(0)=ways(1)=1.",
            "Iterate bottom-up keeping two values.",
        ],
        opt=("O(n)", "O(1)", "Bottom-up DP with two rolling variables (Fibonacci)."),
        editorial="## Approach\nThe number of ways satisfies ways(n)=ways(n-1)+ways(n-2) with base cases ways(0)=ways(1)=1 — the Fibonacci sequence shifted by one.",
        ref=sol_climbing_stairs,
        starter_py="n = int(input())\n\ndef solve(n):\n    # TODO: number of ways to climb n steps\n    return 0\n\nprint(solve(n))\n",
        starter_js="const n = Number(require('fs').readFileSync(0,'utf8').trim());\n\nfunction solve(n) {\n  // TODO: number of ways to climb n steps\n  return 0;\n}\n\nconsole.log(solve(n));\n",
        cases=[
            ("example", "Example 1", "2\n"),
            ("example", "Example 2", "3\n"),
            ("hidden", "Base zero", "0\n"),
            ("hidden", "Five", "5\n"),
            ("hidden", "Large", "45\n"),
        ],
        example_expl=["1+1 or 2 → 2 ways.", "1+1+1, 1+2, 2+1 → 3 ways."],
    ),
    dict(
        slug="rotate-array", title="Rotate Array", difficulty="Medium",
        topics=["Arrays"], subtopics=["Cyclic Shift"], companies=["Microsoft", "Amazon"],
        description=(
            "Rotate an array to the RIGHT by `k` positions.\n\n"
            "### Input\n- Line 1: `n`\n- Line 2: `n` integers\n- Line 3: `k` (may exceed n)\n\n"
            "### Output\nThe rotated array, space-separated."
        ),
        constraints="1 ≤ n ≤ 10^5\n0 ≤ k ≤ 10^9",
        hints=[
            "Rotating by n leaves the array unchanged, so reduce k mod n.",
            "The last k elements move to the front.",
            "A three-reversal trick rotates in place with O(1) extra space.",
            "Reverse all, reverse first k, reverse the rest.",
        ],
        opt=("O(n)", "O(1)", "The reverse-reverse-reverse method rotates in place."),
        editorial="## Approach\nReduce k modulo n. The optimal in-place method reverses the whole array, then reverses the first k and the remaining n-k elements.",
        ref=sol_rotate_array,
        starter_py="import sys\nd = sys.stdin.read().split()\nn = int(d[0]); arr = list(map(int, d[1:1+n])); k = int(d[1+n])\n\ndef solve(arr, k):\n    # TODO: return rotated list\n    return arr\n\nprint(' '.join(map(str, solve(arr, k))))\n",
        starter_js="const d = require('fs').readFileSync(0,'utf8').split(/\\s+/).filter(Boolean).map(Number);\nconst n=d[0], arr=d.slice(1,1+n), k=d[1+n];\n\nfunction solve(arr, k) {\n  // TODO: return rotated array\n  return arr;\n}\n\nconsole.log(solve(arr, k).join(' '));\n",
        cases=[
            ("example", "Example 1", "5\n1 2 3 4 5\n2\n"),
            ("example", "Example 2", "3\n1 2 3\n4\n"),
            ("hidden", "k=0", "4\n1 2 3 4\n0\n"),
            ("hidden", "Single", "1\n7\n3\n"),
            ("hidden", "k equals n", "3\n9 8 7\n3\n"),
        ],
        example_expl=["Right by 2 → 4 5 1 2 3.", "k=4 ≡ 1 (mod 3) → 3 1 2."],
    ),
    dict(
        slug="number-of-islands", title="Number of Islands", difficulty="Medium",
        topics=["Graphs", "Matrix"], subtopics=["BFS", "Flood Fill"], companies=["Amazon", "Google", "Meta"],
        description=(
            "Count connected groups of land cells ('1') in a grid. Cells connect horizontally "
            "and vertically (not diagonally).\n\n"
            "### Input\n- Line 1: `R C`\n- Next `R` lines: strings of `0`/`1` of length `C`\n\n"
            "### Output\nThe number of islands."
        ),
        constraints="1 ≤ R, C ≤ 300",
        hints=[
            "Each unvisited land cell starts a new island.",
            "From it, flood the whole connected component.",
            "Use BFS or DFS over 4-directional neighbors.",
            "Count how many times you launch a fresh flood.",
        ],
        opt=("O(R·C)", "O(R·C)", "Each cell is visited once; the queue/visited grid is O(R·C)."),
        editorial="## Approach\nScan the grid. Each time you meet an unvisited '1', increment the island count and BFS/DFS-mark the entire connected land mass so it isn't recounted.",
        ref=sol_num_islands,
        starter_py="import sys\nlines = sys.stdin.read().split('\\n')\nr, c = map(int, lines[0].split())\ngrid = [lines[1+i] for i in range(r)]\n\ndef solve(grid, r, c):\n    # TODO: count islands\n    return 0\n\nprint(solve(grid, r, c))\n",
        starter_js="const lines = require('fs').readFileSync(0,'utf8').split('\\n');\nconst [r, c] = lines[0].split(/\\s+/).map(Number);\nconst grid = []; for (let i=0;i<r;i++) grid.push(lines[1+i]);\n\nfunction solve(grid, r, c) {\n  // TODO: count islands\n  return 0;\n}\n\nconsole.log(solve(grid, r, c));\n",
        cases=[
            ("example", "Example 1", "4 5\n11110\n11010\n11000\n00000\n"),
            ("example", "Example 2", "3 3\n101\n010\n101\n"),
            ("hidden", "Empty water", "1 1\n0\n"),
            ("hidden", "Full land", "2 2\n11\n11\n"),
            ("hidden", "Diagonal split", "3 3\n100\n010\n001\n"),
        ],
        example_expl=["One connected land mass → 1.", "Five separate single-cell islands → 5."],
    ),
    dict(
        slug="group-anagrams-count", title="Group Anagrams — Count", difficulty="Medium",
        topics=["Hashing", "Strings"], subtopics=["Canonical Form"], companies=["Amazon", "Adobe", "Bloomberg"],
        description=(
            "Given a list of words, count how many groups of anagrams there are. Two words are "
            "anagrams if one is a rearrangement of the other.\n\n"
            "### Input\n- Line 1: `n`\n- Next `n` lines: one lowercase word each\n\n"
            "### Output\nThe number of distinct anagram groups."
        ),
        constraints="1 ≤ n ≤ 10^4\nWords are lowercase, total length ≤ 10^5.",
        hints=[
            "Anagrams share the same multiset of letters.",
            "A canonical key: the sorted letters of the word.",
            "Words with the same key belong to the same group.",
            "Count the distinct keys.",
        ],
        opt=("O(Σ k log k)", "O(Σ k)", "k = word length; sorting each word to form its key dominates."),
        editorial="## Approach\nMap each word to a canonical key (its sorted characters). Anagrams collide on the same key, so the number of groups is the number of distinct keys.",
        ref=sol_group_anagrams,
        starter_py="import sys\nlines = sys.stdin.read().split('\\n')\nn = int(lines[0])\nwords = [lines[1+i] for i in range(n)]\n\ndef solve(words):\n    # TODO: number of anagram groups\n    return 0\n\nprint(solve(words))\n",
        starter_js="const lines = require('fs').readFileSync(0,'utf8').split('\\n');\nconst n = Number(lines[0]);\nconst words = []; for (let i=0;i<n;i++) words.push(lines[1+i]);\n\nfunction solve(words) {\n  // TODO: number of anagram groups\n  return 0;\n}\n\nconsole.log(solve(words));\n",
        cases=[
            ("example", "Example 1", "3\nabc\nbca\nxyz\n"),
            ("example", "Example 2", "5\neat\ntea\ntan\nate\nnat\n"),
            ("hidden", "Single", "1\na\n"),
            ("hidden", "Two groups", "4\nab\nba\nabc\ncba\n"),
            ("hidden", "All same group", "3\nlisten\nsilent\nenlist\n"),
        ],
        example_expl=["{abc,bca} and {xyz} → 2 groups.", "{eat,tea,ate}, {tan,nat} → 2 groups."],
    ),
    dict(
        slug="course-schedule", title="Course Schedule", difficulty="Medium",
        topics=["Graphs"], subtopics=["Topological Sort", "Cycle Detection"], companies=["Amazon", "Google", "Meta"],
        description=(
            "There are `n` courses labeled 0..n-1 with prerequisite pairs. `a b` means course `b` "
            "must be taken before course `a`. Determine whether all courses can be finished.\n\n"
            "### Input\n- Line 1: `n m` (courses, prerequisite pairs)\n- Next `m` lines: `a b`\n\n"
            "### Output\n`true` if a valid order exists, otherwise `false`."
        ),
        constraints="1 ≤ n ≤ 10^5\n0 ≤ m ≤ 2·10^5",
        hints=[
            "Model courses as nodes and prerequisites as directed edges b → a.",
            "A valid order exists iff the graph has no directed cycle.",
            "Kahn's algorithm repeatedly removes zero-indegree nodes.",
            "If you can remove all n nodes, there's no cycle.",
        ],
        opt=("O(n + m)", "O(n + m)", "Kahn's topological sort visits each node and edge once."),
        editorial="## Approach\nBuild the prerequisite graph and run Kahn's algorithm: start from courses with no prerequisites, and 'complete' them, decrementing indegrees. If every course is completed, no cycle exists.",
        ref=sol_course_schedule,
        starter_py="import sys\nlines = sys.stdin.read().split('\\n')\nn, m = map(int, lines[0].split())\nedges = [tuple(map(int, lines[1+i].split())) for i in range(m)]\n\ndef solve(n, edges):\n    # edges are (a, b): b before a. Return 'true' or 'false'.\n    return 'true'\n\nprint(solve(n, edges))\n",
        starter_js="const lines = require('fs').readFileSync(0,'utf8').split('\\n');\nconst [n, m] = lines[0].split(/\\s+/).map(Number);\nconst edges = []; for (let i=0;i<m;i++) edges.push(lines[1+i].split(/\\s+/).map(Number));\n\nfunction solve(n, edges) {\n  // edges are [a, b]: b before a. Return 'true' or 'false'.\n  return 'true';\n}\n\nconsole.log(solve(n, edges));\n",
        cases=[
            ("example", "Example 1", "2 1\n1 0\n"),
            ("example", "Example 2", "2 2\n1 0\n0 1\n"),
            ("hidden", "No prereqs", "3 0\n"),
            ("hidden", "Chain", "4 3\n1 0\n2 1\n3 2\n"),
            ("hidden", "Cycle of three", "3 3\n1 0\n2 1\n0 2\n"),
        ],
        example_expl=["Take 0 then 1 → true.", "0 and 1 require each other → false."],
    ),
    dict(
        slug="longest-increasing-subsequence", title="Longest Increasing Subsequence", difficulty="Hard",
        topics=["Dynamic Programming", "Binary Search"], subtopics=["Patience Sorting"], companies=["Google", "Amazon", "Microsoft"],
        description=(
            "Return the length of the longest STRICTLY increasing subsequence of an array. "
            "A subsequence keeps order but need not be contiguous.\n\n"
            "### Input\n- Line 1: `n`\n- Line 2: `n` integers\n\n### Output\nThe LIS length."
        ),
        constraints="1 ≤ n ≤ 10^5\n-10^9 ≤ a[i] ≤ 10^9",
        hints=[
            "The O(n²) DP asks: LIS ending at each index.",
            "For O(n log n), maintain 'tails': smallest possible tail for each length.",
            "For each value, binary-search the first tail ≥ it.",
            "Replace it (or append). The tails array length is the answer.",
        ],
        opt=("O(n log n)", "O(n)", "Patience sorting: binary search into the tails array for each element."),
        editorial="## Approach\nKeep an array `tails` where `tails[i]` is the smallest possible tail of an increasing subsequence of length i+1. For each element, binary-search the first tail ≥ it and overwrite; if none, append. The final length of `tails` is the LIS length.",
        ref=sol_lis,
        starter_py="import sys, bisect\nd = sys.stdin.read().split()\nn = int(d[0]); nums = list(map(int, d[1:1+n]))\n\ndef solve(nums):\n    # TODO: return LIS length\n    return 0\n\nprint(solve(nums))\n",
        starter_js="const d = require('fs').readFileSync(0,'utf8').split(/\\s+/).filter(Boolean).map(Number);\nconst n=d[0], nums=d.slice(1,1+n);\n\nfunction solve(nums) {\n  // TODO: return LIS length\n  return 0;\n}\n\nconsole.log(solve(nums));\n",
        cases=[
            ("example", "Example 1", "8\n10 9 2 5 3 7 101 18\n"),
            ("example", "Example 2", "5\n1 3 6 7 9\n"),
            ("hidden", "All equal", "6\n7 7 7 7 7 7\n"),
            ("hidden", "Decreasing", "5\n5 4 3 2 1\n"),
            ("hidden", "Single", "1\n42\n"),
        ],
        example_expl=["[2,3,7,18] or [2,3,7,101] → length 4.", "The whole array is increasing → 5."],
    ),
    dict(
        slug="edit-distance", title="Edit Distance", difficulty="Hard",
        topics=["Dynamic Programming", "Strings"], subtopics=["2D DP"], companies=["Google", "Amazon", "Microsoft"],
        description=(
            "Compute the minimum number of single-character insertions, deletions, or "
            "substitutions to turn `word1` into `word2` (Levenshtein distance).\n\n"
            "### Input\n- Line 1: `word1`\n- Line 2: `word2`\n\n### Output\nThe edit distance."
        ),
        constraints="1 ≤ |word1|, |word2| ≤ 1000\nWords are lowercase letters.",
        hints=[
            "Define dp[i][j] = distance between prefixes of lengths i and j.",
            "If the current characters match, no new cost is added.",
            "Otherwise take 1 + min(insert, delete, replace).",
            "You can compress the 2D table to one row.",
        ],
        opt=("O(m·n)", "O(min(m, n))", "The classic Levenshtein DP with a rolling 1-D row."),
        editorial="## Approach\nLet dp[i][j] be the edit distance between the first i characters of word1 and the first j of word2. If characters match, dp[i][j]=dp[i-1][j-1]; else 1 + min of the three neighboring states. Roll the table to one row for O(min(m,n)) space.",
        ref=sol_edit_distance,
        starter_py="import sys\nlines = sys.stdin.read().split('\\n')\na, b = lines[0], lines[1]\n\ndef solve(a, b):\n    # TODO: return edit distance\n    return 0\n\nprint(solve(a, b))\n",
        starter_js="const lines = require('fs').readFileSync(0,'utf8').split('\\n');\nconst a = lines[0], b = lines[1];\n\nfunction solve(a, b) {\n  // TODO: return edit distance\n  return 0;\n}\n\nconsole.log(solve(a, b));\n",
        cases=[
            ("example", "Example 1", "horse\nros\n"),
            ("example", "Example 2", "intention\nexecution\n"),
            ("hidden", "Identical", "abcde\nabcde\n"),
            ("hidden", "One char", "a\nb\n"),
            ("hidden", "Prefix", "kitten\nsitting\n"),
        ],
        example_expl=["horse→rorse→rose→ros → 3.", "Five edits transform the words → 5."],
    ),
    dict(
        slug="trapping-rain-water", title="Trapping Rain Water", difficulty="Hard",
        topics=["Two Pointers", "Arrays"], subtopics=["Prefix Max"], companies=["Amazon", "Google", "Bloomberg"],
        description=(
            "Given an elevation map where each bar has width 1, compute how much water it traps "
            "after raining.\n\n### Input\n- Line 1: `n`\n- Line 2: `n` non-negative heights\n\n"
            "### Output\nThe total trapped water."
        ),
        constraints="1 ≤ n ≤ 10^5\n0 ≤ h[i] ≤ 10^4",
        hints=[
            "Water above a bar = min(max-left, max-right) − its height.",
            "Precomputing left/right maxima is an O(n) space solution.",
            "Two pointers reach O(1) space.",
            "Advance the side with the smaller running max.",
        ],
        opt=("O(n)", "O(1)", "Two pointers moving inward, each contributing bounded by the smaller side's running max."),
        editorial="## Approach\nUse two pointers with running left/right maxima. The side with the smaller max determines the water at that position, so advance it and add `runningMax − height`.",
        ref=sol_trapping_rain,
        starter_py="import sys\nd = sys.stdin.read().split()\nn = int(d[0]); h = list(map(int, d[1:1+n]))\n\ndef solve(h):\n    # TODO: return trapped water\n    return 0\n\nprint(solve(h))\n",
        starter_js="const d = require('fs').readFileSync(0,'utf8').split(/\\s+/).filter(Boolean).map(Number);\nconst n=d[0], h=d.slice(1,1+n);\n\nfunction solve(h) {\n  // TODO: return trapped water\n  return 0;\n}\n\nconsole.log(solve(h));\n",
        cases=[
            ("example", "Example 1", "12\n0 1 0 2 1 0 1 3 2 1 2 1\n"),
            ("example", "Example 2", "6\n4 2 0 3 2 5\n"),
            ("hidden", "Monotonic", "3\n1 2 3\n"),
            ("hidden", "Single bar", "1\n5\n"),
            ("hidden", "Valley", "5\n5 0 0 0 5\n"),
        ],
        example_expl=["The dips trap 6 units.", "This profile traps 9 units."],
    ),
    dict(
        slug="dijkstra-shortest-path", title="Shortest Path (Dijkstra)", difficulty="Hard",
        topics=["Graphs"], subtopics=["Dijkstra", "Priority Queue"], companies=["Google", "Amazon", "Uber"],
        description=(
            "Given a weighted undirected graph with non-negative weights, find the shortest path "
            "distance from `s` to `t`, or -1 if unreachable.\n\n"
            "### Input\n- Line 1: `n m` (nodes 0..n-1, edges)\n- Next `m` lines: `u v w`\n- Last line: `s t`\n\n"
            "### Output\nThe shortest distance from `s` to `t`, or -1."
        ),
        constraints="1 ≤ n ≤ 10^5\n0 ≤ m ≤ 2·10^5\n0 ≤ w ≤ 10^9",
        hints=[
            "Non-negative weights → Dijkstra's algorithm.",
            "Use a min-priority-queue keyed by tentative distance.",
            "Pop the closest unfinalized node and relax its edges.",
            "Skip stale queue entries where popped distance > best known.",
        ],
        opt=("O((n + m) log n)", "O(n + m)", "Dijkstra with a binary heap."),
        editorial="## Approach\nDijkstra's algorithm: maintain a distance array initialized to infinity, push (0, s), and repeatedly pop the smallest-distance node, relaxing outgoing edges. Ignore stale heap entries. Report dist[t] or -1.",
        ref=sol_dijkstra,
        starter_py="import sys, heapq\nlines = sys.stdin.read().split('\\n')\nn, m = map(int, lines[0].split())\nedges = [tuple(map(int, lines[1+i].split())) for i in range(m)]\ns, t = map(int, lines[1+m].split())\n\ndef solve(n, edges, s, t):\n    # TODO: return shortest distance s->t or -1\n    return -1\n\nprint(solve(n, edges, s, t))\n",
        starter_js="const lines = require('fs').readFileSync(0,'utf8').split('\\n');\nconst [n, m] = lines[0].split(/\\s+/).map(Number);\nconst edges = []; for (let i=0;i<m;i++) edges.push(lines[1+i].split(/\\s+/).map(Number));\nconst [s, t] = lines[1+m].split(/\\s+/).map(Number);\n\nfunction solve(n, edges, s, t) {\n  // TODO: return shortest distance s->t or -1\n  return -1;\n}\n\nconsole.log(solve(n, edges, s, t));\n",
        cases=[
            ("example", "Example 1", "5 6\n0 1 2\n0 2 4\n1 2 1\n1 3 7\n2 4 3\n3 4 1\n0 4\n"),
            ("example", "Example 2", "2 1\n0 1 3\n1 0\n"),
            ("hidden", "Unreachable", "3 1\n0 1 5\n0 2\n"),
            ("hidden", "Same node", "1 0\n0 0\n"),
            ("hidden", "Pick cheaper route", "4 4\n0 1 1\n1 3 1\n0 2 5\n2 3 1\n0 3\n"),
        ],
        example_expl=["0→1→2→4 costs 2+1+3 = 6.", "The single edge has weight 3."],
    ),
]

# ---------------------------------------------------------------------------
# Prerequisites: a shared concept library + which concepts each problem needs.
# `CONCEPTS[key] = (name, what)` — a generic explanation of the concept.
# `PREREQS[slug] = [(key, how), ...]` — how that concept helps THIS problem.
# ---------------------------------------------------------------------------

CONCEPTS = {
    "iteration": {
        "name": "Array Iteration",
        "what": "Walking through elements one at a time while maintaining running state such as a sum, max, or counter.",
        "deep": "The workhorse of array problems: one for-loop that updates accumulators as it goes. Most linear-time solutions are just one well-chosen pass, so the real skill is deciding what state to carry so a single sweep suffices.",
        "java": "Use for (int i = 0; i < n; i++) or for (int x : nums). Prefer a primitive int[] over Integer[] to avoid autoboxing overhead.",
    },
    "hashing": {
        "name": "Hash Maps & Sets",
        "what": "Structures giving average O(1) insertion and lookup, trading memory for speed.",
        "deep": "A hash table answers 'have I seen X?' or 'what maps to X?' in expected constant time, converting many O(n^2) pair scans into O(n) single passes. Worst case is O(n) per op under adversarial hashing, but that is rare in practice.",
        "java": "HashMap<K,V> and HashSet<E>. Use getOrDefault(k, 0) and merge(k, 1, Integer::sum) for counting, containsKey/add for membership. For dense int keys, an int[] beats a HashMap.",
    },
    "complement": {
        "name": "Complement Thinking",
        "what": "Instead of testing all pairs, ask what single value would complete the current one, and look it up.",
        "deep": "Reframes 'find two things that combine to T' as 'for each x, does T - x already exist?'. Paired with a hash structure this removes an entire nested loop, and the idea generalizes to differences, XORs, and remainders.",
        "java": "Keep a HashSet<Integer> or HashMap<Integer,Integer> of seen values and query target - x before inserting x.",
    },
    "two_pointers": {
        "name": "Two Pointers",
        "what": "Two indices moving through a sequence (from both ends, or at different speeds) to replace a nested loop.",
        "deep": "By advancing pointers based on a comparison you explore O(n) states instead of O(n^2). Common shapes are opposite ends converging (sorted pair sums, palindromes, rain water) and fast/slow (cycle detection). Correctness hinges on why the pointer you move cannot skip a better answer.",
        "java": "Two int indices lo/hi (or i/j) in a while (lo < hi) loop; no special class needed.",
    },
    "sliding_window": {
        "name": "Sliding Window",
        "what": "A moving sub-range [left, right] whose bounds expand and contract to maintain an invariant.",
        "deep": "Turns 'longest/best sub-array meeting a condition' into an amortized O(n) scan: extend the right edge, and when the invariant breaks advance the left edge. Each index enters and leaves the window at most once, which is why it stays linear.",
        "java": "Two int pointers plus a HashMap<Character,Integer> or an int[128] frequency table to track window contents.",
    },
    "stack": {
        "name": "Stack (LIFO)",
        "what": "A last-in-first-out structure whose top is always the most recent unmatched item.",
        "deep": "Ideal when the newest open item must be resolved first: bracket matching, monotonic-stack range queries, expression parsing, or iterative DFS. Push, pop, and peek are all O(1).",
        "java": "Use ArrayDeque<T> as a stack (push/pop/peek) - it is faster than the legacy Stack class. For brackets use Deque<Character>.",
    },
    "recursion": {
        "name": "Recursion",
        "what": "A function that calls itself on smaller inputs, with base cases that stop the descent.",
        "deep": "Expresses divide-and-conquer and tree/graph walks naturally. Watch the recursion depth against stack limits, and whether subproblems overlap - if they do, add memoization to avoid exponential blow-up.",
        "java": "A private static helper that calls itself. The JVM stack handles ~10^4 depth; convert to an explicit ArrayDeque if you risk StackOverflowError.",
    },
    "sorting": {
        "name": "Sorting",
        "what": "Ordering elements (usually O(n log n)) so structure like duplicates and order statistics becomes easy.",
        "deep": "Sorting is a preprocessing multiplier: it enables binary search, two-pointer sweeps, greedy choices, and grouping. The cost is O(n log n) comparisons, though counting/radix sort can beat that for bounded integer keys.",
        "java": "Arrays.sort(int[]) or Arrays.sort(T[], Comparator) / Collections.sort. For custom order use Comparator.comparingInt(...). Note primitive sort has no comparator overload.",
    },
    "binary_search": {
        "name": "Binary Search",
        "what": "Halving a sorted search space to find a target or boundary in O(log n).",
        "deep": "Beyond exact matches it locates boundaries (first/last occurrence, lower/upper bound) and can 'search on the answer' for any monotonic predicate. The subtle parts are the loop invariant and avoiding off-by-one at the boundary.",
        "java": "Arrays.binarySearch does not give first/last, so hand-roll while (lo <= hi) with mid = lo + (hi - lo) / 2 to avoid overflow.",
    },
    "dp": {
        "name": "Dynamic Programming",
        "what": "Breaking a problem into overlapping subproblems and reusing their answers.",
        "deep": "Applies when there is optimal substructure and overlapping subproblems. Two styles exist: top-down memoized recursion and bottom-up tabulation. Defining the state and transition precisely is the whole game, and space can often be rolled down a dimension.",
        "java": "A memo HashMap or an int[]/int[][] table. For memoization initialize a sentinel with Arrays.fill(dp, -1).",
    },
    "recurrence": {
        "name": "Recurrence Relations",
        "what": "Expressing an answer in terms of smaller answers, e.g. f(n) = f(n-1) + f(n-2).",
        "deep": "A recurrence is the mathematical heart of many DP and divide-and-conquer solutions. Once you name the base cases and the transition you can either recurse with memoization or iterate bottom-up, often reducing space to a few rolling variables.",
        "java": "Iterate bottom-up with a few long variables, or memoize with a long[] dp. Use long when terms grow fast.",
    },
    "dp2d": {
        "name": "2-D Dynamic Programming",
        "what": "A table dp[i][j] indexed by two dimensions, filled from smaller states.",
        "deep": "Used when the state needs two coordinates: prefixes of two sequences, positions in a grid, or index-plus-capacity. The fill order must respect dependencies, and many 2-D DPs compress to one row because dp[i] depends only on dp[i-1].",
        "java": "int[][] dp = new int[m + 1][n + 1] filled row by row; compress to two int[] rows (prev/cur) to save memory.",
    },
    "graph_repr": {
        "name": "Graph Representation",
        "what": "Modeling entities as nodes and relationships as edges, usually an adjacency list.",
        "deep": "The representation dictates efficiency: adjacency lists are O(V+E) space and iterate neighbors quickly, while adjacency matrices are O(V^2) but give O(1) edge tests. Directed vs undirected and weighted vs unweighted change how you build and traverse it.",
        "java": "List<List<Integer>> adj, or List<int[]>[] adj = new List[n] storing new int[]{to, w} for weighted edges.",
    },
    "bfs": {
        "name": "Breadth-First Search",
        "what": "Exploring a graph level by level with a queue; finds shortest paths in unweighted graphs.",
        "deep": "BFS visits nodes in order of distance from the source, so the first time it reaches a node is via a shortest unweighted path. It needs a queue and a visited marker and runs in O(V+E).",
        "java": "ArrayDeque<Integer> as the queue (offer/poll) plus a boolean[] visited. Mark visited when enqueuing, not dequeuing, to avoid duplicates.",
    },
    "flood_fill": {
        "name": "Flood Fill",
        "what": "Spreading outward from a start cell to mark an entire connected region of a grid.",
        "deep": "A grid-specialized BFS/DFS over 4- or 8-directional neighbors. Each launch consumes exactly one connected component, so counting launches counts components - islands, regions, or paint buckets.",
        "java": "From (r, c) run BFS/DFS over the four deltas {{1,0},{-1,0},{0,1},{0,-1}}, guarding bounds and the visited/grid state.",
    },
    "topo": {
        "name": "Topological Sort",
        "what": "Ordering the nodes of a DAG so every edge points forward; impossible iff there is a cycle.",
        "deep": "Applies to dependency problems like build order and course scheduling. Two algorithms exist: Kahn's (BFS on in-degrees) and DFS post-order. If not all nodes are emitted, the graph has a cycle.",
        "java": "Kahn's: an int[] indegree and an ArrayDeque queue of zero-indegree nodes; count how many you pop.",
    },
    "indegree": {
        "name": "In-degree / Kahn's Algorithm",
        "what": "Counting incoming edges and repeatedly removing zero-indegree nodes to order a DAG.",
        "deep": "In-degree is how many prerequisites a node still has. Start from nodes with none, complete them, and decrement their neighbors; newly-zeroed nodes become available. Finishing all n nodes means no cycle exists.",
        "java": "int[] indegree = new int[n]; increment per edge; seed an ArrayDeque with every node whose indegree is 0.",
    },
    "heap": {
        "name": "Priority Queue (Heap)",
        "what": "A structure that always yields the smallest or largest pending item in O(log n).",
        "deep": "A binary heap supports push and pop-min/max in O(log n) and peek in O(1). It powers greedy expansion (Dijkstra, Prim), top-k selection, and merging sorted streams, but it has no fast arbitrary lookup or deletion.",
        "java": "PriorityQueue<T> is a min-heap by default. For pairs use long[]/int[] with a comparator: new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0])).",
    },
    "greedy": {
        "name": "Greedy Choice",
        "what": "Taking the locally-best option at each step when that provably reaches a global optimum.",
        "deep": "Greedy is fast and simple but correct only when the problem has the greedy-choice property and optimal substructure; otherwise DP is the fallback. Proving correctness (often an exchange argument) matters more than the code.",
        "java": "Often just Arrays.sort plus a linear scan, or a PriorityQueue to always grab the current best.",
    },
    "prefix_max": {
        "name": "Running Maxima / Prefix Aggregates",
        "what": "Tracking the best value seen so far from the left/right to answer range questions in one pass.",
        "deep": "Precomputing prefix (and suffix) maxima, sums, or counts converts per-query O(n) work into O(1). It is the idea behind prefix sums and the left/right walls in rain-water style problems.",
        "java": "int[] prefix arrays, or two running int variables when you only need the maxima at the current index.",
    },
    "string_basics": {
        "name": "String Traversal",
        "what": "Treating a string as an indexable sequence of characters to count and compare.",
        "deep": "Most string problems reduce to a single pass with charAt or a char[]. Remember Java strings are immutable, so build output with StringBuilder, and character math relies on ASCII codes.",
        "java": "s.charAt(i), s.length(), s.toCharArray(); build results with StringBuilder, never += inside a loop.",
    },
    "canonical": {
        "name": "Canonical Form",
        "what": "Reducing equivalent items to one identical representative so they collide in a map.",
        "deep": "A canonical key makes 'are these the same up to X?' a simple equality or hash test. For anagrams it is the sorted letters, for fractions the reduced form, for graphs a normalized encoding. Choosing a cheap, collision-free key is the trick.",
        "java": "For anagrams: char[] c = s.toCharArray(); Arrays.sort(c); String key = new String(c); or a length-26 count signature.",
    },
    "math_digits": {
        "name": "Digit Manipulation",
        "what": "Working with a number's decimal digits or its string form while handling signs and edge cases.",
        "deep": "Digit problems peel digits with % 10 and / 10, or operate on the string form. Classic gotchas are negative numbers, trailing zeros, and overflow when reversing, so the first choice is arithmetic vs string handling.",
        "java": "n % 10 and n / 10 to extract digits, or Long.toString(n); use long to avoid overflow on reversal.",
    },
    "number_theory": {
        "name": "Number Theory Basics",
        "what": "Divisibility, gcd, and modular arithmetic facts used to reason about integers.",
        "deep": "Foundations like the Euclidean algorithm, prime factorization, and modular arithmetic underpin many math problems. Even simple tasks benefit from gcd/lcm identities and knowing how modulo distributes over addition and multiplication.",
        "java": "Math.floorMod for correct modulo of negatives; write a short gcd helper (Euclid); BigInteger has gcd() if needed.",
    },
    "modulo": {
        "name": "Modular Reduction",
        "what": "Using n % k to wrap indices around and drop redundant whole cycles.",
        "deep": "Modulo collapses equivalent states: rotating by k equals rotating by k % n, and hashing or bucketing uses remainders. In Java, beware that % can return a negative result for negative operands.",
        "java": "Use k % n after guarding n > 0; for possibly-negative values use Math.floorMod(x, n).",
    },
    "inplace_reverse": {
        "name": "In-place Reversal",
        "what": "Reversing a segment by swapping symmetric elements, using O(1) extra space.",
        "deep": "Swapping a[i] with a[n-1-i] for i in [0, n/2) reverses a range without allocation. It is the building block for array rotation (reverse-whole-then-parts) and for string reversal.",
        "java": "A helper void reverse(int[] a, int i, int j) { while (i < j) { int t = a[i]; a[i++] = a[j]; a[j--] = t; } }.",
    },
    "big_o": {
        "name": "Big-O / Complexity Analysis",
        "what": "Reasoning about how time and memory grow with the input size.",
        "deep": "Big-O bounds the dominant growth term and tells you whether an approach scales to the constraints. Read the limits: n up to 10^5 suggests O(n) or O(n log n), while 10^9 suggests O(log n) or O(1). Sanity-check the work against roughly 10^8 operations per second.",
        "java": "No API - this is analysis. Match your algorithm to the constraints stated in each problem before you start coding.",
    },
    "overflow": {
        "name": "Integer Overflow (int vs long)",
        "what": "Guarding against results that exceed a 32-bit int's range of about 2.1x10^9.",
        "deep": "Sums, products, and reversed numbers can silently wrap a 32-bit int, giving a wrong answer with no error. The fix is a wide enough type or a modulo reduction, so estimate the maximum magnitude before choosing the type.",
        "java": "int overflows past ~2.1e9; long reaches ~9.2e18. Cast early with (long) a * b and accumulate sums into a long.",
    },
    "char_arrays": {
        "name": "Char Arrays & ASCII",
        "what": "Manipulating characters via their numeric codes and mutable char arrays.",
        "deep": "Characters are small integers, so 'a'..'z' map to a 26-slot table via c - 'a'. Because Java strings are immutable, in-place character work needs a char[]. This underlies frequency counts, canonical keys, and in-place edits.",
        "java": "int idx = c - 'a'; char[] arr = s.toCharArray(); new String(arr) to rebuild. A length-26 or length-128 int[] beats a HashMap for letters.",
    },
    "visited_set": {
        "name": "Visited Tracking",
        "what": "Recording which nodes or cells are already processed so you never revisit or double-count.",
        "deep": "Graph and grid traversals loop forever or over-count without visited marks. Mark as early as possible (on enqueue) so a node is not added twice; for grids you can use a boolean[][] or mutate the input to a sentinel value.",
        "java": "boolean[] visited / boolean[][] seen, or overwrite grid cells (set '1' to '0') when mutation is allowed.",
    },
    "queue": {
        "name": "Queue (FIFO)",
        "what": "A first-in-first-out structure that returns items in arrival order.",
        "deep": "Queues drive breadth-first processing: BFS levels, Kahn's topological sort, and streaming buffers. Enqueue at the back and dequeue from the front, both in O(1).",
        "java": "ArrayDeque<T> via offer/poll (avoid the slower LinkedList, and never the legacy Stack/Vector).",
    },
    # ---- Foundational concepts for absolute beginners ----
    "io_basics": {
        "name": "Reading Input & Printing",
        "what": "Getting values in from standard input and writing answers out to standard output.",
        "deep": "Every problem here communicates over stdin/stdout: your program reads the input the grader feeds it and prints the answer. Reading the input format correctly is half the battle when you are starting out, so always match how many numbers or lines the problem describes.",
        "java": "Scanner sc = new Scanner(System.in); then sc.nextInt(), sc.next(), or sc.nextLine(). Print with System.out.println(...). Switch to BufferedReader later for speed.",
    },
    "variables": {
        "name": "Variables & Types",
        "what": "Named boxes that hold values of a specific type such as int, long, double, boolean, or String.",
        "deep": "A variable stores a value you can read and update. Java is statically typed, so you declare the type up front and it never changes. Picking the right type (int vs long, int vs double) prevents overflow and rounding surprises down the line.",
        "java": "Declare with a type: int n = 5; long big = 10000000000L; double d = 3.14; boolean ok = true; String s = ... .",
    },
    "arithmetic": {
        "name": "Arithmetic & Operators",
        "what": "Doing math with +, -, *, / and the remainder operator %.",
        "deep": "Operators combine values. The Java gotchas: integer division truncates (7 / 2 is 3, not 3.5), % gives the remainder (great for even/odd and wrapping), and mixing an int with a double promotes the result to double.",
        "java": "Use +, -, *, /, %. Note 7 / 2 == 3 (int) but 7.0 / 2 == 3.5 (double). Math.max, Math.min, Math.abs help too.",
    },
    "conditionals": {
        "name": "Conditionals (if / else)",
        "what": "Choosing what to do based on whether a condition is true.",
        "deep": "if/else branches let your program react to data. The condition is a boolean expression built from comparisons (==, !=, <, >) and logic (&&, ||, !). Chain several with else if when there are more than two outcomes.",
        "java": "if (n % 2 == 0) { ... } else { ... }. Compare ints with ==, but compare Strings with .equals(), never ==.",
    },
    "loops_basic": {
        "name": "Loops (for / while)",
        "what": "Repeating a block of code a set number of times or until a condition changes.",
        "deep": "A for-loop fits when you know the count; a while-loop when you stop on a condition. Loops are how you process every element or accumulate a running result, and getting the start/end bounds right is the main beginner pitfall.",
        "java": "for (int i = 1; i <= n; i++) { ... } or while (condition) { ... }. Build output strings with StringBuilder inside the loop.",
    },
    "boolean_logic": {
        "name": "Booleans & Comparison",
        "what": "True/false values and the operators that combine them.",
        "deep": "Comparisons produce booleans, and &&, ||, ! combine them. Short-circuit evaluation means the right side of && is skipped when the left is false, which is both handy and sometimes necessary to avoid errors.",
        "java": "boolean type; comparisons ==, !=, <, <=, >, >=; logic && (and), || (or), ! (not).",
    },
}

PREREQS = {
    "print-greeting": [
        ("io_basics", "Even with no numbers to read, you must print the exact text to standard output for the grader to accept it."),
        ("string_basics", "The greeting is a fixed piece of text you print exactly, including its punctuation."),
    ],
    "echo-line": [
        ("io_basics", "You read one line of input and print it straight back out."),
        ("variables", "Store the line in a String variable, then print that variable."),
    ],
    "add-two-numbers": [
        ("io_basics", "Read the two integers that arrive on the input."),
        ("variables", "Hold each number in its own int variable."),
        ("arithmetic", "Add them with the + operator and print the result."),
    ],
    "rectangle-area": [
        ("io_basics", "Read the width and height from the input line."),
        ("variables", "Keep width and height in int variables."),
        ("arithmetic", "Area is width times height - use the * operator."),
    ],
    "even-or-odd": [
        ("io_basics", "Read the single integer to test."),
        ("arithmetic", "n % 2 is 0 for even numbers and non-zero for odd ones."),
        ("conditionals", "Use if/else to print Even or Odd based on that remainder."),
    ],
    "larger-of-two": [
        ("io_basics", "Read the two integers to compare."),
        ("variables", "Store both numbers so you can compare them."),
        ("conditionals", "Compare with > and print the larger, or just use Math.max."),
    ],
    "sum-to-n": [
        ("io_basics", "Read the single value n."),
        ("loops_basic", "Loop i from 1 to n, adding each i to a running total."),
        ("arithmetic", "Or use the closed form n*(n+1)/2 - either way, accumulate carefully."),
    ],
    "countdown": [
        ("io_basics", "Read the starting value n."),
        ("loops_basic", "Loop i from n down to 1, emitting each number."),
        ("string_basics", "Join the numbers into one line separated by spaces (a StringBuilder is tidy)."),
    ],
    "array-sum": [
        ("big_o", "The single loop touches each of the n elements once, so the time is Theta(n) - you must read every value to sum it, and no approach is faster."),
        ("iteration", "You keep a running total and add each element as you pass over the array exactly once."),
        ("overflow", "With up to 10^5 values as large as 10^9, the sum can reach ~10^14, which overflows a 32-bit int - accumulate into a long."),
    ],
    "reverse-string": [
        ("two_pointers", "Put one index at the start and one at the end, swap the characters, and step them toward the middle until they cross."),
        ("inplace_reverse", "Swapping symmetric positions reverses the text using no extra array - O(1) auxiliary space."),
        ("char_arrays", "Java strings are immutable, so convert with toCharArray(), swap in place, then rebuild via new String(arr)."),
    ],
    "count-vowels": [
        ("string_basics", "You walk the string once, inspecting each character in turn."),
        ("hashing", "Storing the five vowels in a set makes each 'is this a vowel?' test O(1) instead of up to five comparisons."),
        ("char_arrays", "Iterate with charAt(i) or over toCharArray() and compare each char against the vowel set."),
    ],
    "gcd": [
        ("number_theory", "The gcd is the largest integer dividing both inputs; Euclid's insight is that gcd(a, b) equals gcd(b, a mod b)."),
        ("recursion", "That identity is naturally recursive - recurse on (b, a % b) until the second argument is 0, then a is the answer (a while-loop works too)."),
        ("modulo", "The % operator drives each step, and the base case is gcd(x, 0) = x."),
    ],
    "palindrome-number": [
        ("math_digits", "You compare digits from the two ends inward; a leading minus sign means it can never be a palindrome."),
        ("two_pointers", "Comparing the decimal string from outside in is the classic two-pointer palindrome test."),
        ("overflow", "If you reverse the number arithmetically instead of as a string, the reversed value can overflow int - use long or compare the string form."),
    ],
    "nth-fibonacci": [
        ("recurrence", "Each term is the sum of the previous two: F(n) = F(n-1) + F(n-2), with F(0)=0 and F(1)=1."),
        ("dp", "Naive recursion recomputes terms exponentially; keep only the last two values and roll forward in O(n)."),
        ("overflow", "F(90) is about 2.9x10^18 - it fits in a long but not an int, so use long."),
    ],
    "two-sum-exists": [
        ("hashing", "A HashSet of values already seen answers 'is the complement present?' in O(1) average time."),
        ("complement", "For each x the partner you need is target - x; checking the set for it avoids the O(n^2) all-pairs scan."),
        ("big_o", "One pass with O(1) lookups gives Theta(n) time and Theta(n) space - the standard time/space trade-off."),
    ],
    "two-sum-indices": [
        ("hashing", "Use a HashMap from value to index so you can recover the partner's position, not just whether it exists."),
        ("complement", "As you scan, look up target - nums[i]; if present you have both indices (remember the answer is 1-based)."),
        ("iteration", "Insert each value into the map only after checking, so an element is never paired with itself."),
    ],
    "longest-unique-substring": [
        ("sliding_window", "Maintain a window [left, right] of all-distinct characters; extend right each step and pull left forward when a repeat enters."),
        ("hashing", "A map from character to last index lets you jump left directly past a previous occurrence instead of shrinking one step at a time."),
        ("string_basics", "Track the best window width as you scan the string exactly once."),
    ],
    "valid-parentheses": [
        ("stack", "Every closer must match the most recently opened bracket - that most-recent rule is exactly a stack."),
        ("string_basics", "Scan left to right, pushing openers and popping on closers."),
        ("hashing", "A small map from closing to opening bracket keeps the matching logic clean."),
    ],
    "binary-search-first": [
        ("binary_search", "Halve the sorted range each step; the trick for the FIRST occurrence is to keep searching left even after a match."),
        ("sorting", "The method only works because the input is already sorted non-decreasing."),
        ("big_o", "This turns an O(n) scan into O(log n) - the payoff of exploiting sorted order."),
    ],
    "maximum-subarray": [
        ("dp", "Kadane's algorithm asks 'best sum ending here?' and reuses the previous answer: cur = max(a[i], cur + a[i])."),
        ("iteration", "A single left-to-right pass maintains cur and the global best."),
        ("overflow", "With 10^5 values up to 10^9, sums can exceed int range - use long for the running and best sums."),
    ],
    "climbing-stairs": [
        ("recurrence", "You reach step n from n-1 or n-2, so ways(n) = ways(n-1) + ways(n-2)."),
        ("dp", "It is Fibonacci in disguise; iterate with two rolling counters instead of exponential recursion."),
        ("overflow", "ways(45) is about 1.8x10^9, right at the int limit, so a long is safest."),
    ],
    "rotate-array": [
        ("modulo", "Rotating by n is a no-op, so first reduce k to k % n; k can be as large as 10^9."),
        ("inplace_reverse", "Reverse the whole array, then the first k and the remaining n-k - three reversals rotate in O(1) space."),
        ("iteration", "Alternatively copy each element to index (i + k) % n in a fresh array - simpler but O(n) extra space."),
    ],
    "number-of-islands": [
        ("graph_repr", "Treat each cell as a node with edges to its up/down/left/right land neighbors."),
        ("bfs", "From each new land cell a queue floods outward, marking the whole connected region."),
        ("flood_fill", "Each time you start a flood from an unvisited '1' you have found one more island."),
        ("visited_set", "Mark cells visited (a boolean[][] or by overwriting the grid) so regions are not counted twice."),
    ],
    "group-anagrams-count": [
        ("canonical", "Sorting a word's letters yields a canonical key that all of its anagrams share."),
        ("hashing", "Putting those keys in a HashSet collapses anagrams together, so the answer is the number of distinct keys."),
        ("sorting", "You sort each word's characters - O(k log k) per word of length k - to build the key."),
    ],
    "course-schedule": [
        ("graph_repr", "Courses are nodes; a prerequisite 'a needs b' is a directed edge b -> a stored as an adjacency list."),
        ("topo", "You can finish everything exactly when the graph is a DAG - a valid order exists iff there is no cycle."),
        ("indegree", "Kahn's algorithm counts incoming edges and repeatedly removes zero-indegree courses; if all n are removed, no cycle exists."),
        ("queue", "A queue holds the currently takeable (zero-prerequisite) courses as you process them."),
    ],
    "longest-increasing-subsequence": [
        ("dp", "The O(n^2) view is dp[i] = longest increasing subsequence ending at index i, built from earlier indices."),
        ("binary_search", "The O(n log n) method keeps a tails array and binary-searches the first tail >= the current value to overwrite."),
        ("greedy", "Greedily keeping the smallest possible tail for each length lets more elements extend the sequence later."),
    ],
    "edit-distance": [
        ("dp2d", "dp[i][j] is the edit distance between the first i characters of word1 and the first j of word2, filled from smaller prefixes."),
        ("recurrence", "On a character match dp[i][j] = dp[i-1][j-1]; otherwise it is 1 + min(insert, delete, replace)."),
        ("string_basics", "Index both strings by prefix length; the 2-D table can be compressed to a single rolling row."),
    ],
    "trapping-rain-water": [
        ("prefix_max", "The water above a bar equals min(highest bar to its left, highest to its right) minus its own height."),
        ("two_pointers", "Two pointers move inward, and the side with the smaller running max is the one safely bounded, giving O(1) space."),
        ("big_o", "Both the prefix-max and two-pointer approaches are Theta(n); the two-pointer one drops the extra arrays."),
    ],
    "dijkstra-shortest-path": [
        ("graph_repr", "Store the weighted graph as an adjacency list of (neighbor, weight) pairs per node."),
        ("heap", "A min-priority-queue always hands you the closest unfinalized node, which is why Dijkstra is efficient."),
        ("greedy", "Finalizing the nearest node first is provably correct because all edge weights are non-negative."),
        ("visited_set", "Skip stale queue entries (a popped distance greater than the best known) so each node is finalized once."),
    ],
}


def build_prereqs(slug):
    out = []
    for key, how in PREREQS.get(slug, []):
        c = CONCEPTS[key]
        out.append({
            "key": key,
            "name": c["name"],
            "what": c["what"],
            "deep": c["deep"],
            "java": c["java"],
            "how": how,
        })
    return out


# ---------------------------------------------------------------------------
# Intro problems (below Easy) for someone new to Java.
# ---------------------------------------------------------------------------

def sol_print_greeting(inp):
    return "Hello, World!"

def sol_echo_line(inp):
    return inp.split("\n")[0] if inp else ""

def sol_add_two(inp):
    a, b = map(int, inp.split())
    return str(a + b)

def sol_rectangle_area(inp):
    w, h = map(int, inp.split())
    return str(w * h)

def sol_even_or_odd(inp):
    return "Even" if int(inp) % 2 == 0 else "Odd"

def sol_larger_of_two(inp):
    a, b = map(int, inp.split())
    return str(max(a, b))

def sol_sum_to_n(inp):
    n = int(inp)
    return str(n * (n + 1) // 2)

def sol_countdown(inp):
    n = int(inp)
    return " ".join(str(i) for i in range(n, 0, -1))


INTRO_DEFS = [
    dict(
        slug="print-greeting", title="Print a Greeting", difficulty="Intro",
        topics=["Basics"], subtopics=["Output"],
        description="Print exactly the text `Hello, World!` (without the backticks).\n\n### Input\nThere is no input.\n\n### Output\nA single line: `Hello, World!`",
        constraints="None.",
        hints=[
            "System.out.println prints a line of text.",
            "Copy the text exactly, including the comma and exclamation mark.",
            "Capitalization matters: H and W are uppercase.",
            "Print: Hello, World!",
        ],
        opt=("O(1)", "O(1)", "A single print statement; there is nothing to read."),
        editorial="## Approach\nThere is no input to read. Just print the fixed string with `System.out.println(\"Hello, World!\")`. This warms up the read-nothing / print-something shape used everywhere.",
        ref=sol_print_greeting,
        starter_py="# TODO: print exactly:  Hello, World!\n",
        cases=[
            ("example", "Only case", ""),
            ("hidden", "Grader check", ""),
        ],
        example_expl=["No input is given; simply print the greeting."],
    ),
    dict(
        slug="echo-line", title="Echo", difficulty="Intro",
        topics=["Basics"], subtopics=["Input/Output"],
        description="Read one line of text and print it back unchanged.\n\n### Input\nA single line.\n\n### Output\nThe same line.",
        constraints="1 ≤ line length ≤ 1000",
        hints=[
            "Read a whole line, not just one word.",
            "Scanner.nextLine() or BufferedReader.readLine() reads a line.",
            "Then print exactly what you read.",
            "Do not add extra text.",
        ],
        opt=("O(n)", "O(n)", "You copy the line once."),
        editorial="## Approach\nRead the line with `nextLine()` (or `readLine()`), then print it. This teaches reading text input versus numbers.",
        ref=sol_echo_line,
        starter_py="# TODO: read one line and print it\n",
        cases=[
            ("example", "Word", "hello\n"),
            ("hidden", "Sentence", "Java is fun\n"),
            ("hidden", "Digits", "12345\n"),
        ],
        example_expl=["The input line is printed back unchanged."],
    ),
    dict(
        slug="add-two-numbers", title="Add Two Numbers", difficulty="Intro",
        topics=["Basics"], subtopics=["Arithmetic"],
        description="Read two integers and print their sum.\n\n### Input\nTwo integers `a b` on one line.\n\n### Output\nThe value of a + b.",
        constraints="-10^9 ≤ a, b ≤ 10^9",
        hints=[
            "Read two integers with sc.nextInt() twice.",
            "Store them in int variables.",
            "Add with the + operator.",
            "Print the result.",
        ],
        opt=("O(1)", "O(1)", "Read two numbers and add them."),
        editorial="## Approach\nRead `a` and `b`, then print `a + b`. The sum of two values up to 10^9 stays within int here, but using long is a safe habit.",
        ref=sol_add_two,
        starter_py="a, b = map(int, input().split())\n# TODO: print a + b\n",
        cases=[
            ("example", "Positives", "2 3\n"),
            ("example", "Negative", "-4 10\n"),
            ("hidden", "Zeros", "0 0\n"),
            ("hidden", "Large", "1000000 2000000\n"),
            ("hidden", "Both negative", "-5 -7\n"),
        ],
        example_expl=["2 + 3 = 5.", "-4 + 10 = 6."],
    ),
    dict(
        slug="rectangle-area", title="Rectangle Area", difficulty="Intro",
        topics=["Basics"], subtopics=["Arithmetic"],
        description="Given a rectangle's width and height, print its area.\n\n### Input\nTwo integers `w h` on one line.\n\n### Output\nThe area (w times h).",
        constraints="1 ≤ w, h ≤ 10^4",
        hints=[
            "Area is width multiplied by height.",
            "Use the * operator.",
            "Read both integers first.",
            "Print w * h.",
        ],
        opt=("O(1)", "O(1)", "One multiplication."),
        editorial="## Approach\nRead `w` and `h` and print `w * h`. A gentle introduction to multiplication and reading two values.",
        ref=sol_rectangle_area,
        starter_py="w, h = map(int, input().split())\n# TODO: print w * h\n",
        cases=[
            ("example", "3 by 4", "3 4\n"),
            ("hidden", "Square", "5 5\n"),
            ("hidden", "Thin", "10 1\n"),
            ("hidden", "Six by seven", "7 6\n"),
        ],
        example_expl=["3 x 4 = 12."],
    ),
    dict(
        slug="even-or-odd", title="Even or Odd", difficulty="Intro",
        topics=["Basics"], subtopics=["Conditionals"],
        description="Decide whether a number is even or odd.\n\n### Input\nA single integer `n`.\n\n### Output\n`Even` if n is even, otherwise `Odd`.",
        constraints="-10^9 ≤ n ≤ 10^9",
        hints=[
            "A number is even when it divides by 2 with no remainder.",
            "n % 2 == 0 means even.",
            "Use if/else to choose the word.",
            "Print exactly Even or Odd.",
        ],
        opt=("O(1)", "O(1)", "One remainder test."),
        editorial="## Approach\nCompute `n % 2`. If it is 0 print `Even`, otherwise print `Odd`. This is your first conditional.",
        ref=sol_even_or_odd,
        starter_py="n = int(input())\n# TODO: print 'Even' or 'Odd'\n",
        cases=[
            ("example", "Even", "4\n"),
            ("example", "Odd", "7\n"),
            ("hidden", "Zero", "0\n"),
            ("hidden", "Negative odd", "-3\n"),
            ("hidden", "Big even", "100\n"),
        ],
        example_expl=["4 divides evenly by 2, so Even.", "7 leaves remainder 1, so Odd."],
    ),
    dict(
        slug="larger-of-two", title="Larger of Two", difficulty="Intro",
        topics=["Basics"], subtopics=["Conditionals"],
        description="Print the larger of two integers.\n\n### Input\nTwo integers `a b` on one line.\n\n### Output\nThe larger value (if equal, print that value).",
        constraints="-10^9 ≤ a, b ≤ 10^9",
        hints=[
            "Compare the two numbers.",
            "a > b means a is larger.",
            "Math.max(a, b) does this in one call.",
            "Print the larger one.",
        ],
        opt=("O(1)", "O(1)", "One comparison."),
        editorial="## Approach\nCompare `a` and `b` with an if/else, or simply print `Math.max(a, b)`.",
        ref=sol_larger_of_two,
        starter_py="a, b = map(int, input().split())\n# TODO: print the larger of a and b\n",
        cases=[
            ("example", "Second larger", "3 8\n"),
            ("hidden", "First larger", "10 2\n"),
            ("hidden", "Equal", "5 5\n"),
            ("hidden", "Negatives", "-1 -4\n"),
        ],
        example_expl=["8 is larger than 3."],
    ),
    dict(
        slug="sum-to-n", title="Sum From 1 to N", difficulty="Intro",
        topics=["Basics"], subtopics=["Loops"],
        description="Add up all integers from 1 to n.\n\n### Input\nA single integer `n`.\n\n### Output\n1 + 2 + ... + n.",
        constraints="1 ≤ n ≤ 10^4",
        hints=[
            "A for-loop from 1 to n can add each number.",
            "Keep a running total variable starting at 0.",
            "Add i to the total each iteration.",
            "There is also a formula: n*(n+1)/2.",
        ],
        opt=("O(1)", "O(1)", "The closed form n*(n+1)/2 avoids the loop, though an O(n) loop is perfectly fine here."),
        editorial="## Approach\nLoop `i` from 1 to n adding to a running `sum`, then print it. Or use the closed form `n*(n+1)/2`. Your first loop that accumulates a result.",
        ref=sol_sum_to_n,
        starter_py="n = int(input())\n# TODO: add 1..n and print the total\n",
        cases=[
            ("example", "Five", "5\n"),
            ("example", "One", "1\n"),
            ("hidden", "Hundred", "100\n"),
            ("hidden", "Ten", "10\n"),
            ("hidden", "Max", "10000\n"),
        ],
        example_expl=["1+2+3+4+5 = 15.", "Just 1."],
    ),
    dict(
        slug="countdown", title="Countdown", difficulty="Intro",
        topics=["Basics"], subtopics=["Loops"],
        description="Print the numbers from n down to 1 on one line, separated by single spaces.\n\n### Input\nA single integer `n`.\n\n### Output\n`n n-1 ... 1` separated by spaces.",
        constraints="1 ≤ n ≤ 1000",
        hints=[
            "A for-loop can count downward: start at n, step -1.",
            "Print each number followed by a space (or join them).",
            "A StringBuilder keeps the output tidy.",
            "Do not print a trailing newline between numbers.",
        ],
        opt=("O(n)", "O(n)", "You emit n numbers."),
        editorial="## Approach\nLoop `i` from n down to 1, appending each to a StringBuilder with spaces, then print. Practice with a decreasing loop.",
        ref=sol_countdown,
        starter_py="n = int(input())\n# TODO: print n, n-1, ..., 1 on one line separated by spaces\n",
        cases=[
            ("example", "Five", "5\n"),
            ("example", "One", "1\n"),
            ("hidden", "Three", "3\n"),
            ("hidden", "Ten", "10\n"),
        ],
        example_expl=["Counts down from 5 to 1.", "Only 1."],
    ),
]

# Intro problems come first.
DEFS = INTRO_DEFS + DEFS


# ---------------------------------------------------------------------------
# Java starter code per problem (Poodcode is Java-centered).
# Each reads the documented stdin format and leaves a `solve(...)` / TODO stub.
# ---------------------------------------------------------------------------

JAVA_STARTERS = {
    "print-greeting": """public class Main {
    public static void main(String[] args) {
        // TODO: print exactly  Hello, World!
        System.out.println();
    }
}
""",
    "echo-line": """import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        // TODO: print the line
    }
}
""",
    "add-two-numbers": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        // TODO: print a + b
    }
}
""",
    "rectangle-area": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int w = sc.nextInt();
        int h = sc.nextInt();
        // TODO: print the area (w * h)
    }
}
""",
    "even-or-odd": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        // TODO: print "Even" or "Odd"
    }
}
""",
    "larger-of-two": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        // TODO: print the larger of a and b
    }
}
""",
    "sum-to-n": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        long sum = 0;
        // TODO: add 1, 2, ..., n to sum
        System.out.println(sum);
    }
}
""",
    "countdown": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        StringBuilder sb = new StringBuilder();
        // TODO: append n, n-1, ..., 1 separated by spaces
        System.out.println(sb.toString().trim());
    }
}
""",
    "array-sum": """import java.util.*;

public class Main {
    static long solve(int[] nums) {
        // TODO: return the sum of nums (use long!)
        return 0;
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();
        System.out.println(solve(nums));
    }
}
""",
    "reverse-string": """import java.io.*;

public class Main {
    static String solve(String s) {
        // TODO: return s reversed
        return s;
    }
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null) s = "";
        System.out.println(solve(s));
    }
}
""",
    "count-vowels": """import java.io.*;

public class Main {
    static int solve(String s) {
        // TODO: count vowels a, e, i, o, u
        return 0;
    }
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null) s = "";
        System.out.println(solve(s));
    }
}
""",
    "gcd": """import java.util.*;

public class Main {
    static long solve(long a, long b) {
        // TODO: return gcd(a, b)
        return 0;
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long a = sc.nextLong();
        long b = sc.nextLong();
        System.out.println(solve(a, b));
    }
}
""",
    "palindrome-number": """import java.io.*;

public class Main {
    // n is the integer in String form.
    static String solve(String n) {
        // TODO: return "true" or "false"
        return "false";
    }
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String n = br.readLine().trim();
        System.out.println(solve(n));
    }
}
""",
    "nth-fibonacci": """import java.util.*;

public class Main {
    static long solve(int n) {
        // TODO: return F(n)
        return 0;
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        System.out.println(solve(n));
    }
}
""",
    "two-sum-exists": """import java.util.*;

public class Main {
    static String solve(int[] nums, long target) {
        // TODO: return "YES" or "NO"
        return "NO";
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();
        long target = sc.nextLong();
        System.out.println(solve(nums, target));
    }
}
""",
    "two-sum-indices": """import java.util.*;

public class Main {
    // Return the two 1-based indices as "i j".
    static String solve(int[] nums, long target) {
        // TODO
        return "-1";
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();
        long target = sc.nextLong();
        System.out.println(solve(nums, target));
    }
}
""",
    "longest-unique-substring": """import java.io.*;

public class Main {
    static int solve(String s) {
        // TODO: length of longest substring without repeats
        return 0;
    }
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null) s = "";
        System.out.println(solve(s));
    }
}
""",
    "valid-parentheses": """import java.io.*;
import java.util.*;

public class Main {
    static String solve(String s) {
        // TODO: return "true" or "false"
        return "false";
    }
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        if (s == null) s = "";
        System.out.println(solve(s));
    }
}
""",
    "binary-search-first": """import java.util.*;

public class Main {
    static int solve(int[] arr, int target) {
        // TODO: first index of target, or -1
        return -1;
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = sc.nextInt();
        int target = sc.nextInt();
        System.out.println(solve(arr, target));
    }
}
""",
    "maximum-subarray": """import java.util.*;

public class Main {
    static long solve(int[] nums) {
        // TODO: maximum subarray sum (use long)
        return 0;
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();
        System.out.println(solve(nums));
    }
}
""",
    "climbing-stairs": """import java.util.*;

public class Main {
    static long solve(int n) {
        // TODO: number of ways to climb n steps
        return 0;
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        System.out.println(solve(n));
    }
}
""",
    "rotate-array": """import java.util.*;

public class Main {
    static int[] solve(int[] arr, long k) {
        // TODO: rotate arr right by k and return it
        return arr;
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = sc.nextInt();
        long k = sc.nextLong();
        int[] res = solve(arr, k);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < res.length; i++) {
            if (i > 0) sb.append(' ');
            sb.append(res[i]);
        }
        System.out.println(sb.toString());
    }
}
""",
    "number-of-islands": """import java.io.*;
import java.util.*;

public class Main {
    static int solve(char[][] grid, int r, int c) {
        // TODO: count islands (4-directional)
        return 0;
    }
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int r = Integer.parseInt(st.nextToken());
        int c = Integer.parseInt(st.nextToken());
        char[][] grid = new char[r][];
        for (int i = 0; i < r; i++) grid[i] = br.readLine().toCharArray();
        System.out.println(solve(grid, r, c));
    }
}
""",
    "group-anagrams-count": """import java.io.*;
import java.util.*;

public class Main {
    static int solve(String[] words) {
        // TODO: number of anagram groups
        return 0;
    }
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        String[] words = new String[n];
        for (int i = 0; i < n; i++) words[i] = br.readLine();
        System.out.println(solve(words));
    }
}
""",
    "course-schedule": """import java.io.*;
import java.util.*;

public class Main {
    // edges[i] = {a, b} means b must be taken before a.
    static String solve(int n, int[][] edges) {
        // TODO: return "true" if all courses can be finished, else "false"
        return "true";
    }
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());
        int[][] edges = new int[m][2];
        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            edges[i][0] = Integer.parseInt(st.nextToken());
            edges[i][1] = Integer.parseInt(st.nextToken());
        }
        System.out.println(solve(n, edges));
    }
}
""",
    "longest-increasing-subsequence": """import java.util.*;

public class Main {
    static int solve(int[] nums) {
        // TODO: length of the LIS
        return 0;
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();
        System.out.println(solve(nums));
    }
}
""",
    "edit-distance": """import java.io.*;

public class Main {
    static int solve(String a, String b) {
        // TODO: return the edit distance
        return 0;
    }
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String a = br.readLine();
        String b = br.readLine();
        if (a == null) a = "";
        if (b == null) b = "";
        System.out.println(solve(a, b));
    }
}
""",
    "trapping-rain-water": """import java.util.*;

public class Main {
    static long solve(int[] h) {
        // TODO: total trapped water
        return 0;
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] h = new int[n];
        for (int i = 0; i < n; i++) h[i] = sc.nextInt();
        System.out.println(solve(h));
    }
}
""",
    "dijkstra-shortest-path": """import java.io.*;
import java.util.*;

public class Main {
    // edges[i] = {u, v, w}, undirected.
    static long solve(int n, int[][] edges, int s, int t) {
        // TODO: shortest distance s -> t, or -1 if unreachable
        return -1;
    }
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());
        int[][] edges = new int[m][3];
        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            edges[i][0] = Integer.parseInt(st.nextToken());
            edges[i][1] = Integer.parseInt(st.nextToken());
            edges[i][2] = Integer.parseInt(st.nextToken());
        }
        st = new StringTokenizer(br.readLine());
        int s = Integer.parseInt(st.nextToken());
        int t = Integer.parseInt(st.nextToken());
        System.out.println(solve(n, edges, s, t));
    }
}
""",
}


# Grouping for the Learn page.
CATEGORY = {
    "io_basics": "Foundations", "variables": "Foundations", "arithmetic": "Foundations",
    "conditionals": "Foundations", "loops_basic": "Foundations", "boolean_logic": "Foundations",
    "string_basics": "Strings", "char_arrays": "Strings", "canonical": "Strings",
    "iteration": "Arrays", "inplace_reverse": "Arrays", "prefix_max": "Arrays",
    "two_pointers": "Arrays", "sliding_window": "Arrays",
    "hashing": "Data Structures", "stack": "Data Structures", "queue": "Data Structures",
    "heap": "Data Structures", "visited_set": "Data Structures", "complement": "Data Structures",
    "sorting": "Searching & Sorting", "binary_search": "Searching & Sorting", "greedy": "Searching & Sorting",
    "recursion": "Recursion & DP", "dp": "Recursion & DP", "recurrence": "Recursion & DP", "dp2d": "Recursion & DP",
    "graph_repr": "Graphs", "bfs": "Graphs", "flood_fill": "Graphs", "topo": "Graphs", "indegree": "Graphs",
    "big_o": "Foundations", "overflow": "Foundations", "math_digits": "Math", "number_theory": "Math", "modulo": "Math",
}


# Detailed teaching pages (Markdown) for every concept.
LESSONS = {
    "io_basics": """### Worked example
The grader sends text on **standard input**; you reply on **standard output**. If the input is `3 4`, you read the two numbers and print their sum, `7`.

### In code (Java)
```java
import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();       // reads 3
        int b = sc.nextInt();       // reads 4
        System.out.println(a + b);  // prints 7
    }
}
```

### Watch out for
- `nextInt()` reads one number; `nextLine()` reads a whole line (use it for text).
- Print **only** the answer. Extra text like `Enter a number:` will fail the grader.
""",
    "variables": """### Worked example
A variable is a labelled box. `int score = 0;` makes a box named `score` holding 0; `score = score + 10;` updates it to 10.

### In code (Java)
```java
int count = 5;               // whole number
long big = 5_000_000_000L;   // too big for int -> long, note the L
double avg = 4.5;            // decimal
boolean done = false;        // true / false
String name = "Ada";         // text
```

### Watch out for
- `int` holds about plus or minus 2.1 billion; if a value can exceed that, use `long`.
- Dividing two `int`s drops the fraction (`7 / 2` is `3`). Use `double` for `3.5`.
""",
    "arithmetic": """### Worked example
`%` (remainder) is the beginner's secret weapon: `17 % 5` is `2`, and `n % 2 == 0` tests even.

### In code (Java)
```java
int a = 17, b = 5;
System.out.println(a + b);   // 22
System.out.println(a / b);   // 3   (integer division)
System.out.println(a % b);   // 2   (remainder)
System.out.println(7.0 / 2); // 3.5 (double math)
```

### Watch out for
- Integer division truncates toward zero — there is no rounding.
- `%` of a negative can be negative in Java (`-3 % 2` is `-1`).
""",
    "conditionals": """### Worked example
Label a number: if it divides evenly by 2 it is Even, otherwise Odd.

### In code (Java)
```java
int n = 7;
if (n % 2 == 0) {
    System.out.println("Even");
} else {
    System.out.println("Odd");
}
```

### Watch out for
- Compare numbers with `==`, but compare Strings with `a.equals(b)`.
- Use `else if` to chain more than two outcomes.
""",
    "loops_basic": """### Worked example
Add 1..n. For n = 5 you want 1+2+3+4+5 = 15.

### In code (Java)
```java
int n = 5;
long sum = 0;
for (int i = 1; i <= n; i++) {
    sum += i;   // 1, 3, 6, 10, 15
}
System.out.println(sum);
```

### Watch out for
- Off-by-one: `i <= n` includes n, `i < n` stops one short.
- Count down with `for (int i = n; i >= 1; i--)`.
""",
    "boolean_logic": """### Worked example
A number is in the range [1, 10] when it is `>= 1` **and** `<= 10`.

### In code (Java)
```java
int x = 7;
boolean inRange = (x >= 1) && (x <= 10); // true
boolean outside = (x < 1) || (x > 10);   // false
System.out.println(inRange && !outside); // true
```

### Watch out for
- `&&` and `||` short-circuit: the right side is skipped once the result is known.
- `=` assigns while `==` compares — a very common typo.
""",
    "string_basics": """### Worked example
Count the letter `a` in `"banana"` — the answer is 3.

### In code (Java)
```java
String s = "banana";
int count = 0;
for (int i = 0; i < s.length(); i++) {
    if (s.charAt(i) == 'a') count++;
}
System.out.println(count); // 3
```

### Watch out for
- Strings are immutable; build output with `StringBuilder`, not `+=` in a loop.
- Index characters with `charAt(i)` (0-based) and compare Strings with `.equals`.
""",
    "char_arrays": """### Worked example
Reverse `"code"` in place by converting to a char array and swapping the ends.

### In code (Java)
```java
char[] c = "code".toCharArray();
int i = 0, j = c.length - 1;
while (i < j) { char t = c[i]; c[i++] = c[j]; c[j--] = t; }
System.out.println(new String(c)); // edoc

int[] freq = new int[26];
for (char ch : "aab".toCharArray()) freq[ch - 'a']++;
```

### Watch out for
- `ch - 'a'` maps 'a'..'z' to 0..25 — a fast index into a size-26 array.
- Rebuild a String with `new String(charArray)`.
""",
    "iteration": """### Worked example
Find the maximum of `[3, 9, 2, 7]` in one pass: start from the first element and update when you see something bigger.

### In code (Java)
```java
int[] a = {3, 9, 2, 7};
int best = a[0];
for (int i = 1; i < a.length; i++) {
    if (a[i] > best) best = a[i];
}
System.out.println(best); // 9
```

### Watch out for
- Initialize `best` from `a[0]`, not `0` — the array might be all negative.
- One pass is O(n); avoid nesting a second loop when a running variable suffices.
""",
    "hashing": """### Worked example
Does the array have a duplicate? Track seen values in a set; if one appears twice, yes.

### In code (Java)
```java
int[] a = {1, 3, 2, 3};
Set<Integer> seen = new HashSet<>();
for (int x : a) {
    if (!seen.add(x)) { System.out.println("duplicate"); break; }
}
```

### Watch out for
- `add` returns false if the value was already present — a tidy one-line check.
- To count occurrences use `map.merge(key, 1, Integer::sum)` or `getOrDefault`.
""",
    "complement": """### Worked example
Do two values in `[2, 7, 4, 8]` sum to 10? For 2 you need 8; store values as you go and check for the partner.

### In code (Java)
```java
int[] a = {2, 7, 4, 8}; int target = 10;
Set<Integer> seen = new HashSet<>();
for (int x : a) {
    if (seen.contains(target - x)) { System.out.println("found"); break; }
    seen.add(x);
}
```

### Watch out for
- Check for the complement **before** inserting the current value.
- Each lookup is O(1), so the whole scan is O(n).
""",
    "two_pointers": """### Worked example
Is `"racecar"` a palindrome? Compare characters from both ends moving inward; they all match.

### In code (Java)
```java
String s = "racecar";
int i = 0, j = s.length() - 1;
boolean ok = true;
while (i < j) {
    if (s.charAt(i++) != s.charAt(j--)) { ok = false; break; }
}
System.out.println(ok); // true
```

### Watch out for
- The loop ends when `i >= j`; a middle character (odd length) needs no check.
- On a sorted array, move the pointer that steps you toward the target.
""",
    "sliding_window": """### Worked example
Longest run of distinct characters in `"abcabc"` is 3. Grow the window right; when a repeat enters, push `left` past the previous copy.

### In code (Java)
```java
String s = "abcabc";
Map<Character,Integer> last = new HashMap<>();
int left = 0, best = 0;
for (int r = 0; r < s.length(); r++) {
    char ch = s.charAt(r);
    if (last.containsKey(ch) && last.get(ch) >= left) left = last.get(ch) + 1;
    last.put(ch, r);
    best = Math.max(best, r - left + 1);
}
System.out.println(best); // 3
```

### Watch out for
- Each index enters and leaves the window once, so it is O(n) despite the nested feel.
- Only ever move `left` forward, never backward.
""",
    "stack": """### Worked example
Are the brackets in `"([])"` balanced? Push openers; each closer must match the top of the stack.

### In code (Java)
```java
Deque<Character> st = new ArrayDeque<>();
Map<Character,Character> match = Map.of(')', '(', ']', '[', '}', '{');
boolean ok = true;
for (char c : "([])".toCharArray()) {
    if (c == '(' || c == '[' || c == '{') st.push(c);
    else if (st.isEmpty() || st.pop() != match.get(c)) { ok = false; break; }
}
ok = ok && st.isEmpty();
```

### Watch out for
- Always check `isEmpty()` before `pop()`.
- Use `ArrayDeque` as your stack, not the legacy `Stack` class.
""",
    "recursion": """### Worked example
Factorial: `fact(4) = 4 * fact(3) = ... = 24`. The base case `fact(0) = 1` stops the descent.

### In code (Java)
```java
static long fact(int n) {
    if (n <= 1) return 1;      // base case
    return n * fact(n - 1);    // smaller subproblem
}
```

### Watch out for
- Every recursion needs a base case, or it never stops (StackOverflowError).
- If the same subproblem recurs, cache results (memoization) to avoid exponential work.
""",
    "sorting": """### Worked example
Sorting `[3, 1, 2]` gives `[1, 2, 3]`, after which smallest/largest and neighbours are trivial to read.

### In code (Java)
```java
int[] a = {3, 1, 2};
Arrays.sort(a);                 // [1, 2, 3]

Integer[] b = {3, 1, 2};
Arrays.sort(b, Comparator.reverseOrder()); // [3, 2, 1]
```

### Watch out for
- Primitive `int[]` sort has no comparator; use `Integer[]` for custom order.
- Sorting is O(n log n) — often the step that unlocks an otherwise-hard problem.
""",
    "binary_search": """### Worked example
Find 7 in sorted `[1, 3, 5, 7, 9]`. Check the middle (5), go right, check 7 — found in O(log n).

### In code (Java)
```java
int[] a = {1,3,5,7,9}; int target = 7, lo = 0, hi = a.length - 1, ans = -1;
while (lo <= hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] == target) { ans = mid; break; }
    else if (a[mid] < target) lo = mid + 1;
    else hi = mid - 1;
}
```

### Watch out for
- Use `lo + (hi - lo) / 2` to avoid overflow on large indices.
- For the *first* match, keep searching left after a hit instead of stopping.
""",
    "dp": """### Worked example
Ways to climb n stairs taking 1 or 2 steps: `ways(n) = ways(n-1) + ways(n-2)`. Build up from the bottom.

### In code (Java)
```java
int n = 5;
long a = 1, b = 1;           // ways(0), ways(1)
for (int i = 2; i <= n; i++) { long c = a + b; a = b; b = c; }
System.out.println(b);       // 8
```

### Watch out for
- Identify the **state** and the **transition** first — the code follows.
- Bottom-up with a couple of variables often replaces an exponential recursion.
""",
    "recurrence": """### Worked example
Fibonacci is a recurrence: each term sums the previous two — 0, 1, 1, 2, 3, 5, 8, ...

### In code (Java)
```java
static long fib(int n) {
    long a = 0, b = 1;
    for (int i = 0; i < n; i++) { long c = a + b; a = b; b = c; }
    return a;
}
```

### Watch out for
- Nail the base cases (`fib(0)=0`, `fib(1)=1`) before the transition.
- Terms grow fast — use `long` to avoid overflow.
""",
    "dp2d": """### Worked example
Edit distance between `"ab"` and `"abc"` is 1 (insert `c`). A table `dp[i][j]` compares the first i and j characters.

### In code (Java)
```java
String a = "ab", b = "abc";
int[][] dp = new int[a.length()+1][b.length()+1];
for (int i = 0; i <= a.length(); i++) dp[i][0] = i;
for (int j = 0; j <= b.length(); j++) dp[0][j] = j;
for (int i = 1; i <= a.length(); i++)
  for (int j = 1; j <= b.length(); j++)
    dp[i][j] = a.charAt(i-1) == b.charAt(j-1)
             ? dp[i-1][j-1]
             : 1 + Math.min(dp[i-1][j-1], Math.min(dp[i-1][j], dp[i][j-1]));
```

### Watch out for
- Initialize the first row and column (matching against an empty prefix).
- Fill in an order where every cell you read is already computed.
""",
    "graph_repr": """### Worked example
Store edges 0-1 and 0-2 as an adjacency list: node 0 lists [1, 2]; nodes 1 and 2 list [0].

### In code (Java)
```java
int n = 3;
List<List<Integer>> adj = new ArrayList<>();
for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
adj.get(0).add(1); adj.get(1).add(0);   // undirected edge 0-1
adj.get(0).add(2); adj.get(2).add(0);
```

### Watch out for
- For undirected graphs, add the edge in **both** directions.
- Adjacency lists use O(V+E) memory and iterate neighbours quickly.
""",
    "bfs": """### Worked example
From node 0 in the chain 0-1-2, BFS visits 0, then 1, then 2 — in order of distance.

### In code (Java)
```java
Queue<Integer> q = new ArrayDeque<>();
boolean[] seen = new boolean[n];
q.offer(0); seen[0] = true;
while (!q.isEmpty()) {
    int u = q.poll();
    for (int v : adj.get(u)) if (!seen[v]) { seen[v] = true; q.offer(v); }
}
```

### Watch out for
- Mark `seen` when you **enqueue**, not when you dequeue, or nodes get added twice.
- BFS gives shortest paths only in *unweighted* graphs.
""",
    "flood_fill": """### Worked example
Count islands in a grid: each time you find unvisited land, flood its whole region and add one to the count.

### In code (Java)
```java
static int[][] DIR = {{1,0},{-1,0},{0,1},{0,-1}};
// from (r, c): mark visited, then visit each in-bounds land neighbour
for (int[] d : DIR) {
    int nr = r + d[0], nc = c + d[1];
    // if in bounds and grid[nr][nc] == '1' and not visited -> recurse/enqueue
}
```

### Watch out for
- Guard the array bounds before touching a neighbour.
- Mark cells visited (or overwrite them) so the flood cannot loop forever.
""",
    "topo": """### Worked example
Tasks with `A before B` and `B before C` order as A, B, C. A cycle (`A before B`, `B before A`) has no valid order.

### In code (Java)
```java
// Kahn's algorithm: start from indegree-0 nodes, remove them,
// decrement each neighbour, and add newly-zeroed nodes. If you
// emit fewer than n nodes, there is a cycle.
```

### Watch out for
- Emitting fewer than n nodes means the graph has a cycle.
- Edge direction matters: `b before a` is an edge b -> a.
""",
    "indegree": """### Worked example
Course 1 needs course 0: `indegree[1] = 1`, `indegree[0] = 0`. Take 0, drop `indegree[1]` to 0, then take 1.

### In code (Java)
```java
int[] indeg = new int[n];
for (int[] e : edges) indeg[e[0]]++;   // edge b->a increments a
Deque<Integer> q = new ArrayDeque<>();
for (int i = 0; i < n; i++) if (indeg[i] == 0) q.offer(i);
```

### Watch out for
- Indegree counts remaining prerequisites; seed the queue with the zeros.
- Count how many you pop — it must equal n for a valid ordering.
""",
    "heap": """### Worked example
Always take the smallest pending item: a min-heap of `{5, 1, 3}` pops 1, then 3, then 5.

### In code (Java)
```java
PriorityQueue<Integer> pq = new PriorityQueue<>();
pq.offer(5); pq.offer(1); pq.offer(3);
while (!pq.isEmpty()) System.out.print(pq.poll() + " "); // 1 3 5
```

### Watch out for
- `PriorityQueue` is a **min**-heap; for max use `Comparator.reverseOrder()`.
- Peeking is O(1), but there is no fast search or arbitrary removal.
""",
    "greedy": """### Worked example
Fewest coins for 30 with {25, 10, 5}: take the biggest that fits each time — 25, then 5 — two coins.

### In code (Java)
```java
int[] coins = {25, 10, 5}; int amount = 30, used = 0;
for (int c : coins) { used += amount / c; amount %= c; }
```

### Watch out for
- Greedy is only correct for some problems (this coin set works; arbitrary sets need DP).
- Sorting the input first is a common setup step.
""",
    "prefix_max": """### Worked example
For heights `[2, 0, 2]`, water over the middle bar is `min(leftMax, rightMax) - height = min(2, 2) - 0 = 2`.

### In code (Java)
```java
int[] h = {2, 0, 2};
int[] left = new int[h.length], right = new int[h.length];
left[0] = h[0];
for (int i = 1; i < h.length; i++) left[i] = Math.max(left[i-1], h[i]);
right[h.length-1] = h[h.length-1];
for (int i = h.length-2; i >= 0; i--) right[i] = Math.max(right[i+1], h[i]);
```

### Watch out for
- Prefix arrays turn repeated range questions into O(1) lookups.
- A two-pointer variant computes the same maxima using O(1) extra space.
""",
    "canonical": """### Worked example
`"eat"` and `"tea"` are anagrams because both share the canonical key `"aet"` (sorted letters).

### In code (Java)
```java
char[] c = "tea".toCharArray();
Arrays.sort(c);
String key = new String(c); // "aet"
```

### Watch out for
- A 26-length count signature is an O(n) alternative to O(n log n) sorting.
- The key must be identical for equivalent items and different otherwise.
""",
    "math_digits": """### Worked example
Sum the digits of 123: `123 % 10 = 3`, then `123 / 10 = 12`, and so on — 3 + 2 + 1 = 6.

### In code (Java)
```java
int n = 123, sum = 0;
while (n > 0) { sum += n % 10; n /= 10; }
System.out.println(sum); // 6
```

### Watch out for
- Handle 0 and negatives explicitly (take `Math.abs` first if sign should not matter).
- Reversing a number arithmetically can overflow — consider the String form.
""",
    "number_theory": """### Worked example
gcd(12, 18): 18 % 12 = 6, then 12 % 6 = 0, so the gcd is 6.

### In code (Java)
```java
static long gcd(long a, long b) { return b == 0 ? a : gcd(b, a % b); }
```

### Watch out for
- `Math.floorMod` gives a non-negative remainder for negative inputs.
- lcm(a, b) = a / gcd(a, b) * b — divide before multiplying to avoid overflow.
""",
    "modulo": """### Worked example
Rotating a length-5 array by k = 7 equals rotating by `7 % 5 = 2` — the extra full turns do nothing.

### In code (Java)
```java
int n = 5, k = 7;
k = k % n;                        // 2
int idx = Math.floorMod(-1, n);   // 4, safe for negatives
```

### Watch out for
- Java's `%` can be negative; `Math.floorMod` keeps the result in [0, n).
- Reduce `k % n` before using it to index, and guard `n > 0`.
""",
    "inplace_reverse": """### Worked example
Reverse `[1, 2, 3, 4]` by swapping ends inward: (1,4) then (2,3) gives `[4, 3, 2, 1]`.

### In code (Java)
```java
static void reverse(int[] a, int i, int j) {
    while (i < j) { int t = a[i]; a[i++] = a[j]; a[j--] = t; }
}
```

### Watch out for
- Rotate right by k = reverse all, reverse the first k, reverse the rest.
- Uses O(1) extra space — no second array required.
""",
    "big_o": """### Worked example
With n up to 100,000, an O(n^2) approach is ~10^10 operations (too slow), but O(n log n) is ~1.7 million — easily fast enough.

### Rules of thumb
```text
n <= 20        -> even O(2^n) may pass
n <= 5,000     -> O(n^2) is fine
n <= 100,000   -> aim for O(n) or O(n log n)
n <= 1e9       -> O(log n) or O(1)
```

### Watch out for
- Read the constraints first; they hint at the intended complexity.
- Budget roughly 10^8 simple operations per second as a guide.
""",
    "overflow": """### Worked example
`100000 * 100000` overflows an `int` (max ~2.1e9) into a garbage negative number; as a `long` it is correctly 10^10.

### In code (Java)
```java
int a = 100000;
long bad = a * a;          // overflow happens BEFORE the assignment
long good = (long) a * a;  // cast first -> 10_000_000_000
```

### Watch out for
- Cast to `long` **before** the multiplication, not after.
- Accumulate sums of many or large values into a `long`.
""",
    "visited_set": """### Worked example
Walking a graph with a cycle loops forever unless you remember visited nodes; marking them makes each node processed once.

### In code (Java)
```java
boolean[] seen = new boolean[n];        // graph
boolean[][] seen2 = new boolean[rows][cols]; // grid
```

### Watch out for
- Mark visited as early as possible (on enqueue) to avoid duplicates.
- For grids you can overwrite the cell (set '1' to '0') instead of a separate array.
""",
    "queue": """### Worked example
A queue serves in arrival order: offer 1, 2, 3 and `poll` returns 1, then 2, then 3.

### In code (Java)
```java
Queue<Integer> q = new ArrayDeque<>();
q.offer(1); q.offer(2);
int first = q.poll(); // 1
```

### Watch out for
- Use `ArrayDeque`, not `LinkedList` (slower) or the legacy `Stack`.
- `poll()` returns null on an empty queue — check `isEmpty()` in loops.
""",
}


def build_concepts():
    cats = []
    for key, c in CONCEPTS.items():
        cats.append({
            "key": key,
            "name": c["name"],
            "category": CATEGORY.get(key, "General"),
            "what": c["what"],
            "deep": c["deep"],
            "java": c["java"],
            "lesson": LESSONS.get(key, ""),
        })
    return cats


# ---------------------------------------------------------------------------
# Patterns (first-class) — derived from topics/subtopics.
# ---------------------------------------------------------------------------

PATTERN_FROM = {
    "Two Pointers": "Two Pointers",
    "Sliding Window": "Sliding Window",
    "Complement Lookup": "Hashing",
    "Hashing": "Hashing",
    "Lower Bound": "Binary Search",
    "Binary Search": "Binary Search",
    "Kadane": "Dynamic Programming",
    "2D DP": "Dynamic Programming",
    "Recurrence": "Dynamic Programming",
    "Patience Sorting": "Dynamic Programming",
    "Dynamic Programming": "Dynamic Programming",
    "BFS": "BFS / DFS",
    "Flood Fill": "BFS / DFS",
    "Topological Sort": "Topological Sort",
    "Cycle Detection": "Topological Sort",
    "Dijkstra": "Dijkstra",
    "Priority Queue": "Heap / Priority Queue",
    "Stack": "Stack",
    "Prefix Max": "Prefix Sums",
    "Canonical Form": "Hashing",
    "Counting": "Counting",
    "Prefix Sum": "Prefix Sums",
    "Bit Manipulation": "Bit Manipulation",
    "XOR": "Bit Manipulation",
    "Greedy": "Greedy",
    "Monotonic Stack": "Stack",
    "Sorting": "Sorting",
    "Sieve": "Math",
    "Expand Around Center": "Two Pointers",
    "Boyer-Moore": "Hashing",
    "Hash Set": "Hashing",
    "1D DP": "Dynamic Programming",
    "Subset Sum": "Dynamic Programming",
}


def derive_patterns(d):
    pats = []
    for tag in list(d.get("topics", [])) + list(d.get("subtopics", [])):
        p = PATTERN_FROM.get(tag)
        if p and p not in pats:
            pats.append(p)
    return pats


# Extra authored editorials (multiple approaches) and follow-up variants, by slug.
EDITORIALS_EXTRA = {
    "two-sum-indices": [
        {"title": "Brute force", "body": "Check every pair (i, j) and return the first whose values sum to the target.", "time": "O(n^2)", "space": "O(1)"},
        {"title": "Hash map (optimal)", "body": "Scan once, storing each value's index. For each element, look up `target - x`; if seen, you have the answer.", "time": "O(n)", "space": "O(n)"},
    ],
    "maximum-subarray": [
        {"title": "Brute force", "body": "Try every subarray and track the maximum sum.", "time": "O(n^2)", "space": "O(1)"},
        {"title": "Kadane (optimal)", "body": "Carry the best sum ending at each index: `cur = max(x, cur + x)`; track the running maximum.", "time": "O(n)", "space": "O(1)"},
    ],
    "longest-unique-substring": [
        {"title": "Sliding window", "body": "Expand the right edge; when a repeat appears, jump the left edge past the previous occurrence.", "time": "O(n)", "space": "O(min(n, alphabet))"},
    ],
}

FOLLOWUPS = {
    "two-sum-indices": [{"slug": "two-sum-exists", "title": "Two Sum (exists?)", "note": "Same idea, boolean answer."}],
    "maximum-subarray": [{"slug": "climbing-stairs", "title": "Climbing Stairs", "note": "Another 1-D DP recurrence."}],
    "binary-search-first": [{"slug": "longest-increasing-subsequence", "title": "Longest Increasing Subsequence", "note": "Binary search on the answer (patience sorting)."}],
}


# ---------------------------------------------------------------------------
# Function-harness demo problems.
#
# The user writes only the function; the app wraps it with generated I/O glue.
# Each defines a native Python implementation used to compute expected outputs
# in the same serialized form the harness prints (arrays = space-separated).
# ---------------------------------------------------------------------------

def _ser(val, ty):
    if ty == "bool":
        return "true" if val else "false"
    if ty.endswith("[]"):
        return " ".join(str(x) for x in val)
    return str(val)


# Auto-generate starter stubs from a function signature, so harness problems get
# correct, compiling Python AND Java starters without hand-authoring each.
_JAVA_TY = {
    "int": "int", "long": "long", "double": "double", "bool": "boolean",
    "string": "String", "int[]": "int[]", "long[]": "long[]",
    "double[]": "double[]", "string[]": "String[]",
}


def _py_default(ty):
    if ty.endswith("[]"):
        return "[]"
    return {"int": "0", "long": "0", "double": "0.0", "bool": "False", "string": '""'}.get(ty, "None")


def _java_default(ty):
    if ty.endswith("[]"):
        base = _JAVA_TY[ty][:-2]
        return f"new {base}[]{{}}"
    return {"int": "0", "long": "0L", "double": "0.0", "bool": "false", "string": '""'}.get(ty, "null")


def stub_py(spec):
    params = ", ".join(p["name"] for p in spec["params"])
    return f"def {spec['name']}({params}):\n    # TODO: implement\n    return {_py_default(spec['returns'])}\n"


def stub_java(spec):
    params = ", ".join(f"{_JAVA_TY[p['type']]} {p['name']}" for p in spec["params"])
    return (
        f"class Solution {{\n    {_JAVA_TY[spec['returns']]} {spec['name']}({params}) {{\n"
        f"        // TODO: implement\n        return {_java_default(spec['returns'])};\n    }}\n}}\n"
    )


def _ser_arg(val, ty):
    if ty == "bool":
        return "true" if val else "false"
    if ty.endswith("[]"):
        return " ".join(str(x) for x in val)
    return str(val)


HARNESS_DEFS = [
    dict(
        slug="two-sum-fn", title="Two Sum (function)", difficulty="Easy",
        topics=["Hashing", "Arrays"], subtopics=["Complement Lookup"], companies=["Amazon", "Google"],
        description=(
            "Return the **1-based indices** of the two numbers that add up to `target`.\n\n"
            "You implement a function — the app handles input parsing and output. "
            "This is the function-signature style you'll see in real interviews."
        ),
        constraints="2 ≤ n ≤ 10^4\nExactly one valid answer exists.",
        hints=[
            "A hash map turns the 'find the complement' step into O(1).",
            "For each x, check whether target - x was already seen.",
            "Store value → index as you scan.",
            "Return the stored index and the current index (1-based).",
        ],
        opt=("O(n)", "O(n)", "A single pass with a hash map of seen values."),
        editorial="## Approach\nScan once, remembering each value's index. For each element look up `target - x`.",
        spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}], "returns": "int[]"},
        fn=lambda nums, target: _two_sum_fn(nums, target),
        starter_py="def solve(nums, target):\n    # nums: list[int], target: int -> return [i, j] (1-based indices)\n    return []\n",
        starter_java="class Solution {\n    int[] solve(int[] nums, int target) {\n        // return the two 1-based indices\n        return new int[]{};\n    }\n}\n",
        cases=[
            ("example", "Example 1", ([2, 7, 11, 15], 9)),
            ("example", "Example 2", ([3, 2, 4], 6)),
            ("hidden", "First and last", ([1, 5, 3, 7], 8)),
            ("hidden", "Adjacent", ([10, 20, 30], 50)),
            ("hidden", "Negatives", ([-3, 4, 1, 90], -2)),
        ],
        example_expl=["nums[1]+nums[2] = 2+7 = 9.", "nums[2]+nums[3] = 2+4 = 6."],
    ),
    dict(
        slug="max-subarray-fn", title="Maximum Subarray (function)", difficulty="Medium",
        topics=["Dynamic Programming", "Arrays"], subtopics=["Kadane"], companies=["Bloomberg", "Amazon"],
        description=(
            "Return the largest sum obtainable from a **contiguous** non-empty subarray.\n\n"
            "Implement the function; the app supplies the array and reads your return value."
        ),
        constraints="1 ≤ n ≤ 10^5\n-10^4 ≤ a[i] ≤ 10^4",
        hints=[
            "Track the best sum ending exactly at the current index.",
            "Either extend the previous run or start fresh at x.",
            "cur = max(x, cur + x).",
            "Keep a separate running maximum.",
        ],
        opt=("O(n)", "O(1)", "Kadane's algorithm in a single pass."),
        editorial="## Approach\nKadane's: `cur = max(x, cur + x)`, track the max.",
        spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
        fn=lambda nums: _kadane_fn(nums),
        starter_py="def solve(nums):\n    # nums: list[int] -> return the maximum contiguous subarray sum\n    return 0\n",
        starter_java="class Solution {\n    int solve(int[] nums) {\n        // return the maximum contiguous subarray sum\n        return 0;\n    }\n}\n",
        cases=[
            ("example", "Example 1", ([-2, 1, -3, 4, -1, 2, 1, -5, 4],)),
            ("example", "Example 2", ([1],)),
            ("hidden", "All negative", ([-5, -2, -8],)),
            ("hidden", "All positive", ([1, 2, 3, 4],)),
            ("hidden", "Single dip", ([5, -1, 5],)),
        ],
        example_expl=["The subarray [4,-1,2,1] sums to 6.", "A single element is its own best subarray."],
    ),
    dict(
        slug="reverse-array-fn", title="Reverse Array (function)", difficulty="Easy",
        topics=["Arrays"], subtopics=["Two Pointers"], companies=["Microsoft"],
        description="Return the input array reversed. Implement the function; the app handles I/O.",
        constraints="0 ≤ n ≤ 10^5",
        hints=["Swap ends moving inward.", "Or build the output back-to-front.", "Two pointers work in place.", "Return the reversed list."],
        opt=("O(n)", "O(n)", "Each element is moved once."),
        editorial="## Approach\nReverse with two pointers or a slice.",
        spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int[]"},
        fn=lambda nums: list(reversed(nums)),
        starter_py="def solve(nums):\n    # nums: list[int] -> return nums reversed\n    return nums\n",
        starter_java="class Solution {\n    int[] solve(int[] nums) {\n        // return nums reversed\n        return nums;\n    }\n}\n",
        cases=[
            ("example", "Example 1", ([1, 2, 3, 4],)),
            ("example", "Example 2", ([5],)),
            ("hidden", "Empty", ([],)),
            ("hidden", "Two", ([9, 8],)),
            ("hidden", "Longer", ([1, 1, 2, 3, 5, 8],)),
        ],
        example_expl=["[1,2,3,4] → [4,3,2,1].", "A single element is unchanged."],
    ),
    dict(
        slug="is-palindrome-fn", title="Is Palindrome (function)", difficulty="Easy",
        topics=["Strings"], subtopics=["Two Pointers"], companies=["Adobe"],
        description="Return `true` if the string reads the same forwards and backwards. Implement the function.",
        constraints="1 ≤ |s| ≤ 10^5\nLowercase letters only.",
        hints=["Compare characters from both ends.", "Advance inward while they match.", "Any mismatch means false.", "s == s reversed also works."],
        opt=("O(n)", "O(1)", "One pass with two pointers."),
        editorial="## Approach\nTwo pointers from each end; mismatch ⇒ not a palindrome.",
        spec={"name": "solve", "params": [{"name": "s", "type": "string"}], "returns": "bool"},
        fn=lambda s: s == s[::-1],
        starter_py="def solve(s):\n    # s: str -> return True if s is a palindrome else False\n    return False\n",
        starter_java="class Solution {\n    boolean solve(String s) {\n        // return true if s is a palindrome\n        return false;\n    }\n}\n",
        cases=[
            ("example", "Example 1", ("racecar",)),
            ("example", "Example 2", ("hello",)),
            ("hidden", "Single", ("a",)),
            ("hidden", "Even palindrome", ("abba",)),
            ("hidden", "Almost", ("abca",)),
        ],
        example_expl=["'racecar' is a palindrome.", "'hello' is not."],
    ),
]


def _two_sum_fn(nums, target):
    pos = {}
    for i, x in enumerate(nums):
        if target - x in pos:
            return [pos[target - x] + 1, i + 1]
        pos[x] = i
    return [-1]


def _kadane_fn(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best


# ---------------------------------------------------------------------------
# Reference implementations for the expanded library (compute expected outputs).
# ---------------------------------------------------------------------------

def _is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def _count_primes(n):  # count primes strictly less than n
    if n < 3:
        return 0
    sieve = [True] * n
    sieve[0] = sieve[1] = False
    i = 2
    while i * i < n:
        if sieve[i]:
            for j in range(i * i, n, i):
                sieve[j] = False
        i += 1
    return sum(sieve)


def _house_rob(nums):
    a = b = 0
    for x in nums:
        a, b = b, max(b, a + x)
    return b


def _coin_change(coins, amount):
    dp = [0] + [math.inf] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != math.inf else -1


def _coin_change_ways(coins, amount):
    dp = [1] + [0] * amount
    for c in coins:
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return dp[amount]


def _best_buy_sell(prices):
    lo = math.inf
    best = 0
    for p in prices:
        lo = min(lo, p)
        best = max(best, p - lo)
    return best


def _container(h):
    l, r = 0, len(h) - 1
    best = 0
    while l < r:
        best = max(best, min(h[l], h[r]) * (r - l))
        if h[l] < h[r]:
            l += 1
        else:
            r -= 1
    return best


def _product_except_self(nums):
    n = len(nums)
    res = [1] * n
    pre = 1
    for i in range(n):
        res[i] = pre
        pre *= nums[i]
    suf = 1
    for i in range(n - 1, -1, -1):
        res[i] *= suf
        suf *= nums[i]
    return res


def _jump_game(nums):
    reach = 0
    for i, x in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + x)
    return True


def _search_insert(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def _isqrt(x):
    if x < 2:
        return x
    lo, hi = 1, x
    while lo <= hi:
        mid = (lo + hi) // 2
        if mid * mid <= x:
            lo = mid + 1
        else:
            hi = mid - 1
    return hi


def _min_cost_stairs(cost):
    a = b = 0
    for i in range(2, len(cost) + 1):
        a, b = b, min(b + cost[i - 1], a + cost[i - 2])
    return b


def _daily_temps(t):
    res = [0] * len(t)
    st = []
    for i, x in enumerate(t):
        while st and t[st[-1]] < x:
            j = st.pop()
            res[j] = i - j
        st.append(i)
    return res


def _next_greater(nums):
    res = [-1] * len(nums)
    st = []
    for i, x in enumerate(nums):
        while st and nums[st[-1]] < x:
            res[st.pop()] = x
        st.append(i)
    return res


def _subarray_sum_k(nums, k):
    cnt = defaultdict(int)
    cnt[0] = 1
    s = 0
    res = 0
    for x in nums:
        s += x
        res += cnt[s - k]
        cnt[s] += 1
    return res


def _longest_consecutive(nums):
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
    return best


def _word_break(s, words):
    w = set(words)
    n = len(s)
    dp = [True] + [False] * n
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in w:
                dp[i] = True
                break
    return dp[n]


def _decode_ways(s):
    if not s or s[0] == "0":
        return 0
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1
    for i in range(2, n + 1):
        if s[i - 1] != "0":
            dp[i] += dp[i - 1]
        two = int(s[i - 2:i])
        if 10 <= two <= 26:
            dp[i] += dp[i - 2]
    return dp[n]


def _longest_palindrome_len(s):
    if not s:
        return 0

    def expand(l, r):
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1
            r += 1
        return r - l - 1

    best = 0
    for i in range(len(s)):
        best = max(best, expand(i, i), expand(i, i + 1))
    return best


def _max_product_subarray(nums):
    best = cur_max = cur_min = nums[0]
    for x in nums[1:]:
        cands = (x, cur_max * x, cur_min * x)
        cur_max = max(cands)
        cur_min = min(cands)
        best = max(best, cur_max)
    return best


def _partition_equal(nums):
    total = sum(nums)
    if total % 2:
        return False
    t = total // 2
    dp = [True] + [False] * t
    for x in nums:
        for a in range(t, x - 1, -1):
            if dp[a - x]:
                dp[a] = True
    return dp[t]


def _majority(nums):
    count = 0
    cand = None
    for x in nums:
        if count == 0:
            cand = x
        count += 1 if x == cand else -1
    return cand


def _single_number(nums):
    r = 0
    for x in nums:
        r ^= x
    return r


def _first_uniq(s):
    c = Counter(s)
    for i, ch in enumerate(s):
        if c[ch] == 1:
            return i
    return -1


def _move_zeroes(nums):
    res = [x for x in nums if x != 0]
    res += [0] * (len(nums) - len(res))
    return res


def _running_sum(nums):
    out2 = []
    s = 0
    for x in nums:
        s += x
        out2.append(s)
    return out2


def _max_consec_ones(nums):
    best = cur = 0
    for x in nums:
        cur = cur + 1 if x == 1 else 0
        best = max(best, cur)
    return best


def _reverse_int(n):
    sign = -1 if n < 0 else 1
    return sign * int(str(abs(n))[::-1])


def _second_largest(nums):
    u = sorted(set(nums))
    return u[-2] if len(u) >= 2 else u[-1]


def _lcp(strs):
    if not strs:
        return ""
    p = strs[0]
    for s in strs[1:]:
        while not s.startswith(p):
            p = p[:-1]
            if not p:
                return ""
    return p


def _factorial(n):
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r


def _sum_digits(n):
    return sum(int(c) for c in str(abs(n)))


def _rotate_right(nums, k):
    n = len(nums)
    if n == 0:
        return nums
    k %= n
    return nums[n - k:] + nums[:n - k]


# ---------------------------------------------------------------------------
# Expanded problem library — basics → DSA, across all four difficulty tiers.
# Authored as function-harness problems: users implement a function (Python or
# Java), the app supplies inputs and reads the return. Expected outputs are
# computed from the reference `fn`.
# ---------------------------------------------------------------------------

HARNESS_DEFS += [
    # ---------------- INTRO ----------------
    dict(slug="is-even", title="Is Even", difficulty="Intro", topics=["Basics"], subtopics=["Conditionals"], companies=["Amazon"],
         description="Return `true` if the integer is even, otherwise `false`.",
         hints=["A number is even when it leaves no remainder mod 2.", "Use the modulo operator `%`.", "`n % 2 == 0`."],
         opt=("O(1)", "O(1)", "A single modulo check."),
         editorial="An integer is even iff `n % 2 == 0`.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "bool"},
         fn=lambda n: n % 2 == 0,
         cases=[("example", "Even", (4,)), ("example", "Odd", (7,)), ("hidden", "Zero", (0,)), ("hidden", "Negative even", (-8,)), ("hidden", "Negative odd", (-3,))],
         example_expl=["4 is even.", "7 is odd."]),
    dict(slug="absolute-value", title="Absolute Value", difficulty="Intro", topics=["Basics", "Math"], subtopics=["Arithmetic"], companies=["Microsoft"],
         description="Return the absolute value of the integer (its distance from zero).",
         hints=["Negatives flip sign; non-negatives stay.", "If n < 0 return -n."],
         opt=("O(1)", "O(1)", "One comparison."),
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "int"},
         fn=lambda n: abs(n),
         cases=[("example", "Negative", (-5,)), ("example", "Positive", (9,)), ("hidden", "Zero", (0,)), ("hidden", "Large", (-100000,))],
         example_expl=["|-5| = 5.", "|9| = 9."]),
    dict(slug="max-of-three", title="Max of Three", difficulty="Intro", topics=["Basics"], subtopics=["Conditionals"], companies=["Adobe"],
         description="Return the largest of three integers.",
         hints=["Compare pairwise.", "max(a, max(b, c))."],
         opt=("O(1)", "O(1)", "Constant comparisons."),
         spec={"name": "solve", "params": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}, {"name": "c", "type": "int"}], "returns": "int"},
         fn=lambda a, b, c: max(a, b, c),
         cases=[("example", "Example", (3, 9, 5)), ("example", "Negatives", (-1, -7, -3)), ("hidden", "Ties", (4, 4, 2)), ("hidden", "First largest", (10, 1, 2))],
         example_expl=["9 is the largest.", "-1 is the largest."]),
    dict(slug="square-number", title="Square", difficulty="Intro", topics=["Basics", "Math"], subtopics=["Arithmetic"], companies=["Amazon"],
         description="Return the square of the integer.",
         hints=["Multiply the number by itself."],
         opt=("O(1)", "O(1)", "One multiplication."),
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "long"},
         fn=lambda n: n * n,
         cases=[("example", "Example", (5,)), ("example", "Negative", (-4,)), ("hidden", "Zero", (0,)), ("hidden", "Large", (100000,))],
         example_expl=["5² = 25.", "(-4)² = 16."]),
    dict(slug="sum-of-digits", title="Sum of Digits", difficulty="Intro", topics=["Math"], subtopics=["Digits"], companies=["Bloomberg"],
         description="Return the sum of the decimal digits of a non-negative integer.",
         hints=["Peel digits with % 10 and // 10.", "Or iterate the string form."],
         opt=("O(log n)", "O(1)", "One pass over the digits."),
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "int"},
         fn=lambda n: _sum_digits(n),
         cases=[("example", "Example", (1234,)), ("example", "Single", (7,)), ("hidden", "Zero", (0,)), ("hidden", "Repeated", (99999,))],
         example_expl=["1+2+3+4 = 10.", "Single digit sums to itself."]),
    dict(slug="factorial", title="Factorial", difficulty="Intro", topics=["Math"], subtopics=["Loops"], companies=["Google"],
         description="Return n! = 1·2·…·n (with 0! = 1).",
         hints=["Multiply a running product from 1 to n.", "Use a 64-bit type — factorials grow fast."],
         opt=("O(n)", "O(1)", "A single multiply loop."),
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "long"},
         fn=lambda n: _factorial(n),
         cases=[("example", "5!", (5,)), ("example", "0!", (0,)), ("hidden", "1!", (1,)), ("hidden", "10!", (10,))],
         example_expl=["5! = 120.", "0! = 1 by definition."]),
    dict(slug="count-evens", title="Count Evens", difficulty="Intro", topics=["Arrays"], subtopics=["Counting"], companies=["Amazon"],
         description="Return how many elements of the array are even.",
         hints=["Scan once, test each element mod 2.", "Increment a counter."],
         opt=("O(n)", "O(1)", "Single pass."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: sum(1 for x in nums if x % 2 == 0),
         cases=[("example", "Mixed", ([1, 2, 3, 4],)), ("example", "None", ([1, 3, 5],)), ("hidden", "All even", ([2, 4, 6, 8],)), ("hidden", "Empty", ([],)), ("hidden", "Negatives", ([-2, -1, 0],))],
         example_expl=["2 and 4 are even.", "No evens."]),
    dict(slug="array-minimum", title="Array Minimum", difficulty="Intro", topics=["Arrays"], subtopics=["Traversal"], companies=["Microsoft"],
         description="Return the smallest element of a non-empty array.",
         hints=["Track a running minimum as you scan."],
         opt=("O(n)", "O(1)", "Single pass tracking the min."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: min(nums),
         cases=[("example", "Example", ([3, 1, 4, 1, 5],)), ("example", "Negatives", ([-2, -9, -1],)), ("hidden", "Single", ([42],)), ("hidden", "Sorted", ([1, 2, 3],))],
         example_expl=["1 is smallest.", "-9 is smallest."]),

    # ---------------- EASY ----------------
    dict(slug="contains-duplicate", title="Contains Duplicate", difficulty="Easy", topics=["Arrays", "Hashing"], subtopics=["Hash Set"], companies=["Amazon", "Google"],
         description="Return `true` if any value appears at least twice.",
         hints=["A set remembers what you've seen.", "If insertion finds a value already present, return true.", "Compare set size to array length."],
         opt=("O(n)", "O(n)", "One pass with a hash set."),
         editorial="Insert into a set; a collision means a duplicate. Equivalent to `len(set) != len(arr)`.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "bool"},
         fn=lambda nums: len(set(nums)) != len(nums),
         cases=[("example", "Has dup", ([1, 2, 3, 1],)), ("example", "Unique", ([1, 2, 3, 4],)), ("hidden", "Empty", ([],)), ("hidden", "All same", ([5, 5, 5],))],
         example_expl=["1 repeats.", "All distinct."]),
    dict(slug="single-number", title="Single Number", difficulty="Easy", topics=["Bit Manipulation", "Arrays"], subtopics=["XOR"], companies=["Amazon", "Uber"],
         description="Every element appears twice except one. Return the element that appears once.",
         hints=["XOR of a value with itself is 0.", "XOR is commutative — pairs cancel.", "Fold the whole array with XOR."],
         opt=("O(n)", "O(1)", "XOR cancels pairs, leaving the unique value."),
         editorial="XOR all elements; duplicates cancel to 0 and the loner remains.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: _single_number(nums),
         cases=[("example", "Example", ([2, 3, 2],)), ("example", "Longer", ([4, 1, 2, 1, 2],)), ("hidden", "Single", ([7],)), ("hidden", "Zeros", ([0, 5, 0],))],
         example_expl=["3 is unique.", "4 is unique."]),
    dict(slug="majority-element", title="Majority Element", difficulty="Easy", topics=["Arrays", "Hashing"], subtopics=["Boyer-Moore"], companies=["Amazon", "Adobe"],
         description="An element appears more than ⌊n/2⌋ times. Return it.",
         hints=["A count that cancels non-matches survives for the majority.", "Boyer-Moore voting keeps one candidate.", "O(1) space is possible."],
         opt=("O(n)", "O(1)", "Boyer-Moore majority vote."),
         editorial="Boyer-Moore: keep a candidate and a count; reset the candidate when count hits 0.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: _majority(nums),
         cases=[("example", "Example", ([3, 2, 3],)), ("example", "Longer", ([2, 2, 1, 1, 2, 2, 2],)), ("hidden", "Single", ([9],)), ("hidden", "All same", ([4, 4, 4, 4],))],
         example_expl=["3 is the majority.", "2 appears 5/7 times."]),
    dict(slug="is-prime", title="Is Prime", difficulty="Easy", topics=["Math"], subtopics=["Number Theory"], companies=["Bloomberg"],
         description="Return `true` if the integer is prime.",
         hints=["Primes have no divisor between 2 and √n.", "Only trial-divide up to √n.", "Handle n < 2 as not prime."],
         opt=("O(√n)", "O(1)", "Trial division up to the square root."),
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "bool"},
         fn=lambda n: _is_prime(n),
         cases=[("example", "Prime", (13,)), ("example", "Composite", (12,)), ("hidden", "One", (1,)), ("hidden", "Two", (2,)), ("hidden", "Large prime", (7919,))],
         example_expl=["13 is prime.", "12 = 3·4."]),
    dict(slug="count-primes", title="Count Primes", difficulty="Easy", topics=["Math"], subtopics=["Sieve"], companies=["Google"],
         description="Return the number of primes strictly less than n.",
         hints=["Trial-dividing each number is slow.", "Mark multiples with a Sieve of Eratosthenes.", "Start crossing out at i·i."],
         opt=("O(n log log n)", "O(n)", "Sieve of Eratosthenes."),
         editorial="Sieve: mark composites by crossing out multiples of each prime starting at i².",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "int"},
         fn=lambda n: _count_primes(n),
         cases=[("example", "Below 10", (10,)), ("example", "Below 2", (2,)), ("hidden", "Below 0", (0,)), ("hidden", "Below 100", (100,))],
         example_expl=["2,3,5,7 → 4.", "No primes below 2."]),
    dict(slug="valid-anagram", title="Valid Anagram", difficulty="Easy", topics=["Strings", "Hashing"], subtopics=["Counting"], companies=["Amazon", "Meta"],
         description="Return `true` if `t` is an anagram of `s` (same letters, same counts).",
         hints=["Anagrams have identical character counts.", "Compare frequency maps, or compare sorted strings."],
         opt=("O(n)", "O(1)", "Compare 26-letter frequency counts."),
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}, {"name": "t", "type": "string"}], "returns": "bool"},
         fn=lambda s, t: sorted(s) == sorted(t),
         cases=[("example", "Anagram", ("listen", "silent")), ("example", "Not", ("rat", "car")), ("hidden", "Diff length", ("a", "ab")), ("hidden", "Same", ("abc", "abc"))],
         example_expl=["Same letters rearranged.", "Different letters."]),
    dict(slug="first-unique-char", title="First Unique Character", difficulty="Easy", topics=["Strings", "Hashing"], subtopics=["Counting"], companies=["Amazon", "Bloomberg"],
         description="Return the index of the first non-repeating character, or -1 if none.",
         hints=["Count characters first.", "Then scan left to right for the first count of 1."],
         opt=("O(n)", "O(1)", "Two passes: count, then find."),
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}], "returns": "int"},
         fn=lambda s: _first_uniq(s),
         cases=[("example", "Example", ("leetcode",)), ("example", "Repeats", ("aabb",)), ("hidden", "Single", ("z",)), ("hidden", "Last unique", ("aabbc",))],
         example_expl=["'l' at index 0 is unique.", "No unique char → -1."]),
    dict(slug="move-zeroes", title="Move Zeroes", difficulty="Easy", topics=["Arrays", "Two Pointers"], subtopics=["Two Pointers"], companies=["Meta", "Amazon"],
         description="Move all zeroes to the end while keeping the order of non-zero elements. Return the resulting array.",
         hints=["Keep a write pointer for the next non-zero slot.", "Fill the rest with zeroes.", "Relative order of non-zeros must hold."],
         opt=("O(n)", "O(1)", "Stable partition around zero."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int[]"},
         fn=lambda nums: _move_zeroes(nums),
         cases=[("example", "Example", ([0, 1, 0, 3, 12],)), ("example", "No zeroes", ([1, 2, 3],)), ("hidden", "All zeroes", ([0, 0, 0],)), ("hidden", "Leading nonzero", ([4, 0, 5, 0],))],
         example_expl=["Non-zeros keep order; zeros trail.", "Unchanged."]),
    dict(slug="running-sum", title="Running Sum", difficulty="Easy", topics=["Arrays"], subtopics=["Prefix Sum"], companies=["Google"],
         description="Return the running (prefix) sum: out[i] = nums[0] + … + nums[i].",
         hints=["Accumulate as you scan.", "out[i] = out[i-1] + nums[i]."],
         opt=("O(n)", "O(n)", "Single prefix pass."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int[]"},
         fn=lambda nums: _running_sum(nums),
         cases=[("example", "Example", ([1, 2, 3, 4],)), ("example", "Negatives", ([3, -1, 2],)), ("hidden", "Single", ([5],)), ("hidden", "Empty", ([],))],
         example_expl=["1,3,6,10.", "3,2,4."]),
    dict(slug="max-consecutive-ones", title="Max Consecutive Ones", difficulty="Easy", topics=["Arrays"], subtopics=["Counting"], companies=["Amazon"],
         description="Given a 0/1 array, return the length of the longest run of consecutive 1s.",
         hints=["Track the current run and the best run.", "Reset the current run on a 0."],
         opt=("O(n)", "O(1)", "Single pass with a running counter."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: _max_consec_ones(nums),
         cases=[("example", "Example", ([1, 1, 0, 1, 1, 1],)), ("example", "All ones", ([1, 1, 1],)), ("hidden", "No ones", ([0, 0],)), ("hidden", "Empty", ([],))],
         example_expl=["Best run is 3.", "Run of 3."]),
    dict(slug="second-largest", title="Second Largest", difficulty="Easy", topics=["Arrays"], subtopics=["Traversal"], companies=["Adobe"],
         description="Return the second largest distinct value (or the largest if only one distinct value exists).",
         hints=["Track the top two as you scan.", "Skip duplicates of the max."],
         opt=("O(n)", "O(1)", "Single pass tracking two maxima."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: _second_largest(nums),
         cases=[("example", "Example", ([3, 1, 4, 1, 5],)), ("example", "Dupes at top", ([5, 5, 3],)), ("hidden", "Single", ([9],)), ("hidden", "Two", ([2, 7],))],
         example_expl=["4 is second largest.", "3 is second largest."]),
    dict(slug="count-occurrences", title="Count Occurrences", difficulty="Easy", topics=["Arrays"], subtopics=["Counting"], companies=["Microsoft"],
         description="Return how many times `target` appears in the array.",
         hints=["Scan and count matches."],
         opt=("O(n)", "O(1)", "Single pass."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}], "returns": "int"},
         fn=lambda nums, target: sum(1 for x in nums if x == target),
         cases=[("example", "Example", ([1, 2, 2, 3, 2], 2)), ("example", "Absent", ([1, 2, 3], 9)), ("hidden", "Empty", ([], 1)), ("hidden", "All", ([4, 4, 4], 4))],
         example_expl=["2 appears 3 times.", "9 is absent."]),
    dict(slug="number-of-1-bits", title="Number of 1 Bits", difficulty="Easy", topics=["Bit Manipulation"], subtopics=["Bit Manipulation"], companies=["Apple", "Amazon"],
         description="Return the number of set bits (1s) in the binary representation of a non-negative integer.",
         hints=["Check the lowest bit with & 1, then shift.", "Or use n & (n-1) to drop the lowest set bit."],
         opt=("O(bits)", "O(1)", "Count set bits."),
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "int"},
         fn=lambda n: bin(n).count("1"),
         cases=[("example", "Eleven", (11,)), ("example", "Power of two", (128,)), ("hidden", "Zero", (0,)), ("hidden", "All low bits", (255,))],
         example_expl=["1011 has three 1s.", "10000000 has one."]),

    # ---------------- MEDIUM ----------------
    dict(slug="product-except-self", title="Product of Array Except Self", difficulty="Medium", topics=["Arrays", "Prefix Sum"], subtopics=["Prefix Sum"], companies=["Amazon", "Meta", "Apple"],
         description="Return an array where out[i] is the product of every element except nums[i] — without using division.",
         hints=["Prefix products to the left, suffix products to the right.", "Combine the two passes.", "No division allowed."],
         opt=("O(n)", "O(n)", "Prefix and suffix products."),
         editorial="Left-to-right prefix products, then multiply by right-to-left suffix products.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int[]"},
         fn=lambda nums: _product_except_self(nums),
         cases=[("example", "Example", ([1, 2, 3, 4],)), ("example", "With zero", ([0, 4, 0],)), ("hidden", "Negatives", ([-1, 1, 2],)), ("hidden", "Two", ([3, 5],))],
         example_expl=["24,12,8,6.", "Two zeros → all zero."]),
    dict(slug="best-time-buy-sell", title="Best Time to Buy and Sell Stock", difficulty="Medium", topics=["Arrays", "Dynamic Programming"], subtopics=["Greedy"], companies=["Amazon", "Bloomberg"],
         description="Given daily prices, return the maximum profit from one buy followed by one later sell (0 if no profit).",
         hints=["Track the lowest price seen so far.", "Best profit = price − running minimum.", "One pass suffices."],
         opt=("O(n)", "O(1)", "Track the running min and best profit."),
         editorial="Sweep left to right keeping the min price; the answer is the max of price − min.",
         spec={"name": "solve", "params": [{"name": "prices", "type": "int[]"}], "returns": "int"},
         fn=lambda prices: _best_buy_sell(prices),
         cases=[("example", "Example", ([7, 1, 5, 3, 6, 4],)), ("example", "Decreasing", ([7, 6, 4, 3],)), ("hidden", "Single", ([5],)), ("hidden", "Increasing", ([1, 2, 3, 4],))],
         example_expl=["Buy at 1, sell at 6 → 5.", "No profit → 0."]),
    dict(slug="container-most-water", title="Container With Most Water", difficulty="Medium", topics=["Arrays", "Two Pointers"], subtopics=["Two Pointers"], companies=["Amazon", "Google"],
         description="Given heights, return the most water a container formed by two lines can hold (area = min(h[i],h[j])·(j−i)).",
         hints=["Start with the widest pair.", "Move the shorter side inward — it's the limiter.", "Track the best area."],
         opt=("O(n)", "O(1)", "Two pointers from both ends."),
         editorial="Two pointers: area is bounded by the shorter wall, so advance that side to seek a taller one.",
         spec={"name": "solve", "params": [{"name": "heights", "type": "int[]"}], "returns": "int"},
         fn=lambda heights: _container(heights),
         cases=[("example", "Example", ([1, 8, 6, 2, 5, 4, 8, 3, 7],)), ("example", "Flat", ([1, 1],)), ("hidden", "Increasing", ([1, 2, 3, 4],)), ("hidden", "Peak", ([4, 1, 4],))],
         example_expl=["Lines 8 and 7 → 49.", "Area 1."]),
    dict(slug="house-robber", title="House Robber", difficulty="Medium", topics=["Dynamic Programming"], subtopics=["1D DP"], companies=["Amazon", "Adobe"],
         description="You can't rob two adjacent houses. Return the maximum total you can rob.",
         hints=["Decide rob-or-skip at each house.", "best[i] = max(best[i-1], best[i-2] + nums[i]).", "Two rolling variables suffice."],
         opt=("O(n)", "O(1)", "1-D DP with two rolling states."),
         editorial="At each house either skip (keep prev) or rob (prev-prev + value); take the max.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: _house_rob(nums),
         cases=[("example", "Example", ([1, 2, 3, 1],)), ("example", "Bigger", ([2, 7, 9, 3, 1],)), ("hidden", "Single", ([5],)), ("hidden", "Empty", ([],))],
         example_expl=["Rob houses 1 and 3 → 4.", "Rob 2,9,1 → 12."]),
    dict(slug="jump-game", title="Jump Game", difficulty="Medium", topics=["Arrays", "Greedy"], subtopics=["Greedy"], companies=["Amazon", "Meta"],
         description="Each value is the max jump length from that index. Return `true` if you can reach the last index.",
         hints=["Track the furthest reachable index.", "If your position ever exceeds reach, you're stuck.", "Greedy beats DP here."],
         opt=("O(n)", "O(1)", "Track the furthest reach greedily."),
         editorial="Sweep left to right; if index i ever exceeds the running max reach, return false.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "bool"},
         fn=lambda nums: _jump_game(nums),
         cases=[("example", "Reachable", ([2, 3, 1, 1, 4],)), ("example", "Stuck", ([3, 2, 1, 0, 4],)), ("hidden", "Single", ([0],)), ("hidden", "Zero early", ([0, 1],))],
         example_expl=["Jumps reach the end.", "Stuck at the 0."]),
    dict(slug="coin-change", title="Coin Change", difficulty="Medium", topics=["Dynamic Programming"], subtopics=["1D DP"], companies=["Amazon", "Uber", "Google"],
         description="Given coin denominations and an amount, return the fewest coins that make the amount, or -1 if impossible.",
         hints=["Build up answers for every amount from 0 to target.", "dp[a] = min over coins of dp[a-c] + 1.", "Unbounded coins — iterate amounts outward."],
         opt=("O(amount·coins)", "O(amount)", "Bottom-up unbounded-knapsack DP."),
         editorial="dp[a] = 1 + min(dp[a-c]) over coins c ≤ a; unreachable stays ∞ → -1.",
         spec={"name": "solve", "params": [{"name": "coins", "type": "int[]"}, {"name": "amount", "type": "int"}], "returns": "int"},
         fn=lambda coins, amount: _coin_change(coins, amount),
         cases=[("example", "Example", ([1, 2, 5], 11)), ("example", "Impossible", ([2], 3)), ("hidden", "Zero", ([1], 0)), ("hidden", "Exact", ([1, 3, 4], 6))],
         example_expl=["5+5+1 → 3 coins.", "Odd amount, only 2s → -1."]),
    dict(slug="coin-change-ways", title="Coin Change II (Count Ways)", difficulty="Medium", topics=["Dynamic Programming"], subtopics=["1D DP"], companies=["Amazon"],
         description="Return the number of distinct combinations of coins that sum to the amount (order doesn't matter).",
         hints=["Iterate coins in the outer loop to avoid counting permutations.", "dp[a] += dp[a-c].", "Start dp[0]=1."],
         opt=("O(amount·coins)", "O(amount)", "Combination-count DP (coin outer loop)."),
         spec={"name": "solve", "params": [{"name": "coins", "type": "int[]"}, {"name": "amount", "type": "int"}], "returns": "int"},
         fn=lambda coins, amount: _coin_change_ways(coins, amount),
         cases=[("example", "Example", ([1, 2, 5], 5)), ("example", "One way", ([2], 4)), ("hidden", "Zero", ([1, 2], 0)), ("hidden", "None", ([3], 2))],
         example_expl=["4 combinations make 5.", "2+2 → 1 way."]),
    dict(slug="longest-common-prefix", title="Longest Common Prefix", difficulty="Medium", topics=["Strings"], subtopics=["Matching"], companies=["Amazon", "Adobe"],
         description="Return the longest common leading prefix shared by all strings (empty string if none).",
         hints=["The answer is no longer than the shortest string.", "Shrink a candidate prefix against each word.", "Stop as soon as it's empty."],
         opt=("O(total chars)", "O(1)", "Shrink a prefix across all words."),
         spec={"name": "solve", "params": [{"name": "strs", "type": "string[]"}], "returns": "string"},
         fn=lambda strs: _lcp(strs),
         cases=[("example", "Example", (["flower", "flow", "flight"],)), ("example", "None", (["dog", "cat"],)), ("hidden", "Single", (["solo"],)), ("hidden", "Identical", (["ab", "ab"],))],
         example_expl=["'fl' is shared.", "No common prefix."]),
    dict(slug="search-insert-position", title="Search Insert Position", difficulty="Medium", topics=["Binary Search", "Arrays"], subtopics=["Lower Bound"], companies=["Amazon", "Microsoft"],
         description="In a sorted array, return the index of target, or the index where it would be inserted to keep order.",
         hints=["This is a lower-bound binary search.", "Narrow [lo, hi) until they meet.", "Return lo."],
         opt=("O(log n)", "O(1)", "Lower-bound binary search."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}], "returns": "int"},
         fn=lambda nums, target: _search_insert(nums, target),
         cases=[("example", "Present", ([1, 3, 5, 6], 5)), ("example", "Insert middle", ([1, 3, 5, 6], 2)), ("hidden", "Before all", ([2, 4], 1)), ("hidden", "After all", ([2, 4], 9))],
         example_expl=["5 is at index 2.", "2 inserts at index 1."]),
    dict(slug="integer-sqrt", title="Integer Square Root", difficulty="Medium", topics=["Binary Search", "Math"], subtopics=["Lower Bound"], companies=["Bloomberg", "Google"],
         description="Return the floor of the square root of a non-negative integer (no floating point).",
         hints=["Binary search the largest m with m·m ≤ x.", "Beware overflow when squaring.", "Answer is the high pointer."],
         opt=("O(log x)", "O(1)", "Binary search on the answer."),
         spec={"name": "solve", "params": [{"name": "x", "type": "int"}], "returns": "int"},
         fn=lambda x: _isqrt(x),
         cases=[("example", "Perfect", (16,)), ("example", "Floor", (17,)), ("hidden", "Zero", (0,)), ("hidden", "One", (1,)), ("hidden", "Large", (2147395599,))],
         example_expl=["√16 = 4.", "⌊√17⌋ = 4."]),
    dict(slug="min-cost-climbing-stairs", title="Min Cost Climbing Stairs", difficulty="Medium", topics=["Dynamic Programming"], subtopics=["1D DP"], companies=["Amazon"],
         description="Each step has a cost; from a step you may climb 1 or 2. Starting before the first step, return the min cost to go past the top.",
         hints=["Reaching step i costs its cost plus the cheaper of the two below.", "dp[i] = cost[i] + min(dp[i-1], dp[i-2]).", "You may start at step 0 or 1."],
         opt=("O(n)", "O(1)", "1-D DP with two rolling states."),
         spec={"name": "solve", "params": [{"name": "cost", "type": "int[]"}], "returns": "int"},
         fn=lambda cost: _min_cost_stairs(cost),
         cases=[("example", "Example", ([10, 15, 20],)), ("example", "Longer", ([1, 100, 1, 1, 1, 100, 1, 1, 100, 1],)), ("hidden", "Two", ([5, 3],)), ("hidden", "Empty", ([],))],
         example_expl=["Start at 15, step to top → 15.", "Weave the cheap steps → 6."]),
    dict(slug="daily-temperatures", title="Daily Temperatures", difficulty="Medium", topics=["Stack", "Arrays"], subtopics=["Monotonic Stack"], companies=["Amazon", "Google"],
         description="For each day, return how many days until a warmer temperature (0 if none).",
         hints=["A monotonic decreasing stack of indices helps.", "Pop while the current day is warmer.", "The gap is the answer for popped days."],
         opt=("O(n)", "O(n)", "Monotonic stack of indices."),
         editorial="Keep a stack of indices with decreasing temps; when today is warmer, pop and record the day gap.",
         spec={"name": "solve", "params": [{"name": "temps", "type": "int[]"}], "returns": "int[]"},
         fn=lambda temps: _daily_temps(temps),
         cases=[("example", "Example", ([73, 74, 75, 71, 69, 72, 76, 73],)), ("example", "Decreasing", ([5, 4, 3],)), ("hidden", "Single", ([50],)), ("hidden", "Increasing", ([1, 2, 3],))],
         example_expl=["1,1,4,2,1,1,0,0.", "Never warmer → all 0."]),
    dict(slug="next-greater-element", title="Next Greater Element", difficulty="Medium", topics=["Stack", "Arrays"], subtopics=["Monotonic Stack"], companies=["Amazon", "Bloomberg"],
         description="For each element, return the next strictly greater element to its right, or -1 if none.",
         hints=["Monotonic stack of pending indices.", "Pop when a bigger value arrives.", "Unpopped indices get -1."],
         opt=("O(n)", "O(n)", "Monotonic decreasing stack."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int[]"},
         fn=lambda nums: _next_greater(nums),
         cases=[("example", "Example", ([2, 1, 3, 4, 2],)), ("example", "Decreasing", ([5, 4, 3],)), ("hidden", "Single", ([7],)), ("hidden", "Increasing", ([1, 2, 3],))],
         example_expl=["3,3,4,-1,-1.", "No greater to the right → all -1."]),
    dict(slug="subarray-sum-k", title="Subarray Sum Equals K", difficulty="Medium", topics=["Arrays", "Hashing"], subtopics=["Prefix Sum"], companies=["Amazon", "Meta"],
         description="Return the number of contiguous subarrays whose elements sum to k.",
         hints=["Prefix sums turn 'range sum = k' into 'seen a prefix of s-k'.", "Count prefix sums in a hash map.", "Handle the empty prefix (sum 0)."],
         opt=("O(n)", "O(n)", "Prefix sums + hash map of counts."),
         editorial="For running prefix s, add the count of earlier prefixes equal to s−k.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}], "returns": "int"},
         fn=lambda nums, k: _subarray_sum_k(nums, k),
         cases=[("example", "Example", ([1, 1, 1], 2)), ("example", "With negatives", ([1, -1, 0], 0)), ("hidden", "Single", ([3], 3)), ("hidden", "None", ([1, 2], 9))],
         example_expl=["Two subarrays sum to 2.", "Three subarrays sum to 0."]),
    dict(slug="longest-consecutive", title="Longest Consecutive Sequence", difficulty="Medium", topics=["Arrays", "Hashing"], subtopics=["Hash Set"], companies=["Google", "Amazon"],
         description="Return the length of the longest run of consecutive integers (order in the array doesn't matter).",
         hints=["Put everything in a set for O(1) membership.", "Only start counting at sequence starts (no x-1 present).", "Walk upward while x+1 exists."],
         opt=("O(n)", "O(n)", "Hash set; count only from sequence starts."),
         editorial="Insert all into a set; for each value with no predecessor, extend upward and measure the run.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: _longest_consecutive(nums),
         cases=[("example", "Example", ([100, 4, 200, 1, 3, 2],)), ("example", "Dupes", ([1, 2, 2, 3],)), ("hidden", "Empty", ([],)), ("hidden", "Single", ([9],))],
         example_expl=["1,2,3,4 → 4.", "1,2,3 → 3."]),
    dict(slug="kth-largest-element", title="Kth Largest Element", difficulty="Medium", topics=["Sorting", "Heap"], subtopics=["Sorting"], companies=["Amazon", "Meta"],
         description="Return the kth largest element in the array (1-indexed, k valid).",
         hints=["Sorting is the simple route.", "A size-k min-heap is more efficient.", "Quickselect gives average O(n)."],
         opt=("O(n log n)", "O(1)", "Sort descending and index (heap/quickselect improve it)."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}], "returns": "int"},
         fn=lambda nums, k: _kth_largest_helper(nums, k),
         cases=[("example", "Example", ([3, 2, 1, 5, 6, 4], 2)), ("example", "With dupes", ([3, 2, 3, 1, 2, 4, 5, 5, 6], 4)), ("hidden", "First", ([1], 1)), ("hidden", "Last", ([7, 8, 9], 3))],
         example_expl=["2nd largest is 5.", "4th largest is 4."]),
    dict(slug="rotate-array-right", title="Rotate Array Right", difficulty="Medium", topics=["Arrays"], subtopics=["Cyclic Shift"], companies=["Amazon", "Microsoft"],
         description="Rotate the array to the right by k steps and return the result.",
         hints=["k can exceed the length — take k mod n.", "The last k elements wrap to the front.", "Reversal trick does it in place."],
         opt=("O(n)", "O(n)", "Slice/reverse to shift by k mod n."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}], "returns": "int[]"},
         fn=lambda nums, k: _rotate_right(nums, k),
         cases=[("example", "Example", ([1, 2, 3, 4, 5, 6, 7], 3)), ("example", "k > n", ([1, 2, 3], 4)), ("hidden", "k = 0", ([1, 2], 0)), ("hidden", "Single", ([9], 5))],
         example_expl=["5,6,7,1,2,3,4.", "k mod 3 = 1 → 3,1,2."]),

    # ---------------- HARD ----------------
    dict(slug="word-break", title="Word Break", difficulty="Hard", topics=["Dynamic Programming", "Strings"], subtopics=["1D DP"], companies=["Amazon", "Google", "Meta"],
         description="Return `true` if the string can be segmented into a space-separated sequence of dictionary words.",
         hints=["dp[i] = can we segment the first i characters.", "dp[i] is true if some dp[j] is true and s[j:i] is a word.", "Use a set for word lookups."],
         opt=("O(n²)", "O(n)", "DP over prefixes with a word set."),
         editorial="dp[i] true iff a split point j exists with dp[j] true and substring s[j:i] in the dictionary.",
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}, {"name": "words", "type": "string[]"}], "returns": "bool"},
         fn=lambda s, words: _word_break(s, words),
         cases=[("example", "Breakable", ("leetcode", ["leet", "code"])), ("example", "Not", ("catsandog", ["cats", "dog", "sand", "and", "cat"])), ("hidden", "Reuse", ("aaaa", ["a", "aa"])), ("hidden", "Single", ("abc", ["abc"]))],
         example_expl=["'leet code'.", "Cannot cover 'catsandog'."]),
    dict(slug="decode-ways", title="Decode Ways", difficulty="Hard", topics=["Dynamic Programming", "Strings"], subtopics=["1D DP"], companies=["Amazon", "Meta"],
         description="A→1 … Z→26. Return how many ways a digit string can be decoded to letters.",
         hints=["Each position: take one digit (1–9) or two digits (10–26).", "dp[i] sums the valid one- and two-digit extensions.", "Leading zeros kill a decoding."],
         opt=("O(n)", "O(1)", "1-D DP counting valid 1- and 2-digit splits."),
         editorial="dp[i] += dp[i-1] if s[i-1]≠'0'; dp[i] += dp[i-2] if s[i-2:i] in 10..26.",
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}], "returns": "int"},
         fn=lambda s: _decode_ways(s),
         cases=[("example", "Two ways", ("12",)), ("example", "226", ("226",)), ("hidden", "Leading zero", ("06",)), ("hidden", "Zero pair", ("10",))],
         example_expl=["'AB' or 'L' → 2.", "'BZ','VF','BBF' → 3."]),
    dict(slug="longest-palindrome-length", title="Longest Palindromic Substring (length)", difficulty="Hard", topics=["Strings", "Dynamic Programming"], subtopics=["Expand Around Center"], companies=["Amazon", "Microsoft"],
         description="Return the length of the longest palindromic substring.",
         hints=["Every palindrome has a center.", "Expand outward from each of the 2n−1 centers.", "Track the best length."],
         opt=("O(n²)", "O(1)", "Expand around each center."),
         editorial="For each center (single char and gap), expand while characters match; keep the longest span.",
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}], "returns": "int"},
         fn=lambda s: _longest_palindrome_len(s),
         cases=[("example", "babad", ("babad",)), ("example", "cbbd", ("cbbd",)), ("hidden", "Single", ("a",)), ("hidden", "All same", ("aaaa",))],
         example_expl=["'bab' (or 'aba') → 3.", "'bb' → 2."]),
    dict(slug="maximum-product-subarray", title="Maximum Product Subarray", difficulty="Hard", topics=["Dynamic Programming", "Arrays"], subtopics=["1D DP"], companies=["Amazon", "Bloomberg"],
         description="Return the largest product of a contiguous non-empty subarray.",
         hints=["A negative can flip the largest and smallest.", "Track both the max and min product ending here.", "Update the answer each step."],
         opt=("O(n)", "O(1)", "Track running max and min products."),
         editorial="Because negatives swap extremes, carry both max and min ending at i; answer is the running max.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: _max_product_subarray(nums),
         cases=[("example", "Example", ([2, 3, -2, 4],)), ("example", "Zeroes", ([-2, 0, -1],)), ("hidden", "Two negs", ([-2, -3, 7],)), ("hidden", "Single", ([-5],))],
         example_expl=["2·3 → 6.", "Best single is 0."]),
    dict(slug="partition-equal-subset-sum", title="Partition Equal Subset Sum", difficulty="Hard", topics=["Dynamic Programming"], subtopics=["Subset Sum"], companies=["Amazon", "Uber"],
         description="Return `true` if the array can be split into two subsets with equal sum.",
         hints=["If the total is odd, it's impossible.", "Otherwise, can we hit total/2 as a subset sum?", "0/1 knapsack over a boolean DP."],
         opt=("O(n·sum)", "O(sum)", "Subset-sum DP to total/2."),
         editorial="Reduce to: is there a subset summing to total/2? Solve with a boolean 0/1-knapsack DP.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "bool"},
         fn=lambda nums: _partition_equal(nums),
         cases=[("example", "Splittable", ([1, 5, 11, 5],)), ("example", "Not", ([1, 2, 3, 5],)), ("hidden", "Two equal", ([2, 2],)), ("hidden", "Odd total", ([1, 2],))],
         example_expl=["{1,5,5} and {11}.", "Total 11 is odd-ish — no equal split."]),
]


def _kth_largest_helper(nums, k):
    return sorted(nums, reverse=True)[k - 1]


# ---------------------------------------------------------------------------
# Build JSON
# ---------------------------------------------------------------------------

out = []
for d in DEFS:
    ref = d["ref"]
    examples = []
    test_cases = []
    ex_expl = d.get("example_expl", [])
    ex_i = 0
    for (kind, name, inp) in d["cases"]:
        expected = ref(inp)
        test_cases.append({
            "kind": kind,
            "name": name,
            "input": inp,
            "expected_output": expected,
            "ordering": len(test_cases),
        })
        if kind == "example":
            expl = ex_expl[ex_i] if ex_i < len(ex_expl) else ""
            examples.append({"input": inp.rstrip("\n"), "output": expected, "explanation": expl})
            ex_i += 1

    opt_time, opt_space, opt_expl = d["opt"]
    starter = {}
    if JAVA_STARTERS.get(d["slug"]):
        starter["java"] = JAVA_STARTERS[d["slug"]]
    if d.get("starter_py"):
        starter["python"] = d["starter_py"]
    if d.get("starter_js"):
        starter["javascript"] = d["starter_js"]
        # TypeScript can reuse the JS skeleton (Node strips types; plain JS is valid TS).
        starter["typescript"] = d["starter_js"]

    out.append({
        "slug": d["slug"],
        "title": d["title"],
        "difficulty": d["difficulty"],
        "description": d["description"],
        "constraints": d["constraints"],
        "examples": examples,
        "editorial": d["editorial"],
        "optimal_time": opt_time,
        "optimal_space": opt_space,
        "optimal_explanation": opt_expl,
        "starter_code": starter,
        "topics": d["topics"],
        "subtopics": d.get("subtopics", []),
        "companies": d.get("companies", []),
        "patterns": derive_patterns(d),
        "hints": d["hints"],
        "prerequisites": build_prereqs(d["slug"]),
        "test_cases": test_cases,
        "editorials": EDITORIALS_EXTRA.get(d["slug"], []),
        "follow_ups": FOLLOWUPS.get(d["slug"], []),
        "judge_mode": "exact",
    })

# Function-harness demo problems: inputs are serialized args, expected outputs
# are the serialized return of the reference implementation.
for d in HARNESS_DEFS:
    spec = d["spec"]
    fn = d["fn"]
    ret_ty = spec["returns"]
    examples = []
    test_cases = []
    ex_expl = d.get("example_expl", [])
    ex_i = 0
    for (kind, name, arg_tuple) in d["cases"]:
        input_str = "\n".join(_ser_arg(v, p["type"]) for v, p in zip(arg_tuple, spec["params"])) + "\n"
        expected = _ser(fn(*arg_tuple), ret_ty)
        test_cases.append({
            "kind": kind, "name": name, "input": input_str,
            "expected_output": expected, "ordering": len(test_cases),
        })
        if kind == "example":
            expl = ex_expl[ex_i] if ex_i < len(ex_expl) else ""
            examples.append({"input": input_str.rstrip("\n"), "output": expected, "explanation": expl})
            ex_i += 1
    opt_time, opt_space, opt_expl = d["opt"]
    out.append({
        "slug": d["slug"], "title": d["title"], "difficulty": d["difficulty"],
        "description": d["description"], "constraints": d.get("constraints", ""),
        "examples": examples, "editorial": d.get("editorial", ""),
        "optimal_time": opt_time, "optimal_space": opt_space, "optimal_explanation": opt_expl,
        "starter_code": {
            "python": d.get("starter_py") or stub_py(spec),
            "java": d.get("starter_java") or stub_java(spec),
        },
        "topics": d["topics"], "subtopics": d.get("subtopics", []),
        "companies": d.get("companies", []), "patterns": derive_patterns(d),
        "hints": d.get("hints", []), "prerequisites": build_prereqs(d["slug"]),
        "test_cases": test_cases,
        "editorials": d.get("editorials", []), "follow_ups": d.get("follow_ups", []),
        "function_spec": spec, "judge_mode": d.get("judge_mode", "exact"),
        "float_tolerance": d.get("float_tolerance", 0),
    })

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"Wrote {len(out)} problems to {os.path.relpath(OUT)}")

CONCEPTS_OUT = os.path.join(HERE, "..", "src-tauri", "seeds", "concepts.json")
concepts = build_concepts()
with open(CONCEPTS_OUT, "w", encoding="utf-8") as f:
    json.dump(concepts, f, indent=2, ensure_ascii=False)
print(f"Wrote {len(concepts)} concepts to {os.path.relpath(CONCEPTS_OUT)}")
