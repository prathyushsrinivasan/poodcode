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
    "array_patterns": {
        "name": "Array Problem Patterns",
        "what": "A decision guide that maps the wording of an array question to the technique that solves it.",
        "deep": "Almost every array problem is one of a handful of shapes. The real skill is reading the prompt, spotting the signal words ('contiguous', 'sorted', 'longest', 'size k', 'in place'), and jumping straight to the matching skeleton instead of re-deriving an approach each time.",
        "java": "No single API — this is a routing table. Learn the signal → pattern → skeleton mapping, then reach for iteration, two pointers, sliding window, prefix sums, or in-place reversal.",
    },
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
    "array_patterns": "Arrays",
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
    "array_patterns": """### The core idea
Nearly every array question is one of a **small number of shapes**. If you can name the shape from the wording, you already know the code skeleton. Read the prompt, find the signal word, jump to the pattern.

### Signal → pattern cheat sheet
| The question says… | Reach for | Key move |
| --- | --- | --- |
| "sum / max / min / count of the array", "in one pass" | **Single-pass iteration** | Carry a running accumulator |
| "**contiguous** subarray with the largest sum" | **Kadane** | Extend-or-restart at each index |
| "sum of `a[l..r]`", many **range-sum queries** | **Prefix sums** | Precompute once, answer in O(1) |
| "**sorted** array" + "pair that sums to T / closest / container" | **Two pointers** (ends inward) | Move the end that helps |
| "remove / move / dedupe **in place**" | **Two pointers** (slow write, fast read) | Slow pointer writes kept elements |
| "**longest / shortest** subarray or substring with <property>" | **Sliding window** (variable) | Grow right, shrink left on break |
| "window / subarray of **size k**" | **Sliding window** (fixed) | Add entering, drop leaving |
| "reverse", "**rotate by k**", "O(1) extra space" | **In-place reversal** | Swap ends; rotate = 3 reversals |
| "count occurrences", values are small integers | **Counting array** `int[]` | Index by value |
| "element appears **more than n/2** times" | **Boyer–Moore majority** | Cancel non-matches |
| "**sorted**" + "find / first index of / does X exist" | **Binary search** | Halve the search space |

### The five skeletons you will reuse most
```java
// 1. Single pass — one summary of the whole array
long acc = 0;                       // or best = a[0], count = 0
for (int x : a) acc += x;           // combine each element

// 2. Two pointers, converging (needs a SORTED array)
int lo = 0, hi = n - 1;
while (lo < hi) {
    int s = a[lo] + a[hi];
    if (s == target) { /* found */ break; }
    else if (s < target) lo++;      // need a bigger value
    else hi--;                      // need a smaller value
}

// 3. Two pointers, slow write / fast read (in-place filter)
int w = 0;
for (int r = 0; r < n; r++)
    if (keep(a[r])) a[w++] = a[r];  // a[0..w-1] is the result, w its length

// 4. Sliding window (variable size)
int left = 0; long cur = 0, best = 0;
for (int r = 0; r < n; r++) {
    cur += a[r];                        // extend right
    while (invariantBroken(cur)) cur -= a[left++]; // shrink left
    best = Math.max(best, r - left + 1);
}

// 5. Prefix sums (answer any range in O(1))
long[] pre = new long[n + 1];
for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];
long sumLR = pre[r + 1] - pre[l];       // sum of a[l..r], inclusive
```

### How to use this page
1. Underline the signal words in the prompt: *contiguous, sorted, longest, size k, in place, range sum*.
2. Match a row in the table above.
3. Paste the skeleton, then fill in the one problem-specific line (the test, the update, the accumulator).

The drills below make you write that one decisive line for each pattern.
""",
    "iteration": """### When to reach for this
The question wants a **single summary of the whole array** — a sum, max, min, count, or the index of one of those — and the order does not matter. Carry a running variable and update it as you sweep once, left to right.

### Simulated solve — max of `[3, 9, 2, 7]`
Start `best` at the first element, then update only when you see something bigger.

| i | a[i] | best before | bigger? | best after |
| - | ---- | ----------- | ------- | ---------- |
| 0 | 3 | — | init | 3 |
| 1 | 9 | 3 | 9 > 3 ✓ | 9 |
| 2 | 2 | 9 | 2 > 9 ✗ | 9 |
| 3 | 7 | 9 | 7 > 9 ✗ | 9 |

Answer: **9**. One sweep — O(n) time, O(1) extra space.

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
    "two_pointers": """### When to reach for this
Two signals point here. **(1)** The array is **sorted** and you need a pair/triple (sum to T, closest, most water) → converge from both ends. **(2)** You must **remove / move / dedupe in place** → a slow *write* pointer trails a fast *read* pointer.

### Simulated solve — does a pair in sorted `[1, 2, 4, 7, 11]` sum to 9?
Look at the two ends. Too big? lower the high end. Too small? raise the low end.

| lo | hi | a[lo]+a[hi] | vs 9 | move |
| -- | -- | ----------- | ---- | ---- |
| 0 | 4 | 1 + 11 = 12 | too big | hi-- |
| 0 | 3 | 1 + 7 = 8 | too small | lo++ |
| 1 | 3 | 2 + 7 = 9 | equal ✓ | **found** |

Answer: **yes** (2 + 7). Each pointer only moves inward, so it is O(n).

### In code (Java)
```java
int lo = 0, hi = n - 1;                 // converging variant (sorted input)
while (lo < hi) {
    int s = a[lo] + a[hi];
    if (s == target) return true;
    else if (s < target) lo++;          // need bigger → raise the low end
    else hi--;                          // need smaller → lower the high end
}

int w = 0;                              // slow/fast variant (in-place filter)
for (int r = 0; r < n; r++)
    if (a[r] != 0) a[w++] = a[r];       // keep non-zeros, in order
```

### Watch out for
- The converging variant needs a **sorted** array — sort first if it isn't.
- The slow/fast variant preserves order: only kept elements advance `w`.
- The loop ends when `lo >= hi`; a lone middle element needs no test.
""",
    "sliding_window": """### When to reach for this
Signals: **"longest / shortest"** subarray or substring meeting a condition, or a window of **fixed size k**. Extend the right edge; when the invariant breaks (or the window overflows size k), advance the left edge. Each index enters and leaves once → O(n).

### Simulated solve — max sum of a size-2 window in `[1, 3, -1, 5, 2]`
Slide by **adding the element that enters** and **subtracting the one that leaves**.

| r | enters | leaves | window sum | best |
| - | ------ | ------ | ---------- | ---- |
| 1 | 1+3 (init) | — | 4 | 4 |
| 2 | -1 | 1 | 2 | 4 |
| 3 | 5 | 3 | 4 | 4 |
| 4 | 2 | -1 | 7 | **7** |

Answer: **7** — the window `[5, 2]`.

### In code (Java) — variable window (longest with sum ≤ limit)
```java
int left = 0; long cur = 0; int best = 0;
for (int r = 0; r < n; r++) {
    cur += a[r];                             // extend right
    while (cur > limit) cur -= a[left++];    // shrink until valid again
    best = Math.max(best, r - left + 1);
}
```

### Watch out for
- The inner `while` looks quadratic but is not: `left` only ever moves forward → O(n) total.
- Variable-size windows assume **non-negative** values, so shrinking always helps.
- Fixed size k? Skip the `while`; just do `cur += a[r] - a[r - k]` once `r >= k`.
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
    "prefix_max": """### When to reach for this
Signals: **"sum of `a[l..r]`"** with many queries, or **"best value so far"** — max profit, running maximum, cheapest-so-far. Precompute an aggregate from the left so each later answer is O(1).

### Simulated solve — best profit on prices `[7, 1, 5, 3, 6]`
"Buy low, sell later" = for each day, how much could you make selling today given the cheapest price seen so far? Track `minSoFar` and the best gap.

| i | price | minSoFar | price − minSoFar | best |
| - | ----- | -------- | ---------------- | ---- |
| 0 | 7 | 7 | — | 0 |
| 1 | 1 | 1 | 0 | 0 |
| 2 | 5 | 1 | 4 | 4 |
| 3 | 3 | 1 | 2 | 4 |
| 4 | 6 | 1 | 5 | **5** |

Answer: **5** (buy at 1, sell at 6). One pass, no nested loop.

### Prefix sums in code (Java)
```java
long[] pre = new long[n + 1];               // pre[0] = 0
for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];
long sumLR = pre[r + 1] - pre[l];           // sum of a[l..r], inclusive
```

### Watch out for
- Use a size **n + 1** prefix array so `pre[0] = 0` and the query needs no special case.
- Sums grow fast — accumulate in `long` to dodge overflow.
- "Best so far" problems keep just one or two running variables, not a whole array.
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
    "inplace_reverse": """### When to reach for this
Signals: **"reverse"**, **"rotate by k"**, or "**O(1) extra space**". Swap symmetric positions inward. The neat trick: a right-rotation is just three reversals.

### Simulated solve — rotate `[1, 2, 3, 4, 5]` right by k = 2
Reverse the whole thing, then reverse the first `k`, then reverse the rest.

| step | operation | array |
| ---- | --------- | ----- |
| start | — | 1 2 3 4 5 |
| 1 | reverse all | 5 4 3 2 1 |
| 2 | reverse first k = 2 | 4 5 3 2 1 |
| 3 | reverse last n − k = 3 | **4 5 1 2 3** |

Answer: **4 5 1 2 3** — the last 2 elements wrapped to the front, no second array.

### In code (Java)
```java
static void rev(int[] a, int i, int j) {
    while (i < j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }
}
// rotate right by k:
k %= n;                                  // rotating by n is a no-op
rev(a, 0, n - 1);
rev(a, 0, k - 1);
rev(a, k, n - 1);
```

### Watch out for
- Reduce `k %= n` first, or `k` past the length breaks the partial reversals.
- Each swap is `a[i] ↔ a[j]`; the loop stops when `i >= j`.
- O(1) extra space — that is the whole point over "copy into a new array".
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


# ---------------------------------------------------------------------------
# Concept exercises — tiny "half-coded" fill-in-the-blank drills.
#
# Each concept in the Learn tab teaches syntax, then offers >=3 exercises where
# almost the whole Java program is written and the learner types only the one
# piece the lesson is about. The blank the learner fills is shown as ____.
#
# Authoring model (`ex`): give the COMPLETE, correct program (`full`, the
# reveal-able solution) plus the exact substring(s) to blank out (`blanks`).
# The starter shown to the learner is `full` with each blank replaced by ____.
# `tests` are (stdin, expected_stdout) pairs; expected outputs are proven
# correct by tests/verify_exercises.rs, which runs `full` through the REAL judge
# (same trust model as reference_solutions.json).
# ---------------------------------------------------------------------------

def prog(body):
    """Wrap an indented main() body in the standard Scanner scaffold."""
    return (
        "import java.util.*;\n\n"
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        f"{body}\n"
        "    }\n"
        "}\n"
    )


def ex(eid, title, prompt, full, blanks, tests, hint="", source_slug=None,
       kind="drill", difficulty=""):
    starter = full
    for b in blanks:
        assert b in full, f"exercise {eid}: blank not found in solution: {b!r}"
        starter = starter.replace(b, "____", 1)
    assert starter != full, f"exercise {eid}: no blank was applied"
    assert tests, f"exercise {eid}: needs at least one test"
    return {
        "id": eid,
        "title": title,
        "prompt": prompt,
        "hint": hint,
        "language": "java",
        "kind": kind,
        "difficulty": difficulty,
        "starter": starter,
        "solution": full,
        "tests": [{"input": i, "output": o} for (i, o) in tests],
        "source_slug": source_slug or "",
    }


