# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery, Month 3 (weeks 9-13): problem sets, runnable projects,
# extra practice and review cards for the chapters in ts_chapters_m3.py.
# Expected outputs are computed (python tools/gen_ts_outputs.py).
# ---------------------------------------------------------------------------

# ===========================================================================
# Week 9 — Maps, Sets, set algebra
# ===========================================================================

TS_PROBLEM_SETS[9] = [
    _tsp(9, "tsm-w9-first-repeat", "The first word said twice", "warm-up",
         "Each input line is a sentence. Print the first word (compared case-insensitively, punctuation ignored) whose second occurrence comes earliest, in lowercase — or `none`.",
         r"""
for (const line of input.split("\n")) {
  const words = line.toLowerCase().match(/[a-z']+/g) ?? [];
  const seen = new Set<string>();
  let repeat = "none";
  for (const w of words) {
    if (seen.has(w)) {
      repeat = w;
      break;
    }
    seen.add(w);
  }
  console.log(repeat);
}
""", ["The cat saw the dog\nNo repeats here\nit is what it is", "A b, B a."],
         hints=["A `Set` of words seen so far; the first word already in it is the answer."]),
    _tsp(9, "tsm-w9-same-shape", "Same shape, different letters", "warm-up",
         "Each input line holds two words of equal length. Print `yes` if the letters of the first can be replaced one-for-one to give the second (each letter always maps to the same letter, and no two letters map to the same one), otherwise `no`.",
         r"""
for (const line of input.split("\n")) {
  const [a = "", b = ""] = line.trim().split(/\s+/);
  const forward = new Map<string, string>();
  const backward = new Map<string, string>();
  let ok = a.length === b.length;
  for (let i = 0; ok && i < a.length; i++) {
    const x = a[i] ?? "";
    const y = b[i] ?? "";
    if ((forward.get(x) ?? y) !== y || (backward.get(y) ?? x) !== x) ok = false;
    forward.set(x, y);
    backward.set(y, x);
  }
  console.log(ok ? "yes" : "no");
}
""", ["egg add\nfoo bar\npaper title\nab aa", "abc xyz\naa bb"],
         hints=["Two maps: letter → image and image → letter. Any disagreement means no."]),
    _tsp(9, "tsm-w9-ransom", "Cut out a note", "warm-up",
         "The first line is a note, the second a magazine. Ignoring spaces and case, can the note's letters be cut from the magazine's (each magazine letter used once)? Print `yes`, or `missing` followed by each missing letter and how many more are needed, alphabetically (`missing a2 z1`).",
         r"""
const [note = "", magazine = ""] = input.split("\n");
const letters = (s: string) => s.toLowerCase().replace(/\s+/g, "");
const available = new Map<string, number>();
for (const ch of letters(magazine)) available.set(ch, (available.get(ch) ?? 0) + 1);
const short = new Map<string, number>();
for (const ch of letters(note)) {
  const left = available.get(ch) ?? 0;
  if (left > 0) available.set(ch, left - 1);
  else short.set(ch, (short.get(ch) ?? 0) + 1);
}
const report = [...short].sort(([a], [b]) => a.localeCompare(b)).map(([ch, n]) => `${ch}${n}`);
console.log(report.length === 0 ? "yes" : `missing ${report.join(" ")}`);
""", ["meet me\nthe team meets", "zebra zoo\nbar", "Hello\nhello world"],
         hints=["Count the magazine's letters in a `Map`, then spend them on the note."]),
    _tsp(9, "tsm-w9-tags", "Tag algebra", "warm-up",
         "Two lines of tags. Print `shared`, `either`, `only first`, `only second` and `in exactly one` — each a sorted list or `(none)` — using the `Set` methods, then `first ⊆ second: <bool>`.",
         r"""
const [x = "", y = ""] = input.split("\n");
const a = new Set(x.trim().split(/\s+/).filter((t) => t !== ""));
const b = new Set(y.trim().split(/\s+/).filter((t) => t !== ""));
const list = (s: Set<string>) => [...s].sort().join(" ") || "(none)";
console.log(`shared: ${list(a.intersection(b))}`);
console.log(`either: ${list(a.union(b))}`);
console.log(`only first: ${list(a.difference(b))}`);
console.log(`only second: ${list(b.difference(a))}`);
console.log(`in exactly one: ${list(a.symmetricDifference(b))}`);
console.log(`first ⊆ second: ${a.isSubsetOf(b)}`);
""", ["ts web js\njs web css", "a\na b", "x y\n"],
         hints=["Each line is one method call on a `Set`."]),
    _tsp(9, "tsm-w9-common", "Common to every list", "core",
         "Each input line is a list of integers. Print the values that appear in every line, ascending (or `(none)`), then how many distinct values appear in at least one line.",
         r"""
const sets = input.split("\n").map((line) => new Set(line.trim().split(/\s+/).map(Number)));
let common = sets[0] ?? new Set<number>();
let seenAnywhere = new Set<number>();
for (const s of sets) {
  common = common.intersection(s);
  seenAnywhere = seenAnywhere.union(s);
}
console.log([...common].sort((p, q) => p - q).join(" ") || "(none)");
console.log(seenAnywhere.size);
""", ["1 2 3 4\n2 4 6\n4 2 8", "5 5\n6", "7 8 9"],
         hints=["Fold the lines together with `intersection` (and `union` for the second answer)."]),
    _tsp(9, "tsm-w9-happy", "Happy numbers", "core",
         "Each input line is a positive integer. Repeatedly replace it by the sum of the squares of its digits. Print the chain up to and including `1` (a happy number) or up to the first repeated value, space-separated, then `happy` or `cycle`.",
         r"""
const squareDigits = (n: number) => [...String(n)].reduce((sum, d) => sum + Number(d) ** 2, 0);
for (const line of input.split("\n")) {
  let n = Number(line);
  const seen = new Set<number>();
  const chain: number[] = [];
  while (n !== 1 && !seen.has(n)) {
    seen.add(n);
    chain.push(n);
    n = squareDigits(n);
  }
  chain.push(n);
  console.log(chain.join(" "));
  console.log(n === 1 ? "happy" : "cycle");
}
""", ["19\n2", "1\n7", "4"],
         hints=["A `Set` of values already seen detects the cycle."]),
    _tsp(9, "tsm-w9-window-distinct", "Distinct values in every window", "core",
         "The first line is k; the second a list of integers. For every window of k consecutive values print how many distinct values it holds, space-separated. Keep a `Map` of counts and update it as the window slides, rather than rebuilding it.",
         r"""
const [kText = "1", line = ""] = input.split("\n");
const k = Number(kText);
const xs = line.trim().split(/\s+/).map(Number);
const counts = new Map<number, number>();
const out: number[] = [];
xs.forEach((x, i) => {
  counts.set(x, (counts.get(x) ?? 0) + 1);
  if (i >= k) {
    const old = xs[i - k] ?? 0;
    const n = (counts.get(old) ?? 0) - 1;
    if (n === 0) counts.delete(old);
    else counts.set(old, n);
  }
  if (i >= k - 1) out.push(counts.size);
});
console.log(out.join(" ") || "(none)");
""", ["3\n1 2 1 3 4 2 3", "1\n5 5 5", "4\n1 1 1 1 2", "5\n1 2"],
         hints=["Add the value entering the window; decrement (and maybe delete) the one leaving it. The `Map`'s size is the answer."]),
    _tsp(9, "tsm-w9-harmony", "Longest harmonious run", "core",
         "The input is a list of integers. A harmonious selection uses values whose max and min differ by exactly 1 (not necessarily adjacent). Print the size of the largest one, and the pair of values it uses as `lo hi` (the smallest `lo` on a tie) — or `0` alone if there is none.",
         r"""
const counts = new Map<number, number>();
for (const x of input.split(/\s+/).map(Number)) counts.set(x, (counts.get(x) ?? 0) + 1);
let best = 0;
let bestLo = 0;
for (const [x, n] of [...counts].sort((a, b) => a[0] - b[0])) {
  const next = counts.get(x + 1);
  if (next !== undefined && n + next > best) {
    best = n + next;
    bestLo = x;
  }
}
console.log(best === 0 ? "0" : `${best}\n${bestLo} ${bestLo + 1}`);
""", ["1 3 2 2 5 2 3 7", "1 1 1", "4 5 5 6 6", "10 8"],
         hints=["Count every value; for each value x the best selection using x and x+1 has count[x] + count[x+1] elements."]),
    _tsp(9, "tsm-w9-pairs-k", "Pairs at distance k", "core",
         "The first line is k (≥ 0); the second a list of integers. Count the distinct value pairs `(a, b)` with `b - a = k` that can be formed from the list, and print them as `a:b`, ascending by `a`, then the count.",
         r"""
const [kText = "0", line = ""] = input.split("\n");
const k = Number(kText);
const counts = new Map<number, number>();
for (const x of line.trim().split(/\s+/).map(Number)) counts.set(x, (counts.get(x) ?? 0) + 1);
const pairs: string[] = [];
for (const x of [...counts.keys()].sort((a, b) => a - b)) {
  const ok = k === 0 ? (counts.get(x) ?? 0) >= 2 : counts.has(x + k);
  if (ok) pairs.push(`${x}:${x + k}`);
}
console.log(pairs.join(" ") || "(none)");
console.log(pairs.length);
""", ["2\n3 1 4 1 5", "0\n1 1 2 2 2 3", "1\n1 2 3 4 5", "10\n1 2"],
         hints=["Count values in a `Map`. For k > 0, look up x + k; for k = 0 a value needs two copies."]),
    _tsp(9, "tsm-w9-anagrams", "Anagram families", "stretch",
         "The input is a line of words. Group anagrams (same letters, ignoring case). Print each group with more than one word as `<words in input order>`, largest group first (ties by the group's first word, alphabetically), then `<k> singletons`.",
         r"""
const groups = new Map<string, string[]>();
for (const word of input.split(/\s+/)) {
  const key = [...word.toLowerCase()].sort().join("");
  const group = groups.get(key);
  if (group === undefined) groups.set(key, [word]);
  else group.push(word);
}
const families = [...groups.values()].filter((g) => g.length > 1);
families.sort((a, b) => b.length - a.length || (a[0] ?? "").localeCompare(b[0] ?? ""));
for (const g of families) console.log(g.join(" "));
console.log(`${groups.size - families.length} singletons`);
""", ["listen silent enlist google banana Tinsel", "abc bca cab xyz zyx q", "one"],
         hints=["The sorted letters are the key; a `Map` from key to the words that share it."]),
    _tsp(9, "tsm-w9-lru", "An LRU cache from a Map", "stretch",
         "The first line is the capacity; each later line is `get k` or `put k v`. Implement a least-recently-used cache using only a `Map` (its insertion order is the recency order: delete and re-insert to mark an entry as used). Print the value or `miss` for each `get`, and `evict <k>` whenever a `put` pushes out the least recently used key.",
         r"""
const [capText = "1", ...ops] = input.split("\n");
const capacity = Number(capText);
const cache = new Map<string, string>();
for (const op of ops) {
  const [cmd = "", key = "", value = ""] = op.trim().split(/\s+/);
  if (cmd === "get") {
    const v = cache.get(key);
    if (v === undefined) {
      console.log("miss");
    } else {
      cache.delete(key);
      cache.set(key, v);
      console.log(v);
    }
  } else {
    cache.delete(key);
    cache.set(key, value);
    if (cache.size > capacity) {
      const oldest = cache.keys().next().value;
      if (oldest !== undefined) {
        cache.delete(oldest);
        console.log(`evict ${oldest}`);
      }
    }
  }
}
""", ["2\nput a 1\nput b 2\nget a\nput c 3\nget b\nget a\nget c", "1\nput x 9\nput x 8\nget x\nput y 1\nget x"],
         hints=["A `Map` iterates in insertion order, so its first key is the least recently used.",
                "`cache.keys().next().value` reads that first key."]),
]

TS_PROJECTS[9] = _project(
    9, "index.ts — a searchable inverted index",
    "Search engines start with an inverted index: for every word, the set of documents containing it. Build one from `Map<string, Set<string>>`, then answer boolean queries with the set methods — `AND` is an intersection, `OR` a union, `NOT` a difference.",
    ["The input has two sections separated by a line containing only `---`: documents as `id: text`, then queries.",
     "Index words case-insensitively (words are runs of letters and digits).",
     "A query is words joined by `AND`, `OR` and `NOT`, evaluated left to right with no precedence (`a OR b AND c` is `(a OR b) AND c`). `NOT` means \"and not\".",
     "Print each query's matching document ids, sorted, or `(none)`; a word that appears nowhere matches nothing.",
     "Finally print `<n> words indexed`."],
    r"""
const [docsPart = "", queryPart = ""] = input.split("\n---\n");
const index = new Map<string, Set<string>>();
for (const line of docsPart.split("\n")) {
  const colon = line.indexOf(":");
  const id = line.slice(0, colon).trim();
  for (const word of line.slice(colon + 1).toLowerCase().match(/[a-z0-9]+/g) ?? []) {
    const docs = index.get(word) ?? new Set<string>();
    docs.add(id);
    index.set(word, docs);
  }
}
const docsFor = (word: string) => index.get(word.toLowerCase()) ?? new Set<string>();
for (const query of queryPart.split("\n").filter((q) => q.trim() !== "")) {
  const tokens = query.trim().split(/\s+/);
  let result = docsFor(tokens[0] ?? "");
  for (let i = 1; i + 1 < tokens.length; i += 2) {
    const op = tokens[i];
    const next = docsFor(tokens[i + 1] ?? "");
    if (op === "AND") result = result.intersection(next);
    else if (op === "OR") result = result.union(next);
    else if (op === "NOT") result = result.difference(next);
  }
  console.log([...result].sort().join(" ") || "(none)");
}
console.log(`${index.size} words indexed`);
""", ["d1: The quick brown fox\nd2: The lazy dog\nd3: Quick brown dogs\n---\nquick\nbrown AND dog\nthe OR dogs\nquick NOT fox\ncat",
      "a: x y\nb: y z\n---\nx OR z\ny AND x AND z\ny NOT x NOT z",
      "only: Hello, hello WORLD!\n---\nhello\nworld",
      "n1: red apple\nn2: green apple\nn3: red cherry\n---\napple NOT red\nred OR green AND apple\ncherry OR apple NOT green",
      "d: 2026 report v2\ne: report\n---\nreport AND 2026\nv2 OR missing\nmissing NOT report"],
    stretch=["Rank results by how many query words each document contains.",
             "Support phrases in quotes by also indexing word positions."],
)

