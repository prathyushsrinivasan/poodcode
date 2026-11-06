"""Author the offline Python interview course. Run to rebuild JSON and roadmap."""
import ast
import builtins
import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
MODULES = []


def clean(text):
    return dedent(text).strip() + "\n"


def lesson(title, stage, goal, explanation, example, pattern, gate):
    item = dict(id=f"p{len(MODULES) + 1:02}", number=len(MODULES) + 1,
                title=title, stage=stage, goal=goal, explanation=clean(explanation),
                example=clean(example), pattern=clean(pattern), gate=gate, exercises=[])
    MODULES.append(item)


def ex(key, title, params, prompt, solution, cases, hint, reasoning, complexity, setup="", prelude=""):
    """cases: (label, Python argument expression, expected Python value)."""
    MODULES[-1]["exercises"].append(dict(
        id="python:" + key, title=title, prompt=prompt, hint=hint,
        starter=clean(prelude + f"def solve({params}):\n    # Replace this return with your solution.\n    return 0\n"),
        solution=clean(prelude + solution), explanation=reasoning, complexity=complexity,
        tests=[dict(name=name, setup=clean(setup) if setup else "", call=f"solve({args})", expected=repr(expected))
               for name, args, expected in cases],
    ))


lesson("Your first Python functions", "1. Learn Python by coding",
       "Read a tiny program, change it, and return an integer.", """
    Python executes statements from top to bottom. A name stores a value: `score = 3`.
    `=` assigns; it is not a mathematical equality test. Integers can be negative.
    `+`, `-`, `*` and `**` mean add, subtract, multiply and exponentiate.
    Parentheses control evaluation order. `//` gives floor division (so `-3 // 2`
    is `-2`); `%` gives the remainder (`7 % 3` is `1`). `/` produces a floating
    point result; use `//` for integer counts. Names are case sensitive.

    `def solve(a, b):` defines a function named `solve` with two parameters.
    Parameters are names supplied by whoever calls the function. The colon starts
    its body. Indent the body with four spaces. `return` sends a value back and
    immediately exits the function. Blank lines separate ideas; `#` starts a
    comment. `print(...)` displays a value; it does not replace `return`.
    A call such as `solve(2, 3)` supplies arguments in parameter order.
    You do not need input parsing: the course runner supplies the arguments.

    Type the example, predict 5, then change the arguments. In each exercise,
    keep the function name and parameters and replace the placeholder return.
    Run all visible cases. Expected and actual values appear in the results.
    A red case is feedback: repair the code and run again. A completed exercise
    means the published cases passed, not a proof of optimal complexity.
    """, """
    def solve(a, b):
        total = a + b
        return total

    print(solve(2, 3))  # 5
    quotient = 7 // 3
    remainder = 7 % 3
    print(quotient, remainder, 2 ** 3, 8 / 2, -3 * 2 - 1)
    """, """
    Trace parameters -> calculation -> return. Never add print statements to
    the submitted function: the runner displays the returned value for you.
    There are no secret input formats, imports, annotations, or class wrappers.
    To run locally, save your function in practice.py, add a print(solve(...))
    call below it, and run `python practice.py` in a terminal with Python 3 installed.
    """, "Explain each character in def solve(a, b): and return a result without printing it.")
ex("add", "Add two integers", "a, b", "Return a + b. Both inputs are integers between -10000 and 10000.",
   "def solve(a, b):\n    return a + b", [("positive", "2, 3", 5), ("negative", "-4, 1", -3), ("zero", "0, 0", 0)],
   "Use the + operator on the two parameters.", "The function returns the arithmetic sum to its caller.", "O(1) time and space for these bounded integers.")
ex("minutes", "Split minutes", "minutes", "Return the number of complete hours in minutes (an integer from 0 to 10000). Ignore leftover minutes.",
   "def solve(minutes):\n    return minutes // 60", [("partial", "59", 0), ("exact", "120", 2), ("leftover", "125", 2), ("zero", "0", 0)],
   "An hour has 60 minutes. Integer floor division discards the remainder here.", "For nonnegative minutes, floor division counts complete groups of 60.", "O(1) time and space.")

lesson("Decisions and booleans", "1. Learn Python by coding", "Choose behavior with explicit conditions.", """
    `True` and `False` are boolean values. `==` compares values; `!=` means
    unequal; `<`, `<=`, `>` and `>=` compare order. `if condition:` executes its
    indented body only when the condition is true. `elif` tests another condition;
    `else` handles what remains. Only the first matching branch runs.
    `and` requires both conditions, `or` requires either, and `not` negates a
    condition. Parenthesize combined conditions while learning.

    A `return` inside an if ends the whole function, not just the branch.
    Keep later branches aligned with if. Try changing the example to -2 and 0.
    Python treats 0, empty containers and None as false, but use explicit
    comparisons until those containers have been introduced.
    """, """
    def label(n):
        if n < 0:
            return -1
        elif n == 0:
            return 0
        else:
            return 1

    print(label(4))
    print(True, False, 2 != 3, 2 <= 3, 4 >= 4, 4 > 2)
    print((2 > 0 and 2 < 5) or not (2 == 2))
    """, "Test the boundary itself and the values immediately on either side. Draw the branches before coding.",
    "Distinguish assignment from comparison and trace which branch runs.")
ex("sign", "Sign of an integer", "n", "Return -1 for negative n, 0 for zero, and 1 for positive n. n is an integer from -10000 to 10000.",
   "def solve(n):\n    if n < 0:\n        return -1\n    if n == 0:\n        return 0\n    return 1", [("negative", "-8", -1), ("zero", "0", 0), ("positive", "7", 1)],
   "Handle negative and zero with early returns; the remaining case is positive.", "Each early return eliminates one possibility.", "O(1) time and space.")
ex("even", "Nonnegative and even", "n", "Return True exactly when integer n is nonnegative and even; otherwise return False.",
   "def solve(n):\n    return n >= 0 and n % 2 == 0", [("even", "8", True), ("odd", "3", False), ("negative even", "-2", False), ("zero", "0", True)],
   "An even integer has remainder zero after division by two.", "Both predicates must hold. Zero is nonnegative and even.", "O(1) time and space.")

lesson("Loops and running state", "1. Learn Python by coding", "Repeat work and maintain a running answer.", """
    `for i in range(n):` visits 0 through n-1. The stop is excluded.
    `range(start, stop, step)` allows a starting value and positive or negative
    step. `while condition:` repeats until its condition is false; update state
    so that it terminates. `total += value` is shorthand for
    `total = total + value`; `i -= 1` subtracts one.
    `break` exits the nearest loop; `continue` starts its next iteration.
    Initialize the running answer before the loop, update it inside, and return
    after the loop. An empty range runs zero iterations.

    Trace i and total on paper for n=3. Returning inside the loop is a common
    bug: it stops after the first item. Write the invariant: total is the sum
    of all values processed so far. If the loop has no iterations, the initial
    value must already be the right answer.
    """, """
    def sum_to(n):
        total = 0
        for i in range(1, n + 1):
            total += i
        return total

    print(sum_to(3))
    i = 3
    while i > 0:
        i -= 1
        if i == 2:
            continue
        if i == 0:
            break
        print(i)
    for i in range(3, 0, -1):
        print(i)
    """, "A loop with n iterations and constant work per iteration takes O(n) time. This is how we count growth, not seconds.",
    "Trace a loop, including zero iterations, and explain why a while loop terminates.")
ex("sum-to", "Sum from one to n", "n", "Return 1 + 2 + ... + n using a loop. n is an integer from 0 to 1000; return 0 for n=0.",
   "def solve(n):\n    total = 0\n    for i in range(1, n + 1):\n        total += i\n    return total", [("three", "3", 6), ("zero", "0", 0), ("one", "1", 1), ("ten", "10", 55)],
   "The exclusive stop must be n + 1.", "After processing i, total contains the sum from 1 through i.", "O(n) time; O(1) auxiliary space.")
ex("digits", "Count decimal digits", "n", "Return the number of decimal digits of integer n, where 0 <= n <= 1000000000. Zero has one digit. Use integer division and a loop.",
   "def solve(n):\n    if n == 0:\n        return 1\n    count = 0\n    while n > 0:\n        n = n // 10\n        count += 1\n    return count", [("zero", "0", 1), ("single", "7", 1), ("multiple", "1020", 4), ("power of ten", "100", 3)],
   "Each division by ten removes one decimal digit; handle zero before the loop.", "Repeated floor division reduces a positive integer to zero.", "O(d) time for d digits; O(1) space.")

lesson("Lists and indexes", "1. Learn Python by coding", "Scan and build arrays safely.", """
    A list such as `[4, -2, 4]` stores ordered values, including duplicates.
    `[]` is empty. `len(nums)` counts items. `nums[0]` is the first item;
    `nums[len(nums)-1]` and `nums[-1]` are the last. These indexes are invalid
    on an empty list. `for value in nums:` visits values; `for i in range(len(nums)):`
    visits indexes. `nums[i] = value` replaces an item. `out.append(value)` adds
    one item to the end. A method is a function attached with a dot to a value.

    Lists are mutable: modifying them changes the original object. An index
    must be in bounds; do not assume the input has a first element unless the
    contract says so. Initialize a maximum from the first actual input value,
    not zero, when all inputs might be negative. First trace on one element,
    then two, then an empty list when allowed.
    """, """
    def doubled(nums):
        out = []
        for value in nums:
            out.append(value * 2)
        return out

    nums = [3, -2]
    nums[0] = 5
    print(len(nums), nums[-1], doubled(nums))
    """, "A scan visits each item once: O(n) time. A new list of n answers uses O(n) auxiliary space. append is amortized O(1).",
    "Choose a value loop or an index loop and handle an empty input deliberately.")
