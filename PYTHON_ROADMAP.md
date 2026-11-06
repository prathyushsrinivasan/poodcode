# Python: zero syntax to interview problems

Open **Courses > Python Course** (`/python-course`) in Poodcode. This document is also a standalone roadmap.

25 ordered modules, 50 original coding exercises. Advance by mastery, not calendar weeks. Plan roughly 60-90 minutes for an early module and 2-4 hours for a later module, plus independent repetition; timing is only a guide.

## Learning contract

Assume no Python syntax knowledge. Read and type each module's example before its exercises. Every reference solution and starter is audited against syntax, built-ins, imports and methods demonstrated by the current and preceding examples. Exercises link to their required syntax lessons. Algorithmic discovery remains your work; unfamiliar Python syntax must not be the obstacle.

Every exercise publishes its complete contract and all graded cases. No hidden tests, parsing, dependencies or interview-platform wrappers are required. The app supplies a driver that calls your function and displays repr(return_value); the driver is infrastructure, not code you must write. List results are order-sensitive; dictionary insertion order is specified in its exercise. Syntax auditing checks the supplied solutions, not every possible solution you might choose.

Use Python 3.9+ (for the final optional annotation example), installed as `python` on PATH. No pip packages are needed. Open the desktop app for real execution; browser mock mode does not execute Python. Drafts stay on this device; accepted progress uses the existing local database.

## Study loop

1. Type and run the example; explain each line and change one input.
2. Close it and attempt the first exercise, then the transfer exercise.
3. Predict results for empty, single, duplicate, negative and boundary inputs when permitted by the contract.
4. Run all cases, repair failures, and explain the invariant and time/space costs.
5. Use a hint only after a serious attempt; read the worked answer afterward and retype your own solution from blank.
6. Repeat missed exercises the next day and a week later. Advance when you pass the module's exit check without looking up syntax.

Passing cases does not enforce the requested algorithm or establish complexity. Verify those against the explanation. Advanced DSA continues in the existing DSA Curriculum after this foundation.

## Ordered roadmap

| Module | Outcome | Coding practice |
| --- | --- | --- |
| 1. Your first Python functions | Read a tiny program, change it, and return an integer. | Add two integers; Split minutes |
| 2. Decisions and booleans | Choose behavior with explicit conditions. | Sign of an integer; Nonnegative and even |
| 3. Loops and running state | Repeat work and maintain a running answer. | Sum from one to n; Count decimal digits |
| 4. Lists and indexes | Scan and build arrays safely. | Count positive entries; Maximum without max |
| 5. Strings and slices | Treat text as a sequence and build new text. | Count vowels; Reverse word order |
| 6. Dictionaries and frequency maps | Associate keys with counts or positions. | Build a frequency map; First unique character index |
| 7. Sets, tuples and unpacking | Track membership and carry small records. | Contains a duplicate; Two Sum |
| 8. Sorting, helpers and copying | Use only explained conveniences and reason about their costs. | Sorted squares: first solution; Closest value to zero |
| 9. Two pointers | Move boundaries using a stated invariant. | Exact palindrome; Pair in a sorted array |
| 10. Sliding windows | Update a contiguous range instead of recomputing it. | Maximum sum of k consecutive values; Longest substring without repeats |
| 11. Prefix sums | Summarize everything before an index. | Static range sums; Count subarrays with sum k |
| 12. Binary search and boundaries | Halve a search interval without losing an answer. | Search insert position; Integer square root |
| 13. Stacks and monotonic stacks | Store unfinished work in last-in, first-out order. | Valid brackets; Days until a warmer temperature |
| 14. Imports, queues and BFS | Process work in first-in, first-out order. | Queue operations; Fewest increments |
| 15. Recursion and the call stack | Define a smaller subproblem and a stopping case. | Recursive factorial; Recursive digit sum |
| 16. Nested helpers and backtracking | Explore choices, copy answers, and undo mutations. | All subsets; Binary strings without adjacent ones |
| 17. Classes, objects and linked lists | Follow references rather than array indexes. | Middle node value; Detect a linked-list cycle |
| 18. Binary trees: DFS and BFS | Combine child results and traverse levels. | Maximum tree depth; Inorder traversal |
| 19. Graphs and grids | Represent neighbors and avoid repeated work. | Shortest unweighted directed path; Count islands |
| 20. Heaps and priority queues | Keep the best pending candidate available. | Kth largest element; Last stone weight |
| 21. Greedy choices and intervals | Justify a local decision and define endpoint rules. | Best one-transaction stock profit; Merge closed intervals |
| 22. One-dimensional dynamic programming | Define a reusable state before writing a recurrence. | Climbing stairs; Maximum nonadjacent sum |
| 23. DP tables and unbounded choices | Translate dependencies into a table and handle impossible states. | Unique right-down grid paths; Fewest coins |
| 24. Bits and integer behavior | Use binary operations only after learning their meaning. | Single number; Count set bits |
| 25. Interview rehearsal and platform syntax | Solve independently and translate your function to an interview platform. | Rehearsal: product except self; Rehearsal: Jump Game |

## 1. Your first Python functions

1. Learn Python by coding

Read a tiny program, change it, and return an integer.

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

```python
def solve(a, b):
    total = a + b
    return total

print(solve(2, 3))  # 5
quotient = 7 // 3
remainder = 7 % 3
print(quotient, remainder, 2 ** 3, 8 / 2, -3 * 2 - 1)
```

Trace parameters -> calculation -> return. Never add print statements to
the submitted function: the runner displays the returned value for you.
There are no secret input formats, imports, annotations, or class wrappers.
To run locally, save your function in practice.py, add a print(solve(...))
call below it, and run `python practice.py` in a terminal with Python 3 installed.


**Exit check:** Explain each character in def solve(a, b): and return a result without printing it.

### Add two integers

Return a + b. Both inputs are integers between -10000 and 10000.

**Syntax lessons:** 1

```python
def solve(a, b):
    # Replace this return with your solution.
    return 0
```

Published cases:

- positive: `solve(2, 3)` -> `5`
- negative: `solve(-4, 1)` -> `-3`
- zero: `solve(0, 0)` -> `0`

<details><summary>Hint</summary>

Use the + operator on the two parameters.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(a, b):
    return a + b
```

The function returns the arithmetic sum to its caller.

O(1) time and space for these bounded integers.

</details>

### Split minutes

Return the number of complete hours in minutes (an integer from 0 to 10000). Ignore leftover minutes.

**Syntax lessons:** 1

```python
def solve(minutes):
    # Replace this return with your solution.
    return 0
```

Published cases:

- partial: `solve(59)` -> `0`
- exact: `solve(120)` -> `2`
- leftover: `solve(125)` -> `2`
- zero: `solve(0)` -> `0`

<details><summary>Hint</summary>

An hour has 60 minutes. Integer floor division discards the remainder here.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(minutes):
    return minutes // 60
```

For nonnegative minutes, floor division counts complete groups of 60.

O(1) time and space.

</details>

## 2. Decisions and booleans

1. Learn Python by coding

Choose behavior with explicit conditions.

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

```python
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
```

Test the boundary itself and the values immediately on either side. Draw the branches before coding.


**Exit check:** Distinguish assignment from comparison and trace which branch runs.

### Sign of an integer

Return -1 for negative n, 0 for zero, and 1 for positive n. n is an integer from -10000 to 10000.

**Syntax lessons:** 1, 2

```python
def solve(n):
    # Replace this return with your solution.
    return 0
```

Published cases:

- negative: `solve(-8)` -> `-1`
- zero: `solve(0)` -> `0`
- positive: `solve(7)` -> `1`

<details><summary>Hint</summary>

Handle negative and zero with early returns; the remaining case is positive.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(n):
    if n < 0:
        return -1
    if n == 0:
        return 0
    return 1
