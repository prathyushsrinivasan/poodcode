# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — the arc project (TS_MASTERY_ROADMAP X-44, M1-05,
# M2-05, M3-05): one ledger program that grows with the programme.
#
#   v1  week 4   a formatted statement from raw lines (strings, numbers)
#   v2  week 8   typed records from JSON, summarised with array methods
#   v3  week 12  a discriminated union of events, parsed through a guard
#   v4  week 14  split into modules, branded cents  (TS_PROJECTS[14])
#   v5  week 22  the typed event catalogue          (TS_PROJECTS[22])
#   final w27    classes, generators, Results, async (TS_PROJECTS[27])
#
# v1-v3 are the week's second project, shown beside the weekly one. They are
# optional like every project, judged by acceptance tests, and each one's
# brief says what changed since the last version. exec()'d before
# mastery_ts_attach.py, which attaches TS_ARC_PROJECTS as `arc_project`.
# ---------------------------------------------------------------------------

TS_ARC_PROJECTS = {}

TS_ARC_PROJECTS[4] = _project(
    4, "ledger.ts v1 — a printed bank statement",
    "The first version of the programme's running project. Every month it grows: typed records in month 2, a "
    "discriminated union in month 3, modules and branded money in month 4, and in the end classes, generators and "
    "async loading. Version 1 only has to read raw lines and print a clean statement — with strings, numbers and "
    "a loop.",
    ["Each input line is `YYYY-MM-DD amount description…` — the amount like `2500` or `-45.50`, the description "
     "one or more words. Skip blank lines.",
     "Print a header `DATE` (padded to 12) `DESCRIPTION` (padded to 21) `AMOUNT` (right-aligned in 10) `BALANCE` "
     "(right-aligned in 11), then one row per transaction in the same columns: the description cut to 19 "
     "characters plus `…` when it is longer than 20, the amount and the running balance to two decimals.",
     "A line with fewer than three parts, or an amount that is not a number, prints `line <n>: skipped` instead "
     "of a row (n counts from 1) and changes nothing.",
     "Finish with 54 dashes and `income <total of positive amounts> · spending <total of negative amounts> · "
     "<n> transactions` (`transaction` for one).",
     "Keep money in whole cents while you add it up — `0.1 + 0.2` is not `0.3`."],
    r"""
const lines = input.split("\n");
const money = (cents: number): string => (cents / 100).toFixed(2);
console.log("DATE".padEnd(12) + "DESCRIPTION".padEnd(21) + "AMOUNT".padStart(10) + "BALANCE".padStart(11));
let balance = 0;
let income = 0;
let spending = 0;
let count = 0;
for (let i = 0; i < lines.length; i++) {
  const line = (lines[i] ?? "").trim();
  if (line === "") continue;
  const parts = line.split(/\s+/);
  const date = parts[0] ?? "";
  const amount = Number(parts[1]);
  if (parts.length < 3 || !Number.isFinite(amount)) {
    console.log(`line ${i + 1}: skipped`);
    continue;
  }
  const description = parts.slice(2).join(" ");
  const cents = Math.round(amount * 100);
  balance += cents;
  count++;
  if (cents >= 0) income += cents;
  else spending += cents;
  const shown = description.length > 20 ? description.slice(0, 19) + "…" : description;
  console.log(date.padEnd(12) + shown.padEnd(21) + money(cents).padStart(10) + money(balance).padStart(11));
}
console.log("-".repeat(54));
console.log(`income ${money(income)} · spending ${money(spending)} · ${count} transaction${count === 1 ? "" : "s"}`);
""", ["2026-01-05 2500 Salary\n2026-01-09 -45.50 Groceries\n2026-01-20 500 Freelance work\n2026-02-01 -1200 Rent",
      "2026-03-01 0.1 a\n2026-03-02 0.2 b",
      "2026-04-01 abc Broken\n2026-04-02 10 Fine\nshort line",
      "2026-05-01 -19.99 A very long description that will not fit",
      "2026-06-01 42 Only one\n\n\n"],
    stretch=["Print the month (`YYYY-MM`) as a heading whenever it changes.",
             "Accept amounts written with a thousands separator (`1,200.00`)."],
    eid="arc-ledger-v1",
)