ex("count-positive", "Count positive entries", "nums", "Return how many entries are strictly greater than zero. nums contains 0 to 1000 integers; zero does not count.",
   "def solve(nums):\n    count = 0\n    for value in nums:\n        if value > 0:\n            count += 1\n    return count", [("mixed", "[-2, 0, 3, 3]", 2), ("empty", "[]", 0), ("none", "[-4, 0]", 0)],
   "Keep a counter and add one only in the positive branch.", "The counter describes exactly the entries already visited.", "O(n) time; O(1) auxiliary space.")
ex("maximum", "Maximum without max", "nums", "Return the greatest value in a nonempty list of 1 to 1000 integers. Use comparisons and a loop rather than a built-in maximum.",
   "def solve(nums):\n    best = nums[0]\n    for value in nums:\n        if value > best:\n            best = value\n    return best", [("mixed", "[3, 9, 2]", 9), ("all negative", "[-8, -2, -4]", -2), ("one", "[-5]", -5)],
   "Use nums[0] as the initial best so negative-only inputs work.", "best is the maximum of the processed prefix.", "O(n) time; O(1) auxiliary space.")

lesson("Strings and slices", "1. Learn Python by coding", "Treat text as a sequence and build new text.", """
    Strings are text in single or double quotes. `''` is empty. Indexing,
    len and for loops work as on lists, but strings are immutable: you cannot
    assign to `text[i]`. `text[start:stop]` copies a slice, excluding stop.
    Omitting a bound uses that end; `text[::-1]` makes a reversed copy using
    a step of -1. Slices clamp to valid bounds rather than raising IndexError.

    `ch in 'aeiou'` tests membership; `not in` negates it. `text.lower()`
    returns lowercased text. `text.split()` returns whitespace-separated words.
    `' '.join(words)` joins strings with spaces. `out = out + ch` concatenates
    strings; repeated growth can be quadratic because it creates new strings.
    For many characters, append to a list and join once. Equality compares
    full string contents. Our exercises specify lowercase ASCII to avoid
    surprising Unicode normalization or case rules.
    """, """
    text = 'Cat dog'
    print(text[0], text[1:3], text[::-1], text.lower())
    words = text.split()
    chars = []
    for ch in text:
        if ch not in 'aeiouAEIOU':
            chars.append(ch)
    print(''.join(chars), ' '.join(words), 'a' in 'cat', 'c' + 'at')
    """, "Scan characters when counting; use slices only when the copied data is needed. A length-k slice costs O(k) time and space.",
    "Explain the difference between an index and a slice, and why strings cannot be updated in place.")
ex("vowels", "Count vowels", "text", "Return the number of lowercase vowels a, e, i, o, u in text. text contains 0 to 1000 lowercase ASCII letters.",
   "def solve(text):\n    count = 0\n    for ch in text:\n        if ch in 'aeiou':\n            count += 1\n    return count", [("word", "'leetcode'", 4), ("empty", "''", 0), ("none", "'rhythm'", 0), ("all", "'aeiou'", 5)],
   "Use a character loop and membership in the fixed vowel string.", "The membership string has a fixed length of five, so each check is constant work.", "O(n) time; O(1) space.")
ex("reverse-words", "Reverse word order", "text", "Return the whitespace-separated words in reverse order, joined with single spaces. Leading, trailing and repeated spaces are allowed; text has at most 1000 ASCII characters. Empty input returns ''.",
   "def solve(text):\n    words = text.split()\n    return ' '.join(words[::-1])", [("normal", "'code every day'", 'day every code'), ("spacing", "'  a   b  '", 'b a'), ("empty", "''", ''), ("one", "'hi'", 'hi')],
   "split removes whitespace runs; reverse the resulting list with a slice, then join.", "A slice reverses a copy of the word list; join controls the output spacing.", "O(n) time and space for n characters.")

lesson("Dictionaries and frequency maps", "1. Learn Python by coding", "Associate keys with counts or positions.", """
    `{}` creates an empty dictionary. `{'a': 2}` maps key 'a' to value 2.
    `counts[key] = value` inserts or updates a mapping. Reading `counts[key]`
    for a missing key raises KeyError. `counts.get(key, 0)` returns zero when
    absent without inserting it. `key in counts` tests keys, not values.
    `for key in counts:` visits keys; `counts.items()` visits key-value pairs
    (pair unpacking comes next module, so use key loops for now).

    Integer and string keys are supported; lists cannot be keys. Count one
    occurrence at a time with counts[ch] = counts.get(ch, 0) + 1. Never change
    the dictionary's size while looping over it. Dictionaries preserve
    insertion order, but solve frequency problems using counts, not accidental
    ordering. Hash table operations take expected O(1), not a guaranteed
    worst-case O(1). A frequency table can use up to O(k) space for k keys.
    """, """
    counts = {}
    for ch in 'aba':
        counts[ch] = counts.get(ch, 0) + 1
    for key in counts:
        print(key, counts[key])
    print('a' in counts, counts.get('z', 0), counts.items())
    """, "Replace repeated full scans with one table-building pass. Separate 'build counts' from 'read counts' when order matters.",
    "Read and update a missing key safely, and explain why a list is not a dictionary key.")
ex("frequencies", "Build a frequency map", "nums", "Return a dictionary mapping each integer to its occurrence count. nums has 0 to 1000 integers. Insert keys in the order first seen; the course displays dictionaries in insertion order.",
   "def solve(nums):\n    counts = {}\n    for value in nums:\n        counts[value] = counts.get(value, 0) + 1\n    return counts", [("repeats", "[2, 1, 2]", {2: 2, 1: 1}), ("empty", "[]", {}), ("negative", "[-1, -1, 0]", {-1: 2, 0: 1})],
   "Start with an empty dictionary and update once per number.", "get supplies the initial count; assignment stores the incremented count.", "Expected O(n) time; O(k) space for k distinct values.")
ex("first-unique", "First unique character index", "text", "Return the index of the first character occurring exactly once, or -1 if none. text has 0 to 1000 lowercase ASCII letters.",
   "def solve(text):\n    counts = {}\n    for ch in text:\n        counts[ch] = counts.get(ch, 0) + 1\n    for i in range(len(text)):\n        if counts[text[i]] == 1:\n            return i\n    return -1", [("early", "'leetcode'", 0), ("later", "'aabbc'", 4), ("none", "'aabb'", -1), ("empty", "''", -1)],
   "Count first; scan indexes in original order second.", "The second pass guarantees the first qualifying index rather than an arbitrary unique character.", "O(n) time; O(1) space for a fixed alphabet.")

lesson("Sets, tuples and unpacking", "1. Learn Python by coding", "Track membership and carry small records.", """
    `set()` is an empty set; `{2, 3}` is a nonempty set (not a dictionary).
    `seen.add(x)` inserts; `seen.discard(x)` removes if present.
    `x in seen` and `x not in seen` test membership in expected O(1).
    Sets remove duplicates and have no promised iteration order.

    `(2, 3)` is a tuple: an immutable sequence. `(2,)` needs the comma for
    one item. A tuple of integers can be a dictionary key or set element.
    `a, b = pair` unpacks exactly two entries from a list or tuple.
    `a, b = b, a` swaps values
    using the original right-hand values. `for i, value in enumerate(nums):`
    visits index-value pairs. `for key, value in counts.items():` unpacks
    dictionary entries. `None` means no value; `is None` and `is not None`
    test that singleton by identity. Use `==` for numeric and text equality.
    """, """
    seen = set()
    seen.add(2)
    seen.discard(9)
    print(2 in seen, 3 not in seen, {2, 3})
    a, b = (2, 3)
    a, b = b, a
    for i, value in enumerate([7, 8]):
        print(i, value)
    for key, value in {'x': 2}.items():
        print(key, value)
    missing = None
    print(missing is None, missing is not None, (2,))
    """, "For Two Sum, look for the complement before inserting the current index. This prevents using one element twice.",
    "Choose a set for membership and a dictionary when the associated index is needed.")
ex("duplicates", "Contains a duplicate", "nums", "Return True if any integer occurs at least twice, otherwise False. nums has 0 to 1000 integers.",
   "def solve(nums):\n    seen = set()\n    for value in nums:\n        if value in seen:\n            return True\n        seen.add(value)\n    return False", [("duplicate", "[1, 2, 1]", True), ("distinct", "[1, 2]", False), ("empty", "[]", False), ("zero pair", "[0, 0]", True)],
   "Check whether a value is already in the set before adding it.", "The set contains precisely the earlier values.", "Expected O(n) time; O(n) space.")
ex("two-sum", "Two Sum", "nums, target", "Return [i, j], i < j, for the two entries summing to target, or [] if absent. nums has 0 to 1000 integers. At most one index pair qualifies. Never reuse an index.",
   "def solve(nums, target):\n    seen = {}\n    for i, value in enumerate(nums):\n        need = target - value\n        if need in seen:\n            return [seen[need], i]\n        seen[value] = i\n    return []", [("pair", "[2, 7, 11, 15], 9", [0, 1]), ("equal values", "[3, 3], 6", [0, 1]), ("single cannot reuse", "[3], 6", []), ("empty", "[], 5", [])],
   "Map previously seen values to indexes; look up target - value first.", "A hit is always an earlier, distinct index. The single-pair contract removes tie ambiguity.", "Expected O(n) time; O(n) space.")

