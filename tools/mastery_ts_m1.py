# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — Month 1: Language foundations (weeks 1-4).
#
# The month's week tables, coding finals, authored bank questions and the
# extra final tests. exec()'d in order by mastery_defs.py, which defines
# `_w`, `_ts_exam` and the four collections this file extends.
# ---------------------------------------------------------------------------

TS_WEEKS.extend([
    # =======================================================================
    # MONTH 1 — Language foundations
    # =======================================================================
    _w(1, "Month 1 · Language foundations",
       "Values, Types & Inference",
       "Declare and annotate values, and understand what TypeScript works out on its own.",
       ["ts_program_io", "ts_variables", "ts_types", "ts_inference"],
       [("print-greeting", "Your first program: read a line, print a line."),
        ("add-two-numbers", "Parse two numbers and print their sum."),
        ("rectangle-area", "Store intermediate results in well-named constants."),
        ("echo-line", "Get comfortable with the stdin/stdout contract.")],
       "Write a `units.ts` that reads a temperature in Celsius and prints it in Fahrenheit and Kelvin, using `const` throughout and one explicit annotation per value.",
       [("Which declaration should you reach for by default?",
         ["const, switching to let only when you must reassign",
          "let, because const is for compile-time constants",
          "var, which is the most compatible",
          "Whichever the inferred type suggests"], 0,
         "`const` locks the binding, which removes a whole class of accidental reassignment. Reach for `let` only when the value genuinely changes."),
        ("What type does `const x = 5` have?",
         ["The literal type 5, because const bindings cannot change",
          "number",
          "any",
          "It has no type until annotated"], 0,
         "A `const` binding to a primitive infers the literal type, since it can never hold anything else. `let y = 5` widens to `number`."),
        ("Why prefer `unknown` over `any` for a value of uncertain type?",
         ["unknown forces you to narrow before using it; any turns checking off entirely",
          "unknown is faster at runtime",
          "any cannot be assigned to variables",
          "There is no difference under strict mode"], 0,
         "`any` silently disables every check that follows it. `unknown` keeps the value opaque until you prove what it is."),
        ("`let count = 0; count = \"zero\";` — what happens?",
         ["A compile error: count was inferred as number",
          "It works; TypeScript widens count to any",
          "It works, but only outside strict mode",
          "A runtime TypeError"], 0,
         "Inference from the initializer is binding. `count` is `number` from that point on, so assigning a string is rejected at compile time.")]),

    _w(2, "Month 1 · Language foundations",
       "Operators & Control Flow",
       "Branch correctly, and know exactly which values are falsy.",
       ["ts_operators", "ts_equality", "ts_conditionals"],
       [("even-or-odd", "The simplest possible branch."),
        ("larger-of-two", "Comparison plus a conditional expression."),
        ("max-of-three", "Chained comparisons without a sort."),
        ("leap-year", "A rule with nested exceptions — get the && / || precedence right."),
        ("is-multiple", "Remainder as a predicate.")],
       "Write a `grade.ts` that reads a score and prints a letter grade, then a second version using a lookup table instead of an if-chain. Compare which one you would rather extend.",
       [("Why should you always use `===` instead of `==`?",
         ["`==` coerces its operands, so \"1\" == 1 is true and the rules are hard to predict",
          "`===` is faster",
          "`==` is deprecated and errors under strict",
          "`===` also compares object identity, which `==` cannot"], 0,
         "Loose equality applies a conversion table almost nobody has memorised. Strict equality compares type and value with no surprises."),
        ("Which of these is truthy?",
         ["\"0\"", "0", "\"\"", "NaN"], 0,
         "Any non-empty string is truthy, including \"0\" and \"false\". The falsy values are false, 0, -0, 0n, \"\", null, undefined and NaN."),
        ("What does `a ?? b` do that `a || b` does not?",
         ["It falls back only for null/undefined, so 0 and \"\" pass through",
          "It short-circuits, which || does not",
          "It works on objects only",
          "It throws when a is null"], 0,
         "`||` falls back on every falsy value, which silently replaces legitimate zeros and empty strings. `??` triggers only on nullish values."),
        ("`obj?.prop` where `obj` is undefined evaluates to…",
         ["undefined", "null", "a TypeError", "false"], 0,
         "Optional chaining short-circuits the whole access and produces `undefined` rather than throwing.")]),

    _w(3, "Month 1 · Language foundations",
       "Loops & Numbers",
       "Iterate deliberately, and know where floating-point arithmetic bites.",
       ["ts_loops", "ts_number_math", "ts_number_format"],
       [("countdown", "Build output in a loop rather than a string concat chain."),
        ("sum-to-n", "Accumulate a running total."),
        ("count-digits", "Peel digits with / and %."),
        ("factorial", "Watch the growth — when does a number stop being exact?"),
        ("is-prime", "Stop the loop at the square root, not at n.")],
       "Write a `stats.ts` that reads a line of numbers and prints their count, sum, mean and range — one pass, no array methods.",
       [("What is the difference between `for...of` and `for...in` over an array?",
         ["for...of yields the values; for...in yields the string keys",
          "They are the same for arrays",
          "for...in yields values, for...of yields indices",
          "for...in does not work on arrays"], 0,
         "`for...in` enumerates keys as strings — including inherited ones — which is almost never what you want for an array."),
        ("Why is `0.1 + 0.2 === 0.3` false?",
         ["number is a 64-bit float, and 0.1 and 0.2 have no exact binary representation",
          "TypeScript rounds differently from JavaScript",
          "=== compares references for numbers",
          "It is true under strict mode"], 0,
         "Binary floating point cannot represent these decimals exactly. Compare with a tolerance, or work in integers (cents rather than dollars)."),
        ("What does `Math.trunc(-4.7)` return?",
         ["-4", "-5", "4", "-4.7"], 0,
         "`trunc` drops the fractional part toward zero. `Math.floor(-4.7)` is -5, which is the usual source of confusion."),
        ("What is the largest exactly-representable integer?",
         ["Number.MAX_SAFE_INTEGER, about 9.007e15",
          "Number.MAX_VALUE",
          "2^64 - 1",
          "There is no limit; number is arbitrary precision"], 0,
         "Past 2^53 - 1 consecutive integers stop being distinguishable. `bigint` exists for values beyond that.")]),

    _w(4, "Month 1 · Language foundations",
       "Text & String Methods",
       "Manipulate strings fluently and remember that they are immutable.",
       ["ts_strings", "ts_string_methods", "ts_regex", "ts_unicode"],
       [("reverse-string", "Split, reverse, join — or an index loop."),
        ("count-vowels", "Scan characters with a membership test."),
        ("is-palindrome-fn", "Two pointers over a string."),
        ("count-words", "Split on whitespace and mind the empty pieces."),
        ("caesar-cipher", "Character codes and modular wrap-around.")],
       "Write a `slug.ts` that turns a title into a URL slug: lowercase, non-alphanumerics to hyphens, collapse runs, trim the ends.",
       [("What does `s.replace(\"a\", \"b\")` do when `s` contains several `a`s?",
         ["Replaces only the first one",
          "Replaces all of them",
          "Throws unless a regex is used",
          "Replaces the last one"], 0,
         "A string pattern replaces one occurrence. Use `replaceAll`, or a regex with the `g` flag, for every match."),
        ("What does `\"abcdef\".slice(-2)` return?",
         ["\"ef\"", "\"ab\"", "\"\"", "\"abcd\""], 0,
         "A negative index counts back from the end. `substring` does not support this and clamps negatives to 0."),
        ("Why does `s[0] = \"X\"` not change the string?",
         ["Strings are immutable; every operation returns a new string",
          "Index assignment needs the charAt setter",
          "It only fails under strict mode",
          "It does change it, but the change is not visible until reassignment"], 0,
         "There is no in-place mutation for strings. Building a result means concatenating or joining an array."),
        ("`\"  hi  \".trim().length` is…",
         ["2", "6", "4", "0"], 0,
         "`trim` removes leading and trailing whitespace, leaving the two characters of \"hi\".")]),
])


