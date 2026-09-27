# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# "Idiomatic TypeScript" editorials for every Library problem the TypeScript
# Mastery track curates (TS_MASTERY_ROADMAP.md X-22).
#
# Not just the algorithm: the types. Each entry is (notes, code) — the code is
# a complete answer in the problem's own TypeScript shape (the `solve`
# function for function-harness problems, a whole stdin program otherwise).
# gen_seed.py appends it to the problem's editorials and adds it to
# reference_solutions.json as the `typescript` reference, so
# `cargo test --test verify_seeds every_reference_solution_is_accepted`
# proves every one through the real judge.
# ---------------------------------------------------------------------------

_IDIO_READ = 'import * as fs from "fs";\n'

_IDIO_HEAP = r'''
class Heap<T> {
  readonly #items: T[] = [];
  readonly #before: (a: T, b: T) => boolean;
  constructor(before: (a: T, b: T) => boolean) {
    this.#before = before;
  }
  get size(): number {
    return this.#items.length;
  }
  peek(): T | undefined {
    return this.#items[0];
  }
  push(x: T): void {
    const a = this.#items;
    a.push(x);
    let i = a.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (!this.#before(a[i]!, a[p]!)) break;
      [a[i], a[p]] = [a[p]!, a[i]!];
      i = p;
    }
  }
  pop(): T | undefined {
    const a = this.#items;
    const top = a[0];
    const last = a.pop();
    if (a.length > 0 && last !== undefined) {
      a[0] = last;
      let i = 0;
      for (;;) {
        const l = 2 * i + 1;
        const r = l + 1;
        let m = i;
        if (l < a.length && this.#before(a[l]!, a[m]!)) m = l;
        if (r < a.length && this.#before(a[r]!, a[m]!)) m = r;
        if (m === i) break;
        [a[i], a[m]] = [a[m]!, a[i]!];
        i = m;
      }
    }
    return top;
  }
}
'''

_IDIO_OPS_HEAD = _IDIO_READ + r'''const lines = fs.readFileSync(0, "utf8").split("\n");
const q = Number(lines[0]);
const out: (string | number | boolean)[] = [];
'''