lesson("Sorting, helpers and copying", "2. Solve array and string patterns", "Use only explained conveniences and reason about their costs.", """
    `sorted(nums)` returns a new sorted list; `nums.sort()` mutates a list and
    returns None. `reverse=True` sorts descending. A keyword argument names
    an option. `key=first` uses the function first to compute a comparison key;
    do not write first() there because you are passing the function itself.
    `min(a, b)`, `max(a, b)`, `abs(x)` and `sum(nums)` return smaller, larger,
    absolute value and sum. These helpers do not replace understanding a scan.

    `copy = nums[:]` copies a list shallowly. `alias = nums` shares it.
    `[0] * n` creates a flat list of zeros. For rows, use
    `[[0] * cols for _ in range(rows)]`: a list comprehension evaluates the
    expression before for once per item. `_` is an ordinary unused variable.
    Never use `[[0] * cols] * rows`: all rows then share one list.
    Comprehensions are optional; the earlier append loop always works.

    Big O measures growth as n increases. One scan is O(n); nested full scans
    are O(n squared); halving repeatedly is O(log n). Sorting is O(n log n).
    A built-in may hide a loop: sum and list copying are O(n). Python sorting
    may use O(n) auxiliary memory. Count output storage separately from working
    storage. No timed tests here prove an asymptotic claim: explain it yourself.
    """, """
    def first(pair):
        return pair[0]

    nums = [3, 1, 2]
    copy = nums[:]
    alias = nums
    copy.sort(reverse=True)
    print(nums, copy, sorted(nums), min(3, 1), max(3, 1), abs(-4), sum(nums))
    print(sorted([[2, 9], [1, 8]], key=first))
    grid = [[0] * 2 for _ in range(2)]
    grid[0][0] = 7
    print(grid, alias)
    """, "Sorting can simplify comparisons, but ask whether it destroys original indexes or order. State the cost of every helper.",
    "Explain mutation versus copying, sort versus sorted, and why repeated rows can alias.")
ex("squares", "Sorted squares: first solution", "nums", "Return the squares of all integers in ascending order. nums has 0 to 1000 integers. Do not mutate the input. This first version may sort.",
   "def solve(nums):\n    out = []\n    for value in nums:\n        out.append(value * value)\n    return sorted(out)", [("mixed", "[-4, -1, 0, 3]", [0, 1, 9, 16]), ("empty", "[]", []), ("negative", "[-3, -2]", [4, 9])],
   "Square each value, then sort the new list.", "Squaring does not preserve signed order, so sorting is necessary for this approach.", "O(n log n) time; O(n) space including output and sorting.")
ex("closest-zero", "Closest value to zero", "nums", "Return the integer closest to zero in a nonempty list of at most 1000 integers. If both -x and x are equally close, prefer x.",
   "def solve(nums):\n    best = nums[0]\n    for value in nums:\n        if abs(value) < abs(best) or (abs(value) == abs(best) and value > best):\n            best = value\n    return best", [("tie", "[-2, 2, 5]", 2), ("negative", "[-7, -1]", -1), ("zero", "[3, 0, -1]", 0), ("one", "[6]", 6)],
   "Compare absolute values first, then apply the positive tie rule.", "The tie rule is explicit; input order cannot change the answer.", "O(n) time; O(1) space.")

lesson("Two pointers", "2. Solve array and string patterns", "Move boundaries using a stated invariant.", """
    No new syntax. Use two integer indexes and a while loop. On a sorted list,
    the smallest and largest remaining values bound a candidate pair. If their
    sum is too small, advancing left is safe: pairing the same left with an
    even smaller right could not help. If too large, decrease right.
    Stop when left >= right so one element is never used twice.

    For a palindrome, compare the two end characters and move inward. Return
    False on a mismatch, True after all pairs match. Empty and single-character
    strings are palindromes under this definition. Trace the indexes explicitly;
    neither slicing nor copying is required. In both patterns each pointer
    moves in one direction at most n times, so the loop is linear.
    """, """
    def palindrome(text):
        left = 0
        right = len(text) - 1
        while left < right:
            if text[left] != text[right]:
                return False
            left += 1
            right -= 1
        return True

    print(palindrome('abba'))
    """, "Before moving a pointer, say which candidates are eliminated and why. A sorted-input contract is essential for the pair-sum rule.",
    "Justify pointer movement rather than memorizing it.")
ex("palindrome", "Exact palindrome", "text", "Return whether text reads identically forward and backward. text has 0 to 1000 lowercase ASCII letters. Use two pointers without a reversed copy.",
   "def solve(text):\n    left = 0\n    right = len(text) - 1\n    while left < right:\n        if text[left] != text[right]:\n            return False\n        left += 1\n        right -= 1\n    return True", [("even", "'abba'", True), ("mismatch", "'abca'", False), ("empty", "''", True), ("single", "'a'", True)],
   "Compare the endpoints; move both inward after a match.", "Every pair outside the active range has already matched.", "O(n) time; O(1) space.")
ex("sorted-pair", "Pair in a sorted array", "nums, target", "Return [i, j] with i < j for two entries summing to target, or []. nums is sorted ascending, has at most 1000 integers, and at most one index pair qualifies. Use constant auxiliary space.",
   "def solve(nums, target):\n    left = 0\n    right = len(nums) - 1\n    while left < right:\n        total = nums[left] + nums[right]\n        if total == target:\n            return [left, right]\n        if total < target:\n            left += 1\n        else:\n            right -= 1\n    return []", [("pair", "[1, 3, 4, 8], 7", [1, 2]), ("equal", "[2, 2], 4", [0, 1]), ("absent", "[1, 3], 8", []), ("empty", "[], 3", [])],
   "Compare the endpoint sum to target; eliminate one endpoint each time.", "Sorted order makes each elimination safe.", "O(n) time; O(1) auxiliary space.")

lesson("Sliding windows", "2. Solve array and string patterns", "Update a contiguous range instead of recomputing it.", """
    No new syntax. A window represents contiguous indexes left through right.
    For fixed width k, add the incoming value and subtract the outgoing value
    once the window grows too large. Record answers only for complete windows.
    Initializing best to zero is incorrect for all-negative windows; initialize
    it from the first complete window or use None and an explicit test.

    For a variable window with nonnegative inputs, extend right and shrink left
    while the window violates its limit. Nonnegative values make shrinking
    reduce the sum; this proof fails with negative numbers. For unique text,
    a last-seen index table lets left jump past a repeated character. Use
    max(left, previous + 1) so left never moves backward. Every item enters and
    leaves at most once: nested loops can still total O(n) work.
    """, """
    def longest_distinct(text):
        last = {}
        left = 0
        best = 0
        for right, ch in enumerate(text):
            if ch in last:
                left = max(left, last[ch] + 1)
            last[ch] = right
            best = max(best, right - left + 1)
        return best

    print(longest_distinct('abba'))
    """, "Write what makes the current window valid, when you shrink it, and when you record its length or sum.",
    "Explain why a left boundary never retreats, and why input signs can matter.")
ex("fixed-window", "Maximum sum of k consecutive values", "nums, k", "Return the maximum sum of a contiguous length-k window. nums has 1 to 1000 integers; 1 <= k <= len(nums). Negative values are allowed.",
   "def solve(nums, k):\n    current = sum(nums[:k])\n    best = current\n    for right in range(k, len(nums)):\n        current += nums[right] - nums[right - k]\n        best = max(best, current)\n    return best", [("mixed", "[1, 4, -2, 5], 2", 5), ("negative", "[-5, -2, -3], 2", -5), ("whole", "[1, 2], 2", 3), ("one", "[-4], 1", -4)],
   "Start with the first k entries, then replace one outgoing value each step.", "The running sum always describes exactly k consecutive values.", "O(n) time; O(k) temporary space for the initial slice (can be reduced to O(1) with a loop).")
ex("unique-window", "Longest substring without repeats", "text", "Return the length of the longest contiguous substring with no repeated character. text has at most 1000 lowercase ASCII letters; empty returns 0.",
   "def solve(text):\n    last = {}\n    left = 0\n    best = 0\n    for right, ch in enumerate(text):\n        if ch in last:\n            left = max(left, last[ch] + 1)\n        last[ch] = right\n        best = max(best, right - left + 1)\n    return best", [("typical", "'abcabcbb'", 3), ("do not retreat", "'abba'", 2), ("empty", "''", 0), ("all same", "'aaaa'", 1)],
   "Keep last-seen indexes and move left past a repeated character only when needed.", "The active range contains no duplicate characters; max prevents an old occurrence from moving left backward.", "O(n) time; O(1) space for the fixed alphabet.")

lesson("Prefix sums", "2. Solve array and string patterns", "Summarize everything before an index.", """
    No new syntax. Define prefix[0] = 0 and append one cumulative sum per
    input value. prefix[i] is the sum of the first i values. Therefore an
    inclusive range [left, right] sums to prefix[right+1] - prefix[left].
    The extra leading zero handles ranges starting at index zero uniformly.

    For subarray sums equal to k, a current prefix total s needs an earlier
    prefix s-k. Count earlier prefix sums in a dictionary. Seed {0: 1} for the
    empty prefix; otherwise subarrays starting at zero disappear. Look up the
    needed count before inserting the current prefix so an empty subarray
    is not counted. Unlike the nonnegative sliding-sum rule, this method works
    with negative numbers and zeroes. Trace [1, -1, 0] with k=0.
    """, """
    nums = [2, -1, 4]
    prefix = [0]
    for value in nums:
        prefix.append(prefix[-1] + value)
    left, right = 1, 2
    print(prefix[right + 1] - prefix[left])  # 3
    """, "Choose prefixes for repeated static range queries or count-of-earlier-total problems. Name exactly what the dictionary counts.",
    "Explain both the leading zero and why a frequency map starts at {0: 1}.")
ex("range-sums", "Static range sums", "nums, queries", "Return one sum per inclusive query [left, right], in order. nums has 1 to 1000 integers; queries has 0 to 1000 valid ranges with 0 <= left <= right < len(nums).",
   "def solve(nums, queries):\n    prefix = [0]\n    for value in nums:\n        prefix.append(prefix[-1] + value)\n    out = []\n    for left, right in queries:\n        out.append(prefix[right + 1] - prefix[left])\n    return out", [("ranges", "[2, -1, 4], [[0, 2], [1, 1], [1, 2]]", [5, -1, 3]), ("no queries", "[8], []", []), ("single", "[-3], [[0, 0]]", [-3])],
   "Build n+1 prefixes, then subtract the prefix before the query from the one after it.", "Each query cancels values outside its range.", "O(n+q) time; O(n) working space plus O(q) output.")