TS_PRACTICE_MORE[9] = [
    _pr("tsm-w9-p4", "A Map lookup", "const ages = new Map<string, number>();\nconst a = ages.get(\"ada\");\n", "a", "number | undefined",
        hints=["`get` may find nothing."]),
    _pr("tsm-w9-p5", "An intersection", "const a = new Set([1, 2]);\nconst both = a.intersection(new Set([2, 3]));\n", "both", "Set<number>",
        hints=["The set methods return a new `Set` of the element type."]),
    _dx("tsm-w9-d4", "An array where a set is expected",
        "error TS2345: Argument of type 'string[]' is not assignable to parameter of type 'ReadonlySetLike<unknown>'.",
        _STDIN + "const [x = \"\", y = \"\"] = input.split(\"\\n\");\nconst a = new Set(x.split(\" \"));\nconsole.log([...a.union(y.split(\" \"))].join(\" \"));\n",
        _STDIN + "const [x = \"\", y = \"\"] = input.split(\"\\n\");\nconst a = new Set(x.split(\" \"));\nconsole.log([...a.union(new Set(y.split(\" \")))].join(\" \"));\n",
        [("a b\nb c", "a b c")], ask="Print every word from either line.", hints=["The argument must be set-like.", "Wrap it in `new Set(...)`."]),
    _fx("tsm-w9-f3", "Points that aren't deduplicated",
        "Count the distinct points visited. Every revisit is counted as new.",
        _STDIN + "const seen = new Set<{ x: number; y: number }>();\nfor (const p of input.split(/\\s+/)) {\n  const [x = 0, y = 0] = p.split(\",\").map(Number);\n  seen.add({ x, y });\n}\nconsole.log(seen.size);\n",
        _STDIN + "const seen = new Set<string>();\nfor (const p of input.split(/\\s+/)) {\n  const [x = 0, y = 0] = p.split(\",\").map(Number);\n  seen.add(`${x},${y}`);\n}\nconsole.log(seen.size);\n",
        [("0,0 1,0 0,0", "2"), ("5,5", "1")], hints=["Objects are compared by identity.", "Key the set by a string."]),
]

TS_CARDS_MORE[9] = [
    ("`a.union(b)`, `a.intersection(b)`, `a.difference(b)` — do they change `a`?", "No — each returns a new `Set`; both operands are untouched."),
    ("What must the argument to a `Set` method be?", "Set-like — it needs `size`, `has` and `keys` — so a `Set` or `Map`, not an array."),
    ("What does `a.symmetricDifference(b)` contain?", "Everything that is in exactly one of the two sets."),
    ("`Map.groupBy` vs `Object.groupBy`?", "`Map.groupBy` keeps keys of any type in a `Map`; `Object.groupBy` makes them property keys."),
    ("`Map` or `WeakMap` for a cache keyed by objects you don't own?","Attaching data to objects without keeping them alive — keys must be objects, and it can't be iterated."),
    ("How does a `Map` give you LRU order for free?", "It iterates in insertion order; deleting and re-setting a key moves it to the end, so the first key is the least recently used."),
]

# ===========================================================================
# Week 10 — Unions, aliases, literal types, enums
# ===========================================================================

TS_PROBLEM_SETS[10] = [
    _tsp(10, "tsm-w10-card", "Name the card", "warm-up",
         "Each input line is a card code: a rank (`2`-`10`, `J`, `Q`, `K`, `A`) followed by a suit letter (`C`, `D`, `H`, `S`), e.g. `QH` or `10S`. Print its full name (`Queen of Hearts`), or `invalid <code>`. Keep ranks and suits as `as const` tables and derive their types.",
         r"""
const RANKS = { "2": "Two", "3": "Three", "4": "Four", "5": "Five", "6": "Six", "7": "Seven", "8": "Eight",
  "9": "Nine", "10": "Ten", J: "Jack", Q: "Queen", K: "King", A: "Ace" } as const;
const SUITS = { C: "Clubs", D: "Diamonds", H: "Hearts", S: "Spades" } as const;
type Rank = keyof typeof RANKS;
type Suit = keyof typeof SUITS;
const isRank = (t: string): t is Rank => Object.hasOwn(RANKS, t);
const isSuit = (t: string): t is Suit => Object.hasOwn(SUITS, t);
for (const line of input.split("\n")) {
  const code = line.trim().toUpperCase();
  const rank = code.slice(0, -1);
  const suit = code.slice(-1);
  console.log(isRank(rank) && isSuit(suit) ? `${RANKS[rank]} of ${SUITS[suit]}` : `invalid ${line.trim()}`);
}
""", ["QH\n10s\nAC\n1D\nKX", "2d\njs"],
         hints=["`keyof typeof TABLE` is the union of its keys.", "A type predicate turns a checked string into a `Rank`."]),
    _tsp(10, "tsm-w10-status", "Classify an HTTP status", "warm-up",
         "Each input line is a status code. Print `<code> <class>`, the class being `informational` (100-199), `success`, `redirect`, `client error` or `server error` (500-599), or `invalid`. Return the class from a function typed with a literal union.",
         r"""
type StatusClass = "informational" | "success" | "redirect" | "client error" | "server error" | "invalid";
function classify(code: number): StatusClass {
  if (!Number.isInteger(code) || code < 100 || code > 599) return "invalid";
  const classes: StatusClass[] = ["informational", "success", "redirect", "client error", "server error"];
  return classes[Math.floor(code / 100) - 1] ?? "invalid";
}
for (const line of input.split("\n")) console.log(`${line.trim()} ${classify(Number(line))}`);
""", ["200\n404\n503\n301\n100", "99\n600\n2.5\nabc"],
         hints=["The hundreds digit picks the class; guard the range first."]),
    _tsp(10, "tsm-w10-compass", "Follow the turns", "warm-up",
         "The input is a string of turns: `L` (left 90°), `R` (right 90°) and `U` (turn around). Starting facing `N`, print the heading after each turn, space-separated. Model headings as `\"N\" | \"E\" | \"S\" | \"W\"`.",
         r"""
const HEADINGS = ["N", "E", "S", "W"] as const;
type Heading = (typeof HEADINGS)[number];
const turn = { L: 3, R: 1, U: 2 } as const;
let index = 0;
const path: Heading[] = [];
for (const t of input.trim()) {
  if (t === "L" || t === "R" || t === "U") {
    index = (index + turn[t]) % 4;
    path.push(HEADINGS[index] ?? "N");
  }
}
console.log(path.join(" ") || "(no turns)");
""", ["RRL", "UUUU", "LLL", "x"],
         hints=["Keep the heading as an index into the `as const` array; a left turn is three rights."]),
    _tsp(10, "tsm-w10-sizes", "Convert clothing sizes", "warm-up",
         "Each input line is `<size> <from> <to>`, where the systems are `letter` (XS-XL), `eu` (44-52) and `us` (34-42), in step: XS=44=34, S=46=36, M=48=38, L=50=40, XL=52=42. Print the converted size, or `unknown size`.",
         r"""
const SYSTEMS = { letter: ["XS", "S", "M", "L", "XL"], eu: ["44", "46", "48", "50", "52"], us: ["34", "36", "38", "40", "42"] } as const;
type System = keyof typeof SYSTEMS;
const isSystem = (s: string): s is System => Object.hasOwn(SYSTEMS, s);
for (const line of input.split("\n")) {
  const [size = "", from = "", to = ""] = line.trim().split(/\s+/);
  if (!isSystem(from) || !isSystem(to)) {
    console.log("unknown size");
    continue;
  }
  const i = SYSTEMS[from].findIndex((s) => s === size.toUpperCase());
  console.log(i < 0 ? "unknown size" : SYSTEMS[to][i]);
}
""", ["M letter eu\n40 us letter\n52 eu us\nXXL letter us\nM letter uk"],
         hints=["Parallel `as const` arrays: find the index in one, read the same index in another."]),
    _tsp(10, "tsm-w10-vending", "A vending machine", "core",
         "A machine is `idle`, `ready` (a coin is in) or `vending`. Commands: `coin` (idle→ready, or `returned` if already ready), `push` (ready→vending, then it drops the item and is idle again; from idle it prints `insert coin`), `refund` (ready→idle, printing `refunded`; otherwise `nothing to refund`). Print the state after each command as `<state>` or the message. Use a literal-union `State` and a transition table.",
         r"""
type State = "idle" | "ready";
type Command = "coin" | "push" | "refund";
const COMMANDS: readonly string[] = ["coin", "push", "refund"];
const table: Record<State, Record<Command, [State, string]>> = {
  idle: { coin: ["ready", "ready"], push: ["idle", "insert coin"], refund: ["idle", "nothing to refund"] },
  ready: { coin: ["ready", "returned"], push: ["idle", "vending -> idle"], refund: ["idle", "refunded"] },
};
let state: State = "idle";
for (const token of input.split(/\s+/)) {
  if (!COMMANDS.includes(token)) {
    console.log(`unknown ${token}`);
    continue;
  }
  const current: State = state;
  // The annotation is load-bearing: `state = next` feeds the narrowed type of
  // `state` (and so of `current`, and so of `table[current]`) back into `next`'s
  // own initializer, which tsc reports as TS7022 rather than resolving.
  const [next, message]: [State, string] = table[current][token as Command];
  state = next;
  console.log(message);
}
""", ["coin push push", "refund coin coin refund", "coin kick push"],
         hints=["A `Record<State, Record<Command, …>>` makes every (state, command) pair a compile-time requirement."]),
    _tsp(10, "tsm-w10-lock", "A combination lock with an alarm", "core",
         "The first line is the correct code; each later line is an attempt or the command `lock`. The lock is `locked` or `open`; three wrong codes in a row while locked set off the `alarm`, after which everything prints `alarm`. Print the state after each line. A correct code resets the wrong-attempt count.",
         r"""
type LockState = "locked" | "open" | "alarm";
const [code = "", ...steps] = input.split("\n");
let state: LockState = "locked";
let wrong = 0;
for (const raw of steps) {
  const step = raw.trim();
  if (state === "alarm") {
    console.log("alarm");
    continue;
  }
  if (step === "lock") {
    state = "locked";
  } else if (state === "locked") {
    if (step === code.trim()) {
      state = "open";
      wrong = 0;
    } else if (++wrong === 3) {
      state = "alarm";
    }
  }
  console.log(state);
}
""", ["1234\n1111\n1234\nlock\n0000\n0000\n0000\n1234", "42\n42\nlock\n1\n42\n1\n1\n1"],
         hints=["The state is a literal union; each input moves between three values."]),
    _tsp(10, "tsm-w10-robot", "A robot on a grid", "core",
         "The input is a command string: `F` moves one step forward, `L`/`R` turn 90°, and `B` moves one step back. The robot starts at 0,0 facing north (y grows north). Print the final position, the final heading (`N`/`E`/`S`/`W`), and the greatest Manhattan distance from the origin reached along the way.",
         r"""
const DIRS = { N: [0, 1], E: [1, 0], S: [0, -1], W: [-1, 0] } as const;
type Heading = keyof typeof DIRS;
const ORDER: Heading[] = ["N", "E", "S", "W"];
let x = 0;
let y = 0;
let h = 0;
let far = 0;
for (const c of input.trim()) {
  const heading = ORDER[h] ?? "N";
  const [dx, dy] = DIRS[heading];
  if (c === "L") h = (h + 3) % 4;
  else if (c === "R") h = (h + 1) % 4;
  else if (c === "F" || c === "B") {
    const s = c === "F" ? 1 : -1;
    x += dx * s;
    y += dy * s;
    far = Math.max(far, Math.abs(x) + Math.abs(y));
  }
}
console.log(`${x},${y}`);
console.log(ORDER[h]);
console.log(far);
""", ["FFRFF", "RRFFBLF", "", "FLFLFLF"],
         hints=["`as const` gives each heading a readonly `[dx, dy]` pair."]),
    _tsp(10, "tsm-w10-rps-league", "A rock-paper-scissors league", "core",
         "Each input line is `playerA moveA playerB moveB`. Moves are case-insensitive. A win is worth 3 points, a draw 1 each; an invalid move forfeits that game to the opponent (both invalid: no points). Print the table sorted by points descending then name: `name points`.",
         r"""
type Move = "rock" | "paper" | "scissors";
const BEATS: Record<Move, Move> = { rock: "scissors", paper: "rock", scissors: "paper" };
const toMove = (s: string): Move | undefined => (["rock", "paper", "scissors"] as const).find((m) => m === s.toLowerCase());
const points = new Map<string, number>();
const add = (p: string, n: number) => points.set(p, (points.get(p) ?? 0) + n);
for (const line of input.split("\n")) {
  const [a = "", ma = "", b = "", mb = ""] = line.trim().split(/\s+/);
  add(a, 0);
  add(b, 0);
  const x = toMove(ma);
  const y = toMove(mb);
  if (x === undefined && y === undefined) continue;
  if (x === undefined) add(b, 3);
  else if (y === undefined) add(a, 3);
  else if (x === y) {
    add(a, 1);
    add(b, 1);
  } else add(BEATS[x] === y ? a : b, 3);
}
const table = [...points].sort((p, q) => q[1] - p[1] || p[0].localeCompare(q[0]));
for (const [name, n] of table) console.log(`${name} ${n}`);
""", ["ann rock bob scissors\nbob paper cy paper\ncy lizard ann Rock", "x ROCK y rock\nx spock y spock"],
         hints=["`Record<Move, Move>` says what each move beats."]),
    _tsp(10, "tsm-w10-playlist", "Playlist modes", "stretch",
         "The first line is the playlist (track names); the second a list of commands: `next`, `prev`, and `mode:off`, `mode:all`, `mode:one`. Start at the first track in mode `off`. With `off`, `next` on the last track (or `prev` on the first) prints `end` and stays; `all` wraps around; `one` repeats the current track. Print the current track after each `next`/`prev`, and the mode name after a mode change.",
         r"""
type Mode = "off" | "all" | "one";
const [trackLine = "", commandLine = ""] = input.split("\n");
const tracks = trackLine.trim().split(/\s+/);
let mode: Mode = "off";
let i = 0;
for (const cmd of commandLine.trim().split(/\s+/)) {
  if (cmd.startsWith("mode:")) {
    const m = cmd.slice(5);
    if (m === "off" || m === "all" || m === "one") mode = m;
    console.log(mode);
    continue;
  }
  const step = cmd === "next" ? 1 : cmd === "prev" ? -1 : 0;
  if (step === 0) continue;
  if (mode === "one") {
    console.log(tracks[i]);
  } else if (mode === "all") {
    i = (i + step + tracks.length) % tracks.length;
    console.log(tracks[i]);
  } else if (i + step < 0 || i + step >= tracks.length) {
    console.log("end");
  } else {
    i += step;
    console.log(tracks[i]);
  }
}
""", ["a b c\nnext next next mode:all next prev prev mode:one next", "solo\nprev mode:all next mode:off next"],
         hints=["The mode is a literal union; each command's effect depends on it."]),
    _tsp(10, "tsm-w10-quantities", "Convert quantities", "stretch",
         "Each input line is `<amount><unit> to <unit>` (spaces optional between number and unit), with units `mm`, `cm`, `m`, `km`, `in`, `ft`, `mi` (1 in = 2.54 cm, 1 ft = 12 in, 1 mi = 5280 ft). Print the converted amount rounded to 3 decimals with trailing zeros removed, plus the unit — or `bad unit <u>` / `bad input`.",
         r"""
const PER_METRE = { mm: 1000, cm: 100, m: 1, km: 0.001, in: 100 / 2.54, ft: 100 / 2.54 / 12, mi: 100 / 2.54 / 12 / 5280 } as const;
type Unit = keyof typeof PER_METRE;
const isUnit = (u: string): u is Unit => Object.hasOwn(PER_METRE, u);
for (const line of input.split("\n")) {
  const m = line.trim().match(/^(-?\d+(?:\.\d+)?)\s*([a-z]+)\s+to\s+([a-z]+)$/);
  if (m === null) {
    console.log("bad input");
    continue;
  }
  const [, amount = "0", from = "", to = ""] = m;
  if (!isUnit(from)) console.log(`bad unit ${from}`);
  else if (!isUnit(to)) console.log(`bad unit ${to}`);
  else {
    const value = (Number(amount) / PER_METRE[from]) * PER_METRE[to];
    console.log(`${Number(value.toFixed(3))} ${to}`);
  }
}
""", ["5km to mi\n12 in to cm\n3 ft to m\n1 mi to km", "100cm to m\n2 yd to m\n7 m to furlong\nfive m to km"],
         hints=["One `as const` table from unit to \"how many per metre\" makes every conversion two multiplications."]),
]

