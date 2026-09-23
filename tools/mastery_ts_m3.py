# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — Month 3: The type system (weeks 9-13).
#
# The month's week tables, coding finals, authored bank questions and the
# extra final tests. exec()'d in order by mastery_defs.py, which defines
# `_w`, `_ts_exam` and the four collections this file extends.
# ---------------------------------------------------------------------------

TS_WEEKS.extend([
    # =======================================================================
    # MONTH 3 — The type system
    # =======================================================================
    _w(9, "Month 3 · The type system",
       "Maps, Sets & Hashing",
       "Reach for the right keyed collection, and use it to turn O(n²) into O(n).",
       ["ts_maps_sets"],
       [("contains-duplicate", "A Set, in one pass."),
        ("two-sum-indices", "Complement lookup in a Map."),
        ("majority-element", "Counting with a Map."),
        ("group-anagrams-count", "A canonical key per group."),
        ("longest-consecutive", "A Set turns a sort into a linear scan.")],
       "Write an `index.ts` that reads lines of `word document` and builds an inverted index, then answers lookup queries from stdin.",
       [("When should you use a `Map` rather than a plain object?",
         ["When keys are not strings, insertion order matters, or you add and remove often",
          "Always — objects are deprecated as dictionaries",
          "Only when the keys are numbers",
          "When you need JSON serialization"], 0,
         "Objects coerce keys to strings and carry a prototype. `Map` takes any key type, preserves insertion order and has a real `size`."),
        ("What does `set.add(x)` return when `x` is already present?",
         ["The set itself — but `has` is how you test membership",
          "false",
          "undefined",
          "The existing value"], 0,
         "`Set.add` returns the set for chaining. It is `Map.set` and `Set.add` returning the collection that makes the 'test and insert' idiom need a separate `has`."),
        ("Two distinct objects with identical contents used as Map keys…",
         ["Are two different keys, because Map compares by reference",
          "Collide into one key",
          "Throw a TypeError",
          "Are compared structurally like TypeScript types"], 0,
         "`Map` uses SameValueZero, which is reference identity for objects. Key by a primitive derived from the object when you want value semantics."),
        ("How do you iterate a Map's key/value pairs?",
         ["for (const [k, v] of map)",
          "for (const k in map)",
          "map.forEach((k, v) => ...)",
          "for (const { k, v } of map)"], 0,
         "A Map is iterable over `[key, value]` entries. `for...in` sees nothing, and `forEach` passes value FIRST, which trips people up.")]),

    _w(10, "Month 3 · The type system",
        "Unions, Aliases & Literal Types",
        "Model 'one of a fixed set' precisely instead of reaching for `string`.",
        ["ts_unions", "ts_aliases", "ts_enums"],
        [("traffic-light", "A state that must be one of three values."),
         ("rock-paper-scissors", "A union in, a union out."),
         ("seconds-to-clock", "Formatting driven by a small fixed vocabulary.")],
        "Write a `state.ts` modelling a download as `\"idle\" | \"loading\" | \"done\" | \"failed\"`, with a transition function that rejects illegal moves.",
        [("What does `type Status = \"on\" | \"off\"` buy you over `string`?",
          ["Only the two literals are assignable, and editors can complete them",
           "It is stored more compactly at runtime",
           "It generates runtime validation",
           "Nothing; it is documentation"], 0,
          "A literal union makes the illegal values unrepresentable at compile time. It has no runtime existence at all."),
         ("Which is true of `type` versus `interface`?",
          ["Interfaces merge across declarations; type aliases can express unions",
           "They are completely interchangeable",
           "Only interfaces can describe objects",
           "Only type aliases can be extended"], 0,
          "Both describe object shapes and both can be extended. Declaration merging is interface-only; unions, tuples and mapped types need a `type`."),
         ("What does `as const` do to `const dirs = [\"up\", \"down\"]`?",
          ["Makes it a readonly tuple of literal types instead of string[]",
           "Freezes it at runtime",
           "Converts it to an enum",
           "Makes the variable non-reassignable, which const already did"], 0,
          "`as const` stops the widening from `\"up\"` to `string`, which is what lets `(typeof dirs)[number]` produce a useful union."),
         ("Why does this track avoid `enum`?",
          ["A literal union plus `as const` gives the same safety with no runtime object",
           "enum is deprecated",
           "enum cannot be used with switch",
           "enum values cannot be compared"], 0,
          "`enum` emits a real runtime object and has surprising numeric-enum behaviour. A string-literal union is erased entirely and narrows better.")]),

    # D-2: `ts_nullish` moved here from week 14 — handling null and undefined
    # IS narrowing, and it belongs beside the other guards.
    _w(11, "Month 3 · The type system",
        "Narrowing, Type Guards & Nullish",
        "Prove to the compiler what a value is — with built-in narrowing, `?.` and `??`, and your own predicates.",
        ["ts_narrowing", "ts_type_predicates", "ts_nullish"],
        [("password-strength", "Several independent checks combined."),
         ("valid-anagram", "Validate, then compare canonical forms."),
         ("mountain-array", "A shape check expressed as a sequence of guards.")],
        "Write a `validate.ts` that reads JSON lines and keeps only those matching a `Person` shape, using a type predicate you wrote yourself.",
        [("What narrows `x: string | number` inside `if (typeof x === \"string\")`?",
          ["typeof narrowing, which the compiler understands natively",
           "A type assertion",
           "Nothing; you must cast",
           "The strictNullChecks flag"], 0,
          "`typeof`, `instanceof`, `in`, equality against literals and truthiness checks are all built-in narrowing forms."),
         ("Why does `function isPerson(x: unknown): boolean` fail to narrow?",
          ["Only an `x is Person` return type carries narrowing information",
           "boolean is not allowed as a return type",
           "The parameter must be typed any",
           "It does narrow, but only inside the function"], 0,
          "A plain boolean tells the compiler nothing about the relationship between the result and the argument. The predicate form is what creates it."),
         ("`function isPerson(x: unknown): x is Person { return true; }` — the compiler…",
          ["Accepts it; predicates are unchecked promises",
           "Rejects it as an unsound predicate",
           "Warns under strict",
           "Narrows to unknown as a fallback"], 0,
          "The body is never verified against the claim, which is exactly why a predicate should check every field it asserts."),
         ("What does `asserts x is string` do?",
          ["Narrows for the rest of the scope by throwing when the check fails",
           "Returns a boolean you branch on",
           "Adds a runtime type tag",
           "Is a synonym for `x is string`"], 0,
          "An assertion function makes a demand rather than asking a question — control continues past it only when the value really is that type."),
         ("What is the difference between `a?.b` and `a!.b`?",
          ["?. short-circuits to undefined; !. asserts a is non-null and checks nothing",
           "They are equivalent",
           "!. throws a helpful error when a is null",
           "?. only works on methods"], 0,
          "The non-null assertion is a promise, not a check. If it is wrong you get a plain runtime TypeError with no extra context.")]),

    _w(12, "Month 3 · The type system",
        "Discriminated Unions",
        "Model variants with a shared tag, and let the compiler prove you handled all of them.",
        ["ts_discriminated_unions"],
        [("valid-parentheses", "A tagged decision per character."),
         ("min-stack", "Commands as variants."),
         ("browser-history", "A small state machine.")],
        "Write an `interpreter.ts` for a tiny stack language (`push n`, `add`, `dup`, `print`) modelled as a discriminated union, with a `never` exhaustiveness check.",
        [("Why must the discriminant be a literal type?",
          ["Only distinct literals let narrowing rule out the other union members",
           "String discriminants are slower",
           "TypeScript forbids string properties in unions",
           "It is required for JSON serialization"], 0,
          "Narrowing works by elimination. With `kind: string` both members still match, so nothing is excluded."),
         ("You add a new variant. What does `const exhaustive: never = value` in the default branch do?",
          ["Errors in every switch that has not handled the new variant",
           "Silently accepts it",
           "Throws at runtime",
           "Narrows the new variant to never"], 0,
          "That is the whole point: the compiler walks you to every place that now needs a case, instead of failing silently in production."),
         ("What is the advantage over one object with all fields optional?",
          ["Each branch guarantees which fields exist, removing runtime undefined checks",
           "Lower memory use",
           "It serializes better",
           "It allows more required fields"], 0,
          "All-optional fields make every impossible combination representable and every access a guard. The tag makes the illegal states unrepresentable."),
         ("Does `if (s.kind === \"circle\")` narrow as well as `switch`?",
          ["Yes — equality against a literal is a narrowing form",
           "No, only switch narrows",
           "Only with a type predicate",
           "Only inside a function"], 0,
          "Both narrow identically. An `else if` chain still wants a final `never` check to stay exhaustive.")]),

    # D-2: week 13 used to schedule no chapters at all. It now teaches the two
    # things months 4-5 lean on — function types in depth, and how a type is
    # tested — and keeps the Months 1-3 checkpoint and review problems.
    _w(13, "Month 3 · The type system",
        "Function Types, Type Tests & Checkpoint",
        "Read any function signature, test a type like you test a value — and prove the first three months stuck.",
        ["ts_function_types", "ts_type_testing"],
        [("longest-unique-substring", "Sliding window over a string — Weeks 4, 7, 9."),
         ("group-anagrams-count", "Review — canonical keys and a Map, first met in Week 9."),
         ("merge-two-sorted-lists", "Careful pointer work and narrowing — Weeks 11, 12."),
         ("subarray-sum-k", "Prefix sums in a Map — Weeks 7, 9."),
         ("valid-anagram", "Review — a fast recap of the string toolkit, first met in Week 11.")],
        "Re-implement your Week 8 config reader from scratch without looking at it, then add type tests for it: `Expect<Equal<…>>` lines pinning its parsed type, and a `@ts-expect-error` line for a key it must reject.",
        [("`const nums = [3, 1, 2]; const sorted = nums.sort();` — what is `nums` afterwards?",
          ["[1, 2, 3] — sort mutates, and sorted is the same array",
           "[3, 1, 2] — sort returns a copy",
           "[1, 2, 3], but sorted is a separate array",
           "Unchanged until sorted is read"], 0,
          "`sort` is in place and returns the same reference. `[...nums].sort()` is the non-destructive form."),
         ("Which pair of values makes `a ?? b` and `a || b` disagree?",
          ["a = 0, b = 5", "a = null, b = 5", "a = undefined, b = 5", "a = \"x\", b = 5"], 0,
          "`0` is falsy but not nullish, so `||` returns 5 while `??` returns 0. This is the bug `??` was introduced to prevent."),
         ("You have `x: unknown` from JSON.parse. What is the safest next step?",
          ["Run it through a type predicate that checks every field you rely on",
           "Cast it with `as Person`",
           "Annotate the variable as Person",
           "Use `any` so the checks stop complaining"], 0,
          "A cast and an annotation both assert without checking. Only a predicate that actually inspects the data makes the type honest."),
         ("What single flag most changes what a type annotation means?",
          ["strictNullChecks", "noImplicitAny", "esModuleInterop", "skipLibCheck"], 0,
          "Without it, every type silently includes null and undefined, so no annotation can be trusted. It is the foundation the rest rests on."),
         ("Why prefer `@ts-expect-error` over `@ts-ignore`?",
          ["It errors once the problem is fixed, so the suppression cannot outlive its reason",
           "It suppresses fewer categories",
           "It is checked at runtime",
           "It works only in tests"], 0,
          "`@ts-ignore` hides whatever the next line does, forever. `@ts-expect-error` fails when there is nothing left to suppress.")]),
])