ex("subarray-k", "Count subarrays with sum k", "nums, k", "Return the count of nonempty contiguous subarrays summing to integer k. nums has 0 to 1000 integers, including negatives.",
   "def solve(nums, k):\n    counts = {0: 1}\n    total = 0\n    answer = 0\n    for value in nums:\n        total += value\n        answer += counts.get(total - k, 0)\n        counts[total] = counts.get(total, 0) + 1\n    return answer", [("positive", "[1, 1, 1], 2", 2), ("zeroes", "[0, 0], 0", 3), ("negative", "[1, -1, 0], 0", 3), ("empty", "[], 0", 0)],
   "Count how many previous prefix totals equal current total minus k.", "Multiple identical prefixes correspond to different starting positions, so store frequencies rather than a set.", "Expected O(n) time; O(n) space.")

lesson("Binary search and boundaries", "2. Solve array and string patterns", "Halve a search interval without losing an answer.", """
    No new syntax. Use a half-open interval [left, right): left is included,
    right is excluded. Start with left=0 and right=len(nums).
    While left < right, mid=(left+right)//2. If nums[mid] < target, all indexes
    through mid can be eliminated: left=mid+1. Otherwise right=mid. At exit,
    left is the first position whose value is at least target, possibly n.
    Check left < len(nums) before reading nums[left]. Short-circuit `and`
    only evaluates the second operand if the first is true, making that guard safe.

    A lower bound handles duplicates predictably. Never mix this interval
    convention with an inclusive right=n-1 template. Every iteration shrinks
    the interval. The same idea searches a monotone yes/no feasibility test
    over answer values, once you have justified monotonicity.
    """, """
    def lower_bound(nums, target):
        left = 0
        right = len(nums)
        while left < right:
            mid = (left + right) // 2
            if nums[mid] < target:
                left = mid + 1
            else:
                right = mid
        return left

    print(lower_bound([1, 3, 3, 8], 3))
    """, "Write the interval convention and the meaning of the answer before coding. Test absent-before, absent-after, duplicates and empty input.",
    "Derive an update from the interval invariant and prove the interval shrinks.")
ex("insert-position", "Search insert position", "nums, target", "Return the first index with value >= target, or len(nums) if none. nums is sorted ascending and has 0 to 1000 integers. Duplicates are allowed.",
   "def solve(nums, target):\n    left = 0\n    right = len(nums)\n    while left < right:\n        mid = (left + right) // 2\n        if nums[mid] < target:\n            left = mid + 1\n        else:\n            right = mid\n    return left", [("duplicates", "[1, 3, 3, 8], 3", 1), ("gap", "[1, 3], 2", 1), ("after", "[1, 3], 9", 2), ("before", "[1, 3], 0", 0), ("empty", "[], 2", 0)],
   "Use [left, right) and move right to mid when the midpoint could be the first answer.", "Equality stays in the search range, so the leftmost equal value survives.", "O(log n) time; O(1) space.")
ex("sqrt", "Integer square root", "n", "Return the largest integer x such that x*x <= n. n is an integer from 0 to 1000000000. Use binary search rather than a square-root helper.",
   "def solve(n):\n    left = 0\n    right = n + 1\n    while left < right:\n        mid = (left + right) // 2\n        if mid * mid <= n:\n            left = mid + 1\n        else:\n            right = mid\n    return left - 1", [("zero", "0", 0), ("one", "1", 1), ("square", "16", 4), ("between", "8", 2), ("large", "1000000000", 31622)],
   "Find the first integer whose square is too large, then subtract one.", "The predicate x*x > n is monotone. The first failing value is one beyond the floor root.", "O(log(n+1)) time; O(1) space.")

lesson("Stacks and monotonic stacks", "3. Learn data structures", "Store unfinished work in last-in, first-out order.", """
    `stack.pop()` removes and returns the last list item. It raises IndexError
    on an empty list. Guard it with `len(stack) > 0`; `and` short-circuits.
    append is push, pop is removal, stack[-1] peeks. Each is amortized O(1)
    at the list end. Removing from the front of a list costs O(n).

    A bracket stack stores openings whose matching closings have not arrived.
    Reject a closing with no opening or the wrong opening; accept only when
    no opening remains. A monotonic stack instead maintains ordered values
    or their indexes. For next-greater problems, a larger current value resolves
    every smaller pending value at the top. Store indexes when answers depend
    on distances. Although one iteration may pop many items, each item is
    pushed once and popped at most once: total O(n) work (amortized analysis).
    """, """
    stack = []
    stack.append(4)
    stack.append(7)
    if len(stack) > 0:
        print(stack[-1], stack.pop())
    print(stack)
    """, "Ask what each pending stack entry is waiting for, and what event makes it safe to pop.",
    "Explain a stack invariant and the total number of pushes and pops.")
ex("brackets", "Valid brackets", "text", "Return whether text is properly nested. text contains only ()[]{} and has at most 1000 characters. Empty is valid.",
   "def solve(text):\n    matching = {')': '(', ']': '[', '}': '{'}\n    stack = []\n    for ch in text:\n        if ch in '([{':\n            stack.append(ch)\n        else:\n            if len(stack) == 0 or stack.pop() != matching[ch]:\n                return False\n    return len(stack) == 0", [("nested", "'([]{})'", True), ("crossed", "'([)]'", False), ("early close", "')'", False), ("leftover", "'('", False), ("empty", "''", True)],
   "Push openings; for a closing, require the matching most recent opening.", "Short-circuit or avoids popping an empty stack.", "O(n) time; O(n) space.")
ex("temperatures", "Days until a warmer temperature", "temps", "Return one distance per day to the next strictly warmer day, or 0 if none. temps has 0 to 1000 integer temperatures. Equal is not warmer.",
   "def solve(temps):\n    out = [0] * len(temps)\n    stack = []\n    for i, value in enumerate(temps):\n        while len(stack) > 0 and temps[stack[-1]] < value:\n            previous = stack.pop()\n            out[previous] = i - previous\n        stack.append(i)\n    return out", [("mixed", "[73, 74, 75, 71, 69, 72, 76, 73]", [1, 1, 4, 2, 1, 1, 0, 0]), ("equal", "[70, 70]", [0, 0]), ("falling", "[3, 2, 1]", [0, 0, 0]), ("empty", "[]", [])],
   "Keep indexes of unresolved days with nonincreasing temperatures.", "A warmer day resolves pending colder days; unresolved indexes retain zero.", "O(n) time; O(n) space including output.")

lesson("Imports, queues and BFS", "3. Learn data structures", "Process work in first-in, first-out order.", """
    `from collections import deque` loads deque from Python's standard library;
    no installation is needed. `deque([start])` constructs a queue.
    `.append(x)` adds at the right, `.popleft()` removes from the left, and
    `.appendleft(x)` adds at the left, all in O(1). Guard removal from empty.
    A library name must be imported before use. You may put imports above def.

    Breadth-first search (BFS) expands the closest pending state first. Store
    (state, distance) tuples and mark states visited when enqueued, so the same
    state is not scheduled repeatedly. With unit-cost edges, the first time
    a state is reached gives its shortest distance. This does not apply to
    arbitrary weighted edges. A queue implementation using list.pop(0) shifts
    all remaining entries and can make an otherwise linear traversal quadratic.
    """, """
    from collections import deque

    queue = deque([(0, 0)])
    seen = {0}
    while len(queue) > 0:
        position, distance = queue.popleft()
        print(position, distance)
        for nxt in [position + 1, position + 2]:
            if nxt <= 3 and nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, distance + 1))
    queue.appendleft((9, 9))
    print(queue.popleft())
    """, "Separate the queue's pending work from the visited set. The set records discovery, not completion.",
    "Choose stack versus queue and explain when BFS proves a shortest path.")
ex("queue-ops", "Queue operations", "ops", "ops is a list of at most 1000 two-item lists [action, value]. action is 'add' or 'take'. Add enqueues value; take ignores value and records the oldest item, or -1 if empty. Return recorded removals.",
   "from collections import deque\n\ndef solve(ops):\n    queue = deque()\n    out = []\n    for action, value in ops:\n        if action == 'add':\n            queue.append(value)\n        elif len(queue) > 0:\n            out.append(queue.popleft())\n        else:\n            out.append(-1)\n    return out", [("fifo", "[['add', 2], ['add', 4], ['take', 0], ['take', 0]]", [2, 4]), ("empty take", "[['take', 0]]", [-1]), ("no ops", "[]", [])],
   "Use deque; add on the right and take from the left.", "The output records only take operations. The -1 rule makes empty behavior explicit.", "O(n) time; O(n) space.")
ex("number-bfs", "Fewest increments", "target", "Start at 0; each move adds 1 or 2. Return the fewest moves to target, an integer from 0 to 100. Practice BFS even though an arithmetic formula exists. Do not visit positions beyond target.",
   "from collections import deque\n\ndef solve(target):\n    queue = deque([(0, 0)])\n    seen = {0}\n    while len(queue) > 0:\n        position, distance = queue.popleft()\n        if position == target:\n            return distance\n        for nxt in [position + 1, position + 2]:\n            if nxt <= target and nxt not in seen:\n                seen.add(nxt)\n                queue.append((nxt, distance + 1))\n    return -1", [("zero", "0", 0), ("one", "1", 1), ("odd", "7", 4), ("even", "10", 5)],
   "Queue position-distance pairs; return when target is removed from the queue.", "FIFO order processes distances in increasing layers, making the first target distance minimal.", "O(target+1) time and space.")

lesson("Recursion and the call stack", "3. Learn data structures", "Define a smaller subproblem and a stopping case.", """
    A function may call itself: that is recursion, using the function-call
    syntax you already know. Every call has its own parameters and local
    variables. A base case returns without another call. Each recursive path
    must move toward that base case. The caller waits for the smaller result
    and then combines it. Trace the descent and the return separately.

    Returning a recursive result is essential: merely calling the function
    discards its answer. Recursion uses stack space proportional to maximum
    depth. Python has a recursion depth limit; this course bounds recursive
    inputs to safe depths. For large adversarial trees or graphs, use an
    explicit stack or queue instead of assuming recursion is unlimited.
    Do not raise the recursion limit as a substitute for choosing an algorithm.
    """, """
    def factorial(n):
        if n <= 1:
            return 1
        smaller = factorial(n - 1)
        return n * smaller

    print(factorial(4))  # 24
    """, "State three things: the base case, the smaller argument, and how its returned result builds this result.",
    "Trace call frames and account for stack space.")