TS_PROJECTS[10] = _project(
    10, "state.ts — a download state machine",
    "Model a download with states that carry their own data, and a transition function that rejects illegal moves instead of corrupting the state. Literal unions name the states and events; one table decides what is legal.",
    ["States: `idle`, `downloading`, `paused`, `done`, `failed`. Events: `start`, `progress <n>`, `pause`, `resume`, `finish`, `fail <reason>`, `reset`.",
     "Legal moves: idle→downloading (start); downloading→downloading (progress, adding n percent, capped at 100), →paused (pause), →done (finish), →failed (fail); paused→downloading (resume), →failed (fail); done/failed→idle (reset).",
     "Each input line is an event. Print the new state after a legal event — `downloading 40%`, `paused at 40%`, `done`, `failed: <reason>`, `idle` — or `illegal <event> in <state>` and keep the state.",
     "`finish` is only legal at 100%; below that it prints `illegal finish in downloading`.",
     "Model the event names and state names as literal unions."],
    r"""
type Status = "idle" | "downloading" | "paused" | "done" | "failed";
let status: Status = "idle";
let percent = 0;
let reason = "";
function describe(): string {
  switch (status) {
    case "idle": return "idle";
    case "downloading": return `downloading ${percent}%`;
    case "paused": return `paused at ${percent}%`;
    case "done": return "done";
    case "failed": return `failed: ${reason}`;
  }
}
for (const line of input.split("\n")) {
  const [event = "", ...args] = line.trim().split(/\s+/);
  const before = status;
  if (event === "start" && status === "idle") {
    status = "downloading";
    percent = 0;
  } else if (event === "progress" && status === "downloading") {
    percent = Math.min(100, percent + Number(args[0] ?? 0));
  } else if (event === "pause" && status === "downloading") {
    status = "paused";
  } else if (event === "resume" && status === "paused") {
    status = "downloading";
  } else if (event === "finish" && status === "downloading" && percent === 100) {
    status = "done";
  } else if (event === "fail" && (status === "downloading" || status === "paused")) {
    status = "failed";
    reason = args.join(" ") || "unknown";
  } else if (event === "reset" && (status === "done" || status === "failed")) {
    status = "idle";
  } else {
    console.log(`illegal ${event} in ${before}`);
    continue;
  }
  console.log(describe());
}
""", ["start\nprogress 40\npause\nprogress 10\nresume\nprogress 70\nfinish\nreset",
      "pause\nstart\nfail disk full\nresume\nreset\nstart\nfinish",
      "start\nprogress 50\nfinish\nprogress 50\nfinish",
      "start\nprogress 30\nprogress 90\nfinish\nreset\nreset",
      "start\npause\nfail\nreset\nstart\nprogress 5\npause\nresume\nprogress 95\nfinish"],
    stretch=["Rewrite the states as a discriminated union carrying their data (week 12), so `percent` can't exist in `idle`.",
             "Print an ASCII progress bar with each progress event."],
)

TS_PRACTICE_MORE[10] = [
    _pr("tsm-w10-p5", "An as-const tuple", 'const pair = ["x", 1] as const;\n', "pair", 'readonly ["x", 1]',
        hints=["`as const` keeps literal types and makes the tuple readonly."]),
    _pr("tsm-w10-p6", "Element type of a const array", 'const SIZES = ["S", "M", "L"] as const;\nconst first = SIZES[0];\n', "first", '"S"',
        hints=["Each position of a const tuple has its own literal type."]),
    _dx("tsm-w10-d5", "A widened literal",
        "error TS2345: Argument of type 'string' is not assignable to parameter of type '\"on\" | \"off\"'.",
        _STDIN + 'function set(state: "on" | "off"): string {\n  return state === "on" ? "light on" : "light off";\n}\nlet next = "on";\nif (input === "0") next = "off";\nconsole.log(set(next));\n',
        _STDIN + 'function set(state: "on" | "off"): string {\n  return state === "on" ? "light on" : "light off";\n}\nlet next: "on" | "off" = "on";\nif (input === "0") next = "off";\nconsole.log(set(next));\n',
        [("1", "light on"), ("0", "light off")], hints=["`let next = \"on\"` widens to `string`.", "Annotate it with the union."]),
    _fx("tsm-w10-f3", "A cast that isn't a check",
        "Print the colour's hex code, or `unknown` for a colour not in the table. Unknown colours print `undefined`.",
        _STDIN + 'const HEX = { red: "#f00", green: "#0f0" } as const;\ntype Color = keyof typeof HEX;\nconst c = input as Color;\nconsole.log(HEX[c]);\n',
        _STDIN + 'const HEX = { red: "#f00", green: "#0f0" } as const;\ntype Color = keyof typeof HEX;\nconst isColor = (s: string): s is Color => Object.hasOwn(HEX, s);\nconsole.log(isColor(input) ? HEX[input] : "unknown");\n',
        [("red", "#f00"), ("pink", "unknown")], hints=["`as Color` only silences the compiler.", "Check the input against the table."], difficulty="Medium"),
]

TS_CARDS_MORE[10] = [
    ("`let d = \"up\"` vs `const d = \"up\"` — types?", "`string` and `\"up\"`: a `let` might be reassigned, so its literal widens."),
    ("Why does `{ method: \"GET\" }` fail where `\"GET\" | \"POST\"` is expected?", "Object properties widen to `string`; use `as const` or annotate the object."),
    ("How do you derive a union from an array of values?", "`const XS = [...] as const; type X = (typeof XS)[number];`"),
    ("How do you turn an input string into a checked literal type?", "`XS.find((x) => x === text)` — it returns the element type or `undefined`; never `text as X`."),
    ("What does `as const` do at runtime?", "Nothing. It only changes types (readonly, literal); the object is not frozen."),
    ("`keyof typeof TABLE`?", "The union of the object's keys — the type of a valid lookup key."),
]

# ===========================================================================
# Week 11 — Narrowing, type guards, nullish, control-flow analysis
# ===========================================================================