TS_EXAMS.update({
    9: _ts_exam(
        "Inverted index",
        "The input is `n` then `n` lines of `document word word ...`, then a final line of query words. For each query print `word: doc1 doc2` (documents in first-appearance order) or `word: -` if unseen.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const index = new Map<string, string[]>();
for (let i = 1; i <= n; i++) {
  const [doc, ...words] = lines[i].trim().split(/\\s+/);
  for (const word of words) {
    const docs = index.get(word) ?? [];
    if (!docs.includes(doc)) docs.push(doc);
    index.set(word, docs);
  }
}
for (const query of lines[n + 1].trim().split(/\\s+/)) {
  const docs = index.get(query);
  console.log(query + ": " + (docs === undefined ? "-" : docs.join(" ")));
}
''',
        [("2\nd1 cat dog\nd2 dog bird\ndog cat fish",
          "dog: d1 d2\ncat: d1\nfish: -"),
         ("1\na x\nx", "x: a"),
         ("2\nd1 k\nd2 k\nk", "k: d1 d2")],
        hint="A Map from word to a document list; guard against adding the same document twice."),

    10: _ts_exam(
        "Traffic light machine",
        "States are `red`, `green`, `amber` and cycle red → green → amber → red. The input is a start state then a number of ticks. Print the state after each tick, one per line.",
        '''
const [start, ticksRaw] = input.split(/\\s+/);
type Light = "red" | "green" | "amber";
const next: Record<Light, Light> = { red: "green", green: "amber", amber: "red" };
let state = start as Light;
const ticks = Number(ticksRaw);
for (let i = 0; i < ticks; i++) {
  state = next[state];
  console.log(state);
}
''',
        [("red 3", "green\namber\nred"), ("green 1", "amber"),
         ("amber 4", "red\ngreen\namber\nred"), ("red 0", "")],
        hint="A Record keyed by the literal union is both the transition table and the proof that every state has a successor."),

    11: _ts_exam(
        "Validate a batch of records",
        "The input is `n` then `n` JSON lines. A record is valid when it is an object with a string `id` of length 3+ and a number `score` between 0 and 100. Write a type predicate. Print `ok <id>` or `bad` per line, then the mean score of the valid ones rounded down (or `0` if none).",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
type Record_ = { id: string; score: number };
function isRecord(x: unknown): x is Record_ {
  if (typeof x !== "object" || x === null) return false;
  const o = x as { [k: string]: unknown };
  if (typeof o.id !== "string" || o.id.length < 3) return false;
  return typeof o.score === "number" && o.score >= 0 && o.score <= 100;
}
let total = 0;
let count = 0;
for (let i = 1; i <= n; i++) {
  const parsed: unknown = JSON.parse(lines[i]);
  if (isRecord(parsed)) {
    total += parsed.score;
    count++;
    console.log("ok " + parsed.id);
  } else {
    console.log("bad");
  }
}
console.log(count === 0 ? 0 : Math.floor(total / count));
''',
        [('3\n{"id":"abc","score":80}\n{"id":"xy","score":50}\n{"id":"def","score":90}',
          "ok abc\nbad\nok def\n85"),
         ('1\n{"id":"aaa","score":101}', "bad\n0"),
         ('2\n5\n{"id":"zzz","score":0}', "bad\nok zzz\n0")],
        hint="Reject non-objects and null first, then check every field the predicate claims — the compiler will not do it for you."),

    12: _ts_exam(
        "Stack language interpreter",
        "Commands are `push n`, `add`, `mul`, `dup`, `pop`. Model them as a discriminated union. The input is `n` then `n` commands. After all of them, print the stack bottom-to-top space-separated (or `(empty)`), then its size. `add`/`mul` pop two and push the result; `dup` copies the top.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
type Cmd =
  | { kind: "push"; value: number }
  | { kind: "add" }
  | { kind: "mul" }
  | { kind: "dup" }
  | { kind: "pop" };
function parse(line: string): Cmd {
  const [op, arg] = line.trim().split(/\\s+/);
  if (op === "push") return { kind: "push", value: Number(arg) };
  if (op === "add") return { kind: "add" };
  if (op === "mul") return { kind: "mul" };
  if (op === "dup") return { kind: "dup" };
  return { kind: "pop" };
}
const stack: number[] = [];
for (let i = 1; i <= n; i++) {
  const cmd = parse(lines[i]);
  switch (cmd.kind) {
    case "push":
      stack.push(cmd.value);
      break;
    case "add": {
      const b = stack.pop() ?? 0;
      const a = stack.pop() ?? 0;
      stack.push(a + b);
      break;
    }
    case "mul": {
      const b = stack.pop() ?? 0;
      const a = stack.pop() ?? 0;
      stack.push(a * b);
      break;
    }
    case "dup":
      stack.push(stack[stack.length - 1] ?? 0);
      break;
    case "pop":
      stack.pop();
      break;
    default: {
      const exhaustive: never = cmd;
      throw new Error(exhaustive);
    }
  }
}
console.log(stack.join(" ") || "(empty)");
console.log(stack.length);
''',
        [("4\npush 2\npush 3\nadd\ndup", "5 5\n2"),
         ("3\npush 4\npush 5\nmul", "20\n1"),
         ("2\npush 1\npop", "(empty)\n0"),
         ("5\npush 1\npush 2\npush 3\nadd\nadd", "6\n1")],
        hint="One case per tag, and a never assignment in the default so adding a sixth command becomes a compile error."),

    13: _ts_exam(
        "Checkpoint: word frequency report",
        "The input is a line of words. Print the three most frequent words as `word=count`, one per line, breaking ties alphabetically; then the number of distinct words. Fewer than three distinct words prints only what exists.",
        '''
const words = input.split(/\\s+/).filter((w) => w.length > 0);
const counts = new Map<string, number>();
for (const word of words) {
  counts.set(word, (counts.get(word) ?? 0) + 1);
}
const ranked = [...counts.entries()].sort((a, b) =>
  b[1] !== a[1] ? b[1] - a[1] : a[0].localeCompare(b[0]),
);
for (const [word, count] of ranked.slice(0, 3)) {
  console.log(word + "=" + count);
}
console.log(counts.size);
''',
        [("a b a c b a", "a=3\nb=2\nc=1\n3"),
         ("solo", "solo=1\n1"),
         ("x y", "x=1\ny=1\n2"),
         ("z z y y x", "y=2\nz=2\nx=1\n3")],
        hint="Count in a Map, then sort the entries by count descending with an alphabetical tie-break."),
})


TS_QUIZ_EXTRA.update({
    9: [
        ("What does `map.get(missingKey)` return?",
         ["undefined", "null", "It throws", "An empty entry"], 0,
         "Which is why `Map.get` is typed `V | undefined` and the result should be checked against undefined rather than tested for truthiness."),
        ("Why is a Set-based duplicate check O(n) rather than O(n²)?",
         ["Set membership is roughly constant time, so one pass suffices",
          "Sets are pre-sorted",
          "Sets deduplicate lazily",
          "It is not — Set lookup is linear"], 0,
         "Hashing turns 'have I seen this?' into a constant-time question, which is the whole reason hashing shows up in so many linear-time solutions."),
    ],
    10: [
        ("What is the type of `\"on\"` in `const s = \"on\"` versus `let s = \"on\"`?",
         ["\"on\" for const, string for let",
          "string for both",
          "\"on\" for both",
          "any for let"], 0,
         "A `let` binding can be reassigned, so its type widens. This widening is exactly what `as const` prevents on object and array literals."),
        ("Can a `type` alias be used before it is declared?",
         ["Yes — type declarations are hoisted for the checker",
          "No, they must be declared first",
          "Only interfaces can",
          "Only inside the same block"], 0,
         "Type declarations are not statements with runtime order, so ordering is free. Recursive and mutually-recursive types depend on this."),
    ],
    13: [
        ("`const a = [1,2]; const b = a; b.push(3);` — what is `a.length`?",
         ["3, because both names point at the same array",
          "2, because const copies the value",
          "2, because push returns a new array",
          "A compile error"], 0,
         "`const` fixes the binding, not the contents. Copying needs `[...a]` — the same distinction as `readonly` versus `const`."),
        ("Which is the safest way to handle a value of type `unknown`?",
         ["Narrow it with a check that inspects the data before use",
          "Cast it with `as`",
          "Annotate the variable with the expected type",
          "Assign it to an any-typed variable"], 0,
         "Casts and annotations both assert without verifying. Only a real runtime check makes the resulting type honest."),
    ],
})


TS_EXAM_MORE_TESTS.update({
    9: [
        ('1\nd1 a a a\na', 'a: d1'),
        ('3\nx one\ny two\nz one two\none two three', 'one: x z\ntwo: y z\nthree: -'),
        ('2\ndocA w\ndocB v\nv w', 'v: docB\nw: docA'),
        ('1\nd hello\nbye hello', 'bye: -\nhello: d'),
        ('2\nd2 k\nd1 k\nk', 'k: d2 d1'),
    ],
    10: [
        ('green 3', 'amber\nred\ngreen'),
        ('amber 1', 'red'),
        ('red 6', 'green\namber\nred\ngreen\namber\nred'),
        ('green 0', ''),
    ],
    11: [
        ('1\n{"id":"abcd","score":100}', 'ok abcd\n100'),
        ('2\n{"id":"abc","score":-1}\n{"id":"abc","score":"50"}', 'bad\nbad\n0'),
        ('2\nnull\n[1,2]', 'bad\nbad\n0'),
        ('3\n{"id":"aaa","score":1}\n{"id":"bbb","score":2}\n{"score":3}', 'ok aaa\nok bbb\nbad\n1'),
        ('1\n"text"', 'bad\n0'),
    ],
    12: [
        ('1\npop', '(empty)\n0'),
        ('3\npush 7\ndup\nmul', '49\n1'),
        ('2\npush -3\npush 4', '-3 4\n2'),
        ('6\npush 2\ndup\ndup\nmul\nmul\npush 1', '8 1\n2'),
    ],
    13: [
        ('b a', 'a=1\nb=1\n2'),
        ('the cat the dog the cat', 'the=3\ncat=2\ndog=1\n3'),
        ('q q q q', 'q=4\n1'),
        ('c b a c b a d', 'a=2\nb=2\nc=2\n4'),
    ],
})