TS_ARC_PROJECTS[8] = _project(
    8, "ledger.ts v2 — typed records and a monthly summary",
    "Version 2 of the running project. Since v1 the raw lines have become JSON records, and the program stops "
    "printing a row per line: it parses each record into a typed `Transaction`, then summarises with array "
    "methods — by category, by month — and formats money through one `formatMoney` with options.",
    ["Each input line is a JSON object with `date` (`YYYY-MM-DD`), `amount` (a number, in dollars), `category` "
     "(a string) and an optional `memo`. A line that is not JSON, or lacks a string `date`, a number `amount` or a "
     "string `category`, prints `line <n>: invalid` and is left out.",
     "Write `formatMoney(cents, { symbol, sign })` — `symbol` defaults to `$`, `sign` to `false` — giving "
     "`$1,234.50`: a thousands separator, two decimals, a leading `-` for negatives and, when `sign` is on, a "
     "leading `+` for positives.",
     "Print `By category:` then `  <category>: <total with sign> (<count>)` for each category, alphabetically.",
     "Print `By month:` then `  <YYYY-MM>: <total with sign>` for each month, in order.",
     "Then `Biggest expense: <memo, or the category if there is none> <amount without sign>` for the most "
     "negative amount (`Biggest expense: none` without one), and `Net: <total with sign>`."],
    r"""
type Transaction = { date: string; cents: number; category: string; memo: string };

function formatMoney(cents: number, { symbol = "$", sign = false }: { symbol?: string; sign?: boolean } = {}): string {
  const abs = Math.abs(cents);
  const whole = Math.floor(abs / 100).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  const frac = String(abs % 100).padStart(2, "0");
  const prefix = cents < 0 ? "-" : sign && cents > 0 ? "+" : "";
  return `${prefix}${symbol}${whole}.${frac}`;
}

function parse(line: string): Transaction | null {
  try {
    const { date, amount, category, memo = "" } = JSON.parse(line);
    if (typeof date !== "string" || typeof amount !== "number" || typeof category !== "string") return null;
    return { date, cents: Math.round(amount * 100), category, memo: typeof memo === "string" ? memo : "" };
  } catch {
    return null;
  }
}

const txns: Transaction[] = [];
input.split("\n").forEach((line, i) => {
  const t = parse(line);
  if (t === null) console.log(`line ${i + 1}: invalid`);
  else txns.push(t);
});

const total = (ts: Transaction[]): number => ts.reduce((sum, t) => sum + t.cents, 0);

console.log("By category:");
const byCategory = Object.groupBy(txns, (t) => t.category);
for (const category of Object.keys(byCategory).sort()) {
  const ts = byCategory[category] ?? [];
  console.log(`  ${category}: ${formatMoney(total(ts), { sign: true })} (${ts.length})`);
}

console.log("By month:");
const byMonth = Object.groupBy(txns, (t) => t.date.slice(0, 7));
for (const month of Object.keys(byMonth).sort()) {
  console.log(`  ${month}: ${formatMoney(total(byMonth[month] ?? []), { sign: true })}`);
}

const expenses = txns.filter((t) => t.cents < 0).toSorted((a, b) => a.cents - b.cents);
const biggest = expenses[0];
console.log(
  biggest === undefined
    ? "Biggest expense: none"
    : `Biggest expense: ${biggest.memo || biggest.category} ${formatMoney(-biggest.cents)}`
);
console.log(`Net: ${formatMoney(total(txns), { sign: true })}`);
""", ['{"date":"2026-01-05","amount":2500,"category":"salary","memo":"January"}\n{"date":"2026-01-09","amount":-45.5,"category":"food","memo":"Groceries"}\n{"date":"2026-02-01","amount":-1200,"category":"home","memo":"Rent"}\n{"date":"2026-02-03","amount":-12.25,"category":"food"}',
      '{"date":"2026-03-01","amount":1234567.89,"category":"windfall"}',
      'not json\n{"date":"2026-04-01","amount":"10","category":"x"}\n{"date":"2026-04-02","amount":10,"category":"gift"}',
      '{"date":"2026-05-01","amount":-3,"category":"coffee"}\n{"date":"2026-05-02","amount":-3,"category":"coffee","memo":"flat white"}',
      '{"date":"2026-06-30","amount":0,"category":"zero"}'],
    stretch=["Add a `--since YYYY-MM` first line that filters the records before summarising.",
             "Give `formatMoney` a `decimals` option."],
    eid="arc-ledger-v2",
)