ex("factorial", "Recursive factorial", "n", "Return n! using recursion. n is an integer from 0 to 12; 0! is 1.",
   "def solve(n):\n    if n <= 1:\n        return 1\n    return n * solve(n - 1)", [("zero", "0", 1), ("one", "1", 1), ("four", "4", 24), ("six", "6", 720)],
   "Stop at 0 or 1. Multiply n by the factorial of n-1.", "Each recursive call reduces n and each waiting frame stores constant information.", "O(n) time; O(n) call-stack space.")
ex("digit-sum", "Recursive digit sum", "n", "Return the sum of decimal digits using recursion. n is an integer from 0 to 1000000000.",
   "def solve(n):\n    if n < 10:\n        return n\n    return n % 10 + solve(n // 10)", [("zero", "0", 0), ("one digit", "7", 7), ("multiple", "1024", 7), ("zeroes", "1000", 1)],
   "Separate the last digit with % and recurse on the remaining digits with //.", "The integer loses a digit each call, so it reaches the single-digit base case.", "O(d) time and stack space for d digits.")

lesson("Nested helpers and backtracking", "4. Traverse and search", "Explore choices, copy answers, and undo mutations.", """
    `def visit(index):` may be defined inside solve. It can read names from
    solve's enclosing scope, such as path and out. Calling path.append(...)
    mutates that shared list; it does not rebind the name. We avoid assigning
    to enclosing scalar names, which would require additional syntax.
    No nonlocal or global declaration is needed in these exercises.
    A bare `return` exits the function with the value None; here it stops
    visiting a finished branch after its answer has been recorded.

    Backtracking is choose -> explore -> undo. Keep one mutable path and
    remove its last item with pop after returning. When recording an answer,
    append path[:] rather than path itself, so later mutations cannot change
    recorded answers. A branching recursion tree can have exponentially many
    outputs. For subsets, each of n values is either excluded or included:
    there are 2**n answers and copying them costs O(n * 2**n) time and space.
    Explore branches in the documented order because our checker compares lists.
    """, """
    def choices(n):
        path = []
        out = []
        def visit(index):
            if index == n:
                out.append(path[:])
                return
            visit(index + 1)
            path.append(index)
            visit(index + 1)
            path.pop()
        visit(0)
        return out

    print(choices(2))  # [[], [1], [0], [0, 1]]
    """, "Record a path snapshot at a complete answer. After every recursive call, restore exactly the state that existed before the choice.",
    "Explain why appending the path without copying would corrupt earlier answers.")
ex("subsets", "All subsets", "nums", "Return every subset of a list of 0 to 10 distinct integers. Process indexes left to right; explore exclusion before inclusion. Preserve original order within subsets. The empty list produces [[]].",
   "def solve(nums):\n    out = []\n    path = []\n    def visit(index):\n        if index == len(nums):\n            out.append(path[:])\n            return\n        visit(index + 1)\n        path.append(nums[index])\n        visit(index + 1)\n        path.pop()\n    visit(0)\n    return out", [("two", "[1, 2]", [[], [2], [1], [1, 2]]), ("empty", "[]", [[]]), ("one", "[9]", [[], [9]])],
   "At each index, recurse without the value, then append it, recurse, and pop it.", "Every sequence of inclusion decisions produces one distinct subset; copying freezes its current path.", "O(n * 2**n) time and output space; O(n) additional stack/path.")
ex("binary-strings", "Binary strings without adjacent ones", "n", "Return all length-n strings of '0' and '1' without '11', in lexicographic order (try '0' first). n is from 0 to 10. For n=0 return [''].",
   "def solve(n):\n    out = []\n    def visit(text):\n        if len(text) == n:\n            out.append(text)\n            return\n        visit(text + '0')\n        if len(text) == 0 or text[-1] != '1':\n            visit(text + '1')\n    visit('')\n    return out", [("zero", "0", ['']), ("one", "1", ['0', '1']), ("two", "2", ['00', '01', '10']), ("three", "3", ['000', '001', '010', '100', '101'])],
   "Always allow 0; allow 1 only at the start or after 0.", "Pruning rejects invalid prefixes before exploring their descendants. Immutable strings require no undo step.", "O(n * 2**n) upper bound on time and output space; O(n squared) upper bound for live copied prefixes.")

NODE = "class ListNode:\n    def __init__(self, val, next=None):\n        self.val = val\n        self.next = next\n\n"
lesson("Classes, objects and linked lists", "4. Traverse and search", "Follow references rather than array indexes.", """
    `class ListNode:` defines an object shape. `def __init__(self, val, next=None):`
    initializes each new object. self is that object; `self.val = val` stores
    a field. A default parameter is used when the caller omits it.
    `ListNode(3)` constructs an object; Python supplies self automatically.
    `.next` holds another node or None. Variable names hold references;
    assigning a reference does not copy a node. `is` compares object identity.

    Walk with node = node.next until node is None. A linked list has no constant
    time indexed access. For a middle node, move slow once and fast twice;
    guard fast and fast.next before following two links. In a cycle, traversal
    may never reach None; fast and slow eventually meet by object identity.
    Node equality for cycle detection is about the same node, not equal values.
    The provided class is part of the starter and has now been fully taught.
    """, NODE + """head = ListNode(4, ListNode(7))
node = head
while node is not None:
    print(node.val)
    node = node.next
print(head is head, head is head.next)
""", "Draw boxes for objects and arrows for references. Trace empty, one-node, two-node and cyclic structures before coding.",
    "Explain self, constructor calls, default arguments, field access and identity.")
ex("middle", "Middle node value", "head", "head is None or the head of an acyclic list with at most 100 nodes. Return the middle node's val, choosing the second middle for even length. Return None for empty. Keep the supplied ListNode definition.",
   "def solve(head):\n    slow = head\n    fast = head\n    while fast is not None and fast.next is not None:\n        slow = slow.next\n        fast = fast.next.next\n    if slow is None:\n        return None\n    return slow.val", [("odd", "ListNode(1, ListNode(2, ListNode(3)))", 2), ("even", "ListNode(1, ListNode(2))", 2), ("one", "ListNode(8)", 8), ("empty", "None", None)],
   "Start both references at head; move fast two links and slow one.", "When fast reaches the end, slow has taken half as many steps, choosing the second middle.", "O(n) time; O(1) space.", prelude=NODE)
ex("cycle", "Detect a linked-list cycle", "head", "Return True if following next references repeats a node, otherwise False. There are at most 100 distinct ListNode objects. Equal values alone are not a cycle. Tests show how cyclic fixtures are constructed.",
   "def solve(head):\n    slow = head\n    fast = head\n    while fast is not None and fast.next is not None:\n        slow = slow.next\n        fast = fast.next.next\n        if slow is fast:\n            return True\n    return False", [("cycle", "cycle", True), ("equal values no cycle", "ListNode(1, ListNode(1))", False), ("self cycle", "self_cycle", True), ("empty", "None", False)],
   "Move first, then compare node identity; both references initially equal head even in an acyclic list.", "Within a finite cycle, the relative gap changes by one per step until the references meet.", "O(n) time; O(1) space.", setup="cycle = ListNode(1, ListNode(2))\ncycle.next.next = cycle\nself_cycle = ListNode(9)\nself_cycle.next = self_cycle", prelude=NODE)

TREE = "class TreeNode:\n    def __init__(self, val, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n"
lesson("Binary trees: DFS and BFS", "4. Traverse and search", "Combine child results and traverse levels.", """
    TreeNode uses the same class syntax as ListNode, with .left and .right
    instead of .next. A missing child is None. The root is the entry reference.
    A tree here is acyclic and each node has at most one parent.
    Depth is measured in nodes: an empty tree has depth 0, a leaf depth 1.
    Recursive depth is 1 + max(left depth, right depth).

    Depth-first traversal follows a child fully before another. Inorder means
    left subtree -> node -> right subtree. A binary search tree additionally
    orders keys, but these exercises accept any binary tree. For breadth-first
    traversal, enqueue children of each removed node. To collect separate
    levels, read the queue length before processing that layer.
    Both DFS and BFS visit n nodes in O(n) time. DFS uses O(h) stack depth;
    BFS uses O(w) queued nodes at the widest level. Recursion exercises cap
    trees at 100 nodes; an arbitrarily skewed large tree needs an explicit stack.
    """, TREE + """def depth(root):
    if root is None:
        return 0
    return 1 + max(depth(root.left), depth(root.right))

root = TreeNode(2, TreeNode(1), TreeNode(3))
print(depth(root), root.left.val, root.right.val)
""", "Define what each recursive call returns. Keep 'visit order' separate from 'what result this call computes'.",
    "Trace a tree by object references and explain depth versus breadth memory use.")
ex("tree-depth", "Maximum tree depth", "root", "Return maximum depth measured in nodes. root is None or a TreeNode in an acyclic binary tree with at most 100 nodes. Empty depth is 0.",
   "def solve(root):\n    if root is None:\n        return 0\n    return 1 + max(solve(root.left), solve(root.right))", [("balanced", "TreeNode(2, TreeNode(1), TreeNode(3))", 2), ("skewed", "TreeNode(1, None, TreeNode(2, None, TreeNode(3)))", 3), ("leaf", "TreeNode(5)", 1), ("empty", "None", 0)],
   "The base case is None; take the larger child depth and add one.", "Every node returns the height of its own subtree.", "O(n) time; O(h) recursion space.", prelude=TREE)