EXERCISES = {
    # -- Foundations ------------------------------------------------------
    "io_basics": [
        ex(
            "io_basics-sum", "Print the sum",
            "The two numbers are already read into `a` and `b`. Replace `____` so the program prints their sum.",
            prog(
                "        int a = sc.nextInt();\n"
                "        int b = sc.nextInt();\n"
                "        System.out.println(a + b);"),
            ["System.out.println(a + b);"],
            [("3 4", "7"), ("10 -2", "8"), ("0 0", "0")],
            hint="System.out.println(...) prints one line — put a + b inside the parentheses.",
        ),
        ex(
            "io_basics-echo-line", "Read a whole line",
            "The program should echo one full line of text. Replace `____` with the statement that reads the line into `line`.",
            prog(
                "        String line = sc.nextLine();\n"
                "        System.out.println(line);"),
            ["String line = sc.nextLine();"],
            [("hello world", "hello world"), ("Poodcode rocks", "Poodcode rocks"),
             ("42 is just text here", "42 is just text here")],
            hint="nextLine() reads a whole line (spaces and all); nextInt() would only grab one number.",
        ),
        ex(
            "io_basics-greet", "Build the greeting",
            "The name is in `name`. Replace `____` to print exactly `Hi, <name>!` — for input `Ada` print `Hi, Ada!`.",
            prog(
                "        String name = sc.nextLine();\n"
                "        System.out.println(\"Hi, \" + name + \"!\");"),
            ["System.out.println(\"Hi, \" + name + \"!\");"],
            [("Ada", "Hi, Ada!"), ("Bob", "Hi, Bob!"), ("Grace Hopper", "Hi, Grace Hopper!")],
            hint="Glue text together with + : \"Hi, \" + name + \"!\".",
        ),
    ],
    "variables": [
        ex(
            "variables-long", "Hold a big number",
            "The input is larger than an `int` can hold (over 2.1 billion). Replace `____` to read it into a `long` named `big`.",
            prog(
                "        long big = sc.nextLong();\n"
                "        System.out.println(big);"),
            ["long big = sc.nextLong();"],
            [("5000000000", "5000000000"), ("9999999999", "9999999999"), ("42", "42")],
            hint="Declare the variable as long and read it with sc.nextLong().",
        ),
        ex(
            "variables-avg", "Average as a decimal",
            "Replace `____` so `avg` is the true average of `a` and `b` — a decimal, not rounded down.",
            prog(
                "        int a = sc.nextInt();\n"
                "        int b = sc.nextInt();\n"
                "        double avg = (a + b) / 2.0;\n"
                "        System.out.println(avg);"),
            ["double avg = (a + b) / 2.0;"],
            [("3 4", "3.5"), ("10 10", "10.0"), ("1 2", "1.5")],
            hint="Divide by 2.0 (a double) so the fraction survives, and store it in a double.",
        ),
        ex(
            "variables-boolean", "Store a yes/no",
            "Replace `____` so `isZero` is `true` when `n` equals 0 and `false` otherwise.",
            prog(
                "        int n = sc.nextInt();\n"
                "        boolean isZero = (n == 0);\n"
                "        System.out.println(isZero);"),
            ["boolean isZero = (n == 0);"],
            [("0", "true"), ("5", "false"), ("-3", "false")],
            hint="Compare numbers with ==, and keep the true/false result in a boolean.",
        ),
    ],
    "arithmetic": [
        ex(
            "arithmetic-divmod", "Quotient and remainder",
            "Replace `____` to print the integer quotient and remainder of `a / b`, separated by a space (e.g. `17 5` -> `3 2`).",
            prog(
                "        int a = sc.nextInt();\n"
                "        int b = sc.nextInt();\n"
                "        System.out.println(a / b + \" \" + a % b);"),
            ["a / b + \" \" + a % b"],
            [("17 5", "3 2"), ("20 4", "5 0"), ("7 3", "2 1")],
            hint="/ is integer division; % is the remainder.",
        ),
        ex(
            "arithmetic-lastdigit", "Last digit",
            "Replace `____` to print the last digit of `n` (e.g. 1234 -> 4).",
            prog(
                "        int n = sc.nextInt();\n"
                "        System.out.println(n % 10);"),
            ["n % 10"],
            [("1234", "4"), ("7", "7"), ("40", "0")],
            hint="The last decimal digit is the remainder after dividing by 10.",
        ),
        ex(
            "arithmetic-double-div", "Keep the fraction",
            "`a / b` on two ints throws the fraction away. Replace `____` to print the exact decimal result (e.g. 7 2 -> 3.5).",
            prog(
                "        int a = sc.nextInt();\n"
                "        int b = sc.nextInt();\n"
                "        System.out.println((double) a / b);"),
            ["(double) a / b"],
            [("7 2", "3.5"), ("9 4", "2.25"), ("5 2", "2.5")],
            hint="Cast one side to double first: (double) a / b.",
        ),
    ],
    "conditionals": [
        ex(
            "conditionals-evenodd", "Even or odd",
            "Replace `____` with the condition that is true when `n` is even, so the program prints `Even` or `Odd`.",
            prog(
                "        int n = sc.nextInt();\n"
                "        if (n % 2 == 0) {\n"
                "            System.out.println(\"Even\");\n"
                "        } else {\n"
                "            System.out.println(\"Odd\");\n"
                "        }"),
            ["n % 2 == 0"],
            [("4", "Even"), ("7", "Odd"), ("0", "Even")],
            hint="A number is even when its remainder mod 2 is 0.",
        ),
        ex(
            "conditionals-sign", "Positive, negative, zero",
            "The `Positive` and `Zero` branches are written. Replace `____` with the middle branch that catches negative numbers.",
            prog(
                "        int n = sc.nextInt();\n"
                "        if (n > 0) {\n"
                "            System.out.println(\"Positive\");\n"
                "        } else if (n < 0) {\n"
                "            System.out.println(\"Negative\");\n"
                "        } else {\n"
                "            System.out.println(\"Zero\");\n"
                "        }"),
            ["else if (n < 0)"],
            [("5", "Positive"), ("-2", "Negative"), ("0", "Zero")],
            hint="Chain another test with `else if (...)` between the first if and the final else.",
        ),
        ex(
            "conditionals-max2", "The larger of two",
            "Replace `____` so the program prints the larger of `a` and `b` (print either when they are equal).",
            prog(
                "        int a = sc.nextInt();\n"
                "        int b = sc.nextInt();\n"
                "        if (a > b) {\n"
                "            System.out.println(a);\n"
                "        } else {\n"
                "            System.out.println(b);\n"
                "        }"),
            ["if (a > b)"],
            [("3 8", "8"), ("10 4", "10"), ("5 5", "5")],
            hint="Test whether a is greater than b.",
        ),
    ],
    "loops_basic": [
        ex(
            "loops_basic-sum", "Sum 1..n",
            "The loop runs `i` from 1 to n. Replace `____` in the loop body so `sum` ends up as 1+2+...+n.",
            prog(
                "        int n = sc.nextInt();\n"
                "        long sum = 0;\n"
                "        for (int i = 1; i <= n; i++) {\n"
                "            sum += i;\n"
                "        }\n"
                "        System.out.println(sum);"),
            ["sum += i;"],
            [("5", "15"), ("1", "1"), ("100", "5050")],
            hint="Add the current i to sum each pass: sum += i;",
        ),
        ex(
            "loops_basic-factorial", "Factorial",
            "Replace `____` so `f` becomes n! = 1*2*...*n (5! is 120).",
            prog(
                "        int n = sc.nextInt();\n"
                "        long f = 1;\n"
                "        for (int i = 2; i <= n; i++) {\n"
                "            f *= i;\n"
                "        }\n"
                "        System.out.println(f);"),
            ["f *= i;"],
            [("5", "120"), ("1", "1"), ("10", "3628800")],
            hint="Multiply f by each i: f *= i;",
        ),
        ex(
            "loops_basic-countdown", "Count down",
            "Replace `____` in the for-header so the loop counts down from n to 1, printing `n ... 2 1` (e.g. 3 -> `3 2 1`).",
            prog(
                "        int n = sc.nextInt();\n"
                "        StringBuilder sb = new StringBuilder();\n"
                "        for (int i = n; i >= 1; i--) {\n"
                "            sb.append(i);\n"
                "            if (i > 1) sb.append(\" \");\n"
                "        }\n"
                "        System.out.println(sb.toString());"),
            ["int i = n; i >= 1; i--"],
            [("3", "3 2 1"), ("1", "1"), ("5", "5 4 3 2 1")],
            hint="Start i at n, keep going while i >= 1, and step with i--.",
        ),
    ],
    "boolean_logic": [
        ex(
            "boolean_logic-inrange", "Inside a range",
            "Replace `____` so `inRange` is true exactly when x is between 1 and 10, inclusive.",
            prog(
                "        int x = sc.nextInt();\n"
                "        boolean inRange = (x >= 1) && (x <= 10);\n"
                "        System.out.println(inRange);"),
            ["(x >= 1) && (x <= 10)"],
            [("5", "true"), ("10", "true"), ("11", "false"), ("0", "false")],
            hint="Both parts must hold at once — combine them with &&.",
        ),
        ex(
            "boolean_logic-div3or5", "Divisible by 3 or 5",
            "Replace `____` so `hit` is true when x is divisible by 3 or by 5 (or both).",
            prog(
                "        int x = sc.nextInt();\n"
                "        boolean hit = (x % 3 == 0) || (x % 5 == 0);\n"
                "        System.out.println(hit);"),
            ["(x % 3 == 0) || (x % 5 == 0)"],
            [("9", "true"), ("10", "true"), ("7", "false"), ("15", "true")],
            hint="Either condition is enough — combine them with ||.",
        ),
        ex(
            "boolean_logic-not-even", "Flip a boolean",
            "`even` is already computed. Replace `____` so `odd` is its logical opposite using `!`.",
            prog(
                "        int x = sc.nextInt();\n"
                "        boolean even = (x % 2 == 0);\n"
                "        boolean odd = !even;\n"
                "        System.out.println(odd);"),
            ["!even"],
            [("7", "true"), ("4", "false"), ("0", "false")],
            hint="! flips a boolean: !even is true when even is false.",
        ),
    ],
    "overflow": [
        ex(
            "overflow-sum-long", "Sum without overflow",
            "`a + b` can exceed the `int` range and wrap to a wrong value. Replace `____` so `sum` is computed in `long`.",
            prog(
                "        int a = sc.nextInt();\n"
                "        int b = sc.nextInt();\n"
                "        long sum = (long) a + b;\n"
                "        System.out.println(sum);"),
            ["(long) a + b"],
            [("2000000000 2000000000", "4000000000"), ("1 2", "3"),
             ("2147483647 1", "2147483648")],
            hint="Promote the maths to long before it overflows: (long) a + b.",
        ),
        ex(
            "overflow-product", "Product without overflow",
            "Two ints can multiply past the `int` limit. Replace `____` so `product` is the correct `long`.",
            prog(
                "        int a = sc.nextInt();\n"
                "        int b = sc.nextInt();\n"
                "        long product = (long) a * b;\n"
                "        System.out.println(product);"),
            ["(long) a * b"],
            [("100000 100000", "10000000000"), ("46341 46341", "2147488281"), ("3 4", "12")],
            hint="Cast one factor first so the multiply happens in long: (long) a * b.",
        ),
        ex(
            "overflow-factorial", "Factorial that fits",
            "13! already overflows `int`. Replace `____` so the running factorial `f` is a `long` (correct up to 20!).",
            prog(
                "        int n = sc.nextInt();\n"
                "        long f = 1;\n"
                "        for (int i = 2; i <= n; i++) {\n"
                "            f *= i;\n"
                "        }\n"
                "        System.out.println(f);"),
            ["long f = 1;"],
            [("13", "6227020800"), ("20", "2432902008176640000"), ("5", "120")],
            hint="Declare f as long (starting at 1) so it can hold the huge product.",
        ),
    ],
    # -- Arrays -----------------------------------------------------------
    "array_patterns": [
        ex(
            "patterns-kadane", "Contiguous max sum (Kadane)",
            "Signal: *\"contiguous subarray with the largest sum\"* → **Kadane**. At each index, the best subarray ending here either extends the previous one or restarts at the current element. Replace `____` with that choice.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        long cur = a[0], best = a[0];\n"
                "        for (int i = 1; i < n; i++) {\n"
                "            cur = Math.max(a[i], cur + a[i]);\n"
                "            best = Math.max(best, cur);\n"
                "        }\n"
                "        System.out.println(best);"),
            ["cur = Math.max(a[i], cur + a[i]);"],
            [("9\n-2 1 -3 4 -1 2 1 -5 4", "6"), ("3\n-5 -2 -8", "-2"), ("4\n1 2 3 4", "10")],
            hint="Extend or restart: cur = max(a[i], cur + a[i]). Then track best separately.",
            source_slug="maximum-subarray",
        ),
        ex(
            "patterns-counting", "Most frequent value (counting array)",
            "Signal: *\"count occurrences\"* with small integer values (0–100) → a **counting array**. Replace `____` to tally each value into `cnt` indexed by the value itself.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int[] cnt = new int[101];\n"
                "        for (int x : a) cnt[x]++;\n"
                "        int best = 0, mode = 0;\n"
                "        for (int v = 0; v <= 100; v++) {\n"
                "            if (cnt[v] > best) { best = cnt[v]; mode = v; }\n"
                "        }\n"
                "        System.out.println(mode);"),
            ["for (int x : a) cnt[x]++;"],
            [("5\n1 2 2 3 2", "2"), ("3\n5 5 1", "5"), ("1\n42", "42")],
            hint="Use the value as the index: cnt[x]++ for each x.",
        ),
        ex(
            "patterns-majority", "Majority element (Boyer–Moore)",
            "Signal: *\"element that appears more than n/2 times\"* → **Boyer–Moore voting**. Keep a candidate and a counter; matches add 1, mismatches subtract 1, and a zero counter adopts the next value. Replace `____` with the vote step.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int cand = a[0], count = 0;\n"
                "        for (int x : a) {\n"
                "            if (count == 0) cand = x;\n"
                "            count += (x == cand) ? 1 : -1;\n"
                "        }\n"
                "        System.out.println(cand);"),
            ["count += (x == cand) ? 1 : -1;"],
            [("5\n3 3 4 2 3", "3"), ("3\n1 1 1", "1"), ("7\n5 5 5 5 1 2 3", "5")],
            hint="Same as candidate → +1, otherwise −1: count += (x == cand) ? 1 : -1;",
        ),
    ],
    "iteration": [
        ex(
            "iteration-sum", "Sum in one pass",
            "Read `n` then `n` integers, and add each to a running total. Replace `____` so `sum` accumulates every element.",
            prog(
                "        int n = sc.nextInt();\n"
                "        long sum = 0;\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            int x = sc.nextInt();\n"
                "            sum += x;\n"
                "        }\n"
                "        System.out.println(sum);"),
            ["sum += x;"],
            [("4\n1 2 3 4", "10"), ("1\n5", "5"), ("3\n-1 -2 -3", "-6")],
            hint="Add the current element to the accumulator each pass: sum += x;",
            source_slug="array-sum",
        ),
        ex(
            "iteration-max", "Maximum element",
            "`best` starts at `a[0]`. Replace `____` so a single pass leaves `best` holding the largest value.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int best = a[0];\n"
                "        for (int i = 1; i < n; i++) {\n"
                "            if (a[i] > best) best = a[i];\n"
                "        }\n"
                "        System.out.println(best);"),
            ["if (a[i] > best) best = a[i];"],
            [("4\n3 9 2 7", "9"), ("3\n-5 -1 -9", "-1"), ("1\n42", "42")],
            hint="Update only when the current element beats the best so far.",
        ),
        ex(
            "iteration-count-above", "Count above a threshold",
            "Input is `n t` then `n` values. Replace `____` to count how many values are strictly greater than `t`.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int t = sc.nextInt();\n"
                "        int count = 0;\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            int x = sc.nextInt();\n"
                "            if (x > t) count++;\n"
                "        }\n"
                "        System.out.println(count);"),
            ["if (x > t) count++;"],
            [("4 5\n3 6 1 9", "2"), ("3 0\n-1 -2 -3", "0"), ("3 0\n1 2 3", "3")],
            hint="Increment count whenever x > t.",
        ),
        ex(
            "iteration-argmax", "Index of the maximum",
            "Track the *index* of the largest element seen. Replace `____` so `bi` ends at the position of the first maximum.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int bi = 0;\n"
                "        for (int i = 1; i < n; i++) {\n"
                "            if (a[i] > a[bi]) bi = i;\n"
                "        }\n"
                "        System.out.println(bi);"),
            ["if (a[i] > a[bi]) bi = i;"],
            [("4\n3 9 2 7", "1"), ("3\n5 5 1", "0"), ("5\n1 2 3 2 3", "2")],
            hint="Compare against a[bi] and move bi only on a strict improvement (keeps the first max).",
        ),
    ],
    "prefix_max": [
        ex(
            "prefix-running-sum", "Running (prefix) sums",
            "Print each prefix total: after reading `[1,2,3,4]` print `1 3 6 10`. Replace `____` so `run` accumulates as you go.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        long run = 0;\n"
                "        StringBuilder sb = new StringBuilder();\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            run += a[i];\n"
                "            sb.append(run);\n"
                "            if (i < n - 1) sb.append(' ');\n"
                "        }\n"
                "        System.out.println(sb.toString());"),
            ["run += a[i];"],
            [("4\n1 2 3 4", "1 3 6 10"), ("3\n5 0 5", "5 5 10"), ("1\n7", "7")],
            hint="Each prefix total is the previous total plus the current element: run += a[i];",
        ),
        ex(
            "prefix-range-sum", "Range sum with a prefix array",
            "Build a size `n+1` prefix array, then answer the query `l r` (inclusive, 0-based) in O(1). Replace `____` so `pre` is the array of prefix sums.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        long[] pre = new long[n + 1];\n"
                "        for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];\n"
                "        int l = sc.nextInt(), r = sc.nextInt();\n"
                "        System.out.println(pre[r + 1] - pre[l]);"),
            ["pre[i + 1] = pre[i] + a[i];"],
            [("5\n1 2 3 4 5\n1 3", "9"), ("3\n10 20 30\n0 2", "60"), ("4\n5 5 5 5\n2 2", "5")],
            hint="pre[i+1] = pre[i] + a[i]; then sum of a[l..r] is pre[r+1] - pre[l].",
        ),
        ex(
            "prefix-running-max", "Running maximum",
            "Print the max of every prefix: `[3,1,4,1,5]` → `3 3 4 4 5`. Replace `____` so `best` tracks the largest value so far.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int best = a[0];\n"
                "        StringBuilder sb = new StringBuilder();\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            best = Math.max(best, a[i]);\n"
                "            sb.append(best);\n"
                "            if (i < n - 1) sb.append(' ');\n"
                "        }\n"
                "        System.out.println(sb.toString());"),
            ["best = Math.max(best, a[i]);"],
            [("5\n3 1 4 1 5", "3 3 4 4 5"), ("3\n5 4 3", "5 5 5"), ("1\n9", "9")],
            hint="best = Math.max(best, a[i]); before appending it.",
        ),
        ex(
            "prefix-best-profit", "Best buy-low sell-high",
            "Prices come in time order; find the max `price[j] - price[i]` with `i < j` (0 if never profitable). Replace `____` so `best` uses the cheapest price seen so far.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int minSoFar = a[0], best = 0;\n"
                "        for (int i = 1; i < n; i++) {\n"
                "            best = Math.max(best, a[i] - minSoFar);\n"
                "            minSoFar = Math.min(minSoFar, a[i]);\n"
                "        }\n"
                "        System.out.println(best);"),
            ["best = Math.max(best, a[i] - minSoFar);"],
            [("6\n7 1 5 3 6 4", "5"), ("5\n7 6 4 3 1", "0"), ("2\n1 5", "4")],
            hint="Selling today earns a[i] - minSoFar; keep the best of those.",
        ),
    ],
    "two_pointers": [
        ex(
            "twoptr-pair-sum", "Pair sum in a sorted array",
            "The array is **sorted**. Decide whether any two elements sum to `target`, converging from both ends. Replace `____` with the move when the current sum is too small.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int target = sc.nextInt();\n"
                "        int lo = 0, hi = n - 1;\n"
                "        boolean found = false;\n"
                "        while (lo < hi) {\n"
                "            int s = a[lo] + a[hi];\n"
                "            if (s == target) { found = true; break; }\n"
                "            else if (s < target) lo++;\n"
                "            else hi--;\n"
                "        }\n"
                "        System.out.println(found ? \"yes\" : \"no\");"),
            ["else if (s < target) lo++;"],
            [("5\n1 2 4 7 11\n9", "yes"), ("4\n1 2 3 4\n100", "no"), ("3\n-3 0 3\n0", "yes")],
            hint="Too small a sum? You need a bigger value, so raise the low pointer: lo++.",
        ),
        ex(
            "twoptr-palindrome", "Is the array a palindrome?",
            "Compare elements from both ends moving inward. Replace `____` with the mismatch check that fails fast.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int i = 0, j = n - 1;\n"
                "        boolean ok = true;\n"
                "        while (i < j) {\n"
                "            if (a[i] != a[j]) { ok = false; break; }\n"
                "            i++;\n"
                "            j--;\n"
                "        }\n"
                "        System.out.println(ok);"),
            ["if (a[i] != a[j]) { ok = false; break; }"],
            [("3\n1 2 1", "true"), ("4\n1 2 2 1", "true"), ("3\n1 2 3", "false")],
            hint="If the mirrored pair differs, it is not a palindrome: if (a[i] != a[j]) ...",
        ),
        ex(
            "twoptr-move-zeros", "Move zeros to the end",
            "Push every non-zero to the front in order, then pad with zeros — the slow/fast write pattern. Replace `____` so kept elements are written at `w`.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int w = 0;\n"
                "        for (int r = 0; r < n; r++) {\n"
                "            if (a[r] != 0) { a[w] = a[r]; w++; }\n"
                "        }\n"
                "        while (w < n) { a[w] = 0; w++; }\n"
                "        StringBuilder sb = new StringBuilder();\n"
                "        for (int i = 0; i < n; i++) { sb.append(a[i]); if (i < n - 1) sb.append(' '); }\n"
                "        System.out.println(sb.toString());"),
            ["if (a[r] != 0) { a[w] = a[r]; w++; }"],
            [("5\n0 1 0 3 12", "1 3 12 0 0"), ("3\n0 0 0", "0 0 0"), ("3\n1 2 3", "1 2 3")],
            hint="Write only non-zeros and advance the write index: a[w] = a[r]; w++.",
        ),
        ex(
            "twoptr-dedupe-sorted", "Count uniques in a sorted array",
            "The array is sorted, so duplicates are adjacent. Replace `____` with the test that keeps only the first copy of each value; print the unique count `w`.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int w = 0;\n"
                "        for (int r = 0; r < n; r++) {\n"
                "            if (r == 0 || a[r] != a[r - 1]) { a[w] = a[r]; w++; }\n"
                "        }\n"
                "        System.out.println(w);"),
            ["if (r == 0 || a[r] != a[r - 1])"],
            [("5\n1 1 2 2 3", "3"), ("4\n1 2 3 4", "4"), ("3\n5 5 5", "1")],
            hint="Keep a[r] when it is the first element or differs from its predecessor.",
        ),
    ],
    "sliding_window": [
        ex(
            "window-maxsum-k", "Max sum of a size-k window",
            "Fixed window: after the first `k` elements, slide by adding the entering element and dropping the one that left. Replace `____` with that slide step.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int k = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        long sum = 0;\n"
                "        for (int i = 0; i < k; i++) sum += a[i];\n"
                "        long best = sum;\n"
                "        for (int r = k; r < n; r++) {\n"
                "            sum += a[r] - a[r - k];\n"
                "            best = Math.max(best, sum);\n"
                "        }\n"
                "        System.out.println(best);"),
            ["sum += a[r] - a[r - k];"],
            [("5 2\n1 3 -1 5 2", "7"), ("3 3\n1 2 3", "6"), ("4 1\n4 1 3 2", "4")],
            hint="Add the new element, subtract the one k positions back: sum += a[r] - a[r-k].",
        ),
        ex(
            "window-longest-atmost", "Longest window with sum ≤ S",
            "Values are non-negative. Grow the window right; when the sum exceeds `S`, shrink from the left. Replace `____` with the shrink loop.",
            prog(
                "        int n = sc.nextInt();\n"
                "        long S = sc.nextLong();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        long sum = 0; int left = 0, best = 0;\n"
                "        for (int r = 0; r < n; r++) {\n"
                "            sum += a[r];\n"
                "            while (sum > S) { sum -= a[left]; left++; }\n"
                "            best = Math.max(best, r - left + 1);\n"
                "        }\n"
                "        System.out.println(best);"),
            ["while (sum > S) { sum -= a[left]; left++; }"],
            [("5 3\n2 1 1 1 1", "3"), ("3 100\n1 2 3", "3"), ("3 0\n1 2 3", "0")],
            hint="Shrink while the invariant is broken: while (sum > S) { sum -= a[left]; left++; }",
        ),
        ex(
            "window-min-atleast", "Shortest window with sum ≥ S",
            "Non-negative values. Whenever the window sum reaches `S`, record its length and shrink. Replace `____` with the length update. Print 0 if impossible.",
            prog(
                "        int n = sc.nextInt();\n"
                "        long S = sc.nextLong();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        long sum = 0; int left = 0, best = Integer.MAX_VALUE;\n"
                "        for (int r = 0; r < n; r++) {\n"
                "            sum += a[r];\n"
                "            while (sum >= S) {\n"
                "                best = Math.min(best, r - left + 1);\n"
                "                sum -= a[left];\n"
                "                left++;\n"
                "            }\n"
                "        }\n"
                "        System.out.println(best == Integer.MAX_VALUE ? 0 : best);"),
            ["best = Math.min(best, r - left + 1);"],
            [("6 7\n2 3 1 2 4 3", "2"), ("3 100\n1 2 3", "0"), ("3 6\n1 2 3", "3")],
            hint="Window length is r - left + 1; keep the smallest that still satisfies sum ≥ S.",
        ),
    ],
    "inplace_reverse": [
        ex(
            "reverse-array", "Reverse in place",
            "Swap symmetric elements moving inward — no second array. Replace `____` with the three-line swap of `a[i]` and `a[j]`.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int i = 0, j = n - 1;\n"
                "        while (i < j) {\n"
                "            int t = a[i]; a[i] = a[j]; a[j] = t;\n"
                "            i++;\n"
                "            j--;\n"
                "        }\n"
                "        StringBuilder sb = new StringBuilder();\n"
                "        for (int k = 0; k < n; k++) { sb.append(a[k]); if (k < n - 1) sb.append(' '); }\n"
                "        System.out.println(sb.toString());"),
            ["int t = a[i]; a[i] = a[j]; a[j] = t;"],
            [("4\n1 2 3 4", "4 3 2 1"), ("1\n7", "7"), ("3\n5 6 7", "7 6 5")],
            hint="Classic swap via a temp: int t = a[i]; a[i] = a[j]; a[j] = t;",
        ),
        ex(
            "reverse-subrange", "Reverse a sub-range",
            "Reverse only `a[l..r]` (inclusive), leaving the rest untouched. Replace `____` with the swap of the current ends.",
            prog(
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        int l = sc.nextInt(), r = sc.nextInt();\n"
                "        while (l < r) {\n"
                "            int t = a[l]; a[l] = a[r]; a[r] = t;\n"
                "            l++;\n"
                "            r--;\n"
                "        }\n"
                "        StringBuilder sb = new StringBuilder();\n"
                "        for (int k = 0; k < n; k++) { sb.append(a[k]); if (k < n - 1) sb.append(' '); }\n"
                "        System.out.println(sb.toString());"),
            ["int t = a[l]; a[l] = a[r]; a[r] = t;"],
            [("5\n1 2 3 4 5\n1 3", "1 4 3 2 5"), ("3\n1 2 3\n0 2", "3 2 1"), ("4\n1 2 3 4\n2 2", "1 2 3 4")],
            hint="Swap a[l] and a[r], then step l forward and r backward.",
        ),
        ex(
            "reverse-rotate", "Rotate right by k (three reversals)",
            "Rotate the array right by `k` using the reversal trick: reverse all, reverse the first k, reverse the rest. The `rev` helper is written. Replace `____` with the two partial reversals.",
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    static void rev(int[] a, int i, int j) {\n"
            "        while (i < j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }\n"
            "    }\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = sc.nextInt();\n"
            "        int[] a = new int[n];\n"
            "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
            "        int k = sc.nextInt() % n;\n"
            "        rev(a, 0, n - 1);\n"
            "        rev(a, 0, k - 1);\n"
            "        rev(a, k, n - 1);\n"
            "        StringBuilder sb = new StringBuilder();\n"
            "        for (int i = 0; i < n; i++) { sb.append(a[i]); if (i < n - 1) sb.append(' '); }\n"
            "        System.out.println(sb.toString());\n"
            "    }\n"
            "}\n",
            ["rev(a, 0, k - 1);\n        rev(a, k, n - 1);"],
            [("5\n1 2 3 4 5\n2", "4 5 1 2 3"), ("3\n1 2 3\n0", "1 2 3"), ("4\n1 2 3 4\n5", "4 1 2 3")],
            hint="After reversing the whole array, reverse a[0..k-1] and a[k..n-1].",
            source_slug="rotate-array",
        ),
    ],
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
            "language": c.get("language", "java"),
            "lesson": LESSONS.get(key, ""),
            "exercises": EXERCISES.get(key, []),
            "cards": c.get("cards", []),
            "quiz": c.get("quiz", []),
            "practice": c.get("practice", []),
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
    "Simulation": "Simulation",
    "Grid": "Grid / Matrix",
    "Matrix": "Grid / Matrix",
    "Neighbors": "Grid / Matrix",
    "State Machine": "Simulation",
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


# --- More reference implementations (second expansion batch) ---

def _count_digits(n):
    return len(str(abs(n)))


def _missing_number(nums):
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)


def _fizzbuzz(n):
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)


def _two_sum_sorted(nums, target):
    l, r = 0, len(nums) - 1
    while l < r:
        s = nums[l] + nums[r]
        if s == target:
            return [l + 1, r + 1]
        if s < target:
            l += 1
        else:
            r -= 1
    return [-1]


