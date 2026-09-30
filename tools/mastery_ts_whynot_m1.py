# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Why-not notes, month 1 (weeks 1-4) — TS_MASTERY_ROADMAP.md X-37.
#
# One note per wrong option of every authored single-choice question whose
# first bank is in weeks 1-4: what makes that option tempting and why it fails.
# Keyed by question text and option text, verbatim (see mastery_ts_why_not.py).
# Check on its own with
#   python tools/check_ts_why_not.py tools/mastery_ts_whynot_m1.py --month 1
# ---------------------------------------------------------------------------

TS_WHY_NOT.update({
    'Which declaration should you reach for by default?': {
        'Whichever the inferred type suggests':
            "Inference decides what type a variable has, not whether it may be reassigned; the keyword is about rebinding, which the inferred type can't tell you.",
        'let, because const is for compile-time constants':
            "`const` isn't a C-style compile-time constant: it only forbids rebinding the name, and any computed value can go in it, so it fits most variables.",
        'var, which is the most compatible':
            '`var` is function-scoped and hoisted, so names leak out of blocks; every environment you target supports `let`/`const`, so compatibility buys nothing.',
    },
    'What type does `const x = 5` have?': {
        'It has no type until annotated':
            'Every initialised declaration gets a type from its initializer; annotations are optional, and here inference picks the most precise type it can.',
        'any':
            'Inference only falls back to `any` when it has nothing to go on; `5` gives it something exact.',
        'number':
            '`number` is what `let x = 5` infers, because a `let` could later hold 6. A `const` can never change, so it keeps the literal `5`.',
    },
    'Why prefer `unknown` over `any` for a value of uncertain type?': {
        'There is no difference under strict mode':
            "Strict mode doesn't touch an explicit `any`: it still switches checking off for that value. `unknown` is the one that stays checked.",
        'any cannot be assigned to variables':
            '`any` can be assigned to and from almost anything; that permissiveness is exactly what makes it dangerous.',
        'unknown is faster at runtime':
            'Both types are erased before the program runs, so neither can affect speed; the difference is purely in what the compiler checks.',
    },
    '`let count = 0; count = "zero";` — what happens?': {
        'A runtime TypeError':
            'The program never gets to run: the compiler rejects the assignment first. Plain JavaScript would happily store the string.',
        'It works, but only outside strict mode':
            'Inference from the initializer applies in every mode; `count` is `number` with or without `strict`.',
        'It works; TypeScript widens count to any':
            'TypeScript never silently widens a variable to `any` to make an assignment fit; the initializer already fixed it as `number`.',
    },
    'What is the difference between `let x` and `const x` at block scope?': {
        'There is none in modern TypeScript':
            'There is one real difference: `const` forbids reassigning the name, which `let` allows.',
        'const deeply freezes the value':
            "`const` only protects the binding; an object held in a `const` can still have its properties changed. Freezing is `Object.freeze`'s job.",
        'const is function-scoped, let is block-scoped':
            "Function scope is `var`'s behaviour. `let` and `const` are both scoped to the nearest `{ }`.",
    },
    '`const x: any = "hi"; x.notAMethod();` — what does the compiler say?': {
        'Object is possibly undefined':
            'That error comes from narrowing a `T | undefined`; `x` is `any`, and `any` suppresses every such check.',
        'Property does not exist on type string':
            "That would be the error if `x` were typed `string`, but the annotation says `any`, so the string initializer's type is forgotten.",
        'any is not assignable to string':
            '`any` is assignable to everything, and nothing here assigns `x` to a `string` anyway.',
    },
    'What type does TypeScript infer for `const names = ["a", "b"]`?': {
        '`["a", "b"]`':
            'A literal tuple type is what `as const` gives; a plain array literal is mutable, so its elements widen to `string`.',
        '`any[]`':
            'The elements are strings, so inference has something to work with; `any[]` only comes from an empty `[]` or an explicit annotation.',
        '`readonly string[]`':
            'Nothing makes this array readonly: `const` fixes the binding, not the array, so `push` still works.',
    },
    "Which of these is NOT one of JavaScript's primitive types?": {
        '`bigint`':
            '`bigint` is a primitive: `typeof 10n` is `"bigint"`, and bigints are immutable values just like numbers.',
        '`symbol`':
            '`symbol` is a primitive, made by `Symbol()`: unique, immutable, and `typeof` reports `"symbol"`.',
        '`undefined`':
            '`undefined` is one of the primitives (alongside `null`); it is a value, not the absence of a type.',
    },
    '`const n: number = Number("abc");` — what happens?': {
        'A compile error':
            '`Number(...)` is declared to take a string and return `number`, so the compiler has nothing to object to.',
        'It throws at runtime':
            '`Number` never throws on bad text; it signals failure by returning `NaN`, which is why you must check the result.',
        '`n` is 0':
            'Only empty or whitespace-only text converts to 0; `"abc"` isn\'t numeric at all, so the result is `NaN`.',
    },
    'What does the judge do with your type annotations when it runs your program?': {
        'Compiles them into bytecode that enforces them':
            'TypeScript produces JavaScript, not bytecode, and the types are deleted from it; nothing enforces them while the program runs.',
        'Ignores them completely':
            "They aren't ignored: a type error stops the judge before your program ever runs.",
        'Turns them into runtime checks':
            'No checks are generated: annotations are erased, so bad data arriving on stdin slips past them unless you validate it yourself.',
    },
    '`const price = 9.99; price = 10;` — result?': {
        'A warning only':
            "tsc has no warning level for this: TS2588 is an error, and the judge won't run a program that has one.",
        'It only fails at runtime':
            'JavaScript would also throw at runtime, but TypeScript catches it earlier, at compile time (TS2588).',
        '`price` becomes 10':
            '`const` means the name can never be reassigned; the assignment is rejected, so `price` stays 9.99.',
    },
    'Which annotation is redundant?': {
        '`const items: string[] = [];`':
            'An empty `[]` has no elements to infer from, so this annotation is what tells the compiler what the array will hold.',
        '`function area(w: number, h: number)`':
            'Parameters have nothing to infer from; without these annotations `noImplicitAny` rejects them as implicit `any`.',
        '`let result: string | null = null;`':
            'A bare `let result = null` becomes an evolving `any` that accepts anything later; the annotation pins it to `string | null`.',
    },
    '`const input = fs.readFileSync(0, "utf8")` — what is `input`\'s type?': {
        '`Buffer`':
            'A `Buffer` is what you get with no encoding; passing `"utf8"` selects the overload that decodes to a `string`.',
        '`any`':
            "Node's type declarations give every overload a precise return type; nothing here is untyped.",
        '`string | undefined`':
            '`readFileSync` either returns the contents or throws; it never returns `undefined`, so the type has no `undefined` in it.',
    },
    'What are `Number("3") + Number("4")` and `"3" + "4"`?': {
        'A compile error for both':
            'Both lines are legal: the first adds two numbers, and `+` on two strings is allowed as concatenation.',
        '`"34"` and `"34"`':
            '`Number(...)` turns each operand into a number first, so the first `+` is arithmetic, not concatenation.',
        '`7` and `7`':
            'The second pair are still strings: `+` joins strings, it never parses them into numbers.',
    },
    'What is the type of `x` in `const x = Math.random() > 0.5 ? "yes" : 42`?': {
        '`any`':
            "The compiler knows both branches' types exactly, so it has no reason to give up and use `any`.",
        '`string | number`':
            "`string | number` is the widened type a `let` would get; a `const` keeps each branch's literal.",
        '`unknown`':
            '`unknown` only appears when you write it yourself; inference produces the union of the two branches instead.',
    },
    'You have `const v: unknown = getValue();`. What happens on `v.toString()`?': {
        'It compiles and returns `unknown`':
            "With `unknown` you can't call methods at all until you narrow, so there is no result type to speak of: TS18046 stops the call.",
        'It compiles; `unknown` behaves like `any`':
            'That is the whole difference between them: `any` allows everything, `unknown` allows almost nothing until you check it.',
        'It is converted to a string automatically':
            'No conversion happens: the compiler blocks the call before the program runs (TS18046).',
    },
    'Which declaration keyword has no place in modern TypeScript code?': {
        '`const`':
            '`const` is the default choice in modern code: block-scoped and not reassignable.',
        '`let`':
            '`let` is the right choice when a value must be reassigned; it is block-scoped, unlike `var`.',
        '`type`':
            "`type` declares a type alias, not a variable; it's a core TypeScript feature, not a legacy one.",
    },
    '`let total = 0; total += "5";` — what happens?': {
        'A runtime error':
            'The program never runs: the compiler rejects adding a string onto a `number` variable first.',
        '`total` becomes 5':
            '`+=` never parses the string into a number; JavaScript would concatenate, and TypeScript blocks even that.',
        '`total` becomes `"05"`':
            'That is what plain JavaScript would do, but TypeScript knows `total` is a `number` and refuses to let it become a string.',
    },
    'What does `console.log([1, 2, 3])` print?': {
        '`1,2,3`':
            "`1,2,3` is what `String(arr)` gives; `console.log` shows the array's structure instead of calling `toString`.",
        '`Array(3)`':
            '`Array(3)` is a summary some browser consoles show; Node prints the elements themselves.',
        '`[1,2,3]`':
            "Close, but Node's formatter puts spaces inside the brackets and after each comma.",
    },
    'What does `String([1, 2, 3])` give?': {
        '`"1 2 3"`':
            'That would need `join(" ")`; an array\'s default `toString` joins with commas.',
        '`"[1, 2, 3]"`':
            'Brackets are how `console.log` displays arrays; converting to a string drops them and just joins with `,`.',
        '`"[object Array]"`':
            '`[object Array]` is what `Object.prototype.toString` gives; arrays override `toString` to join their elements.',
    },
    'What type does `const pair = [1, "a"]` infer?': {
        '`[1, "a"]`':
            'Literal tuple types come only from `as const`; a plain array literal widens to a mutable array.',
        '`[number, string]`':
            'A tuple needs an annotation or `as const`; by default the compiler assumes an array whose length can change.',
        '`any[]`':
            'The elements have known types, so inference combines them into a union instead of giving up.',
    },
    '`const user = { name: "ana" }; user.name = "bo";` — what happens?': {
        'A runtime error':
            'The object itself is ordinary and writable; only rebinding `user` would be an error.',
        'It compiles, but the assignment is ignored':
            'The assignment really happens: `user.name` becomes `"bo"`. Silently ignored writes come from frozen objects, not from `const`.',
        'TS2588: cannot assign to a constant':
            "TS2588 is for `user = ...`, rebinding the name. Changing a property doesn't reassign the constant.",
    },
    'What is `Number("")`?': {
        'A thrown error':
            '`Number` never throws on bad text; its failure signal is `NaN`.',
        '`NaN`':
            'Surprisingly not: an empty string converts to 0, which is why empty input must be checked before converting.',
        '`undefined`':
            '`Number` always returns a number; `undefined` is never a possible result.',
    },
    'What is `Number(" 42 ")`?': {
        '`" 42 "`':
            '`Number` always returns a number, never the original string.',
        '`4`':
            "`Number` reads the whole numeric text; it doesn't stop after the first digit.",
        '`NaN`':
            'Leading and trailing whitespace is ignored; only whitespace inside the digits would make it `NaN`.',
    },
    'What are `Number(null)` and `Number(undefined)`?': {
        'Both `0`':
            'Only `null` converts to 0; `undefined` has no numeric meaning and gives `NaN`.',
        'Both `NaN`':
            '`null` converts to 0, a plausible-looking value that hides a missing input.',
        '`NaN` and `0`':
            "It's the other way round: `null` becomes 0 and `undefined` becomes `NaN`.",
    },
    'On empty stdin, what is `fs.readFileSync(0, "utf8").trim().split("\\n")`?': {
        'A thrown error':
            'Splitting an empty string is perfectly legal and never throws.',
        '`[]`':
            '`split` always returns at least one piece; with nothing to split, that piece is the empty string.',
        '`undefined`':
            '`split` always returns an array, never `undefined`.',
    },
    '`let a = 1; let b = a; b++;` — what is `a`?': {
        'It depends on the engine':
            'Copying primitives is specified behaviour, identical in every engine.',
        '`2`':
            "`b` received a copy of the number; incrementing `b` changes only `b`, because primitives aren't shared.",
        '`undefined`':
            "`a` was assigned 1 and never reassigned; copying it into `b` doesn't empty it.",
    },
    '`const a = [1]; const b = a; b.push(2);` — what is `a.length`?': {
        'A compile error':
            '`push` on a `const` array is fine: `const` only prevents rebinding the name, not changing the array.',
        '`0`':
            'Nothing removed the original element; `a` still holds 1, plus the 2 pushed through `b`.',
        '`1`':
            'That would be true if `b` were a copy, but assigning an array copies the reference, so both names point to one array.',
    },
    '`let x: number; console.log(x);` under `strict`?': {
        'It prints `0`':
            'Variables have no default zero value in JavaScript, and the compiler stops this before it runs anyway.',
        'It prints `undefined` with no error':
            'That is what JavaScript would print, but definite-assignment analysis rejects the read at compile time.',
        'TS7005: implicit any':
            '`x` is annotated `number`, so nothing about its type is implicit; the problem is that it has no value yet.',
    },
    'What does `typeof []` return?': {
        '`"array"`':
            '`typeof` has no `"array"` result; arrays are objects, so use `Array.isArray` to detect them.',
        '`"list"`':
            '`"list"` isn\'t a `typeof` result either, and JavaScript has no list type; arrays report `"object"`.',
        '`"undefined"`':
            '`[]` is a real (empty) array object, not a missing value.',
    },
    'What does `console.log(0.1 * 3)` print?': {
        '`0.299999`':
            'The error goes the other way, slightly above 0.3, and Node prints enough digits to identify the double exactly.',
        '`0.30`':
            "Node never pads with trailing zeros; fixing two decimal places is `toFixed(2)`'s job.",
        '`0.3`':
            '0.1 is stored slightly off, and tripling it lands on the double just above 0.3, which prints differently.',
    },
    'Where is a type annotation genuinely required?': {
        'On every `const`':
            'A `const` infers its type from its initializer; annotating it usually repeats what the compiler already knows.',
        'On every `let`':
            'A `let` with an initializer infers its type too; annotate it only when it starts empty or must hold more than its first value.',
        'On return statements':
            'Return types are inferred from the `return` expressions; annotating them is optional documentation, not a requirement.',
    },
    'What does `parseInt("08")` return in modern engines?': {
        '`0`':
            "`parseInt` doesn't stop at the leading zero; it reads both digits as decimal, giving 8.",
        '`10`':
            'Octal `10` is eight, not the other way round, and modern `parseInt` reads `"08"` as plain decimal anyway.',
        '`NaN`':
            '`"08"` starts with digits, so `parseInt` parses them; `NaN` needs text with no leading digits at all.',
    },
    'What is the type of `const lines = input.split("\\n")` when `input` is a `string`?': {
        '`[string]`':
            '`[string]` is a one-element tuple; `split` can return any number of pieces, so its type is an array.',
        '`string | undefined`':
            '`split` always returns an array; `string | undefined` is closer to what indexing it, `lines[0]`, could give.',
        '`string`':
            '`split` breaks the string into pieces, so the result is an array of strings, not a single string.',
    },
    'What does `fs.readFileSync(0, "utf8")` read?': {
        'Standard output':
            'Descriptor 0 is standard input; standard output is 1, and you write to it with `console.log`, not read it.',
        'The file named `0`':
            'A number argument is a file descriptor, not a filename; only a string path would name a file.',
        'The first line of standard input':
            'It reads everything up to the end of input; splitting it into lines is up to you.',
    },
    'Why call `.trim()` on the input?': {
        'It is required by TypeScript':
            "The compiler doesn't care; `trim` fixes the data, removing the trailing newline that would spoil comparisons.",
        'To convert it to a string':
            'With the `"utf8"` encoding, `input` is already a string; `trim` returns a string but converts nothing.',
        'To remove every space inside it':
            '`trim` only removes whitespace at the two ends; spaces inside are untouched.',
    },
    '`Number("12px")`, `parseInt("12px", 10)` — what do they give?': {
        '`12` and `12`':
            '`Number` needs the whole string to be numeric, so the `px` makes it `NaN`.',
        '`12` and `NaN`':
            "That's backwards: `parseInt` is the lenient one that reads the leading digits; `Number` is the strict one.",
        '`NaN` and `NaN`':
            '`parseInt` stops at the first non-digit and returns what it has read so far, 12.',
    },
    'What does `console.log("sum", 5)` print?': {
        '`["sum", 5]`':
            "The arguments aren't collected into an array; each one is printed in turn.",
        '`sum, 5`':
            '`console.log` separates its arguments with a single space, not a comma.',
        '`sum5`':
            'There is a separator, a single space between arguments; `"sum" + 5` is what would give `sum5`.',
    },
    '`const n = 2.5; console.log(n)` prints `2.5`. How do you print `2.50`?': {
        '`console.log(Number(n.toFixed(2)))`':
            '`toFixed` does produce `"2.50"`, but converting it back to a number drops the trailing zero again.',
        '`console.log(n * 1.00)`':
            "`1.00` is just the number 1; numbers don't remember decimal places, so this still prints `2.5`.",
        '`console.log(n, 2)`':
            'That passes 2 as a second value to print, giving `2.5 2`; `console.log` takes no formatting argument.',
    },
    'Why does `input.split(" ")` miscount words in `"a  b"`?': {
        'It counts characters, not words':
            '`split(" ")` does split on spaces; the trouble is what sits between two adjacent spaces.',
        "It doesn't; it returns two words":
            'Each space is a separator on its own, so two spaces enclose an empty string: three pieces, not two.',
        '`split` ignores the second word':
            '`b` is there as the last piece; the extra item is the empty string between the two spaces.',
    },
    'Why should you always use `===` instead of `==`?': {
        '`===` also compares object identity, which `==` cannot':
            'Both operators compare objects by identity; the difference is that `==` coerces mismatched types first.',
        '`===` is faster':
            'Speed isn\'t the reason; predictability is: `==` applies coercion rules that make `"1" == 1` true.',
        '`==` is deprecated and errors under strict':
            "`==` is still valid in strict mode; it's avoided because its coercions are confusing, not because it errors.",
    },
    'Which of these is truthy?': {
        '""':
            'The empty string is falsy; only non-empty strings, like `"0"`, are truthy.',
        '0':
            'The number 0 is falsy, but the string `"0"` isn\'t: it is a non-empty string.',
        'NaN':
            '`NaN` is falsy, one of the few falsy numbers along with 0 and -0.',
    },
    'What does `a ?? b` do that `a || b` does not?': {
        'It short-circuits, which || does not':
            'Both short-circuit; `||` skips `b` whenever `a` is truthy. The difference is which values trigger the fallback.',
        'It throws when a is null':
            '`??` exists precisely to handle null: it returns `b` instead of throwing.',
        'It works on objects only':
            '`??` works on any type; it is most useful with numbers and strings, where 0 and `""` must be kept.',
    },
    '`obj?.prop` where `obj` is undefined evaluates to…': {
        'a TypeError':
            '`?.` exists to avoid that TypeError: it stops at the undefined `obj` instead of reading a property from it.',
        'false':
            "Optional chaining doesn't convert anything to a boolean; a short-circuited chain yields `undefined`.",
        'null':
            'Even when `obj` is `null`, a short-circuited `?.` gives `undefined`, never `null`.',
    },
    '`if (value)` where `value` is `0` — does the branch run?': {
        'It is a compile error':
            'Any value can be tested with `if`; TypeScript allows a number as a condition.',
        'Only under strict mode':
            "Truthiness rules are the same in every mode; strict mode doesn't change them.",
        'Yes, numbers are always truthy':
            '0 and `NaN` are falsy numbers, which is why `if (value)` silently drops a legitimate zero.',
    },
    'What does `switch` compare cases with?': {
        'A deep structural comparison':
            "`switch` never compares contents: two separate objects with equal fields don't match each other.",
        'Loose equality (==)':
            '`switch` doesn\'t coerce, so `case "1"` never matches the number 1.',
        'Object.is':
            'Close, but `Object.is` treats `NaN` as equal to itself; `switch` uses `===`, where `NaN` matches no case.',
    },
    'Under TypeScript, what happens to `const r = "5" - 2;`?': {
        '`r` is 3':
            'That is what JavaScript would compute by coercing `"5"`, but TypeScript rejects `-` on a string (TS2362).',
        '`r` is `"52"`':
            '`"52"` is what `+` would give; `-` never concatenates, and TypeScript rejects it on a string anyway.',
        '`r` is `NaN`':
            'In JavaScript `"5"` would coerce to 5, not `NaN`, and TypeScript stops the program before any of that happens.',
    },
    '`const r = "5" + 2;` — does it compile, and what is `r`?': {
        'No — compile error':
            'TypeScript allows `+` between a string and a number, because concatenation is a legitimate use of it.',
        'Yes — `r` is 7':
            '`+` with a string operand concatenates; it never parses the string into a number.',
        'Yes — `r` is `NaN`':
            "Concatenation can't produce `NaN`; the number is simply turned into text and appended.",
    },
    'What does `!!"false"` evaluate to?': {
        'A compile error':
            "`!` can be applied to any value in TypeScript; `!!x` is the usual way to get a value's truthiness.",
        '`"false"`':
            '`!` always produces a boolean, so `!!` can never give back the original string.',
        '`false`':
            'The text of a string doesn\'t matter, only whether it is empty; `"false"` is non-empty, so it is truthy.',
    },
    'What are `null ?? "x"` and `0 ?? "x"`?': {
        '`"x"` and `"x"`':
            "`??` doesn't fall back on 0; that is `||`. 0 is a real value, so it is kept.",
        '`"x"` and `null`':
            "In the second expression `0` is on the left and isn't nullish, so it is the result, not `null`.",
        '`null` and `0`':
            'The first `??` does replace `null`; that is exactly what it exists for.',
    },
    'In `a && b`, when is `b` evaluated?': {
        'Always':
            '`&&` short-circuits: if `a` is falsy the result is already known, so `b` is never evaluated.',
        'Only when `a` is falsy':
            "That is `||`'s rule. `&&` only needs `b` when `a` is truthy.",
        'Only when `b` is a boolean':
            "The type of `b` doesn't matter; `&&` works with any values and returns one of them.",
    },
    '`x > 0 ? "pos" : x < 0 ? "neg" : "zero"` when `x` is `NaN`?': {
        'It throws':
            'Comparing with `NaN` never throws; it just returns `false`.',
        '`"neg"`':
            '`NaN < 0` is false, like every comparison with `NaN`, so the second test fails too.',
        '`"pos"`':
            "`NaN > 0` is false, so the first branch doesn't run.",
    },
    'Which is the correct leap-year test?': {
        '`y % 100 !== 0 || y % 400 === 0`':
            "It forgets the every-fourth-year rule: 2023 isn't a multiple of 100, so this calls it a leap year.",
        '`y % 4 === 0 && y % 400 === 0`':
            'Only multiples of 400 pass this, so ordinary leap years like 2024 are missed.',
        '`y % 4 === 0`':
            'This ignores the century rule: 1900 is a multiple of 4 but was not a leap year.',
    },
    'How does `switch (true) { case score >= 90: … }` work?': {
        'Cases are compared with `==`':
            '`switch` always uses `===`; with `switch (true)`, a case matches only when its expression is exactly `true`.',
        'It is a syntax error':
            'Any expression can follow `case`, including a comparison, so `switch (true)` is valid.',
        'Only the first case is ever checked':
            'Cases are tried in order until one matches; the first one is only where checking starts.',
    },
    '`if (x = 5) { … }` — what does TypeScript do?': {
        'Compile error: use `===`':
            'Tempting to expect, but TypeScript accepts an assignment as a condition, which is why this typo is so easy to miss.',
        'It compares `x` to 5':
            "A single `=` assigns; comparing needs `===`. The condition's value is the assigned 5, which is truthy.",
        'It throws at runtime':
            'Assigning 5 is an ordinary operation; its value (5) is then used as the condition, and nothing throws.',
    },
    'What is `typeof NaN`?': {
        '`"NaN"`':
            '`typeof` has no `"NaN"` result; `NaN` is a value of type number, the result of a failed numeric operation.',
        '`"object"`':
            '`"object"` is for objects, arrays and `null`; `NaN` is a primitive number.',
        '`"undefined"`':
            '`NaN` is a defined value, not a missing one, and it is a number.',
    },
    'Which is a safe equality test for two computed floats?': {
        '`Object.is(a, b)`':
            '`Object.is` is still exact equality (it differs from `===` only for `NaN` and -0), so rounding error still defeats it.',
        '`a == b`':
            '`==` adds type coercion but is just as exact for two numbers; `0.1 + 0.2 == 0.3` is still false.',
        '`a === b`':
            'Exact equality fails whenever rounding leaves the results a tiny bit apart, as `0.1 + 0.2` versus `0.3` shows.',
    },
    'What is `1 + 2 + "3"`?': {
        '`"123"`':
            '`+` works left to right: `1 + 2` is numeric addition, done before the string appears.',
        '`"6"`':
            'Only the first `+` adds; the second has a string operand, so it appends `"3"` to 3.',
        '`6`':
            'Once `"3"` is involved, `+` concatenates, so the result is a string, not a number.',
    },
    'What is `"1" + 2 + 3`?': {
        '`"15"`':
            '`2 + 3` isn\'t computed first; evaluation goes left to right, and `"1" + 2` is already a string.',
        '`"33"`':
            'There is no addition at all here: the leftmost operand is a string, so both `+`s concatenate.',
        '`6`':
            'Starting with a string makes every following `+` a concatenation, so no number is produced.',
    },
    'What are `7 % -3` and `-7 % 3`?': {
        '`-1` and `1`':
            'The sign follows the left operand, not the divisor, so `7 % -3` is positive and `-7 % 3` is negative.',
        '`-2` and `2`':
            '`%` gives a remainder, and its size here is 1: 7 = (-2) × (-3) + 1. The -2 is the quotient.',
        '`1` and `2`':
            "2 for `-7 % 3` is a mathematical modulo; JavaScript's `%` keeps the dividend's sign, giving -1.",
    },
    'What is `"10" < "9"`?': {
        'A compile error':
            'Comparing two strings with `<` is allowed; it compares them character by character.',
        '`NaN`':
            "`<` returns a boolean, and strings aren't converted to numbers when both sides are strings.",
        '`false`':
            'That is the numeric answer; as strings, `"1"` sorts before `"9"`, so `"10"` comes first.',
    },
    'What is `+""`?': {
        '`""`':
            "Unary `+` always converts to a number, so the result can't be a string.",
        '`NaN`':
            'The empty string converts to 0, not `NaN`: the same trap as `Number("")`.',
        '`undefined`':
            "Unary `+` always yields a number, and `undefined` isn't one.",
    },
    'What does `a ||= b` do?': {
        'Always assigns `b`':
            '`||=` short-circuits: when `a` is already truthy, nothing is assigned.',
        'Assigns when `a` is nullish':
            'Nullish-only is `??=`; `||=` also replaces 0, `""`, `false` and `NaN`.',
        'Compares `a` and `b`':
            '`||=` is an assignment, not a comparison; it is shorthand for `a || (a = b)`.',
    },
    'What does `a ??= b` do?': {
        'Always assigns':
            '`??=` only assigns when `a` is `null` or `undefined`; any other value is left alone.',
        'Assigns when `a` is falsy':
            'That is `||=`. `??=` keeps falsy values like 0, `""` and `false`.',
        'Throws when `a` is nullish':
            'Handling nullish values is its whole purpose: it fills them in rather than throwing.',
    },
    'What does `true + 1` do under TypeScript?': {
        'Evaluates to `"true1"`':
            "There is no string operand, so there's no concatenation, and TypeScript rejects the expression anyway.",
        'Evaluates to `2`':
            'That is what JavaScript gives by coercing `true` to 1, but TypeScript refuses `+` on a boolean (TS2365).',
        'Evaluates to `NaN`':
            '`true` would coerce to 1, not `NaN`, and the compiler rejects the expression before it runs.',
    },
    'What is `null == undefined` and `null === undefined`?': {
        'Both `false`':
            'Loose equality has a special rule that makes `null` and `undefined` equal to each other.',
        'Both `true`':
            "`===` doesn't coerce, and `null` and `undefined` are different types, so the strict test is false.",
        '`false` and `true`':
            'It is the reverse: loose `==` treats them as equal, strict `===` does not.',
    },
    'What is `{ a: 1 } === { a: 1 }`?': {
        'A compile error':
            'tsc does flag this line (TS2839), but only because the value is known in advance: two separately created objects are never `===`.',
        '`true`':
            '`===` compares objects by identity, not by contents, and the two literals create two different objects.',
        '`undefined`':
            '`===` always produces a boolean, never `undefined`.',
    },
    'What are `!!NaN` and `!![]`?': {
        'Both `false`':
            'Every object is truthy, including an empty array, so `!![]` is `true`.',
        'Both `true`':
            '`NaN` is one of the falsy values, so `!!NaN` is `false`.',
        '`true` and `false`':
            'Both halves are swapped: `NaN` is falsy, and `[]`, being an object, is truthy.',
    },
    'What is `Boolean("0")`?': {
        '`0`':
            "`Boolean` returns a boolean, not a number; it doesn't parse the text.",
        '`NaN`':
            '`Boolean` never returns `NaN`; it only reports truthiness as `true` or `false`.',
        '`false`':
            '`"0"` is a non-empty string, and every non-empty string is truthy; the digit it contains doesn\'t matter.',
    },
    'In `false && sideEffect()`, is `sideEffect` called?': {
        'Only in strict mode':
            'Short-circuit evaluation works the same in every mode.',
        'Yes, always':
            '`&&` stops as soon as the left side is falsy, so the call never happens.',
        'Yes, but its result is ignored':
            "The call is skipped entirely, so its side effects don't happen either.",
    },
    'A `switch` case has no `break`. What happens?': {
        'A runtime error':
            'A missing `break` is legal; execution simply carries on.',
        'The next case is skipped':
            "The next case's code runs without its label being tested; that is what fall-through means.",
        'The switch ends':
            "Only `break` (or `return`) leaves the switch early; reaching the end of one case's code doesn't.",
    },
    'How does `a ? b : c ? d : e` group?': {
        'It depends on the values':
            'Grouping is fixed by the grammar before any value is known.',
        "It's a syntax error":
            'Chained conditionals are valid; they are the usual way to write an else-if as an expression.',
        '`(a ? b : c) ? d : e`':
            'That would be left-associative; the conditional operator is right-associative, so the nested part is the else branch.',
    },
    'What does `user?.name ?? "anon"` give when `user` is `undefined`?': {
        'A TypeError':
            "`?.` guards the access, so reading `name` off `undefined` doesn't throw.",
        '`null`':
            'Nothing here produces `null`; `?.` yields `undefined`, which `??` then replaces.',
        '`undefined`':
            '`user?.name` is `undefined`, but `??` then substitutes `"anon"`.',
    },
    'What is `2 ** -1`?': {
        'A compile error':
            'A negative exponent is valid for `**`.',
        '`-2`':
            'That would be multiplying by -1; `**` raises to a power, and `2 ** -1` means 1/2.',
        '`0`':
            "Numbers aren't integers, so 1/2 isn't truncated to 0.",
    },
    'Which comparison is `true`?': {
        '`NaN === NaN`':
            "`NaN` isn't equal to anything, itself included; tsc even flags this as always false (TS2845).",
        '`[1] === [1]`':
            'Two array literals are two different objects and `===` compares identity; tsc flags this as always false (TS2839).',
        '`null === undefined`':
            "`===` doesn't coerce, and `null` and `undefined` are different values; only `==` equates them.",
    },
    'How do you test whether `x` is `NaN`?': {
        '`typeof x === "NaN"`':
            '`typeof NaN` is `"number"`; there is no `"NaN"` result, and tsc rejects this comparison (TS2367).',
        '`x == NaN`':
            "Loose equality doesn't help: `NaN` is unequal to everything, so this is always false (tsc flags it, TS2845).",
        '`x === NaN`':
            "`NaN` isn't even `===` to itself, so this test is always false; tsc reports it (TS2845).",
    },
    'Which value is truthy?': {
        '`""`':
            'The empty string is the one falsy string; any string with characters in it is truthy.',
        '`0`':
            '0 is falsy, a frequent source of bugs when 0 is a valid value.',
        '`NaN`':
            '`NaN` is falsy, even though its type is `number`.',
    },
    '`const n = 0; n || 10` and `n ?? 10` give…': {
        '`0` and `0`':
            '`||` treats 0 as falsy and falls back to 10.',
        '`0` and `10`':
            "The two are swapped: `||` replaces the 0, while `??` keeps it because 0 isn't nullish.",
        '`10` and `10`':
            '`??` only replaces `null` and `undefined`, so the 0 survives.',
    },
    'What does TypeScript say about `3 === "3"` with those declared types?': {
        'A warning only':
            'tsc reports this as an error (TS2367), and an error stops the judge from running the program.',
        '`false`, with no error':
            'JavaScript would evaluate it to `false`, but TypeScript sees that a `number` and a `string` can never be `===` and rejects it.',
        '`true`':
            "`===` doesn't coerce, so a number is never strictly equal to a string, and tsc rejects the comparison outright.",
    },
    '`Object.is(0, -0)` and `Object.is(NaN, NaN)`?': {
        '`false` and `false`':
            '`Object.is` does treat `NaN` as the same as `NaN`; that is one of the two cases it fixes relative to `===`.',
        '`true` and `false`':
            'That is what `===` gives; `Object.is` flips both corners, telling 0 from -0 and matching `NaN`.',
        '`true` and `true`':
            '`Object.is` distinguishes 0 from -0, unlike `===`.',
    },
    'What is the difference between `for...of` and `for...in` over an array?': {
        'They are the same for arrays':
            'They differ: `for...in` gives string keys (`"0"`, `"1"`, ...) plus any extra enumerable properties; `for...of` gives the elements.',
        'for...in does not work on arrays':
            'It does run on arrays, which is the trap: you get the indexes as strings instead of the elements.',
        'for...in yields values, for...of yields indices':
            'It is the other way round: `of` yields the values, `in` yields the keys as strings.',
    },
    'Why is `0.1 + 0.2 === 0.3` false?': {
        '=== compares references for numbers':
            '`===` compares numbers by value, not reference; the sum really is `0.30000000000000004`, not 0.3.',
        'It is true under `strict`':
            '`strict` changes type checking, not arithmetic; the sum is computed the same way either way.',
        'It is true under strict mode':
            "Strict mode doesn't change floating point; `0.1 + 0.2` is `0.30000000000000004` in every mode.",
        'TypeScript rounds decimals':
            "TypeScript doesn't touch arithmetic; the rounding comes from the IEEE 754 double format itself.",
        'TypeScript rounds differently from JavaScript':
            'TypeScript compiles to JavaScript and runs on the same engine, so its numbers behave identically.',
        '`===` compares references for numbers':
            'Only objects have references; a number is a primitive compared by value, and these two are genuinely different doubles.',
    },
    'What does `Math.trunc(-4.7)` return?': {
        '-4.7':
            '`trunc` removes the fractional part; it only returns the input unchanged if it is already whole.',
        '-5':
            '-5 is `Math.floor`, which rounds towards minus infinity; `trunc` rounds towards zero.',
        '4':
            "`trunc` keeps the sign; dropping it is `Math.abs`'s job.",
    },
    'What is the largest exactly-representable integer?': {
        '2^64 - 1':
            "That is an unsigned 64-bit integer's limit; a `number` is a double with only 53 bits of integer precision.",
        'Number.MAX_VALUE':
            '`MAX_VALUE` (about 1.8e308) is the largest finite double, but long before it integers are spaced more than 1 apart.',
        'There is no limit; number is arbitrary precision':
            '`number` is a fixed 64-bit float; arbitrary-precision integers are what `bigint` is for.',
    },
    'Which loop gives you the index and works with `break`?': {
        'forEach':
            "`forEach` can't be stopped: `break` is a syntax error in its callback, and `return` only skips one element.",
        'map':
            '`map` visits every element to build a new array; there is no way to break out of it.',
        'reduce':
            '`reduce` always walks the whole array; it has no early exit.',
    },
    '`Math.round(-2.5)` returns…': {
        '-2.5':
            '`Math.round` always returns an integer, so the .5 has to go one way or the other.',
        '-3':
            'Rounding half away from zero would give -3, but `Math.round` rounds halves up, towards plus infinity.',
        '2':
            'Rounding keeps the sign; -2.5 rounds to -2, not 2.',
    },
    'How many times does `for (let i = 0; i <= 10; i += 2)` run its body?': {
        '10':
            '10 is the bound, not the count; `i += 2` steps by twos, so far fewer iterations happen.',
        '11':
            '11 counts every integer from 0 to 10, but the step is 2, so only the even ones are visited.',
        '5':
            '`<=` makes the bound inclusive, so 10 itself runs too: 0, 2, 4, 6, 8, 10 is six values.',
    },
    'A digit counter loops `while (n > 0) { n = Math.trunc(n / 10); count++; }`. What does it give for `n = 0`?': {
        '1':
            'One is the correct digit count for 0, which is the point: this loop never runs for 0, so it reports 0 instead.',
        'It loops forever':
            'The condition `0 > 0` is false at once, so the body never runs at all, let alone forever.',
        '`NaN`':
            "`count` is never touched when the loop doesn't run, so it keeps its starting value of 0.",
    },
    'What does `break` inside the inner of two nested loops exit?': {
        'Both loops':
            '`break` only leaves the innermost loop; leaving both needs a label (`break outer`).',
        'Only the current iteration':
            'Skipping just the current iteration is `continue`; `break` ends the whole inner loop.',
        'The whole function':
            "Leaving the function is `return`'s job; `break` only exits a loop.",
    },
    'What is `5 / 0` in JavaScript?': {
        'A thrown error':
            'Number division never throws; floating point defines a nonzero number divided by zero as plus or minus `Infinity`.',
        '`0`':
            'Dividing by ever-smaller numbers makes the result grow, not shrink; at 0 it is `Infinity`.',
        '`NaN`':
            '`NaN` is for `0 / 0`; a nonzero number over 0 is `Infinity`.',
    },
    'What is `10 % 3.5`?': {
        'A compile error':
            '`%` accepts non-integer numbers, so this compiles.',
        '`0.5`':
            "3.5 goes into 10 twice, using up 7, so the remainder is 3; 0.5 isn't what's left over.",
        '`1`':
            "`%` doesn't round the divisor down to 3; `10 % 3` would be 1, but 3.5 fits twice, leaving 3.",
    },
    'Is `2 ** 53 + 1 === 2 ** 53` true or false?': {
        'A compile error':
            'Both sides are ordinary numbers, so the comparison compiles.',
        'False':
            "2^53 + 1 can't be stored as a double; it rounds to 2^53, so both sides are the same number.",
        'It throws a RangeError':
            'Numbers lose precision silently beyond 2^53; nothing throws.',
    },
    '`const big = 123n + 1;` — what happens?': {
        '`"123n1"`':
            'There is no string here; `123n` is a bigint, and TypeScript refuses to mix it with a number (TS2365).',
        '`124`':
            'There is no automatic conversion to number: mixing is an error at compile time and a TypeError at runtime.',
        '`124n`':
            'That is what `123n + 1n` gives; the `1` must be a bigint too, because JavaScript never converts implicitly.',
    },
    'What sums 1..n in constant time?': {
        '`(n + 1) / 2`':
            'That is the average of 1..n; the sum is the average times the count, n.',
        '`n * n / 2`':
            'Close, but it misses half the diagonal: the true sum, `n * (n + 1) / 2`, is larger by `n / 2`.',
        '`n ** 2 + 1`':
            'For n = 3 this gives 10, not 6; the sum grows like n²/2, and there is no `+ 1` in it.',
    },
    '`Number.parseFloat("3.14abc")`?': {
        'A compile error':
            '`parseFloat` accepts any string, so this compiles.',
        '`3`':
            '3 is what `parseInt` would give; `parseFloat` also reads the decimal point and the fractional digits.',
        '`NaN`':
            '`parseFloat` reads the longest valid numeric prefix; `NaN` is what the stricter `Number(...)` would give.',
    },
    'What does `continue` do inside a loop?': {
        'Exits the loop':
            'Exiting the loop is `break`; `continue` skips only the rest of the current iteration.',
        'Nothing outside a switch':
            '`continue` belongs to loops, not to `switch`; inside a loop it jumps to the next iteration.',
        'Restarts the loop from the first iteration':
            "The loop doesn't reset; its counter keeps its progress and the next iteration runs.",
    },
    '`for (const x of [1, 2, 3]) x = x * 2;` — what happens?': {
        'A runtime TypeError only':
            'It would throw at runtime, but TypeScript catches the reassignment of a `const` first (TS2588).',
        'Nothing — it runs and changes nothing':
            'The compiler rejects the loop, so it never runs at all.',
        'The array becomes [2, 4, 6]':
            '`x` is a copy of each element; even with `let`, reassigning it would never write back into the array.',
    },
    'What does `for (const i in "ab")` give `i`?': {
        "Nothing — strings aren't iterable with `in`":
            "At runtime `for...in` does visit a string's index keys (tsc objects to a string there, TS2407, but that is a type rule, not what the loop does).",
        'The numbers 0 and 1':
            '`for...in` enumerates property keys, and keys are always strings, even when they look like indexes.',
        '`"a"` and `"b"`':
            'The characters come from `for...of`; `for...in` gives their positions, as strings.',
    },
    'How many times does a `do…while` body run when its condition is false from the start?': {
        'Forever':
            'The condition is checked after each pass and it is false, so the loop stops after one run.',
        "It's a compile error":
            'A `do...while` with a false condition is valid; it simply runs once.',
        'Zero times':
            "That is `while`'s behaviour; `do...while` runs the body before it checks the condition.",
    },
    'What are `Math.floor(-4.5)` and `Math.ceil(-4.5)`?': {
        'Both `-4`':
            '`floor` rounds towards minus infinity, so it goes down to -5, not up towards zero.',
        'Both `-5`':
            '`ceil` rounds towards plus infinity, and -4 is above -4.5.',
        '`-4` and `-5`':
            'Swapped: for negatives, down means more negative, so `floor` gives -5 and `ceil` gives -4.',
    },
    'What does `(1.005).toFixed(2)` return?': {
        '`"1.005"`':
            '`toFixed(2)` always gives exactly two decimals, so the third digit must go.',
        '`"1.01"`':
            'The stored double is slightly below 1.005, so it rounds down, not up.',
        '`1.01`':
            '`toFixed` returns a string, not a number, and the value rounds down to 1.00 anyway.',
    },
    'What does `(2.5).toFixed(0)` return?': {
        '`"2"`':
            "That is banker's rounding (half to even); `toFixed` rounds an exact half away from zero.",
        '`"2.5"`':
            '`toFixed(0)` means zero decimals, so the `.5` must be rounded off.',
        '`3`':
            'The digit is right but the type isn\'t: `toFixed` returns a string, `"3"`.',
    },
    'What is `Infinity - Infinity`?': {
        'A thrown error':
            'Arithmetic on numbers never throws; results that have no defined value are `NaN`.',
        '`0`':
            "Infinities don't cancel out like ordinary numbers; the difference of two infinities is undefined, so `NaN`.",
        '`Infinity`':
            "Infinity minus infinity has no defined value, so it can't stay `Infinity`.",
    },
    'Is `Number.isSafeInteger(2 ** 53)` true?': {
        'It throws':
            '`isSafeInteger` never throws; it returns a boolean for any argument.',
        'Only for bigint':
            'It returns false for a bigint; "safe" is about a `number`\'s double precision.',
        'Yes':
            '2 ** 53 is exactly representable but not safe: 2 ** 53 + 1 rounds to it, so it is ambiguous.',
    },
    'What is `10n / 3n`?': {
        'A compile error':
            'Dividing two bigints is allowed; only mixing a bigint with a number is an error.',
        '`3.3333333333333335`':
            'Bigint division stays in bigint and never produces a fractional `number`.',
        '`3.333…n`':
            "Bigints can't hold fractions, so the result is truncated to `3n`.",
    },
    'What is `typeof 10n`?': {
        '`"integer"`':
            'JavaScript has no integer category in `typeof`; a bigint reports `"bigint"`.',
        '`"number"`':
            '`bigint` is a primitive separate from `number`, with its own `typeof` result.',
        '`"object"`':
            'Bigints are primitives, not wrapper objects.',
    },
    'What does `Number.parseInt("101", 2)` return?': {
        '`101`':
            'The second argument is a radix, so `"101"` is read as binary, not decimal.',
        '`2`':
            '2 is the radix you passed in; the result is the value of `"101"` in base 2.',
        '`NaN`':
            'All three characters are valid binary digits, so parsing succeeds.',
    },
    'What does `(255).toString(16)` return?': {
        '`"0xff"`':
            '`toString(16)` gives only the digits; add a `0x` prefix yourself if you want one.',
        '`"255"`':
            'The argument is a radix; without it (or with 10) you would get `"255"`.',
        '`"FF"`':
            '`toString` uses lower-case letters for digits above 9; call `toUpperCase()` to get `FF`.',
    },
    'What is `Number("1e3")`?': {
        '`"1e3"`':
            '`Number` returns a number, never the original string.',
        '`1`':
            '`Number` parses the whole text, exponent included; stopping at the first digit is closer to `parseInt`.',
        '`NaN`':
            '`1e3` is valid numeric syntax (1 × 10³), so it converts.',
    },
    '`for (let i = 0; i < 3; i++) queueMicrotask(() => console.log(i));` prints?': {
        'Nothing':
            'Queued microtasks run as soon as the synchronous code finishes, before the program exits.',
        '`0`, `0`, `0`':
            "Each iteration's `let` binding holds that iteration's value, not the first one.",
        '`3`, `3`, `3`':
            'That is the classic `var` result; `let` creates a fresh `i` per iteration, so each callback sees its own.',
    },
    'What range does `Math.random()` return?': {
        '0 to 1 inclusive':
            '1 is excluded: the result is always strictly less than 1.',
        'Any number':
            'The range is fixed at 0 up to, but not including, 1; scale it yourself for other ranges.',
        'Integers 0–100':
            'It returns a fraction; integers need scaling and `Math.floor`.',
    },
    'How do you exit an outer loop from inside an inner one?': {
        '`break 2`':
            "JavaScript's `break` takes a label, not a number of levels to leave; `break 2` is PHP.",
        '`continue outer`':
            "`continue outer` jumps to the outer loop's next iteration rather than leaving it.",
        '`return` from the inner loop only':
            '`return` exits the whole function, not a loop; it only works when nothing after the loops needs to run.',
    },
    'What is `(1234.5678).toFixed(2)`?': {
        '`"1,234.57"`':
            '`toFixed` never adds thousands separators; that is `Intl.NumberFormat` or `toLocaleString`.',
        '`"1234.56"`':
            '`toFixed` rounds rather than truncates: the dropped `78` rounds `.56` up to `.57`.',
        '`1234.57`':
            '`toFixed` returns a string, not a number.',
    },
    'What is `0 / 0`?': {
        'A thrown error':
            'Dividing by zero never throws for numbers; `0 / 0` has no meaningful value, so it is `NaN`.',
        '`0`':
            '0 divided by anything nonzero is 0, but by 0 the result is undefined: `NaN`.',
        '`Infinity`':
            '`Infinity` is for a nonzero number over 0; `0 / 0` is undefined.',
    },
    'What is `Math.sqrt(-1)`?': {
        'A thrown error':
            "`Math` functions don't throw on bad input; they return `NaN`.",
        '`-1`':
            '-1 is the input, not its root; no real number squares to -1.',
        '`i`':
            'JavaScript has no complex numbers; an impossible real result is `NaN`.',
    },
    'How should an app store a price of $19.99?': {
        'As a `bigint`':
            "Overkill: prices fit easily in a `number`'s safe-integer range, so cents as an ordinary integer are already exact.",
        'As the number `19.99`':
            '19.99 has no exact binary representation, so sums of prices pick up rounding errors.',
        'As the string `"19.99"` and parse it every time':
            "Parsing back to a number every time reintroduces the float problem, and strings can't be added as amounts.",
    },
    '`Math.round(-2.5)`?': {
        '`-2.5`':
            '`Math.round` always produces an integer.',
        '`-3`':
            '`Math.round` sends halves towards plus infinity, so -2.5 goes up to -2.',
        '`NaN`':
            '-2.5 is a perfectly ordinary number to round.',
    },
    '`1n + 1`?': {
        '`"11"`':
            'No string is involved; mixing a bigint and a number is an error, not a concatenation.',
        '`2`':
            "JavaScript won't convert the bigint to a number implicitly; TypeScript rejects the mix (TS2365).",
        '`2n`':
            "`2n` needs `1n + 1n`; the plain `1` isn't converted to a bigint automatically.",
    },
    'What is `Number.MAX_SAFE_INTEGER`?': {
        '2^31 − 1':
            'That is the 32-bit signed integer limit; JavaScript numbers are 64-bit doubles.',
        '2^64 − 1':
            'A double spends 11 bits on the exponent, leaving 53 bits of integer precision, not 64.',
        'The largest `number` at all':
            'That is `Number.MAX_VALUE` (about 1.8e308); above `MAX_SAFE_INTEGER` numbers still exist but skip integers.',
    },
    'Why pass `"en-US"` to `Intl.NumberFormat` in a judged program?': {
        "It's faster":
            "Speed isn't the point; the output must be identical on every machine.",
        "It's required":
            "The argument is optional; without it the machine's default locale is used, and that varies.",
        "Other locales can't format currency":
            'Every locale formats currency, just differently (like `1.234,56 €`), which is exactly why you fix one.',
    },
    'What does `s.replace("a", "b")` do when `s` contains several `a`s?': {
        'Replaces all of them':
            'A string pattern replaces only the first match; all of them needs `replaceAll` or a `/g` regex.',
        'Replaces the last one':
            'It scans from the start and stops at the first match.',
        'Throws unless a regex is used':
            'A plain string pattern is fine; it just matches literally, once.',
    },
    'What does `"abcdef".slice(-2)` return?': {
        '""':
            'A negative index counts back from the end rather than being clamped to 0, so something is returned.',
        '"ab"':
            '`"ab"` is `slice(0, 2)`; a negative start counts from the end instead.',
        '"abcd"':
            '`"abcd"` is `slice(0, -2)`, everything except the last two; `slice(-2)` keeps the last two.',
    },
    'Why does `s[0] = "X"` not change the string?': {
        'Index assignment needs the charAt setter':
            '`charAt` only reads; strings have no setter at all, because they are immutable.',
        'It does change it, but the change is not visible until reassignment':
            'There is no hidden pending change: a string can never be modified, only replaced with a new one.',
        'It only fails under strict mode':
            "Strict mode only decides whether the failed write throws or is silently ignored; the string can't change either way (tsc rejects it, TS2542).",
    },
    '`"  hi  ".trim().length` is…': {
        '0':
            '`trim` only removes whitespace at the ends; the letters stay.',
        '4':
            '4 would keep two spaces; `trim` removes all leading and trailing whitespace, not one character per side.',
        '6':
            '6 is the length before trimming; `trim` returns a shorter string.',
    },
    'What does `"a,b,,c".split(",")` produce?': {
        '3 items, empties dropped':
            '`split` never drops empty pieces; you have to filter them out yourself.',
        '4 items, the empty replaced with undefined':
            'The empty piece is an empty string, `""`, which is still a string.',
        'A runtime error':
            'Consecutive separators are perfectly legal; they just produce an empty piece.',
    },
    'How do you compare two strings for sort order?': {
        'a - b':
            "Subtracting strings is a TypeScript error (TS2362) and gives `NaN` at runtime, so it can't order anything.",
        'a.compareTo(b)':
            "`compareTo` is Java's method; JavaScript strings don't have it.",
        'a.equals(b)':
            '`equals` is Java too, and it would only say whether two strings match, not which comes first.',
    },
    'Does `s.toUpperCase()` change `s`?': {
        'Only for ASCII strings':
            'Immutability applies to every string, whatever characters it holds.',
        'Only if `s` was declared with `let`':
            "Even with `let`, a method can't rebind `s`; only `s = s.toUpperCase()` would.",
        'Yes, in place':
            'Strings are immutable; the method returns a new upper-cased string and leaves `s` as it was.',
    },
    '`"hello".indexOf("z")`?': {
        '`0`':
            "0 is a valid position, the start of the string, so it can't mean not found.",
        '`null`':
            "`null` is `match`'s not-found value; `indexOf` returns a number.",
        '`undefined`':
            '`indexOf` always returns a number; -1 is its not-found sentinel.',
    },
    '`"a-b-c".split("-", 2)`?': {
        '`["a", "b", "c"]`':
            'The second argument limits how many pieces come back, so only two are returned.',
        '`["a", "b-c"]`':
            'Some languages keep the remainder in the last piece; JavaScript discards it.',
        '`["a-b", "c"]`':
            'Splitting starts from the left, so the first piece is `"a"`.',
    },
    '`"x".repeat(3)`?': {
        '`"x3"`':
            "`repeat` doesn't append the count; it concatenates the string that many times.",
        '`3`':
            '`repeat` returns the repeated string, not a number.',
        '`["x", "x", "x"]`':
            'It returns one string, not an array; `Array(3).fill("x")` would be the array.',
    },
    'Under plain `strict`, what are the runtime value and static type of `"Hello"[10]`?': {
        'A thrown RangeError':
            'Reading past the end of a string never throws; you get `undefined`.',
        '`""`, typed `string`':
            "An out-of-range index isn't an empty string; there is no character there, so it is `undefined`.",
        '`undefined`, typed `undefined`':
            "The value is `undefined`, but the type comes from the string's index signature: `string`, unless `noUncheckedIndexedAccess` is on.",
    },
    '`"abc".includes("")`?': {
        'A compile error':
            '`includes("")` is valid; any string argument is allowed.',
        '`-1`':
            "`includes` returns a boolean; -1 is `indexOf`'s not-found value.",
        '`false`':
            'The empty string occurs at every position, so every string includes it.',
    },
    '`" a b ".trim().split(" ").length`?': {
        '3':
            'After `trim` only `"a b"` remains, and its single space separates two pieces, not three.',
        '4':
            '4 is what splitting the untrimmed string gives (an empty piece at each end); `trim` removed those spaces first.',
        '5':
            '5 is the character count of the original string; `split` returns pieces, not characters.',
    },
    'What does `"Straße".toUpperCase()` return?': {
        'It throws':
            'Case mapping handles any Unicode text; it never throws.',
        '`"STRAßE"`':
            "`ß` has an upper-case mapping, so it isn't left unchanged.",
        '`"STRAẞE"`':
            'The capital `ẞ` exists, but the standard mapping `toUpperCase` uses turns `ß` into `SS`.',
    },
    'What is `` `${1 + 1}` ``?': {
        'A compile error':
            "Any expression can go inside `${}`, and a template literal's type is `string`.",
        'The number 2':
            'A template literal always produces a string, even when its placeholder is a number.',
        'The string `"1 + 1"`':
            '`${}` evaluates its expression; only text outside the braces is kept literally.',
    },
    '`/^\\d+$/.test("12a")`?': {
        'It throws':
            "`test` just returns a boolean; a non-matching string isn't an error.",
        '`"12"`':
            '`test` returns a boolean, not the matched text; `match` is the one that returns text.',
        '`true`':
            "`^...$` makes the whole string have to be digits, and `a` isn't one.",
    },
    '`"b".localeCompare("a")` returns…': {
        '0':
            '0 means the strings are equal; `"b"` and `"a"` differ.',
        'A negative number':
            'A negative result means the receiver sorts first, but `"b"` comes after `"a"`.',
        '`true`':
            '`localeCompare` returns a number for sorting, not a boolean.',
    },
    '`"a,b".split("")`?': {
        '`["a", "b"]`':
            'The separator is `""`, not `","`, so the comma isn\'t removed; it becomes an element of its own.',
        '`["a,b"]`':
            "An empty separator splits between every character; the string isn't kept whole.",
        '`[]`':
            'Only splitting an empty string gives `[]`; here there are three characters to split.',
    },
    'What is `"abc".at(-1)`?': {
        '`""`':
            "`at(-1)` returns the last character; it doesn't produce an empty string.",
        '`"a"`':
            '-1 counts from the end; `"a"` is at index 0, the other end.',
        '`undefined`':
            '-1 is in range for `at`; `"abc"[-1]` is the form that gives `undefined`.',
    },
    'What is `"a-b-c".replaceAll("-", "+")`?': {
        'An error: `replaceAll` needs a regex':
            '`replaceAll` takes a plain string happily; only a regex without the `g` flag makes it throw.',
        '`"a+b-c"`':
            'Replacing just the first occurrence is `replace`; `replaceAll` does every one.',
        '`"a-b-c"`':
            'Strings are immutable, but `replaceAll` returns a new string with the changes made.',
    },
    'What is `"Hello".startsWith("he")`?': {
        '`"He"`':
            '`startsWith` returns a boolean, not the matched text.',
        '`true`':
            'The test is case-sensitive: `"H"` isn\'t `"h"`.',
        '`undefined`':
            '`startsWith` always returns a boolean, never `undefined`.',
    },
    'What is `"abc".padStart(5, "*")`?': {
        '`"*****abc"`':
            '5 is the target total length, not the number of pad characters to add.',
        '`"*abc*"`':
            "`padStart` only pads the start; it doesn't center the text.",
        '`"abc**"`':
            'Padding the end is `padEnd`; `padStart` adds to the left.',
    },
    'What are `"abc".substring(2, 0)` and `"abc".slice(2, 0)`?': {
        'Both `""`':
            '`substring` swaps its arguments when start is after end, so it returns `"ab"`.',
        'Both `"ab"`':
            "`slice` doesn't swap: with start after end it returns an empty string.",
        '`""` and `"ab"`':
            'Swapped: `substring` is the one that swaps its arguments; `slice` returns `""`.',
    },
    '`const re = /a/g; re.test("a"); re.test("a");` — the two results?': {
        '`false`, `false`':
            'The first call does find the `a`; a `/g` regex only goes wrong on the call after.',
        '`false`, then `true`':
            'The first test starts at index 0 and matches; it is the second that starts past the end.',
        '`true`, `true`':
            'The `g` flag makes `test` resume at `lastIndex` (1 after the first match), so the second search finds nothing.',
    },
    'What is `"a".codePointAt(0)`?': {
        '`"a"`':
            '`codePointAt` returns the numeric code, not the character.',
        '`1`':
            "Code points aren't alphabet positions; lower-case `a` is 97 in Unicode.",
        '`65`':
            '65 is upper-case `A`; lower-case letters start at 97.',
    },
    'What is `String.fromCharCode(72, 105)`?': {
        '`"72105"`':
            'The numbers are character codes, not digits to concatenate.',
        '`"hi"`':
            '72 is upper-case `H`; lower-case `h` would be 104.',
        '`["H", "i"]`':
            'It returns one string built from the codes, not an array.',
    },
    'What does `"x,y".split(",", 1)` return?': {
        '`"x"`':
            '`split` always returns an array, even with a limit of 1.',
        '`["x", "y"]`':
            'The limit of 1 caps the result at one piece, so `"y"` is dropped.',
        '`["x,y"]`':
            'The string is still split at the comma; the limit only discards the extra pieces.',
    },
    'How do you test `s` for a whole string of digits?': {
        '`/\\d+/.test(s)`':
            'Without `^` and `$`, a single digit anywhere passes, so `"a1"` is accepted.',
        '`Number(s) > 0`':
            '`Number` accepts `"1e3"`, `" 5 "` and `"1.5"`, and `"0"` fails `> 0`, so it isn\'t a digit test.',
        '`s.includes("0123456789")`':
            'That looks for the literal substring `0123456789`, not whether every character is a digit.',
    },
    'What does `/\\d+/.test("abc123")` return?': {
        '`"123"`':
            '`test` returns a boolean; getting the text `"123"` needs `match`.',
        "`false` — the string isn't all digits":
            'Only an anchored `^\\d+$` requires all digits; this unanchored one matches digits anywhere.',
        '`null`':
            "`null` is `match`'s no-match result; `test` returns `true` or `false`.",
    },
    'What does `"a1b22".match(/\\d+/g)` return?': {
        'An iterator of match objects':
            'That is `matchAll`; `match` with `g` returns a plain array of the matched strings.',
        '`["1"]`':
            'Only the first match comes back without `g`; with `g` you get every match.',
        '`true`':
            "`true` is `test`'s answer; `match` returns the matches themselves.",
    },
    'Why is `m[1]` typed `string | undefined` under `noUncheckedIndexedAccess`?': {
        'Because `match` returns `any`':
            '`match` is typed `RegExpMatchArray | null`, not `any`; the `undefined` comes from the flag.',
        'Because regexes are untyped':
            "Regex methods are fully typed; the compiler just can't see into the pattern to know which groups took part.",
        "It isn't; it's `string`":
            'Only without the flag; with `noUncheckedIndexedAccess`, every index read adds `| undefined`.',
    },
    'In a replacement string, what is `$<year>`?': {
        'A literal dollar sign':
            'A literal `$` in a replacement string is written `$$`.',
        'A template literal':
            'Template literals use backticks and `${}`; `$<name>` is replacement-string syntax.',
        'The whole match':
            'The whole match is `$&`; `$<year>` picks out just that named group.',
    },
    'Which flag makes `^` and `$` match at each line?': {
        '`g`':
            "`g` finds every match; it doesn't change what `^` and `$` mean.",
        '`i`':
            '`i` makes matching case-insensitive; the anchors still mean the start and end of the whole input.',
        '`s`':
            '`s` (dotAll) lets `.` match newlines; it is `m` that changes the anchors.',
    },
    'Why build patterns from user text carefully?': {
        "It's slower":
            "Speed isn't the issue; correctness is, since special characters change what the pattern means.",
        "User text can't contain letters":
            'User text can contain anything, letters included; the danger is punctuation that regexes treat specially.',
        "`new RegExp` can't take variables":
            '`new RegExp` exists precisely to build patterns from variables, which is exactly where escaping matters.',
    },
    'What is `"😀".length`?': {
        '1':
            '`length` counts UTF-16 code units, not visible characters, and this emoji takes two.',
        '4':
            '4 is its size in UTF-8 bytes; JavaScript strings are UTF-16, where it is two code units.',
        'It depends on the font':
            "`length` is a property of the string's encoding, which a font can't affect.",
    },
    'Which walks a string by code point?': {
        '`for (let i = 0; i < s.length; i++)`':
            'Indexing up to `length` walks UTF-16 code units, splitting an emoji into two surrogate halves.',
        '`s.charAt(i)`':
            '`charAt` reads a single code unit, so it returns half of a surrogate pair.',
        '`s.split("")`':
            '`split("")` separates code units, breaking surrogate pairs apart.',
    },
    'What splits text into user-perceived characters?': {
        '`Array.from(s)`':
            '`Array.from` iterates by code point, so a flag, or a letter plus a combining accent, still comes apart.',
        '`[...s]`':
            'Spreading uses string iteration, which is by code point, so multi-code-point characters get split.',
        '`s.split("")`':
            '`split("")` works on UTF-16 code units, which is even finer than code points.',
    },
    "Two strings look identical but aren't `===`. What's a likely cause?": {
        'Different fonts':
            'Fonts affect only how text is drawn; `===` compares the underlying code units.',
        'The `u` flag':
            '`u` is a regex flag; it has nothing to do with comparing two strings with `===`.',
        'Trailing zeros':
            'Trailing zeros matter for numbers; for strings that look identical, invisible code-point differences are the likely cause.',
    },
    'Why sort names with `localeCompare` rather than the default `sort()`?': {
        'The default sort is random':
            'The default sort is deterministic; it just orders by UTF-16 code units.',
        '`localeCompare` is faster':
            '`localeCompare` is typically slower; it is chosen for the right order, not for speed.',
        "`sort()` can't sort strings":
            '`sort()` sorts strings by default (it converts everything to strings first); it just uses code-unit order.',
    },
    'What does the `u` flag change in a regex?': {
        'It finds every match':
            'Finding every match is the `g` flag; `u` changes how the pattern reads characters.',
        'It makes the match case-insensitive':
            'Case-insensitivity is the `i` flag; `u` makes the regex read the input as code points.',
        'Nothing in modern engines':
            '`u` still matters: without it `.` matches a single code unit and can split an emoji in half.',
    },
})