ex("tree-inorder", "Inorder traversal", "root", "Return values in left-node-right order. root is None or the root of an acyclic TreeNode tree with at most 100 nodes; it need not be a BST.",
   "def solve(root):\n    out = []\n    def visit(node):\n        if node is None:\n            return\n        visit(node.left)\n        out.append(node.val)\n        visit(node.right)\n    visit(root)\n    return out", [("balanced", "TreeNode(2, TreeNode(1), TreeNode(3))", [1, 2, 3]), ("not bst", "TreeNode(9, TreeNode(7), TreeNode(1))", [7, 9, 1]), ("empty", "None", []), ("right only", "TreeNode(1, None, TreeNode(2))", [1, 2])],
   "Reuse the nested helper pattern and append between the two recursive calls.", "Appending between left and right produces inorder regardless of numeric ordering.", "O(n) time; O(h) working stack plus O(n) output.", prelude=TREE)

lesson("Graphs and grids", "4. Traverse and search", "Represent neighbors and avoid repeated work.", """
    No new syntax. An adjacency list graph[u] contains the outgoing neighbors
    of vertex u. Vertices are integers from 0 to len(graph)-1. In a directed
    graph, u -> v does not imply v -> u; an undirected representation includes
    both. A visited set prevents cycles and duplicate scheduling. Mark visited
    when pushing or enqueuing, not after repeated discoveries.

    A grid is a list of row lists. grid[row][col] uses two indexes. Check
    0 <= row < rows and 0 <= col < cols with the explicit and conditions shown
    below before indexing. A tuple (row, col) is a hashable visited key.
    Four-direction movement adds (-1,0), (1,0), (0,-1), (0,1).
    An explicit stack does DFS; deque does BFS. Flood fill processes each
    reachable cell once; restart from every unvisited land cell to count
    islands. Do not mutate input when a separate visited set suffices.
    """, """
    grid = [[1, 0], [1, 1]]
    row, col = 0, 0
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + dr, col + dc
        if nr >= 0 and nr < len(grid) and nc >= 0 and nc < len(grid[0]):
            print(nr, nc, grid[nr][nc])
    seen = {(0, 0)}
    print((row, col) in seen)
    """, "State vertices, edges, direction, and movement rules before choosing a traversal. O(V+E) counts vertices plus adjacency entries.",
    "Explain visited timing, bounds checks, and why BFS rather than DFS finds a shortest unweighted path.")
ex("graph-distance", "Shortest unweighted directed path", "graph, start, target", "graph is an adjacency list with 1 to 100 vertices and valid integer neighbors. Return the fewest directed edges from start to target, or -1 if unreachable. Both vertices are valid. Cycles and self-edges are allowed.",
   "from collections import deque\n\ndef solve(graph, start, target):\n    queue = deque([(start, 0)])\n    seen = {start}\n    while len(queue) > 0:\n        node, distance = queue.popleft()\n        if node == target:\n            return distance\n        for neighbor in graph[node]:\n            if neighbor not in seen:\n                seen.add(neighbor)\n                queue.append((neighbor, distance + 1))\n    return -1", [("shortest", "[[1, 2], [3], [3], []], 0, 3", 2), ("cycle unreachable", "[[1], [0], []], 0, 2", -1), ("same", "[[]], 0, 0", 0), ("directed", "[[1], []], 1, 0", -1)],
   "Adapt the number BFS: neighbors now come from graph[node].",
   "FIFO order guarantees minimum edges; visited prevents infinite cycling.", "O(V+E) time; O(V) space.")
ex("islands", "Count islands", "grid", "Return the number of four-directionally connected groups of 1 cells. grid is [] or a rectangular grid with at most 30 rows and 30 columns; cells are integer 0 or 1. An empty row is allowed. Do not mutate grid.",
   "def solve(grid):\n    if len(grid) == 0:\n        return 0\n    rows = len(grid)\n    cols = len(grid[0])\n    seen = set()\n    count = 0\n    for row in range(rows):\n        for col in range(cols):\n            if grid[row][col] == 1 and (row, col) not in seen:\n                count += 1\n                seen.add((row, col))\n                stack = [(row, col)]\n                while len(stack) > 0:\n                    r, c = stack.pop()\n                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:\n                        nr, nc = r + dr, c + dc\n                        if nr >= 0 and nr < rows and nc >= 0 and nc < cols:\n                            if grid[nr][nc] == 1 and (nr, nc) not in seen:\n                                seen.add((nr, nc))\n                                stack.append((nr, nc))\n    return count", [("two", "[[1, 1, 0], [0, 0, 1]]", 2), ("diagonal separate", "[[1, 0], [0, 1]]", 2), ("water", "[[0, 0]]", 0), ("empty", "[]", 0), ("empty row", "[[]]", 0)],
   "Each unseen land cell begins one flood fill. Mark neighbors when pushing them.", "Each flood fill claims exactly one connected component; restarting counts all components.", "O(rows * cols) time and space.")

lesson("Heaps and priority queues", "5. Build interview solutions", "Keep the best pending candidate available.", """
    `import heapq` loads a standard module. `heapq.heapify(values)` mutates a
    list into a min-heap in O(n). `heapq.heappush(heap, x)` inserts in O(log n);
    `heapq.heappop(heap)` removes the smallest in O(log n). heap[0] peeks
    in O(1); it needs a nonempty heap. A heap is not a fully sorted list.
    Copy the input before heapify when mutation is forbidden.

    To keep the k largest values, use a min-heap capped at k: after insertion,
    remove the smallest when size exceeds k. Its root is then the kth largest.
    To simulate a max-heap with the basic portable API, push negative values
    and negate the removed values. A tuple priority is compared
    lexicographically, including tie fields; avoid putting noncomparable custom
    objects into ties without an integer sequence number.
    """, """
    import heapq

    heap = [4, 1, 7]
    heapq.heapify(heap)
    heapq.heappush(heap, 2)
    print(heap[0], heapq.heappop(heap))
    """, "Use a heap when the best current item changes after each operation; sorting once is often simpler when all results are needed.",
    "Explain what the heap root means and why a size-k heap can discard its minimum.")
ex("kth-largest", "Kth largest element", "nums, k", "Return the kth largest entry, counting duplicates separately. nums has 1 to 1000 integers and 1 <= k <= len(nums). Keep a heap of at most k entries and do not mutate nums.",
   "import heapq\n\ndef solve(nums, k):\n    heap = []\n    for value in nums:\n        heapq.heappush(heap, value)\n        if len(heap) > k:\n            heapq.heappop(heap)\n    return heap[0]", [("typical", "[3, 2, 1, 5, 6, 4], 2", 5), ("duplicates", "[2, 2, 1], 2", 2), ("negative", "[-3, -1, -2], 3", -3), ("one", "[8], 1", 8)],
   "Push each value and remove the minimum whenever the heap grows beyond k.", "The heap contains the k largest entries processed so far; its minimum is kth largest.", "O(n log(k+1)) time; O(k) space.")
ex("last-stone", "Last stone weight", "stones", "Repeatedly take the two heaviest positive integer stones. Equal weights disappear; otherwise insert their positive difference. Return the final weight or 0 if none. stones has 0 to 100 values, each at most 1000. Do not mutate input.",
   "import heapq\n\ndef solve(stones):\n    heap = []\n    for value in stones:\n        heap.append(-value)\n    heapq.heapify(heap)\n    while len(heap) > 1:\n        first = -heapq.heappop(heap)\n        second = -heapq.heappop(heap)\n        if first != second:\n            heapq.heappush(heap, -(first - second))\n    if len(heap) == 0:\n        return 0\n    return -heap[0]", [("typical", "[2, 7, 4, 1, 8, 1]", 1), ("equal", "[4, 4]", 0), ("one", "[9]", 9), ("empty", "[]", 0)],
   "Negative weights make the smallest stored value represent the heaviest stone.", "Each iteration reduces the number of stones, and the heap exposes the two greatest weights.", "O(n log n) time; O(n) space.")

lesson("Greedy choices and intervals", "5. Build interview solutions", "Justify a local decision and define endpoint rules.", """
    No new syntax. Greedy algorithms commit to a local choice; they require
    a proof that some optimal solution can include that choice. For a single
    stock transaction, keep the lowest earlier price and the best profit.
    This is a scan invariant, not a rule to buy every local dip.

    An interval is [start, end]. For merging closed intervals, [1,3] and [3,5]
    overlap because their endpoints touch. Sort by start using a named key
    function, then compare each interval with the last output interval. If it
    overlaps, extend the last end with max; otherwise append a new interval.
    Copy pairs into output so updating their endpoints does not mutate input.
    For scheduling nonoverlapping half-open meetings, earliest finish is a
    different greedy rule with different endpoint behavior. Always read the
    problem's overlap definition before reusing a template.
    """, """
    def start_key(interval):
        return interval[0]

    intervals = [[5, 8], [1, 3], [3, 6]]
    ordered = sorted(intervals, key=start_key)
    out = []
    for start, end in ordered:
        if len(out) == 0 or start > out[-1][1]:
            out.append([start, end])
        else:
            out[-1][1] = max(out[-1][1], end)
    print(out)
    """, "Try to construct a counterexample to the greedy choice. If you cannot explain why it is safe, return to state or exhaustive search.",
    "Explain a greedy invariant, interval endpoints and nested-list aliasing.")
ex("stock", "Best one-transaction stock profit", "prices", "Return the largest profit from buying once and selling on a later day. You may skip trading and return 0. prices has 0 to 1000 nonnegative integer prices.",
   "def solve(prices):\n    if len(prices) == 0:\n        return 0\n    lowest = prices[0]\n    best = 0\n    for price in prices:\n        best = max(best, price - lowest)\n        lowest = min(lowest, price)\n    return best", [("rise after dip", "[7, 1, 5, 3, 6, 4]", 5), ("falling", "[7, 5, 2]", 0), ("one", "[4]", 0), ("empty", "[]", 0)],
   "Track the minimum earlier price and compare its profit with each possible sale.", "The best purchase for any sale is the lowest price before it; skipped trades keep profit nonnegative.", "O(n) time; O(1) space.")