def _merge_sorted(a, b):
    i = j = 0
    out2 = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out2.append(a[i]); i += 1
        else:
            out2.append(b[j]); j += 1
    out2.extend(a[i:])
    out2.extend(b[j:])
    return out2


def _gcd_array(nums):
    g = nums[0]
    for x in nums[1:]:
        g = math.gcd(g, x)
    return g


def _fast_power(base, exp):
    result = 1
    b = base
    e = exp
    while e > 0:
        if e & 1:
            result *= b
        b *= b
        e >>= 1
    return result


def _unique_paths(m, n):
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]
    return dp[n - 1]


def _lcs(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = dp[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1] else max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def _top_k_frequent(nums, k):
    c = Counter(nums)
    ordered = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))
    return [v for v, _ in ordered[:k]]


def _count_bits(n):
    return [bin(i).count("1") for i in range(n + 1)]


def _largest_rectangle(heights):
    st = []
    best = 0
    for i, h in enumerate(heights + [0]):
        while st and heights[st[-1]] >= h:
            top = st.pop()
            width = i if not st else i - st[-1] - 1
            best = max(best, heights[top] * width)
        st.append(i)
    return best


def _window_max(nums, k):
    dq = deque()
    out2 = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out2.append(nums[dq[0]])
    return out2


def _jump_ii(nums):
    if len(nums) <= 1:
        return 0
    jumps = 0
    cur_end = 0
    farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = farthest
    return jumps


def _longest_valid_parens(s):
    st = [-1]
    best = 0
    for i, ch in enumerate(s):
        if ch == "(":
            st.append(i)
        else:
            st.pop()
            if not st:
                st.append(i)
            else:
                best = max(best, i - st[-1])
    return best


def _min_window_len(s, t):
    if not t or not s:
        return 0
    need = Counter(t)
    missing = len(t)
    l = 0
    best = math.inf
    for r, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:
            best = min(best, r - l + 1)
            need[s[l]] += 1
            if need[s[l]] > 0:
                missing += 1
            l += 1
    return 0 if best == math.inf else best


HARNESS_DEFS += [
    # ---------------- INTRO ----------------
    dict(slug="min-of-two", title="Min of Two", difficulty="Intro", topics=["Basics"], subtopics=["Conditionals"], companies=["Amazon"],
         description="Return the smaller of two integers.",
         constraints="-10^9 ≤ a, b ≤ 10^9",
         hints=["Compare the two values.", "Return whichever is not larger."],
         opt=("O(1)", "O(1)", "A single comparison."),
         spec={"name": "solve", "params": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}], "returns": "int"},
         fn=lambda a, b: min(a, b),
         cases=[("example", "Example", (3, 8)), ("example", "Negatives", (-2, -9)), ("hidden", "Equal", (5, 5)), ("hidden", "Zero", (0, -1))],
         example_expl=["3 < 8.", "-9 is smaller."]),
    dict(slug="cube-number", title="Cube", difficulty="Intro", topics=["Basics", "Math"], subtopics=["Arithmetic"], companies=["Microsoft"],
         description="Return the cube (n³) of the integer.",
         constraints="-10^4 ≤ n ≤ 10^4",
         hints=["Multiply n by itself three times.", "Use a 64-bit return type."],
         opt=("O(1)", "O(1)", "Two multiplications."),
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "long"},
         fn=lambda n: n * n * n,
         cases=[("example", "Example", (3,)), ("example", "Negative", (-2,)), ("hidden", "Zero", (0,)), ("hidden", "Larger", (100,))],
         example_expl=["3³ = 27.", "(-2)³ = -8."]),
    dict(slug="is-multiple", title="Is Multiple", difficulty="Intro", topics=["Math"], subtopics=["Number Theory"], companies=["Adobe"],
         description="Return `true` if `a` is a multiple of `b` (b ≠ 0).",
         constraints="1 ≤ b ≤ 10^9\n0 ≤ a ≤ 10^9",
         hints=["A is a multiple of b when the remainder is zero.", "Use the modulo operator."],
         opt=("O(1)", "O(1)", "One modulo test."),
         spec={"name": "solve", "params": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}], "returns": "bool"},
         fn=lambda a, b: b != 0 and a % b == 0,
         cases=[("example", "Multiple", (12, 3)), ("example", "Not", (10, 3)), ("hidden", "Zero dividend", (0, 5)), ("hidden", "Self", (7, 7))],
         example_expl=["12 = 4·3.", "10 mod 3 = 1."]),
    dict(slug="count-digits", title="Count Digits", difficulty="Intro", topics=["Math"], subtopics=["Digits"], companies=["Amazon"],
         description="Return how many decimal digits a non-negative integer has (0 has one digit).",
         constraints="0 ≤ n ≤ 10^9",
         hints=["Divide by 10 repeatedly and count.", "Or take the length of the string form."],
         opt=("O(log n)", "O(1)", "One pass over the digits."),
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "int"},
         fn=lambda n: _count_digits(n),
         cases=[("example", "Example", (12345,)), ("example", "Single", (7,)), ("hidden", "Zero", (0,)), ("hidden", "Round", (1000,))],
         example_expl=["Five digits.", "One digit."]),
    dict(slug="array-maximum", title="Array Maximum", difficulty="Intro", topics=["Arrays"], subtopics=["Traversal"], companies=["Microsoft"],
         description="Return the largest element of a non-empty array.",
         constraints="1 ≤ n ≤ 10^5",
         hints=["Track a running maximum as you scan."],
         opt=("O(n)", "O(1)", "Single pass tracking the max."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: max(nums),
         cases=[("example", "Example", ([3, 1, 4, 1, 5],)), ("example", "Negatives", ([-2, -9, -1],)), ("hidden", "Single", ([42],)), ("hidden", "Sorted", ([1, 2, 3],))],
         example_expl=["5 is largest.", "-1 is largest."]),

    # ---------------- EASY ----------------
    dict(slug="reverse-integer", title="Reverse Integer", difficulty="Easy", topics=["Math"], subtopics=["Digits"], companies=["Amazon", "Bloomberg"],
         description="Return the integer with its digits reversed, preserving sign (assume the result fits in 32 bits).",
         constraints="-2^31 ≤ n ≤ 2^31 − 1",
         hints=["Peel digits off with % 10 and build the reverse.", "Track the sign separately.", "Trailing zeros vanish (120 → 21)."],
         opt=("O(log n)", "O(1)", "One pass over the digits."),
         editorial="Pop the last digit with %10 and push it onto an accumulator (acc = acc*10 + digit); reapply the sign.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "int"},
         fn=lambda n: _reverse_int(n),
         cases=[("example", "Positive", (123,)), ("example", "Negative", (-380,)), ("hidden", "Palindrome", (121,)), ("hidden", "Single", (5,))],
         example_expl=["321.", "-83 (trailing zero dropped)."]),
    dict(slug="power-of-two", title="Power of Two", difficulty="Easy", topics=["Bit Manipulation", "Math"], subtopics=["Bit Manipulation"], companies=["Apple", "Amazon"],
         description="Return `true` if the integer is a power of two.",
         constraints="-2^31 ≤ n ≤ 2^31 − 1",
         hints=["Powers of two have exactly one set bit.", "n & (n-1) clears the lowest set bit.", "Positive numbers only."],
         opt=("O(1)", "O(1)", "Single bit trick: n>0 and n&(n-1)==0."),
         editorial="A positive power of two has a single 1 bit, so n & (n−1) removes it and yields 0.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "bool"},
         fn=lambda n: n > 0 and (n & (n - 1)) == 0,
         cases=[("example", "Yes", (16,)), ("example", "No", (18,)), ("hidden", "One", (1,)), ("hidden", "Zero", (0,)), ("hidden", "Negative", (-8,))],
         example_expl=["16 = 2⁴.", "18 is not a power of two."]),
    dict(slug="missing-number", title="Missing Number", difficulty="Easy", topics=["Arrays", "Math"], subtopics=["XOR"], companies=["Amazon", "Microsoft"],
         description="An array holds n distinct numbers from the range [0, n]. Return the one that's missing.",
         constraints="1 ≤ n ≤ 10^5\nValues are distinct and in [0, n].",
         hints=["The full range has a known sum: n(n+1)/2.", "Subtract the actual sum.", "XOR also works and avoids overflow."],
         opt=("O(n)", "O(1)", "Expected-sum minus actual-sum (or XOR)."),
         editorial="The sum 0+…+n is n(n+1)/2; subtract the array's sum to reveal the gap. XOR of indices and values also isolates it.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: _missing_number(nums),
         cases=[("example", "Example", ([3, 0, 1],)), ("example", "Missing last", ([0, 1, 2],)), ("hidden", "Single", ([1],)), ("hidden", "Missing first", ([1, 2],))],
         example_expl=["2 is missing.", "3 is missing."]),
    dict(slug="count-negatives", title="Count Negatives", difficulty="Easy", topics=["Arrays"], subtopics=["Counting"], companies=["Amazon"],
         description="Return how many elements are negative.",
         constraints="0 ≤ n ≤ 10^5",
         hints=["Scan once and count values below zero."],
         opt=("O(n)", "O(1)", "Single pass."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: sum(1 for x in nums if x < 0),
         cases=[("example", "Example", ([-1, 2, -3, 4],)), ("example", "None", ([1, 2, 3],)), ("hidden", "All", ([-1, -2],)), ("hidden", "Empty", ([],))],
         example_expl=["-1 and -3 → 2.", "No negatives."]),
    dict(slug="is-sorted", title="Is Sorted", difficulty="Easy", topics=["Arrays"], subtopics=["Traversal"], companies=["Adobe"],
         description="Return `true` if the array is sorted in non-decreasing order.",
         constraints="0 ≤ n ≤ 10^5",
         hints=["Every element should be ≤ the next.", "One violation is enough to fail.", "Empty and single arrays are sorted."],
         opt=("O(n)", "O(1)", "Single adjacent-pair scan."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "bool"},
         fn=lambda nums: all(nums[i] <= nums[i + 1] for i in range(len(nums) - 1)),
         cases=[("example", "Sorted", ([1, 2, 2, 3],)), ("example", "Not", ([3, 1, 2],)), ("hidden", "Single", ([5],)), ("hidden", "Empty", ([],))],
         example_expl=["Non-decreasing.", "3 > 1 breaks order."]),
    dict(slug="fizzbuzz-value", title="FizzBuzz Value", difficulty="Easy", topics=["Math"], subtopics=["Conditionals"], companies=["Amazon", "Microsoft"],
         description="Return \"FizzBuzz\" if n is divisible by 15, \"Fizz\" if by 3, \"Buzz\" if by 5, otherwise the number as a string.",
         constraints="1 ≤ n ≤ 10^6",
         hints=["Check divisibility by 15 first.", "Then 3, then 5.", "Otherwise return the number itself."],
         opt=("O(1)", "O(1)", "A few modulo checks."),
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "string"},
         fn=lambda n: _fizzbuzz(n),
         cases=[("example", "Fizz", (9,)), ("example", "FizzBuzz", (15,)), ("hidden", "Buzz", (10,)), ("hidden", "Plain", (7,))],
         example_expl=["9 divisible by 3 → Fizz.", "15 divisible by both → FizzBuzz."]),
    dict(slug="two-sum-sorted", title="Two Sum II (sorted)", difficulty="Easy", topics=["Two Pointers", "Arrays"], subtopics=["Two Pointers"], companies=["Amazon", "Google"],
         description="Given a sorted array with exactly one solution, return the 1-based indices of the two numbers adding to `target`.",
         constraints="2 ≤ n ≤ 10^4\nArray is sorted ascending; exactly one answer.",
         hints=["Exploit the sorted order.", "Two pointers from both ends adjust based on the sum.", "Move left up if the sum is too small, right down if too big."],
         opt=("O(n)", "O(1)", "Converging two pointers on a sorted array."),
         editorial="With the array sorted, converge two pointers: if the pair sum is below target move left up, if above move right down.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}], "returns": "int[]"},
         fn=lambda nums, target: _two_sum_sorted(nums, target),
         cases=[("example", "Example", ([2, 7, 11, 15], 9)), ("example", "Ends", ([1, 2, 3, 6], 7)), ("hidden", "Adjacent", ([1, 4, 5], 9)), ("hidden", "Small", ([0, 3], 3))],
         example_expl=["2+7 at indices 1,2.", "1+6 at indices 1,4."]),

    # ---------------- MEDIUM ----------------
    dict(slug="merge-sorted-arrays", title="Merge Two Sorted Arrays", difficulty="Medium", topics=["Arrays", "Two Pointers"], subtopics=["Two Pointers"], companies=["Amazon", "Microsoft"],
         description="Merge two sorted arrays into one sorted array and return it.",
         constraints="0 ≤ |a|, |b| ≤ 10^5",
         hints=["Walk both arrays with two indices.", "Always take the smaller current head.", "Append the leftover tail."],
         opt=("O(m+n)", "O(m+n)", "Two-pointer merge (the merge step of merge sort)."),
         editorial="Advance two pointers, emitting the smaller front element each step, then append whichever array remains.",
         spec={"name": "solve", "params": [{"name": "a", "type": "int[]"}, {"name": "b", "type": "int[]"}], "returns": "int[]"},
         fn=lambda a, b: _merge_sorted(a, b),
         cases=[("example", "Example", ([1, 3, 5], [2, 4, 6])), ("example", "One empty", ([], [1, 2])), ("hidden", "Overlap", ([1, 2, 3], [2, 3, 4])), ("hidden", "Both single", ([5], [1]))],
         example_expl=["1,2,3,4,5,6.", "1,2."]),
    dict(slug="kth-smallest", title="Kth Smallest Element", difficulty="Medium", topics=["Sorting", "Heap"], subtopics=["Sorting"], companies=["Amazon", "Bloomberg"],
         description="Return the kth smallest element (1-indexed, k valid).",
         constraints="1 ≤ k ≤ n ≤ 10^5",
         hints=["Sorting is the simplest approach.", "A size-k max-heap works too.", "Quickselect gives average O(n)."],
         opt=("O(n log n)", "O(1)", "Sort ascending and index (heap/quickselect improve it)."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}], "returns": "int"},
         fn=lambda nums, k: sorted(nums)[k - 1],
         cases=[("example", "Example", ([3, 2, 1, 5, 4], 2)), ("example", "Dupes", ([2, 2, 1, 3], 3)), ("hidden", "First", ([9], 1)), ("hidden", "Max", ([1, 2, 3], 3))],
         example_expl=["2nd smallest is 2.", "3rd smallest is 2."]),
    dict(slug="gcd-of-array", title="GCD of Array", difficulty="Medium", topics=["Math"], subtopics=["Number Theory"], companies=["Bloomberg"],
         description="Return the greatest common divisor of all elements in a non-empty array.",
         constraints="1 ≤ n ≤ 10^5\n1 ≤ a[i] ≤ 10^9",
         hints=["gcd is associative: fold it across the array.", "Use the Euclidean algorithm for each pair.", "The running gcd only shrinks."],
         opt=("O(n·log max)", "O(1)", "Fold pairwise gcd across the array."),
         editorial="gcd(a,b,c,…) = gcd(gcd(a,b),c,…); accumulate a running gcd using the Euclidean algorithm.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: _gcd_array(nums),
         cases=[("example", "Example", ([12, 18, 24],)), ("example", "Coprime", ([7, 5],)), ("hidden", "Single", ([9],)), ("hidden", "Multiples", ([4, 8, 16],))],
         example_expl=["gcd is 6.", "Coprime → 1."]),
    dict(slug="fast-power", title="Fast Power", difficulty="Medium", topics=["Math", "Recursion"], subtopics=["Recurrence"], companies=["Google", "Amazon"],
         description="Compute base^exp for a non-negative exponent using fast exponentiation.",
         constraints="0 ≤ exp ≤ 40\n-100 ≤ base ≤ 100 (result fits in 64 bits)",
         hints=["Squaring halves the exponent each step.", "Multiply in the base only on odd bits.", "This is O(log exp), not O(exp)."],
         opt=("O(log exp)", "O(1)", "Exponentiation by squaring."),
         editorial="Binary exponentiation: while exp>0, if the low bit is set multiply the base into the result, then square the base and shift.",
         spec={"name": "solve", "params": [{"name": "base", "type": "int"}, {"name": "exp", "type": "int"}], "returns": "long"},
         fn=lambda base, exp: _fast_power(base, exp),
         cases=[("example", "Example", (2, 10)), ("example", "Zero exp", (5, 0)), ("hidden", "Base one", (1, 40)), ("hidden", "Negative base", (-2, 3))],
         example_expl=["2¹⁰ = 1024.", "Anything⁰ = 1."]),
    dict(slug="unique-paths", title="Unique Paths", difficulty="Medium", topics=["Dynamic Programming"], subtopics=["2D DP"], companies=["Amazon", "Bloomberg"],
         description="A robot moves only right or down on an m×n grid from the top-left to the bottom-right. Return how many distinct paths exist.",
         constraints="1 ≤ m, n ≤ 100",
         hints=["Paths to a cell = paths from above + paths from the left.", "The first row and column each have exactly one path.", "A single rolling row of size n suffices."],
         opt=("O(m·n)", "O(n)", "Grid DP with a rolling row."),
         editorial="dp[j] += dp[j-1] across m rows starting from all-ones — each cell sums the paths from above and from the left.",
         spec={"name": "solve", "params": [{"name": "m", "type": "int"}, {"name": "n", "type": "int"}], "returns": "int"},
         fn=lambda m, n: _unique_paths(m, n),
         cases=[("example", "Example", (3, 7)), ("example", "Square", (3, 3)), ("hidden", "Row", (1, 5)), ("hidden", "Small", (2, 2))],
         example_expl=["28 paths on a 3×7 grid.", "6 paths on a 3×3 grid."]),
    dict(slug="longest-common-subsequence", title="Longest Common Subsequence", difficulty="Medium", topics=["Dynamic Programming", "Strings"], subtopics=["2D DP"], companies=["Amazon", "Google", "Adobe"],
         description="Return the length of the longest subsequence common to both strings (characters in order, not necessarily contiguous).",
         constraints="0 ≤ |a|, |b| ≤ 1000",
         hints=["Compare prefixes of the two strings.", "If the last characters match, extend the diagonal; else take the better of dropping one.", "It's a classic 2-D DP table."],
         opt=("O(m·n)", "O(m·n)", "2-D DP over prefixes of both strings."),
         editorial="dp[i][j] = dp[i-1][j-1]+1 when a[i-1]==b[j-1], else max(dp[i-1][j], dp[i][j-1]).",
         spec={"name": "solve", "params": [{"name": "a", "type": "string"}, {"name": "b", "type": "string"}], "returns": "int"},
         fn=lambda a, b: _lcs(a, b),
         cases=[("example", "Example", ("abcde", "ace")), ("example", "None", ("abc", "def")), ("hidden", "Equal", ("abc", "abc")), ("hidden", "Interleaved", ("abcbdab", "bdcab"))],
         example_expl=["'ace' → 3.", "No common subsequence → 0."]),
    dict(slug="top-k-frequent", title="Top K Frequent Elements", difficulty="Medium", topics=["Hashing", "Heap", "Sorting"], subtopics=["Counting"], companies=["Amazon", "Meta"],
         description="Return the k most frequent values, ordered by frequency descending and, for ties, by value ascending.",
         constraints="1 ≤ k ≤ number of distinct values",
         hints=["Count occurrences with a hash map.", "Order by (−count, value) to make ties deterministic.", "A heap of size k avoids a full sort."],
         opt=("O(n log n)", "O(n)", "Count, then order by frequency (heap or sort)."),
         editorial="Tally counts, then sort the distinct values by descending count (ascending value on ties) and take the first k.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}], "returns": "int[]"},
         fn=lambda nums, k: _top_k_frequent(nums, k),
         cases=[("example", "Example", ([1, 1, 1, 2, 2, 3], 2)), ("example", "Tie", ([4, 4, 5, 5, 6], 2)), ("hidden", "All distinct", ([3, 1, 2], 2)), ("hidden", "Single", ([7, 7], 1))],
         example_expl=["1 (×3), 2 (×2) → 1 2.", "Ties broken by value → 4 5."]),
    dict(slug="count-bits", title="Counting Bits", difficulty="Medium", topics=["Bit Manipulation", "Dynamic Programming"], subtopics=["Bit Manipulation"], companies=["Amazon", "Apple"],
         description="Return an array where out[i] is the number of set bits in i, for i from 0 to n.",
         constraints="0 ≤ n ≤ 10^5",
         hints=["popcount(i) = popcount(i>>1) + (i & 1).", "Or popcount(i) = popcount(i & (i-1)) + 1.", "Build the table bottom-up."],
         opt=("O(n)", "O(n)", "DP: popcount(i) = popcount(i>>1) + (i&1)."),
         editorial="Each number's bit count is its half's count plus its lowest bit: dp[i] = dp[i>>1] + (i&1).",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "int[]"},
         fn=lambda n: _count_bits(n),
         cases=[("example", "To 5", (5,)), ("example", "To 2", (2,)), ("hidden", "Zero", (0,)), ("hidden", "To 8", (8,))],
         example_expl=["0,1,1,2,1,2.", "0,1,1."]),

    # ---------------- HARD ----------------
    dict(slug="largest-rectangle-histogram", title="Largest Rectangle in Histogram", difficulty="Hard", topics=["Stack", "Arrays"], subtopics=["Monotonic Stack"], companies=["Amazon", "Google"],
         description="Given bar heights of width 1, return the area of the largest rectangle that fits within the histogram.",
         constraints="0 ≤ n ≤ 10^5\n0 ≤ height ≤ 10^9",
         hints=["For each bar, how far left and right can it extend at its own height?", "A monotonic increasing stack finds the bounds in O(n).", "Pop when a shorter bar appears and settle the popped bar's rectangle."],
         opt=("O(n)", "O(n)", "Monotonic stack of increasing bar indices."),
         editorial="Keep a stack of increasing heights; when a shorter bar arrives, pop and compute each popped bar's maximal width (bounded by the new bar and the stack's previous index).",
         spec={"name": "solve", "params": [{"name": "heights", "type": "int[]"}], "returns": "long"},
         fn=lambda heights: _largest_rectangle(heights),
         cases=[("example", "Example", ([2, 1, 5, 6, 2, 3],)), ("example", "Increasing", ([1, 2, 3, 4],)), ("hidden", "Flat", ([3, 3, 3],)), ("hidden", "Single", ([5],))],
         example_expl=["5 and 6 form area 10.", "Bars 3,4 → 6."]),
    dict(slug="sliding-window-maximum", title="Sliding Window Maximum", difficulty="Hard", topics=["Stack", "Arrays"], subtopics=["Monotonic Stack"], companies=["Amazon", "Google", "Meta"],
         description="Return the maximum of every contiguous window of size k as it slides across the array.",
         constraints="1 ≤ k ≤ n ≤ 10^5",
         hints=["A monotonic decreasing deque of indices holds candidates.", "Drop indices that fall out of the window from the front.", "Drop smaller values from the back before adding a new one."],
         opt=("O(n)", "O(k)", "Monotonic deque of indices."),
         editorial="Maintain a deque of indices with decreasing values; the front is always the window max. Evict out-of-window indices and pop smaller tails.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}], "returns": "int[]"},
         fn=lambda nums, k: _window_max(nums, k),
         cases=[("example", "Example", ([1, 3, -1, -3, 5, 3, 6, 7], 3)), ("example", "k=1", ([4, 2, 12], 1)), ("hidden", "Whole", ([2, 1, 3], 3)), ("hidden", "Increasing", ([1, 2, 3, 4], 2))],
         example_expl=["3,3,5,5,6,7.", "Each element is its own window."]),
    dict(slug="jump-game-ii", title="Jump Game II (min jumps)", difficulty="Hard", topics=["Arrays", "Greedy"], subtopics=["Greedy"], companies=["Amazon", "Meta"],
         description="Each value is the max jump length from that index. Return the fewest jumps to reach the last index (always reachable).",
         constraints="1 ≤ n ≤ 10^4",
         hints=["Think in levels: the range reachable with j jumps.", "Extend a 'current end' greedily to the farthest reachable.", "Bump the jump count when you cross the current end."],
         opt=("O(n)", "O(1)", "Greedy BFS-by-levels over reachable ranges."),
         editorial="Track the farthest reach and the current level's end; each time i hits the end, take a jump and extend the end to farthest.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: _jump_ii(nums),
         cases=[("example", "Example", ([2, 3, 1, 1, 4],)), ("example", "Single", ([0],)), ("hidden", "Two", ([1, 1],)), ("hidden", "Big first", ([5, 1, 1, 1, 1],))],
         example_expl=["2 jumps: index 0→1→4.", "Already at the end → 0."]),
    dict(slug="longest-valid-parentheses", title="Longest Valid Parentheses", difficulty="Hard", topics=["Stack", "Strings", "Dynamic Programming"], subtopics=["Monotonic Stack"], companies=["Amazon", "Google"],
         description="Return the length of the longest substring of well-formed parentheses.",
         constraints="0 ≤ |s| ≤ 10^5\ns contains only '(' and ')'.",
         hints=["A stack of indices marks unmatched positions.", "Seed the stack with -1 as a base.", "On ')', pop; the gap to the new stack top is a valid length."],
         opt=("O(n)", "O(n)", "Index stack tracking the last unmatched boundary."),
         editorial="Push indices of '('; on ')', pop and measure i minus the new top (the last unmatched boundary). Reset the boundary when the stack empties.",
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}], "returns": "int"},
         fn=lambda s: _longest_valid_parens(s),
         cases=[("example", "Example", ("(()",)), ("example", "Longer", (")()())",)), ("hidden", "Empty", ("",)), ("hidden", "All open", ("(((",))],
         example_expl=["'()' → 2.", "'()()' → 4."]),
    dict(slug="min-window-length", title="Minimum Window Substring (length)", difficulty="Hard", topics=["Sliding Window", "Strings", "Hashing"], subtopics=["Sliding Window"], companies=["Amazon", "Meta", "Google"],
         description="Return the length of the shortest substring of s that contains every character of t (with multiplicity), or 0 if none.",
         constraints="1 ≤ |s|, |t| ≤ 10^5",
         hints=["Expand a window until it covers all of t.", "Then shrink from the left while it still covers t.", "Track counts of needed characters."],
         opt=("O(|s|)", "O(|t|)", "Sliding window with a 'missing count'."),
         editorial="Grow the right edge tracking how many required characters are still missing; when zero, shrink the left edge to find the minimal covering window.",
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}, {"name": "t", "type": "string"}], "returns": "int"},
         fn=lambda s, t: _min_window_len(s, t),
         cases=[("example", "Example", ("ADOBECODEBANC", "ABC")), ("example", "None", ("a", "aa")), ("hidden", "Whole", ("abc", "cba")), ("hidden", "Single", ("aa", "a"))],
         example_expl=["'BANC' → 4.", "Impossible → 0."]),
]