TS_PROBLEM_SETS[11] = [
    _tsp(11, "tsm-w11-mixed-lines", "What is on each line?", "warm-up",
         "Each input line holds a number, `true`/`false`, `null`, or anything else (text). Parse each line into `number | boolean | null | string`, then narrow it to print `number <n> (even|odd|fraction)`, `boolean <b>`, `null`, or `text \"<t>\" (<k> chars)`.",
         r"""
type Value = number | boolean | null | string;
function parse(text: string): Value {
  const t = text.trim();
  if (t === "null") return null;
  if (t === "true" || t === "false") return t === "true";
  if (t !== "" && Number.isFinite(Number(t))) return Number(t);
  return t;
}
for (const line of input.split("\n")) {
  const v = parse(line);
  if (v === null) {
    console.log("null");
  } else if (typeof v === "number") {
    const parity = Number.isInteger(v) ? (v % 2 === 0 ? "even" : "odd") : "fraction";
    console.log(`number ${v} (${parity})`);
  } else if (typeof v === "boolean") {
    console.log(`boolean ${v}`);
  } else {
    console.log(`text "${v}" (${v.length} chars)`);
  }
}
""", ["42\ntrue\nnull\nhello\n3.5\n-7", "false\n0x10\nNaN\nnull value", "a\n\nb"],
         hints=["Check `null` first — `typeof null` is `\"object\"`, and it is not a number, boolean or string.",
                "After the `number` and `boolean` branches, what is left is a `string`."]),
    _tsp(11, "tsm-w11-sum-valid", "Sum what parses", "warm-up",
         "The input is numbers separated by spaces and/or commas, some of them garbage. Write `toNumber(text): number | undefined` (only finite numbers count) and use it to print the sum of the valid ones, then `skipped: <tokens>` in input order, or `skipped: none`.",
         r"""
function toNumber(text: string): number | undefined {
  const t = text.trim();
  if (t === "") return undefined;
  const n = Number(t);
  return Number.isFinite(n) ? n : undefined;
}
let sum = 0;
const skipped: string[] = [];
for (const token of input.split(/[\s,]+/)) {
  const n = toNumber(token);
  if (n === undefined) skipped.push(token);
  else sum += n;
}
console.log(sum);
console.log(skipped.length === 0 ? "skipped: none" : `skipped: ${skipped.join(" ")}`);
""", ["1 2 x 3", "4.5, -1, abc, 1e3, Infinity", "7", "1,,2 two 3"],
         hints=["`Number.isFinite` rejects `NaN` and `Infinity` in one check.",
                "Compare the result with `undefined` — `if (n)` would skip a real 0."]),
    _tsp(11, "tsm-w11-default-fill", "Fill in the defaults", "warm-up",
         "Each input line should be a JSON object with optional `name` (string), `age` (number) and `city` (string). Print `name=<n> age=<a> city=<c>` with the defaults `anonymous`, `?` and `nowhere` for anything missing or of the wrong type — but an empty name or an age of 0 is a real value and must be kept. A line that is not JSON prints `not JSON`; JSON that is not an object prints `not an object`.",
         r"""
for (const line of input.split("\n")) {
  let data: unknown;
  try {
    data = JSON.parse(line);
  } catch {
    console.log("not JSON");
    continue;
  }
  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    console.log("not an object");
    continue;
  }
  const name = "name" in data && typeof data.name === "string" ? data.name : undefined;
  const age = "age" in data && typeof data.age === "number" ? data.age : undefined;
  const city = "city" in data && typeof data.city === "string" ? data.city : undefined;
  console.log(`name=${name ?? "anonymous"} age=${age ?? "?"} city=${city ?? "nowhere"}`);
}
""", ['{"name":"Ana","age":31,"city":"Oslo"}\n{"age":0}\n{"name":"","city":null}\n[1,2]\n{oops',
      '{}\n{"name":"Bo","age":"old"}\n7'],
         hints=["`\"age\" in data` narrows `data` so `data.age` can be read (as `unknown`), then `typeof` narrows that.",
                "`??` falls back only for `null`/`undefined`; `||` would also replace `0` and `\"\"`."]),
    _tsp(11, "tsm-w11-nullable-average", "Average the readings you have", "warm-up",
         "Each input line is a series of sensor readings; `-` means the sensor was offline. Print the average of the present readings to two decimals and how many were missing — `<avg> (<k> missing)` — or `no data (<k> missing)` when every reading is missing.",
         r"""
for (const line of input.split("\n")) {
  const readings = line.trim().split(/\s+/).map((t) => (t === "-" ? null : Number(t)));
  const present = readings.filter((r) => r !== null);
  const missing = readings.length - present.length;
  if (present.length === 0) {
    console.log(`no data (${missing} missing)`);
  } else {
    const avg = present.reduce((a, b) => a + b, 0) / present.length;
    console.log(`${avg.toFixed(2)} (${missing} missing)`);
  }
}
""", ["3 - 5 - 7", "- -", "10\n1 2", "0 - 0"],
         hints=["Model an offline reading as `null`, so the array is `(number | null)[]`.",
                "`filter((r) => r !== null)` is inferred as a type predicate (TS 5.5), so the result is `number[]` with no cast."]),
    _tsp(11, "tsm-w11-validate-person", "Keep the people", "core",
         "Each input line should be JSON for a person: `name` (non-empty string), `age` (whole number ≥ 0) and optionally `email` (a string containing `@`). Write `isPerson(data: unknown): data is Person`. For each bad line print `line <n>: <reason>` — `not JSON`, `not an object`, `bad name`, `bad age` or `bad email` (the first that applies) — then list the valid people as `<name>, <age>` plus ` <email>` in angle brackets when present, then `<k> valid`.",
         r"""
type Person = { name: string; age: number; email?: string };
function problemWith(data: unknown): string | undefined {
  if (typeof data !== "object" || data === null || Array.isArray(data)) return "not an object";
  if (!("name" in data) || typeof data.name !== "string" || data.name.trim() === "") return "bad name";
  if (!("age" in data) || typeof data.age !== "number" || !Number.isInteger(data.age) || data.age < 0) return "bad age";
  if ("email" in data && (typeof data.email !== "string" || !data.email.includes("@"))) return "bad email";
  return undefined;
}
function isPerson(data: unknown): data is Person {
  return problemWith(data) === undefined;
}
const people: Person[] = [];
input.split("\n").forEach((line, i) => {
  let data: unknown;
  try {
    data = JSON.parse(line);
  } catch {
    console.log(`line ${i + 1}: not JSON`);
    return;
  }
  if (isPerson(data)) people.push(data);
  else console.log(`line ${i + 1}: ${problemWith(data) ?? "invalid"}`);
});
for (const p of people) console.log(`${p.name}, ${p.age}${p.email === undefined ? "" : ` <${p.email}>`}`);
console.log(`${people.length} valid`);
""", ['{"name":"Ana","age":31}\n{"name":"Bo","age":-2}\n{"name":"Cy","age":40,"email":"cy@x.io"}\nnope\n{"name":"","age":3}',
      '{"name":"Di","age":2.5}\n{"name":"Ed","age":20,"email":"ed"}\n[]\n{"name":"Flo","age":0}',
      '{"age":5}'],
         hints=["Write one function that returns the first problem (or `undefined`), and build the predicate on it.",
                "`\"name\" in data` narrows an `object` to one with a `name` property of type `unknown`."]),
    _tsp(11, "tsm-w11-shape-in", "Shapes told apart by their fields", "core",
         "Each input line is JSON for a shape, recognised by its fields: `{\"radius\"}`, `{\"side\"}` or `{\"width\",\"height\"}` (all positive numbers). Print each area to two decimals — or `bad shape` — and finally `total <sum>` to two decimals. Model the three shapes as a union with no tag, and tell them apart with `in`.",
         r"""
type Circle = { radius: number };
type Square = { side: number };
type Rect = { width: number; height: number };
type Shape = Circle | Square | Rect;
function area(s: Shape): number {
  if ("radius" in s) return Math.PI * s.radius ** 2;
  if ("side" in s) return s.side ** 2;
  return s.width * s.height;
}
function toShape(data: unknown): Shape | undefined {
  if (typeof data !== "object" || data === null) return undefined;
  const rec = data as Record<string, unknown>;
  const positive = (key: string): number | undefined => {
    const v = rec[key];
    return typeof v === "number" && v > 0 ? v : undefined;
  };
  const radius = positive("radius");
  const side = positive("side");
  const width = positive("width");
  const height = positive("height");
  if (radius !== undefined) return { radius };
  if (side !== undefined) return { side };
  if (width !== undefined && height !== undefined) return { width, height };
  return undefined;
}
let total = 0;
for (const line of input.split("\n")) {
  let data: unknown = null;
  try {
    data = JSON.parse(line);
  } catch {
    // not JSON: stays null, and toShape rejects it
  }
  const shape = toShape(data);
  if (shape === undefined) {
    console.log("bad shape");
    continue;
  }
  const a = area(shape);
  total += a;
  console.log(a.toFixed(2));
}
console.log(`total ${total.toFixed(2)}`);
""", ['{"radius":1}\n{"side":3}\n{"width":2,"height":5}\n{"width":2}\nhello',
      '{"radius":-1}\n{"side":0.5}', '{"radius":2,"side":9}'],
         hints=["`\"radius\" in s` narrows a union to the members that declare `radius`.",
                "After ruling out circles and squares, only `Rect` is left — no third check needed."]),
    _tsp(11, "tsm-w11-deep-get", "Follow a path through JSON", "core",
         "The first input line is a JSON document; each later line is a dotted path such as `user.langs.1`. Array steps are indexes; object steps must be the object's own keys. Print the value at the path as JSON, or `missing` if any step fails.",
         r"""
const [doc = "null", ...paths] = input.split("\n");
const root: unknown = JSON.parse(doc);
function step(value: unknown, key: string): unknown {
  if (Array.isArray(value)) {
    const i = Number(key);
    return Number.isInteger(i) && i >= 0 && i < value.length ? value[i] : undefined;
  }
  if (typeof value === "object" && value !== null && Object.hasOwn(value, key)) {
    return (value as Record<string, unknown>)[key];
  }
  return undefined;
}
for (const path of paths) {
  let value: unknown = root;
  for (const key of path.trim().split(".")) {
    value = step(value, key);
    if (value === undefined) break;
  }
  console.log(value === undefined ? "missing" : JSON.stringify(value));
}
""", ['{"user":{"name":"Ana","langs":["ts","go"],"address":null},"n":0}\nuser.name\nuser.langs.1\nuser.langs.5\nuser.address\nuser.address.city\nn\nuser.toString',
      '[[1,2],[3,[4,5]]]\n1.1.0\n0\n0.-1\n2'],
         hints=["Narrow in order: array first (`Array.isArray`), then object (`typeof … === \"object\" && … !== null`).",
                "`Object.hasOwn` keeps inherited names like `toString` from counting as keys."]),
    _tsp(11, "tsm-w11-event-filter", "Errors from a messy log", "core",
         "Each input line should be a JSON log event: `level` (`info`, `warn` or `error`), `msg` (string) and optionally `user` (string). Anything else is skipped. Parse each line to `LogEvent | undefined`, keep the good ones with `filter`, then print every error as `<user>: <msg>` (`(system)` when there is no user), then `info=<a> warn=<b> error=<c>`, then `skipped <k>`.",
         r"""
type Level = "info" | "warn" | "error";
type LogEvent = { level: Level; msg: string; user?: string };
const isLevel = (s: string): s is Level => s === "info" || s === "warn" || s === "error";
function parse(line: string): LogEvent | undefined {
  let data: unknown;
  try {
    data = JSON.parse(line);
  } catch {
    return undefined;
  }
  if (typeof data !== "object" || data === null) return undefined;
  if (!("level" in data) || typeof data.level !== "string" || !isLevel(data.level)) return undefined;
  if (!("msg" in data) || typeof data.msg !== "string") return undefined;
  const event: LogEvent = { level: data.level, msg: data.msg };
  if ("user" in data && typeof data.user === "string") event.user = data.user;
  return event;
}
const lines = input.split("\n");
const events = lines.map(parse).filter((e) => e !== undefined);
for (const e of events) {
  if (e.level === "error") console.log(`${e.user ?? "(system)"}: ${e.msg}`);
}
const counts: Record<Level, number> = { info: 0, warn: 0, error: 0 };
for (const e of events) counts[e.level]++;
console.log(`info=${counts.info} warn=${counts.warn} error=${counts.error}`);
console.log(`skipped ${lines.length - events.length}`);
""", ['{"level":"info","msg":"boot"}\n{"level":"error","msg":"disk full","user":"ana"}\n{"level":"error","msg":"oom"}\n{"level":"debug","msg":"x"}\ngarbage\n{"level":"warn","msg":"slow"}',
      '{"level":"error","msg":42}\n{"level":"warn","msg":"a","user":7}'],
         hints=["`lines.map(parse)` is `(LogEvent | undefined)[]`; `filter((e) => e !== undefined)` narrows it to `LogEvent[]` by itself.",
                "A type predicate `isLevel` turns a checked string into a `Level`."]),
    _tsp(11, "tsm-w11-coerce", "Coerce or reject", "stretch",
         "Each input line is `<type> <value>` with type `int`, `bool`, `date` or `list`. Print `ok <normalised>` or `reject: <reason>`. `int`: an optional minus and digits (`not an integer`), and a safe integer (`too large`). `bool`: `true/false/yes/no/1/0` in any case, printed as `true`/`false` (`not a boolean`). `date`: `YYYY-MM-DD` (`not YYYY-MM-DD`) that exists on the calendar (`no such day`). `list`: comma-separated ints, printed as `[a,b] (<count>)` (`bad item <x>`). Any other type: `unknown type <t>`. Write an assertion function `check(condition, reason): asserts condition` and use it for every rule.",
         r"""
class Rejected extends Error {}
function check(condition: unknown, reason: string): asserts condition {
  if (!condition) throw new Rejected(reason);
}
function toInt(raw: string, reason: string): number {
  check(/^-?\d+$/.test(raw), reason);
  const n = Number(raw);
  check(Number.isSafeInteger(n), "too large");
  return n;
}
function coerce(kind: string, raw: string): string {
  switch (kind) {
    case "int":
      return String(toInt(raw, "not an integer"));
    case "bool": {
      const t = raw.toLowerCase();
      check(["true", "false", "yes", "no", "1", "0"].includes(t), "not a boolean");
      return String(t === "true" || t === "yes" || t === "1");
    }
    case "date": {
      const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(raw);
      check(m !== null, "not YYYY-MM-DD");
      const year = Number(m[1]);
      const month = Number(m[2]);
      const day = Number(m[3]);
      const date = new Date(Date.UTC(year, month - 1, day));
      check(date.getUTCMonth() === month - 1 && date.getUTCDate() === day, "no such day");
      return raw;
    }
    case "list": {
      const items = raw.split(",").map((item) => toInt(item, `bad item ${item}`));
      return `[${items.join(",")}] (${items.length})`;
    }
    default:
      throw new Rejected(`unknown type ${kind}`);
  }
}
for (const line of input.split("\n")) {
  const [kind = "", raw = ""] = line.trim().split(/\s+/);
  try {
    console.log(`ok ${coerce(kind, raw)}`);
  } catch (e) {
    if (e instanceof Rejected) console.log(`reject: ${e.message}`);
    else throw e;
  }
}
""", ["int -042\nint 4.5\nint 99999999999999999\nbool YES\nbool maybe",
      "date 2024-02-29\ndate 2023-02-29\ndate 24-1-1\nlist 1,2,-3\nlist 1,x,3\ncolor red"],
         hints=["After `check(m !== null, …)` returns, the compiler knows `m` is not `null` — that is what `asserts condition` means.",
                "Throw a class of your own so the caller can tell a rejection from a real bug."]),
    _tsp(11, "tsm-w11-safe-queries", "Queries that may miss", "stretch",
         "The first line is a list of integers; each later line is a query: `get i` (negative `i` counts from the end), `sum a b` or `slice a b` (the half-open range `a..b`, with `0 ≤ a ≤ b ≤ length`). Print the answer — `slice` prints the values or `(empty)` — or `out of range`, or `unknown <op>`.",
         r"""
const [first = "", ...queries] = input.split("\n");
const xs = first.trim().split(/\s+/).map(Number);
for (const q of queries) {
  const [op = "", a = "", b = ""] = q.trim().split(/\s+/);
  if (op === "get") {
    const i = Number(a);
    const v = a !== "" && Number.isInteger(i) ? xs.at(i) : undefined;
    console.log(v === undefined ? "out of range" : v);
  } else if (op === "sum" || op === "slice") {
    const lo = Number(a);
    const hi = Number(b);
    const ok = a !== "" && b !== "" && Number.isInteger(lo) && Number.isInteger(hi) && 0 <= lo && lo <= hi && hi <= xs.length;
    if (!ok) {
      console.log("out of range");
      continue;
    }
    const part = xs.slice(lo, hi);
    console.log(op === "sum" ? part.reduce((s, x) => s + x, 0) : part.join(" ") || "(empty)");
  } else {
    console.log(`unknown ${op}`);
  }
}
""", ["5 8 13 21\nget 0\nget -1\nget 4\nsum 1 3\nslice 2 2\nslice 3 9\ntwist 1", "7\nget\nget -2\nsum 0 1\nslice 0 1"],
         hints=["`xs.at(i)` is typed `number | undefined` even without `noUncheckedIndexedAccess` — handle it.",
                "Validate both bounds before slicing; `slice` silently clamps bad ones."]),
]

TS_PROJECTS[11] = _project(
    11, "validate.ts — a record validator that explains itself",
    "Data from outside a program is `unknown` until proven otherwise. Build a validator that turns each JSON line into either a typed `Person` or a list of every problem with it — not just the first — so whoever sent the data can fix it in one pass.",
    ["Each input line is one record. A valid record is a JSON object with `name` (a non-empty string), `age` (a whole number from 0 to 150), and optionally `email` (a string containing `@`) and `tags` (an array of strings). Any other field is an error.",
     "For each line print `line <n>: ok`, or `line <n>: ` followed by every problem joined by `; `, in this order: `name missing` / `name must be a non-empty string`, `age missing` / `age must be an integer from 0 to 150`, `email must contain @`, `tags must be an array of strings`, then `unknown field <key>` for each extra key in input order.",
     "A line that is not JSON prints `line <n>: not JSON`; JSON that is not an object prints `line <n>: not an object`.",
     "Then print `valid <k> of <n>`, `average age <a>` (one decimal, or `-` with no valid records) and `tags: <t>` — the distinct tags of the valid records, sorted and comma-separated, or `none`.",
     "Validate from `unknown` with narrowing and a type predicate `isPerson(data): data is Person` — no `as Person`."],
    r"""
type Person = { name: string; age: number; email?: string; tags?: string[] };
const KNOWN = new Set(["name", "age", "email", "tags"]);
function problems(data: unknown): string[] {
  if (typeof data !== "object" || data === null || Array.isArray(data)) return ["not an object"];
  const out: string[] = [];
  if (!("name" in data)) out.push("name missing");
  else if (typeof data.name !== "string" || data.name.trim() === "") out.push("name must be a non-empty string");
  if (!("age" in data)) out.push("age missing");
  else if (typeof data.age !== "number" || !Number.isInteger(data.age) || data.age < 0 || data.age > 150) {
    out.push("age must be an integer from 0 to 150");
  }
  if ("email" in data && (typeof data.email !== "string" || !data.email.includes("@"))) out.push("email must contain @");
  if ("tags" in data && !(Array.isArray(data.tags) && data.tags.every((t) => typeof t === "string"))) {
    out.push("tags must be an array of strings");
  }
  for (const key of Object.keys(data)) if (!KNOWN.has(key)) out.push(`unknown field ${key}`);
  return out;
}
function isPerson(data: unknown): data is Person {
  return problems(data).length === 0;
}
const valid: Person[] = [];
const lines = input.split("\n");
lines.forEach((line, i) => {
  let data: unknown;
  try {
    data = JSON.parse(line);
  } catch {
    console.log(`line ${i + 1}: not JSON`);
    return;
  }
  if (isPerson(data)) {
    valid.push(data);
    console.log(`line ${i + 1}: ok`);
  } else {
    console.log(`line ${i + 1}: ${problems(data).join("; ")}`);
  }
});
console.log(`valid ${valid.length} of ${lines.length}`);
const average = valid.length === 0 ? "-" : (valid.reduce((s, p) => s + p.age, 0) / valid.length).toFixed(1);
console.log(`average age ${average}`);
const tags = [...new Set(valid.flatMap((p) => p.tags ?? []))].sort();
console.log(`tags: ${tags.join(",") || "none"}`);
""", ['{"name":"Ana","age":31,"tags":["admin","ops"]}\n{"name":"Bo","age":44,"email":"bo@x.io","tags":["ops"]}\n{"name":"Cy","age":19}',
      '{"age":20}\n{"name":"","age":200,"email":"nope"}\n{"name":"Di","age":3,"role":"x","id":7}',
      'not json\n[1,2]\n{"name":"Ed","age":2.5,"tags":"a,b"}\nnull',
      '{"name":"Flo","age":0}\n{"name":"Gus","age":150,"tags":[]}\n{"name":"Hal","age":150,"tags":[1]}',
      '{"name":"Ivy","age":28,"email":"ivy@example.com","tags":["z","a","z"]}'],
    stretch=["Report the path of the problem for nested data (`address.city must be a string`).",
             "Return a discriminated union `{ ok: true; value: Person } | { ok: false; problems: string[] }` instead of two functions."],
)

