# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 1 — Foundations.
#
# exec()'d by tools/dsa_curriculum.py inside its namespace; see that file's
# header for the helpers and the four design rules.
#
# This stage exists because the rest of the curriculum silently assumes three
# things that nobody is born knowing: that a program reads stdin and writes
# stdout (not "returns a value"), that a loop is the only tool for "do this to
# every element", and that an array index is a position rather than a value.
# The 28 Intro problems in the bank live here, and the stage is deliberately
# boring — its job is to make the keyboard stop being the bottleneck.
# ---------------------------------------------------------------------------

_S1 = _stage(
    "foundations", "Foundations", "🌱",
    "Make the keyboard stop being the bottleneck.",
    """
Before a single algorithm is worth learning, four things have to be automatic:
reading input, doing arithmetic without overflowing, branching, and looping.
Every problem in this stage is solvable in under ten lines. That is the point —
you are not learning to think yet, you are learning to type what you already
think without stopping to look anything up.

Finish this stage when you can open any of its problems and have a correct
program before you have finished re-reading the statement.
""")


# --- Unit 1 — Input, output, arithmetic -------------------------------------

_unit(
    "io-and-arithmetic", "Input, Output & Arithmetic", "⌨️", _S1,
    "Read the numbers, do the sum, print the answer.",
    weight=1,
    why="""
Every problem in this app speaks one protocol: the grader writes your input to
**stdin**, your program writes its answer to **stdout**, and the two are
compared as text. No function is called for you and nothing is returned. Until
that loop is automatic — read, compute, print — every other idea in the
curriculum is blocked behind a plumbing problem.

This unit also introduces the first bug that will follow you all the way to the
Hard problems: an `int` in Java holds numbers up to about 2.1 billion, and
quietly wraps around past that.
""",
    model="""
### The shape of every program here

```
read the input  →  compute  →  print exactly one answer
```

**Reading.** `Scanner` is the readable choice and fast enough for everything in
this stage. `sc.nextInt()` pulls the next whitespace-separated token and parses
it; `sc.nextLine()` takes the rest of the current line, newline included.
Whitespace — spaces versus newlines — does not matter to `nextInt()`, which is
why problem statements can describe input loosely.

**Printing.** `System.out.println(x)` writes the value and a newline. The judge
normalises trailing whitespace and trailing blank lines, so a stray final
newline will not fail you — but a missing digit, an extra word, or different
capitalisation will.

**Arithmetic on `int`.** `/` between two `int`s is *integer division*: it
truncates toward zero, so `7 / 2` is `3` and `-7 / 2` is `-3`. `%` is the
remainder and keeps the sign of the left operand, so `-7 % 3` is `-1`, not `2`.
Both facts will bite you in the digits unit.

**Overflow.** `int` spans −2,147,483,648 … 2,147,483,647. Multiply two values
near 100,000 and you are already outside it — silently, with a wrong answer
rather than a crash. When a constraint says values reach 10⁹, or when you
multiply or sum many of them, compute in `long`.
""",
    signals=[
        _sig("“There is no input”", "Print the constant",
             "Nothing to read; the whole program is one `println`."),
        _sig("“A single integer n” / “two integers a and b”", "`sc.nextInt()` per value",
             "Order in the statement is order on the input."),
        _sig("“A single line of text”", "`sc.nextLine()`",
             "Text can contain spaces, so tokens are the wrong unit."),
        _sig("Constraints reach 10⁹, or you multiply two inputs", "`long`",
             "Two values near 10⁹ overflow `int` on the very first multiply."),
    ],
    skeletons=[
        _sk("Read numbers, print an answer",
            "The default shape for almost every problem in the app.",
            """
import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.println(a + b);
    }
}
""",
            "Declare `Scanner` once, read in statement order, print exactly one line."),
        _sk("Read a whole line of text",
            "When the input is a sentence, a word, or anything with spaces.",
            """
import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String line = sc.nextLine();
        System.out.println(line);
    }
}
""",
            "Mixing `nextInt()` and `nextLine()` needs care — see the pitfalls."),
        _sk("Compute in long, print as long",
            "Any time a product or a running sum can leave int's range.",
            """
long total = 0;
for (int i = 0; i < n; i++) {
    total += sc.nextLong();   // read as long, not int
}
System.out.println(total);
""",
            "`(long) a * b` casts *before* multiplying; `(long)(a * b)` is already too late."),
    ],
    costs=[
        _cost("Reading one token with Scanner", "O(1) amortised", "O(1)",
              "Fine up to ~10⁵ tokens; BufferedReader is the upgrade beyond that."),
        _cost("Any fixed arithmetic expression", "O(1)", "O(1)",
              "Cost does not depend on the size of the numbers here."),
    ],
    pitfalls=[
        _pit("`InputMismatchException` on the first read",
             "`nextInt()` hit a token that is not an integer — often because the "
             "input starts with a line of text, or a previous `nextLine()` consumed it.",
             "Match the read calls to the input format line by line before running."),
        _pit("The line you read back is empty",
             "`nextInt()` leaves the newline behind; the next `nextLine()` returns that "
             "empty remainder rather than the following line.",
             "Call `sc.nextLine()` once to discard the remainder before reading real text."),
        _pit("Correct on small cases, wrong on the big one",
             "`int` overflow. The wrong answer is often negative or wildly small.",
             "Do the arithmetic in `long`, casting before the multiply: `(long) a * b`."),
        _pit("Off by one on a division",
             "Integer division truncates toward zero rather than rounding.",
             "For a ceiling of `a / b` with positive values, write `(a + b - 1) / b`."),
    ],
    lessons=["alg_what_is", "io_basics", "variables", "arithmetic", "overflow"],
    checks=[
        _chk("What does `7 / 2` evaluate to in Java, and what about `-7 / 2`?",
             "`3` and `-3`. Integer division truncates **toward zero**, so the negative "
             "case rounds up rather than down."),
        _chk("`int a = 100000, b = 100000; long c = a * b;` — what is `c`?",
             "`1410065408`, not 10¹⁰. The multiply happens in `int` and overflows *before* "
             "the widening to `long`. Write `(long) a * b`."),
        _chk("Why does `sc.nextLine()` sometimes return an empty string?",
             "Because `nextInt()` stops at the end of the number and leaves the newline in "
             "the buffer. The next `nextLine()` consumes that remainder."),
        _chk("The expected output is `Hello, World!` and you print `hello, world!`. Pass or fail?",
             "Fail. The judge normalises trailing whitespace only — the text itself is "
             "compared exactly, capitalisation included."),
    ],
    interview="""
Nobody asks "add two numbers" in an interview — but every interview starts with
you restating the input format, and roughly a third of failed phone screens are
really *"I never confirmed what the input looked like"*. The habit this unit
builds is the one that matters: read the format out loud, name the types, and
say where overflow could happen, before writing a line.
""",
    rungs=[
        _rung("Warm up", "Prove the pipe works: read nothing, print something.",
              ["print-greeting", "echo-line"],
              {"print-greeting": "The whole program is one `println`. If this passes, your toolchain is live."}),
        _rung("Core", "Read values, apply a formula, print one answer.",
              ["add-two-numbers", "rectangle-area", "square-number", "cube-number"],
              {"rectangle-area": "The first place `long` is worth a thought: two sides near 10⁵ already exceed `int` when multiplied."}),
        _rung("Variations", "Same shape, slightly awkward arithmetic.",
              ["absolute-value", "seconds-to-clock"],
              {"seconds-to-clock": "Integer division and `%` doing real work — and zero-padded formatting, which is a printing problem, not a maths one."}),
    ],
    next_up="""
You can read, compute and print. The next unit asks the program to make a
decision instead of always doing the same thing.
""",
)