# ---------------------------------------------------------------------------
# Extend the concept catalog + prerequisites so EVERY problem is fully explained.
# ---------------------------------------------------------------------------

CONCEPTS.update({
    "bit_manip": {
        "name": "Bit Manipulation",
        "what": "Operating on the individual binary bits of an integer with AND, OR, XOR, and shifts.",
        "deep": "Bit tricks give O(1) tools that replace loops: `x & (x-1)` clears the lowest set bit, `x & -x` isolates it, XOR cancels equal values, and shifting multiplies or divides by powers of two. They shine in set membership (bitmasks), parity, and counting.",
        "java": "Use &, |, ^, ~, <<, >>, and >>> (unsigned shift). Integer.bitCount(x) counts set bits; x & (x-1) drops the lowest one.",
    },
    "prefix_sum": {
        "name": "Prefix Sums",
        "what": "Precomputed running totals so any range sum is a single subtraction.",
        "deep": "Build P[i] = a[0]+…+a[i-1]; then the sum of a[l..r] is P[r+1] − P[l] in O(1). Paired with a hash map of seen prefixes it counts subarrays with a target sum in one pass. The same idea extends to prefix XOR, products, and 2-D grids.",
        "java": "A long[] prefix of length n+1, or a running long combined with a HashMap<Long,Integer> of prefix counts.",
    },
})
CATEGORY.update({"bit_manip": "Foundations", "prefix_sum": "Arrays"})

# Prerequisites for every function-harness problem: (concept_key, why-it-helps-here).
PREREQS.update({
    "two-sum-fn": [("complement", "For each x, look up target − x instead of scanning all pairs."), ("hashing", "A hash map makes that complement lookup O(1)."), ("iteration", "One left-to-right pass records indices as you go.")],
    "max-subarray-fn": [("dp", "Carry the best sum ending at the current index."), ("iteration", "A single sweep updates the running and global best."), ("greedy", "Drop a negative running sum — it can never help a later subarray.")],
    "reverse-array-fn": [("two_pointers", "Swap the ends and move inward."), ("iteration", "Or build the result from back to front in one pass.")],
    "is-palindrome-fn": [("two_pointers", "Compare characters from both ends moving inward."), ("string_basics", "Index into the string and compare characters.")],
    "is-even": [("modulo", "Even means the remainder mod 2 is zero."), ("conditionals", "Return a boolean from the comparison.")],
    "absolute-value": [("conditionals", "Negatives flip sign; others stay."), ("arithmetic", "Negate when below zero.")],
    "max-of-three": [("conditionals", "Chain comparisons to find the largest."), ("variables", "Hold the running best in a variable.")],
    "square-number": [("arithmetic", "Multiply the number by itself."), ("overflow", "Use a 64-bit type so large squares don't wrap.")],
    "sum-of-digits": [("math_digits", "Peel digits with % 10 and // 10."), ("modulo", "The remainder mod 10 is the last digit.")],
    "factorial": [("loops_basic", "Multiply a running product from 1 to n."), ("overflow", "Factorials grow fast — use a 64-bit accumulator.")],
    "count-evens": [("iteration", "Scan once, testing each element."), ("modulo", "Even is remainder-zero mod 2.")],
    "array-minimum": [("iteration", "Track a running minimum across one pass.")],
    "array-maximum": [("iteration", "Track a running maximum across one pass.")],
    "contains-duplicate": [("hashing", "A set answers 'seen before?' in O(1)."), ("visited_set", "Insert values and detect a repeat.")],
    "single-number": [("bit_manip", "XOR cancels equal pairs, leaving the loner."), ("iteration", "Fold the whole array with XOR.")],
    "majority-element": [("hashing", "Counts of each value reveal the majority (or use voting)."), ("iteration", "Boyer-Moore keeps one candidate in a single pass.")],
    "is-prime": [("number_theory", "A prime has no divisor up to its square root."), ("loops_basic", "Trial-divide from 2 to √n.")],
    "count-primes": [("number_theory", "Cross out multiples with a sieve."), ("iteration", "Sweep and mark composites.")],
    "valid-anagram": [("hashing", "Compare character frequency maps."), ("canonical", "Sorting both strings is a canonical form."), ("sorting", "Equal anagrams sort to identical strings.")],
    "first-unique-char": [("hashing", "Count characters first."), ("iteration", "Then scan for the first count of one.")],
    "move-zeroes": [("two_pointers", "A write pointer packs the non-zeros."), ("iteration", "Fill the remaining slots with zeroes.")],
    "running-sum": [("prefix_sum", "Each output is the prefix total so far."), ("iteration", "Accumulate as you scan.")],
    "max-consecutive-ones": [("iteration", "Track current and best run lengths."), ("variables", "Reset the current run on a zero.")],
    "second-largest": [("iteration", "Track the top two distinct values."), ("sorting", "Or sort the distinct values and take the runner-up.")],
    "count-occurrences": [("iteration", "Scan once and count matches.")],
    "number-of-1-bits": [("bit_manip", "Check the low bit and shift, or use x & (x-1)."), ("loops_basic", "Loop over the bits.")],
    "product-except-self": [("prefix_sum", "Prefix products left, suffix products right (multiplicative)."), ("iteration", "Two passes combine into the answer.")],
    "best-time-buy-sell": [("greedy", "Best profit is price minus the lowest price seen."), ("iteration", "Track the running minimum in one pass."), ("dp", "It's a one-state DP over 'min so far'.")],
    "container-most-water": [("two_pointers", "The shorter wall limits the area — move it inward."), ("greedy", "Advancing the taller wall can never increase the area.")],
    "house-robber": [("dp", "Choose to rob or skip each house."), ("recurrence", "best[i] = max(best[i-1], best[i-2] + nums[i]).")],
    "jump-game": [("greedy", "Track the furthest index you can reach."), ("iteration", "If your position outruns the reach, you're stuck.")],
    "coin-change": [("dp", "Build the fewest coins for every amount up to the target."), ("recurrence", "dp[a] = 1 + min(dp[a - coin]).")],
    "coin-change-ways": [("dp", "Count combinations for each amount."), ("recurrence", "Iterate coins outermost so order doesn't create duplicates.")],
    "longest-common-prefix": [("string_basics", "Compare characters position by position."), ("iteration", "Shrink a candidate prefix across all words.")],
    "search-insert-position": [("binary_search", "Lower-bound search finds the slot in O(log n)."), ("big_o", "Halving the range beats a linear scan.")],
    "integer-sqrt": [("binary_search", "Search the largest m with m·m ≤ x."), ("overflow", "Squaring m can overflow — use a wide type or compare carefully.")],
    "min-cost-climbing-stairs": [("dp", "Cheapest way to reach each step."), ("recurrence", "dp[i] = cost[i] + min(dp[i-1], dp[i-2]).")],
    "daily-temperatures": [("stack", "A monotonic stack of indices awaits a warmer day."), ("iteration", "Pop and record the day gap when a warmer day arrives.")],
    "next-greater-element": [("stack", "Pending indices wait on a decreasing stack."), ("iteration", "Resolve them when a larger value appears.")],
    "subarray-sum-k": [("prefix_sum", "A range sum of k means two prefixes differ by k."), ("hashing", "Count prefix sums in a map."), ("complement", "For prefix s, add the count of earlier prefixes equal to s − k.")],
    "longest-consecutive": [("hashing", "A set gives O(1) membership for neighbours."), ("visited_set", "Only start counting at sequence starts.")],
    "kth-largest-element": [("sorting", "Sort descending and index."), ("heap", "A size-k min-heap avoids a full sort.")],
    "rotate-array-right": [("inplace_reverse", "Three reversals rotate in O(1) space."), ("iteration", "Reduce k modulo n first.")],
    "word-break": [("dp", "Can the prefix of length i be segmented?"), ("hashing", "A set makes dictionary lookups O(1)."), ("string_basics", "Test substrings against the dictionary.")],
    "decode-ways": [("dp", "Ways to decode each prefix."), ("recurrence", "Add one- and two-digit extensions."), ("string_basics", "Read one or two characters at a time.")],
    "longest-palindrome-length": [("two_pointers", "Expand outward from each center."), ("string_basics", "Match characters around a center.")],
    "maximum-product-subarray": [("dp", "Carry both max and min products — a negative flips them."), ("iteration", "Update the answer each step.")],
    "partition-equal-subset-sum": [("dp", "Reduce to a subset summing to total/2."), ("recurrence", "0/1 knapsack over reachable subset sums.")],
    # --- second expansion batch ---
    "min-of-two": [("conditionals", "Return whichever value is not larger.")],
    "cube-number": [("arithmetic", "Multiply the number by itself twice."), ("overflow", "Use a 64-bit return type.")],
    "is-multiple": [("modulo", "A multiple leaves remainder zero."), ("number_theory", "Divisibility is a remainder test.")],
    "count-digits": [("math_digits", "Divide by 10 repeatedly, counting steps."), ("loops_basic", "Loop until the number reaches zero.")],
    "reverse-integer": [("math_digits", "Peel the last digit with % 10 and push it onto an accumulator."), ("overflow", "Guard against exceeding the 32-bit range.")],
    "power-of-two": [("bit_manip", "Powers of two have a single set bit: n & (n-1) == 0."), ("conditionals", "Reject non-positive numbers.")],
    "missing-number": [("prefix_sum", "The full range sum minus the actual sum is the gap."), ("bit_manip", "XOR of indices and values also isolates it."), ("iteration", "One pass sums the array.")],
    "count-negatives": [("iteration", "Scan once, counting values below zero.")],
    "is-sorted": [("iteration", "Check every adjacent pair in one pass."), ("boolean_logic", "One violation makes the whole answer false.")],
    "fizzbuzz-value": [("modulo", "Divisibility drives the branch."), ("conditionals", "Test 15 before 3 and 5.")],
    "two-sum-sorted": [("two_pointers", "Converge from both ends of the sorted array."), ("iteration", "Adjust a pointer based on whether the sum is too big or small.")],
    "merge-sorted-arrays": [("two_pointers", "Advance the pointer with the smaller head."), ("sorting", "This is the merge step of merge sort.")],
    "kth-smallest": [("sorting", "Sort ascending and index."), ("heap", "A size-k max-heap works in O(n log k).")],
    "gcd-of-array": [("number_theory", "gcd is associative — fold it pairwise."), ("recursion", "The Euclidean algorithm reduces each pair.")],
    "fast-power": [("recursion", "Squaring halves the exponent each step."), ("bit_manip", "Multiply in the base only on set bits of the exponent."), ("overflow", "Results grow quickly — use a wide type.")],
    "unique-paths": [("dp", "Paths to a cell sum the paths from above and left."), ("dp2d", "A grid DP, reducible to one rolling row.")],
    "longest-common-subsequence": [("dp2d", "A 2-D table over prefixes of both strings."), ("recurrence", "Match extends the diagonal; mismatch takes the better neighbour.")],
    "top-k-frequent": [("hashing", "Tally counts with a map."), ("heap", "A size-k heap surfaces the most frequent."), ("sorting", "Order by (−count, value) for deterministic ties.")],
    "count-bits": [("bit_manip", "dp[i] = dp[i>>1] + (i & 1)."), ("dp", "Reuse the already-computed count of i/2.")],
    "largest-rectangle-histogram": [("stack", "A monotonic increasing stack finds each bar's span."), ("iteration", "Settle rectangles as shorter bars arrive.")],
    "sliding-window-maximum": [("stack", "A monotonic deque keeps window candidates."), ("sliding_window", "The window slides one step at a time, evicting stale indices.")],
    "jump-game-ii": [("greedy", "Extend the reachable range level by level."), ("bfs", "Each jump is a BFS level over indices.")],
    "longest-valid-parentheses": [("stack", "Indices of unmatched positions bound valid runs."), ("dp", "Or a DP over ends of valid substrings.")],
    "min-window-length": [("sliding_window", "Grow to cover t, then shrink to minimise."), ("hashing", "Track required character counts."), ("two_pointers", "Left and right edges define the window.")],
})


# ---------------------------------------------------------------------------
# Grid / simulation problems (2-D stdin/stdout) — implementation-heavy and
# beginner-friendly. NOT harness problems (the harness is 1-D): each reads a
# board from stdin and prints a board or a short answer. Reference solutions
# compute the expected outputs.
# ---------------------------------------------------------------------------

def sol_color_bomb(inp):
    L = inp.rstrip("\n").split("\n")
    H, W = map(int, L[0].split())
    g = [L[1 + i] for i in range(H)]
    painted = [[False] * W for _ in range(H)]
    for bi in range(H):
        for bj in range(W):
            if g[bi][bj].isdigit():
                D = int(g[bi][bj])
                for i in range(H):
                    for j in range(W):
                        if abs(i - bi) + abs(j - bj) <= D:
                            painted[i][j] = True
    return "\n".join("".join("#" if painted[i][j] else "." for j in range(W)) for i in range(H))


def sol_territory(inp):
    L = inp.rstrip("\n").split("\n")
    Q = int(L[1])
    state = {}  # (x,y) -> 1 A, 2 B, 3 lockedA, 4 lockedB; absent = neutral
    for t in range(Q):
        p, xs, ys = L[2 + t].split()
        k = (int(xs), int(ys))
        s = state.get(k, 0)
        if s in (3, 4):
            continue
        if p == "A":
            state[k] = {0: 1, 2: 0, 1: 3}[s]
        else:
            state[k] = {0: 2, 1: 0, 2: 4}[s]
    a = sum(1 for v in state.values() if v in (1, 3))
    b = sum(1 for v in state.values() if v in (2, 4))
    return "A" if a > b else "B" if b > a else "Draw"


def sol_minesweeper(inp):
    L = inp.rstrip("\n").split("\n")
    H, W = map(int, L[0].split())
    g = [L[1 + i] for i in range(H)]
    res = []
    for i in range(H):
        row = []
        for j in range(W):
            if g[i][j] == "*":
                row.append("*")
            else:
                c = 0
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < H and 0 <= nj < W and g[ni][nj] == "*":
                            c += 1
                row.append(str(c))
        res.append("".join(row))
    return "\n".join(res)


def sol_life(inp):
    L = inp.rstrip("\n").split("\n")
    H, W = map(int, L[0].split())
    g = [L[1 + i] for i in range(H)]

    def alive(i, j):
        return 0 <= i < H and 0 <= j < W and g[i][j] == "#"

    res = []
    for i in range(H):
        row = []
        for j in range(W):
            n = sum(alive(i + di, j + dj) for di in (-1, 0, 1) for dj in (-1, 0, 1) if not (di == 0 and dj == 0))
            if g[i][j] == "#":
                row.append("#" if n in (2, 3) else ".")
            else:
                row.append("#" if n == 3 else ".")
        res.append("".join(row))
    return "\n".join(res)