TS_PRACTICE_MORE[11] = [
    _pr("tsm-w11-p2", "An inferred type predicate",
        "const xs = [1, undefined, 3].filter((x) => x !== undefined);\n", "xs", "number[]",
        hints=["Since TS 5.5 the arrow is inferred as `(x) => x is number`.", "So `filter` returns `number[]`."]),
    _pr("tsm-w11-p3", "A match result", 'const m = "a1b2".match(/\\d/g);\n', "m", "RegExpMatchArray | null",
        hints=["`match` finds nothing sometimes.", "It returns `null` then, not an empty array."]),
    _dx("tsm-w11-d3", "A match that might fail",
        "error TS18047: 'm' is possibly 'null'.",
        _STDIN + "const m = input.match(/\\d+/);\nconsole.log(Number(m[0]) * 2);\n",
        _STDIN + 'const m = input.match(/\\d+/);\nconsole.log(m === null ? "no number" : Number(m[0]) * 2);\n',
        [("abc 21 def", "42"), ("none", "no number")],
        ask="Print double the first number in the input, or `no number`.",
        hints=["`match` returns `null` when nothing matches.", "Handle that case before reading `m[0]`."]),
    _fx("tsm-w11-f1", "Zero is not missing",
        "Print each quantity, or `missing` for `-`. A quantity of 0 prints `missing` too.",
        _STDIN + 'const qty = input.split(" ").map((t) => (t === "-" ? undefined : Number(t)));\nconsole.log(qty.map((q) => (q ? q : "missing")).join(" "));\n',
        _STDIN + 'const qty = input.split(" ").map((t) => (t === "-" ? undefined : Number(t)));\nconsole.log(qty.map((q) => q ?? "missing").join(" "));\n',
        [("3 - 0", "3 missing 0"), ("-", "missing"), ("0 0", "0 0")],
        hints=["Truthiness treats `0` like `undefined`.", "`??` only replaces `null` and `undefined`."]),
]

TS_CARDS_MORE[11] = [
    ("`[1, undefined].filter((x) => x !== undefined)` — the result type since TS 5.5?", "`number[]`: the arrow is inferred as a type predicate, so `filter` narrows without a cast."),
    ("`asserts cond` vs `asserts x is T`?", "The first narrows by whatever condition you passed (`check(m !== null)`); the second narrows one argument to `T`. Both must throw when the check fails."),
    ("Can an assertion function be an arrow assigned to a `const` without an annotation?", "No — calls to assertion functions need an explicitly declared type, so use a function declaration or annotate the `const`."),
    ("Does `if (\"email\" in data)` work when `data: object`?", "Yes — it narrows to `object & Record<\"email\", unknown>`; then check `typeof data.email`."),
    ("`const isStr = typeof x === \"string\"; if (isStr) …` — does `x` narrow?", "Yes (TS 4.4+), when `x` is a `const` or unassigned parameter and the condition is stored in a `const`."),
    ("`xs.at(-1)` — its type without `noUncheckedIndexedAccess`?", "`T | undefined` regardless of the flag — `at` is declared that way, so it is always honest."),
]

# ===========================================================================
# Week 12 — Discriminated unions, top and bottom types
# ===========================================================================

