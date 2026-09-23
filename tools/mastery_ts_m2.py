# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — Month 2: Functions & data (weeks 5-8).
#
# The month's week tables, coding finals, authored bank questions and the
# extra final tests. exec()'d in order by mastery_defs.py, which defines
# `_w`, `_ts_exam` and the four collections this file extends.
# ---------------------------------------------------------------------------

TS_WEEKS.extend([
    # =======================================================================
    # MONTH 2 — Functions & data
    # =======================================================================
    _w(5, "Month 2 · Functions & data",
       "Functions & Parameters",
       "Write functions with precise signatures — optional, default and rest parameters.",
       ["ts_functions", "ts_params", "ts_overloads", "ts_closures_scope"],
       [("square-number", "A pure function with one parameter."),
        ("absolute-value", "Branch inside a function and return early."),
        ("min-of-two", "Two parameters, one comparison."),
        ("fizzbuzz-value", "A function returning a union of possibilities.")],
       "Write a `format.ts` exporting `formatMoney(cents, options?)` where options may set a currency symbol and whether to show decimals — defaults for both.",
       [("Where must an optional parameter appear?",
         ["After every required parameter",
          "Anywhere in the list",
          "First, so callers can omit the rest",
          "Only as the sole parameter"], 0,
         "Positional arguments are matched left to right, so a required parameter can never follow an optional one."),
        ("What is the type of `x` in `function f(x = 5)`?",
         ["number, inferred from the default",
          "any",
          "number | undefined",
          "unknown until annotated"], 0,
         "The default supplies the inferred type, and the parameter is optional from the caller's side but never undefined inside the body."),
        ("How is a rest parameter typed?",
         ["As an array: (...items: number[])",
          "As a tuple of unknown length",
          "As any[], always",
          "Rest parameters cannot be typed"], 0,
         "`...items: number[]` collects the remaining arguments into a real array, which must be the last parameter."),
        ("What does a function declared to return `void` promise?",
         ["That callers should ignore whatever it returns",
          "That it returns undefined and nothing else",
          "That it never returns",
          "That it throws"], 0,
         "`void` means the return value is not meaningful — which is why a `() => void` slot accepts a function that happens to return something. `never` is the type for functions that do not return at all.")]),

    _w(6, "Month 2 · Functions & data",
       "Higher-Order Functions",
       "Pass and return functions, and read the types that describe them.",
       ["ts_higher_order", "ts_recursion"],
       [("count-above-average", "Two passes, or one reduce and one filter."),
        ("sort-by-frequency", "A comparator with a tie-break."),
        ("count-occurrences", "A predicate handed to a counting helper.")],
       "Write a `pipeline.ts` with a `pipe` helper, then use it to build a text-cleaning pipeline from four small transforms.",
       [("What is the type of `const add = (a: number) => (b: number) => a + b`?",
         ["(a: number) => (b: number) => number",
          "(a: number, b: number) => number",
          "number",
          "(a: number) => number"], 0,
         "`add(1)` returns another function, so the return type is itself a function type. Only `add(1)(2)` gives a number."),
        ("Why does `[\"a\"].map((s) => s.length)` type-check when map passes three arguments?",
         ["A function may declare fewer parameters than the signature offers",
          "map special-cases one-parameter callbacks",
          "The extra arguments become undefined",
          "TypeScript infers the missing parameters as any"], 0,
         "Assignability allows fewer parameters, never more — the callback simply ignores arguments it did not declare."),
        ("What does a closure capture?",
         ["The variable itself, so later changes to it are visible",
          "A snapshot of the value at creation time",
          "Only const bindings",
          "Nothing; parameters must be passed explicitly"], 0,
         "Closures capture bindings, not values. This is why a `var` in a loop famously yields the final value while a `let` gives one binding per iteration."),
        ("Why are arrow functions the default for callbacks?",
         ["They inherit `this` from the enclosing scope instead of rebinding it",
          "They are faster",
          "They cannot be passed to higher-order functions otherwise",
          "They allow default parameters, which function expressions do not"], 0,
         "A non-arrow callback gets its own `this`, which is almost never the object you meant — the classic source of `undefined is not a function` inside a method.")]),

    _w(7, "Month 2 · Functions & data",
       "Arrays & Array Methods",
       "Use the array toolkit fluently and know which methods mutate.",
       ["ts_arrays", "ts_array_methods", "ts_tuples", "ts_array_modern"],
       [("array-sum", "reduce, or a plain loop."),
        ("array-maximum", "Math.max with a spread, or a scan."),
        ("second-largest", "One pass tracking two values."),
        ("move-zeroes", "In-place, stable — mind the mutation."),
        ("running-sum", "A prefix scan.")],
       "Write a `table.ts` that reads CSV-ish lines and prints a summary: row count, per-column sums for numeric columns, and the widest value in each column.",
       [("Which of these MUTATES the array it is called on?",
         ["sort", "map", "filter", "slice"], 0,
         "`sort` and `reverse` sort in place and return the same array — copy first with `[...arr].sort()` when the original matters."),
        ("What is the difference between `slice` and `splice`?",
         ["slice copies a range; splice removes or inserts in place",
          "They are aliases",
          "slice mutates, splice copies",
          "splice only works on strings"], 0,
         "`slice` is non-destructive and returns a new array. `splice` edits the original and returns what it removed."),
        ("What does `[1, 2, 3].reduce((a, b) => a + b)` return without an initial value?",
         ["6, using the first element as the seed",
          "6, using 0 as the seed",
          "undefined",
          "A TypeError"], 0,
         "Without a seed the first element is used and iteration starts at index 1 — which throws on an EMPTY array, the reason to pass an explicit initial value."),
        ("What is a tuple type `[string, number]`?",
         ["A fixed-length array with a type per position",
          "A union of string and number",
          "An object with two keys",
          "An array that can hold either type in any position"], 0,
         "Tuples fix both the length and the type at each index, which is what makes destructuring them type-safe.")]),

    _w(8, "Month 2 · Functions & data",
       "Destructuring, Objects & JSON",
       "Pull data apart cleanly, and cross the untyped JSON boundary safely.",
       ["ts_destructuring", "ts_objects", "ts_json", "ts_interfaces_types", "ts_index_signatures"],
       [("count-equal-pairs", "Objects as counters."),
        ("first-unique-char", "A frequency object, then a second pass."),
        ("run-length-encode", "Build structured output from a scan.")],
       "Write a `config.ts` that reads a JSON object from stdin, destructures the fields it needs with defaults, and prints a normalised summary.",
       [("What type does `JSON.parse(text)` return?",
         ["any — it is an unchecked boundary you should narrow immediately",
          "unknown",
          "object",
          "Record<string, unknown>"], 0,
         "`JSON.parse` is typed `any`, which quietly disables checking downstream. Assign it to `unknown` and validate with a type guard."),
        ("What does `const { a = 1 } = obj` do when `obj.a` is `null`?",
         ["Leaves a as null — defaults apply only to undefined",
          "Sets a to 1",
          "Throws",
          "Sets a to undefined"], 0,
         "Destructuring defaults trigger on `undefined` only, exactly like parameter defaults. `null` is a real value and passes through."),
        ("What does the spread `{ ...a, ...b }` do on conflicting keys?",
         ["b wins, because later spreads overwrite earlier ones",
          "a wins",
          "The values are merged recursively",
          "It is a compile error"], 0,
         "Spread is a shallow, left-to-right copy. Nested objects are shared by reference, not cloned."),
        ("How do you rename while destructuring?",
         ["const { a: renamed } = obj",
          "const { a as renamed } = obj",
          "const { renamed = a } = obj",
          "You cannot; assign afterwards"], 0,
         "The colon form binds the property `a` to a new local name. The `as` spelling is for imports, not destructuring.")]),
])