TS_ARC_PROJECTS[12] = _project(
    12, "ledger.ts v3 — events as a discriminated union",
    "Version 3 of the running project. Since v2 the records have become events of three kinds that carry "
    "different data. Model them as a discriminated union, let a type guard decide what is valid, and let the "
    "compiler check that every kind is handled — then add a kind and watch it point at every `switch`.",
    ["Each input line is a JSON event: `{\"kind\":\"deposit\",\"account\":…,\"amount\":…}`, "
     "`{\"kind\":\"withdrawal\",\"account\":…,\"amount\":…}` or `{\"kind\":\"transfer\",\"from\":…,\"to\":…,\"amount\":…}`, "
     "with accounts as non-empty strings and a positive amount in dollars.",
     "Write a type guard `isEvent(x: unknown): x is LedgerEvent`. A line that is not JSON or not a valid event "
     "prints `line <n>: invalid`.",
     "Apply events in order. A withdrawal or transfer that would take an account below zero prints `line <n>: "
     "rejected <kind> (insufficient funds)` and changes nothing.",
     "Every applied event prints one line from a `switch` on `kind` that ends in an exhaustiveness check: "
     "`deposit 100.00 to A`, `withdrawal 30.00 from A`, `transfer 20.00 A -> B`.",
     "Finish with each account that ever appeared in an applied event, alphabetically, as `<account>: "
     "<balance>`, then `deposits=<n> withdrawals=<n> transfers=<n>` counting applied events."],
    r"""
type LedgerEvent =
  | { kind: "deposit"; account: string; amount: number }
  | { kind: "withdrawal"; account: string; amount: number }
  | { kind: "transfer"; from: string; to: string; amount: number };

const isAccount = (v: unknown): v is string => typeof v === "string" && v.length > 0;

function isEvent(x: unknown): x is LedgerEvent {
  if (typeof x !== "object" || x === null) return false;
  const e = x as Record<string, unknown>;
  if (typeof e.amount !== "number" || !(e.amount > 0)) return false;
  switch (e.kind) {
    case "deposit":
    case "withdrawal":
      return isAccount(e.account);
    case "transfer":
      return isAccount(e.from) && isAccount(e.to);
    default:
      return false;
  }
}

const money = (cents: number): string => (cents / 100).toFixed(2);

function describe(e: LedgerEvent): string {
  switch (e.kind) {
    case "deposit":
      return `deposit ${money(Math.round(e.amount * 100))} to ${e.account}`;
    case "withdrawal":
      return `withdrawal ${money(Math.round(e.amount * 100))} from ${e.account}`;
    case "transfer":
      return `transfer ${money(Math.round(e.amount * 100))} ${e.from} -> ${e.to}`;
    default: {
      const unreachable: never = e;
      return unreachable;
    }
  }
}

const balances = new Map<string, number>();
const counts = { deposit: 0, withdrawal: 0, transfer: 0 };
const bal = (a: string): number => balances.get(a) ?? 0;

input.split("\n").forEach((line, i) => {
  let parsed: unknown;
  try {
    parsed = JSON.parse(line);
  } catch {
    parsed = null;
  }
  if (!isEvent(parsed)) {
    console.log(`line ${i + 1}: invalid`);
    return;
  }
  const e = parsed;
  const cents = Math.round(e.amount * 100);
  const source = e.kind === "withdrawal" ? e.account : e.kind === "transfer" ? e.from : null;
  if (source !== null && bal(source) < cents) {
    console.log(`line ${i + 1}: rejected ${e.kind} (insufficient funds)`);
    return;
  }
  if (e.kind === "deposit") balances.set(e.account, bal(e.account) + cents);
  else if (e.kind === "withdrawal") balances.set(e.account, bal(e.account) - cents);
  else {
    balances.set(e.from, bal(e.from) - cents);
    balances.set(e.to, bal(e.to) + cents);
  }
  counts[e.kind]++;
  console.log(describe(e));
});

for (const account of [...balances.keys()].sort()) console.log(`${account}: ${money(bal(account))}`);
console.log(`deposits=${counts.deposit} withdrawals=${counts.withdrawal} transfers=${counts.transfer}`);
""", ['{"kind":"deposit","account":"A","amount":100}\n{"kind":"withdrawal","account":"A","amount":30}\n{"kind":"transfer","from":"A","to":"B","amount":20}',
      '{"kind":"withdrawal","account":"A","amount":5}\n{"kind":"deposit","account":"A","amount":5}\n{"kind":"withdrawal","account":"A","amount":5}',
      '{"kind":"refund","account":"A","amount":5}\n{"kind":"deposit","account":"","amount":5}\n{"kind":"deposit","account":"C","amount":-1}\nnope',
      '{"kind":"deposit","account":"Z","amount":0.1}\n{"kind":"deposit","account":"Z","amount":0.2}\n{"kind":"transfer","from":"Z","to":"Y","amount":0.3}',
      '{"kind":"transfer","from":"A","to":"B","amount":1}\n{"kind":"deposit","account":"B","amount":2.5}'],
    stretch=["Add a fourth kind, `fee`, and follow the compiler to every place that must handle it.",
             "Report every problem with a line instead of stopping at the first reason it is invalid."],
    eid="arc-ledger-v3",
)