```

Each early return eliminates one possibility.

O(1) time and space.

</details>

### Nonnegative and even

Return True exactly when integer n is nonnegative and even; otherwise return False.

**Syntax lessons:** 1, 2

```python
def solve(n):
    # Replace this return with your solution.
    return 0
```

Published cases:

- even: `solve(8)` -> `True`
- odd: `solve(3)` -> `False`
- negative even: `solve(-2)` -> `False`
- zero: `solve(0)` -> `True`

<details><summary>Hint</summary>

An even integer has remainder zero after division by two.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(n):
    return n >= 0 and n % 2 == 0
```

Both predicates must hold. Zero is nonnegative and even.

O(1) time and space.

</details>

## 3. Loops and running state

1. Learn Python by coding

Repeat work and maintain a running answer.

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

```python
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
```

A loop with n iterations and constant work per iteration takes O(n) time. This is how we count growth, not seconds.


**Exit check:** Trace a loop, including zero iterations, and explain why a while loop terminates.

### Sum from one to n

Return 1 + 2 + ... + n using a loop. n is an integer from 0 to 1000; return 0 for n=0.

**Syntax lessons:** 1, 3

```python
def solve(n):
    # Replace this return with your solution.
    return 0
```

Published cases:

- three: `solve(3)` -> `6`
- zero: `solve(0)` -> `0`
- one: `solve(1)` -> `1`
- ten: `solve(10)` -> `55`

<details><summary>Hint</summary>

The exclusive stop must be n + 1.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total
```

After processing i, total contains the sum from 1 through i.

O(n) time; O(1) auxiliary space.

</details>

### Count decimal digits

Return the number of decimal digits of integer n, where 0 <= n <= 1000000000. Zero has one digit. Use integer division and a loop.

**Syntax lessons:** 1, 2, 3

```python
def solve(n):
    # Replace this return with your solution.
    return 0
```

Published cases:

- zero: `solve(0)` -> `1`
- single: `solve(7)` -> `1`
- multiple: `solve(1020)` -> `4`
- power of ten: `solve(100)` -> `3`

<details><summary>Hint</summary>

Each division by ten removes one decimal digit; handle zero before the loop.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(n):
    if n == 0:
        return 1
    count = 0
    while n > 0:
        n = n // 10
        count += 1
    return count
```

Repeated floor division reduces a positive integer to zero.

O(d) time for d digits; O(1) space.

</details>

## 4. Lists and indexes

1. Learn Python by coding

Scan and build arrays safely.

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

```python
def doubled(nums):
    out = []
    for value in nums:
        out.append(value * 2)
    return out

nums = [3, -2]
nums[0] = 5
print(len(nums), nums[-1], doubled(nums))
```

A scan visits each item once: O(n) time. A new list of n answers uses O(n) auxiliary space. append is amortized O(1).


**Exit check:** Choose a value loop or an index loop and handle an empty input deliberately.

### Count positive entries

Return how many entries are strictly greater than zero. nums contains 0 to 1000 integers; zero does not count.

**Syntax lessons:** 1, 2, 3

```python
def solve(nums):
    # Replace this return with your solution.
    return 0
```

Published cases:

- mixed: `solve([-2, 0, 3, 3])` -> `2`
- empty: `solve([])` -> `0`
- none: `solve([-4, 0])` -> `0`

<details><summary>Hint</summary>

Keep a counter and add one only in the positive branch.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums):
    count = 0
    for value in nums:
        if value > 0:
            count += 1
    return count
```

The counter describes exactly the entries already visited.

O(n) time; O(1) auxiliary space.

</details>

### Maximum without max

Return the greatest value in a nonempty list of 1 to 1000 integers. Use comparisons and a loop rather than a built-in maximum.

**Syntax lessons:** 1, 2, 3, 4

```python
def solve(nums):
    # Replace this return with your solution.
    return 0
```

Published cases:

- mixed: `solve([3, 9, 2])` -> `9`
- all negative: `solve([-8, -2, -4])` -> `-2`
- one: `solve([-5])` -> `-5`

<details><summary>Hint</summary>

Use nums[0] as the initial best so negative-only inputs work.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums):
    best = nums[0]
    for value in nums:
        if value > best:
            best = value
    return best
```

best is the maximum of the processed prefix.

O(n) time; O(1) auxiliary space.

</details>

## 5. Strings and slices

1. Learn Python by coding

Treat text as a sequence and build new text.

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

```python
text = 'Cat dog'
print(text[0], text[1:3], text[::-1], text.lower())
words = text.split()
chars = []
for ch in text:
    if ch not in 'aeiouAEIOU':
        chars.append(ch)
print(''.join(chars), ' '.join(words), 'a' in 'cat', 'c' + 'at')
```

Scan characters when counting; use slices only when the copied data is needed. A length-k slice costs O(k) time and space.


**Exit check:** Explain the difference between an index and a slice, and why strings cannot be updated in place.

### Count vowels

Return the number of lowercase vowels a, e, i, o, u in text. text contains 0 to 1000 lowercase ASCII letters.

**Syntax lessons:** 1, 2, 3, 5

```python
def solve(text):
    # Replace this return with your solution.
    return 0
```

Published cases:

- word: `solve('leetcode')` -> `4`
- empty: `solve('')` -> `0`
- none: `solve('rhythm')` -> `0`
- all: `solve('aeiou')` -> `5`

<details><summary>Hint</summary>

Use a character loop and membership in the fixed vowel string.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(text):
    count = 0
    for ch in text:
        if ch in 'aeiou':
            count += 1
    return count
```

The membership string has a fixed length of five, so each check is constant work.

O(n) time; O(1) space.

</details>

### Reverse word order

Return the whitespace-separated words in reverse order, joined with single spaces. Leading, trailing and repeated spaces are allowed; text has at most 1000 ASCII characters. Empty input returns ''.

**Syntax lessons:** 1, 4, 5

```python
def solve(text):
    # Replace this return with your solution.
    return 0
```

Published cases:

- normal: `solve('code every day')` -> `'day every code'`
- spacing: `solve('  a   b  ')` -> `'b a'`
- empty: `solve('')` -> `''`
- one: `solve('hi')` -> `'hi'`

<details><summary>Hint</summary>

split removes whitespace runs; reverse the resulting list with a slice, then join.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(text):
    words = text.split()
    return ' '.join(words[::-1])
```

A slice reverses a copy of the word list; join controls the output spacing.

O(n) time and space for n characters.

</details>

## 6. Dictionaries and frequency maps

1. Learn Python by coding

Associate keys with counts or positions.

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

```python
counts = {}
for ch in 'aba':
    counts[ch] = counts.get(ch, 0) + 1
for key in counts:
    print(key, counts[key])
print('a' in counts, counts.get('z', 0), counts.items())
```

Replace repeated full scans with one table-building pass. Separate 'build counts' from 'read counts' when order matters.


**Exit check:** Read and update a missing key safely, and explain why a list is not a dictionary key.

### Build a frequency map

Return a dictionary mapping each integer to its occurrence count. nums has 0 to 1000 integers. Insert keys in the order first seen; the course displays dictionaries in insertion order.

**Syntax lessons:** 1, 3, 4, 6

```python
def solve(nums):
    # Replace this return with your solution.
    return 0
```

Published cases:

- repeats: `solve([2, 1, 2])` -> `{2: 2, 1: 1}`
- empty: `solve([])` -> `{}`
- negative: `solve([-1, -1, 0])` -> `{-1: 2, 0: 1}`

<details><summary>Hint</summary>

Start with an empty dictionary and update once per number.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums):
    counts = {}
    for value in nums:
        counts[value] = counts.get(value, 0) + 1
    return counts
