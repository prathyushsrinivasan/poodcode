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
  const [next, message] = table[current][token as Command];
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
