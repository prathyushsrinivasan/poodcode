# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# "Same problem, three ways" (TS_MASTERY_ROADMAP.md X-26).
#
# One problem, solved three times in the week's problem set, each in a style
# the judge enforces:
#
#   loops     statements and mutation — array pipelines and classes banned
#   pipeline  expressions over data — loops, `let` and classes banned
#   class /   the learner writes only the class (or generator); a hidden
#   generator driver reads stdin, uses it, and prints
#
# The three share their tests, so all three must agree; the comparison — what
# each style made easy or hard — is shown once an exercise is solved.
# exec()'d by gen_seed.py before mastery_ts_attach.py.
# ---------------------------------------------------------------------------

_TW_LOOP_BAN = [".map(", ".reduce(", ".filter(", ".forEach(", "class "]
_TW_PIPE_BAN = ["for (", "while (", "let ", "class "]


def _three(week, base, title, problem, inputs, loops, pipeline, third, compare):
    """`third` is (label, prompt, solution, driver)."""
    strictness = _week_strictness(week)
    out = []
    for n, (label, how, starter, solution, harness, forbid) in enumerate([
        ("with loops", "Use statements and loops — no `map`/`reduce`/`filter`/`forEach`, no class.",
         _TS_SCAFFOLD + "____\n", _TS_SCAFFOLD + loops.strip("\n") + "\n", "", _TW_LOOP_BAN),
        ("as a pipeline", "Use expressions over the data — no `for`/`while` loops, no `let`, no class.",
         _TS_SCAFFOLD + "____\n", _TS_SCAFFOLD + pipeline.strip("\n") + "\n", "", _TW_PIPE_BAN),
        (third[0], third[1], "____\n", third[2].strip("\n") + "\n", _DRV + third[3].strip("\n") + "\n", []),
    ], start=1):
        eid = f"{base}-{n}"
        for tok in forbid:
            assert tok not in solution, f"{eid}: the reference breaks its own ban {tok!r}"
        program = solution.rstrip() + "\n" + harness if harness else solution
        out.append({
            "id": eid, "title": f"Three ways ({n}/3): {title} — {label}",
            "prompt": f"{problem}\n\n{how}",
            "hint": how, "hints": [how],
            "language": "typescript", "kind": "challenge", "difficulty": "Medium",
            "strictness": strictness, "harness": harness, "judge_mode": "", "forbid": list(forbid),
            "starter": starter, "solution": solution,
            "tests": _computed(eid, program, inputs, strictness),
            "source_slug": "", "dataset": "",
            "explanation": compare.strip(),
        })
    # Three styles, one behaviour: the references must print exactly the same.
    assert _TSO_COLLECT or out[0]["tests"] == out[1]["tests"] == out[2]["tests"], \
        f"{base}: the three references disagree"
    TS_PROBLEM_SETS.setdefault(week, []).extend(out)


_three(7, "tsm-w7-3w-tally", "Word tally",
       "Read one line of lowercase words. Print each distinct word and how often it appears, `word count`, most frequent first; break ties alphabetically.",
       ["the cat and the hat and the bat", "b a b c", "solo"],
       r'''
const counts: Record<string, number> = {};
for (const w of input.split(/\s+/)) counts[w] = (counts[w] ?? 0) + 1;
const words = Object.keys(counts).sort((a, b) => counts[b] - counts[a] || a.localeCompare(b));
for (const w of words) console.log(`${w} ${counts[w]}`);
''', r'''
const counts = input.split(/\s+/).reduce((m, w) => m.set(w, (m.get(w) ?? 0) + 1), new Map<string, number>());
const lines = [...counts].toSorted((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).map(([w, n]) => `${w} ${n}`);
console.log(lines.join("\n"));
''', ("as a class",
       "Write only `class Tally` with `add(word: string): void` and `ranked(): [string, number][]` (most frequent first, ties alphabetical). A hidden driver reads the words, adds each, and prints `ranked()`.",
       r'''
class Tally {
  readonly #counts = new Map<string, number>();
  add(word: string): void {
    this.#counts.set(word, (this.#counts.get(word) ?? 0) + 1);
  }
  ranked(): [string, number][] {
    return [...this.#counts].toSorted((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  }
}
''', r'''
const __t = new Tally();
for (const __w of __lines.join(" ").split(/\s+/)) __t.add(__w);
for (const [__w, __n] of __t.ranked()) console.log(`${__w} ${__n}`);
'''), '''
**Three ways, compared.** The **loop** version is the most direct to write and to step through, and a plain object is a fine counter — but the counting, sorting and printing are interleaved statements you have to read in order. The **pipeline** says the same thing as three transformations (count → sort → format); `reduce` into a `Map` is dense the first time you meet it and very readable after that, and nothing is mutated after it is built. The **class** hides the counting behind `add` and `ranked`: more code for a one-off script, but the only version you could reuse — another program can tally words without knowing it uses a `Map`.
''')

