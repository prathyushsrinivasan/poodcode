# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# 6-Month Mastery programme — the curated, week-by-week track.
#
# The Learn tab is a reference library: 50 TypeScript chapters you can read in
# any order. This file turns that library into a *programme* — 26 weeks, each
# with a theme, a short list of concepts to study, curated Library problems to
# solve, a build project, and an end-of-week quiz that gates the next week.
#
# exec()'d inside gen_seed.py's namespace AFTER typescript_mastery.py, so every
# concept key referenced below already exists. gen_seed.py writes the result to
# src-tauri/seeds/mastery.json, which the `mastery` Tauri command serves.
#
# INVARIANTS the build asserts (see the checks at the bottom of this file):
#   * every `concepts` key resolves to a real concept in CONCEPTS
#   * every `problems` slug resolves to a real problem in the seed bank
#   * every concept in the track's language is scheduled exactly once, so the
#     programme genuinely covers the syllabus with nothing repeated or dropped
#   * every quiz question's `answer` indexes a real option
# ---------------------------------------------------------------------------


def _q(question, options, answer, explanation):
    return {
        "question": question,
        "options": list(options),
        "answer": answer,
        "explanation": explanation,
    }


def _w(week, phase, title, goal, concepts, problems, project, quiz):
    """One week of the programme. `problems` is a list of (slug, why) pairs.

    `exam`, `contest`, `quiz_from` and `quiz_sample` are attached afterwards by
    `_attach` so the week tables above stay readable."""
    return {
        "week": week,
        "phase": phase,
        "title": title,
        "goal": goal,
        "concepts": concepts,
        "problems": [{"slug": s, "note": n} for (s, n) in problems],
        "project": project,
        "quiz": [_q(*row) for row in quiz],
        # Filled in by _attach / _finalize_mastery.
        "quiz_from": [],
        "quiz_sample": 4,
        "exam": None,
        "contest": None,
    }


def _attach(weeks, exams, extra_quiz=None, quiz_from=None, contests=None, sample=4):
    """Bolt the coding finals, extra bank questions, cross-track quiz sources and
    checkpoint contests onto an already-authored week list."""
    extra_quiz = extra_quiz or {}
    quiz_from = quiz_from or {}
    contests = contests or {}
    for w in weeks:
        n = w["week"]
        w["quiz"].extend(_q(*row) for row in extra_quiz.get(n, []))
        w["quiz_from"] = list(quiz_from.get(n, []))
        w["quiz_sample"] = sample
        w["exam"] = exams.get(n)
        if n in contests:
            title, seconds = contests[n]
            w["contest"] = {"title": title, "duration_seconds": seconds}
    return weeks


def _finalize_mastery(tracks, concepts):
    """Expand each week's question BANK: the authored questions, plus the quiz
    questions already written for the concepts that week studies, plus any
    cross-track concepts named in `quiz_from` (the Java track reuses the
    language-agnostic Algorithms and Java Vocab banks this way).

    The UI samples `quiz_sample` of the bank and shuffles, so a retake is not a
    memory test for answer positions. Deduped by question text; `quiz_from` is
    consumed here and dropped from the emitted JSON."""
    for track in tracks:
        for week in track["weeks"]:
            seen = {q["question"] for q in week["quiz"]}
            sources = list(week["concepts"]) + list(week.pop("quiz_from", []))
            for key in sources:
                for q in concepts.get(key, {}).get("quiz", []) or []:
                    if q["question"] in seen:
                        continue
                    seen.add(q["question"])
                    week["quiz"].append(q)
            # Never ask for more questions than the bank can supply.
            week["quiz_sample"] = min(week["quiz_sample"], len(week["quiz"]))


TS_WEEKS = [
    # =======================================================================
    # MONTH 1 — Language foundations
    # =======================================================================
    _w(1, "Month 1 · Language foundations",
       "Values, Types & Inference",
       "Declare and annotate values, and understand what TypeScript works out on its own.",
       ["ts_variables", "ts_types", "ts_inference"],
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
       ["ts_operators", "ts_conditionals"],
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
       ["ts_loops", "ts_number_math"],
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
       ["ts_strings", "ts_string_methods"],
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

    # =======================================================================
    # MONTH 2 — Functions & data
    # =======================================================================
    _w(5, "Month 2 · Functions & data",
       "Functions & Parameters",
       "Write functions with precise signatures — optional, default and rest parameters.",
       ["ts_functions", "ts_params"],
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
       ["ts_higher_order"],
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
       ["ts_arrays", "ts_array_methods"],
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
       ["ts_destructuring", "ts_objects", "ts_json"],
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

    _w(11, "Month 3 · The type system",
        "Narrowing & Type Guards",
        "Prove to the compiler what a value is — with built-in narrowing and your own predicates.",
        ["ts_narrowing", "ts_type_predicates"],
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
          "An assertion function makes a demand rather than asking a question — control continues past it only when the value really is that type.")]),

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

    _w(13, "Month 3 · The type system",
        "Checkpoint — Consolidation",
        "No new concepts. Re-solve, re-read and prove the first three months stuck.",
        [],
        [("longest-unique-substring", "Sliding window over a string — Weeks 4, 7, 9."),
         ("group-anagrams-count", "Canonical keys and a Map — Week 9."),
         ("merge-two-sorted-lists", "Careful pointer work and narrowing — Weeks 11, 12."),
         ("subarray-sum-k", "Prefix sums in a Map — Weeks 7, 9."),
         ("valid-anagram", "Fast recap of the string toolkit — Week 4.")],
        "Re-implement your Week 8 config reader from scratch without looking at it. Then diff the two and write down every difference you can justify.",
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
          "Without it, every type silently includes null and undefined, so no annotation can be trusted. It is the foundation the rest rests on.")]),

    # =======================================================================
    # MONTH 4 — Rigor
    # =======================================================================
    _w(14, "Month 4 · Rigor",
        "Nullability & Compiler Strictness",
        "Handle absence explicitly, and know which flag is catching you.",
        ["ts_nullish", "ts_tsconfig"],
        [("missing-number", "Absence as a first-class case."),
         ("count-negatives", "Boundary conditions on an index scan."),
         ("is-sorted", "An empty input is a real case — decide what it means.")],
        "Take your Week 8 config reader and turn on `noUncheckedIndexedAccess` in your head: rewrite every index access to handle `undefined` honestly.",
        [("With `strictNullChecks` on, what does `string` mean?",
          ["A string — absence must be written as string | null or string | undefined",
           "A string, null or undefined",
           "A non-empty string",
           "The same as before; the flag only affects parameters"], 0,
          "The flag is what makes annotations mean what they say. Off, every type quietly includes the nullish values."),
         ("What does `noUncheckedIndexedAccess` change?",
          ["arr[i] becomes T | undefined, reflecting that the index may be out of range",
           "It throws at runtime on a bad index",
           "It forbids index signatures",
           "It requires .at() instead of brackets"], 0,
          "It tells the truth about indexing. Not part of `strict`, usually the most disruptive flag to adopt — and the most valuable."),
         ("What is the difference between `a?.b` and `a!.b`?",
          ["?. short-circuits to undefined; !. asserts a is non-null and checks nothing",
           "They are equivalent",
           "!. throws a helpful error when a is null",
           "?. only works on methods"], 0,
          "The non-null assertion is a promise, not a check. If it is wrong you get a plain runtime TypeError with no extra context."),
         ("Why prefer `@ts-expect-error` over `@ts-ignore`?",
          ["It errors once the problem is fixed, so the suppression cannot outlive its reason",
           "It suppresses fewer categories",
           "It is checked at runtime",
           "It works only in tests"], 0,
          "`@ts-ignore` hides whatever the next line does, forever. `@ts-expect-error` fails when there is nothing left to suppress.")]),

    _w(15, "Month 4 · Rigor",
        "Assertions, satisfies & Structural Typing",
        "Understand what the compiler compares, and the two very different ways to override it.",
        ["ts_assertions", "ts_satisfies", "ts_structural_typing"],
        [("longest-common-prefix-strs", "Shape-driven helpers over string arrays."),
         ("design-hashmap", "Build to an interface without inheriting from one.")],
        "Write a `routes.ts` that declares a route table with `satisfies`, derives the route-name union from it, and exposes a lookup that rejects unknown names.",
        [("What does `satisfies` do that an annotation does not?",
          ["Checks the value against the type while keeping its narrower inferred type",
           "Checks the value at runtime",
           "Widens the value to the given type",
           "Makes the value readonly"], 0,
          "An annotation replaces the inferred type; `satisfies` only validates against it, so literal keys and tuple shapes survive."),
         ("Why is `const p: Point = { x: 1, y: 2, label: \"h\" }` an error when assigning the same object via a variable is not?",
          ["The excess property check applies only to fresh object literals assigned directly",
           "Variables are typed any",
           "Both are errors, reported at different times",
           "label is a reserved name"], 0,
          "The literal form is where typos live, so TypeScript checks it. Widening through a variable falls back to ordinary structural assignability."),
         ("Two unrelated aliases with identical members — is one assignable to the other?",
          ["Yes; structural typing compares shapes, not names",
           "No; they are distinct named types",
           "Only if one extends the other",
           "Only for interfaces"], 0,
          "Nothing links them by name, but their members match. This is the core difference from Java's nominal `implements`."),
         ("What makes a class partly nominal?",
          ["private or protected members, which only match the declaring class",
           "A constructor",
           "Implementing an interface",
           "Being abstract"], 0,
          "Private members are tied to their declaration, so two identical-looking classes are not interchangeable — the one nominal corner of the system.")]),

    _w(16, "Month 4 · Rigor",
        "Branded Types & Immutability",
        "Make validated values a type, and stop accidental mutation at the boundary.",
        ["ts_branded_types", "ts_immutability"],
        [("product-except-self", "Build a new array rather than editing in place."),
         ("rotate-array", "Compare the in-place and copying solutions honestly.")],
        "Write an `ids.ts` with branded `UserId` and `OrderId`, validating parsers for both, and a `readonly` lookup table that cannot be mutated by callers.",
        [("What does a brand cost at runtime?",
          ["Nothing — the intersection is erased and the value stays a plain string",
           "One object allocation per value",
           "A hidden property on each value",
           "A prototype lookup per access"], 0,
          "That is the appeal over a wrapper class: nominal safety with zero runtime representation."),
         ("Why should exactly one function apply the `as UserId` cast?",
          ["It concentrates the unchecked assertion in one validated place",
           "TypeScript allows one cast per type",
           "Casting elsewhere fails at runtime",
           "The compiler counts casts"], 0,
          "A brand is only as trustworthy as the assertions that create it. Scattered casts mean the type proves nothing."),
         ("What does `readonly string[]` prevent?",
          ["Calling mutating methods and assigning to indices",
           "Reassigning the variable",
           "Reading elements",
           "Passing the array to functions"], 0,
          "It is a compile-time restriction on the array's own operations. `const` only stops rebinding the variable."),
         ("Does `Object.freeze` give you a deeply immutable object?",
          ["No — it is shallow; nested objects remain mutable",
           "Yes, it recurses",
           "Only under strict mode",
           "Only for arrays"], 0,
          "Freezing one level is the runtime counterpart to `Readonly<T>`, which is also shallow. Deep immutability needs a recursive helper.")]),

    _w(17, "Month 4 · Rigor",
        "Composition & Utility Types",
        "Build types out of other types instead of restating them.",
        ["ts_compose", "ts_utility_types"],
        [("merge-intervals", "Sort, then fold — with a well-typed interval."),
         ("insert-interval", "A variant of the same model."),
         ("can-attend-meetings", "The simplest form of the pattern.")],
        "Model a `Task` type, then derive `TaskDraft` (no id), `TaskPatch` (all optional) and `TaskSummary` (a few fields) with `Omit`, `Partial` and `Pick` rather than three hand-written types.",
        [("What does `Omit<T, K>` do?",
          ["Produces T without the properties named in K",
           "Makes the properties in K optional",
           "Keeps only the properties in K",
           "Makes T readonly except K"], 0,
          "`Pick` keeps, `Omit` removes. `Omit` is defined in terms of `Pick` and `Exclude`."),
         ("How do you combine two object types?",
          ["An intersection: A & B, or interface B extends A",
           "A union: A | B",
           "Object.assign at the type level",
           "Merge<A, B>"], 0,
          "An intersection requires BOTH sets of members. A union means 'one or the other', which is the opposite of combining."),
         ("What is `Record<string, number>`?",
          ["An object type with string keys and number values",
           "A tuple of a string and a number",
           "A Map with those types",
           "A union of string and number"], 0,
          "`Record` is a mapped type: `{ [P in K]: V }`. Note that a string-keyed Record loses literal key checking."),
         ("`Partial<T>` makes every property optional. What is its inverse?",
          ["Required<T>", "Complete<T>", "NonNullable<T>", "Readonly<T>"], 0,
          "`Required<T>` is `{ [K in keyof T]-?: T[K] }` — the `-?` strips the optional modifier the source type had.")]),

    # =======================================================================
    # MONTH 5 — Generics & type-level
    # =======================================================================
    _w(18, "Month 5 · Generics & type-level",
        "Generics & Constraints",
        "Write one implementation that keeps every caller's exact type.",
        ["ts_generics", "ts_generic_constraints"],
        [("two-sum-fn", "A function whose signature is the interesting part."),
         ("reverse-array-fn", "Generic in the element type."),
         ("kth-largest-element", "A comparator-driven selection.")],
        "Write a `collections.ts` exporting generic `unique`, `groupBy`, `partition` and `sortBy` helpers, each preserving the input's element type.",
        [("Why is `<T extends { length: number }>` better than a plain `{ length: number }` parameter?",
          ["The generic returns the caller's exact type instead of collapsing it",
           "It is faster",
           "The non-generic form does not compile",
           "Only the generic accepts arrays"], 0,
          "Both accept the same arguments. The difference is on the way out — the generic hands back `string` for strings."),
         ("In `get<T, K extends keyof T>(obj: T, key: K): T[K]`, what is `T[K]`?",
          ["An indexed access type — the type of the property named K",
           "An array of T indexed by K",
           "A mapped type",
           "The same as keyof T"], 0,
          "It looks up a property type by name, which is how one signature returns `string` for one key and `number` for another."),
         ("What does a type-parameter default like `<T = string>` do?",
          ["Supplies T only when inference has nothing to work from",
           "Makes the parameter optional",
           "Coerces the argument to string",
           "Constrains T to string"], 0,
          "It is not a value default. `makeBox(1)` still infers `number`; the default matters when no argument drives inference."),
         ("When is a generic the WRONG tool?",
          ["When the body never uses T — a plain parameter type is clearer",
           "When there is more than one type parameter",
           "When T is constrained",
           "When the function is exported"], 0,
          "A type parameter used once and never related to anything else adds noise without adding a guarantee.")]),

    _w(19, "Month 5 · Generics & type-level",
        "keyof, typeof & Indexed Access",
        "Derive types from values so one source of truth drives both.",
        ["ts_keyof_indexed"],
        [("time-based-kv", "A keyed store with a typed accessor."),
         ("prefix-counts", "Deriving structure from data.")],
        "Write a `settings.ts` where one `as const` object defines the defaults, and every getter, setter and key union is derived from it — adding a setting should require exactly one edit.",
        [("What is `(typeof levels)[number]` when `const levels = [\"a\", \"b\"] as const`?",
          ["\"a\" | \"b\"", "string", "readonly [\"a\", \"b\"]", "number"], 0,
          "`as const` keeps the elements literal, and indexing the tuple type by `number` unions them — the standard derive-a-union idiom."),
         ("Drop the `as const`. What does it become?",
          ["string", "\"a\" | \"b\"", "never", "string[]"], 0,
          "The array widens to `string[]`, so the literal information is gone before the type-level trick can use it."),
         ("How does type-position `typeof` differ from the runtime operator?",
          ["It lifts a value into a type; the runtime one returns a string when executed",
           "They are the same operator",
           "The type one works on classes only",
           "The runtime one is erased"], 0,
          "They share a keyword and nothing else. One computes a type, the other is a runtime check that happens to narrow."),
         ("What is `keyof Record<string, number>`?",
          ["string | number", "string", "number", "never"], 0,
          "`keyof` on an index signature gives the index type, and numeric keys are also valid string keys — which is why it includes `number`.")]),

    _w(20, "Month 5 · Generics & type-level",
        "Mapped Types",
        "Transform every property of a type at once — and build what the type describes.",
        ["ts_mapped_types"],
        [("design-hashset", "A container described by a derived type."),
         ("top-k-frequent", "Projection over a frequency table.")],
        "Reimplement `Partial`, `Required`, `Readonly`, `Pick` and `Omit` from scratch in a `utils.d.ts`, then check each against the built-in with a type-level test.",
        [("What does `{ [K in keyof T]-?: T[K] }` produce?",
          ["Every property made required — the built-in Required<T>",
           "Every property made optional",
           "T with all properties removed",
           "A union of T's property types"], 0,
          "The `-` prefix strips a modifier the source had. `-readonly` does the same for readonly."),
         ("In an `as` clause, what happens to a key mapped to `never`?",
          ["The property is removed — this is how Omit works",
           "Its type becomes never",
           "It is a compile error",
           "It is renamed to \"never\""], 0,
          "Key remapping to `never` drops the entry, which is the mechanism behind every filtering utility type."),
         ("You define `Getters<T>` renaming keys to getName/getAge. What exists at runtime?",
          ["Nothing — the type only describes an object you still have to build",
           "An object with those methods",
           "A proxy",
           "The original object with extra prototype methods"], 0,
          "Mapped types are erased like everything else in the type system. They describe an obligation your runtime code has to meet."),
         ("What is `keyof (A | B)`?",
          ["The keys A and B have in COMMON",
           "All keys of both",
           "never",
           "The keys of A only"], 0,
          "Only shared keys are safe to access on a value that might be either — a frequent surprise when mapping over a union.")]),

    _w(21, "Month 5 · Generics & type-level",
        "Conditional Types & infer",
        "Branch on types and pattern-match their structure.",
        ["ts_conditional_types"],
        [("subarray-sum-k", "A hashing problem worth revisiting with better types."),
         ("longest-unique-substring", "Sliding window, cleanly typed.")],
        "Write a `types.ts` implementing `ReturnType`, `Parameters`, `Awaited` and `Exclude` yourself, with a comment on each explaining where `infer` binds.",
        [("What does `infer` do?",
          ["Binds a fresh type variable to whatever matched at that position",
           "Forces re-inference of the expression",
           "Declares a default for the type parameter",
           "Converts a value into a type"], 0,
          "`T extends (infer U)[] ? U : T` matches T against 'array of something' and names that something `U`."),
         ("`type NonNil<T> = T extends null | undefined ? never : T`. What is `NonNil<string | null>`?",
          ["string", "string | null", "never", "string | never"], 0,
          "T is naked, so the conditional distributes: `string` takes the else branch, `null` becomes `never`, and `never` vanishes from a union."),
         ("How do you STOP a conditional type distributing?",
          ["Wrap both sides in a tuple: [T] extends [U] ? X : Y",
           "Add a nodistribute modifier",
           "Constrain T with extends object",
           "Use an interface"], 0,
          "Distribution needs a bare type parameter. Putting it in a tuple makes it non-naked, so the check runs once on the whole union."),
         ("What is `IsString<any>` for `type IsString<T> = T extends string ? \"yes\" : \"no\"`?",
          ["\"yes\" | \"no\" — any takes both branches",
           "\"yes\"", "\"no\"", "any"], 0,
          "`any` is assignable to everything and nothing simultaneously, so a conditional over it resolves to the union of both branches.")]),

    _w(22, "Month 5 · Generics & type-level",
        "Template Literals & Recursive Types",
        "Encode naming conventions in the type system, and describe unbounded data.",
        ["ts_template_literal_types", "ts_type_level"],
        [("replace-words-roots", "Prefix matching over a dictionary."),
         ("implement-trie-ops", "A recursive structure with a recursive type.")],
        "Write an `events.ts` where the entity and action lists are `as const` arrays, the event-name type is a template literal over them, and a typed emitter rejects any name not in the catalogue.",
        [("How many members does `` `${\"a\" | \"b\"}-${\"x\" | \"y\" | \"z\"}` `` have?",
          ["6", "5", "2", "3"], 0,
          "Interpolating unions gives the cross product — 2 × 3. This growth is also why deeply nested templates can exhaust the compiler."),
         ("Where can `Capitalize<T>` be used?",
          ["Only inside template literal types — it is a compiler intrinsic",
           "Anywhere, including at runtime",
           "Only in key remapping",
           "Only on unions"], 0,
          "`Capitalize`, `Uppercase`, `Lowercase` and `Uncapitalize` live purely in the type system. Capitalizing a real string is still your own code."),
         ("Why is `type Bad = Bad | string` an error while `type Json = string | Json[]` is fine?",
          ["A recursive alias must go through an object, array or function",
           "Unions cannot be recursive",
           "Bad has no base case",
           "type aliases cannot be recursive at all"], 0,
          "`Bad` refers to itself with nothing to defer into. Wrapping the recursion in `Json[]` gives the checker a structure to expand lazily."),
         ("What does `T extends readonly [unknown, ...infer Rest]` accomplish?",
          ["Peels the first tuple element and binds the rest, enabling recursion",
           "Checks T is a readonly array",
           "Reverses the tuple",
           "Makes the tuple mutable"], 0,
          "It is the type-level head/tail destructure — the shrinking step every recursive tuple algorithm needs.")]),

    # =======================================================================
    # MONTH 6 — Runtime & architecture
    # =======================================================================
    _w(23, "Month 6 · Runtime & architecture",
        "Classes & Encapsulation",
        "Use classes where they pay — real privacy, invariants and accessors.",
        ["ts_classes", "ts_this_accessors"],
        [("design-circular-queue", "Invariants enforced by the class."),
         ("design-linked-list", "State that must stay consistent."),
         ("lru-cache", "Two structures kept in step behind one interface.")],
        "Write an `account.ts` with a `BankAccount` class whose balance is `#private`, exposing `deposit`, `withdraw` (rejecting overdrafts) and a computed `balance` getter.",
        [("What is the difference between `#count` and `private count`?",
          ["`#` is enforced by the JavaScript engine; `private` is erased at compile time",
           "They are identical",
           "`private` works on methods only",
           "`#` cannot be used in generic classes"], 0,
          "A `private` field is visible to any JavaScript that ignores the types. A `#` field is genuinely inaccessible from outside the class."),
         ("Why do arrow-function class fields fix the `this` problem?",
          ["They capture `this` from the instance at construction rather than at call time",
           "They are bound by the compiler",
           "They cannot be detached from the object",
           "They make the method static"], 0,
          "Passing `obj.method` as a callback loses the receiver. An arrow field closes over `this` when the instance is built, so it travels with the function."),
         ("What does a `get` accessor let you do?",
          ["Expose a computed value through property syntax",
           "Make a field readonly",
           "Validate assignments",
           "Define a static member"], 0,
          "Getters compute on access; `set` accessors are the ones that validate assignment. `readonly` is a separate modifier."),
         ("When should you NOT reach for a class?",
          ["When the thing is plain data with no invariant to protect",
           "When you need generics",
           "When you need iteration",
           "When there is more than one instance"], 0,
          "Data with no behaviour is better as a plain object plus functions — it stays serializable and structurally typed.")]),

    _w(24, "Month 6 · Runtime & architecture",
        "Iterators, Generators & Generic Data Structures",
        "Produce values lazily and build containers that feel built-in.",
        ["ts_iterators", "ts_ds_generics"],
        [("implement-queue-stacks", "A container with an interface contract."),
         ("implement-stack-queues", "The mirror image."),
         ("design-twitter", "Composition of several structures.")],
        "Write a `lazy.ts` with generator-based `range`, `map`, `filter`, `take` and `chunk`, then use them to process an infinite sequence without materialising it.",
        [("What happens the second time you iterate the same generator object?",
          ["Nothing is produced — it is exhausted after one pass",
           "It restarts",
           "It throws",
           "It yields in reverse"], 0,
          "A generator holds its own position. Return a FUNCTION when callers may need to iterate more than once."),
         ("Why does `take(naturals(), 4)` terminate?",
          ["Generators are lazy — naturals only computes when take asks, and take stops asking",
           "TypeScript bounds infinite loops",
           "naturals is evaluated up to a default limit",
           "Spread caps at 1000 elements"], 0,
          "Production is driven entirely by consumption. Spreading `naturals()` with no `take` really would hang."),
         ("Why type `pop()` as `T | undefined` rather than `T`?",
          ["An empty stack really returns undefined, and the type should say so",
           "Generic methods cannot return a bare T",
           "It is faster",
           "undefined is needed for iteration"], 0,
          "Typing it `T` hands the caller an `undefined` the compiler swears is a real value — exactly the bug types exist to prevent."),
         ("What does `yield*` do?",
          ["Delegates to another iterable, yielding all its values in place",
           "Yields an array of the remaining values",
           "Marks the generator infinite",
           "Yields then returns"], 0,
          "It forwards every value from the inner iterable as if written inline — the standard way to compose generators.")]),

    _w(25, "Month 6 · Runtime & architecture",
        "Errors & Async",
        "Make failure visible in the type, and run async work concurrently on purpose.",
        ["ts_errors", "ts_error_types", "ts_async", "ts_async_patterns"],
        [("hit-counter", "Time-ordered state with clear failure modes."),
         ("stock-spanner", "Incremental computation you could plausibly make async.")],
        "Write a `fetchAll.ts` that loads several simulated resources concurrently, races each against a timeout, and returns a `Result` per resource — no exception escapes.",
        [("Under `strict`, what type does `catch (e)` give `e`?",
          ["unknown", "Error", "any", "never"], 0,
          "Any value can be thrown, so TypeScript refuses to assume `Error`. Narrow with `instanceof` before reading properties."),
         ("What makes `Result<T, E>` enforce handling?",
          ["It is a discriminated union — `value` only exists after checking `ok`",
           "The compiler tracks unhandled Results",
           "It throws if the error branch is ignored",
           "E defaults to string"], 0,
          "On the failure branch there is no `value` property at all, so skipping the check is a type error rather than a runtime surprise."),
         ("What is the total time of `await Promise.all(ids.map(fetchOne))` versus awaiting in a loop?",
          ["The maximum of the individual times, versus the sum",
           "The same",
           "The sum, versus the maximum",
           "It depends on CPU cores"], 0,
          "`.map` starts every promise before `all` waits, so they overlap. A loop starts each only after the previous resolves."),
         ("How does `Promise.race` differ from `Promise.any`?",
          ["race settles with the first to settle either way; any waits for the first SUCCESS",
           "any is the async version of race",
           "race rejects only on timeout",
           "They are aliases"], 0,
          "`race` is the timeout pattern precisely because an early rejection wins. `any` ignores rejections until every input has failed.")]),

    _w(26, "Month 6 · Runtime & architecture",
        "Modules, Declarations & Capstone",
        "Structure a real project, describe the code you do not own, and prove the six months.",
        ["ts_modules", "ts_declaration_files"],
        [("median-from-stream", "Two heaps, cleanly encapsulated."),
         ("word-ladder-length", "BFS over a derived graph."),
         ("lfu-cache", "The hardest design problem in the bank — take your time.")],
        "Capstone: build a small typed CLI as a multi-file project — a `Result`-based parser, a branded id type, a generic store with an iterator, an ambient declaration for one host global, and `strict` plus `noUncheckedIndexedAccess` clean.",
        [("What does a `.d.ts` file emit at build time?",
          ["Nothing — it only describes types the runtime is assumed to provide",
           "A JavaScript stub per declaration",
           "A module that must be imported",
           "A runtime validation shim"], 0,
          "Declaration files are pure description. Declaring something the runtime lacks gives a ReferenceError with no compile-time warning."),
         ("Why must module augmentation use `interface` rather than `type`?",
          ["Interfaces merge across declarations; type aliases cannot be reopened",
           "type is illegal inside declare module",
           "Interfaces are erased and types are not",
           "type cannot describe objects"], 0,
          "Declaration merging is interface-only, and it is what lets you ADD a field to a library type instead of shadowing it."),
         ("What is the difference between a default export and a named export?",
          ["A default can be imported under any name, which makes it easy to rename inconsistently",
           "A default is faster to load",
           "Named exports cannot be re-exported",
           "A module may have several defaults"], 0,
          "Named exports keep one canonical spelling across the codebase, which is why many style guides prefer them for anything but a single obvious entry point."),
         ("What does `import type { X } from \"./x\"` guarantee?",
          ["The import is erased entirely, so no runtime module dependency is created",
           "X is imported lazily",
           "X must be a type alias, not an interface",
           "The module is loaded but unused"], 0,
          "It makes the type-only intent explicit, avoiding a runtime import that a bundler would otherwise have to keep — the point of `verbatimModuleSyntax`.")]),
]