TS_PROBLEM_SETS[12] = [
    _tsp(12, "tsm-w12-shapes", "Areas from a tagged union", "warm-up",
         "Each input line is `circle r`, `rect w h` or `tri base height` (positive numbers). Parse each into a discriminated union and print `<kind> <area>` (two decimals) or `bad line`, then `total <sum>` and `largest <kind>` (the first on a tie; `none` if nothing parsed). The area function must end in a `never` exhaustiveness check.",
         r"""
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "rect"; w: number; h: number }
  | { kind: "tri"; base: number; height: number };
function parse(line: string): Shape | undefined {
  const [kind = "", ...rest] = line.trim().split(/\s+/);
  const n = rest.map(Number);
  if (n.some((x) => !(x > 0))) return undefined;
  const [a = 0, b = 0] = n;
  if (kind === "circle" && n.length === 1) return { kind, r: a };
  if (kind === "rect" && n.length === 2) return { kind, w: a, h: b };
  if (kind === "tri" && n.length === 2) return { kind, base: a, height: b };
  return undefined;
}
function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.r * s.r;
    case "rect":
      return s.w * s.h;
    case "tri":
      return (s.base * s.height) / 2;
    default: {
      const unreachable: never = s;
      return unreachable;
    }
  }
}
let total = 0;
let largest: Shape | undefined;
for (const line of input.split("\n")) {
  const s = parse(line);
  if (s === undefined) {
    console.log("bad line");
    continue;
  }
  const a = area(s);
  total += a;
  if (largest === undefined || a > area(largest)) largest = s;
  console.log(`${s.kind} ${a.toFixed(2)}`);
}
console.log(`total ${total.toFixed(2)}`);
console.log(`largest ${largest?.kind ?? "none"}`);
""", ["circle 1\nrect 2 3\ntri 4 5\nhexagon 2\nrect 2", "tri 10 10\ncircle -1", "blob"],
         hints=["Check `kind` and the number count together, then build the member with the literal `kind`.",
                "In `default:`, assigning `s` to a `never` only compiles when every kind was handled."]),
    _tsp(12, "tsm-w12-rpn", "A calculator in reverse Polish", "warm-up",
         "Each input line is an expression in reverse Polish notation (`3 4 + 2 *`). Tokenise into `{ kind: \"num\" } | { kind: \"op\" }` and evaluate with a stack. Print the result (rounded to at most 4 decimals), or the first error: `bad token <t>`, `stack underflow`, `division by zero`, or `leftover <k>` when more than one value remains.",
         r"""
type Op = "+" | "-" | "*" | "/";
type Token = { kind: "num"; value: number } | { kind: "op"; op: Op };
function tokenize(t: string): Token | undefined {
  if (t === "+" || t === "-" || t === "*" || t === "/") return { kind: "op", op: t };
  const n = Number(t);
  return t !== "" && Number.isFinite(n) ? { kind: "num", value: n } : undefined;
}
function evaluate(line: string): string {
  const stack: number[] = [];
  for (const raw of line.trim().split(/\s+/)) {
    const tok = tokenize(raw);
    if (tok === undefined) return `bad token ${raw}`;
    if (tok.kind === "num") {
      stack.push(tok.value);
      continue;
    }
    const b = stack.pop();
    const a = stack.pop();
    if (a === undefined || b === undefined) return "stack underflow";
    if (tok.op === "/" && b === 0) return "division by zero";
    stack.push(tok.op === "+" ? a + b : tok.op === "-" ? a - b : tok.op === "*" ? a * b : a / b);
  }
  if (stack.length !== 1) return `leftover ${stack.length}`;
  return String(Number((stack[0] ?? 0).toFixed(4)));
}
for (const line of input.split("\n")) console.log(evaluate(line));
""", ["3 4 + 2 *\n10 3 /\n1 +\n4 0 /\n1 2 3 +\n2 x *", "5\n-2 -3 *\n1 2 3 4 + + +"],
         hints=["After `tok.kind === \"num\"` is handled, `tok` is narrowed to the operator member.",
                "Pop the right operand first."]),
    _tsp(12, "tsm-w12-bank-replay", "Replay the bank's events", "warm-up",
         "Each input line is `deposit <acct> <n>`, `withdraw <acct> <n>` or `transfer <from> <to> <n>` (positive whole amounts). Parse into a discriminated union (a bad line prints `bad line <n>`), apply in order, and reject any withdrawal or transfer that would overdraw with `rejected <line>: insufficient funds`. Finally print every account that appeared in an applied event as `<acct> <balance>`, sorted by name.",
         r"""
type BankEvent =
  | { kind: "deposit"; account: string; amount: number }
  | { kind: "withdraw"; account: string; amount: number }
  | { kind: "transfer"; from: string; to: string; amount: number };
function parse(line: string): BankEvent | undefined {
  const [kind = "", a = "", b = "", c = ""] = line.trim().split(/\s+/);
  if (kind === "deposit" || kind === "withdraw") {
    const amount = Number(b);
    return a !== "" && Number.isInteger(amount) && amount > 0 ? { kind, account: a, amount } : undefined;
  }
  if (kind === "transfer") {
    const amount = Number(c);
    return a !== "" && b !== "" && a !== b && Number.isInteger(amount) && amount > 0 ? { kind, from: a, to: b, amount } : undefined;
  }
  return undefined;
}
const balances = new Map<string, number>();
const balance = (acct: string) => balances.get(acct) ?? 0;
input.split("\n").forEach((line, i) => {
  const e = parse(line);
  if (e === undefined) {
    console.log(`bad line ${i + 1}`);
    return;
  }
  switch (e.kind) {
    case "deposit":
      balances.set(e.account, balance(e.account) + e.amount);
      break;
    case "withdraw":
      if (balance(e.account) < e.amount) console.log(`rejected ${i + 1}: insufficient funds`);
      else balances.set(e.account, balance(e.account) - e.amount);
      break;
    case "transfer":
      if (balance(e.from) < e.amount) {
        console.log(`rejected ${i + 1}: insufficient funds`);
      } else {
        balances.set(e.from, balance(e.from) - e.amount);
        balances.set(e.to, balance(e.to) + e.amount);
      }
      break;
  }
});
for (const [acct, n] of [...balances].sort(([a], [b]) => a.localeCompare(b))) console.log(`${acct} ${n}`);
""", ["deposit ana 100\nwithdraw ana 30\ntransfer ana bo 50\ntransfer ana bo 50\nwithdraw bo 10",
      "withdraw cy 5\ndeposit cy -5\ntransfer cy cy 1\nrefund cy 3\ndeposit cy 7"],
         hints=["Parse once into the union; every later step switches on `kind`.",
                "`kind === \"deposit\" || kind === \"withdraw\"` gives a member whose `kind` is either — TypeScript accepts it as the union."]),
    _tsp(12, "tsm-w12-todo-reducer", "A todo list as a reducer", "core",
         "Each input line is an action: `add <text…>`, `toggle <id>`, `remove <id>`, `rename <id> <text…>` or `clear-done`. Ids start at 1 and are never reused. Parse each line into an `Action` union (skip anything else), fold them with a pure `reduce(state, action): State` that never mutates, then print each todo as `[x] <id> <text>` or `[ ] <id> <text>`, then `<k> left` (undone count).",
         r"""
type Todo = { readonly id: number; readonly text: string; readonly done: boolean };
type State = { readonly todos: readonly Todo[]; readonly nextId: number };
type Action =
  | { type: "add"; text: string }
  | { type: "toggle"; id: number }
  | { type: "remove"; id: number }
  | { type: "rename"; id: number; text: string }
  | { type: "clear-done" };
function parse(line: string): Action | undefined {
  const [type = "", arg = "", ...rest] = line.trim().split(/\s+/);
  const id = Number(arg);
  if (type === "add" && arg !== "") return { type, text: [arg, ...rest].join(" ") };
  if ((type === "toggle" || type === "remove") && Number.isInteger(id)) return { type, id };
  if (type === "rename" && Number.isInteger(id) && rest.length > 0) return { type, id, text: rest.join(" ") };
  if (type === "clear-done") return { type };
  return undefined;
}
function reduce(state: State, action: Action): State {
  switch (action.type) {
    case "add":
      return { todos: [...state.todos, { id: state.nextId, text: action.text, done: false }], nextId: state.nextId + 1 };
    case "toggle":
      return { ...state, todos: state.todos.map((t) => (t.id === action.id ? { ...t, done: !t.done } : t)) };
    case "remove":
      return { ...state, todos: state.todos.filter((t) => t.id !== action.id) };
    case "rename":
      return { ...state, todos: state.todos.map((t) => (t.id === action.id ? { ...t, text: action.text } : t)) };
    case "clear-done":
      return { ...state, todos: state.todos.filter((t) => !t.done) };
  }
}
const actions = input.split("\n").map(parse).filter((a) => a !== undefined);
const final = actions.reduce(reduce, { todos: [], nextId: 1 });
for (const t of final.todos) console.log(`[${t.done ? "x" : " "}] ${t.id} ${t.text}`);
console.log(`${final.todos.filter((t) => !t.done).length} left`);
""", ["add buy milk\nadd call mum\nadd fix bike\ntoggle 1\nrename 3 fix the bike\nremove 2\nadd walk",
      "add a\nadd b\ntoggle 1\ntoggle 2\nclear-done\nadd c\ntoggle 9\nnonsense",
      "clear-done"],
         hints=["Each `case` returns a new state built with spreads; nothing is assigned to.",
                "With a `switch` that returns from every case, the compiler knows the function always returns."]),
    _tsp(12, "tsm-w12-expr", "Evaluate a prefix expression", "core",
         "Each input line is an expression in parentheses: numbers, `(neg e)`, or `(op a b)` with op `+ - * max min`. Parse it into a recursive union (`num`, `neg`, `bin`), then print it in infix form and its value: `(1 + (2 * 3)) = 7`. `neg` prints as `-x`, `max`/`min` as `max(a, b)`. Print `error: <message>` for malformed input (`unexpected end`, `bad atom <t>`, `bad operator <t>`, `expected )`, `trailing input`).",
         r"""
type Expr =
  | { kind: "num"; value: number }
  | { kind: "neg"; arg: Expr }
  | { kind: "bin"; op: "+" | "-" | "*" | "max" | "min"; left: Expr; right: Expr };
function parse(tokens: string[]): Expr {
  let pos = 0;
  const next = (): string => {
    const t: string | undefined = tokens[pos++];
    if (t === undefined) throw new Error("unexpected end");
    return t;
  };
  const expr = (): Expr => {
    const t = next();
    if (t !== "(") {
      const n = Number(t);
      if (t === ")" || !Number.isFinite(n)) throw new Error(`bad atom ${t}`);
      return { kind: "num", value: n };
    }
    const op = next();
    let result: Expr;
    if (op === "neg") {
      result = { kind: "neg", arg: expr() };
    } else if (op === "+" || op === "-" || op === "*" || op === "max" || op === "min") {
      const left = expr();
      const right = expr();
      result = { kind: "bin", op, left, right };
    } else {
      throw new Error(`bad operator ${op}`);
    }
    if (next() !== ")") throw new Error("expected )");
    return result;
  };
  const e = expr();
  if (pos !== tokens.length) throw new Error("trailing input");
  return e;
}
function evaluate(e: Expr): number {
  switch (e.kind) {
    case "num":
      return e.value;
    case "neg":
      return -evaluate(e.arg);
    case "bin": {
      const a = evaluate(e.left);
      const b = evaluate(e.right);
      switch (e.op) {
        case "+": return a + b;
        case "-": return a - b;
        case "*": return a * b;
        case "max": return Math.max(a, b);
        case "min": return Math.min(a, b);
      }
    }
  }
}
function show(e: Expr): string {
  switch (e.kind) {
    case "num":
      return String(e.value);
    case "neg":
      return `-${show(e.arg)}`;
    case "bin":
      return e.op === "max" || e.op === "min"
        ? `${e.op}(${show(e.left)}, ${show(e.right)})`
        : `(${show(e.left)} ${e.op} ${show(e.right)})`;
  }
}
for (const line of input.split("\n")) {
  const tokens = line.replace(/\(/g, " ( ").replace(/\)/g, " ) ").trim().split(/\s+/);
  try {
    const e = parse(tokens);
    console.log(`${show(e)} = ${evaluate(e)}`);
  } catch (err) {
    console.log(`error: ${err instanceof Error ? err.message : String(err)}`);
  }
}
""", ["(+ 1 (* 2 3))\n(neg (- 2 7))\n(max 4 (min 9 6))\n42", "(+ 1)\n(^ 1 2)\n(+ 1 2 3)\n(+ 1 2) 3\n(* x 2)"],
         hints=["A recursive type: `neg` and `bin` hold `Expr`s. Parsing and evaluation are both recursive over it.",
                "Keep the cursor in a closure (`pos`) and read tokens through one `next()` that throws at the end."]),
    _tsp(12, "tsm-w12-http", "Handle every kind of response", "core",
         "Each input line is `<status> <rest…>`. Classify it into a union — `ok` (200-299, rest is the body), `redirect` (300-399, rest is the location), `client` (400-499, rest is the message) or `server` (500-599). Print `show \"<body>\"`, `follow <location>` (or `broken redirect` when there is none), `fail <status>: <message>`, `retry` (for 502, 503, 504) or `give up`; a status outside 200-599 prints `bad status <s>`. Finish with `ok=<a> redirect=<b> client=<c> server=<d>`.",
         r"""
type Response =
  | { kind: "ok"; body: string }
  | { kind: "redirect"; location: string }
  | { kind: "client"; status: number; message: string }
  | { kind: "server"; status: number };
function classify(status: number, rest: string): Response | undefined {
  if (!Number.isInteger(status)) return undefined;
  if (status >= 200 && status < 300) return { kind: "ok", body: rest };
  if (status >= 300 && status < 400) return { kind: "redirect", location: rest };
  if (status >= 400 && status < 500) return { kind: "client", status, message: rest };
  if (status >= 500 && status < 600) return { kind: "server", status };
  return undefined;
}
function handle(r: Response): string {
  switch (r.kind) {
    case "ok":
      return `show "${r.body}"`;
    case "redirect":
      return r.location === "" ? "broken redirect" : `follow ${r.location}`;
    case "client":
      return `fail ${r.status}: ${r.message}`;
    case "server":
      return [502, 503, 504].includes(r.status) ? "retry" : "give up";
  }
}
const counts: Record<Response["kind"], number> = { ok: 0, redirect: 0, client: 0, server: 0 };
for (const line of input.split("\n")) {
  const [code = "", ...rest] = line.trim().split(/\s+/);
  const r = classify(Number(code), rest.join(" "));
  if (r === undefined) {
    console.log(`bad status ${code}`);
    continue;
  }
  counts[r.kind]++;
  console.log(handle(r));
}
console.log(`ok=${counts.ok} redirect=${counts.redirect} client=${counts.client} server=${counts.server}`);
""", ["200 hello world\n301 /new-home\n404 not found\n503\n500\n302\n99 x", "204\n418 I'm a teapot\n504 gateway\nabc"],
         hints=["`Response[\"kind\"]` is the union of the tags — a ready-made key type for the counts.",
                "Each `case` sees only its own member's fields."]),
    _tsp(12, "tsm-w12-undo", "An editor with undo and redo", "core",
         "Each input line is a command: `type <text…>` (append the text, spaces included), `delete <n>` (remove the last n characters, fewer if the document is shorter), `undo`, `redo`, or `print`. Record each edit as `{ kind: \"insert\"; text } | { kind: \"delete\"; removed }` so it can be undone exactly. A new edit clears the redo history. `print` prints the document in quotes; `undo`/`redo` with nothing to do print `nothing to undo`/`nothing to redo`.",
         r"""
type Edit = { kind: "insert"; text: string } | { kind: "delete"; removed: string };
let doc = "";
const done: Edit[] = [];
const undone: Edit[] = [];
function apply(e: Edit): void {
  switch (e.kind) {
    case "insert":
      doc += e.text;
      break;
    case "delete":
      doc = doc.slice(0, doc.length - e.removed.length);
      break;
  }
}
function revert(e: Edit): void {
  switch (e.kind) {
    case "insert":
      doc = doc.slice(0, doc.length - e.text.length);
      break;
    case "delete":
      doc += e.removed;
      break;
  }
}
for (const line of input.split("\n")) {
  const space = line.indexOf(" ");
  const cmd = space < 0 ? line.trim() : line.slice(0, space);
  const arg = space < 0 ? "" : line.slice(space + 1);
  if (cmd === "type" || cmd === "delete") {
    const n = Math.max(0, Math.min(doc.length, Number(arg) || 0));
    const edit: Edit = cmd === "type" ? { kind: "insert", text: arg } : { kind: "delete", removed: doc.slice(doc.length - n) };
    apply(edit);
    done.push(edit);
    undone.length = 0;
  } else if (cmd === "undo" || cmd === "redo") {
    const from = cmd === "undo" ? done : undone;
    const to = cmd === "undo" ? undone : done;
    const e = from.pop();
    if (e === undefined) {
      console.log(`nothing to ${cmd}`);
      continue;
    }
    if (cmd === "undo") revert(e);
    else apply(e);
    to.push(e);
  } else if (cmd === "print") {
    console.log(`"${doc}"`);
  }
}
""", ["type hello\ntype  world\nprint\ndelete 6\nprint\nundo\nprint\nredo\nredo\nprint",
      "undo\ntype abc\ndelete 10\nprint\nundo\nundo\nundo\nprint\nredo\ntype !\nredo\nprint"],
         hints=["A deletion must remember the text it removed, or undo cannot put it back.",
                "Undo moves an edit from `done` to `undone`; redo moves it back."]),
    _tsp(12, "tsm-w12-vm", "A tiny stack machine", "stretch",
         "The input is a program, one instruction per line (numbered from 0): `push n`, `add`, `sub`, `mul`, `dup`, `swap`, `print` (pop and print), `jmp t`, `jz t` (pop; jump to line t if it was 0), `halt`. Parse the whole program into an instruction union first — the first bad line prints `line <k>: bad instruction` and nothing runs. Then execute: stop at `halt` (`halted`), past the last line (`ended`), on underflow (`underflow at <k>`), on a jump outside the program (`bad jump at <k>`) or after 10000 steps (`step limit`). Finally print `stack: <values>` or `stack: empty`.",
         r"""
type Instr =
  | { op: "push"; value: number }
  | { op: "add" | "sub" | "mul" | "dup" | "swap" | "print" | "halt" }
  | { op: "jmp" | "jz"; target: number };
function parseLine(line: string): Instr | undefined {
  const [op = "", arg = ""] = line.trim().split(/\s+/);
  const n = Number(arg);
  if (op === "push") return arg !== "" && Number.isInteger(n) ? { op, value: n } : undefined;
  if (op === "jmp" || op === "jz") return arg !== "" && Number.isInteger(n) ? { op, target: n } : undefined;
  if (op === "add" || op === "sub" || op === "mul" || op === "dup" || op === "swap" || op === "print" || op === "halt") {
    return arg === "" ? { op } : undefined;
  }
  return undefined;
}
function run(program: Instr[], stack: number[]): string {
  let pc = 0;
  for (let steps = 0; steps < 10000; steps++) {
    const ins = program[pc];
    if (ins === undefined) return "ended";
    const at = pc;
    pc++;
    switch (ins.op) {
      case "push":
        stack.push(ins.value);
        break;
      case "add":
      case "sub":
      case "mul": {
        const b = stack.pop();
        const a = stack.pop();
        if (a === undefined || b === undefined) return `underflow at ${at}`;
        stack.push(ins.op === "add" ? a + b : ins.op === "sub" ? a - b : a * b);
        break;
      }
      case "dup": {
        const top = stack.at(-1);
        if (top === undefined) return `underflow at ${at}`;
        stack.push(top);
        break;
      }
      case "swap": {
        const b = stack.pop();
        const a = stack.pop();
        if (a === undefined || b === undefined) return `underflow at ${at}`;
        stack.push(b, a);
        break;
      }
      case "print": {
        const top = stack.pop();
        if (top === undefined) return `underflow at ${at}`;
        console.log(top);
        break;
      }
      case "halt":
        return "halted";
      case "jmp":
      case "jz": {
        if (ins.op === "jz") {
          const top = stack.pop();
          if (top === undefined) return `underflow at ${at}`;
          if (top !== 0) break;
        }
        if (ins.target < 0 || ins.target >= program.length) return `bad jump at ${at}`;
        pc = ins.target;
        break;
      }
    }
  }
  return "step limit";
}
const program: Instr[] = [];
let bad = -1;
input.split("\n").forEach((line, i) => {
  const ins = parseLine(line);
  if (ins === undefined) {
    if (bad < 0) bad = i;
  } else {
    program.push(ins);
  }
});
if (bad >= 0) {
  console.log(`line ${bad}: bad instruction`);
} else {
  const stack: number[] = [];
  console.log(run(program, stack));
  console.log(`stack: ${stack.join(" ") || "empty"}`);
}
""", ["push 3\ndup\nprint\npush 1\nsub\ndup\njz 8\njmp 1\nhalt",
      "push 2\npush 5\nswap\nsub\nprint\npush 7",
      "push 1\nadd",
      "jmp 0",
      "push 1\njz 1\npush x"],
         hints=["Group the operand-free instructions into one member: `{ op: \"add\" | \"sub\" | … }`.",
                "Parse everything before running anything, so a typo on the last line stops the program before it prints."]),
    _tsp(12, "tsm-w12-markdown", "Render a little Markdown", "stretch",
         "The input is a Markdown document. Parse its lines into blocks — `heading` (`#` to `######` then a space), `list` (consecutive `- ` lines), `rule` (`---`) and `paragraph` (consecutive other non-blank lines, joined with one space); a blank line ends a list or paragraph. Render each block on its own line: `<h2>text</h2>`, `<ul><li>a</li><li>b</li></ul>`, `<hr>`, `<p>text</p>`. Finish with `blocks: <n>`. Render with an exhaustive `switch`.",
         r"""
type Block =
  | { kind: "heading"; level: number; text: string }
  | { kind: "list"; items: string[] }
  | { kind: "rule" }
  | { kind: "paragraph"; lines: string[] };
const blocks: Block[] = [];
for (const raw of input.split("\n")) {
  const line = raw.trim();
  const last = blocks.at(-1);
  const heading = /^(#{1,6}) (.+)$/.exec(line);
  if (line === "") {
    blocks.push({ kind: "paragraph", lines: [] });
  } else if (heading !== null) {
    blocks.push({ kind: "heading", level: (heading[1] ?? "#").length, text: heading[2] ?? "" });
  } else if (line === "---") {
    blocks.push({ kind: "rule" });
  } else if (line.startsWith("- ")) {
    if (last?.kind === "list") last.items.push(line.slice(2));
    else blocks.push({ kind: "list", items: [line.slice(2)] });
  } else if (last?.kind === "paragraph") {
    last.lines.push(line);
  } else {
    blocks.push({ kind: "paragraph", lines: [line] });
  }
}
function render(b: Block): string {
  switch (b.kind) {
    case "heading":
      return `<h${b.level}>${b.text}</h${b.level}>`;
    case "list":
      return `<ul>${b.items.map((item) => `<li>${item}</li>`).join("")}</ul>`;
    case "rule":
      return "<hr>";
    case "paragraph":
      return `<p>${b.lines.join(" ")}</p>`;
  }
}
const real = blocks.filter((b) => b.kind !== "paragraph" || b.lines.length > 0);
for (const b of real) console.log(render(b));
console.log(`blocks: ${real.length}`);
""", ["# Title\nSome text\nthat continues.\n\n- one\n- two\n---\n## Next\nEnd.",
      "- a\n\n- b\ntext after\n###### tiny\n####### not a heading\n#nospace"],
         hints=["A blank line pushes an empty paragraph, which ends whatever was open; drop empty paragraphs before rendering.",
                "`last?.kind === \"list\"` narrows `last` to the list member, so `last.items` is available."]),
    _tsp(12, "tsm-w12-tokens", "Tokenise an expression", "stretch",
         "Each input line is an expression. Split it into tokens — `num` (digits, optionally `.digits`), `ident` (a letter or `_`, then letters, digits or `_`), `op` (`==`, `!=`, `<=`, `>=`, then single `+ - * / = < >`), `lparen`, `rparen`, `comma` — skipping spaces. Print them space-separated as `num(12) ident(x) op(+) lparen rparen comma`; at an unexpected character print `unexpected '<c>' at <column>` (1-based) instead of the line's tokens.",
         r"""
type Token =
  | { kind: "num"; text: string }
  | { kind: "ident"; text: string }
  | { kind: "op"; text: string }
  | { kind: "lparen" }
  | { kind: "rparen" }
  | { kind: "comma" };
function tokenize(line: string): Token[] | string {
  const tokens: Token[] = [];
  let i = 0;
  while (i < line.length) {
    const rest = line.slice(i);
    const c = line.charAt(i);
    const num = /^\d+(\.\d+)?/.exec(rest);
    const ident = /^[A-Za-z_]\w*/.exec(rest);
    const op = /^(==|!=|<=|>=|[+\-*\/=<>])/.exec(rest);
    if (c === " ") {
      i++;
    } else if (num !== null) {
      tokens.push({ kind: "num", text: num[0] });
      i += num[0].length;
    } else if (ident !== null) {
      tokens.push({ kind: "ident", text: ident[0] });
      i += ident[0].length;
    } else if (op !== null) {
      tokens.push({ kind: "op", text: op[0] });
      i += op[0].length;
    } else if (c === "(" || c === ")" || c === ",") {
      tokens.push({ kind: c === "(" ? "lparen" : c === ")" ? "rparen" : "comma" });
      i++;
    } else {
      return `unexpected '${c}' at ${i + 1}`;
    }
  }
  return tokens;
}
function show(t: Token): string {
  switch (t.kind) {
    case "num":
    case "ident":
    case "op":
      return `${t.kind}(${t.text})`;
    case "lparen":
    case "rparen":
    case "comma":
      return t.kind;
  }
}
for (const line of input.split("\n")) {
  const result = tokenize(line);
  console.log(typeof result === "string" ? result : result.map(show).join(" "));
}
""", ["x1 = max(a, 12.5) * 3\nif_ok >= 10 != y\nprice * 2 @ 3", "f(g(1),2)\n3.x\n_a==_b"],
         hints=["Return `Token[] | string` and let the caller narrow with `typeof`.",
                "Grouping cases (`case \"num\": case \"ident\":`) narrows to the members that share a `text` field."]),
]