ex("merge", "Merge closed intervals", "intervals", "Return merged intervals sorted by start. Each closed interval [start,end] has integer start <= end. Touching endpoints overlap. There are 0 to 1000 intervals. Do not mutate the original pairs.",
   "def start_key(interval):\n    return interval[0]\n\ndef solve(intervals):\n    out = []\n    for start, end in sorted(intervals, key=start_key):\n        if len(out) == 0 or start > out[-1][1]:\n            out.append([start, end])\n        else:\n            out[-1][1] = max(out[-1][1], end)\n    return out", [("touch and overlap", "[[1, 3], [2, 6], [8, 10], [10, 12]]", [[1, 6], [8, 12]]), ("nested", "[[1, 9], [2, 3]]", [[1, 9]]), ("unsorted", "[[5, 5], [1, 2]]", [[1, 2], [5, 5]]), ("empty", "[]", [])],
   "Sort by start; merge into the last output pair when start <= its end.", "Earlier sorted intervals cannot overlap a later interval without also overlapping the last merged interval.", "O(n log n) time; O(n) space including sort and output.")

lesson("One-dimensional dynamic programming", "5. Build interview solutions", "Define a reusable state before writing a recurrence.", """
    No new syntax. Dynamic programming (DP) stores answers to overlapping
    subproblems. Write the state meaning, base values, transition and evaluation
    order in words first. For stairs, dp[i] counts ways to reach step i with
    moves of 1 or 2: dp[i] = dp[i-1] + dp[i-2]. dp[0]=1 counts doing nothing.
    Two rolling values replace the full table when only the last two states
    are needed. Tuple assignment updates them simultaneously from old values.

    For nonadjacent rewards, a prefix optimum either skips the current value
    or takes it plus the optimum two positions earlier. These are choices,
    so use max; counting choices would instead use addition. Greedy selection
    of the largest current reward can fail. Draw a tiny exhaustive decision
    tree and compare it with the recurrence to verify what is being stored.
    Memoization is top-down DP: storing a recursive result avoids recomputing
    it. You can implement the cache with the already taught dictionary syntax.
    """, """
    def ways(n):
        dp = [0] * (n + 2)
        dp[0] = 1
        dp[1] = 1
        for i in range(2, n + 1):
            dp[i] = dp[i - 1] + dp[i - 2]
        return dp[n]

    print(ways(4))  # 5
    """, "Distinguish counting, minimizing and maximizing states. An unexplained recurrence is harder to debug than a clear state definition.",
    "Derive a transition, supply base cases and explain why the iteration order makes dependencies available.")
ex("stairs", "Climbing stairs", "n", "Return the number of ordered sequences of 1-step and 2-step moves reaching step n. n is from 0 to 30. For n=0 there is one empty sequence.",
   "def solve(n):\n    dp = [0] * (n + 2)\n    dp[0] = 1\n    dp[1] = 1\n    for i in range(2, n + 1):\n        dp[i] = dp[i - 1] + dp[i - 2]\n    return dp[n]", [("zero", "0", 1), ("one", "1", 1), ("two", "2", 2), ("five", "5", 8)],
   "Classify a route by its last move; the earlier route ends at n-1 or n-2.", "The two last-move classes are disjoint, so their counts add.", "O(n) time and space; a rolling version uses O(1) space.")
ex("robber", "Maximum nonadjacent sum", "nums", "Return the greatest sum obtainable by selecting no adjacent entries. You may select none. nums has 0 to 1000 nonnegative integers.",
   "def solve(nums):\n    two_back = 0\n    one_back = 0\n    for value in nums:\n        current = max(one_back, two_back + value)\n        two_back = one_back\n        one_back = current\n    return one_back", [("typical", "[2, 7, 9, 3, 1]", 12), ("greedy trap", "[2, 1, 1, 2]", 4), ("one", "[8]", 8), ("empty", "[]", 0)],
   "For each prefix, compare skipping the new value with taking it after the prefix two positions earlier.", "The rolling variables preserve exactly the two dependent prefix optima.", "O(n) time; O(1) space.")

lesson("DP tables and unbounded choices", "5. Build interview solutions", "Translate dependencies into a table and handle impossible states.", """
    No new syntax. A two-dimensional table dp[r][c] can describe states
    depending on two indexes. For grid paths moving only right and down,
    ways[r][c] = ways[r-1][c] + ways[r][c-1]; seed the start cell and treat
    absent predecessors as zero. Build independent rows using the previously
    taught list comprehension, never repeated row references.

    Coin change uses dp[amount] = fewest coins for that amount. dp[0]=0.
    Use amount+1 as an impossible sentinel for positive integer denominations:
    any feasible minimum uses at most amount coins. For each target subtotal,
    try every coin not exceeding it; a smaller subtotal has already been
    solved. Unlimited reuse comes from reading earlier subtotal states, not
    consuming each coin once. Return -1 when the final sentinel remains.
    A greedy largest-coin-first rule fails for [1,3,4] and amount 6.
    """, """
    rows, cols = 2, 3
    dp = [[0] * cols for _ in range(rows)]
    dp[0][0] = 1
    for r in range(rows):
        for c in range(cols):
            if r > 0:
                dp[r][c] += dp[r - 1][c]
            if c > 0:
                dp[r][c] += dp[r][c - 1]
    print(dp[-1][-1])  # 3
    """, "For each table cell, identify its dependencies and prove they were evaluated earlier. Explain the impossible-state sentinel.",
    "Build nonaliased rows and distinguish unlimited coin reuse from choosing each item once.")
ex("grid-paths", "Unique right-down grid paths", "rows, cols", "Return the number of paths from top-left to bottom-right using only right and down. rows and cols are integers from 1 to 15. A 1 by 1 grid has one empty-move path.",
   "def solve(rows, cols):\n    dp = [[0] * cols for _ in range(rows)]\n    dp[0][0] = 1\n    for r in range(rows):\n        for c in range(cols):\n            if r > 0:\n                dp[r][c] += dp[r - 1][c]\n            if c > 0:\n                dp[r][c] += dp[r][c - 1]\n    return dp[-1][-1]", [("rectangle", "3, 7", 28), ("single", "1, 1", 1), ("one row", "1, 5", 1), ("one col", "4, 1", 1)],
   "Add paths from above and left; seed only the starting cell.", "Each path has a unique final direction, so predecessor counts add without overlap.", "O(rows * cols) time and space.")
ex("coin-change", "Fewest coins", "coins, amount", "Return the fewest coins summing to amount, or -1 if impossible. coins has 1 to 20 distinct positive integer denominations; each may be used unlimited times. amount is from 0 to 1000.",
   "def solve(coins, amount):\n    dp = [amount + 1] * (amount + 1)\n    dp[0] = 0\n    for total in range(1, amount + 1):\n        for coin in coins:\n            if coin <= total:\n                dp[total] = min(dp[total], dp[total - coin] + 1)\n    if dp[amount] == amount + 1:\n        return -1\n    return dp[amount]", [("typical", "[1, 2, 5], 11", 3), ("impossible", "[2], 3", -1), ("zero", "[2], 0", 0), ("greedy trap", "[1, 3, 4], 6", 2)],
   "Solve smaller amounts first, taking the minimum over all possible final coins.", "Every feasible solution has a final coin; considering all denominations covers it. The sentinel never wins over a feasible count.", "O(amount * len(coins)) time; O(amount) space.")

lesson("Bits and integer behavior", "5. Build interview solutions", "Use binary operations only after learning their meaning.", """
    Binary represents integers with powers of two. `a & b` keeps bits set in
    both; `a | b` keeps bits set in either; `a ^ b` is XOR (set when different).
    `a << k` shifts left k places; `a >> k` shifts right. Parenthesize bit tests:
    `(n & 1) == 1` tests the least significant bit. These are integer operations;
    `and` and `or` are boolean control operations with different semantics.
    `~n` is bitwise complement and equals -n-1 in Python. Use nonnegative
    inputs for shift loops: repeatedly right-shifting a negative integer need
    not reach zero. Python integers do not overflow at a fixed 32-bit boundary.

    XOR satisfies x ^ x = 0 and x ^ 0 = x and can be regrouped. If every value
    occurs twice except one, XOR cancels pairs. For bit count, repeatedly add
    n & 1 and shift. Cost depends on bit length; Python arbitrary-size integer
    operations are not constant time for unbounded integers. Our arithmetic
    examples use bounded inputs; name that assumption in interviews.
    """, """
    print(6 & 3, 6 | 3, 6 ^ 3, 1 << 3, 8 >> 1, ~0)
    n = 13
    count = 0
    while n > 0:
        count += n & 1
        n = n >> 1
    print(count)  # 3
    """, "Use bit tricks only when the input contract supplies the necessary pairing or nonnegative assumptions.",
    "Explain XOR cancellation, boolean versus bitwise operators, and bounded-integer assumptions.")
ex("single", "Single number", "nums", "Return the one value occurring once; every other value occurs exactly twice. nums has 1 to 1001 integers, each between 0 and 1000000. Use XOR and constant auxiliary space.",
   "def solve(nums):\n    answer = 0\n    for value in nums:\n        answer = answer ^ value\n    return answer", [("pair", "[2, 2, 1]", 1), ("mixed", "[4, 1, 2, 1, 2]", 4), ("zero", "[0]", 0), ("one", "[9]", 9)],
   "XOR every entry into a running value starting at zero.", "Paired occurrences cancel, leaving only the unpaired value.", "O(n) time and O(1) auxiliary space for bounded integers.")
ex("bit-count", "Count set bits", "n", "Return the number of 1 bits in nonnegative integer n, with 0 <= n < 2**31. Use bitwise operations and a loop.",
   "def solve(n):\n    count = 0\n    while n > 0:\n        count += n & 1\n        n = n >> 1\n    return count", [("zero", "0", 0), ("mixed", "13", 3), ("power of two", "1024", 1), ("all ones", "31", 5)],
   "Read the lowest bit, then shift right by one.", "Each iteration consumes one binary digit. Zero has no set bits.", "O(b) time for b bits; O(1) auxiliary space under the 31-bit bound.")