def sol_robot(inp):
    L = inp.rstrip("\n").split("\n")
    H, W = map(int, L[0].split())
    r, c = map(int, L[1].split())
    cmds = L[2] if len(L) > 2 else ""
    r -= 1
    c -= 1
    vis = [[False] * W for _ in range(H)]
    vis[r][c] = True
    delta = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
    for ch in cmds.strip():
        dr, dc = delta.get(ch, (0, 0))
        nr, nc = r + dr, c + dc
        if 0 <= nr < H and 0 <= nc < W:
            r, c = nr, nc
            vis[r][c] = True
    return "\n".join("".join("#" if vis[i][j] else "." for j in range(W)) for i in range(H))


def sol_set_zeroes(inp):
    L = inp.rstrip("\n").split("\n")
    H, W = map(int, L[0].split())
    g = [list(L[1 + i]) for i in range(H)]
    rows, cols = set(), set()
    for i in range(H):
        for j in range(W):
            if g[i][j] == "0":
                rows.add(i)
                cols.add(j)
    for i in range(H):
        for j in range(W):
            if i in rows or j in cols:
                g[i][j] = "0"
    return "\n".join("".join(r) for r in g)


def sol_rotate(inp):
    L = inp.rstrip("\n").split("\n")
    H, W = map(int, L[0].split())
    g = [L[1 + i] for i in range(H)]
    return "\n".join("".join(g[H - 1 - i][j] for i in range(H)) for j in range(W))


def sol_spiral(inp):
    L = inp.rstrip("\n").split("\n")
    H, W = map(int, L[0].split())
    g = [L[1 + i] for i in range(H)]
    top, bottom, left, right = 0, H - 1, 0, W - 1
    res = []
    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            res.append(g[top][j])
        top += 1
        for i in range(top, bottom + 1):
            res.append(g[i][right])
        right -= 1
        if top <= bottom:
            for j in range(right, left - 1, -1):
                res.append(g[bottom][j])
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                res.append(g[i][left])
            left += 1
    return "".join(res)


# Shared starter helpers keep these readable.
_PY_GRID = "import sys\n\ndef solve(H, W, grid):\n    # grid is a list of H strings. TODO: return a list of H output strings.\n    return grid\n\ndata = sys.stdin.read().split('\\n')\nH, W = map(int, data[0].split())\ngrid = [data[1 + i] for i in range(H)]\nfor line in solve(H, W, grid):\n    print(line)\n"
_JS_GRID = "const data = require('fs').readFileSync(0, 'utf8').split('\\n');\nconst [H, W] = data[0].split(' ').map(Number);\nconst grid = [];\nfor (let i = 0; i < H; i++) grid.push(data[1 + i]);\n\nfunction solve(H, W, grid) {\n  // TODO: return an array of H output strings\n  return grid;\n}\n\nconsole.log(solve(H, W, grid).join('\\n'));\n"

GRID_DEFS = [
    dict(
        slug="color-bomb-explosion", title="Color Bomb Explosion", difficulty="Easy",
        topics=["Simulation", "Matrix"], subtopics=["Grid", "Neighbors"], companies=["AtCoder"],
        description=(
            "A board has `H` rows and `W` columns. Each cell is `.` (empty) or a digit `0`–`9`, a **Color Bomb** "
            "whose explosion power equals that digit.\n\n"
            "When a bomb of power `D` explodes it paints every cell within **Manhattan distance** `D` (including its own "
            "cell) with `#`. Bombs explode independently and do not interfere. Initially nothing is painted.\n\n"
            "The Manhattan distance between `(r1,c1)` and `(r2,c2)` is `|r1−r2| + |c1−c2|`.\n\n"
            "### Input\n- Line 1: `H W`.\n- Next `H` lines: the board, each a string of length `W`.\n\n"
            "### Output\nPrint `H` lines: `#` if a cell is painted by at least one bomb, otherwise `.`"
        ),
        constraints="1 ≤ H, W ≤ 70\nEach character is `.` or a digit 0–9.",
        hints=[
            "Handle each bomb independently — there's no interaction to track.",
            "For a bomb at (bi,bj) with power D, scan every cell and paint it if |i−bi|+|j−bj| ≤ D.",
            "Keep a separate H×W boolean 'painted' grid; a cell stays painted if ANY bomb reaches it.",
            "With H,W ≤ 70 even checking every cell for every bomb (~24M ops) is fast enough.",
        ],
        opt=("O((H·W)^2)", "O(H·W)", "For each bomb, sweep the whole board and mark cells within its Manhattan radius; the small bound makes the brute force comfortably fast."),
        editorial=(
            "## Approach\nCollect nothing fancy — just simulate. Keep a `painted[H][W]` boolean grid, initially all false. "
            "For every cell that holds a digit `D`, loop over the whole board and set `painted[i][j] = true` wherever "
            "`|i−bi| + |j−bj| ≤ D`. A cell can be reached by several bombs; once painted it stays painted. Finally print "
            "`#`/`.` from the boolean grid. Because H,W ≤ 70, the O((H·W)²) double sweep is only a few million operations."
        ),
        ref=sol_color_bomb,
        starter_py=_PY_GRID, starter_js=_JS_GRID,
        cases=[
            ("example", "Example 1", "5 5\n0..0.\n.2..0\n.....\n....1\n.0...\n"),
            ("example", "Example 2", "7 7\n...0...\n.......\n...1...\n..131..\n...1...\n.......\n...0...\n"),
            ("hidden", "Single power-0 bomb", "1 1\n0\n"),
            ("hidden", "No bombs", "2 3\n...\n...\n"),
            ("hidden", "Corner reach", "3 3\n2..\n...\n...\n"),
        ],
        example_expl=[
            "Six bombs paint the shown cells; the power-2 bomb at (1,1) covers a diamond of radius 2.",
            "The central chain of bombs paints a large diamond.",
        ],
    ),
    dict(
        slug="territory-capture", title="Territory Capture Game", difficulty="Easy",
        topics=["Simulation"], subtopics=["State Machine", "Grid"], companies=["AtCoder"],
        description=(
            "Players **A** and **B** play on an `N × M` grid; every cell starts **neutral**. Over `Q` turns a player tries "
            "to capture a cell:\n\n"
            "- **Neutral cell** → becomes that player's territory.\n"
            "- **Opponent's cell** → becomes neutral.\n"
            "- **Your own cell** → becomes **locked** (permanently yours).\n"
            "- **Locked cell** → never changes again, whoever tries.\n\n"
            "After all turns, output who owns more cells.\n\n"
            "### Input\n- Line 1: `N M`.\n- Line 2: `Q`.\n- Next `Q` lines: `P x y` — player (`A`/`B`), row `x` (1-indexed), column `y` (1-indexed).\n\n"
            "### Output\n`A` if A owns more cells, `B` if B owns more, otherwise `Draw`."
        ),
        constraints="1 ≤ N, M ≤ 100\n1 ≤ Q ≤ 100\n1 ≤ x ≤ N, 1 ≤ y ≤ M",
        hints=[
            "Give each cell a state code: neutral, owned-by-A, owned-by-B, locked-A, locked-B.",
            "Process turns in order; a locked cell ignores every later move.",
            "Translate each rule into a precise transition based on (current state, acting player).",
            "At the end, count owned + locked cells for each player and compare.",
        ],
        opt=("O(Q + N·M)", "O(N·M)", "Each turn is O(1) state update; a final O(N·M) pass counts ownership."),
        editorial=(
            "## Approach\nPure simulation. Store each cell's state as a small integer: 0 neutral, 1 A, 2 B, 3 locked-A, "
            "4 locked-B. For each move, if the cell is locked do nothing; otherwise apply the rule for the acting player "
            "(neutral→owned, opponent→neutral, own→locked). After the turns, count states {1,3} for A and {2,4} for B and "
            "print A / B / Draw. Nothing here needs cleverness — the skill is turning the rules into exact transitions and "
            "respecting 1-indexed input."
        ),
        ref=sol_territory,
        starter_py="import sys\n\ndef solve(N, M, moves):\n    # moves is a list of (player, x, y). TODO: return 'A', 'B', or 'Draw'.\n    return 'Draw'\n\ndata = sys.stdin.read().split('\\n')\nN, M = map(int, data[0].split())\nQ = int(data[1])\nmoves = []\nfor i in range(Q):\n    p, x, y = data[2 + i].split()\n    moves.append((p, int(x), int(y)))\nprint(solve(N, M, moves))\n",
        starter_js="const data = require('fs').readFileSync(0, 'utf8').split('\\n');\nconst [N, M] = data[0].split(' ').map(Number);\nconst Q = Number(data[1]);\nconst moves = [];\nfor (let i = 0; i < Q; i++) {\n  const [p, x, y] = data[2 + i].split(' ');\n  moves.push([p, Number(x), Number(y)]);\n}\nfunction solve(N, M, moves) {\n  // TODO: return 'A', 'B', or 'Draw'\n  return 'Draw';\n}\nconsole.log(solve(N, M, moves));\n",
        cases=[
            ("example", "Example 1", "2 2\n4\nA 1 2\nA 1 1\nB 1 1\nB 1 2\n"),
            ("example", "Example 2", "3 3\n10\nA 3 2\nB 3 1\nA 3 3\nB 2 2\nB 2 2\nA 2 1\nB 1 2\nA 3 3\nA 3 1\nA 1 2\n"),
            ("hidden", "Lock then attack", "1 1\n3\nA 1 1\nA 1 1\nB 1 1\n"),
            ("hidden", "Single A capture", "2 2\n1\nA 1 1\n"),
        ],
        example_expl=[
            "A takes two cells, then B neutralises both → 0 vs 0 → Draw.",
            "A ends up owning more cells after the sequence of captures and locks.",
        ],
    ),
    dict(
        slug="minesweeper-counts", title="Minesweeper Counts", difficulty="Easy",
        topics=["Simulation", "Matrix"], subtopics=["Grid", "Neighbors"], companies=["Bloomberg"],
        description=(
            "You're given a Minesweeper board with `*` for mines and `.` for empty cells. Produce the revealed board: "
            "keep each mine as `*`, and replace each empty cell with the number of mines among its **8 neighbours** "
            "(horizontal, vertical, and diagonal).\n\n"
            "### Input\n- Line 1: `H W`.\n- Next `H` lines: the board of `*` and `.`\n\n"
            "### Output\nThe revealed board: `*` stays, empty cells become a digit `0`–`8`."
        ),
        constraints="1 ≤ H, W ≤ 100",
        hints=[
            "Mines are printed unchanged.",
            "For an empty cell, look at up to 8 neighbours using offset pairs.",
            "Bounds-check every neighbour before reading it (0 ≤ ni < H and 0 ≤ nj < W).",
            "Count the mines and print that single digit.",
        ],
        opt=("O(H·W)", "O(H·W)", "Each cell inspects a constant 8 neighbours."),
        editorial=(
            "## Approach\nFor every cell: if it's a mine, output `*`. Otherwise, iterate the 8 offsets `(di,dj)` with "
            "`di,dj ∈ {-1,0,1}` excluding `(0,0)`, guard the indices against the border, and count neighbouring `*`. "
            "Output that count. A tidy trick is to keep `int[] dr = {-1,-1,-1,0,0,1,1,1}` and `int[] dc = {-1,0,1,-1,1,-1,0,1}`."
        ),
        ref=sol_minesweeper,
        starter_py=_PY_GRID, starter_js=_JS_GRID,
        cases=[
            ("example", "Example 1", "3 4\n*...\n..*.\n....\n"),
            ("example", "Example 2", "2 2\n**\n**\n"),
            ("hidden", "No mines", "2 3\n...\n...\n"),
            ("hidden", "Single mine", "3 3\n...\n.*.\n...\n"),
        ],
        example_expl=[
            "Each empty cell shows how many of its 8 neighbours are mines.",
            "Every cell is a mine, so all stay `*`.",
        ],
    ),
    dict(
        slug="robot-grid-walk", title="Robot Grid Walk", difficulty="Easy",
        topics=["Simulation"], subtopics=["Grid", "State Machine"], companies=["Amazon"],
        description=(
            "A robot stands on an `H × W` grid at a start cell and follows a string of moves: `U` (up), `D` (down), "
            "`L` (left), `R` (right). A move that would leave the grid is **ignored** (the robot stays put). Mark every "
            "cell the robot ever occupies — including the start — with `#`, and print the board.\n\n"
            "### Input\n- Line 1: `H W`.\n- Line 2: `r c` — the 1-indexed start cell.\n- Line 3: the move string (may be empty).\n\n"
            "### Output\nThe `H × W` board: `#` for visited cells, `.` otherwise."
        ),
        constraints="1 ≤ H, W ≤ 100\n0 ≤ |moves| ≤ 10^5",
        hints=[
            "Track the robot's current (row, col); mark it visited to start.",
            "Map each command to a (dr, dc) delta.",
            "Only apply a move if the destination is inside the grid.",
            "Mark each newly-occupied cell visited.",
        ],
        opt=("O(H·W + |moves|)", "O(H·W)", "One pass over the moves plus printing the board."),
        editorial=(
            "## Approach\nConvert to 0-indexed, mark the start visited, and walk the command string. For each command look "
            "up its delta, compute the next cell, and move only if it's in bounds — otherwise stay. Mark every cell you "
            "land on. Print `#`/`.` from the visited grid. The one subtlety is that off-grid moves are skipped, not clamped "
            "to the border in a way that still marks a new cell."
        ),
        ref=sol_robot,
        starter_py="import sys\n\ndef solve(H, W, r, c, cmds):\n    # r,c are 1-indexed. TODO: return a list of H strings of '#'/'.'\n    return ['.' * W for _ in range(H)]\n\ndata = sys.stdin.read().split('\\n')\nH, W = map(int, data[0].split())\nr, c = map(int, data[1].split())\ncmds = data[2] if len(data) > 2 else ''\nfor line in solve(H, W, r, c, cmds):\n    print(line)\n",
        starter_js="const data = require('fs').readFileSync(0, 'utf8').split('\\n');\nconst [H, W] = data[0].split(' ').map(Number);\nconst [r, c] = data[1].split(' ').map(Number);\nconst cmds = data[2] || '';\nfunction solve(H, W, r, c, cmds) {\n  // r,c are 1-indexed. TODO: return an array of H strings\n  return Array.from({length: H}, () => '.'.repeat(W));\n}\nconsole.log(solve(H, W, r, c, cmds).join('\\n'));\n",
        cases=[
            ("example", "Example 1", "3 3\n2 2\nUURRDD\n"),
            ("example", "Example 2", "2 2\n1 1\nRRDD\n"),
            ("hidden", "No moves", "2 2\n1 1\n\n"),
            ("hidden", "Bounces off wall", "1 3\n1 1\nLLLRR\n"),
        ],
        example_expl=[
            "The robot traces a path from the centre; off-grid steps are ignored.",
            "From the corner it visits the right column then the bottom-right.",
        ],
    ),
    dict(
        slug="game-of-life-step", title="Game of Life (One Step)", difficulty="Medium",
        topics=["Simulation", "Matrix"], subtopics=["Grid", "Neighbors"], companies=["Google", "Amazon"],
        description=(
            "Conway's Game of Life on an `H × W` board: `#` is a live cell, `.` is dead. Compute the **next** generation, "
            "where all cells update simultaneously based on their 8 neighbours:\n\n"
            "- A live cell with **2 or 3** live neighbours stays live; otherwise it dies.\n"
            "- A dead cell with **exactly 3** live neighbours becomes live.\n\n"
            "### Input\n- Line 1: `H W`.\n- Next `H` lines: the board of `#` and `.`\n\n"
            "### Output\nThe board after one step."
        ),
        constraints="1 ≤ H, W ≤ 100",
        hints=[
            "Every cell updates from the CURRENT board — read from the old grid, write to a new one.",
            "Count the 8 neighbours with bounds checks.",
            "Live survives on a count of 2 or 3; dead is born on exactly 3.",
            "Don't overwrite cells in place, or later counts will be wrong.",
        ],
        opt=("O(H·W)", "O(H·W)", "Constant neighbour work per cell; a fresh output grid avoids in-place corruption."),
        editorial=(
            "## Approach\nThe classic pitfall is updating in place: because all cells change at once, you must count live "
            "neighbours on the *old* board and write results to a *new* board. For each cell, count live neighbours over the "
            "8 offsets with bounds checks, then apply the rule: a live cell survives with 2–3 neighbours; a dead cell is born "
            "with exactly 3. Print the new board."
        ),
        ref=sol_life,
        starter_py=_PY_GRID, starter_js=_JS_GRID,
        cases=[
            ("example", "Blinker", "3 3\n...\n###\n...\n"),
            ("example", "Block (still life)", "4 4\n....\n.##.\n.##.\n....\n"),
            ("hidden", "All dead", "2 2\n..\n..\n"),
            ("hidden", "Single live dies", "3 3\n...\n.#.\n...\n"),
        ],
        example_expl=[
            "A horizontal blinker becomes a vertical one.",
            "A 2×2 block is stable — it maps to itself.",
        ],
    ),
    dict(
        slug="set-matrix-zeroes", title="Set Matrix Zeroes", difficulty="Medium",
        topics=["Matrix", "Simulation"], subtopics=["Grid"], companies=["Amazon", "Microsoft"],
        description=(
            "You're given an `H × W` grid of single digits (`0`–`9`). If a cell is `0`, set its **entire row and column** to "
            "`0`. Print the resulting grid.\n\n"
            "### Input\n- Line 1: `H W`.\n- Next `H` lines: rows of `W` digits.\n\n"
            "### Output\nThe grid after zeroing every row and column that originally contained a `0`."
        ),
        constraints="1 ≤ H, W ≤ 100\nEach character is a digit 0–9.",
        hints=[
            "Decide which rows/columns to zero BEFORE changing anything.",
            "First pass: record the rows and columns that contain a 0.",
            "Second pass: zero any cell whose row or column was marked.",
            "Zeroing as you go would spread zeros incorrectly.",
        ],
        opt=("O(H·W)", "O(H + W)", "Two passes with a set of zero rows and a set of zero columns."),
        editorial=(
            "## Approach\nThe trap is that zeroing immediately would cascade — a freshly-written 0 would trigger more rows and "
            "columns. So first scan the original grid and record which rows and which columns contain a 0 (two sets). Then scan "
            "again and set a cell to 0 if its row or column is marked. This runs in O(H·W) time and O(H+W) extra space."
        ),
        ref=sol_set_zeroes,
        starter_py=_PY_GRID, starter_js=_JS_GRID,
        cases=[
            ("example", "Example 1", "3 3\n123\n405\n678\n"),
            ("example", "No zeroes", "2 2\n12\n34\n"),
            ("hidden", "Whole row", "2 3\n100\n456\n"),
            ("hidden", "Single zero", "1 1\n0\n"),
        ],
        example_expl=[
            "The 0 at (1,0) blanks its row and column.",
            "No zeroes present, so the grid is unchanged.",
        ],
    ),
    dict(
        slug="rotate-matrix-90", title="Rotate Matrix 90°", difficulty="Medium",
        topics=["Matrix", "Simulation"], subtopics=["Grid"], companies=["Amazon", "Adobe", "Apple"],
        description=(
            "Rotate an `H × W` grid of characters **90° clockwise** and print the result. The rotated board has `W` rows and "
            "`H` columns.\n\n"
            "### Input\n- Line 1: `H W`.\n- Next `H` lines: the grid (any visible characters, no spaces).\n\n"
            "### Output\nThe rotated grid: `W` lines, each of length `H`."
        ),
        constraints="1 ≤ H, W ≤ 100",
        hints=[
            "After a clockwise rotation the first column (bottom-to-top) becomes the first row.",
            "Output row `j` is old column `j` read from the bottom up.",
            "Formula: newGrid[j][i] = oldGrid[H-1-i][j].",
            "Remember the dimensions swap: output is W×H.",
        ],
        opt=("O(H·W)", "O(H·W)", "Emit each rotated cell once."),
        editorial=(
            "## Approach\nA 90° clockwise rotation maps old cell `(i, j)` to new cell `(j, H-1-i)`. Equivalently, build output "
            "row `j` by reading old column `j` from the last row up to the first: `newRow_j = [old[H-1-i][j] for i in 0..H)`. "
            "The output has `W` rows of length `H`."
        ),
        ref=sol_rotate,
        starter_py=_PY_GRID, starter_js=_JS_GRID,
        cases=[
            ("example", "Example 1", "2 3\nabc\ndef\n"),
            ("example", "Square", "3 3\n123\n456\n789\n"),
            ("hidden", "Single row", "1 3\nxyz\n"),
            ("hidden", "Single cell", "1 1\nA\n"),
        ],
        example_expl=[
            "Columns become rows: first output row is 'da' (old column 0 bottom-up).",
            "The 3×3 grid rotates a quarter turn clockwise.",
        ],
    ),
    dict(
        slug="spiral-order", title="Spiral Order", difficulty="Medium",
        topics=["Matrix", "Simulation"], subtopics=["Grid"], companies=["Amazon", "Google", "Microsoft"],
        description=(
            "Read an `H × W` grid of characters in **spiral order** — clockwise starting at the top-left: across the top row, "
            "down the right column, back along the bottom, up the left, then inward — and print all characters on one line.\n\n"
            "### Input\n- Line 1: `H W`.\n- Next `H` lines: the grid (visible characters, no spaces).\n\n"
            "### Output\nA single line: the characters in spiral order, concatenated."
        ),
        constraints="1 ≤ H, W ≤ 100",
        hints=[
            "Track four boundaries: top, bottom, left, right.",
            "Walk right along the top, then down the right, then left along the bottom, then up the left.",
            "Shrink the boundary after finishing each edge.",
            "Guard against re-walking a row/column when the grid is a single line or column.",
        ],
        opt=("O(H·W)", "O(H·W)", "Peel one ring at a time, visiting each cell once."),
        editorial=(
            "## Approach\nKeep four shrinking boundaries `top, bottom, left, right`. Repeatedly: walk left→right along `top` "
            "then `top++`; walk `top→bottom` down `right` then `right--`; if `top ≤ bottom`, walk right→left along `bottom` then "
            "`bottom--`; if `left ≤ right`, walk `bottom→top` up `left` then `left++`. The two guards prevent double-visiting the "
            "middle row/column of odd-shaped grids."
        ),
        ref=sol_spiral,
        starter_py="import sys\n\ndef solve(H, W, grid):\n    # TODO: return the characters in spiral order as one string\n    return ''\n\ndata = sys.stdin.read().split('\\n')\nH, W = map(int, data[0].split())\ngrid = [data[1 + i] for i in range(H)]\nprint(solve(H, W, grid))\n",
        starter_js="const data = require('fs').readFileSync(0, 'utf8').split('\\n');\nconst [H, W] = data[0].split(' ').map(Number);\nconst grid = [];\nfor (let i = 0; i < H; i++) grid.push(data[1 + i]);\nfunction solve(H, W, grid) {\n  // TODO: return the spiral-order characters as one string\n  return '';\n}\nconsole.log(solve(H, W, grid));\n",
        cases=[
            ("example", "Example 1", "3 3\n123\n456\n789\n"),
            ("example", "Wide", "2 4\nabcd\nefgh\n"),
            ("hidden", "Single row", "1 4\nwxyz\n"),
            ("hidden", "Single column", "3 1\na\nb\nc\n"),
        ],
        example_expl=[
            "1 2 3 6 9 8 7 4 5 spiralling inward.",
            "a b c d h g f e around the ring.",
        ],
    ),
]