TS_PROJECTS[12] = _project(
    12, "interpreter.ts — a stack language with a checker",
    "Model a small language as a discriminated union of instructions, check the whole program before running any of it, and let an exhaustive `switch` — ending in `never` — be what forces you to handle every instruction you add.",
    ["The input is a program, one instruction per line: `push <int>`, `pop`, `add`, `sub`, `mul`, `div` (integer division, truncating toward zero), `dup`, `swap`, `print`. Blank lines and lines starting with `#` are ignored; line numbers count every line from 1.",
     "Parse every line first. For each bad line print `line <n>: unknown instruction <word>` or `line <n>: push needs an integer` (also for any extra words: `line <n>: <word> takes no argument`). If there were any, print `not run` and stop.",
     "Otherwise run it. `print` prints the top of the stack without popping. The first runtime error — `line <n>: stack underflow` or `line <n>: division by zero` — stops the program.",
     "At the end (normal or after an error) print `stack: <bottom … top>` or `stack: empty`.",
     "Represent instructions as a discriminated union and execute them with a `switch` that ends in a `never` check."],
    r"""
type Instr =
  | { op: "push"; value: number; line: number }
  | { op: "pop" | "add" | "sub" | "mul" | "div" | "dup" | "swap" | "print"; line: number };
const NO_ARG = ["pop", "add", "sub", "mul", "div", "dup", "swap", "print"] as const;
type NoArg = (typeof NO_ARG)[number];
const isNoArg = (s: string): s is NoArg => NO_ARG.some((op) => op === s);
const program: Instr[] = [];
const errors: string[] = [];
for (const [i, raw] of input.split("\n").entries()) {
  const line = i + 1;
  const text = raw.trim();
  if (text === "" || text.startsWith("#")) continue;
  const [word = "", arg, extra] = text.split(/\s+/);
  if (word === "push") {
    const n = Number(arg);
    if (arg === undefined || extra !== undefined || !Number.isInteger(n)) errors.push(`line ${line}: push needs an integer`);
    else program.push({ op: "push", value: n, line });
  } else if (isNoArg(word)) {
    if (arg !== undefined) errors.push(`line ${line}: ${word} takes no argument`);
    else program.push({ op: word, line });
  } else {
    errors.push(`line ${line}: unknown instruction ${word}`);
  }
}
const stack: number[] = [];
function run(): string | undefined {
  for (const ins of program) {
    const need = ins.op === "push" ? 0 : ins.op === "pop" || ins.op === "dup" || ins.op === "print" ? 1 : 2;
    if (stack.length < need) return `line ${ins.line}: stack underflow`;
    switch (ins.op) {
      case "push":
        stack.push(ins.value);
        break;
      case "pop":
        stack.pop();
        break;
      case "dup":
        stack.push(stack[stack.length - 1] ?? 0);
        break;
      case "print":
        console.log(stack[stack.length - 1] ?? 0);
        break;
      case "swap":
      case "add":
      case "sub":
      case "mul":
      case "div": {
        const b = stack.pop() ?? 0;
        const a = stack.pop() ?? 0;
        if (ins.op === "swap") stack.push(b, a);
        else if (ins.op === "add") stack.push(a + b);
        else if (ins.op === "sub") stack.push(a - b);
        else if (ins.op === "mul") stack.push(a * b);
        else if (b === 0) return `line ${ins.line}: division by zero`;
        else stack.push(Math.trunc(a / b));
        break;
      }
      default: {
        const unreachable: never = ins;
        return unreachable;
      }
    }
  }
  return undefined;
}
if (errors.length > 0) {
  for (const e of errors) console.log(e);
  console.log("not run");
} else {
  const failure = run();
  if (failure !== undefined) console.log(failure);
  console.log(`stack: ${stack.join(" ") || "empty"}`);
}
""", ["push 6\npush 7\nmul\nprint\npush 5\nswap\nsub\nprint",
      "# division\npush 7\npush -2\ndiv\nprint\n\npush 0\ndiv\nprint",
      "push 1\nadd\npush 9",
      "push x\nfrobnicate\npop 3\npush 1 2\npush 4",
      "push 3\ndup\ndup\nmul\nmul\nprint\npop\npop"],
    stretch=["Add `jz <line>` and `jmp <line>` instructions — the `never` check shows you every switch that must learn them.",
             "Report *all* runtime problems a static pass can find before running (like underflow on straight-line code)."],
)

TS_PRACTICE_MORE[12] = [
    _pr("tsm-w12-p2", "Pop from an empty literal", "const nothing = [].pop();\n", "nothing", "undefined",
        hints=["Under `strict`, `[]` on its own is `never[]`.", "`pop` returns the element type or `undefined` — and `never | undefined` is `undefined`."]),
    _dx("tsm-w12-d2", "A light nobody handled",
        "error TS2322: Type '\"amber\"' is not assignable to type 'never'.",
        'type Light = "red" | "green" | "amber";\nfunction next(l: Light): Light {\n  switch (l) {\n    case "red":\n      return "green";\n    case "green":\n      return "amber";\n    default: {\n      const unreachable: never = l;\n      return unreachable;\n    }\n  }\n}\nconsole.log(next("amber"));\n',
        'type Light = "red" | "green" | "amber";\nfunction next(l: Light): Light {\n  switch (l) {\n    case "red":\n      return "green";\n    case "green":\n      return "amber";\n    case "amber":\n      return "red";\n    default: {\n      const unreachable: never = l;\n      return unreachable;\n    }\n  }\n}\nconsole.log(next("amber"));\n',
        [("", "red")], ask="After amber comes red. Keep the exhaustiveness check.",
        hints=["The check is doing its job: one member reaches `default`.", "Add the missing `case`."]),
    _fx("tsm-w12-f2", "Zero read as a failure",
        "Print each parsed value, or the error for a bad token. A value of 0 prints `error`.",
        _STDIN + 'type Result = { ok: true; value: number } | { ok: false; error: string };\nfunction parse(t: string): Result {\n  const n = Number(t);\n  return Number.isInteger(n) ? { ok: true, value: n } : { ok: false, error: `bad ${t}` };\n}\nfor (const t of input.split(" ")) {\n  const r = parse(t);\n  console.log("value" in r && r.value ? r.value : "error");\n}\n',
        _STDIN + 'type Result = { ok: true; value: number } | { ok: false; error: string };\nfunction parse(t: string): Result {\n  const n = Number(t);\n  return Number.isInteger(n) ? { ok: true, value: n } : { ok: false, error: `bad ${t}` };\n}\nfor (const t of input.split(" ")) {\n  const r = parse(t);\n  console.log(r.ok ? r.value : r.error);\n}\n',
        [("5 0 x", "5\n0\nbad x"), ("0", "0")],
        hints=["The tag is `ok` — narrow on it, not on the payload's truthiness.", "`r.ok ? r.value : r.error`."], difficulty="Medium"),
]

TS_CARDS_MORE[12] = [
    ("Which type holds every value but allows nothing until you narrow it?", "`unknown`, the safe top type."),
    ("`string | never` simplifies to?", "`string` — `never` is the empty union and disappears from any union."),
    ("What does the type `{}` accept?", "Every value except `null` and `undefined` — including `0` and `\"\"`."),
    ("`object` vs `Object`?", "`object` is any non-primitive; `Object` (capital) accepts nearly everything, primitives included — avoid it."),
    ("A function whose return type is `never`?", "It never returns normally: it always throws, or loops forever."),
    ("`value satisfies never` in a `default:` branch?", "An exhaustiveness check without a throwaway variable: it fails to compile when a member reaches the default."),
]

# ===========================================================================
# Week 13 — Function types, type tests, checkpoint
# ===========================================================================

TS_PROBLEM_SETS[13] = [
    _tsp(13, "tsm-w13-dispatch", "A command table", "warm-up",
         "Each input line is `<command> <args…>`. Keep a `Record<string, Command>` where `type Command = (args: string[]) => string`, with `upper` (args joined by spaces, upper-cased), `count` (how many args), `reverse` (args in reverse order) and `sum` (args as numbers). `help` prints the command names, sorted. Anything else prints `unknown command <name>`.",
         r"""
type Command = (args: string[]) => string;
const commands: Record<string, Command> = {
  upper: (args) => args.join(" ").toUpperCase(),
  count: (args) => String(args.length),
  reverse: (args) => [...args].reverse().join(" "),
  sum: (args) => String(args.map(Number).reduce((a, b) => a + b, 0)),
};
for (const line of input.split("\n")) {
  const [name = "", ...args] = line.trim().split(/\s+/);
  if (name === "help") {
    console.log(Object.keys(commands).sort().join(" "));
    continue;
  }
  const run = Object.hasOwn(commands, name) ? commands[name] : undefined;
  console.log(run === undefined ? `unknown command ${name}` : run(args));
}
""", ["upper hello there\ncount a b c\nreverse 1 2 3\nsum 4 5 6\nhelp\ndance", "count\ntoString x\nsum -1 1"],
         hints=["Each table entry only needs to fit the `Command` signature.",
                "`Object.hasOwn` keeps `toString` from being treated as a command."]),
    _tsp(13, "tsm-w13-stats", "Three results in one tuple", "warm-up",
         "Each input line is a list of numbers. Write `stats(xs): [min: number, max: number, mean: number]` and destructure its result to print `min <a> max <b> mean <c> range <d>`, with the mean rounded to at most 2 decimals.",
         r"""
function stats(xs: readonly number[]): [min: number, max: number, mean: number] {
  let min = Infinity;
  let max = -Infinity;
  let sum = 0;
  for (const x of xs) {
    min = Math.min(min, x);
    max = Math.max(max, x);
    sum += x;
  }
  return [min, max, sum / xs.length];
}
for (const line of input.split("\n")) {
  const [min, max, mean] = stats(line.trim().split(/\s+/).map(Number));
  console.log(`min ${min} max ${max} mean ${Number(mean.toFixed(2))} range ${max - min}`);
}
""", ["3 1 4 1 5", "10\n-2 2", "0.5 0.25 1"],
         hints=["A labelled tuple documents what each position means, and destructuring reads it back by position."]),
    _tsp(13, "tsm-w13-variadic", "Rest parameters", "warm-up",
         "Each input line is `sum <n…>`, `join <sep> <word…>` or `longest <word…>`. Implement them as `sum(...xs: number[])`, `joinWith(sep: string, ...parts: string[])` and `longest(first: string, ...rest: string[])` (the first longest word). `longest` with no words prints `longest needs a word`; anything else prints `unknown <op>`.",
         r"""
function sum(...xs: number[]): number {
  return xs.reduce((a, b) => a + b, 0);
}
function joinWith(separator: string, ...parts: string[]): string {
  return parts.join(separator);
}
function longest(first: string, ...rest: string[]): string {
  return rest.reduce((best, s) => (s.length > best.length ? s : best), first);
}
for (const line of input.split("\n")) {
  const [op = "", ...args] = line.trim().split(/\s+/);
  if (op === "sum") {
    console.log(sum(...args.map(Number)));
  } else if (op === "join") {
    const [sep = "", ...words] = args;
    console.log(joinWith(sep, ...words));
  } else if (op === "longest") {
    const [first, ...rest] = args;
    console.log(first === undefined ? "longest needs a word" : longest(first, ...rest));
  } else {
    console.log(`unknown ${op}`);
  }
}
""", ["sum 1 2 3\njoin - a b c\nlongest hi hello hey\nlongest", "sum 5\njoin :: x\nlongest ab cd\nmax 1 2"],
         hints=["`longest(first, ...rest)` makes \"at least one word\" part of the signature.",
                "Spread an array into a rest parameter with `...`."]),
    _tsp(13, "tsm-w13-overloads", "One parser, three return types", "core",
         "Each input line is `number <text>`, `list <a,b,c>` or `bool <text>`. Write an overloaded `parse` whose return type follows its second argument — `parse(text, \"number\"): number`, `parse(text, \"list\"): number[]`, `parse(text, \"bool\"): boolean` (true for `true`, `yes`, `1` in any case). Print `number <n>, doubled <2n>`, `list of <k>, sum <s>`, `bool <b>, negated <!b>`, or `unknown kind <k>`.",
         r"""
function parse(text: string, as: "number"): number;
function parse(text: string, as: "list"): number[];
function parse(text: string, as: "bool"): boolean;
function parse(text: string, as: "number" | "list" | "bool"): number | number[] | boolean {
  if (as === "number") return Number(text);
  if (as === "list") return text === "" ? [] : text.split(",").map(Number);
  return ["true", "yes", "1"].includes(text.toLowerCase());
}
for (const line of input.split("\n")) {
  const [kind = "", text = ""] = line.trim().split(/\s+/);
  if (kind === "number") {
    const n = parse(text, "number");
    console.log(`number ${n}, doubled ${n * 2}`);
  } else if (kind === "list") {
    const xs = parse(text, "list");
    console.log(`list of ${xs.length}, sum ${xs.reduce((a, b) => a + b, 0)}`);
  } else if (kind === "bool") {
    const b = parse(text, "bool");
    console.log(`bool ${b}, negated ${!b}`);
  } else {
    console.log(`unknown kind ${kind}`);
  }
}
""", ["number 21\nlist 1,2,3\nbool YES\nbool no", "list 7\nnumber -0.5\ndate 2024"],
         hints=["Write the overload signatures first, then one implementation signature that covers all of them.",
                "Callers only see the overloads, so `parse(text, \"list\")` is a `number[]` with no narrowing."]),
    _tsp(13, "tsm-w13-registry", "A callback registry", "core",
         "Commands, one per line: `on <event> <handler>` registers a handler and prints its id (`#1`, `#2`, …), `off <id>` prints `removed #<id>` or `no #<id>`, and `emit <event> <payload…>` runs that event's handlers in registration order, printing each result — or `no listeners for <event>`. Handlers are made by name: `echo` (the payload), `shout` (upper-case plus `!`), `count` (how many times *this* registration has run, as `call <n>`) and `len` (the payload's length). An unknown handler name prints `unknown handler <name>`.",
         r"""
type Handler = (payload: string) => string;
const factories: Record<string, () => Handler> = {
  echo: () => (payload) => payload,
  shout: () => (payload) => payload.toUpperCase() + "!",
  count: () => {
    let calls = 0;
    return () => `call ${++calls}`;
  },
  len: () => (payload) => String(payload.length),
};
const registry = new Map<number, { event: string; handler: Handler }>();
let nextId = 1;
for (const line of input.split("\n")) {
  const [cmd = "", a = "", ...rest] = line.trim().split(/\s+/);
  if (cmd === "on") {
    const name = rest[0] ?? "";
    const make = Object.hasOwn(factories, name) ? factories[name] : undefined;
    if (make === undefined) {
      console.log(`unknown handler ${name}`);
      continue;
    }
    registry.set(nextId, { event: a, handler: make() });
    console.log(`#${nextId++}`);
  } else if (cmd === "off") {
    const id = Number(a.replace("#", ""));
    console.log(registry.delete(id) ? `removed #${id}` : `no #${id}`);
  } else if (cmd === "emit") {
    const listeners = [...registry.values()].filter((r) => r.event === a);
    if (listeners.length === 0) console.log(`no listeners for ${a}`);
    for (const { handler } of listeners) console.log(handler(rest.join(" ")));
  }
}
""", ["on greet echo\non greet shout\non greet count\nemit greet hi there\nemit greet again\noff 2\nemit greet bye\nemit other x",
      "on a len\non a nope\noff #1\noff 1\nemit a hello\non a count\non a count\nemit a x"],
         hints=["A factory returning a fresh closure gives each registration its own `count` state.",
                "A `Map` iterates in insertion order — registration order for free."]),
    _tsp(13, "tsm-w13-partial", "Fix the first argument", "core",
         "Each input line is `<op> <a> [then <op> <a>]… | <values…>`, with ops `add`, `sub`, `mul`, `pow`, `max`. Each `<op> <a>` becomes a one-argument function by fixing the operator's *first* argument (`sub 10` is `b => 10 - b`); chain them left to right with `then`, and apply the chain to every value. Print the results space-separated, or `unknown op <op>`. Use `bindFirst(f: Binary, a: number): Unary` and `compose(f: Unary, g: Unary): Unary`.",
         r"""
type Binary = (a: number, b: number) => number;
type Unary = (b: number) => number;
const OPS: Record<string, Binary> = {
  add: (a, b) => a + b,
  sub: (a, b) => a - b,
  mul: (a, b) => a * b,
  pow: Math.pow,
  max: Math.max,
};
function bindFirst(f: Binary, a: number): Unary {
  return (b) => f(a, b);
}
function compose(f: Unary, g: Unary): Unary {
  return (x) => g(f(x));
}
for (const line of input.split("\n")) {
  const [chain = "", values = ""] = line.split("|");
  let pipeline: Unary = (x) => x;
  let error = "";
  for (const stage of chain.trim().split(/\s+then\s+/)) {
    const [name = "", a = "0"] = stage.trim().split(/\s+/);
    const op = Object.hasOwn(OPS, name) ? OPS[name] : undefined;
    if (op === undefined) {
      error = `unknown op ${name}`;
      break;
    }
    pipeline = compose(pipeline, bindFirst(op, Number(a)));
  }
  console.log(error || values.trim().split(/\s+/).map((v) => pipeline(Number(v))).join(" "));
}
""", ["add 5 | 1 2 3\nsub 10 | 1 2 3\nadd 1 then mul 2 | 0 1 2\npow 2 | 0 3 10", "max 4 then sub 0 | 1 9\nmod 3 | 1"],
         hints=["`Math.pow` and `Math.max` already fit `Binary`.",
                "Start the pipeline with the identity function and compose each stage onto it."]),
    _tsp(13, "tsm-w13-handlers", "Handlers with different signatures", "stretch",
         "Handlers have different parameter lists: `click(x, y)`, `key(key, shift)` and `scroll(dy)`, typed as one `Handlers` object type. Each input line is an event (`click 3 4`, `key a shift`, `key b`, `scroll -5`). Parse the arguments for that event, call the right handler with correctly typed arguments, and print its result: `click at 3,4`, `key A` (upper-case when `shift`) / `key b`, `scroll up 5` / `scroll down 2`. Bad arguments print `bad args for <event>`, unknown events `unknown event <e>`. Finish with the number of handled events per kind: `click=<a> key=<b> scroll=<c>`.",
         r"""
type Handlers = {
  click: (x: number, y: number) => string;
  key: (key: string, shift: boolean) => string;
  scroll: (dy: number) => string;
};
const handlers: Handlers = {
  click: (x, y) => `click at ${x},${y}`,
  key: (key, shift) => `key ${shift ? key.toUpperCase() : key}`,
  scroll: (dy) => (dy < 0 ? `scroll up ${-dy}` : `scroll down ${dy}`),
};
const handled: Record<keyof Handlers, number> = { click: 0, key: 0, scroll: 0 };
const isInt = (s: string | undefined): s is string => s !== undefined && /^-?\d+$/.test(s);
function dispatch(name: string, args: string[]): string {
  const [a, b] = args;
  switch (name) {
    case "click":
      if (!isInt(a) || !isInt(b) || args.length !== 2) return "bad args for click";
      handled.click++;
      return handlers.click(Number(a), Number(b));
    case "key":
      if (a === undefined || a.length !== 1 || (b !== undefined && b !== "shift")) return "bad args for key";
      handled.key++;
      return handlers.key(a, b === "shift");
    case "scroll":
      if (!isInt(a) || args.length !== 1) return "bad args for scroll";
      handled.scroll++;
      return handlers.scroll(Number(a));
    default:
      return `unknown event ${name}`;
  }
}
for (const line of input.split("\n")) {
  const [name = "", ...args] = line.trim().split(/\s+/);
  console.log(dispatch(name, args));
}
console.log(`click=${handled.click} key=${handled.key} scroll=${handled.scroll}`);
""", ["click 3 4\nkey a shift\nkey b\nscroll -5\nscroll 2\nhover 1", "click 1\nkey ab\nkey x ctrl\nscroll 1.5\nclick 0 0"],
         hints=["Validate the strings first, then call with the converted, correctly typed values — each handler's parameters are checked.",
                "`keyof Handlers` gives the event names for the counts object."]),
    _tsp_types(13, "tsm-w13-middleware-type", "Type the middleware slot", "core",
               "`auth` and `log` are middleware: they take a request and a `next` function that produces the response, and return the response. Write the `Middleware` function type so both fit — and so a middleware that forgets to return is rejected.",
               '''
type HttpRequest = { path: string; user?: string };
type Middleware = (req: HttpRequest, next: () => string) => string;

const auth: Middleware = (req, next) => (req.user === undefined ? "401" : next());
const log: Middleware = (req, next) => req.path + " -> " + next();
console.log(log({ path: "/a", user: "ana" }, () => auth({ path: "/a", user: "ana" }, () => "200")));
''', "(req: HttpRequest, next: () => string) => string",
               '''
type _1 = Expect<Equal<Parameters<Middleware>, [req: HttpRequest, next: () => string]>>;
type _2 = Expect<Equal<ReturnType<Middleware>, string>>;
function _typeTests() {
  // @ts-expect-error — a middleware must return the response
  const forgetful: Middleware = (req, next) => {
    next();
  };
}
''', hints=["It is a function type: two parameters and a return type.",
            "`next` itself is a function that takes nothing and returns a `string`."]),
    _tsp_types(13, "tsm-w13-plugin-ctor", "A slot for a class", "stretch",
               "`load` receives a plugin *class* and creates it with `new`. Write `PluginClass`, the type of anything that can be constructed from a config string into a `Plugin`.",
               '''
interface Plugin {
  name: string;
  run(input: string): string;
}
type PluginClass = new (config: string) => Plugin;

class Upper implements Plugin {
  name: string;
  constructor(config: string) {
    this.name = "upper:" + config;
  }
  run(input: string): string {
    return input.toUpperCase();
  }
}
function load(cls: PluginClass, config: string): Plugin {
  return new cls(config);
}
console.log(load(Upper, "x").run("hi"));
''', "new (config: string) => Plugin",
               '''
type _1 = Expect<Equal<InstanceType<PluginClass>, Plugin>>;
type _2 = Expect<Equal<ConstructorParameters<PluginClass>, [config: string]>>;
function _typeTests() {
  // @ts-expect-error — a plain function is not a class
  load((config: string) => ({ name: config, run: (s: string) => s }), "x");
}
''', hints=["A construct signature starts with `new`.", "`new (config: string) => Plugin`."]),
]