```

get supplies the initial count; assignment stores the incremented count.

Expected O(n) time; O(k) space for k distinct values.

</details>

### First unique character index

Return the index of the first character occurring exactly once, or -1 if none. text has 0 to 1000 lowercase ASCII letters.

**Syntax lessons:** 1, 2, 3, 4, 6

```python
def solve(text):
    # Replace this return with your solution.
    return 0
```

Published cases:

- early: `solve('leetcode')` -> `0`
- later: `solve('aabbc')` -> `4`
- none: `solve('aabb')` -> `-1`
- empty: `solve('')` -> `-1`

<details><summary>Hint</summary>

Count first; scan indexes in original order second.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(text):
    counts = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    for i in range(len(text)):
        if counts[text[i]] == 1:
            return i
    return -1
```

The second pass guarantees the first qualifying index rather than an arbitrary unique character.

O(n) time; O(1) space for a fixed alphabet.

</details>

## 7. Sets, tuples and unpacking

1. Learn Python by coding

Track membership and carry small records.

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

```python
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
```

For Two Sum, look for the complement before inserting the current index. This prevents using one element twice.


**Exit check:** Choose a set for membership and a dictionary when the associated index is needed.

### Contains a duplicate

Return True if any integer occurs at least twice, otherwise False. nums has 0 to 1000 integers.

**Syntax lessons:** 1, 2, 3, 4, 5, 7

```python
def solve(nums):
    # Replace this return with your solution.
    return 0
```

Published cases:

- duplicate: `solve([1, 2, 1])` -> `True`
- distinct: `solve([1, 2])` -> `False`
- empty: `solve([])` -> `False`
- zero pair: `solve([0, 0])` -> `True`

<details><summary>Hint</summary>

Check whether a value is already in the set before adding it.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums):
    seen = set()
    for value in nums:
        if value in seen:
            return True
        seen.add(value)
    return False
```

The set contains precisely the earlier values.

Expected O(n) time; O(n) space.

</details>

### Two Sum

Return [i, j], i < j, for the two entries summing to target, or [] if absent. nums has 0 to 1000 integers. At most one index pair qualifies. Never reuse an index.

**Syntax lessons:** 1, 2, 3, 4, 5, 6, 7

```python
def solve(nums, target):
    # Replace this return with your solution.
    return 0
```

Published cases:

- pair: `solve([2, 7, 11, 15], 9)` -> `[0, 1]`
- equal values: `solve([3, 3], 6)` -> `[0, 1]`
- single cannot reuse: `solve([3], 6)` -> `[]`
- empty: `solve([], 5)` -> `[]`

<details><summary>Hint</summary>

Map previously seen values to indexes; look up target - value first.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums, target):
    seen = {}
    for i, value in enumerate(nums):
        need = target - value
        if need in seen:
            return [seen[need], i]
        seen[value] = i
    return []
```

A hit is always an earlier, distinct index. The single-pair contract removes tie ambiguity.

Expected O(n) time; O(n) space.

</details>

## 8. Sorting, helpers and copying

2. Solve array and string patterns

Use only explained conveniences and reason about their costs.

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

```python
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
```

Sorting can simplify comparisons, but ask whether it destroys original indexes or order. State the cost of every helper.


**Exit check:** Explain mutation versus copying, sort versus sorted, and why repeated rows can alias.

### Sorted squares: first solution

Return the squares of all integers in ascending order. nums has 0 to 1000 integers. Do not mutate the input. This first version may sort.

**Syntax lessons:** 1, 3, 4, 8

```python
def solve(nums):
    # Replace this return with your solution.
    return 0
```

Published cases:

- mixed: `solve([-4, -1, 0, 3])` -> `[0, 1, 9, 16]`
- empty: `solve([])` -> `[]`
- negative: `solve([-3, -2])` -> `[4, 9]`

<details><summary>Hint</summary>

Square each value, then sort the new list.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums):
    out = []
    for value in nums:
        out.append(value * value)
    return sorted(out)
```

Squaring does not preserve signed order, so sorting is necessary for this approach.

O(n log n) time; O(n) space including output and sorting.

</details>

### Closest value to zero

Return the integer closest to zero in a nonempty list of at most 1000 integers. If both -x and x are equally close, prefer x.

**Syntax lessons:** 1, 2, 3, 4, 8

```python
def solve(nums):
    # Replace this return with your solution.
    return 0
```

Published cases:

- tie: `solve([-2, 2, 5])` -> `2`
- negative: `solve([-7, -1])` -> `-1`
- zero: `solve([3, 0, -1])` -> `0`
- one: `solve([6])` -> `6`

<details><summary>Hint</summary>

Compare absolute values first, then apply the positive tie rule.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums):
    best = nums[0]
    for value in nums:
        if abs(value) < abs(best) or (abs(value) == abs(best) and value > best):
            best = value
    return best
```

The tie rule is explicit; input order cannot change the answer.

O(n) time; O(1) space.

</details>

## 9. Two pointers

2. Solve array and string patterns

Move boundaries using a stated invariant.

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

```python
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
```

Before moving a pointer, say which candidates are eliminated and why. A sorted-input contract is essential for the pair-sum rule.


**Exit check:** Justify pointer movement rather than memorizing it.

### Exact palindrome

Return whether text reads identically forward and backward. text has 0 to 1000 lowercase ASCII letters. Use two pointers without a reversed copy.

**Syntax lessons:** 1, 2, 3, 4

```python
def solve(text):
    # Replace this return with your solution.
    return 0
```

Published cases:

- even: `solve('abba')` -> `True`
- mismatch: `solve('abca')` -> `False`
- empty: `solve('')` -> `True`
- single: `solve('a')` -> `True`

<details><summary>Hint</summary>

Compare the endpoints; move both inward after a match.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(text):
    left = 0
    right = len(text) - 1
    while left < right:
        if text[left] != text[right]:
            return False
        left += 1
        right -= 1
    return True
```

Every pair outside the active range has already matched.

O(n) time; O(1) space.

</details>

### Pair in a sorted array

Return [i, j] with i < j for two entries summing to target, or []. nums is sorted ascending, has at most 1000 integers, and at most one index pair qualifies. Use constant auxiliary space.

**Syntax lessons:** 1, 2, 3, 4

```python
def solve(nums, target):
    # Replace this return with your solution.
    return 0
```

Published cases:

- pair: `solve([1, 3, 4, 8], 7)` -> `[1, 2]`
- equal: `solve([2, 2], 4)` -> `[0, 1]`
- absent: `solve([1, 3], 8)` -> `[]`
- empty: `solve([], 3)` -> `[]`

<details><summary>Hint</summary>

Compare the endpoint sum to target; eliminate one endpoint each time.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums, target):
    left = 0
    right = len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return [left, right]
        if total < target:
            left += 1
        else:
            right -= 1
    return []
```

Sorted order makes each elimination safe.

O(n) time; O(1) auxiliary space.

</details>

## 10. Sliding windows

2. Solve array and string patterns

Update a contiguous range instead of recomputing it.

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

```python
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
```

Write what makes the current window valid, when you shrink it, and when you record its length or sum.


**Exit check:** Explain why a left boundary never retreats, and why input signs can matter.

### Maximum sum of k consecutive values

Return the maximum sum of a contiguous length-k window. nums has 1 to 1000 integers; 1 <= k <= len(nums). Negative values are allowed.

**Syntax lessons:** 1, 3, 4, 5, 8

```python
def solve(nums, k):
    # Replace this return with your solution.
    return 0
```

Published cases:

- mixed: `solve([1, 4, -2, 5], 2)` -> `5`
- negative: `solve([-5, -2, -3], 2)` -> `-5`
- whole: `solve([1, 2], 2)` -> `3`
- one: `solve([-4], 1)` -> `-4`

<details><summary>Hint</summary>

Start with the first k entries, then replace one outgoing value each step.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums, k):
    current = sum(nums[:k])
    best = current
    for right in range(k, len(nums)):
        current += nums[right] - nums[right - k]
        best = max(best, current)
    return best