_three(12, "tsm-w12-3w-ledger", "An account ledger",
       "Each input line is `deposit N`, `withdraw N` or `balance`. Start at 0. A withdrawal larger than the balance prints `declined` and changes nothing; `balance` prints the balance. After the last line print `final <balance>`.",
       ["deposit 50\nwithdraw 20\nbalance\nwithdraw 100\ndeposit 5\nbalance", "balance", "withdraw 1\ndeposit 1"],
       r'''
let balance = 0;
for (const line of input.split("\n")) {
  const [op, arg] = line.trim().split(/\s+/);
  const n = Number(arg);
  switch (op) {
    case "deposit":
      balance += n;
      break;
    case "withdraw":
      if (n > balance) console.log("declined");
      else balance -= n;
      break;
    case "balance":
      console.log(balance);
      break;
  }
}
console.log(`final ${balance}`);
''', r'''
type Cmd = { op: "deposit" | "withdraw"; n: number } | { op: "balance" };
type State = { readonly balance: number; readonly out: readonly string[] };
const parse = (line: string): Cmd => {
  const [op = "", arg = "0"] = line.trim().split(/\s+/);
  return op === "balance" ? { op: "balance" } : { op: op === "withdraw" ? "withdraw" : "deposit", n: Number(arg) };
};
const step = (s: State, c: Cmd): State => {
  switch (c.op) {
    case "deposit":
      return { ...s, balance: s.balance + c.n };
    case "withdraw":
      return c.n > s.balance ? { ...s, out: [...s.out, "declined"] } : { ...s, balance: s.balance - c.n };
    case "balance":
      return { ...s, out: [...s.out, String(s.balance)] };
  }
};
const start: State = { balance: 0, out: [] };
const end = input.split("\n").map(parse).reduce(step, start);
console.log([...end.out, `final ${end.balance}`].join("\n"));
''', ("as a class",
       "Write only `class Account` with `deposit(n: number): void`, `withdraw(n: number): boolean` (false, and no change, when it would overdraw) and a `balance` getter. A hidden driver runs the commands and prints what they report.",
       r'''
class Account {
  #balance = 0;
  deposit(n: number): void {
    this.#balance += n;
  }
  withdraw(n: number): boolean {
    if (n > this.#balance) return false;
    this.#balance -= n;
    return true;
  }
  get balance(): number {
    return this.#balance;
  }
}
''', r'''
const __acct = new Account();
for (const __line of __lines) {
  const [__op, __arg] = __line.trim().split(/\s+/);
  const __n = Number(__arg);
  if (__op === "deposit") __acct.deposit(__n);
  else if (__op === "withdraw") {
    if (!__acct.withdraw(__n)) console.log("declined");
  } else if (__op === "balance") console.log(__acct.balance);
}
console.log(`final ${__acct.balance}`);
'''), '''
**Three ways, compared.** The **loop** keeps one mutable `balance` and prints as it goes — short, and fine until you want to test a single step on its own. The **pipeline** turns each line into a typed command (a discriminated union) and folds them into an immutable state, collecting output instead of printing it: longer, but every step is a pure function you can test with plain values, and adding a command is a compile error until `step` handles it. The **class** puts the rule ("no overdrafts") next to the balance it protects, and `#balance` means nothing outside can break it — the shape most real code ends up in when state has invariants.
''')