CONCEPTS.update({
    "grid": {
        "name": "Grid / Matrix Traversal",
        "what": "Walking a 2-D board with nested loops, neighbour offsets, and bounds checks.",
        "deep": "Most grid problems are two nested loops over rows and columns. Neighbours come from offset lists — 4-directional {(-1,0),(1,0),(0,-1),(0,1)} or 8-directional including diagonals — and every access must be bounds-checked (0<=r<H and 0<=c<W). Manhattan distance |r1-r2|+|c1-c2| counts 4-directional steps between two cells.",
        "java": "char[][] or int[][]; loop for(i..H) for(j..W). Keep int[] dr={-1,1,0,0}, dc={0,0,-1,1} for the four neighbours (or all 8) and guard indices before reading.",
    },
    "simulation": {
        "name": "Simulation",
        "what": "Directly modelling a process step by step, exactly as the statement describes, instead of finding a formula.",
        "deep": "When constraints are small, the intended solution is often to just do what the problem says: hold the state, apply each event or rule in order, and read the answer at the end. The skill is translating rules into precise state transitions and handling edge cases and 1- vs 0-indexing carefully.",
        "java": "Model state in an array or a small int/enum code; process events in a loop, updating state per the rules. Watch off-by-one and 1-indexed input.",
    },
})
CATEGORY.update({"grid": "Arrays", "simulation": "Foundations"})

PREREQS.update({
    "color-bomb-explosion": [("grid", "Nested loops over the board plus a Manhattan-distance test decide each cell."), ("simulation", "Model each bomb's blast directly rather than deriving a formula."), ("big_o", "With H,W ≤ 70 the O((H·W)²) brute force is fast enough — no cleverness needed.")],
    "territory-capture": [("simulation", "Model each cell's state and apply each turn's rule in order."), ("conditionals", "Branch on the current owner and the acting player."), ("iteration", "Tally owned and locked cells at the end.")],
    "minesweeper-counts": [("grid", "For each empty cell, count mines among its 8 neighbours."), ("conditionals", "Leave mines untouched; otherwise write the neighbour count."), ("iteration", "Bounds-check every neighbour before reading it.")],
    "robot-grid-walk": [("simulation", "Move the robot command by command, ignoring off-grid steps."), ("grid", "Mark visited cells on the board."), ("conditionals", "Only move when the destination is inside the grid.")],
    "game-of-life-step": [("grid", "Count live neighbours with the 8 offsets and bounds checks."), ("simulation", "Apply the birth/survival rules to produce the next generation."), ("boolean_logic", "Survive on 2–3 neighbours; born on exactly 3 — and read from the old board.")],
    "set-matrix-zeroes": [("grid", "Record which rows and columns hold a 0, then blank them."), ("iteration", "Two passes: find the zeros, then apply."), ("conditionals", "Zero a cell if its row or column was marked.")],
    "rotate-matrix-90": [("grid", "Map each source cell to its rotated position: new[j][i] = old[H-1-i][j]."), ("char_arrays", "Build each rotated row as a sequence of characters."), ("iteration", "Emit the W×H output row by row.")],
    "spiral-order": [("grid", "Peel the board ring by ring."), ("simulation", "Track four shrinking boundaries: top, bottom, left, right."), ("iteration", "Walk right, down, left, and up on each layer.")],
})

JAVA_STARTERS.update({
    "color-bomb-explosion": "import java.util.*;\nimport java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int H = Integer.parseInt(st.nextToken()), W = Integer.parseInt(st.nextToken());\n        char[][] g = new char[H][];\n        for (int i = 0; i < H; i++) g[i] = br.readLine().toCharArray();\n        boolean[][] painted = new boolean[H][W];\n        // TODO: for each digit cell (a bomb of power D), paint cells within Manhattan distance D\n        StringBuilder sb = new StringBuilder();\n        for (int i = 0; i < H; i++) {\n            for (int j = 0; j < W; j++) sb.append(painted[i][j] ? '#' : '.');\n            sb.append('\\n');\n        }\n        System.out.print(sb);\n    }\n}\n",
    "territory-capture": "import java.util.*;\nimport java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int N = Integer.parseInt(st.nextToken()), M = Integer.parseInt(st.nextToken());\n        int Q = Integer.parseInt(br.readLine().trim());\n        int[][] state = new int[N + 1][M + 1]; // 0 neutral,1 A,2 B,3 lockA,4 lockB\n        for (int t = 0; t < Q; t++) {\n            st = new StringTokenizer(br.readLine());\n            String p = st.nextToken();\n            int x = Integer.parseInt(st.nextToken()), y = Integer.parseInt(st.nextToken());\n            // TODO: update state[x][y] per the capture rules\n        }\n        int a = 0, b = 0;\n        // TODO: count cells owned/locked by each player\n        System.out.println(a > b ? \"A\" : b > a ? \"B\" : \"Draw\");\n    }\n}\n",
    "minesweeper-counts": "import java.util.*;\nimport java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int H = Integer.parseInt(st.nextToken()), W = Integer.parseInt(st.nextToken());\n        char[][] g = new char[H][];\n        for (int i = 0; i < H; i++) g[i] = br.readLine().toCharArray();\n        StringBuilder sb = new StringBuilder();\n        for (int i = 0; i < H; i++) {\n            for (int j = 0; j < W; j++) {\n                // TODO: '*' stays '*'; otherwise print the count of neighbouring mines\n                sb.append('.');\n            }\n            sb.append('\\n');\n        }\n        System.out.print(sb);\n    }\n}\n",
    "robot-grid-walk": "import java.util.*;\nimport java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int H = Integer.parseInt(st.nextToken()), W = Integer.parseInt(st.nextToken());\n        st = new StringTokenizer(br.readLine());\n        int r = Integer.parseInt(st.nextToken()) - 1, c = Integer.parseInt(st.nextToken()) - 1;\n        String cmds = br.readLine();\n        if (cmds == null) cmds = \"\";\n        boolean[][] vis = new boolean[H][W];\n        vis[r][c] = true;\n        // TODO: apply each move (U/D/L/R), ignoring off-grid steps, marking visited cells\n        StringBuilder sb = new StringBuilder();\n        for (int i = 0; i < H; i++) {\n            for (int j = 0; j < W; j++) sb.append(vis[i][j] ? '#' : '.');\n            sb.append('\\n');\n        }\n        System.out.print(sb);\n    }\n}\n",
    "game-of-life-step": "import java.util.*;\nimport java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int H = Integer.parseInt(st.nextToken()), W = Integer.parseInt(st.nextToken());\n        char[][] g = new char[H][];\n        for (int i = 0; i < H; i++) g[i] = br.readLine().toCharArray();\n        char[][] out = new char[H][W];\n        // TODO: count live neighbours from g (the OLD board) and fill out with the next generation\n        StringBuilder sb = new StringBuilder();\n        for (int i = 0; i < H; i++) { sb.append(new String(out[i])); sb.append('\\n'); }\n        System.out.print(sb);\n    }\n}\n",
    "set-matrix-zeroes": "import java.util.*;\nimport java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int H = Integer.parseInt(st.nextToken()), W = Integer.parseInt(st.nextToken());\n        char[][] g = new char[H][];\n        for (int i = 0; i < H; i++) g[i] = br.readLine().toCharArray();\n        boolean[] zr = new boolean[H], zc = new boolean[W];\n        // TODO: first mark rows/columns that contain a '0', then blank them\n        StringBuilder sb = new StringBuilder();\n        for (int i = 0; i < H; i++) { sb.append(new String(g[i])); sb.append('\\n'); }\n        System.out.print(sb);\n    }\n}\n",
    "rotate-matrix-90": "import java.util.*;\nimport java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int H = Integer.parseInt(st.nextToken()), W = Integer.parseInt(st.nextToken());\n        char[][] g = new char[H][];\n        for (int i = 0; i < H; i++) g[i] = br.readLine().toCharArray();\n        StringBuilder sb = new StringBuilder();\n        // TODO: output W rows of length H; row j is old column j read bottom-to-top\n        System.out.print(sb);\n    }\n}\n",
    "spiral-order": "import java.util.*;\nimport java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int H = Integer.parseInt(st.nextToken()), W = Integer.parseInt(st.nextToken());\n        char[][] g = new char[H][];\n        for (int i = 0; i < H; i++) g[i] = br.readLine().toCharArray();\n        StringBuilder sb = new StringBuilder();\n        // TODO: append characters in clockwise spiral order using top/bottom/left/right bounds\n        System.out.println(sb.toString());\n    }\n}\n",
})

DEFS += GRID_DEFS


# ---------------------------------------------------------------------------
# "Basics" problems — ad-hoc reasoning solvable with core Java (loops,
# conditionals, arithmetic, strings, arrays). No data structures or algorithmic
# techniques required — just figure out the logic and implement it. Authored as
# harness problems so the learner writes only the function body.
# ---------------------------------------------------------------------------

def _leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def _count_divisors(n):
    n = abs(n)
    if n == 0:
        return 0
    c = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            c += 1 if i * i == n else 2
        i += 1
    return c


def _digital_root(n):
    n = abs(n)
    while n >= 10:
        n = sum(int(ch) for ch in str(n))
    return n


def _alt_sum(nums):
    return sum(x if i % 2 == 0 else -x for i, x in enumerate(nums))


def _count_above_avg(nums):
    total = sum(nums)
    n = len(nums)
    return sum(1 for x in nums if x * n > total)


def _us_coins(cents):
    count = 0
    for coin in (25, 10, 5, 1):
        count += cents // coin
        cents %= coin
    return count


def _armstrong(n):
    s = str(n)
    k = len(s)
    return sum(int(d) ** k for d in s) == n


def _perfect(n):
    if n < 2:
        return False
    return sum(d for d in range(1, n) if n % d == 0) == n


def _collatz(n):
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def _sec_to_clock(s):
    return f"{s // 3600}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def _count_words(s):
    return len(s.split())


def _mountain(nums):
    n = len(nums)
    if n < 3:
        return False
    i = 0
    while i + 1 < n and nums[i] < nums[i + 1]:
        i += 1
    if i == 0 or i == n - 1:
        return False
    while i + 1 < n and nums[i] > nums[i + 1]:
        i += 1
    return i == n - 1


def _is_perm(nums):
    return sorted(nums) == list(range(1, len(nums) + 1))


def _rps(a, b):
    beats = {"R": "S", "S": "P", "P": "R"}
    aw = bw = 0
    for x, y in zip(a, b):
        if x == y:
            continue
        if beats[x] == y:
            aw += 1
        else:
            bw += 1
    return "A" if aw > bw else "B" if bw > aw else "Draw"


def _traffic(g, y, r, t):
    p = t % (g + y + r)
    return "green" if p < g else "yellow" if p < g + y else "red"


def _max_depth(s):
    depth = best = 0
    for ch in s:
        if ch == "(":
            depth += 1
            best = max(best, depth)
        elif ch == ")":
            depth -= 1
    return best


def _caesar(s, k):
    k %= 26
    return "".join(chr((ord(ch) - 97 + k) % 26 + 97) if "a" <= ch <= "z" else ch for ch in s)


def _rle(s):
    if not s:
        return ""
    out2 = []
    run = 1
    for i in range(1, len(s) + 1):
        if i < len(s) and s[i] == s[i - 1]:
            run += 1
        else:
            out2.append(s[i - 1] + str(run))
            run = 1
    return "".join(out2)


def _password_ok(s):
    return (
        len(s) >= 8
        and any(c.isupper() for c in s)
        and any(c.islower() for c in s)
        and any(c.isdigit() for c in s)
    )


def _bank_balance(tx):
    bal = 0
    for t in tx:
        if t < 0 and bal + t < 0:
            continue
        bal += t
    return bal


def _max_passengers(changes):
    cur = best = 0
    for c in changes:
        cur += c
        best = max(best, cur)
    return best


def _good_pairs(nums):
    c = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                c += 1
    return c