```

The running sum always describes exactly k consecutive values.

O(n) time; O(k) temporary space for the initial slice (can be reduced to O(1) with a loop).

</details>

### Longest substring without repeats

Return the length of the longest contiguous substring with no repeated character. text has at most 1000 lowercase ASCII letters; empty returns 0.

**Syntax lessons:** 1, 2, 3, 4, 5, 6, 7, 8

```python
def solve(text):
    # Replace this return with your solution.
    return 0
```

Published cases:

- typical: `solve('abcabcbb')` -> `3`
- do not retreat: `solve('abba')` -> `2`
- empty: `solve('')` -> `0`
- all same: `solve('aaaa')` -> `1`

<details><summary>Hint</summary>

Keep last-seen indexes and move left past a repeated character only when needed.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(text):
    last = {}
    left = 0
    best = 0
    for right, ch in enumerate(text):
        if ch in last:
            left = max(left, last[ch] + 1)
        last[ch] = right
        best = max(best, right - left + 1)
    return best
```

The active range contains no duplicate characters; max prevents an old occurrence from moving left backward.

O(n) time; O(1) space for the fixed alphabet.

</details>

## 11. Prefix sums

2. Solve array and string patterns

Summarize everything before an index.

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

```python
nums = [2, -1, 4]
prefix = [0]
for value in nums:
    prefix.append(prefix[-1] + value)
left, right = 1, 2
print(prefix[right + 1] - prefix[left])  # 3
```

Choose prefixes for repeated static range queries or count-of-earlier-total problems. Name exactly what the dictionary counts.


**Exit check:** Explain both the leading zero and why a frequency map starts at {0: 1}.

### Static range sums

Return one sum per inclusive query [left, right], in order. nums has 1 to 1000 integers; queries has 0 to 1000 valid ranges with 0 <= left <= right < len(nums).

**Syntax lessons:** 1, 3, 4, 7

```python
def solve(nums, queries):
    # Replace this return with your solution.
    return 0
```

Published cases:

- ranges: `solve([2, -1, 4], [[0, 2], [1, 1], [1, 2]])` -> `[5, -1, 3]`
- no queries: `solve([8], [])` -> `[]`
- single: `solve([-3], [[0, 0]])` -> `[-3]`

<details><summary>Hint</summary>

Build n+1 prefixes, then subtract the prefix before the query from the one after it.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums, queries):
    prefix = [0]
    for value in nums:
        prefix.append(prefix[-1] + value)
    out = []
    for left, right in queries:
        out.append(prefix[right + 1] - prefix[left])
    return out
```

Each query cancels values outside its range.

O(n+q) time; O(n) working space plus O(q) output.

</details>

### Count subarrays with sum k

Return the count of nonempty contiguous subarrays summing to integer k. nums has 0 to 1000 integers, including negatives.

**Syntax lessons:** 1, 3, 4, 6

```python
def solve(nums, k):
    # Replace this return with your solution.
    return 0
```

Published cases:

- positive: `solve([1, 1, 1], 2)` -> `2`
- zeroes: `solve([0, 0], 0)` -> `3`
- negative: `solve([1, -1, 0], 0)` -> `3`
- empty: `solve([], 0)` -> `0`

<details><summary>Hint</summary>

Count how many previous prefix totals equal current total minus k.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums, k):
    counts = {0: 1}
    total = 0
    answer = 0
    for value in nums:
        total += value
        answer += counts.get(total - k, 0)
        counts[total] = counts.get(total, 0) + 1
    return answer
```

Multiple identical prefixes correspond to different starting positions, so store frequencies rather than a set.

Expected O(n) time; O(n) space.

</details>

## 12. Binary search and boundaries

2. Solve array and string patterns

Halve a search interval without losing an answer.

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

```python
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
```

Write the interval convention and the meaning of the answer before coding. Test absent-before, absent-after, duplicates and empty input.


**Exit check:** Derive an update from the interval invariant and prove the interval shrinks.

### Search insert position

Return the first index with value >= target, or len(nums) if none. nums is sorted ascending and has 0 to 1000 integers. Duplicates are allowed.

**Syntax lessons:** 1, 2, 3, 4

```python
def solve(nums, target):
    # Replace this return with your solution.
    return 0
```

Published cases:

- duplicates: `solve([1, 3, 3, 8], 3)` -> `1`
- gap: `solve([1, 3], 2)` -> `1`
- after: `solve([1, 3], 9)` -> `2`
- before: `solve([1, 3], 0)` -> `0`
- empty: `solve([], 2)` -> `0`

<details><summary>Hint</summary>

Use [left, right) and move right to mid when the midpoint could be the first answer.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums, target):
    left = 0
    right = len(nums)
    while left < right:
        mid = (left + right) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left
```

Equality stays in the search range, so the leftmost equal value survives.

O(log n) time; O(1) space.

</details>

### Integer square root

Return the largest integer x such that x*x <= n. n is an integer from 0 to 1000000000. Use binary search rather than a square-root helper.

**Syntax lessons:** 1, 2, 3

```python
def solve(n):
    # Replace this return with your solution.
    return 0
```

Published cases:

- zero: `solve(0)` -> `0`
- one: `solve(1)` -> `1`
- square: `solve(16)` -> `4`
- between: `solve(8)` -> `2`
- large: `solve(1000000000)` -> `31622`

<details><summary>Hint</summary>

Find the first integer whose square is too large, then subtract one.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(n):
    left = 0
    right = n + 1
    while left < right:
        mid = (left + right) // 2
        if mid * mid <= n:
            left = mid + 1
        else:
            right = mid
    return left - 1
```

The predicate x*x > n is monotone. The first failing value is one beyond the floor root.

O(log(n+1)) time; O(1) space.

</details>

## 13. Stacks and monotonic stacks

3. Learn data structures

Store unfinished work in last-in, first-out order.

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

```python
stack = []
stack.append(4)
stack.append(7)
if len(stack) > 0:
    print(stack[-1], stack.pop())
print(stack)
```

Ask what each pending stack entry is waiting for, and what event makes it safe to pop.


**Exit check:** Explain a stack invariant and the total number of pushes and pops.

### Valid brackets

Return whether text is properly nested. text contains only ()[]{} and has at most 1000 characters. Empty is valid.

**Syntax lessons:** 1, 2, 3, 4, 5, 6, 13

```python
def solve(text):
    # Replace this return with your solution.
    return 0
```

Published cases:

- nested: `solve('([]{})')` -> `True`
- crossed: `solve('([)]')` -> `False`
- early close: `solve(')')` -> `False`
- leftover: `solve('(')` -> `False`
- empty: `solve('')` -> `True`

<details><summary>Hint</summary>

Push openings; for a closing, require the matching most recent opening.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(text):
    matching = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in text:
        if ch in '([{':
            stack.append(ch)
        else:
            if len(stack) == 0 or stack.pop() != matching[ch]:
                return False
    return len(stack) == 0
```

Short-circuit or avoids popping an empty stack.

O(n) time; O(n) space.

</details>

### Days until a warmer temperature

Return one distance per day to the next strictly warmer day, or 0 if none. temps has 0 to 1000 integer temperatures. Equal is not warmer.

**Syntax lessons:** 1, 2, 3, 4, 7, 13

```python
def solve(temps):
    # Replace this return with your solution.
    return 0
```

Published cases:

- mixed: `solve([73, 74, 75, 71, 69, 72, 76, 73])` -> `[1, 1, 4, 2, 1, 1, 0, 0]`
- equal: `solve([70, 70])` -> `[0, 0]`
- falling: `solve([3, 2, 1])` -> `[0, 0, 0]`
- empty: `solve([])` -> `[]`

<details><summary>Hint</summary>

Keep indexes of unresolved days with nonincreasing temperatures.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(temps):
    out = [0] * len(temps)
    stack = []
    for i, value in enumerate(temps):
        while len(stack) > 0 and temps[stack[-1]] < value:
            previous = stack.pop()
            out[previous] = i - previous
        stack.append(i)
    return out
```