TS_EXAMS.update({
    1: _ts_exam(
        "Temperature table",
        "The input is a line of Celsius temperatures. For each one print `C=F` where F is `C * 9 / 5 + 32`, one per line, then print the count on the last line.",
        '''
const temps = input.split(/\\s+/).map(Number);
for (const c of temps) {
  const f = c * 9 / 5 + 32;
  console.log(c + "=" + f);
}
console.log(temps.length);
''',
        [("0 100", "0=32\n100=212\n2"), ("-40", "-40=-40\n1"),
         ("10 20 30", "10=50\n20=68\n30=86\n3"), ("37", "37=98.6\n1")],
        hint="Declare each converted value with const inside the loop; TypeScript infers number throughout."),

    2: _ts_exam(
        "Ticket price",
        "The input is `age isMember` (the second is `yes` or `no`). Base price is 20. Under 13 pays half; 65 and over pays 15; members get 5 off after that, but the price never drops below 0. Print the price, then `member` or `guest`.",
        '''
const [ageRaw, memberRaw] = input.split(/\\s+/);
const age = Number(ageRaw);
const isMember = memberRaw === "yes";
let price = 20;
if (age < 13) price = 10;
else if (age >= 65) price = 15;
if (isMember) price = Math.max(0, price - 5);
console.log(price);
console.log(isMember ? "member" : "guest");
''',
        [("30 no", "20\nguest"), ("10 yes", "5\nmember"),
         ("70 yes", "10\nmember"), ("65 no", "15\nguest"), ("12 no", "10\nguest")],
        hint="Resolve the age band first with if/else if, then apply the member discount to whatever that produced."),

    3: _ts_exam(
        "Number report",
        "The input is one integer `n` (at least 1). Print four lines: the sum 1..n, the count of divisors of n, whether n is prime, and the number of digits in n.",
        '''
const n = Number(input);
let sum = 0;
for (let i = 1; i <= n; i++) sum += i;
let divisors = 0;
for (let d = 1; d <= n; d++) {
  if (n % d === 0) divisors++;
}
const isPrime = n >= 2 && divisors === 2;
let digits = 0;
let rest = n;
while (rest > 0) {
  digits++;
  rest = Math.trunc(rest / 10);
}
console.log(sum);
console.log(divisors);
console.log(isPrime);
console.log(digits);
''',
        [("7", "28\n2\ntrue\n1"), ("1", "1\n1\nfalse\n1"),
         ("12", "78\n6\nfalse\n2"), ("97", "4753\n2\ntrue\n2")],
        hint="A number is prime exactly when it has two divisors. Use Math.trunc when peeling digits so negatives and floats cannot creep in."),

    4: _ts_exam(
        "Title case and initials",
        "The input is a line of lowercase words. Print the line in Title Case, then the initials joined and uppercased, then the length of the longest word.",
        '''
const words = input.split(/\\s+/);
const titled = words.map((w) => w[0].toUpperCase() + w.slice(1)).join(" ");
const initials = words.map((w) => w[0].toUpperCase()).join("");
let longest = 0;
for (const w of words) {
  if (w.length > longest) longest = w.length;
}
console.log(titled);
console.log(initials);
console.log(longest);
''',
        [("grace hopper", "Grace Hopper\nGH\n6"),
         ("ada", "Ada\nA\n3"),
         ("the quick brown fox", "The Quick Brown Fox\nTQBF\n5"),
         ("a bb", "A Bb\nAB\n2")],
        hint="Strings are immutable, so build the capitalised word from w[0] plus w.slice(1)."),
})