# --- Unit 2 — Branching -----------------------------------------------------

_unit(
    "branching", "Branching & Conditions", "🔀", _S1,
    "Pick an answer instead of computing one.",
    weight=1,
    prereqs=["io-and-arithmetic"],
    why="""
A formula gives the same shape of answer every time. The moment a problem says
*"if … otherwise …"*, *"the larger of"*, or *"is it …?"*, the program has to
choose a branch. Getting that right is mostly about one thing people skip:
enumerating the cases and checking they are **exhaustive and non-overlapping**.

Every later unit leans on this. A binary search is three cases; a DP transition
is a `max` over cases; a graph traversal is "visited or not". Branching is
never *the* algorithm — it is the joint that every algorithm is built from.
""",
    model="""
### Cases, not conditions

Write the cases down before the code. Three questions:

1. **Are they exhaustive?** Does every possible input match one?
2. **Do they overlap?** If two can be true at once, the *first* one wins — so
   order matters. `n % 15 == 0` must be tested before `n % 3 == 0`.
3. **Where are the boundaries?** The bug is almost always at `==`, at zero, or
   at a negative value.

### The three forms

```java
if (cond) { ... } else { ... }          // two cases
if (a) { } else if (b) { } else { }     // ordered chain, first match wins
cond ? x : y                            // an expression, when both sides are values
```

A `boolean` is already a value — `return n % 2 == 0;` is better than
`if (n % 2 == 0) return true; else return false;`, and the difference is not
style: the second form is where a stray `=` hides.

### Comparison traps

- `&&` and `||` **short-circuit**: the right side is skipped when the left
  settles it. That is what makes `i < n && a[i] == x` safe.
- For `String`, `==` compares *references*. Always `a.equals(b)`.
- Chaining does not work: `a < b < c` does not compile. Write `a < b && b < c`.
""",
    signals=[
        _sig("“is …?”, “return true if …”", "One boolean expression",
             "Return the comparison itself; no `if` is needed."),
        _sig("“the larger / smaller of”", "`Math.max` / `Math.min`",
             "Built-ins say what you mean and cannot be mistyped."),
        _sig("“otherwise”, “in all other cases”", "A final `else`",
             "The word is the statement telling you the chain must be exhaustive."),
        _sig("Overlapping rules (multiples of 3 *and* 5)", "Most specific case first",
             "An ordered chain takes the first match, so the combined case goes first."),
    ],
    skeletons=[
        _sk("Boolean answer",
            "“Is n even?”, “is it a leap year?”, “does it satisfy …?”",
            """
static boolean isEven(int n) {
    return n % 2 == 0;      // the comparison IS the answer
}
""",
            "Never `if (x) return true; else return false;` — return `x`."),
        _sk("Ordered case chain",
            "Several rules where more than one can apply.",
            """
if (n % 15 == 0)      System.out.println("FizzBuzz");
else if (n % 3 == 0)  System.out.println("Fizz");
else if (n % 5 == 0)  System.out.println("Buzz");
else                  System.out.println(n);
""",
            "Most specific first. Reordering these two lines is the classic FizzBuzz bug."),
        _sk("Max of three",
            "Extending a two-way comparison without nesting `if`s.",
            """
int best = Math.max(a, Math.max(b, c));
""",
            "Nesting `Math.max` scales; nesting `if`/`else` past three cases does not."),
    ],
    costs=[
        _cost("A chain of k conditions", "O(k)", "O(1)",
              "Constant in practice — but a condition that scans an array is not O(1)."),
    ],
    pitfalls=[
        _pit("The condition is always true",
             "`=` typed instead of `==`. In Java this only compiles for `boolean`, which "
             "is exactly where it does the most damage.",
             "Put the constant on the left (`if (0 == n)`) if you keep making this typo."),
        _pit("Strings that look equal compare as different",
             "`==` on `String` compares object identity, not characters.",
             "`a.equals(b)`, or `a.equalsIgnoreCase(b)` when case should not matter."),
        _pit("Right answer for positives, wrong for 0 or negatives",
             "The case list was written with only positive input in mind.",
             "Test the boundary explicitly: `0`, `-1`, and the constraint's extremes."),
        _pit("FizzBuzz prints `Fizz` where `FizzBuzz` was expected",
             "The `% 3` branch is tested before the `% 15` branch and wins first.",
             "Order overlapping cases most-specific first."),
    ],
    lessons=["conditionals", "boolean_logic"],
    checks=[
        _chk("Why is `if (i < n && a[i] == x)` safe when `i` may equal `n`?",
             "`&&` short-circuits: when `i < n` is false the right side is never evaluated, "
             "so the out-of-bounds read never happens. Swapping the order crashes."),
        _chk("What is wrong with `if (s == \"yes\")`?",
             "It compares references, not text. It may even appear to work for literals "
             "because of interning, which makes the bug worse. Use `s.equals(\"yes\")`."),
        _chk("Rewrite `if (n % 2 == 0) return true; else return false;`",
             "`return n % 2 == 0;` — the comparison already produces the boolean."),
    ],
    interview="""
Interviewers read your case analysis as a proxy for your rigour. Saying *"three
cases: empty, single element, and the general one"* before you type buys more
credit than any clever line you write afterwards — and it is the same habit that
catches the empty-array bug in the array unit.
""",
    rungs=[
        _rung("Warm up", "One comparison, one answer.",
              ["even-or-odd", "is-even", "larger-of-two", "min-of-two"],
              {"is-even": "Return the comparison. If you wrote an `if`, rewrite it before moving on."}),
        _rung("Core", "More than two cases, so order starts to matter.",
              ["max-of-three", "leap-year", "fizzbuzz-value"],
              {"leap-year": "Three interacting rules — the standard example of a case chain whose order is the whole problem.",
               "fizzbuzz-value": "Overlapping cases. Most specific first, or it is silently wrong."}),
    ],
    next_up="""
You can choose. The next unit repeats — and repetition is where arithmetic on
the *digits* of a number becomes possible.
""",
)