A warmer day resolves pending colder days; unresolved indexes retain zero.

O(n) time; O(n) space including output.

</details>

## 14. Imports, queues and BFS

3. Learn data structures

Process work in first-in, first-out order.

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

```python
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
```

Separate the queue's pending work from the visited set. The set records discovery, not completion.


**Exit check:** Choose stack versus queue and explain when BFS proves a shortest path.

### Queue operations

ops is a list of at most 1000 two-item lists [action, value]. action is 'add' or 'take'. Add enqueues value; take ignores value and records the oldest item, or -1 if empty. Return recorded removals.

**Syntax lessons:** 1, 2, 3, 4, 7, 14

```python
def solve(ops):
    # Replace this return with your solution.
    return 0
```

Published cases:

- fifo: `solve([['add', 2], ['add', 4], ['take', 0], ['take', 0]])` -> `[2, 4]`
- empty take: `solve([['take', 0]])` -> `[-1]`
- no ops: `solve([])` -> `[]`

<details><summary>Hint</summary>

Use deque; add on the right and take from the left.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
from collections import deque

def solve(ops):
    queue = deque()
    out = []
    for action, value in ops:
        if action == 'add':
            queue.append(value)
        elif len(queue) > 0:
            out.append(queue.popleft())
        else:
            out.append(-1)
    return out
```

The output records only take operations. The -1 rule makes empty behavior explicit.

O(n) time; O(n) space.

</details>

### Fewest increments

Start at 0; each move adds 1 or 2. Return the fewest moves to target, an integer from 0 to 100. Practice BFS even though an arithmetic formula exists. Do not visit positions beyond target.

**Syntax lessons:** 1, 2, 3, 4, 5, 7, 14

```python
def solve(target):
    # Replace this return with your solution.
    return 0
```

Published cases:

- zero: `solve(0)` -> `0`
- one: `solve(1)` -> `1`
- odd: `solve(7)` -> `4`
- even: `solve(10)` -> `5`

<details><summary>Hint</summary>

Queue position-distance pairs; return when target is removed from the queue.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
from collections import deque

def solve(target):
    queue = deque([(0, 0)])
    seen = {0}
    while len(queue) > 0:
        position, distance = queue.popleft()
        if position == target:
            return distance
        for nxt in [position + 1, position + 2]:
            if nxt <= target and nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, distance + 1))
    return -1
```

FIFO order processes distances in increasing layers, making the first target distance minimal.

O(target+1) time and space.

</details>

## 15. Recursion and the call stack

3. Learn data structures

Define a smaller subproblem and a stopping case.

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

```python
def factorial(n):
    if n <= 1:
        return 1
    smaller = factorial(n - 1)
    return n * smaller

print(factorial(4))  # 24
```

State three things: the base case, the smaller argument, and how its returned result builds this result.


**Exit check:** Trace call frames and account for stack space.

### Recursive factorial

Return n! using recursion. n is an integer from 0 to 12; 0! is 1.

**Syntax lessons:** 1, 2

```python
def solve(n):
    # Replace this return with your solution.
    return 0
```

Published cases:

- zero: `solve(0)` -> `1`
- one: `solve(1)` -> `1`
- four: `solve(4)` -> `24`
- six: `solve(6)` -> `720`

<details><summary>Hint</summary>

Stop at 0 or 1. Multiply n by the factorial of n-1.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(n):
    if n <= 1:
        return 1
    return n * solve(n - 1)
```

Each recursive call reduces n and each waiting frame stores constant information.

O(n) time; O(n) call-stack space.

</details>

### Recursive digit sum

Return the sum of decimal digits using recursion. n is an integer from 0 to 1000000000.

**Syntax lessons:** 1, 2

```python
def solve(n):
    # Replace this return with your solution.
    return 0
```

Published cases:

- zero: `solve(0)` -> `0`
- one digit: `solve(7)` -> `7`
- multiple: `solve(1024)` -> `7`
- zeroes: `solve(1000)` -> `1`

<details><summary>Hint</summary>

Separate the last digit with % and recurse on the remaining digits with //.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(n):
    if n < 10:
        return n
    return n % 10 + solve(n // 10)
```

The integer loses a digit each call, so it reaches the single-digit base case.

O(d) time and stack space for d digits.

</details>

## 16. Nested helpers and backtracking

4. Traverse and search

Explore choices, copy answers, and undo mutations.

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

```python
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
```

Record a path snapshot at a complete answer. After every recursive call, restore exactly the state that existed before the choice.


**Exit check:** Explain why appending the path without copying would corrupt earlier answers.

### All subsets

Return every subset of a list of 0 to 10 distinct integers. Process indexes left to right; explore exclusion before inclusion. Preserve original order within subsets. The empty list produces [[]].

**Syntax lessons:** 1, 2, 4, 5, 13

```python
def solve(nums):
    # Replace this return with your solution.
    return 0
```

Published cases:

- two: `solve([1, 2])` -> `[[], [2], [1], [1, 2]]`
- empty: `solve([])` -> `[[]]`
- one: `solve([9])` -> `[[], [9]]`

<details><summary>Hint</summary>

At each index, recurse without the value, then append it, recurse, and pop it.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums):
    out = []
    path = []
    def visit(index):
        if index == len(nums):
            out.append(path[:])
            return
        visit(index + 1)
        path.append(nums[index])
        visit(index + 1)
        path.pop()
    visit(0)
    return out
```

Every sequence of inclusion decisions produces one distinct subset; copying freezes its current path.

O(n * 2**n) time and output space; O(n) additional stack/path.

</details>

### Binary strings without adjacent ones

Return all length-n strings of '0' and '1' without '11', in lexicographic order (try '0' first). n is from 0 to 10. For n=0 return [''].

**Syntax lessons:** 1, 2, 4

```python
def solve(n):
    # Replace this return with your solution.
    return 0
```

Published cases:

- zero: `solve(0)` -> `['']`
- one: `solve(1)` -> `['0', '1']`
- two: `solve(2)` -> `['00', '01', '10']`
- three: `solve(3)` -> `['000', '001', '010', '100', '101']`

<details><summary>Hint</summary>

Always allow 0; allow 1 only at the start or after 0.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(n):
    out = []
    def visit(text):
        if len(text) == n:
            out.append(text)
            return
        visit(text + '0')
        if len(text) == 0 or text[-1] != '1':
            visit(text + '1')
    visit('')
    return out
```

Pruning rejects invalid prefixes before exploring their descendants. Immutable strings require no undo step.

O(n * 2**n) upper bound on time and output space; O(n squared) upper bound for live copied prefixes.

</details>

## 17. Classes, objects and linked lists

4. Traverse and search

Follow references rather than array indexes.

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

```python
class ListNode:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

head = ListNode(4, ListNode(7))
node = head
while node is not None:
    print(node.val)
    node = node.next
print(head is head, head is head.next)
```

Draw boxes for objects and arrows for references. Trace empty, one-node, two-node and cyclic structures before coding.


**Exit check:** Explain self, constructor calls, default arguments, field access and identity.

### Middle node value

head is None or the head of an acyclic list with at most 100 nodes. Return the middle node's val, choosing the second middle for even length. Return None for empty. Keep the supplied ListNode definition.

**Syntax lessons:** 1, 2, 3, 4, 7, 17

```python
class ListNode:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

def solve(head):
    # Replace this return with your solution.
    return 0
```

Published cases:

- odd: `solve(ListNode(1, ListNode(2, ListNode(3))))` -> `2`
- even: `solve(ListNode(1, ListNode(2)))` -> `2`
- one: `solve(ListNode(8))` -> `8`
- empty: `solve(None)` -> `None`

<details><summary>Hint</summary>

Start both references at head; move fast two links and slow one.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
class ListNode:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

def solve(head):
    slow = head
    fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    if slow is None:
        return None
    return slow.val
```

When fast reaches the end, slow has taken half as many steps, choosing the second middle.

O(n) time; O(1) space.

</details>

### Detect a linked-list cycle

Return True if following next references repeats a node, otherwise False. There are at most 100 distinct ListNode objects. Equal values alone are not a cycle. Tests show how cyclic fixtures are constructed.

**Syntax lessons:** 1, 2, 3, 4, 7, 17

```python
class ListNode:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

def solve(head):
    # Replace this return with your solution.
    return 0
```

Published cases:

Fixture setup:

```python
cycle = ListNode(1, ListNode(2))
cycle.next.next = cycle
self_cycle = ListNode(9)
self_cycle.next = self_cycle
```

- cycle: `solve(cycle)` -> `True`
Fixture setup:

```python
cycle = ListNode(1, ListNode(2))
cycle.next.next = cycle
self_cycle = ListNode(9)
self_cycle.next = self_cycle
```

- equal values no cycle: `solve(ListNode(1, ListNode(1)))` -> `False`
Fixture setup:

```python
cycle = ListNode(1, ListNode(2))
cycle.next.next = cycle
self_cycle = ListNode(9)
self_cycle.next = self_cycle
```

- self cycle: `solve(self_cycle)` -> `True`
Fixture setup:

```python
cycle = ListNode(1, ListNode(2))
cycle.next.next = cycle
self_cycle = ListNode(9)
self_cycle.next = self_cycle
```

- empty: `solve(None)` -> `False`

<details><summary>Hint</summary>

Move first, then compare node identity; both references initially equal head even in an acyclic list.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
class ListNode:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

def solve(head):
    slow = head
    fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
```

Within a finite cycle, the relative gap changes by one per step until the references meet.

O(n) time; O(1) space.

</details>

## 18. Binary trees: DFS and BFS

4. Traverse and search

Combine child results and traverse levels.

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

```python
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def depth(root):
    if root is None:
        return 0
    return 1 + max(depth(root.left), depth(root.right))

root = TreeNode(2, TreeNode(1), TreeNode(3))
print(depth(root), root.left.val, root.right.val)
```

Define what each recursive call returns. Keep 'visit order' separate from 'what result this call computes'.


**Exit check:** Trace a tree by object references and explain depth versus breadth memory use.

### Maximum tree depth

Return maximum depth measured in nodes. root is None or a TreeNode in an acyclic binary tree with at most 100 nodes. Empty depth is 0.

**Syntax lessons:** 1, 2, 4, 7, 8, 17, 18

```python
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def solve(root):
    # Replace this return with your solution.
    return 0
```

Published cases:

- balanced: `solve(TreeNode(2, TreeNode(1), TreeNode(3)))` -> `2`
- skewed: `solve(TreeNode(1, None, TreeNode(2, None, TreeNode(3))))` -> `3`
- leaf: `solve(TreeNode(5))` -> `1`
- empty: `solve(None)` -> `0`

<details><summary>Hint</summary>

The base case is None; take the larger child depth and add one.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def solve(root):
    if root is None:
        return 0
    return 1 + max(solve(root.left), solve(root.right))
```

Every node returns the height of its own subtree.

O(n) time; O(h) recursion space.

</details>

### Inorder traversal

Return values in left-node-right order. root is None or the root of an acyclic TreeNode tree with at most 100 nodes; it need not be a BST.

**Syntax lessons:** 1, 2, 4, 7, 17, 18

```python
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def solve(root):
    # Replace this return with your solution.
    return 0
```

Published cases:

- balanced: `solve(TreeNode(2, TreeNode(1), TreeNode(3)))` -> `[1, 2, 3]`
- not bst: `solve(TreeNode(9, TreeNode(7), TreeNode(1)))` -> `[7, 9, 1]`
- empty: `solve(None)` -> `[]`
- right only: `solve(TreeNode(1, None, TreeNode(2)))` -> `[1, 2]`

<details><summary>Hint</summary>

Reuse the nested helper pattern and append between the two recursive calls.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def solve(root):
    out = []
    def visit(node):
        if node is None:
            return
        visit(node.left)
        out.append(node.val)
        visit(node.right)
    visit(root)
    return out
```

Appending between left and right produces inorder regardless of numeric ordering.

O(n) time; O(h) working stack plus O(n) output.

</details>

## 19. Graphs and grids

4. Traverse and search

Represent neighbors and avoid repeated work.

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

```python
grid = [[1, 0], [1, 1]]
row, col = 0, 0
for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
    nr, nc = row + dr, col + dc
    if nr >= 0 and nr < len(grid) and nc >= 0 and nc < len(grid[0]):
        print(nr, nc, grid[nr][nc])
seen = {(0, 0)}
print((row, col) in seen)
```

State vertices, edges, direction, and movement rules before choosing a traversal. O(V+E) counts vertices plus adjacency entries.


**Exit check:** Explain visited timing, bounds checks, and why BFS rather than DFS finds a shortest unweighted path.

### Shortest unweighted directed path

graph is an adjacency list with 1 to 100 vertices and valid integer neighbors. Return the fewest directed edges from start to target, or -1 if unreachable. Both vertices are valid. Cycles and self-edges are allowed.

**Syntax lessons:** 1, 2, 3, 4, 5, 7, 14

```python
def solve(graph, start, target):
    # Replace this return with your solution.
    return 0
```

Published cases:

- shortest: `solve([[1, 2], [3], [3], []], 0, 3)` -> `2`
- cycle unreachable: `solve([[1], [0], []], 0, 2)` -> `-1`
- same: `solve([[]], 0, 0)` -> `0`
- directed: `solve([[1], []], 1, 0)` -> `-1`

<details><summary>Hint</summary>

Adapt the number BFS: neighbors now come from graph[node].

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
from collections import deque

def solve(graph, start, target):
    queue = deque([(start, 0)])
    seen = {start}
    while len(queue) > 0:
        node, distance = queue.popleft()
        if node == target:
            return distance
        for neighbor in graph[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, distance + 1))
    return -1
```

FIFO order guarantees minimum edges; visited prevents infinite cycling.

O(V+E) time; O(V) space.

</details>

### Count islands

Return the number of four-directionally connected groups of 1 cells. grid is [] or a rectangular grid with at most 30 rows and 30 columns; cells are integer 0 or 1. An empty row is allowed. Do not mutate grid.

**Syntax lessons:** 1, 2, 3, 4, 5, 7, 13

```python
def solve(grid):
    # Replace this return with your solution.
    return 0
```

Published cases:

- two: `solve([[1, 1, 0], [0, 0, 1]])` -> `2`
- diagonal separate: `solve([[1, 0], [0, 1]])` -> `2`
- water: `solve([[0, 0]])` -> `0`
- empty: `solve([])` -> `0`
- empty row: `solve([[]])` -> `0`

<details><summary>Hint</summary>

Each unseen land cell begins one flood fill. Mark neighbors when pushing them.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(grid):
    if len(grid) == 0:
        return 0
    rows = len(grid)
    cols = len(grid[0])
    seen = set()
    count = 0
    for row in range(rows):
        for col in range(cols):
            if grid[row][col] == 1 and (row, col) not in seen:
                count += 1
                seen.add((row, col))
                stack = [(row, col)]
                while len(stack) > 0:
                    r, c = stack.pop()
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if nr >= 0 and nr < rows and nc >= 0 and nc < cols:
                            if grid[nr][nc] == 1 and (nr, nc) not in seen:
                                seen.add((nr, nc))
                                stack.append((nr, nc))
    return count
```