# ===========================================================================
# TypeScript coding finals — one per week.
#
# A multiple-choice quiz is the weakest possible gate for a programming
# curriculum, so every week also ends with a real problem run through the same
# judge as the Learn challenges (`run_tests` with a null problem id). The week
# only unlocks the next one when BOTH are passed.
#
# Each final synthesises the week's chapters rather than drilling one of them,
# and is scoped to what the syllabus has taught so far. Every `solution` is
# proven end-to-end by tests/verify_mastery.rs.
# ===========================================================================

_TS_SCAFFOLD = 'import * as fs from "fs";\nconst input = fs.readFileSync(0, "utf8").trim();\n'


def _ts_exam(title, prompt, body, tests, hint=""):
    """A TypeScript final: the stdin scaffold plus one `____` for the whole
    solution, exactly like a Learn challenge."""
    body = body.strip("\n")
    solution = _TS_SCAFFOLD + body + "\n"
    return {
        "title": title,
        "prompt": prompt,
        "hint": hint,
        "language": "typescript",
        "starter": _TS_SCAFFOLD + "____\n",
        "solution": solution,
        "tests": [{"input": i, "output": o} for (i, o) in tests],
    }


TS_EXAMS = {
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

    14: _ts_exam(
        "Safe lookup table",
        "The input is `n` then `n` lines of `key value`, then a final line of keys to look up. Treat every index and map access as possibly missing. Print `key=value` or `key=(missing)` per query, then how many queries missed.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const table = new Map<string, string>();
for (let i = 1; i <= n; i++) {
  const parts = lines[i].trim().split(/\\s+/);
  const key: string | undefined = parts[0];
  const value: string | undefined = parts[1];
  if (key !== undefined && value !== undefined) table.set(key, value);
}
let missed = 0;
for (const query of lines[n + 1].trim().split(/\\s+/)) {
  const found = table.get(query);
  if (found === undefined) missed++;
  console.log(query + "=" + (found ?? "(missing)"));
}
console.log(missed);
''',
        [("2\na 1\nb 2\na b c", "a=1\nb=2\nc=(missing)\n1"),
         ("1\nk v\nk", "k=v\n0"),
         ("1\nk v\nx y", "x=(missing)\ny=(missing)\n2")],
        hint="Map.get returns T | undefined — compare against undefined explicitly rather than relying on truthiness, or an empty-string value looks missing."),

    15: _ts_exam(
        "Route table with satisfies",
        "Declare a route table (`home` → `/`, `about` → `/about`, `docs` → `/docs`) checked with `satisfies Record<string, string>`, derive the name union from it, and look up each of the `n` requested names. Print the path or `404`, then the number of routes.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const routes = {
  home: "/",
  about: "/about",
  docs: "/docs",
} satisfies Record<string, string>;
type RouteName = keyof typeof routes;
for (let i = 1; i <= n; i++) {
  const name = lines[i].trim();
  console.log(name in routes ? routes[name as RouteName] : "404");
}
console.log(Object.keys(routes).length);
''',
        [("3\nhome\ndocs\nnope", "/\n/docs\n404\n3"),
         ("1\nabout", "/about\n3"),
         ("2\nx\ny", "404\n404\n3")],
        hint="`satisfies` keeps the keys literal, so `keyof typeof routes` is the three names rather than plain string."),

    16: _ts_exam(
        "Branded money",
        "Brand `Cents` and `Dollars`. The input is `n` then `n` amounts in cents. Print the running total in cents after each, then the final total in dollars (cents / 100). Only a validating constructor may produce a branded value; reject negatives by printing `invalid` for that line and skipping it.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
declare const brand: unique symbol;
type Cents = number & { readonly [brand]: "Cents" };
type Dollars = number & { readonly [brand]: "Dollars" };
function toCents(raw: number): Cents | null {
  return Number.isInteger(raw) && raw >= 0 ? (raw as Cents) : null;
}
function toDollars(c: Cents): Dollars {
  return (c / 100) as Dollars;
}
let total = 0;
for (let i = 1; i <= n; i++) {
  const cents = toCents(Number(lines[i].trim()));
  if (cents === null) {
    console.log("invalid");
    continue;
  }
  total += cents;
  console.log(total);
}
console.log(toDollars(total as Cents));
''',
        [("3\n120\n30\n-5", "120\n150\ninvalid\n1.5"),
         ("1\n100", "100\n1"),
         ("2\n0\n0", "0\n0\n0"),
         ("2\n250\n250", "250\n500\n5")],
        hint="Return `Cents | null` from the constructor so the caller must handle bad input; the cast inside it is the single place the brand is applied."),

    17: _ts_exam(
        "Merge intervals",
        "The input is `n` then `n` lines of `start end`. Merge every overlapping or touching interval and print the merged ones as `start end`, one per line sorted by start, then how many intervals were absorbed (input count minus output count).",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
type Interval = { start: number; end: number };
const intervals: Interval[] = [];
for (let i = 1; i <= n; i++) {
  const [start, end] = lines[i].trim().split(/\\s+/).map(Number);
  intervals.push({ start, end });
}
intervals.sort((a, b) => a.start - b.start);
const merged: Interval[] = [];
for (const current of intervals) {
  const last = merged[merged.length - 1];
  if (last !== undefined && current.start <= last.end) {
    last.end = Math.max(last.end, current.end);
  } else {
    merged.push({ ...current });
  }
}
for (const iv of merged) console.log(iv.start + " " + iv.end);
console.log(n - merged.length);
''',
        [("4\n1 3\n2 6\n8 10\n15 18", "1 6\n8 10\n15 18\n1"),
         ("2\n1 4\n4 5", "1 5\n1"),
         ("1\n5 7", "5 7\n0"),
         ("3\n1 10\n2 3\n4 5", "1 10\n2")],
        hint="Sort by start, then either extend the last merged interval or push a copy of the current one."),

    18: _ts_exam(
        "Generic collection helpers",
        "Write generic `unique`, `groupBy` and `sortBy`. The input is `n` then `n` lines of `category value`. Print each category in alphabetical order as `category: v1 v2` with its values sorted numerically ascending and duplicates removed, then the number of categories.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
type Row = { category: string; value: number };
function unique<T>(items: T[]): T[] {
  return [...new Set(items)];
}
function groupBy<T, K extends keyof T>(items: T[], key: K): Map<T[K], T[]> {
  const out = new Map<T[K], T[]>();
  for (const item of items) {
    const bucket = out.get(item[key]);
    if (bucket === undefined) out.set(item[key], [item]);
    else bucket.push(item);
  }
  return out;
}
function sortBy<T>(items: T[], score: (item: T) => number): T[] {
  return [...items].sort((a, b) => score(a) - score(b));
}
const rows: Row[] = [];
for (let i = 1; i <= n; i++) {
  const [category, value] = lines[i].trim().split(/\\s+/);
  rows.push({ category, value: Number(value) });
}
const groups = groupBy(rows, "category");
for (const category of [...groups.keys()].sort()) {
  const values = unique(sortBy(groups.get(category)!, (r) => r.value).map((r) => r.value));
  console.log(category + ": " + values.join(" "));
}
console.log(groups.size);
''',
        [("4\nb 2\na 3\nb 1\na 3", "a: 3\nb: 1 2\n2"),
         ("1\nx 9", "x: 9\n1"),
         ("3\nz 1\nz 2\nz 1", "z: 1 2\n1")],
        hint="`K extends keyof T` is what keeps the Map keyed by the field's real type instead of collapsing to string."),

    19: _ts_exam(
        "Settings from one source of truth",
        "Declare a defaults object, derive `Setting` with `keyof typeof`, and write a `read<K extends Setting>` returning `Profile[K]`. Defaults are `theme: \"dark\"`, `size: 14`, `wrap: true`. The input is `n` then `n` setting names. Print each value, or `unknown`, then the boolean-valued keys in alphabetical order.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const defaults = { theme: "dark", size: 14, wrap: true };
type Profile = typeof defaults;
type Setting = keyof Profile;
function read<K extends Setting>(key: K): Profile[K] {
  return defaults[key];
}
for (let i = 1; i <= n; i++) {
  const name = lines[i].trim();
  console.log(name in defaults ? String(read(name as Setting)) : "unknown");
}
const booleans = (Object.keys(defaults) as Setting[])
  .filter((k) => typeof defaults[k] === "boolean")
  .sort();
console.log(booleans.join(" "));
''',
        [("3\ntheme\nsize\nnope", "dark\n14\nunknown\nwrap"),
         ("1\nwrap", "true\nwrap"),
         ("2\nsize\ntheme", "14\ndark\nwrap")],
        hint="One object drives the values, the key union and the getter's return type — adding a setting should need exactly one edit."),

    20: _ts_exam(
        "Build what the mapped type describes",
        "`Getters<T>` renames each key to `getX` returning that property's type. The input is a name. Build the getters object at runtime for `{ name, size: 5 }`, then print `getName()`, `getSize()`, and the getter keys sorted and comma-joined.",
        '''
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };
const source = { name: input, size: 5 };
function makeGetters<T extends object>(obj: T): Getters<T> {
  const out: { [k: string]: () => unknown } = {};
  for (const key of Object.keys(obj)) {
    out["get" + key[0].toUpperCase() + key.slice(1)] = () =>
      (obj as { [k: string]: unknown })[key];
  }
  return out as Getters<T>;
}
const getters = makeGetters(source);
console.log(getters.getName());
console.log(getters.getSize());
console.log(Object.keys(getters).sort().join(","));
''',
        [("ada", "ada\n5\ngetName,getSize"), ("bob", "bob\n5\ngetName,getSize")],
        hint="The mapped type is erased — the loop has to produce the renamed keys itself, and the cast at the end is where you assert it matched."),

    21: _ts_exam(
        "Unwrap and compact",
        "Write `Unwrap<T>` (element type of an array, else T) and `NonNil<T>` (drops null/undefined from a union). The input is a line of tokens where `-` means null. Print the first non-null token or `(none)`, then the compacted tokens space-separated or `(none)`, then how many were dropped.",
        '''
type Unwrap<T> = T extends (infer U)[] ? U : T;
type NonNil<T> = T extends null | undefined ? never : T;
function firstOrSelf<T>(value: T): Unwrap<T> {
  return (Array.isArray(value) ? value[0] : value) as Unwrap<T>;
}
function compact<T>(items: T[]): NonNil<T>[] {
  return items.filter((x) => x !== null && x !== undefined) as NonNil<T>[];
}
const raw = input.split(/\\s+/).map((t) => (t === "-" ? null : t));
const kept = compact(raw);
console.log(firstOrSelf(kept) ?? "(none)");
console.log(kept.join(" ") || "(none)");
console.log(raw.length - kept.length);
''',
        [("- a b", "a\na b\n1"), ("- -", "(none)\n(none)\n2"),
         ("x y", "x\nx y\n0"), ("a - b -", "a\na b\n2")],
        hint="Both types are erased, so each function ends in a cast — the type describes what the runtime branch is obliged to produce."),

    22: _ts_exam(
        "Event catalogue",
        "Entities are `user`, `order`; actions are `created`, `updated`, `deleted`. Derive `EventName` as a template literal over `as const` arrays and build the catalogue at runtime. The input is `n` then `n` candidate names. Print `ok` or `bad` per name, then the catalogue size, then the names for `user` sorted.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const entities = ["user", "order"] as const;
const actions = ["created", "updated", "deleted"] as const;
type Entity = (typeof entities)[number];
type Action = (typeof actions)[number];
type EventName = `${Entity}:${Action}`;
const catalogue: EventName[] = [];
for (const entity of entities) {
  for (const action of actions) {
    catalogue.push(`${entity}:${action}`);
  }
}
const known = new Set<string>(catalogue);
for (let i = 1; i <= n; i++) {
  console.log(known.has(lines[i].trim()) ? "ok" : "bad");
}
console.log(catalogue.length);
console.log(catalogue.filter((e) => e.startsWith("user:")).sort().join(" "));
''',
        [("2\nuser:created\nuser:archived", "ok\nbad\n6\nuser:created user:deleted user:updated"),
         ("1\norder:deleted", "ok\n6\nuser:created user:deleted user:updated"),
         ("1\nnope", "bad\n6\nuser:created user:deleted user:updated")],
        hint="The nested loops over the two as-const arrays produce exactly the six names the template literal type describes."),

    23: _ts_exam(
        "Bank account with invariants",
        "Write a `BankAccount` class with a `#balance`, a `deposit`, a `withdraw` that refuses overdrafts, and a `balance` getter. The input is `n` then `n` commands (`deposit n`, `withdraw n`). Print the balance after each command, printing `refused` instead when a withdrawal would overdraw, then the final balance.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
class BankAccount {
  #balance = 0;
  deposit(amount: number): void {
    if (amount > 0) this.#balance += amount;
  }
  withdraw(amount: number): boolean {
    if (amount <= 0 || amount > this.#balance) return false;
    this.#balance -= amount;
    return true;
  }
  get balance(): number {
    return this.#balance;
  }
}
const account = new BankAccount();
for (let i = 1; i <= n; i++) {
  const [op, amountRaw] = lines[i].trim().split(/\\s+/);
  const amount = Number(amountRaw);
  if (op === "deposit") {
    account.deposit(amount);
    console.log(account.balance);
  } else {
    console.log(account.withdraw(amount) ? account.balance : "refused");
  }
}
console.log(account.balance);
''',
        [("3\ndeposit 100\nwithdraw 30\nwithdraw 200", "100\n70\nrefused\n70"),
         ("1\nwithdraw 5", "refused\n0"),
         ("2\ndeposit 10\ndeposit 5", "10\n15\n15")],
        hint="The invariant lives inside the class: withdraw is the only path that reduces #balance, and it refuses rather than going negative."),

    24: _ts_exam(
        "Lazy pipeline over an infinite source",
        "Write generators `naturals`, `filter`, `map` and `take`. The input is `count divisor`. Take the first `count` naturals divisible by `divisor`, square them, and print them space-separated (or `(none)`), then their sum. Nothing infinite may be materialised.",
        '''
const [count, divisor] = input.split(/\\s+/).map(Number);
function* naturals(): Generator<number> {
  let i = 1;
  while (true) yield i++;
}
function* filter<T>(source: Iterable<T>, keep: (value: T) => boolean): Generator<T> {
  for (const value of source) {
    if (keep(value)) yield value;
  }
}
function* map<T, U>(source: Iterable<T>, fn: (value: T) => U): Generator<U> {
  for (const value of source) yield fn(value);
}
function* take<T>(source: Iterable<T>, n: number): Generator<T> {
  let taken = 0;
  for (const value of source) {
    if (taken >= n) return;
    taken++;
    yield value;
  }
}
const picked = [...map(take(filter(naturals(), (x) => x % divisor === 0), count), (x) => x * x)];
console.log(picked.join(" ") || "(none)");
console.log(picked.reduce((a, b) => a + b, 0));
''',
        [("3 5", "25 100 225\n350"), ("1 1", "1\n1"),
         ("0 3", "(none)\n0"), ("2 2", "4 16\n20")],
        hint="take must `return` the moment it has enough — that is what stops the infinite source being pulled forever."),

    25: _ts_exam(
        "Concurrent loads with a Result",
        "`load(id)` resolves to `id * 10` after `id` ms but rejects for a negative id. Run every id concurrently, convert each outcome to a `Result`, and print `id=value` or `id=failed` in input order, then the number that succeeded and their total, space-separated.",
        '''
const ids = input.split(/\\s+/).map(Number);
type Result<T, E = string> = { ok: true; value: T } | { ok: false; error: E };
function load(id: number): Promise<number> {
  return new Promise((resolve, reject) => {
    if (id < 0) reject(new Error("bad id"));
    else setTimeout(() => resolve(id * 10), id);
  });
}
const settled = await Promise.allSettled(ids.map(load));
const results: Result<number>[] = settled.map((s) =>
  s.status === "fulfilled"
    ? { ok: true, value: s.value }
    : { ok: false, error: s.reason instanceof Error ? s.reason.message : String(s.reason) },
);
let succeeded = 0;
let total = 0;
results.forEach((result, i) => {
  if (result.ok) {
    succeeded++;
    total += result.value;
    console.log(ids[i] + "=" + result.value);
  } else {
    console.log(ids[i] + "=failed");
  }
});
console.log(succeeded + " " + total);
''',
        [("1 2 -1", "1=10\n2=20\n-1=failed\n2 30"),
         ("3", "3=30\n1 30"),
         ("-1 -2", "-1=failed\n-2=failed\n0 0"),
         ("0 4", "0=0\n4=40\n2 40")],
        hint="allSettled never rejects, so one bad id cannot lose the others; converting each entry to a Result makes the caller handle both branches."),

    26: _ts_exam(
        "Capstone: typed record store",
        "Combine the programme: a branded `RecordId`, a `Result`-returning parser, a generic iterable `Store<T>`, and an ambient host global. The input is `n` then `n` lines of `id value` (ids must match `r-\\\\d+`). Print `added <id>` or `rejected <line>` per line, then the stored ids space-separated in insertion order, then the store size.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
declare const brand: unique symbol;
type RecordId = string & { readonly [brand]: "RecordId" };
type Result<T, E = string> = { ok: true; value: T } | { ok: false; error: E };
function parseId(raw: string): Result<RecordId> {
  return /^r-\\d+$/.test(raw)
    ? { ok: true, value: raw as RecordId }
    : { ok: false, error: "bad id" };
}
class Store<T> {
  #items = new Map<string, T>();
  add(key: string, value: T): void {
    this.#items.set(key, value);
  }
  get size(): number {
    return this.#items.size;
  }
  *[Symbol.iterator](): Generator<string> {
    yield* this.#items.keys();
  }
}
const store = new Store<string>();
for (let i = 1; i <= n; i++) {
  const line = lines[i].trim();
  const [idRaw, value] = line.split(/\\s+/);
  const parsed = parseId(idRaw ?? "");
  if (parsed.ok && value !== undefined) {
    store.add(parsed.value, value);
    console.log("added " + parsed.value);
  } else {
    console.log("rejected " + line);
  }
}
console.log([...store].join(" ") || "(empty)");
console.log(store.size);
''',
        [("3\nr-1 alpha\nx-2 beta\nr-3 gamma",
          "added r-1\nrejected x-2 beta\nadded r-3\nr-1 r-3\n2"),
         ("1\nr-9 solo", "added r-9\nr-9\n1"),
         ("2\nbad\nnope x", "rejected bad\nrejected nope x\n(empty)\n0"),
         ("2\nr-1 a\nr-1 b", "added r-1\nadded r-1\nr-1\n1")],
        hint="Each piece is one week's idea: the brand proves validation happened, the Result forces the caller to branch, and Symbol.iterator makes the store spreadable."),
}




# ---------------------------------------------------------------------------
# Extra bank questions.
#
# Weeks whose chapters already carry their own quizzes (the mastery-track
# chapters each ship three) get a deep bank for free via _finalize_mastery.
# The foundational weeks below have no such source, so they get two authored
# questions each — enough that sampling four from the bank is a real draw
# rather than always the same paper.
# ---------------------------------------------------------------------------

TS_QUIZ_EXTRA = {
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
    17: [
        ("What does `A & B` mean for two object types?",
         ["A value must satisfy BOTH — it has all members of A and of B",
          "A value must satisfy either one",
          "Only the shared members",
          "A is replaced by B"], 0,
         "Intersection combines requirements. It is unions that mean 'one or the other', which is the opposite of what people first expect from the & symbol."),
        ("What is `Exclude<\"a\" | \"b\" | \"c\", \"b\">`?",
         ["\"a\" | \"c\"", "\"b\"", "never", "\"a\" | \"b\" | \"c\""], 0,
         "`Exclude` filters a union with a distributive conditional type. `Omit` is the object-level cousin, built from Exclude and Pick."),
    ],
    23: [
        ("Why does `const f = obj.method; f();` often break?",
         ["`this` is lost when the method is detached from its receiver",
          "Methods cannot be assigned to variables",
          "f is undefined",
          "It only breaks in strict mode"], 0,
         "A plain method call binds `this` from the call site. An arrow-function class field, or an explicit bind, keeps the receiver attached."),
        ("What does `readonly` on a class field prevent?",
         ["Assignment after the constructor finishes",
          "Reading the field from outside",
          "Subclasses declaring the same field",
          "Mutating the object the field points at"], 0,
         "It is a compile-time restriction on reassigning the field. The object it references can still be mutated freely."),
    ],
}

TS_CONTESTS = {
    13: ("Mastery checkpoint — Months 1–3", 90 * 60),
    26: ("Mastery finale — the whole programme", 120 * 60),
}

_attach(TS_WEEKS, TS_EXAMS, extra_quiz=TS_QUIZ_EXTRA, contests=TS_CONTESTS, sample=4)




# ===========================================================================
# JAVA MASTERY TRACK
#
# The same 26-week shape as the TypeScript programme, over the Java syllabus:
# language foundations, then the array/string scanning patterns, then the data
# structures, then trees, then recursion/DP, then graphs.
#
# Its question banks lean on two existing, already-authored sets of quizzes —
# the language-agnostic Algorithms track and the Java Vocab track — pulled in
# per week via `quiz_from`. Those are real questions about exactly this
# material, so reusing them is better than paraphrasing them.
# ===========================================================================

_JAVA_SCAFFOLD = (
    "import java.util.*;\n\n"
    "public class Main {\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
)


def _java_exam(title, prompt, body, tests, hint=""):
    """A Java final: the Scanner scaffold plus one `____` for the whole body."""
    indented = _b(body)
    return {
        "title": title,
        "prompt": prompt,
        "hint": hint,
        "language": "java",
        "starter": prog("        ____"),
        "solution": prog(indented),
        "tests": [{"input": i, "output": o} for (i, o) in tests],
    }


def _java_exam_cls(title, prompt, members, blank, tests, hint=""):
    """A Java final that needs class-level members (a helper method or a Node
    class). `members` is the full class body; `blank` is the fragment of it the
    learner writes, quoted verbatim."""
    full = _cls(members.strip("\n"))
    starter = full.replace(blank.strip("\n"), "____", 1)
    assert starter != full, f"java exam {title}: blank not found"
    return {
        "title": title,
        "prompt": prompt,
        "hint": hint,
        "language": "java",
        "starter": starter,
        "solution": full,
        "tests": [{"input": i, "output": o} for (i, o) in tests],
    }


JAVA_WEEKS = [
    # =======================================================================
    # MONTH 1 — Java foundations
    # =======================================================================
    _w(1, "Month 1 · Java foundations",
       "Reading Input & Variables",
       "Get data in, get answers out, and name values with the right type.",
       ["io_basics", "variables"],
       [("print-greeting", "The smallest possible read-and-print."),
        ("echo-line", "Whole-line input rather than a token."),
        ("add-two-numbers", "Two tokens, one arithmetic result."),
        ("rectangle-area", "Name the intermediate values.")],
       "Write a `Profile.java` that reads a name, an age and a city, then prints a three-line labelled summary — one variable per field, each explicitly typed.",
       [("Which Scanner call reads a whole line including spaces?",
         ["nextLine()", "next()", "nextString()", "readLine()"], 0,
         "`next()` stops at whitespace and returns one token. Mixing `nextInt()` with `nextLine()` also famously leaves the newline behind — read it off deliberately."),
        ("What is the difference between `int` and `Integer`?",
         ["int is a primitive; Integer is an object wrapper that can be null",
          "They are identical",
          "Integer is faster",
          "int can be null"], 0,
         "Collections can only hold objects, which is why `List<Integer>` exists — and why an unboxed null throws a NullPointerException."),
        ("What does `System.out.println(1 + 2 + \"x\")` print?",
         ["3x", "12x", "x3", "1 + 2x"], 0,
         "Evaluation is left to right: the two ints add first, then the result is concatenated. `\"x\" + 1 + 2` would give x12.")]),

    _w(2, "Month 1 · Java foundations",
       "Arithmetic & Booleans",
       "Integer division, remainder, and building conditions that read like the rule.",
       ["arithmetic", "boolean_logic"],
       [("even-or-odd", "Remainder as a predicate."),
        ("is-multiple", "The same idea, generalised."),
        ("larger-of-two", "A comparison feeding a decision."),
        ("leap-year", "A rule with nested exceptions — mind && over ||.")],
       "Write a `Change.java` that reads an amount in cents and prints how many quarters, dimes, nickels and pennies it takes, using only `/` and `%`.",
       [("What is `-7 / 2` in Java?",
         ["-3, because integer division truncates toward zero",
          "-4, rounding down",
          "-3.5",
          "3"], 0,
         "Java truncates toward zero, so -7/2 is -3 and -7%2 is -1. Languages that floor instead (like Python) give -4 and 1."),
        ("Why does `0.1 + 0.2 == 0.3` fail for doubles?",
         ["Binary floating point cannot represent those decimals exactly",
          "== compares references for doubles",
          "Java rounds to 15 digits",
          "It does not fail"], 0,
         "Compare with a tolerance, or use integers (cents) or BigDecimal when exactness matters."),
        ("What does short-circuit evaluation of `a && b` guarantee?",
         ["b is not evaluated when a is false",
          "Both sides always evaluate",
          "b evaluates first",
          "The result is cached"], 0,
         "This is what makes `if (arr != null && arr.length > 0)` safe. The non-short-circuiting `&` would evaluate both and throw.")]),

    _w(3, "Month 1 · Java foundations",
       "Conditionals & Loops",
       "Branch and repeat deliberately, with the right loop for the job.",
       ["conditionals", "loops_basic"],
       [("max-of-three", "Chained comparisons."),
        ("countdown", "Build output in a loop."),
        ("sum-to-n", "Accumulate a running total."),
        ("fizzbuzz-value", "Order the conditions correctly.")],
       "Write a `Triangle.java` that reads `n` and prints a right triangle of `*`, then the same triangle right-aligned — one nested loop each.",
       [("What is the difference between `while` and `do-while`?",
         ["do-while always runs the body at least once",
          "while can be broken out of; do-while cannot",
          "do-while is faster",
          "There is none"], 0,
         "`do-while` tests after the body, which is what you want for 'read, then decide whether to read again' loops."),
        ("What does `break` do inside nested loops?",
         ["Exits only the innermost loop, unless a label is used",
          "Exits every loop",
          "Exits the method",
          "Skips to the next iteration"], 0,
         "`continue` skips one iteration; a labelled break (`outer: for ...` then `break outer;`) is how you leave several levels at once."),
        ("Why does `for (int i = 0; i <= n; i++)` over an array of length n break?",
         ["The last index is n - 1, so i == n is out of bounds",
          "The loop never runs",
          "It skips the first element",
          "It is fine"], 0,
         "Off-by-one at the boundary is the most common array bug. The half-open convention `i < n` avoids it.")]),

    _w(4, "Month 1 · Java foundations",
       "Overflow & Bit Manipulation",
       "Know when an int is not big enough, and work with the bits directly.",
       ["overflow", "bit_manip"],
       [("factorial", "Growth that outruns int quickly."),
        ("number-of-1-bits", "Popcount."),
        ("power-of-two", "One bit trick, one line."),
        ("single-number", "XOR as a cancelling accumulator."),
        ("count-bits", "Popcount for a whole range.")],
       "Write a `Bits.java` that reads an int and prints its 32-bit binary form, its popcount, and the value with only its lowest set bit kept (`n & -n`).",
       [("`int a = 2_000_000_000; int b = a + a;` — what is b?",
         ["A negative number; the addition wrapped around",
          "4000000000",
          "Integer.MAX_VALUE",
          "It throws ArithmeticException"], 0,
         "Java's int arithmetic wraps silently. Widening one operand to long BEFORE the operation is the fix — casting the result afterwards is too late."),
        ("What does `n & (n - 1)` do?",
         ["Clears the lowest set bit",
          "Sets the lowest bit",
          "Halves n",
          "Flips every bit"], 0,
         "Which is why `n > 0 && (n & (n - 1)) == 0` tests for a power of two, and why repeating it counts set bits."),
        ("What is the difference between `>>` and `>>>`?",
         [">> keeps the sign bit; >>> shifts in zeros",
          ">>> is left shift",
          "They are identical for ints",
          ">> is unsigned"], 0,
         "For negative numbers `>>` preserves the sign while `>>>` does not — which is why `>>>` is used for the midpoint trick and hash mixing.")]),

    # =======================================================================
    # MONTH 2 — Numbers, arrays, strings
    # =======================================================================
    _w(5, "Month 2 · Numbers, arrays & strings",
       "Digits, Number Theory & Modular Arithmetic",
       "Take numbers apart, factor them, and keep results inside a modulus.",
       ["math_digits", "number_theory", "modulo"],
       [("count-digits", "Peel with / and %."),
        ("sum-of-digits", "Accumulate while peeling."),
        ("reverse-integer", "Rebuild in the other direction."),
        ("palindrome-number", "Compare without converting to a String."),
        ("gcd", "Euclid's algorithm."),
        ("is-prime", "Stop at the square root.")],
       "Write a `Modpow.java` computing `base^exp mod m` by squaring, and check it against a slow loop for small inputs.",
       [("Why does trial division stop at `d * d <= n`?",
         ["Any factor above the square root pairs with one below it",
          "Larger divisors cannot exist",
          "It is an approximation",
          "To avoid overflow"], 0,
         "Factors come in pairs around the square root, so finding none below it proves there are none at all."),
        ("Why compute LCM as `a / gcd * b` rather than `a * b / gcd`?",
         ["Dividing first keeps the intermediate value from overflowing",
          "It is faster",
          "a * b / gcd is wrong",
          "gcd may be zero"], 0,
         "Both are mathematically equal, but `a * b` can overflow long before the division brings it back down."),
        ("Why take the modulus at every step of modular exponentiation?",
         ["It keeps every intermediate product inside the range of a long",
          "It makes the result correct, which it otherwise would not be",
          "It is faster to compute",
          "It is only needed at the end"], 0,
         "The maths works either way; the reduction is what stops the intermediate values overflowing.")]),

    _w(6, "Month 2 · Numbers, arrays & strings",
       "Array Iteration & Patterns",
       "Scan an array once and answer several questions at the same time.",
       ["iteration", "array_patterns"],
       [("array-sum", "The basic accumulator."),
        ("array-maximum", "Seed correctly for negatives."),
        ("second-largest", "Track two values in one pass."),
        ("count-evens", "A predicate count."),
        ("running-sum", "Carry state across iterations.")],
       "Write a `Stats.java` that reads `n` then `n` numbers and prints min, max, sum, mean (2 decimals) and how many are above the mean — using no more than two passes.",
       [("Why seed a running maximum with `a[0]` rather than 0?",
         ["An all-negative array would otherwise report 0",
          "0 is slower",
          "a[0] is always the largest",
          "It avoids an off-by-one"], 0,
         "Seeding with a real element (or Integer.MIN_VALUE) is what makes the scan correct for every input, not just non-negative ones."),
        ("What does `int[] b = a;` do?",
         ["Copies the reference — both names see the same array",
          "Copies the contents",
          "Creates an empty array of the same length",
          "Is a compile error"], 0,
         "Arrays are objects. `Arrays.copyOf` or `clone()` is what actually duplicates the contents."),
        ("What is `arr.length` versus `s.length()`?",
         ["Arrays expose a length FIELD; String exposes a length() METHOD",
          "Both are methods",
          "Both are fields",
          "length() only works on char arrays"], 0,
         "A small inconsistency in the language, and one of the most common compile errors when moving between the two.")]),

    _w(7, "Month 2 · Numbers, arrays & strings",
       "Strings & Char Arrays",
       "Traverse text efficiently, and know when to drop to a char array.",
       ["string_basics", "char_arrays"],
       [("reverse-string", "Two pointers or a StringBuilder."),
        ("count-vowels", "A membership test per character."),
        ("count-words", "Splitting and its edge cases."),
        ("caesar-cipher", "Character arithmetic with wrap-around."),
        ("first-unique-char", "Two passes with a frequency table.")],
       "Write a `Words.java` that reads a line and prints the word count, the longest word, and the line with every word reversed in place.",
       [("Why is building a string with `s += c` in a loop slow?",
         ["Strings are immutable, so each += allocates and copies a new string",
          "The compiler cannot optimise +=",
          "It is not slow",
          "Because of Unicode handling"], 0,
         "That makes the loop O(n²). `StringBuilder` appends into a growable buffer and is the standard fix."),
        ("What does `s.charAt(i) - 'a'` give you?",
         ["The 0-based position of the letter in the alphabet",
          "The ASCII code of s.charAt(i)",
          "A String of length 1",
          "A compile error"], 0,
         "chars are integers, so subtracting 'a' maps 'a'..'z' onto 0..25 — the index into a 26-element counting array."),
        ("Why compare strings with `.equals()` rather than `==`?",
         ["== compares references, which differ for equal strings built at runtime",
          "equals is faster",
          "== does not compile for strings",
          "They are interchangeable"], 0,
         "Literals are interned so `==` often appears to work, which makes the bug show up only once the string comes from input.")]),

    _w(8, "Month 2 · Numbers, arrays & strings",
       "Canonical Forms & Simulation",
       "Give equivalent things one representation, and just follow the rules.",
       ["canonical", "simulation"],
       [("valid-anagram", "Sorting as a canonical key."),
        ("group-anagrams-count", "Grouping by that key."),
        ("robot-grid-walk", "Follow the instructions exactly."),
        ("minesweeper-counts", "Neighbour counting in a grid."),
        ("rotate-matrix-90", "Index arithmetic done carefully.")],
       "Write a `Life.java` that reads a grid and prints the next Game of Life generation — a pure simulation with careful boundary handling.",
       [("What makes a good canonical form?",
         ["Equivalent inputs map to the same key, and different ones do not",
          "It is always shorter than the input",
          "It is reversible",
          "It is always a sorted string"], 0,
         "Sorted characters work for anagrams; a 26-length count vector is the O(n) alternative with the same property."),
        ("Why copy the grid before applying Game of Life rules?",
         ["Every cell's next state depends on the CURRENT generation",
          "The original is readonly",
          "To avoid an out-of-bounds error",
          "Copying is not necessary"], 0,
         "Updating in place lets already-updated neighbours feed into later cells, which silently computes the wrong generation."),
        ("What is the usual way to visit a cell's four neighbours?",
         ["Two offset arrays, dr = {1,-1,0,0} and dc = {0,0,1,-1}, in one loop",
          "Four separate if blocks, which is the only correct way",
          "A nested loop over the whole grid",
          "Recursion"], 0,
         "The direction-array idiom keeps the bounds check in one place; the eight-neighbour version just extends the arrays.")]),

    # =======================================================================
    # MONTH 3 — Scanning patterns
    # =======================================================================
    _w(9, "Month 3 · Scanning patterns",
       "Two Pointers & In-place Work",
       "Walk a sorted array from both ends, and rearrange without extra space.",
       ["two_pointers", "inplace_reverse"],
       [("two-sum-sorted", "The canonical converging walk."),
        ("move-zeroes", "A write pointer trailing a read pointer."),
        ("reverse-array-fn", "Swap toward the middle."),
        ("container-most-water", "Move the limiting side."),
        ("is-palindrome-fn", "Converge and compare.")],
       "Write a `Dutch.java` sorting an array of 0s, 1s and 2s in one pass with three pointers — no sorting library call.",
       [("Why does the two-pointer sum walk require a SORTED array?",
         ["Sortedness is what makes 'too small' imply moving the low pointer",
          "It does not; it works on any array",
          "Sorting removes duplicates",
          "To allow binary search inside the loop"], 0,
         "Without order, a smaller sum tells you nothing about which side to move, and the O(n) argument collapses."),
        ("What does the write-pointer idiom achieve in move-zeroes?",
         ["Compaction in place: the write index only advances on a kept element",
          "It sorts the array",
          "It reverses the array",
          "It counts the zeroes"], 0,
         "Read every element, write only the ones you keep, then fill the tail — the standard in-place filter."),
        ("Rotating by reversal: reverse first k, reverse the rest, reverse the whole. Why does it work?",
         ["Each reversal puts a block in place while reversing it; the final one undoes that",
          "It is a coincidence of index arithmetic",
          "It only works when k divides n",
          "It requires extra space"], 0,
         "Three linear reversals give an O(n) time, O(1) space rotation — much simpler than juggling with cycle following.")]),

    _w(10, "Month 3 · Scanning patterns",
        "Sliding Window",
        "Maintain a window instead of recomputing every subarray.",
        ["sliding_window"],
        [("max-consecutive-ones", "The simplest window."),
         ("longest-unique-substring", "A window with a set."),
         ("min-window-length", "A window with counts."),
         ("best-time-buy-sell", "A running minimum, which is the degenerate case.")],
        "Write a `Window.java` that reads `n k` and `n` numbers and prints the maximum, minimum and average of every window of size k — one pass.",
        [("What is the difference between a fixed and a variable window?",
          ["A fixed window always moves both ends together; a variable one grows until a condition breaks, then shrinks",
           "A variable window can move backwards",
           "A fixed window needs sorting",
           "There is none"], 0,
          "The variable form is the one that solves 'longest substring with property P' — grow greedily, shrink only while the property is violated."),
         ("Why is the sliding-window sum O(n) rather than O(n·k)?",
          ["Each step adds the entering element and subtracts the leaving one",
           "Because k is small",
           "Because the array is sorted",
           "It is O(n·k)"], 0,
          "Reusing the previous window's answer is the whole trick — the same idea as a prefix sum, computed incrementally."),
         ("A window over an array with negative numbers — which pattern breaks?",
          ["Variable-size windows that assume growing the window grows the sum",
           "Fixed-size windows",
           "Both break",
           "Neither breaks"], 0,
          "Monotonicity is the hidden precondition of the shrink step. With negatives you usually need prefix sums plus a map instead.")]),

    _w(11, "Month 3 · Scanning patterns",
        "Prefix Sums & Running Maxima",
        "Precompute once so every range query is constant time.",
        ["prefix_sum", "prefix_max"],
        [("running-sum", "Building the prefix array."),
         ("product-except-self", "Prefix and suffix passes."),
         ("subarray-sum-k", "Prefix sums plus a hash map."),
         ("count-above-average", "Two passes over one aggregate.")],
        "Write a `Ranges.java` that reads an array and `q` queries and answers each `l r` range sum in O(1) after an O(n) build.",
        [("Given `pre[i+1] = pre[i] + a[i]`, what is the sum of `a[l..r]`?",
          ["pre[r+1] - pre[l]", "pre[r] - pre[l]",
           "pre[r] - pre[l-1]", "pre[r+1] - pre[l+1]"], 0,
          "The off-by-one is exactly why the prefix array is given an extra leading zero — it makes l = 0 work without a special case."),
         ("Why does subarray-sum-k need a hash map of prefix sums?",
          ["A subarray sums to k exactly when two prefix sums differ by k",
           "To deduplicate the array",
           "To sort the prefix sums",
           "It does not need one"], 0,
          "Counting earlier prefixes equal to `current - k` turns an O(n²) scan into one pass."),
         ("What does a difference array give you?",
          ["O(1) range UPDATES, with one final pass to materialise the values",
           "O(1) range queries",
           "A sorted array",
           "The maximum of a range"], 0,
          "It is the dual of a prefix sum: prefix sums make queries cheap, difference arrays make updates cheap.")]),

    _w(12, "Month 3 · Scanning patterns",
        "Hashing, Complements & Visited Sets",
        "Trade memory for time — the single most reusable idea in the syllabus.",
        ["hashing", "complement", "visited_set"],
        [("contains-duplicate", "A set, one pass."),
         ("two-sum-indices", "Complement lookup."),
         ("majority-element", "Counting in a map."),
         ("longest-consecutive", "A set turns a sort into a scan."),
         ("count-occurrences", "The basic frequency table.")],
        "Write an `Index.java` that reads lines of `word document` and answers lookup queries from an inverted index built in one pass.",
        [("Why is `map.getOrDefault(k, 0) + 1` preferred over a containsKey check?",
          ["It is one lookup and one branch fewer, with the same behaviour",
           "containsKey does not work for Integer keys",
           "It handles null values differently",
           "It is required for HashMap"], 0,
          "`merge(k, 1, Integer::sum)` is the same idea. Both avoid the double lookup of checking then getting."),
         ("What must a key type get right to work in a HashMap?",
          ["equals and hashCode must agree — equal objects must hash the same",
           "It must implement Comparable",
           "It must be immutable",
           "It must override toString"], 0,
          "Immutability matters too (mutating a key after insertion loses it), but the equals/hashCode contract is the hard requirement."),
         ("What does the complement pattern replace?",
          ["The inner loop of a nested search, by asking 'have I already seen what I need?'",
           "Sorting",
           "Recursion",
           "The need for a hash map"], 0,
          "It converts 'find a pair' from O(n²) to O(n) by storing what has been seen instead of re-scanning it.")]),

    _w(13, "Month 3 · Scanning patterns",
        "Checkpoint — Consolidation",
        "No new concepts. Re-solve across everything so far and prove it stuck.",
        [],
        [("two-sum-indices", "Hashing — Week 12."),
         ("longest-unique-substring", "Sliding window plus a set — Weeks 10, 12."),
         ("product-except-self", "Prefix and suffix — Week 11."),
         ("group-anagrams-count", "Canonical keys — Week 8."),
         ("move-zeroes", "In-place two pointers — Week 9.")],
        "Re-implement your Week 6 `Stats.java` from scratch without looking at it, then diff the two and justify every difference.",
        [("You need the k largest of a huge stream. Which shape fits best?",
          ["A size-k min-heap, so memory stays O(k)",
           "Sorting the whole stream",
           "A hash map of counts",
           "Two pointers"], 0,
          "Sorting needs the whole stream in memory and does more work than asked. The heap keeps only the current top k."),
         ("A problem says 'contiguous subarray'. Which two techniques should come to mind first?",
          ["Sliding window and prefix sums",
           "Binary search and sorting",
           "DFS and BFS",
           "Union-find and topological sort"], 0,
          "Contiguity is the signal. Once the problem says 'subsequence' instead, you are usually in dynamic-programming territory."),
         ("What does `Arrays.sort` use for an `int[]`?",
          ["A dual-pivot quicksort, which is not stable",
           "Merge sort, which is stable",
           "Heap sort",
           "Counting sort"], 0,
          "Primitives get quicksort (no stability concern since values are indistinguishable); object arrays get a stable TimSort.")]),
]


JAVA_EXAMS = {
    1: _java_exam(
        "Profile card",
        "The input is a name, an age and a city on one line. Print three labelled lines — `Name: ada`, `Age: 36`, `City: london` — then a fourth line with the age in dog years (age times 7).",
        """
        String name = sc.next();
        int age = sc.nextInt();
        String city = sc.next();
        System.out.println("Name: " + name);
        System.out.println("Age: " + age);
        System.out.println("City: " + city);
        System.out.println(age * 7);
        """,
        [("ada 36 london", "Name: ada\nAge: 36\nCity: london\n252"),
         ("bob 10 paris", "Name: bob\nAge: 10\nCity: paris\n70"),
         ("z 0 x", "Name: z\nAge: 0\nCity: x\n0")],
        hint="Read the three tokens in order with next()/nextInt()/next(), then build each line with string concatenation."),

    2: _java_exam(
        "Coin breakdown",
        "The input is an amount in cents. Print how many quarters (25), dimes (10), nickels (5) and pennies (1) it takes, one per line, taking as many of each as possible in that order.",
        """
        int cents = sc.nextInt();
        int quarters = cents / 25;
        cents %= 25;
        int dimes = cents / 10;
        cents %= 10;
        int nickels = cents / 5;
        cents %= 5;
        System.out.println(quarters);
        System.out.println(dimes);
        System.out.println(nickels);
        System.out.println(cents);
        """,
        [("87", "3\n1\n0\n2"), ("0", "0\n0\n0\n0"),
         ("100", "4\n0\n0\n0"), ("99", "3\n2\n0\n4")],
        hint="Divide to take the coins, then use % to keep only what is left before moving to the next denomination."),

    3: _java_exam(
        "Right triangle",
        "The input is one integer `n`. Print a left-aligned triangle of `*` with rows 1..n, then a blank line, then the same triangle right-aligned in a field of width `n` (padded with spaces).",
        """
        int n = sc.nextInt();
        for (int i = 1; i <= n; i++) {
            StringBuilder row = new StringBuilder();
            for (int j = 0; j < i; j++) row.append('*');
            System.out.println(row.toString());
        }
        System.out.println();
        for (int i = 1; i <= n; i++) {
            StringBuilder row = new StringBuilder();
            for (int j = 0; j < n - i; j++) row.append(' ');
            for (int j = 0; j < i; j++) row.append('*');
            System.out.println(row.toString());
        }
        """,
        [("3", "*\n**\n***\n\n  *\n **\n***"),
         ("1", "*\n\n*"),
         ("4", "*\n**\n***\n****\n\n   *\n  **\n ***\n****")],
        hint="Two nested loops per triangle: the inner one writes the padding, then the stars. Trailing spaces are trimmed by the judge, leading ones are not."),

    4: _java_exam(
        "Bit report",
        "The input is one non-negative int. Print its 32-bit binary form with leading zeros, its popcount, the value with only the lowest set bit kept (`n & -n`), and whether it is a power of two.",
        """
        int n = sc.nextInt();
        StringBuilder bits = new StringBuilder();
        for (int i = 31; i >= 0; i--) bits.append((n >> i) & 1);
        int count = 0;
        int rest = n;
        while (rest != 0) {
            rest &= rest - 1;
            count++;
        }
        System.out.println(bits.toString());
        System.out.println(count);
        System.out.println(n & -n);
        System.out.println(n > 0 && (n & (n - 1)) == 0);
        """,
        [("12", "00000000000000000000000000001100\n2\n4\nfalse"),
         ("16", "00000000000000000000000000010000\n1\n16\ntrue"),
         ("0", "00000000000000000000000000000000\n0\n0\nfalse"),
         ("7", "00000000000000000000000000000111\n3\n1\nfalse")],
        hint="Walk bits from 31 down to 0 for the binary string; `rest &= rest - 1` clears one set bit per pass, which counts them."),

    5: _java_exam(
        "Modular power",
        "The input is `base exp mod`. Print `base^exp mod m` computed by squaring, then the greatest common divisor of `base` and `mod`, then whether `base` is prime.",
        """
        long base = sc.nextLong();
        long exp = sc.nextLong();
        long mod = sc.nextLong();
        long result = 1 % mod;
        long b = base % mod;
        long e = exp;
        while (e > 0) {
            if ((e & 1) == 1) result = result * b % mod;
            b = b * b % mod;
            e >>= 1;
        }
        System.out.println(result);
        long x = base;
        long y = mod;
        while (y != 0) {
            long t = x % y;
            x = y;
            y = t;
        }
        System.out.println(x);
        boolean prime = base >= 2;
        for (long d = 2; d * d <= base; d++) {
            if (base % d == 0) {
                prime = false;
                break;
            }
        }
        System.out.println(prime);
        """,
        [("2 10 1000", "24\n2\ntrue"), ("3 0 7", "1\n1\ntrue"),
         ("12 3 100", "28\n4\nfalse"), ("5 3 13", "8\n1\ntrue")],
        hint="Reduce mod at every multiplication. Keep the gcd loop separate from the exponentiation so neither clobbers the other's variables."),

    6: _java_exam(
        "Array statistics",
        "The input is `n` then `n` integers. Print the minimum, the maximum, the sum, the mean to exactly two decimals, and how many values are strictly above the mean.",
        """
        int n = sc.nextInt();
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        int min = a[0];
        int max = a[0];
        long sum = 0;
        for (int i = 0; i < n; i++) {
            if (a[i] < min) min = a[i];
            if (a[i] > max) max = a[i];
            sum += a[i];
        }
        double mean = (double) sum / n;
        int above = 0;
        for (int i = 0; i < n; i++) {
            if (a[i] > mean) above++;
        }
        System.out.println(min);
        System.out.println(max);
        System.out.println(sum);
        System.out.printf("%.2f%n", mean);
        System.out.println(above);
        """,
        [("4\n1 2 3 4", "1\n4\n10\n2.50\n2"),
         ("1\n7", "7\n7\n7\n7.00\n0"),
         ("3\n-5 -1 -3", "-5\n-1\n-9\n-3.00\n1"),
         ("5\n2 2 2 2 2", "2\n2\n10\n2.00\n0")],
        hint="Seed min and max with a[0]. Cast to double BEFORE dividing, or integer division truncates the mean."),

    7: _java_exam(
        "Word report",
        "The input is one line of lowercase words. Print the word count, the longest word (first on a tie), the line with each word reversed in place, and the number of vowels in the whole line.",
        """
        String line = sc.nextLine();
        String[] words = line.split(" ");
        String longest = words[0];
        StringBuilder out = new StringBuilder();
        int vowels = 0;
        for (int i = 0; i < words.length; i++) {
            if (words[i].length() > longest.length()) longest = words[i];
            if (i > 0) out.append(' ');
            out.append(new StringBuilder(words[i]).reverse());
        }
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') vowels++;
        }
        System.out.println(words.length);
        System.out.println(longest);
        System.out.println(out.toString());
        System.out.println(vowels);
        """,
        [("the quick brown fox", "4\nquick\neht kciuq nworb xof\n5"),
         ("hello", "1\nhello\nolleh\n2"),
         ("a bb ccc", "3\nccc\na bb ccc\n1")],
        hint="StringBuilder.reverse() gives you each reversed word; count the vowels over the original line, spaces and all."),

    8: _java_exam(
        "Game of Life step",
        "The input is `r c` then an `r` x `c` grid of 0/1. Print the next generation: a live cell with 2 or 3 live neighbours survives, a dead cell with exactly 3 becomes alive, everything else dies. Rows are space-separated values.",
        """
        int r = sc.nextInt();
        int c = sc.nextInt();
        int[][] g = new int[r][c];
        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) g[i][j] = sc.nextInt();
        }
        int[][] next = new int[r][c];
        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) {
                int live = 0;
                for (int di = -1; di <= 1; di++) {
                    for (int dj = -1; dj <= 1; dj++) {
                        if (di == 0 && dj == 0) continue;
                        int ni = i + di;
                        int nj = j + dj;
                        if (ni < 0 || ni >= r || nj < 0 || nj >= c) continue;
                        live += g[ni][nj];
                    }
                }
                if (g[i][j] == 1) next[i][j] = (live == 2 || live == 3) ? 1 : 0;
                else next[i][j] = live == 3 ? 1 : 0;
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) {
                if (j > 0) sb.append(' ');
                sb.append(next[i][j]);
            }
            sb.append('\\n');
        }
        System.out.print(sb.toString());
        """,
        [("3 3\n0 1 0\n0 1 0\n0 1 0", "0 0 0\n1 1 1\n0 0 0"),
         ("2 2\n1 1\n1 1", "1 1\n1 1"),
         ("3 3\n0 0 0\n0 0 0\n0 0 0", "0 0 0\n0 0 0\n0 0 0"),
         ("1 3\n1 1 1", "0 1 0")],
        hint="Write into a SECOND grid — updating in place lets already-updated neighbours corrupt the count for later cells."),

    9: _java_exam(
        "Dutch national flag",
        "The input is `n` then `n` values, each 0, 1 or 2. Sort them in ONE pass with three pointers (no library sort) and print the result space-separated, then the count of each value as `zeros ones twos`.",
        """
        int n = sc.nextInt();
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        int low = 0;
        int mid = 0;
        int high = n - 1;
        while (mid <= high) {
            if (a[mid] == 0) {
                int t = a[low];
                a[low] = a[mid];
                a[mid] = t;
                low++;
                mid++;
            } else if (a[mid] == 2) {
                int t = a[high];
                a[high] = a[mid];
                a[mid] = t;
                high--;
            } else {
                mid++;
            }
        }
        StringBuilder sb = new StringBuilder();
        int[] counts = new int[3];
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(a[i]);
            counts[a[i]]++;
        }
        System.out.println(sb.toString());
        System.out.println(counts[0] + " " + counts[1] + " " + counts[2]);
        """,
        [("6\n2 0 1 2 1 0", "0 0 1 1 2 2\n2 2 2"),
         ("1\n1", "1\n0 1 0"),
         ("4\n2 2 2 2", "2 2 2 2\n0 0 4"),
         ("5\n0 1 2 0 1", "0 0 1 1 2\n2 2 1")],
        hint="Only advance mid when you swap a 0 forward or see a 1 — after swapping a 2 back, the newly arrived value has not been examined yet."),

    10: _java_exam(
        "Window report",
        "The input is `n k` then `n` integers. For every window of `k` consecutive values print `max min sum` on its own line, then the largest window sum on the final line.",
        """
        int n = sc.nextInt();
        int k = sc.nextInt();
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        StringBuilder sb = new StringBuilder();
        long best = Long.MIN_VALUE;
        for (int start = 0; start + k <= n; start++) {
            int max = a[start];
            int min = a[start];
            long sum = 0;
            for (int i = start; i < start + k; i++) {
                if (a[i] > max) max = a[i];
                if (a[i] < min) min = a[i];
                sum += a[i];
            }
            sb.append(max).append(' ').append(min).append(' ').append(sum).append('\\n');
            if (sum > best) best = sum;
        }
        System.out.print(sb.toString());
        System.out.println(best);
        """,
        [("5 3\n1 2 3 4 5", "3 1 6\n4 2 9\n5 3 12\n12"),
         ("3 3\n7 7 7", "7 7 21\n21"),
         ("4 2\n-1 -2 -3 -4", "-1 -2 -3\n-2 -3 -5\n-3 -4 -7\n-3"),
         ("1 1\n9", "9 9 9\n9")],
        hint="Seed best with Long.MIN_VALUE so an all-negative array reports the real maximum rather than 0."),

    11: _java_exam(
        "Range sum queries",
        "The input is `n q`, then `n` integers, then `q` lines of `l r` (0-indexed, inclusive). Build a prefix-sum array once and answer each query in O(1), one per line. Finish with the largest answer.",
        """
        int n = sc.nextInt();
        int q = sc.nextInt();
        long[] pre = new long[n + 1];
        for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + sc.nextInt();
        StringBuilder sb = new StringBuilder();
        long best = Long.MIN_VALUE;
        for (int i = 0; i < q; i++) {
            int l = sc.nextInt();
            int r = sc.nextInt();
            long sum = pre[r + 1] - pre[l];
            sb.append(sum).append('\\n');
            if (sum > best) best = sum;
        }
        System.out.print(sb.toString());
        System.out.println(best);
        """,
        [("5 3\n1 2 3 4 5\n0 4\n1 3\n2 2", "15\n9\n3\n15"),
         ("4 2\n-1 -2 -3 -4\n0 1\n2 3", "-3\n-7\n-3"),
         ("1 1\n42\n0 0", "42\n42"),
         ("6 2\n1 1 1 1 1 1\n0 5\n3 4", "6\n2\n6")],
        hint="The extra leading zero in the prefix array is what lets l = 0 work with no special case."),

    12: _java_exam(
        "Inverted index",
        "The input is `n` then `n` lines of `document word word ...`, then a final line of query words. For each query print `word: doc1 doc2` with the documents in first-appearance order, or `word: -` when the word was never seen.",
        """
        int n = sc.nextInt();
        sc.nextLine();
        LinkedHashMap<String, List<String>> index = new LinkedHashMap<>();
        for (int i = 0; i < n; i++) {
            String[] parts = sc.nextLine().trim().split("\\\\s+");
            String doc = parts[0];
            for (int j = 1; j < parts.length; j++) {
                List<String> docs = index.computeIfAbsent(parts[j], k -> new ArrayList<>());
                if (!docs.contains(doc)) docs.add(doc);
            }
        }
        StringBuilder sb = new StringBuilder();
        for (String query : sc.nextLine().trim().split("\\\\s+")) {
            List<String> docs = index.get(query);
            sb.append(query).append(": ");
            if (docs == null) sb.append('-');
            else sb.append(String.join(" ", docs));
            sb.append('\\n');
        }
        System.out.print(sb.toString());
        """,
        [("2\nd1 cat dog\nd2 dog bird\ndog cat fish", "dog: d1 d2\ncat: d1\nfish: -"),
         ("1\na x\nx", "x: a"),
         ("2\nd1 k\nd2 k\nk", "k: d1 d2")],
        hint="Call sc.nextLine() once after nextInt() to consume the rest of that line, or the first readLine comes back empty."),

    13: _java_exam(
        "Checkpoint: word frequency report",
        "The input is a line of words. Print the three most frequent as `word=count`, one per line, ties broken alphabetically, then the number of distinct words and the total word count separated by a space.",
        """
        String[] words = sc.nextLine().trim().split("\\\\s+");
        HashMap<String, Integer> counts = new HashMap<>();
        for (String w : words) counts.merge(w, 1, Integer::sum);
        List<Map.Entry<String, Integer>> ranked = new ArrayList<>(counts.entrySet());
        ranked.sort((a, b) -> b.getValue().equals(a.getValue())
                ? a.getKey().compareTo(b.getKey())
                : b.getValue() - a.getValue());
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < Math.min(3, ranked.size()); i++) {
            sb.append(ranked.get(i).getKey()).append('=').append(ranked.get(i).getValue()).append('\\n');
        }
        System.out.print(sb.toString());
        System.out.println(counts.size() + " " + words.length);
        """,
        [("a b a c b a", "a=3\nb=2\nc=1\n3 6"),
         ("solo", "solo=1\n1 1"),
         ("x y", "x=1\ny=1\n2 2"),
         ("z z y y x", "y=2\nz=2\nx=1\n3 5")],
        hint="merge(w, 1, Integer::sum) is the compact counting idiom; sort the entry list by count descending with an alphabetical tie-break."),
}




JAVA_WEEKS += [
    # =======================================================================
    # MONTH 4 — Data structures
    # =======================================================================
    _w(14, "Month 4 · Data structures",
       "Stacks",
       "Use LIFO order to match, undo, and find the next greater thing.",
       ["stack"],
       [("valid-parentheses", "The canonical matching problem."),
        ("min-stack", "An auxiliary stack carrying an invariant."),
        ("next-greater-element", "The monotonic stack."),
        ("daily-temperatures", "The same pattern over distances.")],
       "Write a `Rpn.java` evaluating a reverse-Polish expression from stdin, reporting `error` on a malformed one rather than crashing.",
       [("Which Java type should you use as a stack?",
         ["ArrayDeque, via push/pop/peek",
          "java.util.Stack",
          "LinkedList only",
          "ArrayList with remove(0)"], 0,
         "`Stack` extends Vector and is synchronised legacy code; `ArrayDeque` is the modern, faster choice — and `remove(0)` on an ArrayList is O(n)."),
        ("What makes a stack monotonic?",
         ["You pop before pushing so the contents stay sorted in one direction",
          "It stores only distinct values",
          "It is backed by a sorted array",
          "It never pops"], 0,
         "Popping everything the new element dominates is what makes 'next greater element' linear overall — each element is pushed and popped at most once."),
        ("Why does min-stack need a second stack rather than a single min variable?",
         ["Popping the current minimum has to restore the previous one",
          "For thread safety",
          "To keep push O(1)",
          "It does not"], 0,
         "A lone variable cannot recover the old minimum after a pop. Storing the running minimum alongside each element keeps every operation O(1).")]),

    _w(15, "Month 4 · Data structures",
       "Queues & Designed Structures",
       "FIFO order, and building a data structure to a stated interface.",
       ["queue", "design_ds"],
       [("implement-queue-stacks", "One structure built from another."),
        ("implement-stack-queues", "The mirror image."),
        ("design-circular-queue", "Fixed capacity with wrap-around indices."),
        ("lru-cache", "Two structures kept in step."),
        ("design-hashmap", "Buckets from scratch.")],
       "Write a `RingBuffer.java` with a fixed capacity that overwrites the oldest entry when full, plus a `toString` listing contents oldest-first.",
       [("Why is `ArrayList.remove(0)` a poor queue dequeue?",
         ["It shifts every remaining element, making it O(n)",
          "It throws on an empty list",
          "It returns the wrong element",
          "It is fine"], 0,
         "`ArrayDeque.pollFirst()` is O(1). Using a list as a queue is a classic accidental O(n²)."),
        ("What does LRU need in order to be O(1) for both get and put?",
         ["A hash map for lookup plus a doubly-linked list for recency order",
          "A single TreeMap",
          "A priority queue keyed by timestamp",
          "An ArrayList of keys"], 0,
         "The map finds the node; the linked list moves it to the front without a scan. `LinkedHashMap` with access order bundles both."),
        ("In a circular queue, how do you distinguish full from empty?",
         ["Keep an explicit size (or leave one slot unused)",
          "Compare head and tail only",
          "Check for null entries",
          "It cannot be distinguished"], 0,
         "head == tail is ambiguous on its own — it holds for both states, which is why a size counter is the usual fix.")]),

    _w(16, "Month 4 · Data structures",
       "Heaps & Priority Queues",
       "Always know the current extreme — including with two heaps at once.",
       ["heap", "top_k", "two_heaps", "heap_greedy"],
       [("kth-largest-element", "A size-k heap."),
        ("top-k-frequent", "Counting, then a heap."),
        ("last-stone-weight", "Repeated extremes."),
        ("median-from-stream", "Two heaps kept balanced."),
        ("min-meeting-rooms", "Greedy with the earliest-finishing room.")],
       "Write a `Huffman.java` that reads weights, repeatedly merges the two smallest, and prints the total merge cost plus the number of merges.",
       [("What order does Java's `PriorityQueue` use by default?",
         ["Natural order — it is a MIN-heap",
          "Reverse order — a max-heap",
          "Insertion order",
          "Undefined"], 0,
         "`new PriorityQueue<>(Collections.reverseOrder())` gives a max-heap. Getting this backwards is the single most common heap bug."),
        ("To keep the k LARGEST elements, which heap do you maintain?",
         ["A min-heap of size k, polling whenever it grows past k",
          "A max-heap of size k",
          "A min-heap of size n",
          "A max-heap of size n"], 0,
         "The min-heap's root is the weakest survivor, so it is exactly the one to evict — O(n log k) instead of O(n log n)."),
        ("Does iterating a `PriorityQueue` give sorted order?",
         ["No — only poll() respects the ordering",
          "Yes, always",
          "Yes, but only for primitives",
          "Only after calling sort()"], 0,
         "The backing array is heap-ordered, not sorted. Printing a PriorityQueue directly is a routine source of confusing output.")]),

    _w(17, "Month 4 · Data structures",
       "Tries",
       "Share prefixes so lookup costs the length of the word, not the size of the dictionary.",
       ["trie"],
       [("implement-trie-ops", "Insert, search, startsWith."),
        ("longest-common-prefix-strs", "The degenerate one-path case."),
        ("replace-words-roots", "Walk until a root matches."),
        ("longest-buildable-word", "Only words whose prefixes are all present."),
        ("word-dictionary-wildcard", "Branching search over the trie.")],
       "Write an `Autocomplete.java` that loads a dictionary, then for each query prints the first five completions in alphabetical order.",
       [("What does a trie cost to look up a word of length L?",
         ["O(L), independent of how many words are stored",
          "O(log n) in the dictionary size",
          "O(n) in the dictionary size",
          "O(L log n)"], 0,
         "That independence from dictionary size is the whole point, and why tries beat hash sets for prefix queries."),
        ("Why does a trie node need an `isWord` flag?",
         ["To distinguish a stored word from a mere prefix of longer words",
          "To mark the root",
          "To count children",
          "To support deletion only"], 0,
         "Without it, storing \"cars\" would make \"car\" appear to be in the dictionary."),
        ("What is the main cost of a trie over a hash set?",
         ["Memory — a node per character, each with child pointers",
          "Slower exact lookup",
          "It cannot store duplicates",
          "It requires sorted input"], 0,
         "A 26-way array per node is fast but wasteful; a HashMap per node trades some speed for much less memory on sparse dictionaries.")]),

    _w(18, "Month 4 · Data structures",
       "Linked Lists",
       "Pointer surgery: reverse, find the middle, detect a cycle.",
       ["list_basics", "list_reversal", "fast_slow"],
       [("list-length", "Walk to the end."),
        ("reverse-linked-list", "The three-pointer walk."),
        ("middle-of-list", "Fast and slow in one pass."),
        ("has-cycle", "Floyd's algorithm."),
        ("merge-two-sorted-lists", "Two cursors and a dummy head."),
        ("remove-nth-from-end", "A gap between two pointers.")],
       "Write a `Palindrome.java` that decides whether a linked list reads the same forwards and backwards in O(n) time and O(1) extra space.",
       [("In `reverse`, why must you save `curr.next` before reassigning it?",
         ["Overwriting it first loses the rest of the list",
          "To keep the list sorted",
          "For the null check",
          "You do not have to"], 0,
         "The saved `next` is the only remaining handle on the untouched tail. When curr falls off the end, prev is the new head."),
        ("Why does a dummy head node simplify list building?",
         ["It removes the special case for inserting the very first node",
          "It makes the list circular",
          "It stores the length",
          "It speeds up traversal"], 0,
         "You always append after a real node, then return `dummy.next` — no branch for the empty case."),
        ("Why do fast and slow pointers meet inside a cycle?",
         ["The gap closes by one each step, so the faster one must catch up",
          "They start at the same node",
          "The cycle length is always even",
          "They do not always meet"], 0,
         "Once both are inside the loop the distance shrinks by exactly one per step, so a meeting is guaranteed.")]),

    # =======================================================================
    # MONTH 5 — Trees, sorting & search
    # =======================================================================
    _w(19, "Month 5 · Trees, sorting & search",
        "Binary Trees & Traversals",
        "Recurse over structure, and know what each traversal order gives you.",
        ["tree_basics", "tree_traversal"],
        [("max-depth-tree", "The simplest recursion on a tree."),
         ("count-nodes-tree", "Aggregate over both subtrees."),
         ("inorder-traversal", "Left, node, right."),
         ("level-order-traversal", "BFS with a queue."),
         ("invert-binary-tree", "Structural mutation."),
         ("symmetric-tree", "Two cursors descending in mirror.")],
        "Write a `Serialize.java` that prints a tree in preorder with `#` for null, then rebuilds it from that string and prints its inorder to prove the round trip.",
        [("Which traversal of a BST produces sorted order?",
          ["Inorder", "Preorder", "Postorder", "Level order"], 0,
          "Left subtree, node, right subtree visits keys in ascending order — the property behind kth-smallest and BST validation."),
         ("Why is postorder the right shape for 'compute something from both subtrees'?",
          ["Both children are fully processed before the node combines them",
           "It visits fewer nodes",
           "It is iterative by nature",
           "It works only on balanced trees"], 0,
          "Height, diameter and subtree sums are all postorder aggregations — the node's answer needs its children's answers first."),
         ("What does level-order need that depth-first traversals do not?",
          ["A queue", "A stack", "Recursion", "A visited set"], 0,
          "BFS is queue-driven. Processing a whole level at a time means recording the queue size before draining it.")]),

    _w(20, "Month 5 · Trees, sorting & search",
        "BSTs & Tree DP",
        "Exploit ordering, and aggregate answers upward through a tree.",
        ["bst", "tree_dp"],
        [("bst-search", "Ordering turns search into a descent."),
         ("validate-bst", "Bounds passed down, not just child comparisons."),
         ("lca-bst", "Ordering makes the ancestor obvious."),
         ("kth-smallest-bst", "Inorder with a counter."),
         ("diameter-of-tree", "A postorder aggregation."),
         ("max-path-sum", "The hardest version of the same shape.")],
        "Write a `BstRange.java` that reads a BST and a range `lo hi` and prints the sum of all keys inside it, pruning subtrees that cannot contribute.",
        [("Why is comparing each node only against its children NOT enough to validate a BST?",
          ["A deep descendant can violate a distant ancestor's bound",
           "Children may be null",
           "Duplicates are allowed",
           "It is enough"], 0,
          "Pass a (low, high) range down and tighten it at each step — the local check misses violations one level further away."),
         ("What does a tree-DP function typically return?",
          ["Its subtree's answer, while updating a global best on the way up",
           "Only a boolean",
           "The node's depth",
           "Nothing; it mutates the tree"], 0,
          "Diameter and max-path-sum both do this: return the best downward path, but combine both sides into the global answer at each node."),
         ("What is the worst-case height of an unbalanced BST with n nodes?",
          ["n, when the keys arrive already sorted",
           "log n always",
           "sqrt(n)",
           "n / 2"], 0,
          "Sorted insertion degenerates the tree into a linked list, which is why self-balancing trees (Java's TreeMap uses a red-black tree) exist.")]),

    _w(21, "Month 5 · Trees, sorting & search",
        "Sorting & Binary Search",
        "Order the data, then exploit that order.",
        ["sorting", "binary_search"],
        [("kth-smallest", "Sort, then index."),
         ("sort-by-frequency", "A comparator with a tie-break."),
         ("binary-search-first", "The lower-bound form."),
         ("search-insert-position", "Where it WOULD go."),
         ("integer-sqrt", "Binary search on the answer, not the array."),
         ("mountain-array", "Search a shape rather than a value.")],
        "Write a `Bounds.java` implementing lowerBound and upperBound over a sorted array with duplicates, and print how many times a target occurs.",
        [("Why write `mid = lo + (hi - lo) / 2` instead of `(lo + hi) / 2`?",
          ["The naive form can overflow int for large indices",
           "It is faster",
           "It rounds differently",
           "It handles empty ranges"], 0,
          "A famous bug that sat in the JDK's own binarySearch for years."),
         ("For a lower bound, why is the update `hi = mid` rather than `hi = mid - 1`?",
          ["mid itself may be the answer, so it must stay in the range",
           "To avoid an infinite loop",
           "Because the range is inclusive",
           "It should be mid - 1"], 0,
          "Half-open `[lo, hi)` with `hi = mid` is the form that reliably finds the FIRST qualifying element."),
         ("What does `Arrays.sort` use for an object array?",
          ["A stable TimSort", "Dual-pivot quicksort", "Heap sort", "Counting sort"], 0,
          "Objects get stability (equal elements keep their relative order); primitives get quicksort, where stability is meaningless.")]),

    _w(22, "Month 5 · Trees, sorting & search",
        "Greedy & Intervals",
        "When does taking the locally best choice actually give the global optimum?",
        ["greedy", "intervals"],
        [("jump-game", "Track the furthest reachable index."),
         ("merge-intervals", "Sort by start, then fold."),
         ("non-overlapping-remove", "Sort by END — the classic surprise."),
         ("min-arrows-balloons", "The same shape as interval scheduling."),
         ("can-attend-meetings", "The simplest overlap check."),
         ("insert-interval", "Merging into an already-sorted set.")],
        "Write a `Schedule.java` that reads meetings and prints the largest number that can be attended without overlap, plus which ones.",
        [("For maximum non-overlapping intervals, what do you sort by?",
          ["End time — finishing earliest leaves the most room",
           "Start time",
           "Duration",
           "Start time descending"], 0,
          "Sorting by start solves MERGING; sorting by end solves SELECTION. Mixing them up is the classic interval mistake."),
         ("What must be true for a greedy algorithm to be correct?",
          ["The locally optimal choice is always part of some global optimum",
           "The input is sorted",
           "There are no duplicates",
           "It runs in O(n log n)"], 0,
          "This is the exchange-argument property. Without it — coin change with arbitrary denominations, for instance — greedy silently returns a worse answer."),
         ("Two intervals overlap when…",
          ["a.start <= b.end && b.start <= a.end",
           "a.start < b.start",
           "a.end == b.start",
           "They share an endpoint"], 0,
          "Whether touching endpoints count as overlapping is a per-problem decision — read the statement rather than assuming.")]),

    # =======================================================================
    # MONTH 6 — Recursion, DP & graphs
    # =======================================================================
    _w(23, "Month 6 · Recursion, DP & graphs",
        "Grids & Flood Fill",
        "Treat a grid as a graph and explore its connected regions.",
        ["grid", "flood_fill"],
        [("number-of-islands", "The canonical flood fill."),
         ("territory-capture", "Filling from the border inward."),
         ("color-bomb-explosion", "Region replacement."),
         ("spiral-order", "Pure index discipline."),
         ("set-matrix-zeroes", "In-place marking."),
         ("shortest-path-binary-matrix", "BFS on a grid.")],
        "Write a `Regions.java` that reads a character grid and prints the number of regions and the size of the largest, treating equal adjacent characters as connected.",
        [("Why mark a cell visited as you ENQUEUE it rather than when you dequeue it?",
          ["Otherwise the same cell can be enqueued several times before processing",
           "Dequeuing is slower",
           "It changes the traversal order",
           "There is no difference"], 0,
          "Marking on dequeue lets duplicates pile up in the queue, which can blow up the memory and the running time."),
         ("Why is a recursive flood fill risky on a large grid?",
          ["The recursion depth can equal the number of cells and overflow the stack",
           "It gives the wrong answer",
           "It cannot handle diagonals",
           "It is slower asymptotically"], 0,
          "An explicit stack or a BFS queue has the same complexity without depending on the JVM's stack size."),
         ("What is a common trick to avoid a separate visited array?",
          ["Overwrite each visited cell with a sentinel value in the grid itself",
           "Use a HashSet of coordinates, which is always faster",
           "Sort the grid first",
           "Traverse twice"], 0,
          "It saves memory and is fine when the grid may be mutated — otherwise copy first or use a boolean array.")]),

    _w(24, "Month 6 · Recursion, DP & graphs",
        "Recursion, Backtracking & Pruning",
        "Explore a decision tree, undo cleanly, and cut branches that cannot win.",
        ["recursion", "recurrence", "backtracking", "pruning"],
        [("generate-subsets", "Take-or-skip at each element."),
         ("generate-permutations", "Choose, recurse, undo."),
         ("combination-sum-count", "Repetition allowed."),
         ("letter-combinations-phone", "A product of choices."),
         ("word-search", "Backtracking over a grid."),
         ("n-queens-count", "Where pruning stops being optional.")],
        "Write a `Sudoku.java` that reads a 9x9 grid and reports whether it is solvable, using constraint checks to prune before recursing.",
        [("What distinguishes backtracking from plain recursion?",
          ["It UNDOES its choice after recursing, so siblings see a clean state",
           "It is always iterative",
           "It uses memoisation",
           "It never revisits a state"], 0,
          "The undo step is the definition. Forgetting it is why the second branch of a search returns nonsense."),
         ("Why does naive recursive Fibonacci take exponential time?",
          ["The same subproblems are recomputed along different branches",
           "Recursion is inherently slow",
           "The stack depth is exponential",
           "It does not"], 0,
          "Memoising collapses it to linear. Recognising overlapping subproblems is the step from recursion to dynamic programming."),
         ("What is the point of a pruning check?",
          ["Abandon a branch as soon as it cannot possibly lead to a solution",
           "Reduce the recursion depth",
           "Make the search iterative",
           "Sort the candidates"], 0,
          "It does not change the worst case, but on real inputs it is often the difference between milliseconds and never finishing.")]),

    _w(25, "Month 6 · Recursion, DP & graphs",
        "Dynamic Programming & Complexity",
        "Find the state, write the recurrence, then decide top-down or bottom-up.",
        ["dp", "dp2d", "big_o"],
        [("climbing-stairs", "The smallest recurrence."),
         ("house-robber", "Two rolling states."),
         ("coin-change", "Unbounded choice."),
         ("unique-paths", "A 2-D table."),
         ("longest-common-subsequence", "The classic 2-D DP."),
         ("edit-distance", "Three transitions per cell.")],
        "Write a `Knapsack.java` solving 0/1 knapsack bottom-up, printing the best value and the chosen items, with the table reduced to one dimension.",
        [("What are the two ingredients of a dynamic-programming solution?",
          ["Overlapping subproblems and optimal substructure",
           "Sorting and binary search",
           "A greedy choice and a tie-break",
           "Recursion and a visited set"], 0,
          "Without overlap, memoising buys nothing; without optimal substructure, combining subproblem answers is simply invalid."),
         ("What is the difference between memoisation and tabulation?",
          ["Memoisation is top-down and computes only the states it needs; tabulation is bottom-up and fills them all",
           "Memoisation is always faster",
           "Tabulation uses recursion",
           "They give different answers"], 0,
          "Top-down is usually easier to derive from the recurrence; bottom-up avoids stack depth and makes rolling-array space savings obvious."),
         ("`for (int i = 0; i < n; i++) for (int j = i; j < n; j++)` — what is the complexity?",
          ["O(n²) — roughly n²/2 iterations, and constants are dropped",
           "O(n)",
           "O(n log n)",
           "O(n² log n)"], 0,
          "Half of a quadratic is still quadratic. Big-O describes the growth rate, not the constant factor.")]),

    _w(26, "Month 6 · Recursion, DP & graphs",
        "Graphs & Capstone",
        "Represent a graph, traverse it, order it, connect it, and weight it.",
        ["graph_repr", "bfs", "indegree", "topo", "graph_cycle",
         "union_find", "dijkstra", "bellman_ford", "mst"],
        [("number-of-provinces", "Connectivity, two ways."),
         ("course-schedule", "Topological order and cycles."),
         ("count-components", "Union-find or DFS."),
         ("dijkstra-shortest-path", "Weighted shortest paths."),
         ("mst-total-weight", "Kruskal with union-find."),
         ("word-ladder-length", "BFS over an implicit graph.")],
        "Capstone: write a `Network.java` that reads a weighted graph and reports whether it is connected, its MST weight, the shortest path between two nodes, and whether it contains a cycle — one program, four algorithms.",
        [("When is BFS the right choice over DFS for shortest paths?",
          ["On unweighted graphs, where the first arrival is already the shortest",
           "Always",
           "Only on trees",
           "When the graph is weighted"], 0,
          "With weights you need Dijkstra (non-negative) or Bellman-Ford (negatives allowed) — BFS's guarantee depends on every edge costing the same."),
         ("What does Kahn's algorithm placing fewer than n vertices tell you?",
          ["The graph contains a directed cycle",
           "The graph is disconnected",
           "The input had duplicate edges",
           "Nothing"], 0,
          "Anything left with a non-zero in-degree is trapped in a cycle — which is why the same routine answers both 'topological order' and 'is it acyclic'."),
         ("Why can Dijkstra fail on negative edge weights?",
          ["It finalises a node on first extraction, which a later negative edge could improve",
           "The priority queue cannot hold negatives",
           "It loops forever",
           "It cannot — Dijkstra handles them"], 0,
          "Bellman-Ford relaxes every edge n-1 times instead, which is slower but tolerates negatives and detects negative cycles.")]),
]


JAVA_EXAMS.update({
    14: _java_exam(
        "Reverse-Polish calculator",
        "The input is one line of space-separated RPN tokens (integers and the operators `+ - * /`). Print the result, or `error` if the expression is malformed (too few operands, leftover operands, or division by zero).",
        """
        String[] tokens = sc.nextLine().trim().split("\\\\s+");
        ArrayDeque<Long> stack = new ArrayDeque<>();
        boolean ok = true;
        for (String t : tokens) {
            if (t.equals("+") || t.equals("-") || t.equals("*") || t.equals("/")) {
                if (stack.size() < 2) {
                    ok = false;
                    break;
                }
                long b = stack.pop();
                long a = stack.pop();
                if (t.equals("/") && b == 0) {
                    ok = false;
                    break;
                }
                if (t.equals("+")) stack.push(a + b);
                else if (t.equals("-")) stack.push(a - b);
                else if (t.equals("*")) stack.push(a * b);
                else stack.push(a / b);
            } else {
                stack.push(Long.parseLong(t));
            }
        }
        if (!ok || stack.size() != 1) System.out.println("error");
        else System.out.println(stack.pop());
        """,
        [("3 4 +", "7"), ("5 1 2 + 4 * + 3 -", "14"),
         ("1 +", "error"), ("1 2", "error"), ("4 0 /", "error"),
         ("6 2 /", "3")],
        hint="Pop the RIGHT operand first — `a - b` with the pops in the wrong order silently computes b - a."),

    15: _java_exam(
        "Ring buffer",
        "The input is `capacity n` then `n` values. Push each into a fixed-capacity buffer that drops the oldest once full. Print the contents oldest-first space-separated (or `(empty)`), then the size, then whether it is full.",
        """
        int capacity = sc.nextInt();
        int n = sc.nextInt();
        ArrayDeque<Integer> buffer = new ArrayDeque<>();
        for (int i = 0; i < n; i++) {
            buffer.addLast(sc.nextInt());
            if (buffer.size() > capacity) buffer.pollFirst();
        }
        StringBuilder sb = new StringBuilder();
        for (int v : buffer) {
            if (sb.length() > 0) sb.append(' ');
            sb.append(v);
        }
        System.out.println(sb.length() == 0 ? "(empty)" : sb.toString());
        System.out.println(buffer.size());
        System.out.println(buffer.size() == capacity);
        """,
        [("3 5\n1 2 3 4 5", "3 4 5\n3\ntrue"),
         ("5 2\n7 8", "7 8\n2\nfalse"),
         ("1 3\n1 2 3", "3\n1\ntrue"),
         ("2 0", "(empty)\n0\nfalse")],
        hint="addLast then trim from the front — iterating an ArrayDeque walks it front-to-back, which is oldest-first."),

    16: _java_exam(
        "Huffman merge cost",
        "The input is `n` then `n` positive weights. Repeatedly remove the two smallest, push back their sum, and charge that sum — until one remains. Print the total cost, then the number of merges performed.",
        """
        int n = sc.nextInt();
        PriorityQueue<Long> pq = new PriorityQueue<>();
        for (int i = 0; i < n; i++) pq.add(sc.nextLong());
        long cost = 0;
        int merges = 0;
        while (pq.size() > 1) {
            long a = pq.poll();
            long b = pq.poll();
            cost += a + b;
            pq.add(a + b);
            merges++;
        }
        System.out.println(cost);
        System.out.println(merges);
        """,
        [("4\n1 2 3 4", "19\n3"), ("1\n7", "0\n0"),
         ("2\n5 5", "10\n1"), ("5\n4 3 2 6 1", "35\n4")],
        hint="A PriorityQueue<Long> is a min-heap, so poll() hands you the smallest. n items always take n-1 merges."),

    17: _java_exam(
        "Autocomplete",
        "The input is `n` then `n` dictionary words, then `q` then `q` prefixes. For each prefix print up to five completions in alphabetical order, space-separated, or `(none)`.",
        """
        int n = sc.nextInt();
        List<String> words = new ArrayList<>();
        for (int i = 0; i < n; i++) words.add(sc.next());
        Collections.sort(words);
        int q = sc.nextInt();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < q; i++) {
            String prefix = sc.next();
            List<String> hits = new ArrayList<>();
            for (String w : words) {
                if (w.startsWith(prefix)) hits.add(w);
                if (hits.size() == 5) break;
            }
            sb.append(hits.isEmpty() ? "(none)" : String.join(" ", hits)).append('\\n');
        }
        System.out.print(sb.toString());
        """,
        [("4\ncar cat dog cart\n2\nca do", "car cart cat\ndog"),
         ("3\na ab abc\n1\nab", "ab abc"),
         ("2\nxy yz\n1\nq", "(none)"),
         ("6\naa ab ac ad ae af\n1\na", "aa ab ac ad ae")],
        hint="Sorting once up front means the first five matches you find are already the alphabetically first five."),

    18: _java_exam_cls(
        "Linked list palindrome",
        "The input is `n` then `n` values forming a linked list. Print `true` if the values read the same forwards and backwards, using O(1) extra space: find the middle with fast/slow, reverse the second half, then compare. Print the list's length on the second line.",
        """
    static class Node {
        int val;
        Node next;
        Node(int val) { this.val = val; }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        Node head = null;
        Node tail = null;
        for (int i = 0; i < n; i++) {
            Node node = new Node(sc.nextInt());
            if (head == null) head = node;
            else tail.next = node;
            tail = node;
        }
        Node slow = head;
        Node fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        Node prev = null;
        Node curr = slow;
        while (curr != null) {
            Node next = curr.next;
            curr.next = prev;
            prev = curr;
            curr = next;
        }
        boolean palindrome = true;
        Node left = head;
        Node right = prev;
        while (right != null && left != null) {
            if (left.val != right.val) {
                palindrome = false;
                break;
            }
            left = left.next;
            right = right.next;
        }
        System.out.println(palindrome);
        System.out.println(n);
    }
""",
        """
        Node slow = head;
        Node fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        Node prev = null;
        Node curr = slow;
        while (curr != null) {
            Node next = curr.next;
            curr.next = prev;
            prev = curr;
            curr = next;
        }
        boolean palindrome = true;
        Node left = head;
        Node right = prev;
        while (right != null && left != null) {
            if (left.val != right.val) {
                palindrome = false;
                break;
            }
            left = left.next;
            right = right.next;
        }
        System.out.println(palindrome);
        System.out.println(n);
""",
        [("5\n1 2 3 2 1", "true\n5"), ("4\n1 2 2 1", "true\n4"),
         ("3\n1 2 3", "false\n3"), ("1\n9", "true\n1"),
         ("2\n4 4", "true\n2")],
        hint="Reverse from the slow pointer onward; comparing until the reversed half runs out handles both odd and even lengths."),

    19: _java_exam_cls(
        "Serialize and rebuild a tree",
        "The input is `n` then `n` level-order values with `-1` for a missing node. Print the tree's preorder with `#` for null (space-separated), then its inorder (real values only, space-separated).",
        """
    static int[] a;
    static StringBuilder pre = new StringBuilder();
    static StringBuilder ino = new StringBuilder();

    static void preorder(int i) {
        if (i >= a.length || a[i] == -1) {
            if (pre.length() > 0) pre.append(' ');
            pre.append('#');
            return;
        }
        if (pre.length() > 0) pre.append(' ');
        pre.append(a[i]);
        preorder(2 * i + 1);
        preorder(2 * i + 2);
    }

    static void inorder(int i) {
        if (i >= a.length || a[i] == -1) return;
        inorder(2 * i + 1);
        if (ino.length() > 0) ino.append(' ');
        ino.append(a[i]);
        inorder(2 * i + 2);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        preorder(0);
        inorder(0);
        System.out.println(pre.toString());
        System.out.println(ino.toString());
    }
""",
        """
    static void preorder(int i) {
        if (i >= a.length || a[i] == -1) {
            if (pre.length() > 0) pre.append(' ');
            pre.append('#');
            return;
        }
        if (pre.length() > 0) pre.append(' ');
        pre.append(a[i]);
        preorder(2 * i + 1);
        preorder(2 * i + 2);
    }

    static void inorder(int i) {
        if (i >= a.length || a[i] == -1) return;
        inorder(2 * i + 1);
        if (ino.length() > 0) ino.append(' ');
        ino.append(a[i]);
        inorder(2 * i + 2);
    }
""",
        [("3\n2 1 3", "2 1 # # 3 # #\n1 2 3"),
         ("1\n5", "5 # #\n5"),
         ("7\n1 2 3 4 5 6 7", "1 2 4 # # 5 # # 3 6 # # 7 # #\n4 2 5 1 6 3 7")],
        hint="Preorder emits the node then both children, so a null slot still contributes a `#`. Inorder skips nulls entirely."),

    20: _java_exam_cls(
        "BST range sum",
        "The input is `n`, then `n` level-order values with `-1` for a missing node (values are positive and form a valid BST), then `lo hi`. Print the sum of every key in `[lo, hi]`, then how many keys were in range — pruning subtrees that cannot contribute.",
        """
    static int[] a;
    static int lo;
    static int hi;
    static long sum = 0;
    static int count = 0;

    static void walk(int i) {
        if (i >= a.length || a[i] == -1) return;
        int v = a[i];
        if (v > lo) walk(2 * i + 1);
        if (v >= lo && v <= hi) {
            sum += v;
            count++;
        }
        if (v < hi) walk(2 * i + 2);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        lo = sc.nextInt();
        hi = sc.nextInt();
        walk(0);
        System.out.println(sum);
        System.out.println(count);
    }
""",
        """
    static void walk(int i) {
        if (i >= a.length || a[i] == -1) return;
        int v = a[i];
        if (v > lo) walk(2 * i + 1);
        if (v >= lo && v <= hi) {
            sum += v;
            count++;
        }
        if (v < hi) walk(2 * i + 2);
    }
""",
        [("7\n8 4 12 2 6 10 14\n5 12", "36\n4"),
         ("3\n2 1 3\n1 3", "6\n3"),
         ("1\n5\n6 10", "0\n0"),
         ("7\n8 4 12 2 6 10 14\n8 8", "8\n1")],
        hint="Only descend left when the node's key is above lo, and right when it is below hi — that is the pruning."),

    21: _java_exam(
        "Lower and upper bound",
        "The input is `n target` then `n` integers sorted ascending (duplicates allowed). Print the first index whose value is >= target, the first index whose value is > target, and how many times target occurs.",
        """
        int n = sc.nextInt();
        int target = sc.nextInt();
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        int lo = 0;
        int hi = n;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (a[mid] >= target) hi = mid;
            else lo = mid + 1;
        }
        int lower = lo;
        lo = 0;
        hi = n;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (a[mid] > target) hi = mid;
            else lo = mid + 1;
        }
        int upper = lo;
        System.out.println(lower);
        System.out.println(upper);
        System.out.println(upper - lower);
        """,
        [("6 3\n1 2 3 3 3 5", "2\n5\n3"),
         ("5 4\n1 2 3 5 6", "3\n3\n0"),
         ("4 1\n1 1 1 1", "0\n4\n4"),
         ("3 9\n1 2 3", "3\n3\n0")],
        hint="The two searches differ by one character: >= for the lower bound, > for the upper. Their gap is the occurrence count."),

    22: _java_exam(
        "Meeting schedule",
        "The input is `n` then `n` lines of `start end`. Print the largest number of meetings attendable without overlap, then their `start end` pairs one per line in the order chosen. A meeting starting exactly when another ends is fine.",
        """
        int n = sc.nextInt();
        int[][] m = new int[n][2];
        for (int i = 0; i < n; i++) {
            m[i][0] = sc.nextInt();
            m[i][1] = sc.nextInt();
        }
        Arrays.sort(m, (x, y) -> x[1] != y[1] ? Integer.compare(x[1], y[1]) : Integer.compare(x[0], y[0]));
        List<int[]> chosen = new ArrayList<>();
        int lastEnd = Integer.MIN_VALUE;
        for (int[] meeting : m) {
            if (meeting[0] >= lastEnd) {
                chosen.add(meeting);
                lastEnd = meeting[1];
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int[] meeting : chosen) sb.append(meeting[0]).append(' ').append(meeting[1]).append('\\n');
        System.out.println(chosen.size());
        System.out.print(sb.toString());
        """,
        [("3\n0 30\n5 10\n15 20", "2\n5 10\n15 20"),
         ("2\n1 4\n4 5", "2\n1 4\n4 5"),
         ("1\n1 5", "1\n1 5"),
         ("4\n1 4\n2 5\n3 6\n4 7", "2\n1 4\n4 7")],
        hint="Sort by END time — finishing earliest leaves the most room for what follows. Sorting by start solves a different problem."),

    23: _java_exam(
        "Count regions",
        "The input is `r c` then `r` rows of `c` characters (no spaces). Adjacent cells (up/down/left/right) holding the SAME character belong to one region. Print the number of regions, then the size of the largest.",
        """
        int r = sc.nextInt();
        int c = sc.nextInt();
        char[][] g = new char[r][];
        for (int i = 0; i < r; i++) g[i] = sc.next().toCharArray();
        boolean[][] seen = new boolean[r][c];
        int[] dr = {1, -1, 0, 0};
        int[] dc = {0, 0, 1, -1};
        int regions = 0;
        int largest = 0;
        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) {
                if (seen[i][j]) continue;
                regions++;
                char target = g[i][j];
                int size = 0;
                ArrayDeque<int[]> stack = new ArrayDeque<>();
                stack.push(new int[]{i, j});
                seen[i][j] = true;
                while (!stack.isEmpty()) {
                    int[] cur = stack.pop();
                    size++;
                    for (int d = 0; d < 4; d++) {
                        int ni = cur[0] + dr[d];
                        int nj = cur[1] + dc[d];
                        if (ni < 0 || ni >= r || nj < 0 || nj >= c) continue;
                        if (seen[ni][nj] || g[ni][nj] != target) continue;
                        seen[ni][nj] = true;
                        stack.push(new int[]{ni, nj});
                    }
                }
                if (size > largest) largest = size;
            }
        }
        System.out.println(regions);
        System.out.println(largest);
        """,
        [("3 3\naab\naab\nccb", "3\n4"),
         ("1 1\nx", "1\n1"),
         ("2 2\nab\nba", "4\n1"),
         ("2 3\naaa\naaa", "1\n6")],
        hint="Mark each cell seen as you PUSH it, not when you pop it, or the same cell enters the stack several times."),

    24: _java_exam_cls(
        "Sudoku solvable",
        "The input is 9 lines of 9 digits, `0` meaning empty. Print `true` if the puzzle can be completed legally and `false` otherwise, then the number of empty cells in the input. Reject an already-illegal board up front — searching one wastes the whole run.",
        """
    static int[][] g = new int[9][9];

    static boolean ok(int r, int c, int v) {
        for (int i = 0; i < 9; i++) {
            if (g[r][i] == v || g[i][c] == v) return false;
        }
        int br = r / 3 * 3;
        int bc = c / 3 * 3;
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                if (g[br + i][bc + j] == v) return false;
            }
        }
        return true;
    }

    static boolean givensAreLegal() {
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                int v = g[r][c];
                if (v == 0) continue;
                g[r][c] = 0;
                boolean fine = ok(r, c, v);
                g[r][c] = v;
                if (!fine) return false;
            }
        }
        return true;
    }

    static boolean solve(int pos) {
        if (pos == 81) return true;
        int r = pos / 9;
        int c = pos % 9;
        if (g[r][c] != 0) return solve(pos + 1);
        for (int v = 1; v <= 9; v++) {
            if (!ok(r, c, v)) continue;
            g[r][c] = v;
            if (solve(pos + 1)) return true;
            g[r][c] = 0;
        }
        return false;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int empty = 0;
        for (int i = 0; i < 9; i++) {
            String row = sc.next();
            for (int j = 0; j < 9; j++) {
                g[i][j] = row.charAt(j) - '0';
                if (g[i][j] == 0) empty++;
            }
        }
        System.out.println(givensAreLegal() && solve(0));
        System.out.println(empty);
    }
""",
        """
    static boolean ok(int r, int c, int v) {
        for (int i = 0; i < 9; i++) {
            if (g[r][i] == v || g[i][c] == v) return false;
        }
        int br = r / 3 * 3;
        int bc = c / 3 * 3;
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                if (g[br + i][bc + j] == v) return false;
            }
        }
        return true;
    }

    static boolean givensAreLegal() {
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                int v = g[r][c];
                if (v == 0) continue;
                g[r][c] = 0;
                boolean fine = ok(r, c, v);
                g[r][c] = v;
                if (!fine) return false;
            }
        }
        return true;
    }

    static boolean solve(int pos) {
        if (pos == 81) return true;
        int r = pos / 9;
        int c = pos % 9;
        if (g[r][c] != 0) return solve(pos + 1);
        for (int v = 1; v <= 9; v++) {
            if (!ok(r, c, v)) continue;
            g[r][c] = v;
            if (solve(pos + 1)) return true;
            g[r][c] = 0;
        }
        return false;
    }
""",
        [("534678912\n672195348\n198342567\n859761423\n426853791\n713924856\n961537284\n287419635\n345286179",
          "true\n0"),
         ("534678912\n672195348\n198342567\n859761423\n426853791\n713924856\n961537284\n287419635\n345286170",
          "true\n1"),
         ("110000000\n000000000\n000000000\n000000000\n000000000\n000000000\n000000000\n000000000\n000000000",
          "false\n79")],
        hint="Check the givens first — an illegal board has no solution, and searching for one takes effectively forever. Then undo each placement (`g[r][c] = 0`) when a branch fails."),

    25: _java_exam(
        "0/1 knapsack",
        "The input is `n capacity` then `n` lines of `weight value`. Print the best achievable value, then how much capacity it uses. Fill the table bottom-up with a single rolling row.",
        """
        int n = sc.nextInt();
        int capacity = sc.nextInt();
        int[] weight = new int[n];
        int[] value = new int[n];
        for (int i = 0; i < n; i++) {
            weight[i] = sc.nextInt();
            value[i] = sc.nextInt();
        }
        int[] best = new int[capacity + 1];
        for (int i = 0; i < n; i++) {
            for (int w = capacity; w >= weight[i]; w--) {
                best[w] = Math.max(best[w], best[w - weight[i]] + value[i]);
            }
        }
        int answer = best[capacity];
        int used = 0;
        for (int w = 0; w <= capacity; w++) {
            if (best[w] == answer) {
                used = w;
                break;
            }
        }
        System.out.println(answer);
        System.out.println(used);
        """,
        [("3 5\n2 3\n3 4\n4 5", "7\n5"),
         ("1 1\n2 9", "0\n0"),
         ("2 10\n5 10\n5 10", "20\n10"),
         ("3 4\n1 1\n2 2\n3 3", "4\n4")],
        hint="Iterate the capacity DOWNWARD so each item is used at most once — an ascending loop turns this into unbounded knapsack."),

    26: _java_exam(
        "Capstone: network report",
        "The input is `n m src dst` then `m` lines of `u v w` (undirected, non-negative weights). Print four lines: whether the graph is connected, the total weight of a minimum spanning tree (or `-1` if disconnected), the shortest distance from `src` to `dst` (or `-1`), and the number of connected components.",
        """
        int n = sc.nextInt();
        int m = sc.nextInt();
        int src = sc.nextInt();
        int dst = sc.nextInt();
        int[][] edges = new int[m][3];
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int i = 0; i < m; i++) {
            int u = sc.nextInt();
            int v = sc.nextInt();
            int w = sc.nextInt();
            edges[i][0] = u;
            edges[i][1] = v;
            edges[i][2] = w;
            adj.get(u).add(new int[]{v, w});
            adj.get(v).add(new int[]{u, w});
        }
        int[] parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        Arrays.sort(edges, (x, y) -> Integer.compare(x[2], y[2]));
        long mst = 0;
        int joined = 0;
        for (int[] e : edges) {
            int ra = e[0];
            while (parent[ra] != ra) ra = parent[ra];
            int rb = e[1];
            while (parent[rb] != rb) rb = parent[rb];
            if (ra == rb) continue;
            parent[rb] = ra;
            mst += e[2];
            joined++;
        }
        int components = 0;
        for (int i = 0; i < n; i++) {
            int r = i;
            while (parent[r] != r) r = parent[r];
            if (r == i) components++;
        }
        boolean connected = components == 1;
        long[] dist = new long[n];
        Arrays.fill(dist, Long.MAX_VALUE);
        dist[src] = 0;
        PriorityQueue<long[]> pq = new PriorityQueue<>((x, y) -> Long.compare(x[0], y[0]));
        pq.add(new long[]{0, src});
        while (!pq.isEmpty()) {
            long[] cur = pq.poll();
            int u = (int) cur[1];
            if (cur[0] > dist[u]) continue;
            for (int[] e : adj.get(u)) {
                long nd = cur[0] + e[1];
                if (nd < dist[e[0]]) {
                    dist[e[0]] = nd;
                    pq.add(new long[]{nd, e[0]});
                }
            }
        }
        System.out.println(connected);
        System.out.println(joined == n - 1 ? String.valueOf(mst) : "-1");
        System.out.println(dist[dst] == Long.MAX_VALUE ? "-1" : String.valueOf(dist[dst]));
        System.out.println(components);
        """,
        [("4 4 0 3\n0 1 1\n1 2 2\n2 3 1\n0 3 10", "true\n4\n4\n1"),
         ("4 2 0 3\n0 1 1\n2 3 1", "false\n-1\n-1\n2"),
         ("1 0 0 0", "true\n0\n0\n1"),
         ("3 3 0 2\n0 1 4\n1 2 1\n0 2 2", "true\n3\n2\n1")],
        hint="Four algorithms, one parse: Kruskal gives the MST and the components, Dijkstra gives the distance. Keep their state separate."),
})

JAVA_QUIZ_FROM = {
    1: ["jv_keywords"],
    2: ["jv_types"],
    3: ["alg_what_is"],
    4: ["jv_types", "jv_jvm"],
    5: ["alg_analyzing"],
    6: ["alg_linear_search"],
    7: ["jv_strings"],
    8: ["jv_strings", "alg_pattern_recognition"],
    9: ["alg_two_pointers"],
    10: ["alg_sliding_window"],
    11: ["alg_prefix_sums"],
    12: ["jv_collections"],
    13: ["alg_big_o", "alg_pattern_recognition"],
    14: ["jv_collections", "alg_space"],
    15: ["jv_oop", "jv_collections"],
    16: ["jv_collections", "alg_efficient_sorts"],
    17: ["jv_collections", "jv_strings"],
    18: ["jv_collections", "jv_jvm"],
    19: ["alg_recursion"],
    20: ["alg_recursion", "jv_generics"],
    21: ["alg_binary_search", "alg_sorting_basics", "alg_efficient_sorts",
         "alg_non_comparison_sorts"],
    22: ["alg_pattern_recognition"],
    23: ["alg_space"],
    24: ["alg_recursion", "alg_recurrences"],
    25: ["alg_recurrences", "alg_big_o", "alg_analyzing"],
    26: ["alg_pattern_recognition", "jv_collections"],
}

JAVA_CONTESTS = {
    13: ("Java checkpoint — Months 1–3", 90 * 60),
    26: ("Java finale — the whole programme", 120 * 60),
}

_attach(JAVA_WEEKS, JAVA_EXAMS, quiz_from=JAVA_QUIZ_FROM,
        contests=JAVA_CONTESTS, sample=4)


MASTERY = [
    {
        "key": "typescript",
        "title": "TypeScript Mastery",
        "language": "typescript",
        "subtitle": "26 weeks from `const` to conditional types — every chapter, in order, with problems, a build project and an end-of-week exam.",
        "intro": (
            "This is the Learn library turned into a programme. Each week gives you a "
            "small number of chapters to study, curated problems from the Library to "
            "apply them, a build project of your own, and a quiz you must pass to "
            "unlock the next week. Weeks ahead of you stay sealed — the point is to "
            "go in order. Weeks behind you stay open forever."
        ),
        "pass_mark": 75,
        "exam_language": "typescript",
        "weeks": TS_WEEKS,
    },
    {
        "key": "java",
        "title": "Java Mastery",
        "language": "java",
        "subtitle": "26 weeks from `Scanner` to Dijkstra — the whole Java syllabus in order, with problems, a build project and an end-of-week exam.",
        "intro": (
            "The interview-focused half of the app, sequenced. Each week gives you a "
            "few chapters, curated problems from the Library, something to build, and "
            "an exam — multiple choice plus a real coding final — that you must pass "
            "to unlock the next week. Weeks ahead stay sealed; weeks behind stay open."
        ),
        "pass_mark": 75,
        "exam_language": "java",
        "weeks": JAVA_WEEKS,
    },
]


# ---------------------------------------------------------------------------
# Invariants — a broken curriculum is worse than no curriculum, so fail the
# build rather than shipping dangling references.
# ---------------------------------------------------------------------------
def _check_mastery(tracks, concepts, problem_slugs):
    for track in tracks:
        lang = track["language"]
        in_language = {k for k, c in concepts.items() if c.get("language", "java") == lang}
        scheduled = []
        seen_weeks = set()
        for week in track["weeks"]:
            assert week["week"] not in seen_weeks, f"duplicate week {week['week']}"
            seen_weeks.add(week["week"])
            for key in week["concepts"]:
                assert key in concepts, f"week {week['week']}: unknown concept {key!r}"
                assert key in in_language, f"week {week['week']}: {key!r} is not a {lang} concept"
                scheduled.append(key)
            for ref in week["problems"]:
                assert ref["slug"] in problem_slugs, \
                    f"week {week['week']}: unknown problem slug {ref['slug']!r}"
            assert week["quiz"], f"week {week['week']}: no end-of-week quiz"
            for q in week["quiz"]:
                assert 0 <= q["answer"] < len(q["options"]), \
                    f"week {week['week']}: answer index out of range for {q['question']!r}"
                assert len(q["options"]) >= 2, f"week {week['week']}: quiz needs options"
            assert week["quiz_sample"] >= 1, f"week {week['week']}: quiz_sample must be >= 1"
            assert len(week["quiz"]) >= week["quiz_sample"], \
                f"week {week['week']}: bank of {len(week['quiz'])} is smaller than the sample"

            exam = week["exam"]
            assert exam, f"week {week['week']}: no coding final"
            assert "____" in exam["starter"], \
                f"week {week['week']}: exam starter has no ____ blank"
            assert exam["starter"] != exam["solution"], \
                f"week {week['week']}: exam starter equals its solution"
            assert exam["tests"], f"week {week['week']}: exam has no tests"
            assert exam["language"] == track["exam_language"], \
                f"week {week['week']}: exam language does not match the track"

            if week["contest"]:
                assert week["problems"], \
                    f"week {week['week']}: a checkpoint contest needs problems to draw from"
                assert week["contest"]["duration_seconds"] > 0, \
                    f"week {week['week']}: contest needs a positive duration"

        assert sorted(seen_weeks) == list(range(1, len(track["weeks"]) + 1)), \
            f"{track['key']}: weeks must be numbered 1..N with no gaps"

        duplicates = {k for k in scheduled if scheduled.count(k) > 1}
        assert not duplicates, f"{track['key']}: concepts scheduled twice: {sorted(duplicates)}"

        missing = in_language - set(scheduled)
        assert not missing, \
            f"{track['key']}: concepts never scheduled (syllabus gap): {sorted(missing)}"