_three(18, "tsm-w18-3w-topk", "Top k by score",
       "The first line is `k`; each further line is `name score`. Print the `k` highest-scoring entries, `name score`, highest first; break ties alphabetically by name. (Fewer than `k` entries: print them all.)",
       ["2\nann 5\nbob 9\ncy 5\ndee 7", "3\nx 1\ny 1", "1\nsolo 3"],
       r'''
const [head = "0", ...rows] = input.split("\n");
const k = Number(head);
const top: [string, number][] = [];
for (const row of rows) {
  const [name = "", s = "0"] = row.trim().split(/\s+/);
  const score = Number(s);
  let i = top.length;
  while (i > 0) {
    const prev = top[i - 1];
    if (prev === undefined || prev[1] > score || (prev[1] === score && prev[0].localeCompare(name) < 0)) break;
    i--;
  }
  top.splice(i, 0, [name, score]);
  if (top.length > k) top.pop();
}
for (const [name, score] of top) console.log(`${name} ${score}`);
''', r'''
function topK<T>(items: readonly T[], k: number, score: (x: T) => number, tie: (a: T, b: T) => number): T[] {
  return items.toSorted((a, b) => score(b) - score(a) || tie(a, b)).slice(0, k);
}
const [head = "0", ...rows] = input.split("\n");
const entries = rows.map((r) => {
  const [name = "", s = "0"] = r.trim().split(/\s+/);
  return { name, score: Number(s) };
});
const best = topK(entries, Number(head), (e) => e.score, (a, b) => a.name.localeCompare(b.name));
console.log(best.map((e) => `${e.name} ${e.score}`).join("\n"));
''', ("as a generic class",
       "Write only the generic `class TopK<T>`: `constructor(k: number, score: (x: T) => number, tie: (a: T, b: T) => number)`, `add(x: T): void` and `items(): T[]` (best first, at most `k`). A hidden driver feeds it `{ name, score }` entries and prints `items()`.",
       r'''
class TopK<T> {
  readonly #k: number;
  readonly #score: (x: T) => number;
  readonly #tie: (a: T, b: T) => number;
  #items: T[] = [];
  constructor(k: number, score: (x: T) => number, tie: (a: T, b: T) => number) {
    this.#k = k;
    this.#score = score;
    this.#tie = tie;
  }
  add(x: T): void {
    this.#items = [...this.#items, x]
      .toSorted((a, b) => this.#score(b) - this.#score(a) || this.#tie(a, b))
      .slice(0, this.#k);
  }
  items(): T[] {
    return [...this.#items];
  }
}
''', r'''
const [__head = "0", ...__rows] = __lines;
const __top = new TopK<{ name: string; score: number }>(
  Number(__head),
  (e) => e.score,
  (a, b) => a.name.localeCompare(b.name),
);
for (const __r of __rows) {
  const [__n = "", __s = "0"] = __r.trim().split(/\s+/);
  __top.add({ name: __n, score: Number(__s) });
}
for (const __e of __top.items()) console.log(`${__e.name} ${__e.score}`);
'''), '''
**Three ways, compared.** The **loop** never holds more than `k` entries — an insertion into a small sorted array — which is what you want for a huge stream, at the price of index arithmetic that is easy to get wrong by one. The **pipeline** sorts everything and slices: one readable line, `O(n log n)` and all entries in memory, and the generic `topK<T>` works for any item type. The **generic class** keeps the bounded memory of the loop behind the API of the pipeline, and the type parameter means the same `TopK` ranks players, files or anything with a score — the payoff of week 18.
''')

_three(24, "tsm-w24-3w-range", "Ranges and their sums",
       "Each input line is `start end step`. Print the numbers from `start` (included) to `end` (excluded) in steps of `step`, space-separated, then ` | ` and their sum.",
       ["0 10 3\n5 6 1", "1 8 2"],
       r'''
for (const line of input.split("\n")) {
  const parts = line.trim().split(/\s+/);
  const a = Number(parts[0] ?? 0);
  const b = Number(parts[1] ?? 0);
  const s = Number(parts[2] ?? 1);
  const out: number[] = [];
  for (let x = a; x < b; x += s) out.push(x);
  let sum = 0;
  for (const x of out) sum += x;
  console.log(`${out.join(" ")} | ${sum}`);
}
''', r'''
const lines = input.split("\n").map((line) => {
  const [a = 0, b = 0, s = 1] = line.trim().split(/\s+/).map(Number);
  const xs = Array.from({ length: Math.max(0, Math.ceil((b - a) / s)) }, (_, i) => a + i * s);
  return `${xs.join(" ")} | ${xs.reduce((t, x) => t + x, 0)}`;
});
console.log(lines.join("\n"));
''', ("with a generator",
       "Write only `function* range(start: number, end: number, step: number)`, yielding the numbers lazily. A hidden driver spreads each range into an array and prints it with its sum.",
       r'''
function* range(start: number, end: number, step: number): Generator<number> {
  for (let x = start; x < end; x += step) yield x;
}
''', r'''
for (const __line of __lines) {
  const [__a = 0, __b = 0, __s = 1] = __line.trim().split(/\s+/).map(Number);
  const __xs = [...range(__a, __b, __s)];
  console.log(`${__xs.join(" ")} | ${__xs.reduce((t, x) => t + x, 0)}`);
}
'''), '''
**Three ways, compared.** The **loop** is the obvious translation and builds the whole list. The **pipeline** has to compute the length up front (`Math.ceil((end - start) / step)`) to use `Array.from` — correct, but the off-by-one lives in that formula now. The **generator** is the loop again, except it produces values only when asked: `[...range(0, 1e9, 1)]` would still be a problem, but `range(0, 1e9, 1).take(3)` (an iterator helper) costs three steps — laziness is what week 24 adds.
''')