Each flood fill claims exactly one connected component; restarting counts all components.

O(rows * cols) time and space.

</details>

## 20. Heaps and priority queues

5. Build interview solutions

Keep the best pending candidate available.

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

```python
import heapq

heap = [4, 1, 7]
heapq.heapify(heap)
heapq.heappush(heap, 2)
print(heap[0], heapq.heappop(heap))
```

Use a heap when the best current item changes after each operation; sorting once is often simpler when all results are needed.


**Exit check:** Explain what the heap root means and why a size-k heap can discard its minimum.

### Kth largest element

Return the kth largest entry, counting duplicates separately. nums has 1 to 1000 integers and 1 <= k <= len(nums). Keep a heap of at most k entries and do not mutate nums.

**Syntax lessons:** 1, 2, 3, 4, 14, 20

```python
def solve(nums, k):
    # Replace this return with your solution.
    return 0
```

Published cases:

- typical: `solve([3, 2, 1, 5, 6, 4], 2)` -> `5`
- duplicates: `solve([2, 2, 1], 2)` -> `2`
- negative: `solve([-3, -1, -2], 3)` -> `-3`
- one: `solve([8], 1)` -> `8`

<details><summary>Hint</summary>

Push each value and remove the minimum whenever the heap grows beyond k.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
import heapq

def solve(nums, k):
    heap = []
    for value in nums:
        heapq.heappush(heap, value)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]
```

The heap contains the k largest entries processed so far; its minimum is kth largest.

O(n log(k+1)) time; O(k) space.

</details>

### Last stone weight

Repeatedly take the two heaviest positive integer stones. Equal weights disappear; otherwise insert their positive difference. Return the final weight or 0 if none. stones has 0 to 100 values, each at most 1000. Do not mutate input.

**Syntax lessons:** 1, 2, 3, 4, 14, 20

```python
def solve(stones):
    # Replace this return with your solution.
    return 0
```

Published cases:

- typical: `solve([2, 7, 4, 1, 8, 1])` -> `1`
- equal: `solve([4, 4])` -> `0`
- one: `solve([9])` -> `9`
- empty: `solve([])` -> `0`

<details><summary>Hint</summary>

Negative weights make the smallest stored value represent the heaviest stone.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
import heapq

def solve(stones):
    heap = []
    for value in stones:
        heap.append(-value)
    heapq.heapify(heap)
    while len(heap) > 1:
        first = -heapq.heappop(heap)
        second = -heapq.heappop(heap)
        if first != second:
            heapq.heappush(heap, -(first - second))
    if len(heap) == 0:
        return 0
    return -heap[0]
```

Each iteration reduces the number of stones, and the heap exposes the two greatest weights.

O(n log n) time; O(n) space.

</details>

## 21. Greedy choices and intervals

5. Build interview solutions

Justify a local decision and define endpoint rules.

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

```python
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
```

Try to construct a counterexample to the greedy choice. If you cannot explain why it is safe, return to state or exhaustive search.


**Exit check:** Explain a greedy invariant, interval endpoints and nested-list aliasing.

### Best one-transaction stock profit

Return the largest profit from buying once and selling on a later day. You may skip trading and return 0. prices has 0 to 1000 nonnegative integer prices.

**Syntax lessons:** 1, 2, 3, 4, 8

```python
def solve(prices):
    # Replace this return with your solution.
    return 0
```

Published cases:

- rise after dip: `solve([7, 1, 5, 3, 6, 4])` -> `5`
- falling: `solve([7, 5, 2])` -> `0`
- one: `solve([4])` -> `0`
- empty: `solve([])` -> `0`

<details><summary>Hint</summary>

Track the minimum earlier price and compare its profit with each possible sale.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(prices):
    if len(prices) == 0:
        return 0
    lowest = prices[0]
    best = 0
    for price in prices:
        best = max(best, price - lowest)
        lowest = min(lowest, price)
    return best
```

The best purchase for any sale is the lowest price before it; skipped trades keep profit nonnegative.

O(n) time; O(1) space.

</details>

### Merge closed intervals

Return merged intervals sorted by start. Each closed interval [start,end] has integer start <= end. Touching endpoints overlap. There are 0 to 1000 intervals. Do not mutate the original pairs.

**Syntax lessons:** 1, 2, 3, 4, 7, 8

```python
def solve(intervals):
    # Replace this return with your solution.
    return 0
```

Published cases:

- touch and overlap: `solve([[1, 3], [2, 6], [8, 10], [10, 12]])` -> `[[1, 6], [8, 12]]`
- nested: `solve([[1, 9], [2, 3]])` -> `[[1, 9]]`
- unsorted: `solve([[5, 5], [1, 2]])` -> `[[1, 2], [5, 5]]`
- empty: `solve([])` -> `[]`

<details><summary>Hint</summary>

Sort by start; merge into the last output pair when start <= its end.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def start_key(interval):
    return interval[0]

def solve(intervals):
    out = []
    for start, end in sorted(intervals, key=start_key):
        if len(out) == 0 or start > out[-1][1]:
            out.append([start, end])
        else:
            out[-1][1] = max(out[-1][1], end)
    return out
```

Earlier sorted intervals cannot overlap a later interval without also overlapping the last merged interval.

O(n log n) time; O(n) space including sort and output.

</details>

## 22. One-dimensional dynamic programming

5. Build interview solutions

Define a reusable state before writing a recurrence.

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

```python
def ways(n):
    dp = [0] * (n + 2)
    dp[0] = 1
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

print(ways(4))  # 5
```

Distinguish counting, minimizing and maximizing states. An unexplained recurrence is harder to debug than a clear state definition.


**Exit check:** Derive a transition, supply base cases and explain why the iteration order makes dependencies available.

### Climbing stairs

Return the number of ordered sequences of 1-step and 2-step moves reaching step n. n is from 0 to 30. For n=0 there is one empty sequence.

**Syntax lessons:** 1, 3, 4

```python
def solve(n):
    # Replace this return with your solution.
    return 0
```

Published cases:

- zero: `solve(0)` -> `1`
- one: `solve(1)` -> `1`
- two: `solve(2)` -> `2`
- five: `solve(5)` -> `8`

<details><summary>Hint</summary>

Classify a route by its last move; the earlier route ends at n-1 or n-2.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(n):
    dp = [0] * (n + 2)
    dp[0] = 1
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]
```

The two last-move classes are disjoint, so their counts add.

O(n) time and space; a rolling version uses O(1) space.

</details>

### Maximum nonadjacent sum

Return the greatest sum obtainable by selecting no adjacent entries. You may select none. nums has 0 to 1000 nonnegative integers.

**Syntax lessons:** 1, 3, 8

```python
def solve(nums):
    # Replace this return with your solution.
    return 0
```

Published cases:

- typical: `solve([2, 7, 9, 3, 1])` -> `12`
- greedy trap: `solve([2, 1, 1, 2])` -> `4`
- one: `solve([8])` -> `8`
- empty: `solve([])` -> `0`

<details><summary>Hint</summary>

For each prefix, compare skipping the new value with taking it after the prefix two positions earlier.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums):
    two_back = 0
    one_back = 0
    for value in nums:
        current = max(one_back, two_back + value)
        two_back = one_back
        one_back = current
    return one_back
```

The rolling variables preserve exactly the two dependent prefix optima.

O(n) time; O(1) space.

</details>

## 23. DP tables and unbounded choices

5. Build interview solutions

Translate dependencies into a table and handle impossible states.

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

```python
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
```

For each table cell, identify its dependencies and prove they were evaluated earlier. Explain the impossible-state sentinel.


**Exit check:** Build nonaliased rows and distinguish unlimited coin reuse from choosing each item once.

### Unique right-down grid paths