TS_PROJECTS[13] = _project(
    13, "config.ts — the config reader, from scratch",
    "Rebuild the Week 8 config reader without looking at it, the way you would now: every input line is untrusted, every value is validated against a schema, every problem is reported with its line number, and the parsed result has an exact type. (Stretch: pin that type down with `Expect<Equal<…>>` tests.)",
    ["The input is an INI-style file: `key = value` lines, `[section]` headers, blank lines and `#` comments. Line numbers count every line from 1.",
     "Top-level keys: `name` (required, non-empty), `port` (integer 1-65535, default 3000), `debug` (`yes/no/true/false/on/off`, default `false`), `tags` (comma-separated, trimmed, empty items dropped; default none). A `[db]` section may set `host` (required when the section appears) and `port` (default 5432).",
     "Report, sorted by line: `line <n>: expected key = value`, `line <n>: unknown section [<s>]` (its keys are then skipped), `line <n>: unknown key <k>`, `line <n>: duplicate key <k>`, `line <n>: port must be an integer from 1 to 65535`, `line <n>: debug must be yes or no`. Then the missing ones, unnumbered: `name is required`, `db.host is required`.",
     "With any problem, print them all and then `invalid config (<k> problems)` (`problem` when there is one).",
     "Otherwise print `name: <n>`, `port: <p>`, `debug: <true|false>`, `tags: <a, b>` or `tags: (none)`, and `db: <host>:<port>` or `db: (none)`."],
    r"""
type Entry = { value: string; line: number };
type Problem = { line: number; message: string };
const problems: Problem[] = [];
const top = new Map<string, Entry>();
const db = new Map<string, Entry>();
let section: "top" | "db" | "skip" = "top";
let sawDb = false;
const ALLOWED = { top: ["name", "port", "debug", "tags"], db: ["host", "port"] };
for (const [i, raw] of input.split("\n").entries()) {
  const line = i + 1;
  const text = raw.trim();
  if (text === "" || text.startsWith("#")) continue;
  const header = /^\[(.*)\]$/.exec(text);
  if (header !== null) {
    const name = (header[1] ?? "").trim();
    if (name === "db") {
      section = "db";
      sawDb = true;
    } else {
      section = "skip";
      problems.push({ line, message: `unknown section [${name}]` });
    }
    continue;
  }
  const eq = text.indexOf("=");
  if (eq <= 0) {
    problems.push({ line, message: "expected key = value" });
    continue;
  }
  if (section === "skip") continue;
  const key = text.slice(0, eq).trim();
  const target = section === "db" ? db : top;
  if (!ALLOWED[section].includes(key)) problems.push({ line, message: `unknown key ${key}` });
  else if (target.has(key)) problems.push({ line, message: `duplicate key ${key}` });
  else target.set(key, { value: text.slice(eq + 1).trim(), line });
}
function port(entry: Entry | undefined, fallback: number): number {
  if (entry === undefined) return fallback;
  const p = Number(entry.value);
  if (/^\d+$/.test(entry.value) && p >= 1 && p <= 65535) return p;
  problems.push({ line: entry.line, message: "port must be an integer from 1 to 65535" });
  return fallback;
}
function flag(entry: Entry | undefined): boolean {
  if (entry === undefined) return false;
  const v = entry.value.toLowerCase();
  if (["yes", "true", "on"].includes(v)) return true;
  if (!["no", "false", "off"].includes(v)) problems.push({ line: entry.line, message: "debug must be yes or no" });
  return false;
}
type Config = { name: string; port: number; debug: boolean; tags: string[]; db?: { host: string; port: number } };
const config: Config = {
  name: top.get("name")?.value ?? "",
  port: port(top.get("port"), 3000),
  debug: flag(top.get("debug")),
  tags: (top.get("tags")?.value ?? "").split(",").map((t) => t.trim()).filter((t) => t !== ""),
};
const dbPort = port(db.get("port"), 5432);
const host = db.get("host")?.value ?? "";
if (sawDb && host !== "") config.db = { host, port: dbPort };
problems.sort((a, b) => a.line - b.line);
const missing: string[] = [];
if (config.name === "") missing.push("name is required");
if (sawDb && host === "") missing.push("db.host is required");
const all = [...problems.map((p) => `line ${p.line}: ${p.message}`), ...missing];
if (all.length > 0) {
  for (const p of all) console.log(p);
  console.log(`invalid config (${all.length} ${all.length === 1 ? "problem" : "problems"})`);
} else {
  console.log(`name: ${config.name}`);
  console.log(`port: ${config.port}`);
  console.log(`debug: ${config.debug}`);
  console.log(`tags: ${config.tags.join(", ") || "(none)"}`);
  console.log(`db: ${config.db === undefined ? "(none)" : `${config.db.host}:${config.db.port}`}`);
}
""", ["# app\nname = poodcode\nport = 8080\ndebug = YES\ntags = web, , cli\n[db]\nhost = localhost",
      "name = svc\n[db]\nhost = db.local\nport = 6543",
      "port = 99999\ndebug = maybe\nname\n[cache]\nsize = 3\n[db]\nport = 1\nuser = x",
      "name = a\nname = b\nport = 80",
      "name = tiny"],
    stretch=["Add type tests: `Expect<Equal<Config[\"db\"], { host: string; port: number } | undefined>>`, and a `@ts-expect-error` line assigning a string to `port`.",
             "Make the schema data (key → validator) so adding a key is one line."],
)

TS_PRACTICE_MORE[13] = [
    _pr("tsm-w13-p2", "A default parameter in a signature",
        "const pad = (text: string, width = 8) => text.padStart(width);\n", "pad", "(text: string, width?: number) => string",
        hints=["A parameter with a default is optional to the caller.", "Its type is inferred from the default."]),
    _dx("tsm-w13-d1", "Called without its `this`",
        "error TS2684: The 'this' context of type 'void' is not assignable to method's 'this' of type 'Account'.",
        'interface Account {\n  owner: string;\n}\nfunction greet(this: Account): string {\n  return "hi " + this.owner;\n}\nconsole.log(greet());\n',
        'interface Account {\n  owner: string;\n}\nfunction greet(this: Account): string {\n  return "hi " + this.owner;\n}\nconsole.log(greet.call({ owner: "Ana" }));\n',
        [("", "hi Ana")], ask="Greet the account owned by Ana.",
        hints=["`greet` needs an `Account` as `this`.", "Supply one with `.call`."]),
    _dx("tsm-w13-d2", "A negative test that never failed",
        "error TS2578: Unused '@ts-expect-error' directive.",
        'function setPort(port: number | string): number {\n  return Number(port);\n}\nfunction _typeTests() {\n  // @ts-expect-error — a port must be a number\n  setPort("8080");\n}\nconsole.log(setPort(8080));\n',
        'function setPort(port: number): number {\n  return port;\n}\nfunction _typeTests() {\n  // @ts-expect-error — a port must be a number\n  setPort("8080");\n}\nconsole.log(setPort(8080));\n',
        [("", "8080")], ask="The test is right — a port must be a number. Fix `setPort`, not the test.",
        hints=["The directive expects the next line to be an error, and it isn't.", "Narrow the parameter type."], difficulty="Medium"),
]

TS_CARDS_MORE[13] = [
    ("Is `(x: number) => void` assignable to `(x: number, i: number) => void`?", "Yes — a function taking fewer parameters can always be called with more; the extras are ignored."),
    ("What is a construct signature?", "`new (args) => T`: the type of something you call with `new`, such as a class value."),
    ("What does a `this` parameter compile to?", "Nothing — it's erased, but every call is checked for the right `this`."),
    ("How do you write a type test for a misuse?", "Put `// @ts-expect-error` on the line above it; if the line compiles, the unused directive is itself an error (TS2578)."),
    ("Why pair type tests with runtime tests?", "Type tests prove shapes, not values — a correctly typed function can still return the wrong number."),
    ("What is `typeof fn<string>`?", "An instantiation expression: the generic function's type with `T` fixed to `string`."),
]