HARNESS_DEFS += [
    # ------- INTRO -------
    dict(slug="leap-year", title="Leap Year", difficulty="Intro", topics=["Math"], subtopics=["Conditionals"], companies=["Microsoft"],
         description="Return `true` if the given year is a leap year. A year is a leap year if it is divisible by 4, **except** century years (divisible by 100), which are leap years only if also divisible by 400.",
         constraints="1 ≤ y ≤ 10^5",
         hints=["Start from 'divisible by 4'.", "Then carve out the century exception.", "2000 is a leap year; 1900 is not."],
         opt=("O(1)", "O(1)", "A short chain of divisibility checks."),
         editorial="Leap iff (y%4==0 and y%100!=0) or y%400==0. Get the operator precedence right.",
         spec={"name": "solve", "params": [{"name": "y", "type": "int"}], "returns": "bool"},
         fn=lambda y: _leap(y),
         cases=[("example", "Divisible by 4", (2024,)), ("example", "Century non-leap", (1900,)), ("hidden", "400 year", (2000,)), ("hidden", "Ordinary", (2023,))],
         example_expl=["2024 is divisible by 4 → leap.", "1900 is a century but not divisible by 400 → not leap."]),
    dict(slug="count-divisors", title="Count Divisors", difficulty="Intro", topics=["Math"], subtopics=["Number Theory"], companies=["Amazon"],
         description="Return how many positive integers divide `n` exactly (including 1 and n itself).",
         constraints="1 ≤ n ≤ 10^9",
         hints=["A divisor d pairs with n/d.", "You only need to test up to √n.", "Count both members of each pair (once when d·d = n)."],
         opt=("O(√n)", "O(1)", "Test divisors up to the square root, counting each pair."),
         editorial="For i from 1 to √n, if i divides n add 2 (for i and n/i), or add 1 when i·i == n.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "int"},
         fn=lambda n: _count_divisors(n),
         cases=[("example", "Twelve", (12,)), ("example", "Prime", (7,)), ("hidden", "One", (1,)), ("hidden", "Square", (36,))],
         example_expl=["1,2,3,4,6,12 → 6 divisors.", "A prime has exactly 2."]),
    dict(slug="digital-root", title="Digital Root", difficulty="Intro", topics=["Math"], subtopics=["Digits"], companies=["Adobe"],
         description="Repeatedly replace the number by the sum of its digits until a single digit remains, and return it.",
         constraints="0 ≤ n ≤ 10^9",
         hints=["Sum the digits.", "If the result has more than one digit, repeat.", "Loop until the value is below 10."],
         opt=("O(log n) per pass", "O(1)", "Repeatedly fold the digit sum until a single digit remains."),
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "int"},
         fn=lambda n: _digital_root(n),
         cases=[("example", "Example", (942,)), ("example", "Single", (7,)), ("hidden", "Zero", (0,)), ("hidden", "Nines", (99999,))],
         example_expl=["9+4+2=15 → 1+5=6.", "Already a single digit."]),
    dict(slug="alternating-sum", title="Alternating Sum", difficulty="Intro", topics=["Arrays"], subtopics=["Traversal"], companies=["Bloomberg"],
         description="Return a[0] − a[1] + a[2] − a[3] + … (add even indices, subtract odd indices).",
         constraints="0 ≤ n ≤ 10^5",
         hints=["Walk the array with an index.", "Add when the index is even, subtract when odd.", "An empty array sums to 0."],
         opt=("O(n)", "O(1)", "One pass toggling the sign by index parity."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: _alt_sum(nums),
         cases=[("example", "Example", ([1, 2, 3, 4, 5],)), ("example", "Two", ([10, 3],)), ("hidden", "Single", ([7],)), ("hidden", "Empty", ([],))],
         example_expl=["1-2+3-4+5 = 3.", "10-3 = 7."]),
    dict(slug="us-coins-change", title="Coin Count (US coins)", difficulty="Intro", topics=["Math", "Greedy"], subtopics=["Greedy"], companies=["Amazon"],
         description="Make `cents` using quarters (25), dimes (10), nickels (5), and pennies (1). Return the **fewest** coins needed. (With these denominations, always take the largest coin that fits.)",
         constraints="0 ≤ cents ≤ 10^6",
         hints=["Take as many quarters as possible, then dimes, then nickels, then pennies.", "After each coin, keep the remainder with %.", "Sum how many coins you used."],
         opt=("O(1)", "O(1)", "Greedy over four fixed denominations."),
         editorial="Greedily divide by 25, then 10, then 5, then 1, summing the quotients — optimal for these canonical coins.",
         spec={"name": "solve", "params": [{"name": "cents", "type": "int"}], "returns": "int"},
         fn=lambda cents: _us_coins(cents),
         cases=[("example", "63 cents", (63,)), ("example", "Exact quarter", (25,)), ("hidden", "Zero", (0,)), ("hidden", "Pennies only", (4,))],
         example_expl=["2×25 + 1×10 + 3×1 = 6 coins.", "One quarter."]),

    # ------- EASY -------
    dict(slug="count-above-average", title="Count Above Average", difficulty="Easy", topics=["Arrays"], subtopics=["Counting"], companies=["Amazon"],
         description="Return how many elements are strictly greater than the array's average.",
         constraints="1 ≤ n ≤ 10^5",
         hints=["First find the total (or average).", "Then count elements above it.", "To avoid fractions, compare x·n with the sum instead of x with sum/n."],
         opt=("O(n)", "O(1)", "One pass for the sum, one to count."),
         editorial="Compute the sum; an element x beats the average exactly when x·n > sum — this dodges floating point.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: _count_above_avg(nums),
         cases=[("example", "Example", ([1, 2, 3, 4, 5],)), ("example", "Flat", ([2, 2, 2],)), ("hidden", "One big", ([1, 1, 10],)), ("hidden", "Single", ([5],))],
         example_expl=["Average 3; 4 and 5 are above → 2.", "Nothing exceeds the average."]),
    dict(slug="armstrong-number", title="Armstrong Number", difficulty="Easy", topics=["Math"], subtopics=["Digits"], companies=["Adobe"],
         description="Return `true` if `n` equals the sum of each of its digits raised to the power of the number of digits (e.g. 153 = 1³+5³+3³).",
         constraints="0 ≤ n ≤ 10^9",
         hints=["Count the digits first — that's the exponent.", "Raise each digit to that power and add.", "Compare the total to n."],
         opt=("O(d)", "O(1)", "One pass over the d digits."),
         editorial="Let k be the digit count; sum digit^k over all digits and check equality with n.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "bool"},
         fn=lambda n: _armstrong(n),
         cases=[("example", "153", (153,)), ("example", "Not", (100,)), ("hidden", "Single", (5,)), ("hidden", "Four-digit", (9474,))],
         example_expl=["1³+5³+3³ = 153.", "1+0+0 ≠ 100."]),
    dict(slug="perfect-number", title="Perfect Number", difficulty="Easy", topics=["Math"], subtopics=["Number Theory"], companies=["Bloomberg"],
         description="Return `true` if `n` equals the sum of its proper divisors (all positive divisors except itself).",
         constraints="1 ≤ n ≤ 10^5",
         hints=["Proper divisors of n are 1..n-1 that divide n.", "Sum them and compare to n.", "6 = 1+2+3 is the smallest perfect number."],
         opt=("O(√n)", "O(1)", "Sum divisors up to √n in pairs."),
         editorial="Add every proper divisor (pair i with n/i up to √n, excluding n itself) and test equality with n.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "bool"},
         fn=lambda n: _perfect(n),
         cases=[("example", "Six", (6,)), ("example", "Not", (10,)), ("hidden", "28", (28,)), ("hidden", "One", (1,))],
         example_expl=["1+2+3 = 6.", "1+2+5 = 8 ≠ 10."]),
    dict(slug="collatz-steps", title="Collatz Steps", difficulty="Easy", topics=["Math", "Simulation"], subtopics=["Simulation"], companies=["Google"],
         description="Starting from `n`, repeatedly halve it if even or replace it with 3n+1 if odd. Return how many steps it takes to reach 1.",
         constraints="1 ≤ n ≤ 10^6",
         hints=["Loop until n becomes 1.", "Even → n/2, odd → 3n+1.", "Count each transformation."],
         opt=("O(steps)", "O(1)", "Simulate the sequence, counting steps."),
         editorial="Just simulate the rule, incrementing a counter until n reaches 1. No formula is known — you run it.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "int"},
         fn=lambda n: _collatz(n),
         cases=[("example", "Example", (6,)), ("example", "Already one", (1,)), ("hidden", "Power of two", (16,)), ("hidden", "Odd", (7,))],
         example_expl=["6→3→10→5→16→8→4→2→1 = 8 steps.", "0 steps."]),
    dict(slug="seconds-to-clock", title="Seconds to Clock", difficulty="Easy", topics=["Math"], subtopics=["Arithmetic"], companies=["Amazon"],
         description="Convert a number of seconds into `H:MM:SS` form: hours as-is, minutes and seconds zero-padded to two digits.",
         constraints="0 ≤ s ≤ 10^9",
         hints=["Hours = s / 3600.", "Minutes = (s / 60) % 60, seconds = s % 60.", "Zero-pad minutes and seconds to width 2."],
         opt=("O(1)", "O(1)", "Integer division and modulo, then format."),
         editorial="h = s/3600, m = (s%3600)/60, sec = s%60; print h ':' then two-digit m and sec.",
         spec={"name": "solve", "params": [{"name": "s", "type": "int"}], "returns": "string"},
         fn=lambda s: _sec_to_clock(s),
         cases=[("example", "Example", (3661,)), ("example", "Zero", (0,)), ("hidden", "Minutes", (75,)), ("hidden", "Big", (86399,))],
         example_expl=["1:01:01.", "0:00:00."]),
    dict(slug="count-words", title="Count Words", difficulty="Easy", topics=["Strings"], subtopics=["Counting"], companies=["Microsoft"],
         description="Return the number of words in a sentence. Words are maximal runs of non-space characters; there may be extra spaces.",
         constraints="0 ≤ |s| ≤ 10^5",
         hints=["Split the string on spaces.", "Ignore empty pieces caused by repeated spaces.", "An empty or all-space string has 0 words."],
         opt=("O(|s|)", "O(1)", "Scan once, counting transitions into a word."),
         editorial="Count the number of times a non-space character follows a space (or the start) — equivalently the number of non-empty split tokens.",
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}], "returns": "int"},
         fn=lambda s: _count_words(s),
         cases=[("example", "Example", ("the quick brown fox",)), ("example", "Extra spaces", ("  hello   world  ",)), ("hidden", "One word", ("java",)), ("hidden", "Empty", ("",))],
         example_expl=["Four words.", "Extra spaces don't add words → 2."]),
    dict(slug="mountain-array", title="Mountain Array", difficulty="Easy", topics=["Arrays"], subtopics=["Traversal"], companies=["Amazon", "Meta"],
         description="Return `true` if the array strictly increases to a single peak and then strictly decreases. The peak must not be the first or last element (length ≥ 3).",
         constraints="0 ≤ n ≤ 10^5",
         hints=["Walk up while strictly increasing.", "The peak can't be at either end.", "Then it must strictly decrease all the way down."],
         opt=("O(n)", "O(1)", "Two directional scans (up then down)."),
         editorial="Advance while a[i] < a[i+1]; the stopping index is the peak (reject if at an end); then require strictly decreasing to the last index.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "bool"},
         fn=lambda nums: _mountain(nums),
         cases=[("example", "Mountain", ([1, 3, 5, 4, 2],)), ("example", "Only up", ([1, 2, 3],)), ("hidden", "Plateau", ([1, 2, 2, 1],)), ("hidden", "Too short", ([1, 2],))],
         example_expl=["Up to 5 then down → true.", "Never comes down → false."]),
    dict(slug="is-permutation-1n", title="Is a Permutation of 1..n", difficulty="Easy", topics=["Arrays"], subtopics=["Counting"], companies=["Adobe"],
         description="Return `true` if the array of length n contains every integer from 1 to n exactly once (in any order).",
         constraints="0 ≤ n ≤ 10^5",
         hints=["A valid permutation uses each of 1..n once.", "Sorting it should give 1,2,…,n.", "Or mark seen values and check for duplicates / out-of-range."],
         opt=("O(n log n)", "O(1)", "Sort and compare to 1..n (or a seen-array in O(n))."),
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "bool"},
         fn=lambda nums: _is_perm(nums),
         cases=[("example", "Permutation", ([3, 1, 2],)), ("example", "Missing", ([1, 2, 2],)), ("hidden", "Empty", ([],)), ("hidden", "Out of range", ([0, 1],))],
         example_expl=["Exactly 1,2,3 → true.", "2 repeats, 3 missing → false."]),
    dict(slug="rock-paper-scissors", title="Rock Paper Scissors", difficulty="Easy", topics=["Simulation"], subtopics=["State Machine"], companies=["Amazon"],
         description="Two players play several rounds. Each move is `R`, `P`, or `S` (rock beats scissors, scissors beats paper, paper beats rock). Given both players' move strings of equal length, return `A`, `B`, or `Draw` for whoever wins more rounds.",
         constraints="0 ≤ length ≤ 10^5\nEach character is R, P, or S.",
         hints=["Compare the moves round by round.", "Encode who-beats-whom in a small lookup.", "Tally each player's round wins, then compare totals."],
         opt=("O(n)", "O(1)", "One pass tallying round wins."),
         editorial="Use beats = {R:S, S:P, P:R}. For each round, if a beats b give A a point, else B; equal moves are draws. Compare totals.",
         spec={"name": "solve", "params": [{"name": "a", "type": "string"}, {"name": "b", "type": "string"}], "returns": "string"},
         fn=lambda a, b: _rps(a, b),
         cases=[("example", "A wins", ("RPS", "SRP")), ("example", "Draw", ("RR", "RR")), ("hidden", "B wins", ("R", "P")), ("hidden", "Mixed", ("RPSR", "PSRP"))],
         example_expl=["A wins each round → A.", "Identical moves → Draw."]),
    dict(slug="traffic-light", title="Traffic Light", difficulty="Easy", topics=["Math", "Simulation"], subtopics=["Simulation"], companies=["Bloomberg"],
         description="A light cycles green for `g` seconds, then yellow for `y`, then red for `r`, forever, starting at green at time 0. Return the colour (\"green\", \"yellow\", or \"red\") at time `t`.",
         constraints="1 ≤ g, y, r ≤ 10^4\n0 ≤ t ≤ 10^9",
         hints=["The pattern repeats every g+y+r seconds.", "Reduce t modulo the cycle length.", "Then place it in the green / yellow / red band."],
         opt=("O(1)", "O(1)", "One modulo plus two comparisons."),
         editorial="phase = t mod (g+y+r); it's green if phase < g, yellow if phase < g+y, otherwise red.",
         spec={"name": "solve", "params": [{"name": "g", "type": "int"}, {"name": "y", "type": "int"}, {"name": "r", "type": "int"}, {"name": "t", "type": "int"}], "returns": "string"},
         fn=lambda g, y, r, t: _traffic(g, y, r, t),
         cases=[("example", "Green", (5, 2, 3, 1)), ("example", "Red", (5, 2, 3, 9)), ("hidden", "Yellow edge", (5, 2, 3, 6)), ("hidden", "Wraps", (5, 2, 3, 10))],
         example_expl=["t=1 is within the first 5s → green.", "t=9 mod 10 = 9 → red band."]),
    dict(slug="max-nesting-depth", title="Maximum Nesting Depth", difficulty="Easy", topics=["Strings"], subtopics=["Counting"], companies=["Amazon", "Google"],
         description="Given a string of parentheses (guaranteed balanced), return the maximum nesting depth.",
         constraints="0 ≤ |s| ≤ 10^5\ns contains only '(' and ')'.",
         hints=["Track a running depth.", "'(' increases it, ')' decreases it.", "Remember the largest depth seen."],
         opt=("O(n)", "O(1)", "A single counter — no stack needed."),
         editorial="Scan the string keeping a depth counter; bump it on '(' (updating the max) and drop it on ')'. Because the input is balanced, a plain counter suffices.",
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}], "returns": "int"},
         fn=lambda s: _max_depth(s),
         cases=[("example", "Nested", ("((()))",)), ("example", "Flat", ("()()",)), ("hidden", "Empty", ("",)), ("hidden", "Mixed", ("(()(()))",))],
         example_expl=["Three levels deep.", "Never deeper than 1."]),
    dict(slug="caesar-cipher", title="Caesar Cipher", difficulty="Easy", topics=["Strings"], subtopics=["Arithmetic"], companies=["Adobe"],
         description="Shift each lowercase letter forward by `k` positions in the alphabet, wrapping past 'z' back to 'a'. Non-letter characters are unchanged.",
         constraints="0 ≤ |s| ≤ 10^5\n0 ≤ k ≤ 10^9\nLetters are lowercase.",
         hints=["Map each letter to 0–25 with c − 'a'.", "Add k, wrap with mod 26, map back.", "Reduce k mod 26 first for big shifts."],
         opt=("O(|s|)", "O(|s|)", "Shift each character in one pass."),
         editorial="For each lowercase c: ((c - 'a' + k) mod 26) + 'a'. Reducing k mod 26 keeps the arithmetic small.",
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}, {"name": "k", "type": "int"}], "returns": "string"},
         fn=lambda s, k: _caesar(s, k),
         cases=[("example", "Shift 3", ("abc", 3)), ("example", "Wrap", ("xyz", 2)), ("hidden", "No shift", ("hello", 0)), ("hidden", "Big k", ("abc", 29))],
         example_expl=["a→d, b→e, c→f.", "x→z, y→a, z→b."]),
    dict(slug="run-length-encode", title="Run-Length Encoding", difficulty="Easy", topics=["Strings"], subtopics=["Counting"], companies=["Amazon", "Microsoft"],
         description="Compress a string by replacing each run of identical characters with the character followed by its count. For example `aaabbc` → `a3b2c1`.",
         constraints="0 ≤ |s| ≤ 10^5",
         hints=["Track the current character and how long its run is.", "When the character changes, emit char + count.", "Don't forget to emit the final run."],
         opt=("O(|s|)", "O(|s|)", "One pass grouping consecutive equal characters."),
         editorial="Walk the string; while the next char equals the current, grow the run; otherwise append char+count and reset. Emit the last run at the end.",
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}], "returns": "string"},
         fn=lambda s: _rle(s),
         cases=[("example", "Example", ("aaabbc",)), ("example", "All same", ("zzzz",)), ("hidden", "Empty", ("",)), ("hidden", "No runs", ("abc",))],
         example_expl=["a3b2c1.", "z4."]),
    dict(slug="password-strength", title="Valid Password", difficulty="Easy", topics=["Strings"], subtopics=["Conditionals"], companies=["Amazon"],
         description="Return `true` if the password is valid: at least 8 characters long AND containing at least one uppercase letter, one lowercase letter, and one digit.",
         constraints="0 ≤ |s| ≤ 10^5",
         hints=["Check the length first.", "Scan once, setting flags for upper, lower, and digit.", "All conditions must hold."],
         opt=("O(|s|)", "O(1)", "One pass collecting character-class flags."),
         editorial="Track three booleans (seen upper, lower, digit) in a single scan and combine them with the length requirement.",
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}], "returns": "bool"},
         fn=lambda s: _password_ok(s),
         cases=[("example", "Valid", ("Abcdef12",)), ("example", "Too short", ("Abc12",)), ("hidden", "No digit", ("Abcdefgh",)), ("hidden", "No upper", ("abcdefg1",))],
         example_expl=["8 chars with upper, lower, digit → valid.", "Only 5 characters → invalid."]),
    dict(slug="bank-balance", title="Bank Account Balance", difficulty="Easy", topics=["Arrays", "Simulation"], subtopics=["Simulation"], companies=["Bloomberg", "Amazon"],
         description="Process a list of transactions on an account that starts at 0. A positive value is a deposit (always applied). A negative value is a withdrawal, but a withdrawal that would make the balance negative is **rejected** (skipped). Return the final balance.",
         constraints="0 ≤ n ≤ 10^5",
         hints=["Keep a running balance.", "Apply deposits directly.", "Only apply a withdrawal if the balance stays ≥ 0; otherwise skip it."],
         opt=("O(n)", "O(1)", "Single pass with a guarded update."),
         editorial="Iterate the transactions; for a negative t, apply it only if balance + t ≥ 0, otherwise ignore it. Positives always apply.",
         spec={"name": "solve", "params": [{"name": "transactions", "type": "int[]"}], "returns": "int"},
         fn=lambda transactions: _bank_balance(transactions),
         cases=[("example", "Example", ([100, -30, -200, 50],)), ("example", "All deposits", ([10, 20, 30],)), ("hidden", "Reject first", ([-5, 40],)), ("hidden", "Empty", ([],))],
         example_expl=["100, then -30 → 70, -200 rejected, +50 → 120.", "10+20+30 = 60."]),
    dict(slug="max-passengers", title="Maximum Passengers", difficulty="Easy", topics=["Arrays", "Simulation"], subtopics=["Prefix Sum"], companies=["Amazon"],
         description="A bus starts empty. At each stop, `changes[i]` people board (or leave, if negative). Return the maximum number of passengers on the bus at any moment.",
         constraints="1 ≤ n ≤ 10^5\nThe bus is never over-emptied (running total stays ≥ 0).",
         hints=["Keep a running count of passengers.", "Update it at each stop.", "Track the largest value it reaches."],
         opt=("O(n)", "O(1)", "Running total with a max tracker."),
         editorial="Accumulate the changes into a running passenger count and record the maximum seen — a prefix-sum-with-running-max.",
         spec={"name": "solve", "params": [{"name": "changes", "type": "int[]"}], "returns": "int"},
         fn=lambda changes: _max_passengers(changes),
         cases=[("example", "Example", ([3, 2, -1, 4, -3],)), ("example", "Only boarding", ([1, 1, 1],)), ("hidden", "Empties", ([5, -5, 2],)), ("hidden", "Single", ([7],))],
         example_expl=["Counts 3,5,4,8,5 → peak 8.", "1,2,3 → peak 3."]),
    dict(slug="count-equal-pairs", title="Count Equal Pairs", difficulty="Easy", topics=["Arrays"], subtopics=["Counting"], companies=["Amazon", "Adobe"],
         description="Return the number of index pairs (i, j) with i < j and nums[i] == nums[j].",
         constraints="1 ≤ n ≤ 2000",
         hints=["A pair needs two equal values at different indices.", "With small n, a double loop is fine.", "For each i, compare against every later j."],
         opt=("O(n²)", "O(1)", "Check every pair — the small bound makes it fine (counts also work)."),
         editorial="With n ≤ 2000 a nested loop over i < j counting equal values is well within limits. (Frequency counts give an O(n) alternative: sum c·(c−1)/2.)",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: _good_pairs(nums),
         cases=[("example", "Example", ([1, 2, 1, 1],)), ("example", "None", ([1, 2, 3],)), ("hidden", "All same", ([5, 5, 5, 5],)), ("hidden", "Single", ([9],))],
         example_expl=["Pairs (0,2),(0,3),(2,3) → 3.", "All distinct → 0."]),
]

PREREQS.update({
    "leap-year": [("conditionals", "The rule is a chain of divisibility conditions."), ("modulo", "Divisibility is a remainder test.")],
    "count-divisors": [("number_theory", "Divisors pair as d and n/d."), ("loops_basic", "Trial-divide up to √n."), ("big_o", "Stopping at √n turns O(n) into O(√n).")],
    "digital-root": [("math_digits", "Sum the digits with % 10 and // 10 (or the string form)."), ("loops_basic", "Repeat until a single digit remains.")],
    "alternating-sum": [("iteration", "Walk the array once."), ("conditionals", "Add or subtract based on index parity.")],
    "count-above-average": [("iteration", "One pass for the sum, one to count."), ("arithmetic", "Compare x·n with the sum to avoid fractions.")],
    "us-coins-change": [("greedy", "Always take the largest coin that fits."), ("modulo", "Keep the remainder after each denomination.")],
    "armstrong-number": [("math_digits", "Break n into its digits."), ("arithmetic", "Raise each digit to the digit-count power and sum.")],
    "perfect-number": [("number_theory", "Sum the proper divisors."), ("loops_basic", "Find divisors up to √n in pairs.")],
    "collatz-steps": [("simulation", "Apply the even/odd rule step by step."), ("loops_basic", "Loop until you reach 1.")],
    "seconds-to-clock": [("arithmetic", "Integer division and modulo split the seconds."), ("string_basics", "Zero-pad the minute and second fields.")],
    "count-words": [("string_basics", "Split on spaces and ignore empties."), ("iteration", "Or count word-start transitions in one scan.")],
    "mountain-array": [("iteration", "Walk up to the peak, then down."), ("conditionals", "Reject peaks at the ends or non-strict steps.")],
    "is-permutation-1n": [("sorting", "Sorting should yield 1..n."), ("iteration", "Or mark seen values and check the range.")],
    "rock-paper-scissors": [("simulation", "Resolve each round in order."), ("conditionals", "Encode who beats whom and tally wins.")],
    "traffic-light": [("modulo", "The pattern repeats every g+y+r seconds."), ("conditionals", "Place the phase in the right colour band.")],
    "max-nesting-depth": [("iteration", "A single depth counter over the string."), ("conditionals", "Bump on '(' and drop on ')'.")],
    "caesar-cipher": [("string_basics", "Map letters to 0–25 and back."), ("modulo", "Wrap past 'z' with mod 26."), ("char_arrays", "Rebuild the shifted string character by character.")],
    "run-length-encode": [("string_basics", "Group consecutive equal characters."), ("iteration", "Emit char+count when the run ends — including the last run.")],
    "password-strength": [("string_basics", "Scan for character classes."), ("boolean_logic", "All requirements must hold together.")],
    "bank-balance": [("simulation", "Apply each transaction in order."), ("conditionals", "Reject a withdrawal that would overdraft.")],
    "max-passengers": [("prefix_sum", "The running total is the current passenger count."), ("iteration", "Track the maximum as you go.")],
    "count-equal-pairs": [("iteration", "Compare every pair i < j."), ("big_o", "The small n makes the O(n²) double loop acceptable.")],
})


# ---------------------------------------------------------------------------
# Special-judge (checker) demo — a problem with MULTIPLE valid answers, judged
# by a checker instead of exact match. Proves the checker pipeline.
# ---------------------------------------------------------------------------

def _two_sum_any(nums, target):
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i + 1, j + 1]
    return [-1, -1]


_TWO_SUM_CHECKER = (
    "def check(inp, out):\n"
    "    lines = inp.strip().split('\\n')\n"
    "    nums = list(map(int, lines[0].split())) if lines and lines[0].strip() else []\n"
    "    target = int(lines[1]) if len(lines) > 1 else 0\n"
    "    toks = out.split()\n"
    "    if len(toks) != 2:\n"
    "        return False\n"
    "    try:\n"
    "        i, j = int(toks[0]), int(toks[1])\n"
    "    except ValueError:\n"
    "        return False\n"
    "    n = len(nums)\n"
    "    if not (1 <= i <= n and 1 <= j <= n and i != j):\n"
    "        return False\n"
    "    return nums[i - 1] + nums[j - 1] == target\n"
)