Return the number of paths from top-left to bottom-right using only right and down. rows and cols are integers from 1 to 15. A 1 by 1 grid has one empty-move path.

**Syntax lessons:** 1, 2, 3, 4, 8

```python
def solve(rows, cols):
    # Replace this return with your solution.
    return 0
```

Published cases:

- rectangle: `solve(3, 7)` -> `28`
- single: `solve(1, 1)` -> `1`
- one row: `solve(1, 5)` -> `1`
- one col: `solve(4, 1)` -> `1`

<details><summary>Hint</summary>

Add paths from above and left; seed only the starting cell.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(rows, cols):
    dp = [[0] * cols for _ in range(rows)]
    dp[0][0] = 1
    for r in range(rows):
        for c in range(cols):
            if r > 0:
                dp[r][c] += dp[r - 1][c]
            if c > 0:
                dp[r][c] += dp[r][c - 1]
    return dp[-1][-1]
```

Each path has a unique final direction, so predecessor counts add without overlap.

O(rows * cols) time and space.

</details>

### Fewest coins

Return the fewest coins summing to amount, or -1 if impossible. coins has 1 to 20 distinct positive integer denominations; each may be used unlimited times. amount is from 0 to 1000.

**Syntax lessons:** 1, 2, 3, 4, 8

```python
def solve(coins, amount):
    # Replace this return with your solution.
    return 0
```

Published cases:

- typical: `solve([1, 2, 5], 11)` -> `3`
- impossible: `solve([2], 3)` -> `-1`
- zero: `solve([2], 0)` -> `0`
- greedy trap: `solve([1, 3, 4], 6)` -> `2`

<details><summary>Hint</summary>

Solve smaller amounts first, taking the minimum over all possible final coins.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(coins, amount):
    dp = [amount + 1] * (amount + 1)
    dp[0] = 0
    for total in range(1, amount + 1):
        for coin in coins:
            if coin <= total:
                dp[total] = min(dp[total], dp[total - coin] + 1)
    if dp[amount] == amount + 1:
        return -1
    return dp[amount]
```

Every feasible solution has a final coin; considering all denominations covers it. The sentinel never wins over a feasible count.

O(amount * len(coins)) time; O(amount) space.

</details>

## 24. Bits and integer behavior

5. Build interview solutions

Use binary operations only after learning their meaning.

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

```python
print(6 & 3, 6 | 3, 6 ^ 3, 1 << 3, 8 >> 1, ~0)
n = 13
count = 0
while n > 0:
    count += n & 1
    n = n >> 1
print(count)  # 3
```

Use bit tricks only when the input contract supplies the necessary pairing or nonnegative assumptions.


**Exit check:** Explain XOR cancellation, boolean versus bitwise operators, and bounded-integer assumptions.

### Single number

Return the one value occurring once; every other value occurs exactly twice. nums has 1 to 1001 integers, each between 0 and 1000000. Use XOR and constant auxiliary space.

**Syntax lessons:** 1, 3, 24

```python
def solve(nums):
    # Replace this return with your solution.
    return 0
```

Published cases:

- pair: `solve([2, 2, 1])` -> `1`
- mixed: `solve([4, 1, 2, 1, 2])` -> `4`
- zero: `solve([0])` -> `0`
- one: `solve([9])` -> `9`

<details><summary>Hint</summary>

XOR every entry into a running value starting at zero.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums):
    answer = 0
    for value in nums:
        answer = answer ^ value
    return answer
```

Paired occurrences cancel, leaving only the unpaired value.

O(n) time and O(1) auxiliary space for bounded integers.

</details>

### Count set bits

Return the number of 1 bits in nonnegative integer n, with 0 <= n < 2**31. Use bitwise operations and a loop.

**Syntax lessons:** 1, 2, 3, 24

```python
def solve(n):
    # Replace this return with your solution.
    return 0
```

Published cases:

- zero: `solve(0)` -> `0`
- mixed: `solve(13)` -> `3`
- power of two: `solve(1024)` -> `1`
- all ones: `solve(31)` -> `5`

<details><summary>Hint</summary>

Read the lowest bit, then shift right by one.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(n):
    count = 0
    while n > 0:
        count += n & 1
        n = n >> 1
    return count
```

Each iteration consumes one binary digit. Zero has no set bits.

O(b) time for b bits; O(1) auxiliary space under the 31-bit bound.

</details>

## 25. Interview rehearsal and platform syntax

6. Interview rehearsal

Solve independently and translate your function to an interview platform.

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

```python
from typing import List, Optional

class Solution:
    def total(self, nums: list[int]) -> int:
        return sum(nums)

def identity(value: Optional[int]) -> Optional[int]:
    return value

values: List[int] = [1, 2, 3]
print(Solution().total(values), identity(None))
```

Ready to continue when you can solve both rehearsal tasks from blank, explain their invariants and costs, and reproduce them after a delay. Passing samples alone is insufficient.


**Exit check:** Solve a mixed interview task without hints, translate its signature, and explain an edge-case trace and complexity.

### Rehearsal: product except self

Return a list where out[i] is the product of every input except nums[i]. nums has 2 to 100 bounded integers; zero and negatives are allowed. Use O(n) time, no division, and O(1) working space beyond the output. Products fit within signed 32-bit integers. Start by explaining a brute-force solution.

**Syntax lessons:** 1, 3, 4

```python
def solve(nums):
    # Replace this return with your solution.
    return 0
```

Published cases:

- positive: `solve([1, 2, 3, 4])` -> `[24, 12, 8, 6]`
- one zero: `solve([-1, 1, 0, -3, 3])` -> `[0, 0, 9, 0, 0]`
- two zeroes: `solve([0, 0, 2])` -> `[0, 0, 0]`
- pair: `solve([2, 3])` -> `[3, 2]`

<details><summary>Hint</summary>

Store products strictly before each index, then multiply by products strictly after it.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums):
    out = [1] * len(nums)
    prefix = 1
    for i in range(len(nums)):
        out[i] = prefix
        prefix = prefix * nums[i]
    suffix = 1
    for i in range(len(nums) - 1, -1, -1):
        out[i] = out[i] * suffix
        suffix = suffix * nums[i]
    return out
```

The two passes exclude the current value by updating the running product after storing it. No division means zero needs no special branch.

O(n) time; O(1) auxiliary space beyond O(n) output.

</details>

### Rehearsal: Jump Game

Return whether the last index is reachable from index 0. Each entry is the maximum forward jump from that index (any distance from 1 through that value is allowed). nums has 1 to 1000 nonnegative integers. A one-element input is already reached. Explain why your greedy choice is safe.

**Syntax lessons:** 1, 2, 3, 7, 8

```python
def solve(nums):
    # Replace this return with your solution.
    return 0
```

Published cases:

- reachable: `solve([2, 3, 1, 1, 4])` -> `True`
- blocked: `solve([3, 2, 1, 0, 4])` -> `False`
- one: `solve([0])` -> `True`
- stuck: `solve([0, 1])` -> `False`
- skip zero: `solve([2, 0, 0])` -> `True`

<details><summary>Hint</summary>

Keep the farthest reachable index from all reachable entries processed so far.

</details>

<details><summary>Worked answer (read after attempting)</summary>

```python
def solve(nums):
    farthest = 0
    for i, value in enumerate(nums):
        if i > farthest:
            return False
        farthest = max(farthest, i + value)
    return True
```

Every position up to farthest is reachable because shorter jumps are allowed. An index beyond farthest cannot be rescued by any later, unreachable index.

O(n) time; O(1) space.

</details>

## Authoring and checks

Rebuild with `python tools/python_course.py`. Verify syntax prerequisites, all example programs, every reference answer, input preservation where required, and that every starter fails at least one case with `python tools/verify_python_course.py`. The AST vocabulary check is conservative and cannot prove teaching quality or algorithm correctness; review explanations as well.
