# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — Month 6: Runtime & architecture (weeks 23-26), plus
# the optional capstone week 27.
#
# The month's week tables, coding finals, authored bank questions and the
# extra final tests. exec()'d in order by mastery_defs.py, which defines
# `_w`, `_ts_exam` and the four collections this file extends.
# ---------------------------------------------------------------------------

TS_WEEKS.extend([
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

    # D-2: the old "Errors & Async" week carried four chapters. Errors now have
    # week 25 to themselves; async moves to week 26; the capstone that used to
    # share week 26 with modules and declarations is the optional week 27.
    _w(25, "Month 6 · Runtime & architecture",
        "Errors, Result & Resource Management",
        "Make failure visible in the type: throw for bugs, return a `Result` for failures the caller must handle, and never lose an error.",
        ["ts_errors", "ts_error_types"],
        [("evaluate-rpn", "A parser where every malformed token is a failure you must decide how to report."),
         ("valid-sudoku", "Validation that finds every violation, not just the first."),
         ("basic-calculator", "A real grammar — and a real set of ways for input to be wrong.")],
        "Write a `parse.ts`: a `Result`-based CSV parser that reports every bad line with its line number, never throws, and returns the good rows as typed records.",
        [("Under `strict`, what type does `catch (e)` give `e`?",
          ["unknown", "Error", "any", "never"], 0,
          "Any value can be thrown, so TypeScript refuses to assume `Error`. Narrow with `instanceof` before reading properties."),
         ("What makes `Result<T, E>` enforce handling?",
          ["It is a discriminated union — `value` only exists after checking `ok`",
           "The compiler tracks unhandled Results",
           "It throws if the error branch is ignored",
           "E defaults to string"], 0,
          "On the failure branch there is no `value` property at all, so skipping the check is a type error rather than a runtime surprise.")]),

    _w(26, "Month 6 · Runtime & architecture",
        "Async, Concurrency & Cancellation",
        "Run async work concurrently on purpose, keep the output deterministic, and stop work you no longer need.",
        ["ts_async", "ts_async_patterns"],
        [("hit-counter", "Time-ordered state — the shape of every rate limiter."),
         ("stock-spanner", "Incremental computation over a stream of values."),
         ("process-tasks-using-servers", "A simulated clock and a pool of workers — concurrency without real timers.")],
        "Write a `fetchAll.ts` that loads several simulated resources concurrently, races each against a timeout, and returns a `Result` per resource — no exception escapes.",
        [("What is the total time of `await Promise.all(ids.map(fetchOne))` versus awaiting in a loop?",
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

    # Optional and ungated by the programme: it opens once week 26 is done, and
    # never counts toward the 26 weeks, the pace or completion (D-2).
    _w(27, "Capstone · optional",
        "Capstone & Mock Interview",
        "Put six months together in one program, then rehearse the interview: TypeScript idioms, a DSA problem in TypeScript, and a type-level puzzle.",
        [],
        [("median-from-stream", "Two heaps, cleanly encapsulated."),
         ("word-ladder-length", "BFS over a derived graph."),
         ("lfu-cache", "The hardest design problem in the bank — take your time.")],
        "Capstone: build a small typed CLI — a `Result`-based parser, a branded id type, a generic store with an iterator, an ambient declaration for one host global — `strict` and `noUncheckedIndexedAccess` clean. Then run a mock interview on yourself: 45 minutes, one idiom question, one problem above, one type puzzle.",
        [("An interviewer asks you to type `pipe(f, g, h)`. What is the honest first answer?",
          ["Overloads for a fixed number of steps — or a variadic tuple type if they want the general version",
           "`(...fns: any[]) => any`",
           "It cannot be typed in TypeScript",
           "Use a class instead"], 0,
          "Overloads are what most libraries ship; the recursive tuple version exists but is harder to read. Saying which trade-off you are making is the point."),
         ("You are asked to explain `unknown` vs `any` in one sentence. Which is best?",
          ["`unknown` makes you prove what a value is before using it; `any` turns checking off",
           "They are the same, but `unknown` is newer",
           "`any` is for objects and `unknown` for primitives",
           "`unknown` is only for errors"], 0,
          "Lead with the consequence for the reader of the code — that is what an interviewer is listening for."),
         ("Where do types stop helping in a program that reads JSON?",
          ["At the boundary: `JSON.parse` returns `any`, so the data must be validated before it gets a type",
           "Nowhere — the compiler checks JSON files",
           "Only inside async functions",
           "At every function call"], 0,
          "Types describe what the code assumes. Untrusted input has to earn its type through a check or a schema.")],
        optional=True),
])


TS_EXAMS.update({
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
  const [op, amountRaw] = (lines[i] ?? "").trim().split(/\\s+/);
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
const [count = 0, divisor = 1] = input.split(/\\s+/).map(Number);
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

    25: _ts_exam_io(
        "final-w25",
        "Result-based config loader",
        "The input is a config file of `key=value` lines. Blank lines and lines starting with `#` are ignored. The known keys are `host` (a non-empty string), `port` (an integer 1-65535), `debug` (`true` or `false`) and `retries` (an integer 0-10); their defaults are `localhost`, `8080`, `false` and `3`. A line fails with `missing '='`, `empty key`, `unknown key <k>`, `duplicate key <k>`, `empty host`, `not an integer: <v>`, `out of range <min>-<max>: <v>` or `not a boolean: <v>`. Print every failure as `line <n>: <message>` in input order (lines numbered from 1), then either the final config as `host=… port=… debug=… retries=…`, or `invalid: <count> error(s)`. Nothing may throw: every line's outcome is a `Result`.",
        r'''
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };
const ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
const err = <E>(error: E): Result<never, E> => ({ ok: false, error });

type Config = { host: string; port: number; debug: boolean; retries: number };
type Key = keyof Config;
const DEFAULTS: Config = { host: "localhost", port: 8080, debug: false, retries: 3 };

function parseInteger(text: string, min: number, max: number): Result<number, string> {
  if (!/^-?\d+$/.test(text)) return err("not an integer: " + text);
  const n = Number(text);
  return n < min || n > max ? err(`out of range ${min}-${max}: ${n}`) : ok(n);
}

const parsers: { [K in Key]: (text: string) => Result<Config[K], string> } = {
  host: (t) => (t.length > 0 ? ok(t) : err("empty host")),
  port: (t) => parseInteger(t, 1, 65535),
  debug: (t) => (t === "true" ? ok(true) : t === "false" ? ok(false) : err("not a boolean: " + t)),
  retries: (t) => parseInteger(t, 0, 10),
};

function isKey(k: string): k is Key {
  return Object.hasOwn(DEFAULTS, k);
}

function setKey<K extends Key>(config: Config, key: K, text: string): Result<Config, string> {
  const r = parsers[key](text);
  return r.ok ? ok({ ...config, [key]: r.value }) : r;
}

function parseLine(line: string, config: Config, seen: Set<Key>): Result<Config, string> {
  const eq = line.indexOf("=");
  if (eq < 0) return err("missing '='");
  const key = line.slice(0, eq).trim();
  if (key === "") return err("empty key");
  if (!isKey(key)) return err("unknown key " + key);
  if (seen.has(key)) return err("duplicate key " + key);
  seen.add(key);
  return setKey(config, key, line.slice(eq + 1).trim());
}

const errors: string[] = [];
const seen = new Set<Key>();
let config = DEFAULTS;
(input === "" ? [] : input.split("\n")).forEach((raw, i) => {
  const line = raw.trim();
  if (line === "" || line.startsWith("#")) return;
  const r = parseLine(line, config, seen);
  if (r.ok) config = r.value;
  else errors.push(`line ${i + 1}: ${r.error}`);
});
for (const e of errors) console.log(e);
console.log(errors.length === 0
  ? `host=${config.host} port=${config.port} debug=${config.debug} retries=${config.retries}`
  : `invalid: ${errors.length} error(s)`);
''',
        ["port=3000\nhost=example.com",
         "",
         "debug=yes\nport=70000\nretries=2",
         "# a comment\nhost=\nport=80",
         "colour=blue\n=5\nport",
         "port=80\nport=81",
         "retries=10\ndebug=true\nhost=db.local\nport=5432",
         "port=8o80\nretries=-1",
         "toString=1",
         "  host = spaced.io  \n\nretries = 0"],
        hint="Give each key its own parser returning a `Result`, and let the line parser return a `Result<Config, string>` too — the loop then only ever branches on `ok`."),

    26: _ts_exam(
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

    27: _ts_exam(
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
  const line = (lines[i] ?? "").trim();
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
})


TS_QUIZ_EXTRA.update({
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
})


TS_EXAM_MORE_TESTS.update({
    23: [
        ('2\nwithdraw 0\ndeposit 0', 'refused\n0\n0'),
        ('3\ndeposit 50\nwithdraw 50\nwithdraw 1', '50\n0\nrefused\n0'),
        ('2\ndeposit -5\nwithdraw 1', '0\nrefused\n0'),
        ('4\ndeposit 10\nwithdraw 3\nwithdraw 3\nwithdraw 3', '10\n7\n4\n1\n1'),
        ('1\ndeposit 1000000', '1000000\n1000000'),
    ],
    24: [
        ('5 1', '1 4 9 16 25\n55'),
        ('4 7', '49 196 441 784\n1470'),
        ('1 100', '10000\n10000'),
        ('3 3', '9 36 81\n126'),
    ],
    26: [
        ('5 1 3', '5=50\n1=10\n3=30\n3 90'),
        ('-5', '-5=failed\n0 0'),
        ('0', '0=0\n1 0'),
        ('2 -3 4 -1', '2=20\n-3=failed\n4=40\n-1=failed\n2 60'),
    ],
    27: [
        ('1\nr-10', 'rejected r-10\n(empty)\n0'),
        ('3\nr-1 a\nr-2 b\nr-3 c', 'added r-1\nadded r-2\nadded r-3\nr-1 r-2 r-3\n3'),
        ('2\nR-1 x\nr-x y', 'rejected R-1 x\nrejected r-x y\n(empty)\n0'),
        ('3\nr-2 b\nr-1 a\nr-2 c', 'added r-2\nadded r-1\nadded r-2\nr-2 r-1\n2'),
    ],
})