lesson("Interview rehearsal and platform syntax", "6. Interview rehearsal", "Solve independently and translate your function to an interview platform.", """
    The final two exercises introduce no new algorithm syntax: solve them
    without opening hints or answers. Use 30 to 40 minutes per problem.
    Clarify constraints, write a brute-force idea, choose a pattern, state its
    invariant, code, and trace edge cases before running. Afterwards explain
    complexity and reimplement the missed problem from blank the next day.

    Interview platforms may provide `class Solution:` with a method such as
    `def twoSum(self, nums: list[int], target: int) -> list[int]:`.
    self is the instance parameter taught with nodes. `: int` and `: list[int]`
    are type annotations for readers and tools; `-> list[int]` annotates the
    return. They do not convert or validate values at runtime. Built-in
    generic annotations such as list[int] need Python 3.9 or newer.
    `from typing import Optional, List` supports older platform templates:
    `Optional[ListNode]` means a node or None, and `List[int]` is a list of ints.
    You may keep a provided platform annotation; the course exercises do not
    require you to write annotations. Do not paste the course's print driver
    into the platform. Move only your function body into the supplied method.

    After this foundation, continue with topological sorting, union-find,
    tries, weighted shortest paths and more DP variants in the DSA Curriculum.
    They require new algorithm lessons, not unexplained Python shortcuts.
    Optional future conveniences include Counter, defaultdict, bisect, cache,
    lambdas, generators and itertools. None is required anywhere in this course.
    Read a syntax lesson before adopting one from an external editorial.
    """, """
    from typing import List, Optional

    class Solution:
        def total(self, nums: list[int]) -> int:
            return sum(nums)

    def identity(value: Optional[int]) -> Optional[int]:
        return value

    values: List[int] = [1, 2, 3]
    print(Solution().total(values), identity(None))
    """, "Ready to continue when you can solve both rehearsal tasks from blank, explain their invariants and costs, and reproduce them after a delay. Passing samples alone is insufficient.",
    "Solve a mixed interview task without hints, translate its signature, and explain an edge-case trace and complexity.")
ex("product", "Rehearsal: product except self", "nums", "Return a list where out[i] is the product of every input except nums[i]. nums has 2 to 100 bounded integers; zero and negatives are allowed. Use O(n) time, no division, and O(1) working space beyond the output. Products fit within signed 32-bit integers. Start by explaining a brute-force solution.",
   "def solve(nums):\n    out = [1] * len(nums)\n    prefix = 1\n    for i in range(len(nums)):\n        out[i] = prefix\n        prefix = prefix * nums[i]\n    suffix = 1\n    for i in range(len(nums) - 1, -1, -1):\n        out[i] = out[i] * suffix\n        suffix = suffix * nums[i]\n    return out", [("positive", "[1, 2, 3, 4]", [24, 12, 8, 6]), ("one zero", "[-1, 1, 0, -3, 3]", [0, 0, 9, 0, 0]), ("two zeroes", "[0, 0, 2]", [0, 0, 0]), ("pair", "[2, 3]", [3, 2])],
   "Store products strictly before each index, then multiply by products strictly after it.", "The two passes exclude the current value by updating the running product after storing it. No division means zero needs no special branch.", "O(n) time; O(1) auxiliary space beyond O(n) output.")
ex("jump", "Rehearsal: Jump Game", "nums", "Return whether the last index is reachable from index 0. Each entry is the maximum forward jump from that index (any distance from 1 through that value is allowed). nums has 1 to 1000 nonnegative integers. A one-element input is already reached. Explain why your greedy choice is safe.",
   "def solve(nums):\n    farthest = 0\n    for i, value in enumerate(nums):\n        if i > farthest:\n            return False\n        farthest = max(farthest, i + value)\n    return True", [("reachable", "[2, 3, 1, 1, 4]", True), ("blocked", "[3, 2, 1, 0, 4]", False), ("one", "[0]", True), ("stuck", "[0, 1]", False), ("skip zero", "[2, 0, 0]", True)],
   "Keep the farthest reachable index from all reachable entries processed so far.", "Every position up to farthest is reachable because shorter jumps are allowed. An index beyond farthest cannot be rescued by any later, unreachable index.", "O(n) time; O(1) space.")


def syntax_features(code):
    """Conservative AST vocabulary: syntax shapes, operators, methods, built-ins.

    Identifiers and constants are intentionally not a vocabulary. User-defined
    function names are not new syntax. Method/field names and stdlib calls are.
    """
    features = set()
    for node in ast.walk(ast.parse(code)):
        if isinstance(node, (ast.expr_context, ast.arguments, ast.arg, ast.Module)):
            continue
        features.add(type(node).__name__)
        if isinstance(node, ast.Attribute):
            features.add("." + node.attr)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and hasattr(builtins, node.func.id):
            features.add(node.func.id + "()")
        if isinstance(node, ast.Import):
            features.update("import " + alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            features.update("from " + node.module + " import " + alias.name for alias in node.names)
        if isinstance(node, ast.keyword):
            features.add("keyword " + str(node.arg))
    return features


def authored_course():
    providers = {}
    for module in MODULES:
        for feature in syntax_features(module["example"]):
            providers.setdefault(feature, module["id"])
        module["syntax"] = sorted(feature for feature, provider in providers.items() if provider == module["id"])
        for exercise in module["exercises"]:
            needed = syntax_features(exercise["solution"]) | syntax_features(exercise["starter"])
            unknown = needed - providers.keys()
            if unknown:
                raise ValueError(f"{exercise['id']} needs untaught syntax: {sorted(unknown)}")
            exercise["requires"] = sorted(set(providers[feature] for feature in needed))
    return MODULES


def main():
    modules = authored_course()
    target = ROOT / "src/data/python/course.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Python: zero syntax to interview problems", "",
             "Open **Courses > Python Course** (`/python-course`) in Poodcode. This document is also a standalone roadmap.", "",
             "25 ordered modules, 50 original coding exercises. Advance by mastery, not calendar weeks. Plan roughly 60-90 minutes for an early module and 2-4 hours for a later module, plus independent repetition; timing is only a guide.", "",
             "## Learning contract", "",
             "Assume no Python syntax knowledge. Read and type each module's example before its exercises. Every reference solution and starter is audited against syntax, built-ins, imports and methods demonstrated by the current and preceding examples. Exercises link to their required syntax lessons. Algorithmic discovery remains your work; unfamiliar Python syntax must not be the obstacle.", "",
             "Every exercise publishes its complete contract and all graded cases. No hidden tests, parsing, dependencies or interview-platform wrappers are required. The app supplies a driver that calls your function and displays repr(return_value); the driver is infrastructure, not code you must write. List results are order-sensitive; dictionary insertion order is specified in its exercise. Syntax auditing checks the supplied solutions, not every possible solution you might choose.", "",
             "Use Python 3.9+ (for the final optional annotation example), installed as `python` on PATH. No pip packages are needed. Open the desktop app for real execution; browser mock mode does not execute Python. Drafts stay on this device; accepted progress uses the existing local database.", "",
             "## Study loop", "",
             "1. Type and run the example; explain each line and change one input.",
             "2. Close it and attempt the first exercise, then the transfer exercise.",
             "3. Predict results for empty, single, duplicate, negative and boundary inputs when permitted by the contract.",
             "4. Run all cases, repair failures, and explain the invariant and time/space costs.",
             "5. Use a hint only after a serious attempt; read the worked answer afterward and retype your own solution from blank.",
             "6. Repeat missed exercises the next day and a week later. Advance when you pass the module's exit check without looking up syntax.", "",
             "Passing cases does not enforce the requested algorithm or establish complexity. Verify those against the explanation. Advanced DSA continues in the existing DSA Curriculum after this foundation.", "",
             "## Ordered roadmap", "", "| Module | Outcome | Coding practice |", "| --- | --- | --- |"]
    for module in modules:
        lines.append(f"| {module['number']}. {module['title']} | {module['goal']} | " + "; ".join(e["title"] for e in module["exercises"]) + " |")
    for module in modules:
        lines += ["", f"## {module['number']}. {module['title']}", "", module["stage"], "", module["goal"], "",
                  module["explanation"], "```python", module["example"].rstrip(), "```", "", module["pattern"], "",
                  "**Exit check:** " + module["gate"]]
        for exercise in module["exercises"]:
            lines += ["", "### " + exercise["title"], "", exercise["prompt"], "",
                      "**Syntax lessons:** " + ", ".join(str(int(key[1:])) for key in exercise["requires"]), "",
                      "```python", exercise["starter"].rstrip(), "```", "", "Published cases:", ""]
            for case in exercise["tests"]:
                if case["setup"]:
                    lines += ["Fixture setup:", "", "```python", case["setup"].rstrip(), "```", ""]
                lines.append(f"- {case['name']}: `{case['call']}` -> `{case['expected']}`")
            lines += ["", "<details><summary>Hint</summary>", "", exercise["hint"], "", "</details>", "",
                      "<details><summary>Worked answer (read after attempting)</summary>", "", "```python",
                      exercise["solution"].rstrip(), "```", "", exercise["explanation"], "", exercise["complexity"], "", "</details>"]
    lines += ["", "## Authoring and checks", "", "Rebuild with `python tools/python_course.py`. Verify syntax prerequisites, all example programs, every reference answer, input preservation where required, and that every starter fails at least one case with `python tools/verify_python_course.py`. The AST vocabulary check is conservative and cannot prove teaching quality or algorithm correctness; review explanations as well.", ""]
    (ROOT / "PYTHON_ROADMAP.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Authored {len(modules)} modules and {sum(len(m['exercises']) for m in modules)} exercises")


if __name__ == "__main__":
    main()