TS_IDIOMATIC = {
    "print-greeting": (
        "A whole program can be one statement. `console.log` adds the newline.",
        'console.log("Hello, World!");'),
    "add-two-numbers": (
        "Destructure with defaults (`= 0`): under `noUncheckedIndexedAccess` a destructured array element may be `undefined`, and a default says what to do about it.",
        _IDIO_READ + 'const [a = 0, b = 0] = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconsole.log(a + b);'),
    "rectangle-area": (
        "`.map(Number)` turns the tokens into `number[]` in one step; the defaults keep the destructuring honest when the flag is on.",
        _IDIO_READ + 'const [w = 0, h = 0] = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconsole.log(w * h);'),
    "echo-line": (
        "`split(\"\\n\")[0]` is `string | undefined` once indexed access is checked — `?? \"\"` settles it.",
        _IDIO_READ + 'const line = fs.readFileSync(0, "utf8").split("\\n")[0] ?? "";\nconsole.log(line);'),
    "even-or-odd": (
        "A conditional expression picks between two literals; the result is typed `\"Even\" | \"Odd\"`, which is exactly what the output can be. `n % 2 === 0` is right for negative numbers too (`-3 % 2` is `-1`).",
        _IDIO_READ + 'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(n % 2 === 0 ? "Even" : "Odd");'),
    "larger-of-two": (
        "`Math.max` says what you mean; no branch to get wrong.",
        _IDIO_READ + 'const [a = 0, b = 0] = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconsole.log(Math.max(a, b));'),
    "max-of-three": (
        "`Math.max` is variadic, so three values need no nesting.",
        "function solve(a: number, b: number, c: number): number {\n  return Math.max(a, b, c);\n}"),
    "leap-year": (
        "Return the boolean expression itself rather than `if (…) return true; return false;` — the return type already says it is a yes/no answer.",
        "function solve(y: number): boolean {\n  return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;\n}"),
    "is-multiple": (
        "One comparison. (`-6 % 3` is `-0`, and `-0 === 0` is `true`.)",
        "function solve(a: number, b: number): boolean {\n  return a % b === 0;\n}"),
    "countdown": (
        "`Array.from({ length: n }, …)` builds the sequence as data, and `join` owns the separators — no trailing-space bookkeeping.",
        _IDIO_READ + 'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(Array.from({ length: Math.max(0, n) }, (_, i) => n - i).join(" "));'),
    "sum-to-n": (
        "The closed form `n(n + 1) / 2` — guarded so a non-positive `n` gives the empty sum, 0.",
        _IDIO_READ + 'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(n > 0 ? (n * (n + 1)) / 2 : 0);'),
    "count-digits": (
        "For a non-negative integer, its decimal string's length is the digit count — `String(0)` is `\"0\"`, one digit.",
        "function solve(n: number): number {\n  return String(n).length;\n}"),
    "factorial": (
        "A plain loop with a `let` accumulator. (`number` is exact up to 2^53; past about 18! the answers would need `bigint`.)",
        "function solve(n: number): number {\n  let product = 1;\n  for (let i = 2; i <= n; i++) product *= i;\n  return product;\n}"),
    "is-prime": (
        "Trial division up to the square root; the early `return` keeps each case obvious.",
        "function solve(n: number): boolean {\n  if (n < 2) return false;\n  for (let d = 2; d * d <= n; d++) if (n % d === 0) return false;\n  return true;\n}"),
    "reverse-string": (
        "`[...s]` splits into code points (so an emoji survives), then `reverse` and `join`.",
        _IDIO_READ + 'const s = fs.readFileSync(0, "utf8").replace(/\\n$/, "");\n\nfunction solve(s: string): string {\n  return [...s].reverse().join("");\n}\n\nconsole.log(solve(s));'),
    "count-vowels": (
        "Filter the characters and count what is left; `\"aeiou\".includes(c)` reads as the rule itself.",
        _IDIO_READ + 'const s = fs.readFileSync(0, "utf8").replace(/\\n$/, "");\n\nfunction solve(s: string): number {\n  return [...s].filter((c) => "aeiou".includes(c)).length;\n}\n\nconsole.log(solve(s));'),
    "is-palindrome-fn": (
        "Compare the string with its reverse — one expression, typed `boolean`.",
        'function solve(s: string): boolean {\n  return s === [...s].reverse().join("");\n}'),
    "count-words": (
        "Split on runs of whitespace and drop the empty strings leading or trailing spaces leave behind — `filter(Boolean)` narrows nothing here, it just removes `\"\"`.",
        "function solve(s: string): number {\n  return s.split(/\\s+/).filter(Boolean).length;\n}"),
    "caesar-cipher": (
        "`replace` with a regex and a callback touches only the letters; the double `% 26` keeps negative shifts in range too.",
        "function solve(s: string, k: number): string {\n  return s.replace(/[a-z]/g, (c) => String.fromCharCode((((c.charCodeAt(0) - 97 + k) % 26) + 26) % 26 + 97));\n}"),
    "square-number": ("`n ** 2` or `n * n` — no type work needed.", "function solve(n: number): number {\n  return n * n;\n}"),
    "absolute-value": ("`Math.abs` — the library already has the right name.", "function solve(n: number): number {\n  return Math.abs(n);\n}"),
    "min-of-two": ("`Math.min` rather than a hand-written branch.", "function solve(a: number, b: number): number {\n  return Math.min(a, b);\n}"),
    "fizzbuzz-value": (
        "A chain of conditional expressions, most specific first; the return type `string` covers both the words and `String(n)`.",
        'function solve(n: number): string {\n  return n % 15 === 0 ? "FizzBuzz" : n % 3 === 0 ? "Fizz" : n % 5 === 0 ? "Buzz" : String(n);\n}'),
    "count-above-average": (
        "Compare `x * length > sum` instead of `x > sum / length`: integers stay integers, and no rounding can move an element across the average.",
        "function solve(nums: readonly number[]): number {\n  const sum = nums.reduce((a, b) => a + b, 0);\n  return nums.filter((x) => x * nums.length > sum).length;\n}"),
    "sort-by-frequency": (
        "Count into a `Map<string, number>`, then sort its entries: by count descending, ties by character. `<` compares code points; `localeCompare` would reorder by locale and break the tie rule.",
        'function solve(s: string): string {\n  const freq = new Map<string, number>();\n  for (const c of s) freq.set(c, (freq.get(c) ?? 0) + 1);\n  return [...freq]\n    .toSorted(([a, x], [b, y]) => y - x || (a < b ? -1 : a > b ? 1 : 0))\n    .map(([c, n]) => c.repeat(n))\n    .join("");\n}'),
    "count-occurrences": (
        "`filter` and `length`: the count is the size of what matches.",
        "function solve(nums: readonly number[], target: number): number {\n  return nums.filter((x) => x === target).length;\n}"),
    "array-sum": (
        "Destructure the count off the front (`[n = 0, ...rest]`) and `reduce` with an explicit `0` seed, so an empty array sums to 0 instead of throwing.",
        _IDIO_READ + 'const [n = 0, ...rest] = fs.readFileSync(0, "utf8").split(/\\s+/).filter(Boolean).map(Number);\nconsole.log(rest.slice(0, n).reduce((a, b) => a + b, 0));'),
    "array-maximum": (
        "Spread into `Math.max`. (For arrays of hundreds of thousands, `reduce` avoids the argument-count limit.)",
        "function solve(nums: readonly number[]): number {\n  return Math.max(...nums);\n}"),
    "second-largest": (
        "`new Set` removes duplicates, `toSorted` does not disturb the input, and `?? distinct[0]` says what happens with one distinct value.",
        "function solve(nums: readonly number[]): number {\n  const distinct = [...new Set(nums)].toSorted((a, b) => b - a);\n  return distinct[1] ?? distinct[0] ?? 0;\n}"),
    "move-zeroes": (
        "Two filters and a spread build a new array — the input is `readonly`, so the function cannot rearrange its caller's data by accident.",
        "function solve(nums: readonly number[]): number[] {\n  return [...nums.filter((x) => x !== 0), ...nums.filter((x) => x === 0)];\n}"),
    "running-sum": (
        "`map` with one running accumulator: the assignment expression `(total += x)` is the new value.",
        "function solve(nums: readonly number[]): number[] {\n  let total = 0;\n  return nums.map((x) => (total += x));\n}"),
    "count-equal-pairs": (
        "Each element pairs with every equal element seen before it: a `Map<number, number>` of counts makes it one pass.",
        "function solve(nums: readonly number[]): number {\n  const seen = new Map<number, number>();\n  let pairs = 0;\n  for (const x of nums) {\n    pairs += seen.get(x) ?? 0;\n    seen.set(x, (seen.get(x) ?? 0) + 1);\n  }\n  return pairs;\n}"),
    "first-unique-char": (
        "Count first, then `findIndex` — which already returns `-1` for \"none\".",
        "function solve(s: string): number {\n  const count = new Map<string, number>();\n  for (const c of s) count.set(c, (count.get(c) ?? 0) + 1);\n  return [...s].findIndex((c) => count.get(c) === 1);\n}"),
    "run-length-encode": (
        "A regex finds each run — `(.)\\1*` is a character and its repeats — and the callback writes it out.",
        'function solve(s: string): string {\n  return s.replace(/(.)\\1*/g, (run: string, c: string) => c + run.length);\n}'),
    "contains-duplicate": (
        "A `Set` is shorter than its source exactly when something repeated.",
        "function solve(nums: readonly number[]): boolean {\n  return new Set(nums).size !== nums.length;\n}"),
    "two-sum-indices": (
        "One pass with a `Map<number, number>` from value to index. `seen.get(...)` is `number | undefined`, so the `!== undefined` check is also what makes the index usable.",
        _IDIO_READ + 'const d = fs.readFileSync(0, "utf8").split(/\\s+/).filter(Boolean).map(Number);\nconst n = d[0] ?? 0;\nconst nums = d.slice(1, 1 + n);\nconst target = d[1 + n] ?? 0;\n\nfunction solve(nums: readonly number[], target: number): string {\n  const seen = new Map<number, number>();\n  for (const [i, x] of nums.entries()) {\n    const j = seen.get(target - x);\n    if (j !== undefined) return `${j + 1} ${i + 1}`;\n    if (!seen.has(x)) seen.set(x, i);\n  }\n  return "-1";\n}\n\nconsole.log(solve(nums, target));'),
    "majority-element": (
        "Boyer–Moore voting: constant memory, and the two `let`s are the whole state.",
        "function solve(nums: readonly number[]): number {\n  let candidate = nums[0] ?? 0;\n  let count = 0;\n  for (const x of nums) {\n    if (count === 0) candidate = x;\n    count += x === candidate ? 1 : -1;\n  }\n  return candidate;\n}"),
    "group-anagrams-count": (
        "Anagrams share their sorted letters, so the number of groups is the number of distinct sorted keys — a `Set` of them.",
        _IDIO_READ + 'const lines = fs.readFileSync(0, "utf8").split("\\n");\nconst n = Number(lines[0]);\nconst words = lines.slice(1, 1 + n).map((w) => w.trim());\nconsole.log(new Set(words.map((w) => [...w].sort().join(""))).size);'),
    "longest-consecutive": (
        "A `Set` gives constant-time membership; start counting only at a run's first element (`x - 1` absent), so each element is visited once.",
        "function solve(nums: readonly number[]): number {\n  const set = new Set(nums);\n  let best = 0;\n  for (const x of set) {\n    if (set.has(x - 1)) continue;\n    let len = 1;\n    while (set.has(x + len)) len++;\n    best = Math.max(best, len);\n  }\n  return best;\n}"),
    "traffic-light": (
        "Return a union of the three colours rather than `string`: a typo in any branch is then a compile error.",
        'type Colour = "green" | "yellow" | "red";\n\nfunction solve(g: number, y: number, r: number, t: number): Colour {\n  const at = t % (g + y + r);\n  return at < g ? "green" : at < g + y ? "yellow" : "red";\n}'),
    "rock-paper-scissors": (
        "A table of what beats what (`Record<string, string>`) replaces nine comparisons; the result is the literal union `\"A\" | \"B\" | \"Draw\"`.",
        'const BEATS: Record<string, string> = { R: "S", S: "P", P: "R" };\n\nfunction solve(a: string, b: string): "A" | "B" | "Draw" {\n  let score = 0;\n  for (let i = 0; i < a.length; i++) {\n    const x = a[i] ?? "";\n    const y = b[i] ?? "";\n    if (BEATS[x] === y) score++;\n    else if (BEATS[y] === x) score--;\n  }\n  return score > 0 ? "A" : score < 0 ? "B" : "Draw";\n}'),
    "seconds-to-clock": (
        "`padStart(2, \"0\")` does the zero-padding; a template literal assembles the parts.",
        'function solve(s: number): string {\n  const h = Math.floor(s / 3600);\n  const m = Math.floor((s % 3600) / 60);\n  const sec = s % 60;\n  return `${h}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;\n}'),
    "password-strength": (
        "Each rule is its own test — a length check and three regex classes — joined with `&&`.",
        "function solve(s: string): boolean {\n  return s.length >= 8 && /[A-Z]/.test(s) && /[a-z]/.test(s) && /\\d/.test(s);\n}"),
    "valid-anagram": (
        "Same letters, same counts means the same sorted string.",
        'function solve(s: string, t: string): boolean {\n  const key = (w: string) => [...w].sort().join("");\n  return key(s) === key(t);\n}'),
    "mountain-array": (
        "Walk up while it rises, walk down while it falls, and check you ended at the last element with a real peak in between.",
        "function solve(nums: readonly number[]): boolean {\n  let i = 0;\n  while (i + 1 < nums.length && nums[i] < nums[i + 1]) i++;\n  if (i === 0 || i === nums.length - 1) return false;\n  while (i + 1 < nums.length && nums[i] > nums[i + 1]) i++;\n  return i === nums.length - 1;\n}"),
    "valid-parentheses": (
        "A `Record` from each closer to its opener, and a `string[]` as the stack; `stack.pop()` is `string | undefined`, which compares correctly with the expected opener when the stack is empty.",
        _IDIO_READ + 'const s = fs.readFileSync(0, "utf8").replace(/\\n$/, "");\nconst OPENER: Record<string, string | undefined> = { ")": "(", "]": "[", "}": "{" };\n\nfunction solve(s: string): boolean {\n  const stack: string[] = [];\n  for (const c of s) {\n    const open = OPENER[c];\n    if (open === undefined) stack.push(c);\n    else if (stack.pop() !== open) return false;\n  }\n  return stack.length === 0;\n}\n\nconsole.log(solve(s));'),
    "min-stack": (
        "Store each value with the minimum at the time it was pushed — `{ value, min }` objects — so `getMin` is the top's `min`. `stack.at(-1)` is typed `… | undefined`, which the optional chaining handles.",
        _IDIO_OPS_HEAD + 'const stack: { value: number; min: number }[] = [];\nfor (const line of lines.slice(1, 1 + q)) {\n  const [op, arg] = line.trim().split(" ");\n  const top = stack.at(-1);\n  if (op === "push") {\n    const value = Number(arg);\n    stack.push({ value, min: top ? Math.min(top.min, value) : value });\n  } else if (op === "pop") stack.pop();\n  else if (op === "top") out.push(top?.value ?? "");\n  else if (op === "getMin") out.push(top?.min ?? "");\n}\nconsole.log(out.join("\\n"));'),
    "browser-history": (
        "An array of pages and a cursor; `visit` truncates the forward history with `slice`, and `Math.min`/`Math.max` clamp the moves.",
        _IDIO_OPS_HEAD + 'let pages: string[] = [];\nlet at = 0;\nfor (const line of lines.slice(1, 1 + q)) {\n  const [op = "", arg = ""] = line.trim().split(" ");\n  if (op === "home") {\n    pages = [arg];\n    at = 0;\n  } else if (op === "visit") {\n    pages = [...pages.slice(0, at + 1), arg];\n    at = pages.length - 1;\n  } else if (op === "back") {\n    at = Math.max(0, at - Number(arg));\n    out.push(pages[at] ?? "");\n  } else if (op === "forward") {\n    at = Math.min(pages.length - 1, at + Number(arg));\n    out.push(pages[at] ?? "");\n  }\n}\nconsole.log(out.join("\\n"));'),
    "longest-unique-substring": (
        "A sliding window with a `Map` from character to its last index: the window's start jumps past a repeat instead of creeping.",
        _IDIO_READ + 'const s = fs.readFileSync(0, "utf8").replace(/\\n$/, "");\n\nfunction solve(s: string): number {\n  const last = new Map<string, number>();\n  let start = 0;\n  let best = 0;\n  [...s].forEach((c, i) => {\n    const prev = last.get(c);\n    if (prev !== undefined && prev >= start) start = prev + 1;\n    last.set(c, i);\n    best = Math.max(best, i - start + 1);\n  });\n  return best;\n}\n\nconsole.log(solve(s));'),
    "merge-two-sorted-lists": (
        "Two indices and a result array; whatever remains of either input is already sorted and is spread on the end.",
        "function solve(a: readonly number[], b: readonly number[]): number[] {\n  const out: number[] = [];\n  let i = 0;\n  let j = 0;\n  while (i < a.length && j < b.length) out.push(a[i] <= b[j] ? a[i++] : b[j++]);\n  return [...out, ...a.slice(i), ...b.slice(j)];\n}"),
    "subarray-sum-k": (
        "Prefix sums with a `Map` of how often each has occurred: a subarray sums to `k` when an earlier prefix equals `sum - k`. The map starts with `[[0, 1]]` for the empty prefix.",
        "function solve(nums: readonly number[], k: number): number {\n  const seen = new Map<number, number>([[0, 1]]);\n  let sum = 0;\n  let count = 0;\n  for (const x of nums) {\n    sum += x;\n    count += seen.get(sum - k) ?? 0;\n    seen.set(sum, (seen.get(sum) ?? 0) + 1);\n  }\n  return count;\n}"),
    "missing-number": (
        "The expected total `n(n + 1) / 2` minus the actual sum is the gap.",
        "function solve(nums: readonly number[]): number {\n  const n = nums.length;\n  return (n * (n + 1)) / 2 - nums.reduce((a, b) => a + b, 0);\n}"),
    "count-negatives": ("`filter` then `length`.", "function solve(nums: readonly number[]): number {\n  return nums.filter((x) => x < 0).length;\n}"),
    "is-sorted": (
        "`every` stops at the first element smaller than its predecessor.",
        "function solve(nums: readonly number[]): boolean {\n  return nums.every((x, i) => i === 0 || nums[i - 1] <= x);\n}"),
    "longest-common-prefix-strs": (
        "Start from the first string and shorten it until every string starts with it; `startsWith` states the test directly.",
        'function solve(strs: readonly string[]): string {\n  let prefix = strs[0] ?? "";\n  for (const s of strs) while (!s.startsWith(prefix)) prefix = prefix.slice(0, -1);\n  return prefix;\n}'),
    "design-hashmap": (
        "The point is not to use `Map`: an array of buckets of `[key, value]` tuples, with the bucket chosen by `key % size`. A class keeps the buckets private (`#buckets`).",
        _IDIO_OPS_HEAD + 'class HashTable {\n  static readonly SIZE = 1024;\n  readonly #buckets: [number, number][][] = Array.from({ length: HashTable.SIZE }, () => []);\n  #bucket(key: number): [number, number][] {\n    return this.#buckets[((key % HashTable.SIZE) + HashTable.SIZE) % HashTable.SIZE] ?? [];\n  }\n  put(key: number, value: number): void {\n    const b = this.#bucket(key);\n    const hit = b.find(([k]) => k === key);\n    if (hit) hit[1] = value;\n    else b.push([key, value]);\n  }\n  get(key: number): number {\n    return this.#bucket(key).find(([k]) => k === key)?.[1] ?? -1;\n  }\n  remove(key: number): void {\n    const b = this.#bucket(key);\n    const i = b.findIndex(([k]) => k === key);\n    if (i >= 0) b.splice(i, 1);\n  }\n}\nconst table = new HashTable();\nfor (const line of lines.slice(1, 1 + q)) {\n  const [op, a, b] = line.trim().split(" ");\n  if (op === "put") table.put(Number(a), Number(b));\n  else if (op === "get") out.push(table.get(Number(a)));\n  else if (op === "remove") table.remove(Number(a));\n}\nconsole.log(out.join("\\n"));'),
    "product-except-self": (
        "Products to the left in one pass, to the right in another; `map(() => 1)` sizes the output without mutating the input.",
        "function solve(nums: readonly number[]): number[] {\n  const out = nums.map(() => 1);\n  let left = 1;\n  nums.forEach((x, i) => {\n    out[i] = left;\n    left *= x;\n  });\n  let right = 1;\n  for (let i = nums.length - 1; i >= 0; i--) {\n    out[i] *= right;\n    right *= nums[i];\n  }\n  return out;\n}"),
    "rotate-array": (
        "Reduce `k` modulo the length first, then rotation is two slices spread together.",
        _IDIO_READ + 'const d = fs.readFileSync(0, "utf8").split(/\\s+/).filter(Boolean).map(Number);\nconst n = d[0] ?? 0;\nconst arr = d.slice(1, 1 + n);\nconst k = d[1 + n] ?? 0;\n\nfunction solve(arr: readonly number[], k: number): number[] {\n  const s = arr.length === 0 ? 0 : k % arr.length;\n  return [...arr.slice(arr.length - s), ...arr.slice(0, arr.length - s)];\n}\n\nconsole.log(solve(arr, k).join(" "));'),
    "merge-intervals": (
        "Zip the parallel arrays into `[start, end]` tuples (annotate the callback's return so they are tuples, not `number[]`), sort a copy, merge, and `flat()` back to the output shape.",
        "function solve(starts: readonly number[], ends: readonly number[]): number[] {\n  const intervals = starts\n    .map((s, i): [number, number] => [s, ends[i]])\n    .toSorted((a, b) => a[0] - b[0]);\n  const merged: [number, number][] = [];\n  for (const [s, e] of intervals) {\n    const last = merged.at(-1);\n    if (last && s <= last[1]) last[1] = Math.max(last[1], e);\n    else merged.push([s, e]);\n  }\n  return merged.flat();\n}"),
    "insert-interval": (
        "Inserting is merging with one more interval: add it to the list and reuse the merge.",
        "function merge(starts: readonly number[], ends: readonly number[]): number[] {\n  const intervals = starts\n    .map((s, i): [number, number] => [s, ends[i]])\n    .toSorted((a, b) => a[0] - b[0]);\n  const merged: [number, number][] = [];\n  for (const [s, e] of intervals) {\n    const last = merged.at(-1);\n    if (last && s <= last[1]) last[1] = Math.max(last[1], e);\n    else merged.push([s, e]);\n  }\n  return merged.flat();\n}\n\nfunction solve(starts: number[], ends: number[], ns: number, ne: number): number[] {\n  return merge([...starts, ns], [...ends, ne]);\n}"),
    "can-attend-meetings": (
        "Sort meetings by start (as tuples), then no meeting may start before the previous one ends.",
        "function solve(starts: readonly number[], ends: readonly number[]): boolean {\n  const m = starts.map((s, i): [number, number] => [s, ends[i]]).toSorted((a, b) => a[0] - b[0]);\n  return m.every(([s], i) => i === 0 || m[i - 1][1] <= s);\n}"),
    "kth-largest-element": (
        "Sort a copy descending and index it. (For a stream or a huge array, a size-`k` heap keeps it `O(n log k)`.)",
        "function solve(nums: readonly number[], k: number): number {\n  return nums.toSorted((a, b) => b - a)[k - 1];\n}"),
    "time-based-kv": (
        "A `Map` from key to its `{ t, v }` history, which is already sorted because timestamps only grow — so `get` is a binary search for the last stamp not after `t`.",
        _IDIO_OPS_HEAD + 'const store = new Map<string, { t: number; v: string }[]>();\nfor (const line of lines.slice(1, 1 + q)) {\n  const [op = "", key = "", a = "", b = ""] = line.trim().split(" ");\n  if (op === "set") {\n    const history = store.get(key) ?? [];\n    history.push({ t: Number(b), v: a });\n    store.set(key, history);\n  } else if (op === "get") {\n    const history = store.get(key) ?? [];\n    const t = Number(a);\n    let lo = 0;\n    let hi = history.length;\n    while (lo < hi) {\n      const mid = (lo + hi) >> 1;\n      if ((history[mid]?.t ?? Infinity) <= t) lo = mid + 1;\n      else hi = mid;\n    }\n    out.push(history[lo - 1]?.v ?? "null");\n  }\n}\nconsole.log(out.join("\\n"));'),
    "top-k-frequent": (
        "Count with a `Map`, sort its entries by count then value, take `k`, keep the values — each step one method.",
        "function solve(nums: readonly number[], k: number): number[] {\n  const count = new Map<number, number>();\n  for (const x of nums) count.set(x, (count.get(x) ?? 0) + 1);\n  return [...count]\n    .toSorted((a, b) => b[1] - a[1] || a[0] - b[0])\n    .slice(0, k)\n    .map(([x]) => x);\n}"),
    "decode-string": (
        "A stack of `[textSoFar, repeat]` tuples: `[` saves the context, `]` restores it with the inner text repeated.",
        _IDIO_READ + 'const s = (fs.readFileSync(0, "utf8").split("\\n")[0] ?? "").trim();\n\nfunction solve(s: string): string {\n  const stack: [string, number][] = [];\n  let current = "";\n  let k = 0;\n  for (const c of s) {\n    if (c >= "0" && c <= "9") k = k * 10 + Number(c);\n    else if (c === "[") {\n      stack.push([current, k]);\n      current = "";\n      k = 0;\n    } else if (c === "]") {\n      const [prev, n] = stack.pop() ?? ["", 1];\n      current = prev + current.repeat(n);\n    } else current += c;\n  }\n  return current;\n}\n\nconsole.log(solve(s));'),
    "implement-trie-ops": (
        "Each node is `{ children: Map<string, TrieNode>; end: boolean }`; `#walk` is shared by `search` and `startsWith`, which differ only in whether the word must end there.",
        _IDIO_OPS_HEAD + 'type TrieNode = { children: Map<string, TrieNode>; end: boolean };\nclass Trie {\n  readonly #root: TrieNode = { children: new Map(), end: false };\n  insert(word: string): void {\n    let node = this.#root;\n    for (const c of word) {\n      let next = node.children.get(c);\n      if (!next) {\n        next = { children: new Map(), end: false };\n        node.children.set(c, next);\n      }\n      node = next;\n    }\n    node.end = true;\n  }\n  #walk(prefix: string): TrieNode | undefined {\n    let node: TrieNode | undefined = this.#root;\n    for (const c of prefix) node = node?.children.get(c);\n    return node;\n  }\n  search(word: string): boolean {\n    return this.#walk(word)?.end === true;\n  }\n  startsWith(prefix: string): boolean {\n    return this.#walk(prefix) !== undefined;\n  }\n}\nconst trie = new Trie();\nfor (const line of lines.slice(1, 1 + q)) {\n  const [op, w = ""] = line.trim().split(" ");\n  if (op === "insert") trie.insert(w);\n  else if (op === "search") out.push(trie.search(w));\n  else if (op === "startsWith") out.push(trie.startsWith(w));\n}\nconsole.log(out.join("\\n"));'),
    "design-circular-queue": (
        "A fixed array, a head index and a count; every position is `% capacity`. The fields are `#private` so nothing outside can break the invariants.",
        _IDIO_OPS_HEAD + 'class RingBuffer {\n  readonly #items: number[];\n  #head = 0;\n  #count = 0;\n  constructor(capacity: number) {\n    this.#items = new Array<number>(capacity).fill(0);\n  }\n  get isEmpty(): boolean {\n    return this.#count === 0;\n  }\n  get isFull(): boolean {\n    return this.#count === this.#items.length;\n  }\n  enQueue(x: number): boolean {\n    if (this.isFull) return false;\n    this.#items[(this.#head + this.#count) % this.#items.length] = x;\n    this.#count++;\n    return true;\n  }\n  deQueue(): boolean {\n    if (this.isEmpty) return false;\n    this.#head = (this.#head + 1) % this.#items.length;\n    this.#count--;\n    return true;\n  }\n  get front(): number {\n    return this.isEmpty ? -1 : (this.#items[this.#head] ?? -1);\n  }\n  get rear(): number {\n    return this.isEmpty ? -1 : (this.#items[(this.#head + this.#count - 1) % this.#items.length] ?? -1);\n  }\n}\nlet ring = new RingBuffer(0);\nfor (const line of lines.slice(1, 1 + q)) {\n  const [op, arg] = line.trim().split(" ");\n  if (op === "cap") ring = new RingBuffer(Number(arg));\n  else if (op === "enQueue") out.push(ring.enQueue(Number(arg)));\n  else if (op === "deQueue") out.push(ring.deQueue());\n  else if (op === "Front") out.push(ring.front);\n  else if (op === "Rear") out.push(ring.rear);\n  else if (op === "isEmpty") out.push(ring.isEmpty);\n  else if (op === "isFull") out.push(ring.isFull);\n}\nconsole.log(out.join("\\n"));'),
    "design-linked-list": (
        "Nodes are `{ val: number; next: ListNode | null }`, and a sentinel head means inserting at index 0 is not a special case.",
        _IDIO_OPS_HEAD + 'type ListNode = { val: number; next: ListNode | null };\nclass LinkedList {\n  readonly #sentinel: ListNode = { val: 0, next: null };\n  #size = 0;\n  #before(index: number): ListNode {\n    let node = this.#sentinel;\n    for (let i = 0; i < index && node.next; i++) node = node.next;\n    return node;\n  }\n  get(index: number): number {\n    if (index < 0 || index >= this.#size) return -1;\n    return this.#before(index).next?.val ?? -1;\n  }\n  addAtIndex(index: number, val: number): void {\n    if (index < 0 || index > this.#size) return;\n    const prev = this.#before(index);\n    prev.next = { val, next: prev.next };\n    this.#size++;\n  }\n  deleteAtIndex(index: number): void {\n    if (index < 0 || index >= this.#size) return;\n    const prev = this.#before(index);\n    prev.next = prev.next?.next ?? null;\n    this.#size--;\n  }\n  get size(): number {\n    return this.#size;\n  }\n}\nconst list = new LinkedList();\nfor (const line of lines.slice(1, 1 + q)) {\n  const [op, a, b] = line.trim().split(" ");\n  if (op === "addAtHead") list.addAtIndex(0, Number(a));\n  else if (op === "addAtTail") list.addAtIndex(list.size, Number(a));\n  else if (op === "addAtIndex") list.addAtIndex(Number(a), Number(b));\n  else if (op === "deleteAtIndex") list.deleteAtIndex(Number(a));\n  else if (op === "get") out.push(list.get(Number(a)));\n}\nconsole.log(out.join("\\n"));'),
    "lru-cache": (
        "A `Map` remembers insertion order, so re-inserting a key on each use keeps the least recently used first — `keys().next()` is the one to evict.",
        _IDIO_OPS_HEAD + 'class LruCache {\n  readonly #entries = new Map<number, number>();\n  readonly #capacity: number;\n  constructor(capacity: number) {\n    this.#capacity = capacity;\n  }\n  get(key: number): number {\n    const value = this.#entries.get(key);\n    if (value === undefined) return -1;\n    this.#entries.delete(key);\n    this.#entries.set(key, value);\n    return value;\n  }\n  put(key: number, value: number): void {\n    this.#entries.delete(key);\n    this.#entries.set(key, value);\n    if (this.#entries.size > this.#capacity) {\n      const oldest = this.#entries.keys().next();\n      if (!oldest.done) this.#entries.delete(oldest.value);\n    }\n  }\n}\nlet cache = new LruCache(0);\nfor (const line of lines.slice(1, 1 + q)) {\n  const [op, a, b] = line.trim().split(" ");\n  if (op === "cap") cache = new LruCache(Number(a));\n  else if (op === "put") cache.put(Number(a), Number(b));\n  else if (op === "get") out.push(cache.get(Number(a)));\n}\nconsole.log(out.join("\\n"));'),
    "implement-queue-stacks": (
        "Two arrays used as stacks: push onto `#inbox`, and refill `#outbox` only when it is empty — each element moves once, so operations are amortised O(1).",
        _IDIO_OPS_HEAD + 'class Queue<T> {\n  readonly #inbox: T[] = [];\n  readonly #outbox: T[] = [];\n  push(x: T): void {\n    this.#inbox.push(x);\n  }\n  #fill(): void {\n    if (this.#outbox.length === 0) while (this.#inbox.length) this.#outbox.push(this.#inbox.pop()!);\n  }\n  pop(): T | undefined {\n    this.#fill();\n    return this.#outbox.pop();\n  }\n  peek(): T | undefined {\n    this.#fill();\n    return this.#outbox.at(-1);\n  }\n  get empty(): boolean {\n    return this.#inbox.length === 0 && this.#outbox.length === 0;\n  }\n}\nconst queue = new Queue<number>();\nfor (const line of lines.slice(1, 1 + q)) {\n  const [op, arg] = line.trim().split(" ");\n  if (op === "push") queue.push(Number(arg));\n  else if (op === "pop") out.push(queue.pop() ?? "");\n  else if (op === "peek") out.push(queue.peek() ?? "");\n  else if (op === "empty") out.push(queue.empty);\n}\nconsole.log(out.join("\\n"));'),
    "implement-stack-queues": (
        "An array is already a stack; a generic `Stack<T>` wrapper exposes only the four operations, so nothing can index into the middle.",
        _IDIO_OPS_HEAD + 'class Stack<T> {\n  readonly #items: T[] = [];\n  push(x: T): void {\n    this.#items.push(x);\n  }\n  pop(): T | undefined {\n    return this.#items.pop();\n  }\n  top(): T | undefined {\n    return this.#items.at(-1);\n  }\n  get empty(): boolean {\n    return this.#items.length === 0;\n  }\n}\nconst stack = new Stack<number>();\nfor (const line of lines.slice(1, 1 + q)) {\n  const [op, arg] = line.trim().split(" ");\n  if (op === "push") stack.push(Number(arg));\n  else if (op === "pop") out.push(stack.pop() ?? "");\n  else if (op === "top") out.push(stack.top() ?? "");\n  else if (op === "empty") out.push(stack.empty);\n}\nconsole.log(out.join("\\n"));'),
    "design-twitter": (
        "Tweets in posting order and a `Map<number, Set<number>>` of who follows whom; the feed walks the tweets newest first and keeps ten.",
        _IDIO_OPS_HEAD + 'const tweets: { user: number; id: number }[] = [];\nconst follows = new Map<number, Set<number>>();\nfor (const line of lines.slice(1, 1 + q)) {\n  const [op = "", a = "", b = ""] = line.trim().split(" ");\n  const u = Number(a);\n  const v = Number(b);\n  if (op === "postTweet") tweets.push({ user: u, id: v });\n  else if (op === "follow") follows.set(u, (follows.get(u) ?? new Set<number>()).add(v));\n  else if (op === "unfollow") follows.get(u)?.delete(v);\n  else if (op === "getNewsFeed") {\n    const followed = follows.get(u) ?? new Set<number>();\n    const feed = tweets\n      .toReversed()\n      .filter((t) => t.user === u || followed.has(t.user))\n      .slice(0, 10)\n      .map((t) => t.id);\n    out.push(feed.length ? feed.join(" ") : "empty");\n  }\n}\nconsole.log(out.join("\\n"));'),
    "evaluate-rpn": (
        "A table of operators (`Record<string, (a: number, b: number) => number>`) keeps the loop to two cases; `Math.trunc` gives Java's division.",
        _IDIO_READ + 'const L = fs.readFileSync(0, "utf8").trim().split("\\n");\nconst tokens = (L[1] ?? "").trim().split(/\\s+/);\n\nconst OPS: Record<string, (a: number, b: number) => number> = {\n  "+": (a, b) => a + b,\n  "-": (a, b) => a - b,\n  "*": (a, b) => a * b,\n  "/": (a, b) => Math.trunc(a / b),\n};\n\nfunction solve(tokens: readonly string[]): number {\n  const stack: number[] = [];\n  for (const t of tokens) {\n    const op = OPS[t];\n    if (op) {\n      const b = stack.pop() ?? 0;\n      const a = stack.pop() ?? 0;\n      stack.push(op(a, b));\n    } else stack.push(Number(t));\n  }\n  return stack.pop() ?? 0;\n}\n\nconsole.log(solve(tokens));'),
    "valid-sudoku": (
        "One `Set<string>` of facts such as `r3:5`, `c7:5`, `b12:5`: a digit is invalid exactly when one of its three facts is already there.",
        _IDIO_READ + 'const d = fs.readFileSync(0, "utf8").split(/\\s+/).filter(Boolean);\nconst rows = d.slice(2, 11);\n\nfunction solve(rows: readonly string[]): "YES" | "NO" {\n  const seen = new Set<string>();\n  for (const [r, row] of rows.entries()) {\n    for (const [c, digit] of [...row].entries()) {\n      if (digit === ".") continue;\n      for (const fact of [`r${r}:${digit}`, `c${c}:${digit}`, `b${Math.floor(r / 3)}${Math.floor(c / 3)}:${digit}`]) {\n        if (seen.has(fact)) return "NO";\n        seen.add(fact);\n      }\n    }\n  }\n  return "YES";\n}\n\nconsole.log(solve(rows));'),
    "basic-calculator": (
        "A running result and sign, and a stack of `[result, sign]` tuples for parentheses; a unary minus falls out, because it is a `-` applied to an empty (zero) left side.",
        _IDIO_READ + 'const s = (fs.readFileSync(0, "utf8").split("\\n")[0] ?? "").replace(/\\r$/, "");\n\nfunction solve(s: string): number {\n  const stack: [number, number][] = [];\n  let result = 0;\n  let sign = 1;\n  let num = 0;\n  for (const c of s) {\n    if (c >= "0" && c <= "9") num = num * 10 + Number(c);\n    else if (c === "+" || c === "-") {\n      result += sign * num;\n      num = 0;\n      sign = c === "+" ? 1 : -1;\n    } else if (c === "(") {\n      stack.push([result, sign]);\n      result = 0;\n      sign = 1;\n    } else if (c === ")") {\n      result += sign * num;\n      num = 0;\n      const [before, outer] = stack.pop() ?? [0, 1];\n      result = before + outer * result;\n    }\n  }\n  return result + sign * num;\n}\n\nconsole.log(String(solve(s)));'),
    "hit-counter": (
        "Hits arrive in time order, so a queue with a moving start index drops everything older than the window.",
        _IDIO_OPS_HEAD + 'const hits: number[] = [];\nlet start = 0;\nfor (const line of lines.slice(1, 1 + q)) {\n  const [op, arg] = line.trim().split(" ");\n  const t = Number(arg);\n  if (op === "hit") hits.push(t);\n  else if (op === "get") {\n    while (start < hits.length && (hits[start] ?? t) <= t - 300) start++;\n    out.push(hits.length - start);\n  }\n}\nconsole.log(out.join("\\n"));'),
    "stock-spanner": (
        "A monotonic stack of `[price, span]` tuples: a day absorbs the spans of every earlier day it beats, so each day is pushed and popped at most once.",
        _IDIO_OPS_HEAD + 'const stack: [price: number, span: number][] = [];\nfor (const line of lines.slice(1, 1 + q)) {\n  const [op, arg] = line.trim().split(" ");\n  if (op !== "next") continue;\n  const price = Number(arg);\n  let span = 1;\n  for (let top = stack.at(-1); top && top[0] <= price; top = stack.at(-1)) {\n    span += top[1];\n    stack.pop();\n  }\n  stack.push([price, span]);\n  out.push(span);\n}\nconsole.log(out.join("\\n"));'),
    "process-tasks-using-servers": (
        "Two heaps from one generic `Heap<T>` class, each with its own ordering: free servers by `[weight, index]`, busy ones by `[freeAt, weight, index]`. Labelled tuple types document which number is which.",
        _IDIO_READ + 'const d = fs.readFileSync(0, "utf8").split(/\\s+/).filter(Boolean);\nconst n = Number(d[0]);\nconst a = d.slice(1, 1 + n).map(Number);\nconst m = Number(d[1 + n]);\nconst b = d.slice(2 + n, 2 + n + m).map(Number);\n' + _IDIO_HEAP + r'''
type Free = [weight: number, index: number];
type Busy = [freeAt: number, weight: number, index: number];

function solve(weights: readonly number[], tasks: readonly number[]): string {
  const free = new Heap<Free>((x, y) => x[0] < y[0] || (x[0] === y[0] && x[1] < y[1]));
  const busy = new Heap<Busy>(
    (x, y) => x[0] < y[0] || (x[0] === y[0] && (x[1] < y[1] || (x[1] === y[1] && x[2] < y[2]))),
  );
  weights.forEach((w, i) => free.push([w, i]));
  const release = (now: number) => {
    for (let top = busy.peek(); top && top[0] <= now; top = busy.peek()) {
      busy.pop();
      free.push([top[1], top[2]]);
    }
  };
  let time = 0;
  const assigned: number[] = [];
  tasks.forEach((duration, j) => {
    time = Math.max(time, j);
    release(time);
    if (free.size === 0) {
      time = busy.peek()?.[0] ?? time;
      release(time);
    }
    const server = free.pop();
    if (!server) return;
    assigned.push(server[1]);
    busy.push([time + duration, server[0], server[1]]);
  });
  return assigned.join(" ");
}

console.log(String(solve(a, b)));'''),
    "median-from-stream": (
        "Two heaps — a max-heap of the lower half and a min-heap of the upper — from one generic `Heap<T>` with opposite orderings; the median is read off their tops.",
        _IDIO_READ + 'const L = fs.readFileSync(0, "utf8").split("\\n");\nconst q = Number(L[0]);\n' + _IDIO_HEAP + r'''
const lower = new Heap<number>((x, y) => x > y);
const upper = new Heap<number>((x, y) => x < y);
const out: string[] = [];
for (const line of L.slice(1, 1 + q)) {
  const [op, arg] = line.trim().split(" ");
  if (op === "add") {
    const x = Number(arg);
    if (lower.size === 0 || x <= (lower.peek() ?? x)) lower.push(x);
    else upper.push(x);
    if (lower.size > upper.size + 1) upper.push(lower.pop()!);
    else if (upper.size > lower.size) lower.push(upper.pop()!);
  } else if (op === "median") {
    const lo = lower.peek() ?? 0;
    const median = lower.size > upper.size ? lo : (lo + (upper.peek() ?? lo)) / 2;
    out.push(median.toFixed(1));
  }
}
console.log(out.join("\n"));'''),
    "word-ladder-length": (
        "Breadth-first search, one frontier array per step, with a `Set` for the dictionary and another for what has been seen.",
        "function solve(begin: string, end: string, words: string[]): number {\n  const dict = new Set(words);\n  if (!dict.has(end)) return 0;\n  const seen = new Set([begin]);\n  let frontier = [begin];\n  for (let steps = 1; frontier.length > 0; steps++) {\n    const next: string[] = [];\n    for (const w of frontier) {\n      if (w === end) return steps;\n      for (let i = 0; i < w.length; i++) {\n        for (let c = 97; c < 123; c++) {\n          const candidate = w.slice(0, i) + String.fromCharCode(c) + w.slice(i + 1);\n          if (dict.has(candidate) && !seen.has(candidate)) {\n            seen.add(candidate);\n            next.push(candidate);\n          }\n        }\n      }\n    }\n    frontier = next;\n  }\n  return 0;\n}"),
    "lfu-cache": (
        "Values and use counts in `Map`s, and one insertion-ordered `Set` of keys per count: the least frequently used key is the first in the lowest count's set, which also makes the tie-break least recently used.",
        _IDIO_OPS_HEAD + 'class LfuCache {\n  readonly #capacity: number;\n  readonly #values = new Map<number, number>();\n  readonly #counts = new Map<number, number>();\n  readonly #byCount = new Map<number, Set<number>>();\n  #min = 0;\n  constructor(capacity: number) {\n    this.#capacity = capacity;\n  }\n  #touch(key: number): void {\n    const n = this.#counts.get(key) ?? 0;\n    const bucket = this.#byCount.get(n);\n    bucket?.delete(key);\n    if (bucket?.size === 0 && this.#min === n) this.#min = n + 1;\n    this.#counts.set(key, n + 1);\n    this.#byCount.set(n + 1, (this.#byCount.get(n + 1) ?? new Set<number>()).add(key));\n  }\n  get(key: number): number {\n    const value = this.#values.get(key);\n    if (value === undefined) return -1;\n    this.#touch(key);\n    return value;\n  }\n  put(key: number, value: number): void {\n    if (this.#capacity <= 0) return;\n    if (this.#values.has(key)) {\n      this.#values.set(key, value);\n      this.#touch(key);\n      return;\n    }\n    if (this.#values.size >= this.#capacity) {\n      const bucket = this.#byCount.get(this.#min);\n      const victim = bucket?.values().next();\n      if (victim && !victim.done) {\n        bucket?.delete(victim.value);\n        this.#values.delete(victim.value);\n        this.#counts.delete(victim.value);\n      }\n    }\n    this.#values.set(key, value);\n    this.#counts.set(key, 0);\n    this.#byCount.set(0, (this.#byCount.get(0) ?? new Set<number>()).add(key));\n    this.#min = 0;\n    this.#touch(key);\n  }\n}\nlet cache = new LfuCache(0);\nfor (const line of lines.slice(1, 1 + q)) {\n  const [op, a, b] = line.trim().split(" ");\n  if (op === "cap") cache = new LfuCache(Number(a));\n  else if (op === "put") cache.put(Number(a), Number(b));\n  else if (op === "get") out.push(cache.get(Number(a)));\n}\nconsole.log(out.join("\\n"));'),
}


def _idiomatic_editorials(problems, curated):
    """Append the TypeScript editorial to each curated problem that has one;
    fail the build if a curated problem has none."""
    missing = sorted(s for s in curated if s not in TS_IDIOMATIC)
    assert not missing, f"X-22: curated TypeScript-track problems without an idiomatic editorial: {missing}"
    by_slug = {p["slug"]: p for p in problems}
    for slug, (notes, code) in TS_IDIOMATIC.items():
        assert slug in by_slug, f"X-22: editorial for an unknown problem {slug}"
        p = by_slug[slug]
        p["editorials"] = list(p.get("editorials") or []) + [{
            "title": "Idiomatic TypeScript",
            "body": notes + "\n\n```ts\n" + code.strip("\n") + "\n```",
            "time": p.get("optimal_time", ""), "space": p.get("optimal_space", ""),
        }]