# --- Unit 3 — Loops and digits ----------------------------------------------

_unit(
    "loops-and-digits", "Loops & Digit Arithmetic", "🔁", _S1,
    "Repeat until something runs out — including a number's digits.",
    weight=1,
    prereqs=["branching"],
    why="""
A loop is the first idea in this curriculum whose *cost depends on the input*,
which makes it the first place Big-O means anything at all. It is also where a
second, sneakier skill appears: taking a number apart with `% 10` and `/ 10`,
without ever converting it to a string.

That digit loop shows up far past this stage — in palindromic numbers, in
digital roots, in the base conversion that hides inside bit manipulation. It is
worth being fluent in it now, while the problems are small.
""",
    model="""
### The two loop shapes

```java
for (int i = 0; i < n; i++) { ... }   // a known number of steps
while (n > 0) { ... }                 // until a condition breaks
```

Use `for` when you can say the trip count in advance, and `while` when the body
is what changes the condition. Every `while` needs an answer to *"what makes
this stop?"* — if you cannot say it in a sentence, you have written an infinite
loop.

### Taking a number apart

```java
while (n > 0) {
    int d = n % 10;   // the last digit
    n /= 10;          // drop it
}
```

Three facts make this work, and each one is a bug when forgotten:

- It reads digits **right to left**. If order matters, build the answer in
  reverse or push the digits somewhere.
- It runs **⌊log₁₀ n⌋ + 1 times** — about 10 iterations for an `int`. Digit
  loops are effectively free; that is why they beat string conversion.
- It **never runs for `n == 0`**. A zero-digit-count answer for the input `0` is
  the single most common wrong answer in this unit.

### Accumulators

Almost every loop here carries a value across iterations: a `sum`, a `count`, a
`best`, a `reversed`. Name it for what it holds, initialise it where the empty
case is correct (`sum = 0`, `count = 0`, `product = 1`), and update it exactly
once per iteration.
""",
    signals=[
        _sig("“sum / count / product of the first n …”", "`for` with an accumulator",
             "Trip count known up front."),
        _sig("“digits of n”, “sum of digits”, “reverse the number”", "`% 10` / `/= 10`",
             "Cheap, exact, and avoids string conversion entirely."),
        _sig("“repeat until it reaches 1”", "`while` with a stated stopping condition",
             "The body changes the value the condition tests."),
        _sig("“is it the same backwards?” (a number)", "Rebuild it reversed and compare",
             "Reversing digits is the same `% 10` loop with an accumulator."),
    ],
    skeletons=[
        _sk("Accumulate over a range",
            "Sums, counts, factorials — anything with a known trip count.",
            """
long sum = 0;
for (int i = 1; i <= n; i++) {
    sum += i;
}
System.out.println(sum);
""",
            "`long` because a sum of n terms grows far faster than any single term."),
        _sk("Walk the digits",
            "Digit sums, digit counts, digital roots, digit filters.",
            """
int total = 0, m = Math.abs(n);
if (m == 0) total = 0;             // the case the loop cannot reach
while (m > 0) {
    total += m % 10;
    m /= 10;
}
""",
            "Handle `0` outside the loop, and `Math.abs` before it if input may be negative."),
        _sk("Reverse a number",
            "Palindromic numbers, reversed integers.",
            """
long rev = 0, m = n;
while (m > 0) {
    rev = rev * 10 + m % 10;
    m /= 10;
}
""",
            "`long` for `rev`: reversing a valid `int` can overflow an `int`."),
    ],
    costs=[
        _cost("Loop over n elements", "O(n)", "O(1)", "One pass, one accumulator."),
        _cost("Digit loop on n", "O(log n)", "O(1)",
              "≤ 10 iterations for an `int` — cheaper than any string conversion."),
        _cost("Nested loop over n", "O(n²)", "O(1)",
              "Fine at n ≤ 3,000; the wall the whole next stage exists to avoid."),
    ],
    pitfalls=[
        _pit("The answer is 0 when the input is 0",
             "`while (n > 0)` never executes, so the accumulator keeps its initial value.",
             "Treat `n == 0` as an explicit case before the loop."),
        _pit("The program hangs",
             "A `while` whose body does not move it toward the stopping condition — a "
             "forgotten `n /= 10`, or dividing by a value that can be 1.",
             "State the stopping condition in a sentence; if you cannot, the loop is wrong."),
        _pit("Reversing a large number gives a negative result",
             "The reversed value left `int` range mid-loop.",
             "Accumulate in `long` and compare afterwards."),
        _pit("Off by one in the last iteration",
             "`<` versus `<=`, or starting at 1 where the problem counts from 0.",
             "Say what the *first* and *last* values of `i` should be, then write the header."),
    ],
    lessons=["loops_basic", "math_digits", "big_o"],
    checks=[
        _chk("How many times does `while (n > 0) { n /= 10; }` run for n = 4,096?",
             "Four — once per digit. Generally ⌊log₁₀ n⌋ + 1, which is at most 10 for an `int`."),
        _chk("Why initialise a product accumulator to 1 and a sum accumulator to 0?",
             "They are the identity elements: combining with them changes nothing, so the "
             "empty case comes out right without a special branch."),
        _chk("Why compute a digit sum with `% 10` instead of `String.valueOf(n)`?",
             "It avoids allocating a string and parsing characters, it cannot pick up a "
             "minus sign by accident, and it is the same loop you will reuse for base-2."),
        _chk("What is `-7 % 3` in Java, and why does it matter here?",
             "`-1` — the remainder keeps the sign of the left operand. A digit loop on a "
             "negative number therefore produces negative digits unless you `Math.abs` first."),
    ],
    interview="""
"What is the complexity?" gets asked about the code you just wrote, and a digit
loop is the first place the honest answer is not O(n). Saying *O(log n) in the
value of n, which is at most 10 iterations here* is a small thing that signals
you distinguish the size of the input from the size of the number in it.
""",
    rungs=[
        _rung("Warm up", "A loop with a known trip count and one accumulator.",
              ["sum-to-n", "countdown", "factorial"],
              {"factorial": "The first problem where the *answer* overflows `int` long before the input does."}),
        _rung("Core", "Take a number apart digit by digit.",
              ["sum-of-digits", "count-digits", "digital-root"],
              {"count-digits": "Check your answer for `0` before you submit. Most first attempts print 0 instead of 1."}),
        _rung("Variations", "The digit loop with an accumulator that rebuilds a number.",
              ["palindrome-number", "reverse-integer", "armstrong-number", "collatz-steps"],
              {"collatz-steps": "A `while` whose stopping condition is not obvious from the body — say it out loud before coding.",
               "reverse-integer": "Accumulate in `long`; the reversed value can leave `int` range."}),
    ],
    next_up="""
One value at a time is done. Next: many values at once, and the index
arithmetic that comes with them.
""",
)


