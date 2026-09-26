# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — the programme's final exam (TS_MASTERY_ROADMAP X-36).
#
# Opens once all 26 core weeks are complete. One timed sitting of 3 hours:
#   * 40 quiz questions drawn by the app from every week's bank,
#   * 5 coding problems, each drawing on a different stretch of the programme,
#   * a 5-puzzle type-challenge section.
# Passing it is recorded on the completion summary (X-68).
#
# Problems and puzzles are ordinary exercises (judged exactly like a problem
# set), so tests/verify_mastery.rs proves every reference and that every
# starter fails. exec()'d before mastery_ts_attach.py, which attaches it to the
# TypeScript track.
# ---------------------------------------------------------------------------

_FX = 26  # the exam runs at the strictness of the programme's end


TS_FINAL_EXAM = {
    "title": "TypeScript Mastery — final exam",
    "minutes": 180,
    "intro": (
        "Three hours, one sitting: 40 questions from across all 26 weeks, five coding problems — one "
        "for each stretch of the programme — and five type puzzles. You pass with 70% on the questions, "
        "three of the five problems and three of the five puzzles. Everything is checked with `strict` "
        "and `noUncheckedIndexedAccess`, like the last months of the programme."
    ),
    "quiz_size": 40,
    "pass_mark": 70,
    "min_problems": 3,
    "min_types": 3,
    "problems": [
        _tsp(_FX, "tsm-exam-receipt", "Months 1–2: a receipt", "core",
             "The input is `n` then `n` lines `name qty cents` — a whole positive quantity and a whole "
             "non-negative unit price in cents. Print one line per valid item, `<name padded to the longest "
             "valid name> x<qty> <line total>`, where money prints as `$D.CC`; a line that does not parse "
             "prints `skipped line <k>` (k counts from 1) in its place. Finish with `total <money>`.",
             r'''
function money(cents: number): string {
  return "$" + Math.floor(cents / 100) + "." + String(cents % 100).padStart(2, "0");
}
type Item = { name: string; qty: number; cents: number };
function parseItem(line: string): Item | null {
  const [name, qtyText, centsText, ...extra] = line.trim().split(/\s+/);
  if (name === undefined || qtyText === undefined || centsText === undefined || extra.length > 0) return null;
  const qty = Number(qtyText);
  const cents = Number(centsText);
  if (!Number.isInteger(qty) || qty <= 0 || !Number.isInteger(cents) || cents < 0) return null;
  return { name, qty, cents };
}
const lines = input.split("\n");
const n = Number(lines[0]);
const parsed: (Item | null)[] = [];
for (let i = 1; i <= n; i++) parsed.push(parseItem(lines[i] ?? ""));
const width = Math.max(0, ...parsed.map((p) => (p === null ? 0 : p.name.length)));
let total = 0;
parsed.forEach((item, k) => {
  if (item === null) {
    console.log(`skipped line ${k + 1}`);
    return;
  }
  const line = item.qty * item.cents;
  total += line;
  console.log(`${item.name.padEnd(width)} x${item.qty} ${money(line)}`);
});
console.log(`total ${money(total)}`);
''', ["3\ntea 2 250\ncoffee 1 399\nbiscuits 3 120",
      "2\nbread 1 0\nwater x 100",
      "1\nsingle 10 5",
      "3\na 1 1\nbb 2 2\nccc 3 3",
      "2\nbad 1\nworse -1 5",
      "4\nmilk 2 99\nmilk 1 99\neggs 12 25\nfree 1 0",
      "1\nextra 1 2 3",
      "2\npen 3 1.5\npad 1 150"],
             hints=["Parse every line into `Item | null` first — the padding width depends on the valid names only.",
                    "`padEnd` pads the name; `padStart(2, \"0\")` pads the cents."]),

        _tsp(_FX, "tsm-exam-orders", "Month 3: an order state machine", "core",
             "Orders move `placed → paid → shipped`, and can be `cancelled` from `placed` or `paid`. The "
             "input is `n` then `n` commands `place <id>`, `pay <id>`, `ship <id>` or `cancel <id>`. Model the "
             "commands as a discriminated union. Print `ok <id> <state>` for an allowed command, "
             "`invalid <id> <command> from <state>` for one the state does not allow (including placing an id "
             "that exists), `unknown <id>` for an id never placed, and `bad command` for anything else. "
             "Finish with `placed=<a> paid=<b> shipped=<c> cancelled=<d>`.",
             r'''
type OrderState = "placed" | "paid" | "shipped" | "cancelled";
type Command =
  | { kind: "place"; id: string }
  | { kind: "pay"; id: string }
  | { kind: "ship"; id: string }
  | { kind: "cancel"; id: string };
function parse(line: string): Command | null {
  const [kind, id, ...extra] = line.trim().split(/\s+/);
  if (id === undefined || extra.length > 0) return null;
  if (kind === "place" || kind === "pay" || kind === "ship" || kind === "cancel") return { kind, id };
  return null;
}
function next(state: OrderState, cmd: Command): OrderState | null {
  switch (cmd.kind) {
    case "place":
      return null;
    case "pay":
      return state === "placed" ? "paid" : null;
    case "ship":
      return state === "paid" ? "shipped" : null;
    case "cancel":
      return state === "placed" || state === "paid" ? "cancelled" : null;
  }
}
const lines = input.split("\n");
const n = Number(lines[0]);
const orders = new Map<string, OrderState>();
for (let i = 1; i <= n; i++) {
  const cmd = parse(lines[i] ?? "");
  if (cmd === null) {
    console.log("bad command");
    continue;
  }
  const state = orders.get(cmd.id);
  if (state === undefined) {
    if (cmd.kind === "place") {
      orders.set(cmd.id, "placed");
      console.log(`ok ${cmd.id} placed`);
    } else {
      console.log(`unknown ${cmd.id}`);
    }
    continue;
  }
  const to = next(state, cmd);
  if (to === null) {
    console.log(`invalid ${cmd.id} ${cmd.kind} from ${state}`);
  } else {
    orders.set(cmd.id, to);
    console.log(`ok ${cmd.id} ${to}`);
  }
}
const counts: Record<OrderState, number> = { placed: 0, paid: 0, shipped: 0, cancelled: 0 };
for (const state of orders.values()) counts[state]++;
console.log(`placed=${counts.placed} paid=${counts.paid} shipped=${counts.shipped} cancelled=${counts.cancelled}`);
''', ["4\nplace a\npay a\nship a\ncancel a",
      "3\npay x\nplace x\nplace x",
      "5\nplace a\nplace b\ncancel a\npay b\ncancel b",
      "2\nrefund a\nplace",
      "4\nplace q\nship q\npay q\nship q",
      "1\nplace solo",
      "6\nplace a\nplace b\nplace c\npay a\npay b\nship a",
      "3\nplace z\ncancel z\npay z"],
             hints=["Parse each line into `Command | null`; the transition function switches on `kind`.",
                    "`Record<OrderState, number>` makes the final counts exhaustive."]),

        _tsp(_FX, "tsm-exam-departments", "Months 4–5: summarise by department", "core",
             "The input is `n` then `n` lines `dept|name|salary`. Write generic `groupBy` and `maxBy` helpers. "
             "Print, for each department in alphabetical order, `<dept>: n=<count> total=<sum> top=<name>` "
             "(the top earner, ties to the alphabetically first name); then `overall top=<name> (<salary>)` "
             "with the same tie rule — or `overall top=none` for no rows.",
             r'''
type Row = { dept: string; name: string; salary: number };
function groupBy<T, K>(items: readonly T[], keyOf: (item: T) => K): Map<K, T[]> {
  const out = new Map<K, T[]>();
  for (const item of items) {
    const key = keyOf(item);
    const bucket = out.get(key);
    if (bucket === undefined) out.set(key, [item]);
    else bucket.push(item);
  }
  return out;
}
function maxBy<T>(items: readonly T[], better: (a: T, b: T) => boolean): T | undefined {
  let best: T | undefined;
  for (const item of items) if (best === undefined || better(item, best)) best = item;
  return best;
}
const higher = (a: Row, b: Row): boolean =>
  a.salary > b.salary || (a.salary === b.salary && a.name < b.name);
const lines = input.split("\n");
const n = Number(lines[0]);
const rows: Row[] = [];
for (let i = 1; i <= n; i++) {
  const [dept = "", name = "", salary = "0"] = (lines[i] ?? "").trim().split("|");
  rows.push({ dept, name, salary: Number(salary) });
}
const groups = groupBy(rows, (r) => r.dept);
for (const dept of [...groups.keys()].sort()) {
  const members = groups.get(dept) ?? [];
  const total = members.reduce((sum, r) => sum + r.salary, 0);
  console.log(`${dept}: n=${members.length} total=${total} top=${maxBy(members, higher)?.name ?? "none"}`);
}
const top = maxBy(rows, higher);
console.log(top === undefined ? "overall top=none" : `overall top=${top.name} (${top.salary})`);
''', ["3\neng|ada|100\neng|alan|90\nops|grace|95",
      "0",
      "2\nhr|bo|50\nhr|al|50",
      "4\nb|x|1\na|y|2\nb|z|3\na|w|2",
      "1\nsolo|me|10",
      "3\nops|q|70\nops|r|80\neng|s|80",
      "5\nx|a|5\ny|b|4\nz|c|3\nx|d|6\ny|e|4",
      "2\nsales|zed|0\nsales|amy|0"],
             hints=["`groupBy` returns a `Map<K, T[]>`; `maxBy` returns `T | undefined` because the input may be empty.",
                    "Pass the tie rule into `maxBy` as a comparison function."]),

        _tsp(_FX, "tsm-exam-statement", "Month 6: import a bank statement", "core",
             "The first line is the header `date,amount,memo`; every later line is a transaction. Parse each "
             "into a `Result` and collect every error — `line <k>: wrong field count`, `bad date` (not "
             "`YYYY-MM-DD` with month 01-12 and day 01-31), `bad amount` (an optional `-`, digits, and at most "
             "two decimals) or `empty memo` — where k is the line number in the file. Print the errors in "
             "order, then `imported <count>`, the balance as `balance <money>` (money as `$D.CC` or "
             "`-$D.CC`, computed in cents), and `largest debit <memo> <money>` for the most negative amount "
             "(first wins on a tie) or `largest debit none`.",
             r'''
type Result<T> = { ok: true; value: T } | { ok: false; error: string };
type Txn = { date: string; cents: number; memo: string };
function parseCents(text: string): number | null {
  const m = /^(-?)(\d+)(?:\.(\d{1,2}))?$/.exec(text);
  if (m === null) return null;
  const whole = Number(m[2] ?? "0");
  const frac = Number((m[3] ?? "").padEnd(2, "0"));
  const cents = whole * 100 + frac;
  return m[1] === "-" ? -cents : cents;
}
function parseLine(line: string): Result<Txn> {
  const fields = line.split(",");
  if (fields.length !== 3) return { ok: false, error: "wrong field count" };
  const [date = "", amount = "", memo = ""] = fields.map((f) => f.trim());
  const d = /^\d{4}-(\d{2})-(\d{2})$/.exec(date);
  const month = Number(d?.[1] ?? "0");
  const day = Number(d?.[2] ?? "0");
  if (d === null || month < 1 || month > 12 || day < 1 || day > 31) return { ok: false, error: "bad date" };
  const cents = parseCents(amount);
  if (cents === null) return { ok: false, error: "bad amount" };
  if (memo === "") return { ok: false, error: "empty memo" };
  return { ok: true, value: { date, cents, memo } };
}
function money(cents: number): string {
  const abs = Math.abs(cents);
  return (cents < 0 ? "-$" : "$") + Math.floor(abs / 100) + "." + String(abs % 100).padStart(2, "0");
}
const lines = input.split("\n").slice(1);
const imported: Txn[] = [];
lines.forEach((line, i) => {
  const r = parseLine(line);
  if (r.ok) imported.push(r.value);
  else console.log(`line ${i + 2}: ${r.error}`);
});
const balance = imported.reduce((sum, t) => sum + t.cents, 0);
let debit: Txn | undefined;
for (const t of imported) if (t.cents < 0 && (debit === undefined || t.cents < debit.cents)) debit = t;
console.log(`imported ${imported.length}`);
console.log(`balance ${money(balance)}`);
console.log(debit === undefined ? "largest debit none" : `largest debit ${debit.memo} ${money(debit.cents)}`);
''', ["date,amount,memo\n2026-01-05,1200.00,salary\n2026-01-06,-45.5,groceries\n2026-01-07,-300,rent",
      "date,amount,memo\n2026-13-01,5,x\n2026-02-30,5,y",
      "date,amount,memo\n2026-03-01,1.234,z\n2026-03-02,abc,w\n2026-03-03,7,",
      "date,amount,memo\n2026-04-01,10,a,b\n2026-04-02,-0.99,coffee",
      "date,amount,memo",
      "date,amount,memo\n2026-05-01,-10,first\n2026-05-02,-10,second\n2026-05-03,5.05,refund",
      "date,amount,memo\n26-01-01,1,short year\n2026-06-15,0.5,interest",
      "date,amount,memo\n2026-07-01,-1000,big\n2026-07-02,999.99,back"],
             hints=["One parse function returning `Result<Txn>`; the loop only decides whether to print or keep.",
                    "Money in cents: parse the whole and fractional parts separately; never add floats."]),

        _tsp(_FX, "tsm-exam-pages", "Month 6: consume a paginated feed", "stretch",
             "The first line is `pageSize limit`; the second is the feed's numbers. `fetchPage(k)` (async, "
             "no timers) returns page k's items and the next page number, or `null` after the last. Write an "
             "async generator `pages()` over it, and consume it with `for await`: print `page <k>: <items>` as "
             "each page arrives, and add its items one at a time to a running sum — stopping for good just "
             "before an item would push the sum past `limit`. The generator's `finally` prints `closed after "
             "page <k>`. Then print `sum <s>` and `stopped at <item>` or `all consumed`.",
             r'''
const [head = "", feed = ""] = input.split("\n");
const [pageSize = 1, limit = 0] = head.trim().split(/\s+/).map(Number);
const all = feed.trim() === "" ? [] : feed.trim().split(/\s+/).map(Number);
type Page = { items: number[]; next: number | null };
async function fetchPage(k: number): Promise<Page> {
  await Promise.resolve();
  const items = all.slice(k * pageSize, (k + 1) * pageSize);
  return { items, next: (k + 1) * pageSize < all.length ? k + 1 : null };
}
async function* pages(): AsyncGenerator<number[]> {
  let k: number | null = 0;
  let last = 0;
  try {
    while (k !== null) {
      const page: Page = await fetchPage(k);
      last = k;
      yield page.items;
      k = page.next;
    }
  } finally {
    console.log(`closed after page ${last}`);
  }
}
let sum = 0;
let stoppedAt: number | undefined;
let k = 0;
outer: for await (const items of pages()) {
  console.log(`page ${k}: ${items.join(" ") || "(empty)"}`);
  k++;
  for (const item of items) {
    if (sum + item > limit) {
      stoppedAt = item;
      break outer;
    }
    sum += item;
  }
}
console.log(`sum ${sum}`);
console.log(stoppedAt === undefined ? "all consumed" : `stopped at ${stoppedAt}`);
''', ["2 10\n1 2 3 4 5 6",
      "3 100\n5 5 5 5",
      "1 0\n1",
      "4 7\n1 1 1 1 1 1 1 1 1",
      "2 5\n",
      "5 50\n10 10 10 10 10 1",
      "3 6\n2 2 2 2",
      "2 1000\n100 200 300"],
             hints=["`break` out of a `for await` calls the generator's `return`, which runs its `finally`.",
                    "A label on the outer loop lets the inner loop stop both."]),
    ],
    "type_section": [
        _tsp_types(_FX, "tsm-exam-promisify", "Type puzzle: Promisify", "core",
                   "Write `Promisify<F>`: for a function type, the same parameters returning a `Promise` of "
                   "its (awaited) return type; `never` for anything that is not a function.",
                   '''
type Promisify<F> = F extends (...args: infer A) => infer R ? (...args: A) => Promise<Awaited<R>> : never;
''', "F extends (...args: infer A) => infer R ? (...args: A) => Promise<Awaited<R>> : never",
                   '''
type _1 = Expect<Equal<Promisify<(a: number, b: string) => boolean>, (a: number, b: string) => Promise<boolean>>>;
type _2 = Expect<Equal<Promisify<() => Promise<number>>, () => Promise<number>>>;
type _3 = Expect<Equal<Promisify<string>, never>>;
''', hints=["`infer` the parameter tuple and the return type in one pattern.",
            "Wrap the return in `Awaited` so a function that already returns a promise is not double-wrapped."]),

        _tsp_types(_FX, "tsm-exam-entries", "Type puzzle: Entries", "core",
                   "Write `Entries<T>`: the union of `[key, value]` tuples for every property of `T`. An "
                   "optional property's value type includes `undefined`, but no stray `undefined` member may "
                   "appear in the union itself.",
                   '''
type Entries<T> = { [K in keyof T]-?: [K, T[K]] }[keyof T];
''', "{ [K in keyof T]-?: [K, T[K]] }[keyof T]",
                   '''
type _1 = Expect<Equal<Entries<{ a: number; b: string }>, ["a", number] | ["b", string]>>;
type _2 = Expect<Equal<Entries<{ c?: boolean }>, ["c", boolean | undefined]>>;
type _3 = Expect<Equal<Entries<{}>, never>>;
''', hints=["Map every key to its tuple, then index the mapped type with `keyof T` to get the union.",
            "`-?` stops optional keys from adding `undefined` to the union."]),

        _tsp_types(_FX, "tsm-exam-from-entries", "Type puzzle: FromEntries", "core",
                   "Write `FromEntries<E>`: the object type built from a union of `[key, value]` tuples — the "
                   "inverse of `Entries`.",
                   '''
type FromEntries<E extends [PropertyKey, unknown]> = { [P in E as P[0]]: P[1] };
''', "{ [P in E as P[0]]: P[1] }",
                   '''
type _1 = Expect<Equal<FromEntries<["a", 1] | ["b", "x"]>, { a: 1; b: "x" }>>;
type _2 = Expect<Equal<FromEntries<["only", boolean]>, { only: boolean }>>;
type _3 = Expect<Equal<FromEntries<never>, {}>>;
''', hints=["A mapped type can iterate a union of anything — not only keys — if `as` gives each member a key.",
            "`[P in E as P[0]]: P[1]`."]),

        _tsp_types(_FX, "tsm-exam-zip", "Type puzzle: Zip", "stretch",
                   "Write `Zip<A, B>`: pair up two tuples element by element; the result is as long as the "
                   "shorter one.",
                   '''
type Zip<A extends unknown[], B extends unknown[]> =
  A extends [infer HA, ...infer RA]
    ? B extends [infer HB, ...infer RB] ? [[HA, HB], ...Zip<RA, RB>] : []
    : [];
''', '''A extends [infer HA, ...infer RA]
    ? B extends [infer HB, ...infer RB] ? [[HA, HB], ...Zip<RA, RB>] : []
    : []''',
                   '''
type _1 = Expect<Equal<Zip<[1, 2], ["a", "b"]>, [[1, "a"], [2, "b"]]>>;
type _2 = Expect<Equal<Zip<[1, 2, 3], ["a"]>, [[1, "a"]]>>;
type _3 = Expect<Equal<Zip<[], [1]>, []>>;
''', hints=["Take the head of both tuples with `[infer H, ...infer R]`, then recurse on the rests.",
            "Stop with `[]` as soon as either tuple is empty."]),

        _tsp_types(_FX, "tsm-exam-count-of", "Type puzzle: CountOf", "stretch",
                   "Write `CountOf<T, V>`: how many elements of the tuple `T` are exactly `V` (mutually "
                   "assignable — `boolean` is not `true`), as a number literal. Count with an accumulator "
                   "tuple and read its `length`.",
                   '''
type CountOf<T extends readonly unknown[], V, Acc extends unknown[] = []> =
  T extends readonly [infer H, ...infer R]
    ? CountOf<R, V, [H] extends [V] ? ([V] extends [H] ? [...Acc, H] : Acc) : Acc>
    : Acc["length"];
''', '''T extends readonly [infer H, ...infer R]
    ? CountOf<R, V, [H] extends [V] ? ([V] extends [H] ? [...Acc, H] : Acc) : Acc>
    : Acc["length"]''',
                   '''
type _1 = Expect<Equal<CountOf<[1, 2, 1, 3, 1], 1>, 3>>;
type _2 = Expect<Equal<CountOf<["a", "b"], "c">, 0>>;
type _3 = Expect<Equal<CountOf<[true, boolean, true], true>, 2>>;
type _4 = Expect<Equal<CountOf<[], 1>, 0>>;
''', hints=["Walk the tuple head by head, growing `Acc` by one element for every match.",
            "Wrap both sides in `[…]` so the comparison does not distribute, and check it both ways."]),
    ],
}