TS_EXAMS.update({
    5: _ts_exam(
        "Formatter with options",
        "The input is `value width pad` where `pad` may be the word `none`. Write `format(value, width?, pad?)` with `width` defaulting to 8 and `pad` to `.`, returning the value right-aligned to that width. Print `format` applied to the input, then `format(value)` using both defaults.",
        '''
const [value, widthRaw, padRaw] = input.split(/\\s+/);
function format(value: string, width = 8, pad = "."): string {
  if (value.length >= width) return value;
  return pad.repeat(width - value.length) + value;
}
const width = Number(widthRaw);
const pad = padRaw === "none" ? undefined : padRaw;
console.log(format(value, width, pad));
console.log(format(value));
''',
        [("ab 5 -", "---ab\n......ab"), ("hello 3 x", "hello\n...hello"),
         ("z 4 none", "...z\n.......z"), ("abc 6 *", "***abc\n.....abc")],
        hint="Passing `undefined` for an optional parameter uses its default — which is exactly why `none` maps to undefined rather than an empty string."),

    6: _ts_exam(
        "Compose a text pipeline",
        "The input is a line of words. Build a `pipe` helper that composes `(s: string) => string` transforms left to right, then apply: trim, collapse runs of spaces to one, uppercase. Print the result, then the number of words in it.",
        '''
function pipe(...fns: Array<(s: string) => string>): (start: string) => string {
  return (start) => fns.reduce((acc, f) => f(acc), start);
}
const clean = pipe(
  (s) => s.trim(),
  (s) => s.replace(/\\s+/g, " "),
  (s) => s.toUpperCase(),
);
const result = clean(input);
console.log(result);
console.log(result.split(" ").length);
''',
        [("hello   world", "HELLO WORLD\n2"), ("a", "A\n1"),
         ("one  two   three", "ONE TWO THREE\n3"), ("mixed Case", "MIXED CASE\n2")],
        hint="pipe returns a function; reduce threads the value through each transform in order."),

    7: _ts_exam(
        "Array statistics",
        "The input is a line of numbers. Print, one per line: the sum, the maximum, the count of values above the mean, and the numbers sorted descending joined by spaces — without mutating the original order for the earlier answers.",
        '''
const nums = input.split(/\\s+/).map(Number);
const sum = nums.reduce((a, b) => a + b, 0);
const max = Math.max(...nums);
const mean = sum / nums.length;
const above = nums.filter((n) => n > mean).length;
const sorted = [...nums].sort((a, b) => b - a);
console.log(sum);
console.log(max);
console.log(above);
console.log(sorted.join(" "));
''',
        [("1 2 3 4", "10\n4\n2\n4 3 2 1"), ("5", "5\n5\n0\n5"),
         ("3 3 3", "9\n3\n0\n3 3 3"), ("-1 4 2", "5\n4\n2\n4 2 -1")],
        hint="sort mutates — copy with [...nums] first, and pass a numeric comparator or you get lexicographic order."),

    8: _ts_exam(
        "Merge JSON records",
        "The input is `n` then `n` lines of JSON objects with a `name` and optional `tags` array. Merge them into one record per name (later `tags` append, duplicates dropped) and print `name: tag1,tag2` per name in alphabetical order, tags sorted.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const byName = new Map<string, Set<string>>();
for (let i = 1; i <= n; i++) {
  const { name, tags = [] } = JSON.parse(lines[i]) as { name: string; tags?: string[] };
  const bucket = byName.get(name) ?? new Set<string>();
  for (const tag of tags) bucket.add(tag);
  byName.set(name, bucket);
}
for (const name of [...byName.keys()].sort()) {
  console.log(name + ": " + [...byName.get(name)!].sort().join(","));
}
''',
        [('3\n{"name":"ada","tags":["x"]}\n{"name":"bob"}\n{"name":"ada","tags":["y","x"]}',
          "ada: x,y\nbob: "),
         ('1\n{"name":"solo","tags":["a","a"]}', "solo: a"),
         ('2\n{"name":"z","tags":["q"]}\n{"name":"a","tags":["p"]}', "a: p\nz: q")],
        hint="Destructure with a default for the optional tags, and use a Set per name so duplicates collapse."),
})


TS_QUIZ_EXTRA.update({
    5: [
        ("What does the `?` in `function f(x?: number)` mean for the body?",
         ["x has type number | undefined and must be narrowed before use",
          "x defaults to 0",
          "x is always present at runtime",
          "x can be passed in any position"], 0,
         "Optional means possibly-undefined inside the function. A default value is what removes the undefined; `?` alone does not."),
        ("Why can a `() => void` slot accept `() => number`?",
         ["void means the return value is not meaningful, so returning something is allowed",
          "number is assignable to void",
          "The compiler inserts a discard",
          "It cannot — that is an error"], 0,
         "This asymmetry is deliberate: it lets `arr.forEach(x => arr2.push(x))` type-check even though push returns a number."),
    ],
    7: [
        ("What does `[10, 9, 1].sort()` return without a comparator?",
         ["[1, 10, 9] — elements are compared as strings",
          "[1, 9, 10]",
          "[10, 9, 1]",
          "A type error"], 0,
         "The default sort converts to strings, so \"10\" sorts before \"9\". Numeric sorts always need `(a, b) => a - b`."),
        ("What is the difference between `find` and `filter`?",
         ["find returns the first match or undefined; filter returns an array of all matches",
          "find returns an index",
          "filter stops at the first match",
          "They are aliases"], 0,
         "`find` gives `T | undefined`, so its result needs a check before use — the type is telling you the search can fail."),
    ],
    8: [
        ("What does `const { a, ...rest } = obj` put in `rest`?",
         ["A new object with every own property except a",
          "An array of the remaining values",
          "A reference to obj",
          "Only the properties declared after a"], 0,
         "Rest in a destructuring pattern builds a fresh shallow object. Nested values are still shared by reference."),
        ("`JSON.stringify({ a: undefined, b: 1 })` produces…",
         ["{\"b\":1} — undefined properties are dropped",
          "{\"a\":null,\"b\":1}",
          "{\"a\":undefined,\"b\":1}",
          "A TypeError"], 0,
         "undefined, functions and symbols are omitted from objects (and become null inside arrays) — a routine source of fields vanishing over the wire."),
    ],
})


TS_EXAM_MORE_TESTS.update({
    5: [
        ('abcdefgh 8 -', 'abcdefgh\nabcdefgh'),
        ('a 1 none', 'a\n.......a'),
        ('toolongvalue 20 #', '########toolongvalue\ntoolongvalue'),
        ('q 2 0', '0q\n.......q'),
    ],
    6: [
        ('x  y', 'X Y\n2'),
        ('a b c d e', 'A B C D E\n5'),
        ('UPPER lower', 'UPPER LOWER\n2'),
        ('one', 'ONE\n1'),
    ],
    7: [
        ('10 -10', '0\n10\n1\n10 -10'),
        ('0 0 0 1', '1\n1\n1\n1 0 0 0'),
        ('5 1 4 2 3', '15\n5\n2\n5 4 3 2 1'),
        ('-5 -1 -3', '-9\n-1\n1\n-1 -3 -5'),
    ],
    8: [
        ('2\n{"name":"a"}\n{"name":"a"}', 'a:'),
        ('3\n{"name":"m","tags":["b","a"]}\n{"name":"k","tags":[]}\n{"name":"m","tags":["c"]}', 'k:\nm: a,b,c'),
        ('1\n{"name":"only"}', 'only:'),
        ('4\n{"name":"b","tags":["z"]}\n{"name":"a","tags":["y"]}\n{"name":"c"}\n{"name":"a","tags":["x","y"]}', 'a: x,y\nb: z\nc:'),
        ('2\n{"name":"dup","tags":["t","t","s"]}\n{"name":"dup","tags":["s"]}', 'dup: s,t'),
    ],
})
