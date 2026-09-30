# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Why-not notes, month 2 (weeks 5-8) of the TypeScript Mastery quiz banks
# (TS_MASTERY_ROADMAP.md X-37): functions, callbacks and recursion, arrays
# and tuples, objects, JSON and interfaces.
#
# For each authored single-choice question, one note per wrong option saying
# what makes it tempting and why it fails. Keyed by question and option text,
# verbatim. exec()'d by tools/mastery_ts_why_not.py; check on its own with
#   python tools/check_ts_why_not.py tools/mastery_ts_whynot_m2.py --month 2
# ---------------------------------------------------------------------------

TS_WHY_NOT.update({
    'Where must an optional parameter appear?': {
        'Anywhere in the list':
            'Arguments fill parameters left to right, so an optional one before a required one could never be skipped. The compiler rejects that order (TS1016).',
        'First, so callers can omit the rest':
            'Putting it first is exactly what fails: `f(5)` would fill the optional slot, and the required ones after it would get nothing.',
        'Only as the sole parameter':
            'There is no such restriction: `(a: number, b?: number)` is fine. The only rule is that optional parameters come after the required ones.',
    },
    'What is the type of `x` in `function f(x = 5)`?': {
        'any':
            "A default is an initializer, so TypeScript infers the parameter's type from it, just as `let x = 5` infers `number`. No implicit `any` here.",
        'number | undefined':
            'Only the caller may omit it. Inside the body the default has already filled in any `undefined`, so `x` is plain `number`.',
        'unknown until annotated':
            'TypeScript never leaves a parameter as `unknown` on its own. With no annotation, the default value supplies the type.',
    },
    'How is a rest parameter typed?': {
        'As a tuple of unknown length':
            'A rest parameter can be typed as a tuple, but for any number of items the usual type is a plain array like `number[]`.',
        'As any[], always':
            'Only an unannotated rest parameter becomes `any[]`, and strict mode flags that. Annotate it with the element type, e.g. `...items: number[]`.',
        'Rest parameters cannot be typed':
            'They can: annotate the collected array, as in `(...items: number[])`. Leaving it off is what gives you an implicit `any[]`.',
    },
    'What does a function declared to return `void` promise?': {
        'That it never returns':
            "That is `never`. A `void` function normally returns; you just shouldn't use what it gives back.",
        'That it returns undefined and nothing else':
            'At runtime it usually does return `undefined`, but the type only tells callers not to use the value. A `() => void` slot can hold a function that returns a number.',
        'That it throws':
            "Throwing is what `never` describes. `void` says nothing about errors, only that the return value isn't meaningful.",
    },
    'What does the `?` in `function f(x?: number)` mean for the body?': {
        'x can be passed in any position':
            "`?` doesn't affect position. Arguments are still matched left to right; `x` is just allowed to be missing.",
        'x defaults to 0':
            '`?` supplies no value. An omitted `x` is `undefined`; you need `x = 0` to get a default.',
        'x is always present at runtime':
            'The opposite: `?` means the caller may leave it out, so inside the body `x` can be `undefined`.',
    },
    'Why can a `() => void` slot accept `() => number`?': {
        'It cannot — that is an error':
            'It is allowed on purpose, so callbacks like `xs.forEach(x => ys.push(x))` still type-check even though `push` returns a number.',
        'The compiler inserts a discard':
            'Nothing is inserted at runtime. The function still returns its number; the type system just tells callers to ignore it.',
        'number is assignable to void':
            'Assigning a `number` value to a `void` variable is an error. The rule is only about function return types in a `() => void` slot.',
    },
    '`function f(x: number, y?: number) { return y ?? x; }` — what is `f(3)`?': {
        'A compile error':
            '`y` is optional, so calling `f(3)` with one argument type-checks.',
        '`NaN`':
            'There is no arithmetic here. `??` just picks `x` when `y` is `undefined`.',
        '`undefined`':
            '`??` replaces `undefined` with its right side, so the result is `x`, not the missing `y`.',
    },
    '`function greet(name = "you") { … }` — what does `greet(undefined)` use for `name`?': {
        'A compile error':
            '`name` is optional because it has a default, and passing `undefined` explicitly is allowed.',
        '`"undefined"`':
            'Nothing is turned into a string. `undefined` counts as a missing argument, so the default is used.',
        '`undefined`':
            'Defaults exist for exactly this case: an `undefined` argument, passed or omitted, is replaced by the default.',
    },
    'Can you call `const f = () => 1;` on a line above its declaration?': {
        'Only in strict mode':
            'Strict mode makes no difference here. `const` is in the temporal dead zone before its line in every mode.',
        'Yes, arrows are hoisted':
            "Only `function` declarations are hoisted with their bodies. An arrow stored in a `const` doesn't exist until its line runs.",
        'Yes, but it returns `undefined`':
            'That is how `var` behaves: hoisted as `undefined`, so the call throws a TypeError. A `const` read before its line throws a ReferenceError.',
    },
    'What return type is inferred for `function f(n: number) { if (n > 0) return "pos"; }`?': {
        '`"pos"`':
            'The function can also run off the end without returning, which gives `undefined`. The inferred type includes that path.',
        '`string`':
            'The inferred return type keeps the literal `"pos"` rather than widening to `string`, and the path that falls through adds `undefined`.',
        '`void`':
            '`void` is inferred only when no path returns a value. Here one path returns `"pos"`.',
    },
    'Which type describes a function taking any number of strings and returning a string?': {
        '`(...parts: string) => string`':
            'A rest parameter always collects an array, so its type must be an array type like `string[]`, not `string`.',
        '`(parts: ...string[]) => string`':
            'The `...` goes before the parameter name, not inside the type: `(...parts: string[])`.',
        '`(parts: string) => string[]`':
            'That takes exactly one string and returns an array, the reverse of what was asked.',
    },
    '`const add = (a: number, b: number) => a + b; add(1, "2");` — result?': {
        '`"12"`':
            'That is what plain JavaScript would do. TypeScript checks each argument at the call, and `"2"` is not a `number`.',
        '`3`':
            "No coercion happens because the call is rejected first: a `string` can't be passed where `number` is declared.",
        '`NaN`':
            'The call never runs. The compiler rejects the `string` argument before anything could produce `NaN`.',
    },
    'Given overloads `parse(x: string): number` and `parse(x: string[]): number[]`, can you call `parse(v)` with `v: string | string[]`?': {
        'Only with `as any`':
            '`as any` would compile, but it hides the problem. The fix is a third overload that accepts `string | string[]`.',
        'Yes, it returns `number | number[]`':
            "Neither overload accepts a union, and the compiler doesn't try each member and combine the results.",
        'Yes, the implementation signature accepts it':
            'The implementation signature is invisible to callers. Only the overload signatures above it can be called.',
    },
    'What does a function with no `return` statement return?': {
        'Nothing — calling it is an error':
            'Calling it is fine. The call just produces `undefined`.',
        '`null`':
            "JavaScript never returns `null` by default. A function that doesn't return gives `undefined`.",
        '`void` as a runtime value':
            '`void` exists only in the type system. At runtime the value is `undefined`.',
    },
    '`function f(opts: { width?: number } = {})` — inside `f()`, what is `opts.width`?': {
        '0':
            'No default is filled in for properties. A missing property reads as `undefined`, not `0`.',
        'A thrown TypeError':
            "The default `{}` means `opts` is an object. Reading a missing property from it gives `undefined`; it doesn't throw.",
        '`null`':
            "JavaScript never gives `null` by default. A property that isn't there reads as `undefined`.",
    },
    'Why is a pure function easier to test?': {
        "It can't throw":
            'A pure function can still throw, e.g. on bad input. Purity is about depending only on inputs and having no side effects.',
        'It runs faster':
            "Purity isn't about speed. Tests are simpler because there's no setup or hidden state.",
        'TypeScript checks it more strictly':
            'The compiler treats pure and impure functions the same. The benefit is in how you test them, not in the type checking.',
    },
    'For `function f(a, b = 2, c) {}`, what is `f.length`?': {
        '`0`':
            '`a` has no default, so it counts. Only the parameters after the first default are left out.',
        '`2`':
            "`length` stops counting at the first default. `c` comes after `b = 2`, so it isn't counted.",
        '`3`':
            "`length` isn't the total number of parameters. It counts only those before the first default or rest parameter.",
    },
    '`function addItem(item: number, list: number[] = []) { list.push(item); return list; }` — do two calls share `list`?': {
        "It's a compile error":
            'It compiles fine. The question is only about what happens at runtime.',
        'Only if called with the same item':
            "The argument values don't matter. A default is evaluated again on every call that needs it.",
        'Yes — the default array is created once':
            "That is Python's behaviour. JavaScript runs the default expression on each call, so each call gets a new array.",
    },
    'Can you call a function declaration `function f() {}` on a line above it?': {
        'No — TDZ error':
            'The temporal dead zone applies to `let`, `const` and `class`. Function declarations are hoisted with their whole body.',
        'Only if it has no parameters':
            "Parameters don't affect hoisting. The whole declaration is available from the start of its scope.",
        'Only in strict mode':
            'Function declarations are hoisted in both strict and sloppy code.',
    },
    'What is `this` inside a plain `function` called as `f()` in a module?': {
        'The function itself':
            'A function never gets itself as `this` automatically. For a plain call, `this` is `undefined` in strict code.',
        'The global object':
            'That was true of sloppy scripts. Modules are always strict, so a bare call gets `this === undefined`.',
        '`null`':
            '`this` is never `null` by default. In strict code a bare call gets `undefined`.',
    },
    'What does `(...args: number[]) => …` accept?': {
        'At least one number':
            'A rest parameter can be empty: calling `f()` gives `args` as `[]`.',
        'Exactly one array':
            'The caller passes separate numbers, `f(1, 2)`. They are collected into the array; passing one array would be a type error.',
        'Only numbers in an array literal':
            "Callers don't write array literals. They pass separate numbers, or spread an existing array with `f(...xs)`.",
    },
    'How do you pass an array to a rest parameter?': {
        '`f([...xs])`':
            'That still passes a single argument: a new array. The spread has to be directly in the call, `f(...xs)`.',
        '`f(xs)`':
            'This passes the whole array as the first argument, so the compiler rejects it for `...items: number[]`.',
        '`f.apply(xs)`':
            '`apply` takes the `this` value first, so this would use `xs` as `this` and pass no arguments. Spreading is simpler anyway.',
    },
    'What does `function f(): never` promise?': {
        'It returns `null`':
            'Returning `null` is a normal return, and `never` rules out returning at all.',
        'It returns `undefined`':
            "That is `void`. `never` means the call doesn't return at all.",
        'It returns nothing useful':
            'That is `void`: it returns, and you ignore the value. `never` means it never returns.',
    },
    'Why are parameters with defaults usually placed last?': {
        'Defaults are slower in the middle':
            'Position has no effect on speed. It matters for how callers can leave arguments out.',
        "They must be, or it's a syntax error":
            'A default in the middle is legal. It is just awkward, because the caller has to pass `undefined` to use it.',
        'TypeScript reorders them':
            'TypeScript never changes parameter order. Arguments always match left to right as written.',
    },
    'What is an IIFE?': {
        'A generator':
            'Generators are `function*` functions that yield values. An IIFE is any function expression called right away.',
        'An imported function':
            'An IIFE is written and called in the same place. It has nothing to do with imports.',
        'An inline interface':
            "It isn't a type construct. IIFE stands for Immediately Invoked Function Expression.",
    },
    'Two overloads and an implementation — how many signatures can callers use?': {
        'One':
            'Each overload signature is a separate callable form. Callers see all of them, not just one merged signature.',
        "Only the implementation's":
            'The opposite: the implementation signature is the one callers cannot see.',
        'Three':
            "The implementation signature isn't counted. Callers only get the overloads written above it.",
    },
    'A closure keeps a reference to `count`. Another function changes `count`. What does the closure see?': {
        'A copy made when the closure was created':
            'No copy is made. The closure refers to the same variable, so it sees the latest value.',
        'The old value':
            'A closure keeps a reference to the variable, not its value at the time, so later changes show up.',
        '`undefined`':
            'The variable stays alive as long as the closure does, and it keeps whatever value it was last given.',
    },
    'Why is `const inc = (n: number) => n + 1` preferred to a `function` for a small helper?': {
        "Functions can't have types":
            '`function` declarations can be fully typed. This is about style and behaviour, not what can be annotated.',
        "It's faster":
            "There's no meaningful speed difference. The reasons are the shorter syntax, no own `this`, and no hoisting.",
        'Only arrows can be exported':
            '`export function` works fine. Both forms can be exported.',
    },
    'What is a pure function?': {
        'A function that returns `void`':
            'Returning `void` often means the function exists for its side effects, which is the opposite of pure.',
        'A function without parameters':
            'A function with parameters can be pure. Purity means no side effects and a result that depends only on its arguments.',
        'Any arrow function':
            "Arrow syntax doesn't make a function pure. An arrow can change outside state or read a global.",
    },
    "What does `function f(x: number | undefined)` require that `function f(x?: number)` doesn't?": {
        'A default value':
            'Neither form has a default. The difference is whether the caller may leave the argument out.',
        "Nothing — they're identical":
            'They differ at the call site: `x?: number` allows `f()`, while `x: number | undefined` still requires an argument.',
        '`strictNullChecks` off':
            'Both forms work with `strictNullChecks` on. They just differ in whether the argument may be omitted.',
    },
    'What do callers of an overloaded function see?': {
        'Both':
            'The implementation signature is hidden once overloads exist. Callers see only the overload list.',
        'Only the implementation signature':
            'The implementation signature is hidden. Callers see only the overloads above it.',
        'Whichever is more general':
            "The compiler doesn't choose the broader one. The implementation is never visible, however general it is.",
    },
    'In what order are overloads tried?': {
        'All at once, merging the results':
            "The results aren't merged. The first matching overload decides the return type.",
        'Bottom to top':
            'Resolution goes top to bottom, which is why the most specific overload goes first.',
        'Most specific first, automatically':
            "The compiler doesn't reorder by specificity. It uses your written order, so a broad overload listed first hides the narrower ones.",
    },
    'What does the compiler check about the implementation?': {
        'Nothing':
            'The implementation body is type-checked like any other function, and each overload must be compatible with its signature.',
        'Only the number of parameters':
            'It checks parameter and return types for compatibility, not just the count.',
        'That each branch returns what the matching overload promises':
            "It can't tell which branch handles which overload. It only checks the body against the implementation signature.",
    },
    'When is a union parameter better than overloads?': {
        'Never':
            'A union parameter is often better: when every input gives the same return type, overloads add nothing.',
        'When the function is async':
            "Being async doesn't matter. What matters is whether the return type depends on the argument type.",
        'When there are more than two types':
            "The number of types doesn't matter. What matters is whether the return type changes with the input.",
    },
    'A variable is `string | number`. The overloads accept `string` and `number` separately. Can you call it?': {
        'Only with `as any`':
            '`as any` would compile, but it hides the gap. Adding an overload that accepts `string | number` fixes it properly.',
        'Yes, if the implementation accepts the union':
            "The implementation signature is hidden from callers, so what it accepts doesn't help this call.",
        'Yes, the compiler splits the call':
            'The compiler never splits a union argument across overloads. One overload must accept the whole union.',
    },
    'What does a closure capture?': {
        'A snapshot of the value at creation time':
            'Nothing is copied at creation time. The closure keeps the variable itself, so later assignments show up.',
        'A snapshot of the values at creation':
            'No values are frozen when the closure is made. It reads the current value of each variable whenever it runs.',
        'Nothing; it copies its arguments':
            'Closures do capture outer variables, by reference. Arguments are a different thing.',
        'Nothing; parameters must be passed explicitly':
            'A closure can read any outer variable it names, without passing it in. That is the whole point of a closure.',
        'Only `const` variables':
            '`let` and `var` variables are captured too, and changes to them are visible, which is how a counter closure works.',
        'Only const bindings':
            'Any binding in scope is captured, `let` included. A counter closure usually captures a `let`.',
    },
    'Why do closures made in `for (var i…)` all see the same `i`?': {
        'Because of the event loop':
            'This happens even without async code. `var` creates a single variable that all the closures share.',
        "Closures can't capture loop variables":
            'They can. The catch is that `var` gives the whole loop a single `i`, so every closure captures the same one.',
        "They don't; each sees its own":
            'With `var` there is only one `i`. Each closure would get its own only with `let` in the loop header.',
    },
    '`const a = makeCounter(); const b = makeCounter();` — do they share a count?': {
        'Only if `count` is `const`':
            '`const` or not, each `makeCounter()` call creates a new variable, so the counters are separate.',
        "Only if they're called in the same tick":
            "Timing doesn't matter. Each factory call has its own variables.",
        'Yes, always':
            'Each call runs the factory body again and creates a new `count`. They would share only if `count` were declared outside.',
    },
    'Where is a `let` declared inside an `if` block visible?': {
        'Anywhere in the file':
            "`let` is block-scoped. It isn't visible outside the `{ }` it's declared in.",
        'Anywhere in the function':
            'That describes `var`, which is function-scoped. `let` stays inside its block.',
        'From the start of the function, as `undefined`':
            "That is how `var` behaves. A `let` can't be read before its line, and it stays inside the block.",
    },
    'What is the temporal dead zone?': {
        'A block with no variables':
            "It isn't about empty blocks. It's the part of a scope before a `let` or `const` is declared.",
        'Code after a `return`':
            'Code after a `return` is unreachable code, which is a different thing. The TDZ is the part before a declaration.',
        'The time between two awaits':
            "It has nothing to do with async. It's about reading a `let` or `const` before its declaration line.",
    },
    'Why are arrow functions the default for callbacks?': {
        'They allow default parameters, which function expressions do not':
            'Function expressions support default parameters too. The real difference is how `this` is bound.',
        'They are faster':
            "Speed isn't the reason; the difference is negligible. Arrows are the default because they keep the surrounding `this`.",
        'They cannot be passed to higher-order functions otherwise':
            'Any function value can be passed to `map`, `filter` and the rest. Arrows are just the safer choice because of `this`.',
    },
    '`[1, 2, 3].map((x) => x * 2).filter((x) => x > 2)`?': {
        '`[2, 4, 6]`':
            "That's the result after `map` alone. `filter` then drops the `2`, since it isn't greater than 2.",
        '`[3]`':
            'That applies `filter` to the original numbers. `map` runs first, so `filter` sees `[2, 4, 6]`.',
        '`[6]`':
            '`filter` keeps every element above 2, so both `4` and `6` stay.',
    },
    '`for (var i = 0; i < 3; i++) setTimeout(() => console.log(i));` prints…': {
        '`0 0 0`':
            'The callbacks run after the loop ends, so they read `i` once it has reached its final value, 3.',
        '`0 1 2`':
            "That's what `let` would print, with a new `i` per iteration. `var` gives the whole loop a single `i`.",
        '`undefined` three times':
            "`i` is still in scope when the callbacks run. It's 3 because the loop has finished.",
    },
    'What does a typical `once(fn)` helper return?': {
        'A boolean saying whether `fn` has run':
            '`once` returns a function you call in place of `fn`, not a flag. The flag is kept privately inside that function.',
        'A promise':
            '`once` is synchronous. It wraps `fn` in a closure; no promise is involved.',
        'The result of `fn()` immediately':
            "It doesn't call `fn` right away. It returns a wrapper, and `fn` runs on the first call to the wrapper.",
    },
    'What happens to `function fact(n: number): number { return n * fact(n - 1); }`?': {
        'Compile error: missing base case':
            "TypeScript doesn't check whether recursion terminates. This compiles; it fails at runtime.",
        'It returns 0':
            'Nothing ever returns: every call makes another call, until the stack runs out.',
        'It returns `NaN`':
            "No call ever finishes, so there's no value at all. The program crashes with a RangeError.",
    },
    "How does naive recursive Fibonacci's running time grow?": {
        'Linearly':
            'Each call makes two more, so the number of calls roughly doubles as `n` grows, not by a fixed amount.',
        'Logarithmically':
            'The calls branch rather than halving the input, so the growth is exponential, not logarithmic.',
        'Quadratically':
            'Quadratic growth would be manageable. The two-way branching makes the call count exponential.',
    },
    '`[].reduce((acc, x) => acc + x, 0)`?': {
        'It throws':
            'It throws only without an initial value. With `0` given, an empty array just returns it.',
        '`NaN`':
            "No addition ever happens: the callback isn't called on an empty array.",
        '`undefined`':
            '`reduce` returns the accumulator, and it starts at the initial value `0`.',
    },
    'With `const compose = (f, g) => (x) => f(g(x))`, `double = x => x * 2` and `inc = x => x + 1`, what is `compose(double, inc)(3)`?': {
        '6':
            'That doubles 3 and ignores `inc`. `compose` runs both functions.',
        '7':
            "That's `inc(double(3))`, left to right. `compose(f, g)` runs `g` first, so `inc` goes first.",
        '9':
            '`compose(double, inc)(3)` is `double(inc(3))`, which is `double(4)`, so 8.',
    },
    'How do you type a callback that takes a number and returns a boolean?': {
        '`(number) => boolean`':
            "In a function type, a single word is taken as the parameter's name. This declares a parameter called `number`, typed implicitly `any`.",
        '`Function<number, boolean>`':
            "`Function` isn't generic and can't take type arguments. Write the signature as an arrow type.",
        '`function(number): boolean`':
            "That isn't TypeScript syntax. Function types are written like arrows: `(n: number) => boolean`.",
    },
    '`[3, 1, 2].sort((a, b) => b - a)`?': {
        '`[1, 2, 3]`':
            "That's what `a - b` gives. Here `b - a` puts larger numbers first.",
        '`[2, 1, 3]`':
            "That isn't sorted at all. The comparator's sign decides the order, and `b - a` sorts descending.",
        '`[3, 1, 2]`':
            "That's the input order. `sort` reorders the array in place using the comparator.",
    },
    '`[].every((x) => x > 0)`?': {
        'It throws':
            "`every` on an empty array doesn't throw. It returns without calling the callback.",
        '`false`':
            'No element fails the test, so `every` has nothing to disprove and returns `true`.',
        '`undefined`':
            '`every` always returns a boolean, never `undefined`.',
    },
    'A recursive function recurses once per item on a list of a million items. What happens in Node?': {
        'It runs fine; Node optimises tail calls':
            "Node (V8) doesn't eliminate tail calls, so every call keeps its stack frame.",
        'It runs, just slowly':
            "Speed isn't the problem. The stack holds roughly ten thousand frames, so a million-deep recursion crashes.",
        'TypeScript refuses to compile it':
            "TypeScript doesn't check recursion depth. It compiles and then fails at runtime.",
    },
    'What does `["10", "10", "10"].map(parseInt)` return?': {
        'A compile error':
            "`parseInt` takes `(string, radix?)`, and `map`'s callback shape fits it, so this compiles.",
        '`["10", "10", "10"]`':
            '`map` returns what the callback returns, and `parseInt` returns numbers, not the original strings.',
        '`[10, 10, 10]`':
            '`map` also passes the index, which `parseInt` uses as the radix: base 0 means default, base 1 is invalid (NaN), and base 2 reads `"10"` as 2.',
    },
    'What is `[].some((x) => true)`?': {
        'A thrown error':
            "`some` on an empty array doesn't throw. It returns without calling the callback.",
        '`true`':
            'The callback never runs because there are no elements, so nothing can make `some` return `true`.',
        '`undefined`':
            '`some` always returns a boolean, never `undefined`.',
    },
    'What does `[1, 2, 3, 4].findLast((n) => n % 2 === 1)` return?': {
        '`1`':
            '`1` is the first odd number. `findLast` searches from the end, so it finds `3` first.',
        '`4`':
            '`4` is even, so it fails the test. `findLast` returns the last element that passes.',
        '`[1, 3]`':
            "That's what `filter` would return. `findLast` returns a single element, not an array.",
    },
    'What does a higher-order function do?': {
        'Calls itself':
            "That's a recursive function. Higher-order means taking or returning functions.",
        'Only works on arrays':
            '`once`, `compose` and `debounce` have nothing to do with arrays. The term is about functions as values.',
        'Runs at a higher priority':
            "It isn't about scheduling. It means the function works with other functions as values.",
    },
    '`const twice = (f: (x: number) => number) => (x: number) => f(f(x));` — what is `twice((n) => n + 3)(1)`?': {
        '`1`':
            "That's the input unchanged. `twice` applies `n + 3` two times.",
        '`4`':
            'That applies the function only once. `twice` calls `f` again on the result: `f(4)` is 7.',
        '`6`':
            '6 is just `3 + 3`, dropping the starting 1. `twice` nests the calls: `f(f(1))` = `f(4)` = 7.',
    },
    'Why prefer `for…of` to `forEach` when you need to stop early?': {
        "They're the same":
            'They differ exactly here: `break` works in `for…of`, but `forEach` can only be stopped by throwing.',
        '`forEach` is slower':
            "Speed isn't the issue. `forEach` always visits every element, and there is no way to stop it early.",
        "`for…of` can't access the index":
            'It can: `for (const [i, x] of arr.entries())`. The real difference is that `break` works.',
    },
    'What does memoisation trade?': {
        'Correctness for speed':
            'A correct memoised function returns the same results. It just avoids recomputing them.',
        'Readability for types':
            'Memoisation is a runtime technique. It has nothing to do with types.',
        'Time for memory':
            "That's the wrong way round: it uses more memory to save time.",
    },
    'What is tail recursion, and does Node optimise it?': {
        'A loop — yes':
            "A tail call is still a function call, and Node doesn't turn it into a loop.",
        'Recursion on the last element — yes':
            "It isn't about the last element; it's about the call being the last action. And Node doesn't optimise it.",
        'Recursion that returns early — only in strict mode':
            "Returning early isn't what makes a call a tail call, and strict mode doesn't make Node optimise tail calls.",
    },
    'How do you turn recursion into iteration in general?': {
        "It isn't possible":
            "It's always possible. The call stack is just a stack, and you can keep your own in an array.",
        'Use `setTimeout`':
            "`setTimeout` only postpones work. It doesn't replace the pending work the call stack was holding.",
        'Use `try`/`catch`':
            "`try`/`catch` handles errors. It doesn't manage the work that recursion leaves pending.",
    },
    'What does `reduce` without an initial value do on `[]`?': {
        'Returns `0`':
            "There's no built-in default of `0`. With no initial value and no elements, `reduce` has nothing to return and throws.",
        'Returns `[]`':
            "`reduce` doesn't return the array. With no initial value and no elements, it throws.",
        'Returns `undefined`':
            "It doesn't quietly return `undefined`. It throws `TypeError: Reduce of empty array with no initial value`.",
    },
    'What does `pipe(f, g, h)(x)` compute?': {
        '`[f(x), g(x), h(x)]`':
            "`pipe` chains the functions, feeding each result into the next. It doesn't collect separate results.",
        '`f(g(h(x)))`':
            "That's `compose`, which runs right to left. `pipe` runs `f` first.",
        '`f(x) + g(x) + h(x)`':
            "Nothing is added up. Each function receives the previous one's output.",
    },
    "A callback's parameter is typed `(item: T, index: number) => boolean`. Must your arrow declare `index`?": {
        'Only for arrays':
            "Arrays aren't special. Any callback may declare fewer parameters than its type offers.",
        'Only with `strict`':
            "Strict mode doesn't change this. Having fewer parameters is always assignable.",
        'Yes, both are required':
            'Declaring fewer parameters is fine; the extra arguments are simply ignored. Only declaring more than offered is an error.',
    },
    'What is a predicate function?': {
        'A function that runs first':
            'Order has nothing to do with it. A predicate returns `true` or `false` about its argument.',
        'A function with no side effects':
            "That's a pure function. A predicate is defined by returning a boolean.",
        'A generic function':
            'Being generic is unrelated. A predicate is any function that returns a boolean test result.',
    },
    'Why does `const fns = [1, 2, 3].map((n) => () => n);` give three functions returning 1, 2, 3?': {
        "It's a compile error":
            'An arrow returning an arrow is valid, and the result is typed `(() => number)[]`.',
        'They all return 3':
            'All returning 3 is the `var` loop bug. Each `map` callback call gets its own `n`.',
        'They all return undefined':
            'Each inner arrow keeps the `n` from its own call, so it returns that number.',
    },
    'What does `Array.from("ab", (c) => c + c)` return?': {
        '`"aabb"`':
            '`Array.from` always returns an array, not a joined string.',
        '`["a", "b"]`':
            'The second argument is a mapping function, so each character is doubled.',
        '`["ab", "ab"]`':
            'A string is iterated one character at a time, so `c` is `"a"` and then `"b"`, not the whole string.',
    },
    'How deep can naive recursion go in Node before a stack overflow?': {
        'About a million':
            'A million frames is far beyond the default stack. It overflows around ten thousand.',
        'Exactly 100':
            "There's no fixed limit like 100. It depends on stack size and frame size, and is typically around ten thousand.",
        'Unlimited':
            "The stack is a fixed-size region, and Node doesn't grow it, so deep recursion eventually throws a RangeError.",
    },
    'What does `once(fn)` usually guarantee?': {
        "`fn` can't throw":
            "`once` doesn't catch errors. If `fn` throws on its first run, the error reaches the caller.",
        '`fn` runs exactly once immediately':
            "`once` doesn't call `fn` right away. It runs on the first call to the wrapper, if there is one.",
        '`fn` runs once per second':
            "That's throttling. `once` never runs `fn` a second time.",
    },
    'What makes `sort((a, b) => a - b)` correct for numbers?': {
        'It avoids mutating the array':
            "`sort` always mutates the array; the comparator doesn't change that. Copy first with `[...xs]` if needed.",
        'It sorts strings too':
            '`a - b` on strings gives `NaN`. String sorting uses `localeCompare` or the default comparison.',
        "It's stable only for numbers":
            '`sort` is stable for every element type. The comparator matters because the default compares strings.',
    },
    'What does `const add = (a: number) => (b: number) => a + b; add(2)` return?': {
        'A compile error':
            'Returning a function from a function is valid. `add(2)` has type `(b: number) => number`.',
        '`2`':
            '`add` returns the inner arrow, not `a`. You get the number only by calling that arrow.',
        '`NaN`':
            'No arithmetic runs yet. `a + b` happens only when the returned function is called with `b`.',
    },
    'What is the type of `const add = (a: number) => (b: number) => a + b;`?': {
        '(a: number) => number':
            "The outer arrow's body is another arrow, so it returns a function, not a number.",
        '(a: number, b: number) => number':
            "That's a two-parameter function called as `add(1, 2)`. This one takes its arguments one at a time.",
        'number':
            '`add` is a function, not the result of calling it. You get a number only from `add(1)(2)`.',
    },
    "Why does `['a','b'].map((s) => s.length)` type-check even though `map` passes three arguments to its callback?": {
        'The extra arguments are silently dropped at runtime only':
            'This is a compile-time rule, not just runtime behaviour: a callback with fewer parameters is assignable to a type with more.',
        'TypeScript infers the missing parameters as any':
            "Nothing is inferred for parameters you don't declare. They don't exist in your callback's type.",
        'map special-cases single-parameter callbacks':
            '`map` has no special case. The general assignability rule allows fewer parameters for every function type.',
    },
    'In `const shout = pipe<string>(f, g)`, what does `pipe` need to guarantee about `f` and `g`?': {
        'Both must return void':
            'A `void` stage would pass nothing useful on. Each stage must return a `string` for the next one to take.',
        'Neither — pipe erases the types at runtime':
            'Types are erased at runtime, but the compiler checks them first. That check is exactly the guarantee this `pipe` gives.',
        'f must return the argument type of g, which can differ from string':
            "That's true of a pipeline typed with a separate generic per stage. This `pipe` is typed `Array<(x: T) => T>`, so every stage stays `string`.",
    },
    'What two things does every recursive function need?': {
        'A global variable and a return':
            'Recursion uses parameters, not globals. It needs a stopping case and a step that shrinks the input.',
        'A loop and a counter':
            'The recursive calls take the place of the loop. A counter is just one way to make the input shrink.',
        'Two recursive calls':
            'One recursive call is enough, as in factorial. What matters is reaching the base case.',
    },
    'What happens when recursion goes about ten thousand calls deep in Node?': {
        'A compile error':
            "TypeScript doesn't track recursion depth. This is a runtime failure.",
        'It silently returns `undefined`':
            "It doesn't fail silently. Node throws a RangeError when the stack is full.",
        'Node grows the stack forever':
            "The call stack has a fixed size, so it can't grow forever.",
    },
    'Why does naive `fib(40)` take so long?': {
        'Numbers get too big':
            '`fib(40)` is about 100 million, well within safe integers. The problem is the number of calls.',
        'Recursion is slow in JavaScript':
            'Function calls are cheap. The problem is that the naive version makes exponentially many of them.',
        'The stack limit makes it retry':
            "There's no retrying. `fib(40)` is only 40 frames deep; it's slow because of the total number of calls.",
    },
    "Why annotate a recursive function's return type?": {
        'It makes recursion faster':
            "Annotations are erased, so they don't affect speed. They help the compiler and the reader.",
        'It raises the stack limit':
            "Types are erased, so annotations can't change the runtime stack size.",
        "It's required for every function":
            'Most return types can be inferred. Recursive functions are the case where inference can fail.',
    },
    'When is recursion clearly better than a loop?': {
        'Always':
            "A linear process like counting or summing is usually clearer as a loop, and doesn't risk overflowing the stack.",
        'For summing an array':
            'Summing is linear. A loop does it with no risk of overflowing the stack.',
        'Never — loops are always better':
            'Trees and nested data are naturally recursive. A loop would need an explicit stack for them.',
    },
    'Which of these MUTATES the array it is called on?': {
        'filter':
            '`filter` returns a new array with the matching elements and leaves the original alone.',
        'map':
            "`map` builds a new array from the callback's results; the original is unchanged.",
        'slice':
            "`slice` copies part of the array into a new one. It's `splice`, the similar name, that mutates.",
    },
    'What is the difference between `slice` and `splice`?': {
        'They are aliases':
            "They're different methods with names that look alike. One copies, the other edits the array in place.",
        'slice mutates, splice copies':
            "It's the other way round: `slice` leaves the array alone, and `splice` changes it.",
        'splice only works on strings':
            "`splice` is an array method, and strings don't have it. Strings have `slice`.",
    },
    'What does `[1, 2, 3].reduce((a, b) => a + b)` return without an initial value?': {
        '6, using 0 as the seed':
            'The total is right, but no `0` is used. Without a seed, the first element becomes the accumulator.',
        'A TypeError':
            'It throws only on an empty array. With three elements, the first one becomes the seed.',
        'undefined':
            '`reduce` returns the final accumulator, `1 + 2 + 3`, not `undefined`.',
    },
    'What is a tuple type `[string, number]`?': {
        'A union of string and number':
            'A union is one value of either type. A tuple holds several values, each with its own type by position.',
        'An array that can hold either type in any position':
            "That's `(string | number)[]`. A tuple fixes which type goes in each position, and how many positions there are.",
        'An object with two keys':
            'A tuple is an array, indexed by `0` and `1`, not by named keys.',
    },
    'What does `[10, 9, 1].sort()` return without a comparator?': {
        'A type error':
            'Calling `sort()` with no comparator type-checks on any array. The surprise comes at runtime.',
        '[1, 9, 10]':
            'That needs a numeric comparator. The default converts elements to strings, and `"10"` comes before `"9"`.',
        '[10, 9, 1]':
            '`sort` reorders the array. It compares the numbers as strings, so `10` goes before `9`.',
    },
    'What is the difference between `find` and `filter`?': {
        'They are aliases':
            'They return different things: `find` returns one element or `undefined`, and `filter` returns an array.',
        'filter stops at the first match':
            "That's `find`. `filter` checks every element and collects all the matches.",
        'find returns an index':
            "That's `findIndex`. `find` returns the element itself.",
    },
    '`[1, 2, 3].slice(1)`?': {
        '`2`':
            '`slice` returns an array, even for a single element. `2` is what `xs[1]` gives.',
        '`[1, 2]`':
            "That's `slice(0, 2)`. With a single argument, `slice` copies from that index to the end.",
        '`[1]`':
            'That keeps what comes before index 1. `slice(1)` keeps everything from index 1 on.',
    },
    '`const a = [1, 2, 3]; a.splice(1, 1);` — what is `a` now?': {
        '`[1, 2, 3]`':
            "`splice` changes the array in place. The original doesn't survive, unlike with `slice`.",
        '`[1, 2]`':
            '`splice(1, 1)` removes one element starting at index 1, which is the `2`, not the last one.',
        '`[2]`':
            '`[2]` is what `splice` returns: the removed items. The array `a` keeps the rest.',
    },
    '`[..."ab", ..."cd"]`?': {
        'A compile error':
            'Spreading a string into an array literal is valid, because strings are iterable.',
        '`"abcd"`':
            'An array literal always creates an array. To get a string back you\'d need `.join("")`.',
        '`["ab", "cd"]`':
            'Spreading a string gives its characters, not the whole string as one element.',
    },
    '`Array.from({ length: 3 }, (_, i) => i * i)`?': {
        '`[0, 0, 0]`':
            "The mapper's second argument is the index, so each slot gets `i * i`, not a fixed value.",
        '`[1, 4, 9]`':
            'Indexes start at 0, so the squares are of 0, 1 and 2.',
        '`[undefined, undefined, undefined]`':
            "That's without a mapper. Here the mapper fills each slot with `i * i`.",
    },
    '`[1, [2, [3]]].flat()`?': {
        '`[1, 2, 3]`':
            "`flat()` with no argument flattens only one level. You'd need `flat(Infinity)` or `flat(2)`.",
        '`[1, [2, [3]]]`':
            '`flat()` does flatten one level, so the `[2, [3]]` wrapper is removed.',
        '`[[1], [2], [3]]`':
            '`flat` removes nesting; it never adds it. Here it unwraps the inner array by one level.',
    },
    '`const xs: readonly number[] = [1]; xs.push(2);` — what happens?': {
        'A runtime error only':
            'The compiler catches it first: `readonly number[]` has no `push` method at all.',
        'A warning':
            "TypeScript doesn't give warnings; it reports an error. The readonly type simply has no `push`.",
        '`xs` becomes [1, 2]':
            "It doesn't compile. At runtime the array is an ordinary one, but the type removes `push`.",
    },
    '`[0, 1, 2].findIndex((x) => x > 5)`?': {
        '`3`':
            '`3` would be a valid-looking index just past the end. `findIndex` returns `-1` for no match.',
        '`null`':
            "Array methods don't return `null`. `findIndex` returns `-1`.",
        '`undefined`':
            "That's what `find` returns. `findIndex` returns `-1`.",
    },
    '`[1, 2, 3].indexOf("2")` in TypeScript?': {
        '`-1`':
            "That's what plain JavaScript returns. TypeScript rejects the call because a `string` can't be passed where a `number` is expected.",
        '`1`':
            '`indexOf` uses `===`, so `"2"` wouldn\'t match `2` even in JavaScript. TypeScript rejects the call anyway.',
        '`undefined`':
            "`indexOf` returns a number, never `undefined`, and here the call doesn't even compile.",
    },
    'What type does `const mixed = [1, "a"]` get?': {
        '`[1, "a"]`':
            "Without `as const`, the literals widen, and an array literal doesn't become a tuple.",
        '`[number, string]`':
            'An array literal is inferred as an array, not a tuple. You get a tuple by annotating it or using `as const`.',
        '`any[]`':
            "TypeScript infers the union of the element types, so there's no `any`.",
    },
    'What type does `const pair = [1, "a"] as const` get?': {
        '`(string | number)[]`':
            "That's without `as const`. The assertion keeps both the positions and the literal values.",
        '`[number, string]`':
            '`as const` also keeps the literals `1` and `"a"` and makes the tuple readonly.',
        '`readonly (1 | "a")[]`':
            '`as const` keeps the positions: it gives a tuple, not an array of a union.',
    },
    '`[5, 1, 10].sort((a, b) => a - b)`?': {
        '`[1, 10, 5]`':
            "That's the default string order. The numeric comparator puts 5 before 10.",
        '`[10, 5, 1]`':
            "That's descending, which is `b - a`. A negative `a - b` puts `a` first.",
        '`[5, 1, 10]`':
            '`sort` reorders in place, and the comparator puts the numbers in ascending order.',
    },
    'What does `[NaN].includes(NaN)` return, and `[NaN].indexOf(NaN)`?': {
        '`false` and `-1`':
            '`includes` uses SameValueZero, which treats `NaN` as equal to `NaN`. So it returns `true`.',
        '`false` and `0`':
            "`includes` finds `NaN`, and `indexOf` uses `===`, which can't find it.",
        '`true` and `0`':
            '`indexOf` uses `===`, and `NaN === NaN` is false, so it returns `-1`.',
    },
    'What does `[3, 20, 100].sort()` return?': {
        '`[100, 3, 20]`':
            'As strings, `"20"` comes before `"3"`, because `"2"` is less than `"3"`.',
        '`[20, 3, 100]`':
            '`"100"` sorts first because `"1"` is less than `"2"`, so `20` can\'t lead.',
        '`[3, 20, 100]`':
            "That's numeric order. With no comparator, `sort` compares strings.",
    },
    '`const grid = Array(2).fill([]); grid[0].push(1);` — what is `grid[1].length`?': {
        'A TypeError':
            '`grid[0]` is an array, so `push` works. Nothing throws.',
        '`0`':
            '`fill` puts the SAME array in both slots, so pushing through `grid[0]` shows up in `grid[1]`.',
        '`2`':
            "Only one `push` ran. There's a single shared array, and it now has one element.",
    },
    'What does `[1, 2, 3].fill(0, 1)` return?': {
        '`[0, 0, 0]`':
            'The second argument is the start index, so index 0 keeps its `1`.',
        '`[0, 2, 3]`':
            'That fills only index 0. Here filling starts at index 1 and runs to the end.',
        '`[1, 2, 3]`':
            '`fill` mutates the array and returns it, so the values change.',
    },
    'What is `[, 1].length`?': {
        'A syntax error':
            'Elisions (empty slots) in array literals are valid syntax.',
        '`0`':
            "The hole still counts toward `length`. It's an empty slot, not a missing one.",
        '`1`':
            'The leading comma creates a slot at index 0, so the `1` is at index 1 and the length is 2.',
    },
    'What does `[1, [2, [3, [4]]]].flat(Infinity)` return?': {
        'A RangeError':
            '`Infinity` is a valid depth for `flat`. It means flatten everything.',
        '`[1, 2, [3, [4]]]`':
            "That's `flat()` with the default depth of 1. `Infinity` keeps going to the bottom.",
        '`[1, [2, [3, [4]]]]`':
            '`flat` always removes some nesting. `Infinity` removes all of it.',
    },
    'What does `[..."abc"].reverse().join("")` return?': {
        'A syntax error':
            'Spreading a string into an array literal is valid syntax.',
        '`"abc"`':
            '`reverse` changes the order of the character array before `join` runs.',
        '`["c", "b", "a"]`':
            '`join("")` turns the array back into a string.',
    },
    'Which of these does NOT mutate: `reverse`, `sort`, `toReversed`, `splice`?': {
        '`reverse`':
            '`reverse` reverses the array in place.',
        '`sort`':
            '`sort` sorts in place. `toSorted` is the copying version.',
        '`splice`':
            '`splice` removes and inserts elements in the original array.',
    },
    'What does `xs.with(1, "x")` do?': {
        'Inserts `"x"` at index 1':
            "`with` replaces the element at index 1. It doesn't insert, so the length stays the same.",
        'Replaces index 1 in place':
            'That\'s `xs[1] = "x"`. `with` leaves `xs` unchanged and returns a copy.',
        'Returns `"x"`':
            'It returns the whole new array, not the value you put in.',
    },
    'What is the type of the element in `const [first] = [1, 2]` under `noUncheckedIndexedAccess`?': {
        '`1`':
            'Literals in an array widen to `number` unless you use `as const`.',
        '`never`':
            '`never` would mean no value is possible. Here the element may just be missing.',
        '`number`':
            "That's without the flag. `[1, 2]` is inferred as `number[]`, so reading index 0 may be `undefined`.",
    },
    'What does `Object.keys([4, 5])` return?': {
        '`[0, 1]`':
            'Object keys are always strings, and array indexes are too.',
        '`[4, 5]`':
            'Those are the values. `Object.values` returns them; `Object.keys` returns the indexes as strings.',
        '`[]`':
            'Array indexes are own enumerable keys, so `Object.keys` lists them.',
    },
    'How do you remove duplicates from an array of primitives?': {
        '`Array.dedupe(xs)`':
            "There's no `Array.dedupe`. Put the values in a `Set` and spread it back into an array.",
        '`xs.filter(Set)`':
            '`filter` needs a predicate. `Set` is a constructor, and calling it without `new` throws.',
        '`xs.unique()`':
            'Arrays have no `unique` method. `[...new Set(xs)]` is the usual idiom.',
    },
    'What does `xs.findIndex(p)` return when nothing matches?': {
        '`null`':
            "Array methods don't return `null`. `findIndex` returns `-1`.",
        '`undefined`':
            "That's what `find` returns. `findIndex` returns the number `-1`.",
        '`xs.length`':
            '`xs.length` would look like a real index just past the end. The no-match value is `-1`.',
    },
    'What type does `const p = [1, "a"]` get?': {
        '`[number, string]`':
            'An array literal is inferred as an array, not a tuple. Annotate it or use `as const` to get a tuple.',
        '`any[]`':
            'The element types are known, so TypeScript infers their union, not `any`.',
        '`readonly [1, "a"]`':
            "That's what `as const` gives. Without it, the literals widen and you get an array.",
    },
    'What is `pair[2]` for `pair: [string, number]`?': {
        '`never`, with no error':
            "The compiler doesn't quietly give `never`. It reports that index 2 is out of range for a length-2 tuple.",
        '`string | number`':
            "That's the type for a numeric index it can't check. A literal `2` is checked against the tuple's length.",
        '`undefined`':
            'At runtime it would be `undefined`, but the compiler rejects the index before that.',
    },
    'Why prefer `readonly [number, number]` for a return type?': {
        "It's faster":
            "`readonly` is erased at compile time, so it can't affect speed.",
        "Mutable tuples can't be returned":
            'Mutable tuples can be returned. The issue is that `push` can break the fixed length the type promises.',
        'Only readonly tuples can be destructured':
            'Mutable tuples can be destructured too. `readonly` is about stopping mutation.',
    },
    'What does `[name: string, ...scores: number[]]` describe?': {
        'An array of strings and numbers in any order':
            'Order is fixed: the first element is a string, and every element after it is a number.',
        'An object with `name` and `scores`':
            'The labels `name` and `scores` are only for readability. The type is still an array.',
        'Exactly two elements':
            'The rest element `...scores` allows any number of numbers after the string, including none.',
    },
    'What is each element of `Object.entries({ a: 1 })`?': {
        'A `Map` entry object':
            '`Object.entries` returns plain arrays, not `Map` entry objects.',
        'A `string`':
            "That's what `Object.keys` gives. Each entry pairs the key with its value.",
        'A `{ key, value }` object':
            'Entries are two-element arrays, `[key, value]`, not objects with named fields.',
    },
    "What does `xs.toSorted()` do that `xs.sort()` doesn't?": {
        'Sorts faster':
            'It uses the same sorting; the only difference is that it copies instead of mutating.',
        'Sorts in place and returns nothing':
            "That's what `sort` does, and `sort` also returns the array. `toSorted` returns a new array.",
        'Sorts numbers correctly by default':
            'Its default comparison is still by string, just like `sort`. Numbers need `(a, b) => a - b`.',
    },
    'What is `[1, 2, 3].at(-1)` typed as?': {
        '`3`':
            "Array literals widen to `number[]`, so there's no literal `3` in the type.",
        '`any`':
            '`at` is typed, so the result is based on the element type, not `any`.',
        '`number`':
            '`at` is declared to return `T | undefined` even without `noUncheckedIndexedAccess`, because the index may be out of range.',
    },
    'Why does `new Array(3).map((_, i) => i)` not give `[0, 1, 2]`?': {
        "Arrays can't be created with `new`":
            '`new Array(3)` is valid and creates an array of length 3 with three holes.',
        'It gives `[0, 1, 2]`':
            'It gives an array with three holes. `map` skips holes, so nothing is filled in.',
        "`map` can't use the index":
            '`map` does pass the index. It just never calls the callback for holes.',
    },
    'What does `Object.groupBy(xs, f)` return?': {
        'A `Map`':
            "That's `Map.groupBy`. `Object.groupBy` returns a plain object keyed by the group key.",
        'A count per key':
            'It collects the items themselves into arrays, not their counts.',
        'An array of arrays':
            "The groups are values of an object keyed by the callback's result, not an array of arrays.",
    },
    'How is `structuredClone(o)` different from `{ ...o }`?': {
        'It freezes the copy':
            "The copy isn't frozen. `structuredClone` makes an independent deep copy you can change.",
        'It only copies arrays':
            'It clones objects, Maps, Sets, Dates and more, not just arrays.',
        "It's the same":
            'Spread copies only the top level, so nested objects stay shared. `structuredClone` copies them too.',
    },
    'What type does `JSON.parse(text)` return?': {
        'Record<string, unknown>':
            "It's typed `any`, not a record. The parsed value might not even be an object.",
        'object':
            "It's typed `any`. That's why it quietly disables checking unless you assign it to `unknown`.",
        'unknown':
            'That would be the safer type, but the built-in declaration returns `any`. You opt in by annotating it as `unknown`.',
    },
    'What does `const { a = 1 } = obj` do when `obj.a` is `null`?': {
        'Sets a to 1':
            "That's what `a ?? 1` would do. Destructuring defaults apply only when the value is `undefined`, and `null` is a real value.",
        'Sets a to undefined':
            'Nothing turns `null` into `undefined`. The value `null` is copied into `a` as it is.',
        'Throws':
            'Reading a property whose value is `null` is fine. It would throw only if `obj` itself were `null` or `undefined`.',
    },
    'What does the spread `{ ...a, ...b }` do on conflicting keys?': {
        'It is a compile error':
            "Overlapping keys in spreads are allowed. The later spread's value is used.",
        'The values are merged recursively':
            'Spread is shallow: a nested object from `b` replaces the one from `a` entirely.',
        'a wins':
            "Spreads apply left to right, so the later object's values replace the earlier ones.",
    },
    'How do you rename while destructuring?': {
        'You cannot; assign afterwards':
            'You can rename in the pattern itself with `{ a: renamed }`.',
        'const { a as renamed } = obj':
            '`as` renames imports and exports. In destructuring, you rename with a colon.',
        'const { renamed = a } = obj':
            'That reads a property called `renamed` and defaults it to the variable `a`, which is a different thing.',
    },
    'What does `const { a, ...rest } = obj` put in `rest`?': {
        'A reference to obj':
            "`rest` is a new object. Changing it doesn't change `obj`, though nested values are still shared.",
        'An array of the remaining values':
            'Object rest gives an object. Only array destructuring gives an array for `...rest`.',
        'Only the properties declared after a':
            "Order in the pattern doesn't matter. `rest` gets every property you didn't name.",
    },
    '`JSON.stringify({ a: undefined, b: 1 })` produces…': {
        'A TypeError':
            "`undefined` values don't make `stringify` throw. The key is just left out.",
        '{"a":null,"b":1}':
            '`null` would be written, but `undefined` properties are dropped from the output.',
        '{"a":undefined,"b":1}':
            "`undefined` isn't valid JSON, so it can't appear in the output. The key is left out instead.",
    },
    '`const o = { a: 1 }; const p = o; p.a = 2;` — what is `o.a`?': {
        'A compile error':
            '`p` has the same type as `o`, so assigning a number to `p.a` type-checks.',
        '`1`':
            '`p = o` copies the reference, not the object. Both names point to the same object.',
        '`undefined`':
            'The property still exists. It was changed through the other name, to `2`.',
    },
    '`{ ...{ a: 1, b: 2 }, a: 3 }`?': {
        'A compile error':
            'Writing a property after a spread is allowed. It overrides the spread value.',
        '`{ a: 1, b: 2 }`':
            'The later `a: 3` overwrites the `a` that came from the spread.',
        '`{ a: [1, 3], b: 2 }`':
            "Spread doesn't combine values. The later property replaces the earlier one.",
    },
    '`JSON.stringify({ b: 1, a: 2 })`?': {
        "`'[1,2]'`":
            'An object is written as a JSON object with its keys, not as an array of values.',
        '`\'{"a":2,"b":1}\'`':
            "`JSON.stringify` doesn't sort keys. It follows insertion order, so `b` comes first.",
        "`'{b:1,a:2}'`":
            'JSON always puts keys in double quotes. Unquoted keys are JavaScript syntax, not JSON.',
    },
    '`JSON.parse("{\'a\': 1}")`?': {
        '`null`':
            "`JSON.parse` doesn't return `null` for bad input. It throws.",
        '`{ "a": 1 }`':
            "JSON doesn't accept single quotes, so this text isn't valid JSON, and parsing fails.",
        '`{ a: 1 }`':
            'JavaScript would accept that literal, but JSON requires double quotes, so parsing throws.',
    },
    '`Object.entries({ a: 1 })`?': {
        '`["a", 1]`':
            "That's one entry. `entries` returns an array of them, even when there's only one.",
        '`[["a"], [1]]`':
            'Each entry is a single `[key, value]` pair, not separate arrays of keys and values.',
        '`{ a: 1 }`':
            "That's the input. `Object.entries` turns it into an array of pairs.",
    },
    '`const { x: { y } } = { x: { y: 5 } };` — what is bound?': {
        "Nothing — it's a syntax error":
            'Nested destructuring patterns are valid syntax.',
        '`x` and `y`':
            "`x:` here says where to look for `y`. It's part of the pattern and doesn't create a variable.",
        '`x`, with the value `{ y: 5 }`':
            "To bind `x` too you'd write `{ x, x: { y } }`. Here `x` is only the path to `y`.",
    },
    '`{ name?: string }` vs `{ name: string | undefined }`?': {
        'The first allows `null`':
            'Neither form allows `null`. Both are about `undefined`.',
        'The second allows the key to be missing':
            "It's the other way round: only `?` lets the key be left out.",
        "They're identical":
            'They differ in whether the key may be left out. Only `name?` allows an object without it.',
    },
    '`interface A { x: number }` then `interface A { y: number }` — result?': {
        'Duplicate identifier error':
            "That's what happens with type aliases. Interfaces with the same name merge.",
        'The second replaces the first':
            "Interfaces aren't replaced. Both declarations add members to the same interface.",
        '`A` has only `x`':
            'Later declarations add their members, so `y` is part of `A` too.',
    },
    '`type A = { x: number }` then `type A = { y: number }` — result?': {
        'The second replaces the first':
            "TypeScript doesn't replace a type alias. Declaring it twice is an error.",
        'They merge':
            "Only interfaces merge. Type aliases can't be reopened.",
        '`A` becomes a union':
            "Declaring an alias twice never builds a union. To combine them you'd write `|` or `&` yourself.",
    },
    'What does `JSON.parse(JSON.stringify({ when: new Date(0) })).when` give back?': {
        'A `Date`':
            "`JSON.parse` doesn't know the string was a date. It only gives back strings, numbers, booleans, null, arrays and plain objects.",
        '`0`':
            "`stringify` uses the date's `toJSON`, which gives an ISO string, not the timestamp.",
        '`{}`':
            "A Date isn't written as an empty object. Its `toJSON` method turns it into an ISO string.",
    },
    'What does `JSON.stringify([undefined])` produce?': {
        'A TypeError':
            "`undefined` doesn't make `stringify` throw. In an array it's replaced with `null`.",
        '`"[]"`':
            "An array keeps its length, so the slot isn't removed. It's written as `null`.",
        '`"[undefined]"`':
            "`undefined` isn't valid JSON, so it can't appear in the output.",
    },
    'What does `JSON.stringify(new Map([[1, 2]]))` produce?': {
        'A TypeError':
            "`stringify` doesn't throw on a Map. It writes the Map's own enumerable properties, and it has none.",
        '`"[[1,2]]"`':
            "Map entries aren't own properties, so they aren't written. You'd need `[...map]` first to get that.",
        '`"{\\"1\\":2}"`':
            "`stringify` doesn't read Map entries as keys. Convert with `Object.fromEntries(map)` first.",
    },
    'What is `JSON.parse(\'{"a":1,"a":2}\').a`?': {
        'A SyntaxError':
            "Duplicate keys don't cause a parse error. The parser keeps the last value.",
        '`1`':
            'Each later value replaces the earlier one, so the first value is lost.',
        '`[1, 2]`':
            "Values for repeated keys aren't collected. The last one wins.",
    },
    'What is `typeof JSON.parse("null")`?': {
        'A SyntaxError':
            '`"null"` is valid JSON text, and it parses to the value `null`.',
        '`"string"`':
            'The JSON text is a string, but parsing turns it into the value `null`.',
        '`"undefined"`':
            '`null` isn\'t `undefined`, and `typeof null` has always been `"object"`.',
    },
    'What does `{ ...[1, 2] }` produce?': {
        'A TypeError':
            "Spreading an array into an object is allowed. It copies the array's own enumerable properties.",
        '`[1, 2]`':
            'Braces create an object, not an array. Use `[...xs]` to copy an array.',
        '`{}`':
            "An array's indexes are own enumerable properties, so they are copied.",
    },
    'What does `{ ...null }` produce?': {
        'A TypeError':
            "Object spread skips `null` and `undefined` without throwing. That's different from array spread.",
        '`null`':
            'Braces always create a new object, never `null`.',
        '`{ null: undefined }`':
            'Nothing named `null` becomes a key. Spreading `null` adds no properties at all.',
    },
    'Does `Object.assign(target, src)` return a new object?': {
        'It returns `src`':
            'It returns the first argument, `target`, not `src`.',
        'Only when `target` is empty':
            "Whether `target` is empty doesn't matter. It is always changed and returned.",
        'Yes, always':
            'It copies into `target` in place. Pass `{}` as the target if you want a new object.',
    },
    'What does `Object.fromEntries([["a", 1]])` return?': {
        '`Map { "a" => 1 }`':
            '`Object.fromEntries` builds a plain object. `new Map(entries)` builds a Map.',
        '`[["a", 1]]`':
            "It turns the pairs into an object; it doesn't return the array.",
        '`{ 0: ["a", 1] }`':
            'Each inner array is taken as a `[key, value]` pair, not as a value at an index.',
    },
    'How do you swap `x` and `y` without a temporary variable?': {
        '`swap(x, y)`':
            "There's no built-in `swap` function. Destructuring does it in one line.",
        '`x, y = y, x`':
            "That's Python. In JavaScript the comma operator makes this do something else entirely.",
        '`{ x, y } = { y, x }`':
            'Object destructuring matches by name, so `x` gets `x` again. Swapping needs positions, which means arrays.',
    },
    'What does `const { length } = "abc"` bind?': {
        "An error: strings can't be destructured":
            'Destructuring reads properties, and a string has a `length` property.',
        '`length` = "abc"':
            'Destructuring `{ length }` reads the property called `length`, not the string itself.',
        '`length` = undefined':
            '`length` exists on the string, so the value 3 is read.',
    },
    'What does `JSON.stringify(obj, null, 2)` do differently?': {
        'Drops `null` values':
            'The second argument is the replacer, and `null` there just means no replacer. Nothing is dropped.',
        'Keeps only 2 keys':
            '`2` is the indentation, not a limit on how many keys are written.',
        'Limits depth to 2':
            '`stringify` has no depth limit. The third argument sets the indentation.',
    },
    'In what order does `Object.entries({ b: 2, a: 1 })` list keys?': {
        'Alphabetical':
            "`Object.entries` doesn't sort anything. String keys come out in the order they were added.",
        'Random':
            'The order is fixed by the language: integer-like keys first, then string keys in insertion order.',
        'Reverse insertion order':
            'Keys come out in the order they were added, not reversed.',
    },
    'What type should `JSON.parse` results be given before validation?': {
        'The expected interface':
            'Annotating the result with the expected interface is really a cast. Nothing checks that the data has that shape.',
        '`any`':
            '`any` is what `JSON.parse` already returns, and it switches off checking entirely.',
        '`object`':
            "`object` still lets through `null` and arrays, and doesn't let you read properties. `unknown` makes you check everything.",
    },
    '`interface Point { x: number }` — can a class `implements Point` without extending anything?': {
        'No, it must extend a base class':
            "`implements` doesn't need a base class. It checks the class's own members against the interface.",
        'Only at runtime':
            '`implements` is only a compile-time check and is erased at runtime.',
        'Only if `Point` is a type alias':
            'A class can implement an interface or an object-type alias. Interfaces are the usual case.',
    },
    'Which can name a union type?': {
        'Both':
            "An interface can only describe an object shape, so it can't name a union.",
        "Neither — unions can't be named":
            'Unions can be named with `type`, e.g. `type Id = string | number`.',
        'Only an `interface`':
            'Interfaces describe object shapes only. A union needs a `type` alias.',
    },
    'Two `interface Settings` declarations in one scope…': {
        'are an error':
            "Two interfaces with the same name aren't an error. They merge.",
        'create two unrelated types':
            'Same-name interfaces in one scope are the same type, and they merge their members.',
        'the second replaces the first':
            'Interfaces are never replaced. The members from both declarations are combined.',
    },
    '`type T = { id: number } & { id: string }` — what is `T["id"]`?': {
        'A compile error at the declaration':
            'The declaration compiles. The conflict shows up only when you try to build a value.',
        '`number | string`':
            'An intersection needs a value that fits both parts, so `id` must be both a `number` and a `string`, which is impossible.',
        '`string`':
            'Neither side wins. Intersecting `number` with `string` gives `never`.',
    },
    'What does `class A implements Shape` do at runtime?': {
        "Copies `Shape`'s methods onto `A`":
            "`implements` doesn't add any methods. The class must write them itself; the compiler only checks.",
        'Makes `instanceof Shape` work':
            "Interfaces don't exist at runtime, so `instanceof Shape` can't work at all.",
        'Registers `A` as a `Shape`':
            'Nothing is recorded at runtime. `implements` is erased along with the interface.',
    },
    'Assigning a variable with extra properties to an interface type…': {
        'is allowed only with `as`':
            'No cast is needed. Excess-property errors apply only to object literals written in place.',
        'is always an error':
            'Only a fresh object literal gets the excess-property error. A variable with extra properties is assignable.',
        'strips the extra properties':
            "Types don't change runtime values. The extra properties are still on the object; the type just doesn't mention them.",
    },
    'What does `{ [key: string]: number }` promise about `obj["missing"]`?': {
        "Nothing — it's `any`":
            'The signature gives the value type `number`, not `any`.',
        "That it's `number | undefined`":
            "That's what you get with `noUncheckedIndexedAccess`. Without it, reads are typed `number`.",
        'That the key exists':
            'An index signature says what type values have, not which keys exist. Any string key type-checks.',
    },
    'What does `Record<"a" | "b", number>` require?': {
        'Any string keys':
            'The key type is limited to `"a" | "b"`, so other string keys aren\'t allowed.',
        'At least one of the keys':
            'A `Record` over a literal union requires every key in it, not just one.',
        'Keys `a` or `b`, optionally':
            "The keys aren't optional. You'd need `Partial<Record<...>>` for that.",
    },
    '`{ x?: number }` vs `{ x: number | undefined }`?': {
        "The first can't be `undefined`":
            'Without `exactOptionalPropertyTypes`, you can assign `undefined` to `x?`, and reading it gives `number | undefined`.',
        'The second may omit the key':
            'The second needs the key to be present. Only `x?` lets it be left out.',
        "They're identical in every mode":
            'Even without `exactOptionalPropertyTypes`, only the first allows an object without the key.',
    },
    'Why can `"constructor" in {}` be `true`?': {
        'Because of `strict` mode':
            'Strict mode has nothing to do with it. `in` checks the prototype chain.',
        "It can't":
            'It is `true`: `in` finds `constructor` on `Object.prototype`.',
        "It's a TypeScript bug":
            "It isn't a TypeScript issue. It's a JavaScript runtime result, caused by inherited properties.",
    },
    'What does TS7053 usually mean?': {
        'The key is misspelled':
            'A misspelled key in `o["nmae"]` can trigger it, but the usual cause is a `string`-typed key on an object with no index signature.',
        'The object is `readonly`':
            'Readonly errors are TS2540 and similar. TS7053 is about indexing with an arbitrary string key.',
        'The value is `any`':
            'TS7053 says the element implicitly has type `any`, because the object has no index signature for the key you used.',
    },
})