TS_QUIZ_EXTRA.update({
    1: [
        ("What is the difference between `let x` and `const x` at block scope?",
         ["const cannot be rebound; both are scoped to the enclosing { }",
          "const is function-scoped, let is block-scoped",
          "const deeply freezes the value",
          "There is none in modern TypeScript"], 0,
         "`const` blocks reassignment of the NAME. A const object's contents are still mutable — that is `readonly`'s job, not const's."),
        ("`const x: any = \"hi\"; x.notAMethod();` — what does the compiler say?",
         ["Nothing; any disables checking for that value",
          "Property does not exist on type string",
          "Object is possibly undefined",
          "any is not assignable to string"], 0,
         "That silence is the whole problem with `any`, and the reason `unknown` is the right escape hatch when you genuinely do not know a type."),
    ],
    2: [
        ("`if (value)` where `value` is `0` — does the branch run?",
         ["No, 0 is falsy", "Yes, numbers are always truthy",
          "Only under strict mode", "It is a compile error"], 0,
         "0 is falsy, which is why truthiness checks silently swallow legitimate zeros. Compare explicitly when 0 is a valid value."),
        ("What does `switch` compare cases with?",
         ["Strict equality (===)", "Loose equality (==)",
          "Object.is", "A deep structural comparison"], 0,
         "`switch` uses strict equality, so `case \"1\"` never matches the number 1 — the same discipline as writing === everywhere else."),
    ],
    3: [
        ("Which loop gives you the index and works with `break`?",
         ["A classic for loop, or for...of with .entries()",
          "forEach", "map", "reduce"], 0,
         "`forEach` cannot be broken out of — `return` only skips one callback. Reach for `for...of` when you need early exit."),
        ("`Math.round(-2.5)` returns…",
         ["-2", "-3", "-2.5", "2"], 0,
         "`Math.round` breaks ties toward positive infinity, so -2.5 rounds to -2. Use Math.floor or trunc when you need a predictable direction."),
    ],
    4: [
        ("What does `\"a,b,,c\".split(\",\")` produce?",
         ["4 items, one of them an empty string",
          "3 items, empties dropped",
          "4 items, the empty replaced with undefined",
          "A runtime error"], 0,
         "`split` keeps empty pieces. Filter them out yourself when consecutive separators are possible — a classic source of off-by-one word counts."),
        ("How do you compare two strings for sort order?",
         ["a.localeCompare(b), which returns a negative/zero/positive number",
          "a.compareTo(b)",
          "a - b",
          "a.equals(b)"], 0,
         "`localeCompare` is the comparator-shaped API. Subtraction on strings gives NaN, and there is no compareTo or equals in JavaScript."),
    ],
})


TS_EXAM_MORE_TESTS.update({
    1: [
        ('0', '0=32\n1'),
        ('-10 -20', '-10=14\n-20=-4\n2'),
        ('1000', '1000=1832\n1'),
        ('5 15 25 35', '5=41\n15=59\n25=77\n35=95\n4'),
    ],
    2: [
        ('13 no', '20\nguest'),
        ('64 yes', '15\nmember'),
        ('0 yes', '5\nmember'),
        ('100 no', '15\nguest'),
    ],
    3: [
        ('2', '3\n2\ntrue\n1'),
        ('10', '55\n4\nfalse\n2'),
        ('36', '666\n9\nfalse\n2'),
        ('1000', '500500\n16\nfalse\n4'),
    ],
    4: [
        ('x', 'X\nX\n1'),
        ('hello world again', 'Hello World Again\nHWA\n5'),
        ('zebra apple', 'Zebra Apple\nZA\n5'),
        ('i am here now', 'I Am Here Now\nIAHN\n4'),
    ],
})