HARNESS_DEFS += [
    dict(slug="two-sum-any", title="Two Sum (any valid pair)", difficulty="Easy",
         topics=["Hashing", "Arrays"], subtopics=["Complement Lookup"], companies=["Amazon", "Google"],
         description=(
             "Return the 1-based indices of **any** two distinct elements that add up to `target` "
             "(at least one such pair exists). **Any** valid pair is accepted — a special judge checks "
             "your answer, so you don't have to match one specific output."
         ),
         constraints="2 ≤ n ≤ 10^4\nAt least one valid pair exists.",
         hints=["Any correct pair scores — you don't have to find a particular one.", "A hash map of seen values finds a complement in O(1).", "Return the two 1-based indices in either order."],
         opt=("O(n)", "O(n)", "Hash-map complement lookup; any valid pair is accepted."),
         editorial="Because multiple answers are valid, a checker verifies that your two indices are in range, distinct, and sum to the target. A single hash-map pass finds one such pair.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}], "returns": "int[]"},
         fn=lambda nums, target: _two_sum_any(nums, target),
         judge_mode="checker", checker=_TWO_SUM_CHECKER,
         cases=[("example", "Example 1", ([2, 7, 11, 15], 9)), ("example", "Example 2", ([3, 2, 4], 6)), ("hidden", "Multiple pairs", ([1, 2, 3, 4, 5], 6)), ("hidden", "Ends", ([5, 1, 2, 4], 9))],
         example_expl=["Indices 1 and 2 (2+7=9) — but 'any' valid pair is accepted.", "Indices 2 and 3 (2+4=6)."]),
]

PREREQS.update({
    "two-sum-any": [("complement", "For each x, look up target − x."), ("hashing", "A hash map makes the lookup O(1)."), ("iteration", "One pass finds a valid pair; the checker accepts any correct one.")],
})


# ---------------------------------------------------------------------------
# Syllabus expansion — 9 interview domains (trees, linked lists, backtracking,
# heaps, intervals, design, union-find, advanced graphs, tries). Authored in a
# separate file and exec'd here so it can extend CONCEPTS/HARNESS_DEFS/DEFS/etc.
# in place. Defines EXPANSION_REFS (merged into REFERENCE_SOLUTIONS below).
# ---------------------------------------------------------------------------
_exp_path = os.path.join(HERE, "expansion_defs.py")
if os.path.exists(_exp_path):
    with open(_exp_path, encoding="utf-8") as _ef:
        exec(compile(_ef.read(), _exp_path, "exec"))


# ---------------------------------------------------------------------------
# TypeScript foundational Learn track — a second language for the Learn tab.
# Authored in a separate file and exec'd here so it can extend CONCEPTS /
# CATEGORY / LESSONS / EXERCISES in place with TypeScript concepts (each marked
# "language": "typescript"). No problem-bank / SEED_VERSION impact — concepts
# are embedded JSON, not SQLite.
# ---------------------------------------------------------------------------
_ts_path = os.path.join(HERE, "typescript_defs.py")
if os.path.exists(_ts_path):
    with open(_ts_path, encoding="utf-8") as _tf:
        exec(compile(_tf.read(), _ts_path, "exec"))

# TypeScript expansion — one coding challenge per foundational concept, plus
# two new foundational concepts (Numbers & Math, String Methods). Runs after
# typescript_defs.py so it can reuse tsx/tsc/_P and extend EXERCISES in place.
_tse_path = os.path.join(HERE, "typescript_expand.py")
if os.path.exists(_tse_path):
    with open(_tse_path, encoding="utf-8") as _tef:
        exec(compile(_tef.read(), _tse_path, "exec"))


# ---------------------------------------------------------------------------
# Japanese coding-vocabulary Learn track — a THIRD "language" for the Learn
# tab. Reference concepts only (big vocabulary tables, no code drills), each
# marked "language": "japanese". Extends CONCEPTS / CATEGORY / LESSONS in
# place. No SEED_VERSION / SQLite impact — concepts are embedded JSON.
# ---------------------------------------------------------------------------
_jp_path = os.path.join(HERE, "japanese_defs.py")
if os.path.exists(_jp_path):
    with open(_jp_path, encoding="utf-8") as _jpf:
        exec(compile(_jpf.read(), _jp_path, "exec"))

# Japanese → Java bridge content (problem statements in Japanese + interview
# Q&A). Defines JP_BRIDGE; written to seeds/jp_bridge.json near the concepts.
_jpb_path = os.path.join(HERE, "japanese_bridge.py")
if os.path.exists(_jpb_path):
    with open(_jpb_path, encoding="utf-8") as _jpbf:
        exec(compile(_jpbf.read(), _jpb_path, "exec"))


# ---------------------------------------------------------------------------
# Language-agnostic Algorithms Learn track — a FOURTH "language" for the Learn
# tab. Concepts teach the algorithm itself (pseudocode, complexity, worked
# trace tables) plus multiple-choice quizzes and curated practice-problem
# pointers — no code judge, each marked "language": "algorithms". Extends
# CONCEPTS / CATEGORY / LESSONS in place. No SEED_VERSION / SQLite impact —
# concepts are embedded JSON.
# ---------------------------------------------------------------------------
_alg_path = os.path.join(HERE, "algorithms_defs.py")
if os.path.exists(_alg_path):
    with open(_alg_path, encoding="utf-8") as _algf:
        exec(compile(_algf.read(), _alg_path, "exec"))


# ---------------------------------------------------------------------------
# Java core-concept drills — backfills fill-in-the-blank exercises for the
# high-value interview concepts that shipped with lessons but no practice
# (strings, hashing/complement, stack/queue, recursion, binary search,
# sorting). Extends EXERCISES in place; concepts/lessons already exist.
# ---------------------------------------------------------------------------
_jc_path = os.path.join(HERE, "java_core_drills.py")
if os.path.exists(_jc_path):
    with open(_jc_path, encoding="utf-8") as _jf:
        exec(compile(_jf.read(), _jc_path, "exec"))

# Batch 2: math, prefix sums, bit manipulation, greedy, dp/recurrence, heap, BFS.
_jc2_path = os.path.join(HERE, "java_core2_drills.py")
if os.path.exists(_jc2_path):
    with open(_jc2_path, encoding="utf-8") as _jf2:
        exec(compile(_jf2.read(), _jc2_path, "exec"))


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
        "judge_mode": d.get("judge_mode", "exact"),
        "checker": d.get("checker", ""),
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
        "examples": examples, "editorial": d.get("editorial") or opt_expl,
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
        "checker": d.get("checker", ""),
    })

# Assign a curated easiest→hardest global rank (used by the library's default sort):
# primary axis is the difficulty tier, then the authoring order within the tier.
_DIFF_RANK = {"Intro": 0, "Easy": 1, "Medium": 2, "Hard": 3}
_ranked = sorted(range(len(out)), key=lambda i: (_DIFF_RANK.get(out[i]["difficulty"], 9), i))
for _rank, _idx in enumerate(_ranked):
    out[_idx]["order"] = _rank

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"Wrote {len(out)} problems to {os.path.relpath(OUT)}")

CONCEPTS_OUT = os.path.join(HERE, "..", "src-tauri", "seeds", "concepts.json")
concepts = build_concepts()
with open(CONCEPTS_OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(concepts, f, indent=2, ensure_ascii=False)
print(f"Wrote {len(concepts)} concepts to {os.path.relpath(CONCEPTS_OUT)}")

# Concept flashcards (signal -> technique), seeded idempotently at launch.
FLASHCARDS_OUT = os.path.join(HERE, "..", "src-tauri", "seeds", "flashcards.json")
_flashcards = [
    {"front": f, "back": b, "source": s}
    for (f, b, s) in globals().get("FLASHCARDS", [])
]
with open(FLASHCARDS_OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(_flashcards, f, indent=2, ensure_ascii=False)
print(f"Wrote {len(_flashcards)} flashcards to {os.path.relpath(FLASHCARDS_OUT)}")

# Japanese → Java bridge (problem statements in Japanese + interview Q&A).
BRIDGE_OUT = os.path.join(HERE, "..", "src-tauri", "seeds", "jp_bridge.json")
_bridge = globals().get("JP_BRIDGE", {"problems": [], "interview": []})
with open(BRIDGE_OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(_bridge, f, indent=2, ensure_ascii=False)
print(
    f"Wrote {len(_bridge['problems'])} bridge problems + "
    f"{len(_bridge['interview'])} interview Q&A to {os.path.relpath(BRIDGE_OUT)}"
)

# ---------------------------------------------------------------------------
# Reference solutions — CORRECT, submittable solutions in each shipped language,
# used by the backend test `verify_seeds` to prove the judging + harness
# serialization contract end-to-end (a correct solution must be Accepted). This
# is NOT embedded in the app; it exists purely to guarantee trust in the bank.
# Curated to cover every return type, param type, and both languages.
# ---------------------------------------------------------------------------

REFERENCE_SOLUTIONS = {
    # -- harness problems: implement the function --
    "two-sum-fn": {
        "python": "def solve(nums, target):\n    pos = {}\n    for i, x in enumerate(nums):\n        if target - x in pos:\n            return [pos[target - x] + 1, i + 1]\n        pos[x] = i\n    return [-1]\n",
        "java": "import java.util.*;\nclass Solution {\n    int[] solve(int[] nums, int target) {\n        HashMap<Integer,Integer> pos = new HashMap<>();\n        for (int i = 0; i < nums.length; i++) {\n            if (pos.containsKey(target - nums[i])) return new int[]{pos.get(target - nums[i]) + 1, i + 1};\n            pos.put(nums[i], i);\n        }\n        return new int[]{-1};\n    }\n}\n",
    },
    "max-subarray-fn": {
        "python": "def solve(nums):\n    best = cur = nums[0]\n    for x in nums[1:]:\n        cur = max(x, cur + x)\n        best = max(best, cur)\n    return best\n",
        "java": "class Solution {\n    int solve(int[] nums) {\n        int best = nums[0], cur = nums[0];\n        for (int i = 1; i < nums.length; i++) { cur = Math.max(nums[i], cur + nums[i]); best = Math.max(best, cur); }\n        return best;\n    }\n}\n",
    },
    "reverse-array-fn": {
        "python": "def solve(nums):\n    return nums[::-1]\n",
        "java": "class Solution {\n    int[] solve(int[] nums) {\n        int n = nums.length; int[] r = new int[n];\n        for (int i = 0; i < n; i++) r[i] = nums[n - 1 - i];\n        return r;\n    }\n}\n",
    },
    "is-palindrome-fn": {
        "python": "def solve(s):\n    return s == s[::-1]\n",
        "java": "class Solution {\n    boolean solve(String s) {\n        int i = 0, j = s.length() - 1;\n        while (i < j) { if (s.charAt(i) != s.charAt(j)) return false; i++; j--; }\n        return true;\n    }\n}\n",
    },
    "factorial": {
        "python": "def solve(n):\n    r = 1\n    for i in range(2, n + 1):\n        r *= i\n    return r\n",
        "java": "class Solution {\n    long solve(int n) {\n        long r = 1;\n        for (int i = 2; i <= n; i++) r *= i;\n        return r;\n    }\n}\n",
    },
    "contains-duplicate": {
        "python": "def solve(nums):\n    return len(set(nums)) != len(nums)\n",
        "java": "import java.util.*;\nclass Solution {\n    boolean solve(int[] nums) {\n        HashSet<Integer> seen = new HashSet<>();\n        for (int x : nums) if (!seen.add(x)) return true;\n        return false;\n    }\n}\n",
    },
    "running-sum": {
        "python": "def solve(nums):\n    out = []\n    s = 0\n    for x in nums:\n        s += x\n        out.append(s)\n    return out\n",
        "java": "class Solution {\n    int[] solve(int[] nums) {\n        int[] r = new int[nums.length]; int s = 0;\n        for (int i = 0; i < nums.length; i++) { s += nums[i]; r[i] = s; }\n        return r;\n    }\n}\n",
    },
    "product-except-self": {
        "python": "def solve(nums):\n    n = len(nums)\n    res = [1] * n\n    pre = 1\n    for i in range(n):\n        res[i] = pre\n        pre *= nums[i]\n    suf = 1\n    for i in range(n - 1, -1, -1):\n        res[i] *= suf\n        suf *= nums[i]\n    return res\n",
        "java": "class Solution {\n    int[] solve(int[] nums) {\n        int n = nums.length; int[] res = new int[n];\n        int pre = 1; for (int i = 0; i < n; i++) { res[i] = pre; pre *= nums[i]; }\n        int suf = 1; for (int i = n - 1; i >= 0; i--) { res[i] *= suf; suf *= nums[i]; }\n        return res;\n    }\n}\n",
    },
    "fizzbuzz-value": {
        "python": "def solve(n):\n    if n % 15 == 0: return 'FizzBuzz'\n    if n % 3 == 0: return 'Fizz'\n    if n % 5 == 0: return 'Buzz'\n    return str(n)\n",
        "java": "class Solution {\n    String solve(int n) {\n        if (n % 15 == 0) return \"FizzBuzz\";\n        if (n % 3 == 0) return \"Fizz\";\n        if (n % 5 == 0) return \"Buzz\";\n        return Integer.toString(n);\n    }\n}\n",
    },
    "caesar-cipher": {
        "python": "def solve(s, k):\n    k %= 26\n    out = []\n    for ch in s:\n        if 'a' <= ch <= 'z':\n            out.append(chr((ord(ch) - 97 + k) % 26 + 97))\n        else:\n            out.append(ch)\n    return ''.join(out)\n",
        "java": "class Solution {\n    String solve(String s, int k) {\n        k %= 26; StringBuilder sb = new StringBuilder();\n        for (char c : s.toCharArray()) {\n            if (c >= 'a' && c <= 'z') sb.append((char)((c - 'a' + k) % 26 + 'a'));\n            else sb.append(c);\n        }\n        return sb.toString();\n    }\n}\n",
    },
    "word-break": {
        "python": "def solve(s, words):\n    w = set(words)\n    n = len(s)\n    dp = [True] + [False] * n\n    for i in range(1, n + 1):\n        for j in range(i):\n            if dp[j] and s[j:i] in w:\n                dp[i] = True\n                break\n    return dp[n]\n",
        "java": "import java.util.*;\nclass Solution {\n    boolean solve(String s, String[] words) {\n        Set<String> w = new HashSet<>(Arrays.asList(words));\n        int n = s.length(); boolean[] dp = new boolean[n + 1]; dp[0] = true;\n        for (int i = 1; i <= n; i++)\n            for (int j = 0; j < i; j++)\n                if (dp[j] && w.contains(s.substring(j, i))) { dp[i] = true; break; }\n        return dp[n];\n    }\n}\n",
    },
    "count-primes": {
        "python": "def solve(n):\n    if n < 3: return 0\n    sieve = [True] * n\n    sieve[0] = sieve[1] = False\n    i = 2\n    while i * i < n:\n        if sieve[i]:\n            for j in range(i * i, n, i): sieve[j] = False\n        i += 1\n    return sum(sieve)\n",
        "java": "class Solution {\n    int solve(int n) {\n        if (n < 3) return 0;\n        boolean[] c = new boolean[n];\n        int cnt = 0;\n        for (int i = 2; i < n; i++) {\n            if (!c[i]) { cnt++; for (long j = (long)i * i; j < n; j += i) c[(int)j] = true; }\n        }\n        return cnt;\n    }\n}\n",
    },
    "daily-temperatures": {
        "python": "def solve(temps):\n    res = [0] * len(temps)\n    st = []\n    for i, x in enumerate(temps):\n        while st and temps[st[-1]] < x:\n            j = st.pop(); res[j] = i - j\n        st.append(i)\n    return res\n",
        "java": "import java.util.*;\nclass Solution {\n    int[] solve(int[] temps) {\n        int[] res = new int[temps.length];\n        Deque<Integer> st = new ArrayDeque<>();\n        for (int i = 0; i < temps.length; i++) {\n            while (!st.isEmpty() && temps[st.peek()] < temps[i]) { int j = st.pop(); res[j] = i - j; }\n            st.push(i);\n        }\n        return res;\n    }\n}\n",
    },
    "coin-change": {
        "python": "def solve(coins, amount):\n    INF = float('inf')\n    dp = [0] + [INF] * amount\n    for a in range(1, amount + 1):\n        for c in coins:\n            if c <= a: dp[a] = min(dp[a], dp[a - c] + 1)\n    return dp[amount] if dp[amount] != INF else -1\n",
        "java": "import java.util.*;\nclass Solution {\n    int solve(int[] coins, int amount) {\n        int[] dp = new int[amount + 1];\n        Arrays.fill(dp, amount + 1); dp[0] = 0;\n        for (int a = 1; a <= amount; a++)\n            for (int c : coins) if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);\n        return dp[amount] > amount ? -1 : dp[amount];\n    }\n}\n",
    },
    "two-sum-sorted": {
        "python": "def solve(nums, target):\n    l, r = 0, len(nums) - 1\n    while l < r:\n        s = nums[l] + nums[r]\n        if s == target: return [l + 1, r + 1]\n        if s < target: l += 1\n        else: r -= 1\n    return [-1]\n",
        "java": "class Solution {\n    int[] solve(int[] nums, int target) {\n        int l = 0, r = nums.length - 1;\n        while (l < r) {\n            int s = nums[l] + nums[r];\n            if (s == target) return new int[]{l + 1, r + 1};\n            if (s < target) l++; else r--;\n        }\n        return new int[]{-1};\n    }\n}\n",
    },
    "digital-root": {
        "python": "def solve(n):\n    n = abs(n)\n    while n >= 10:\n        n = sum(int(c) for c in str(n))\n    return n\n",
        "java": "class Solution {\n    int solve(int n) {\n        n = Math.abs(n);\n        while (n >= 10) { int s = 0; while (n > 0) { s += n % 10; n /= 10; } n = s; }\n        return n;\n    }\n}\n",
    },
    "seconds-to-clock": {
        "python": "def solve(s):\n    return f\"{s // 3600}:{(s % 3600) // 60:02d}:{s % 60:02d}\"\n",
        "java": "class Solution {\n    String solve(int s) {\n        return (s / 3600) + \":\" + String.format(\"%02d\", (s % 3600) / 60) + \":\" + String.format(\"%02d\", s % 60);\n    }\n}\n",
    },
    # -- special-judge problem: a valid pair (may differ from the sample) --
    "two-sum-any": {
        "python": "def solve(nums, target):\n    seen = {}\n    for i in range(len(nums)):\n        for j in range(i + 1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i + 1, j + 1]\n    return [-1, -1]\n",
        "java": "class Solution {\n    int[] solve(int[] nums, int target) {\n        for (int i = 0; i < nums.length; i++)\n            for (int j = i + 1; j < nums.length; j++)\n                if (nums[i] + nums[j] == target) return new int[]{i + 1, j + 1};\n        return new int[]{-1, -1};\n    }\n}\n",
    },
    # -- raw stdin/stdout problems: full programs --
    "array-sum": {
        "python": "import sys\nd = sys.stdin.read().split()\nn = int(d[0])\nprint(sum(map(int, d[1:1 + n])))\n",
        "java": "import java.util.*;\npublic class Main {\n    public static void main(String[] a) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt(); long s = 0;\n        for (int i = 0; i < n; i++) s += sc.nextLong();\n        System.out.println(s);\n    }\n}\n",
    },
    "minesweeper-counts": {
        "python": "import sys\nL = sys.stdin.read().split('\\n')\nH, W = map(int, L[0].split())\ng = [L[1 + i] for i in range(H)]\nout = []\nfor i in range(H):\n    row = []\n    for j in range(W):\n        if g[i][j] == '*':\n            row.append('*')\n        else:\n            c = 0\n            for di in (-1, 0, 1):\n                for dj in (-1, 0, 1):\n                    if di == 0 and dj == 0: continue\n                    ni, nj = i + di, j + dj\n                    if 0 <= ni < H and 0 <= nj < W and g[ni][nj] == '*': c += 1\n            row.append(str(c))\n    out.append(''.join(row))\nprint('\\n'.join(out))\n",
        "java": "import java.util.*;\nimport java.io.*;\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int H = Integer.parseInt(st.nextToken()), W = Integer.parseInt(st.nextToken());\n        char[][] g = new char[H][];\n        for (int i = 0; i < H; i++) g[i] = br.readLine().toCharArray();\n        StringBuilder sb = new StringBuilder();\n        for (int i = 0; i < H; i++) {\n            for (int j = 0; j < W; j++) {\n                if (g[i][j] == '*') { sb.append('*'); continue; }\n                int c = 0;\n                for (int di = -1; di <= 1; di++) for (int dj = -1; dj <= 1; dj++) {\n                    if (di == 0 && dj == 0) continue;\n                    int ni = i + di, nj = j + dj;\n                    if (ni >= 0 && ni < H && nj >= 0 && nj < W && g[ni][nj] == '*') c++;\n                }\n                sb.append((char)('0' + c));\n            }\n            sb.append('\\n');\n        }\n        System.out.print(sb);\n    }\n}\n",
    },
}

REFERENCE_SOLUTIONS.update(globals().get("EXPANSION_REFS", {}))

REFS_OUT = os.path.join(HERE, "..", "src-tauri", "seeds", "reference_solutions.json")
with open(REFS_OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(REFERENCE_SOLUTIONS, f, indent=2, ensure_ascii=False)
print(f"Wrote {len(REFERENCE_SOLUTIONS)} reference solution sets to {os.path.relpath(REFS_OUT)}")