# --- Unit 4 — Arrays, first pass --------------------------------------------

_unit(
    "arrays-first-pass", "Arrays: The First Pass", "📊", _S1,
    "One scan, one accumulator, and the index bugs that come free with them.",
    weight=3,
    prereqs=["loops-and-digits"],
    why="""
An array is the first data structure, and *single-pass scanning* is the first
algorithm. Roughly a third of every problem bank — including a surprising
number of the Mediums — is a single pass with a cleverer accumulator, so this
unit is not a warm-up you outgrow: it is the shape you will keep returning to.

It is also where the two eternal array bugs first appear: reading `a[n]`, and
seeding a maximum with `0` when the data can be negative.
""",
    model="""
### What an array actually is

A single fixed-length block of slots, indexed `0 … a.length - 1`. The length is
decided at creation and never changes. `a[a.length]` is always out of bounds —
the `<` in `i < a.length` is not a style choice.

### The single-pass template

```java
int best = a[0];                  // seed from the data, never from 0
for (int i = 1; i < a.length; i++) {
    if (a[i] > best) best = a[i];
}
```

Three decisions, and each one is a bug in waiting:

1. **What does the accumulator hold?** Say it in words: *"the largest value seen
   so far"*. If you cannot, you do not yet have the algorithm.
2. **What is it seeded with?** Seed from the data (`a[0]`) or from a value the
   data cannot beat (`Integer.MIN_VALUE`). `0` is wrong the moment values can be
   negative, and it is wrong silently.
3. **Does the empty array make sense?** `a[0]` on an empty array throws. If the
   constraints permit `n = 0`, decide the answer before the loop.

### When one accumulator is not enough

*Second largest* needs two, and updating them in the right order is the whole
problem: when a new champion arrives, the old champion becomes the runner-up.
Trying to do it with one variable and a second pass is where most wrong answers
come from.

### Counting

"How many elements satisfy P?" is the same template with `count++` in the body.
If P depends on something global — an average, a maximum — you need **two
passes**: compute the global first, then count. Two passes is still O(n); it is
not something to avoid.
""",
    signals=[
        _sig("“sum / count / max / min of the array”", "One pass, one accumulator",
             "Nothing needs to be stored; the running value is the answer."),
        _sig("“how many … than the average”", "Two passes",
             "Pass 1 computes the average, pass 2 counts against it."),
        _sig("“is the array sorted / a permutation?”", "One pass comparing neighbours",
             "A property of adjacent pairs never needs more than `a[i-1]` and `a[i]`."),
        _sig("“the second largest”", "Two accumulators updated together",
             "Update the runner-up in the same branch that replaces the champion."),
        _sig("“longest run of …”", "A current-run counter plus a best-so-far",
             "Reset the current counter the moment the run breaks."),
    ],
    skeletons=[
        _sk("Read an array from stdin",
            "The standard preamble for every array problem in the bank.",
            """
Scanner sc = new Scanner(System.in);
int n = sc.nextInt();
int[] a = new int[n];
for (int i = 0; i < n; i++) a[i] = sc.nextInt();
""",
            "Read `n` first; the input format always gives it before the values."),
        _sk("One pass, one accumulator",
            "Sum, max, min, count — the workhorse.",
            """
long sum = 0;
int best = Integer.MIN_VALUE;
for (int x : a) {
    sum += x;
    if (x > best) best = x;
}
""",
            "The enhanced `for` is clearer when the index is not needed. Seed `best` from "
            "the data or from MIN_VALUE — never from 0."),
        _sk("Two accumulators (second largest)",
            "Any “best and runner-up” question.",
            """
int best = Integer.MIN_VALUE, second = Integer.MIN_VALUE;
for (int x : a) {
    if (x > best) { second = best; best = x; }
    else if (x > second && x < best) { second = x; }
}
""",
            "The demoted champion becomes the runner-up — that is the line people miss."),
        _sk("Longest run",
            "Consecutive ones, longest streak, maximum plateau.",
            """
int run = 0, best = 0;
for (int x : a) {
    run = (x == 1) ? run + 1 : 0;   // extend, or reset
    best = Math.max(best, run);
}
""",
            "Extend-or-reset. The same two lines become Kadane's algorithm in the DP unit."),
    ],
    costs=[
        _cost("Single pass", "O(n)", "O(1)", "The floor: you must at least look at every element."),
        _cost("Two passes", "O(n)", "O(1)", "Still linear. Do not contort the code to avoid it."),
        _cost("Nested pass (every pair)", "O(n²)", "O(1)",
              "Acceptable to about n = 3,000; the reason the next stage exists."),
        _cost("Random access `a[i]`", "O(1)", "—", "Indexing is arithmetic, not a search."),
    ],
    pitfalls=[
        _pit("`ArrayIndexOutOfBoundsException`",
             "`i <= a.length` in the loop header, or comparing `a[i]` with `a[i + 1]` on the "
             "last iteration.",
             "When the body touches `a[i + 1]`, the header must stop at `a.length - 1`."),
        _pit("The maximum comes out as 0 on all-negative input",
             "`best` was seeded with `0`, which no negative value can beat.",
             "Seed from `a[0]` (and start the loop at 1) or from `Integer.MIN_VALUE`."),
        _pit("A sum is wrong only on the largest test",
             "The sum overflowed `int` even though every element fits.",
             "Accumulate sums in `long`."),
        _pit("`second == best` when the array has duplicates",
             "The runner-up branch accepted a value equal to the champion.",
             "Decide what the problem means by *second largest* for `[5, 5, 3]`, then make "
             "the strictness of the comparison match."),
        _pit("Crash on an empty array",
             "`a[0]` was read to seed an accumulator without checking `n > 0`.",
             "Decide the empty-array answer explicitly when the constraints allow `n = 0`."),
    ],
    lessons=["iteration", "array_patterns", "prefix_max"],
    checks=[
        _chk("Why seed a maximum with `a[0]` rather than `0`?",
             "Because `0` is a value the data might never exceed. On `[-5, -2, -9]` the "
             "`0` seed reports `0`, which is not in the array at all."),
        _chk("Is a two-pass solution worse than a one-pass one?",
             "Not asymptotically — both are O(n). Prefer whichever is clearer; only "
             "collapse passes when a measurement or a constraint asks for it."),
        _chk("In the longest-run template, why does `run` reset to 0 rather than 1?",
             "Because the element that broke the run is not part of any run. Resetting to 1 "
             "would count the breaking element itself."),
        _chk("What is the cost of `a[i]` compared with searching for a value in `a`?",
             "`a[i]` is O(1) address arithmetic; searching is O(n). Confusing the two is the "
             "root of most accidental O(n²) code."),
    ],
    interview="""
Every array interview opens with the same three questions, and asking them
yourself scores the points: *Can it be empty? Can values be negative? How large
can the sum get?* Each maps directly onto a pitfall above — and each is a real
bug in the code most candidates write when they skip them.
""",
    rungs=[
        _rung("Warm up", "One pass, one accumulator.",
              ["count-evens", "array-sum", "array-minimum", "array-maximum"],
              {"array-maximum": "Try it once with a `0` seed on all-negative input, so the bug is one you have actually seen."}),
        _rung("Core", "Accumulators that carry a little more state.",
              ["alternating-sum", "count-negatives", "count-occurrences", "max-consecutive-ones"],
              {"max-consecutive-ones": "Extend-or-reset. This exact pair of lines returns as Kadane's algorithm."}),
        _rung("Variations", "Properties of neighbours, and of the array as a whole.",
              ["is-sorted", "mountain-array", "is-permutation-1n"],
              {"is-sorted": "The first problem where the loop must stop at `a.length - 1`, because the body reads `a[i + 1]`.",
               "is-permutation-1n": "A seen-array indexed by value — the first hint of the hashing idea two units away."}),
    ],
    next_up="""
You can scan. The next stage asks the question that turns scanning into
engineering: *how expensive is this, and can it be cheaper?*
""",
)
