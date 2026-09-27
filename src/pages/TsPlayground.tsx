// The TypeScript playground (TS_MASTERY_ROADMAP X-67, with X-64, X-65, M3-01
// and M5-01): a scratch file, and four views of it computed by the editor's own
// TypeScript service —
//   * Types      every declared type fully expanded, every top-level value's type
//   * Narrowing  one variable's type at each place it is used
//   * What runs  the JavaScript the types erase to
//   * Compiler   strictness flags to flip, and the errors they produce
//   * Step       a conditional type's evaluation, one union member at a time
//   * Machines   a union of states and its transitions, drawn (M3-03)
//                (M5-01): which branch, what each `infer` binds, the result
// Run executes the file through the real judge, like any exercise.

import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useMonaco } from "@monaco-editor/react";
import { api } from "../api";
import { CodeEditor } from "../components/CodeEditor";
import { TsErrorLinks } from "../components/TsErrorLinks";
import { restoreJudgeCompilerOptions, setPlaygroundCompilerOptions } from "../monacoSetup";
import {
  expandableTypes,
  lineOf,
  occurrences,
  probeSource,
  probeType,
} from "../lib/tsAnalysis";
import type { ProcOut } from "../types";
import { applications, conditionalAliases, planSteps, splitUnion, withArg } from "../lib/typeStepper";
import { analyseMachine, findMachines } from "../lib/stateMachine";
import { StateDiagram } from "../components/StateDiagram";

const MAIN = "file:///playground/main.ts";
const PROBE = "file:///playground/__probe.ts";
const STEP_PROBE = "file:///playground/__steps.ts";
// A distributive identity: forces an alias or application to evaluate and
// prints a union member by member, without expanding `Promise` or `Date` into
// their structure the way the Types view's helper does.
const STEP_HELPER = "type __PgId<T> = T extends unknown ? T : never;";
const STORE = "poodcode:ts-playground";

type Example = { title: string; focus: string; code: string };

const EXAMPLES: Example[] = [
  {
    title: "Narrowing",
    focus: "input",
    code: `type Shape = { kind: "circle"; r: number } | { kind: "square"; side: number };

function area(s: Shape): number {
  if (s.kind === "circle") return Math.PI * s.r ** 2;
  return s.side ** 2;
}

function describe(input: string | number | null): string {
  if (input === null) return "nothing";
  if (typeof input === "number") return input.toFixed(1);
  return input.toUpperCase();
}

console.log(area({ kind: "square", side: 3 }), describe(2), describe(null), describe("ok"));
`,
  },
  {
    title: "Type-level",
    focus: "user",
    code: `type User = { id: number; name: string; email?: string };
type Patch = Partial<Omit<User, "id">>;
type Keys = keyof User;
type Getters = { [K in keyof User as \`get\${Capitalize<K>}\`]: () => User[K] };
type Unwrapped = Awaited<Promise<Promise<number>>>;
type Names = User["name" | "email"];

const user: User = { id: 1, name: "Ada" };
const patch: Patch = { email: "ada@example.com" };
console.log({ ...user, ...patch });
`,
  },
  {
    title: "State machine",
    focus: "status",
    code: `// Open the Machines tab. Try deleting "archived" from the table, or adding a state.
type Status = "draft" | "review" | "live" | "archived";

const NEXT: Record<Status, readonly Status[]> = {
  draft: ["review"],
  review: ["draft", "live"],
  live: ["archived"],
  archived: [],
};

function move(status: Status, to: Status): Status {
  if (!NEXT[status].includes(to)) throw new Error(\`\${status} cannot become \${to}\`);
  return to;
}

let status: Status = "draft";
status = move(status, "review");
status = move(status, "live");
console.log(status);
`,
  },
  {
    title: "Conditional types, stepped",
    focus: "sizes",
    code: `// Open the Step tab: each application below is evaluated one union member at a time.
type ElementOf<T> = T extends readonly (infer E)[] ? E : T;
type Unwrap<T> = T extends Promise<infer V> ? V : T;
type IsString<T> = [T] extends [string] ? "yes" : "no";

type Mixed = ElementOf<string[] | readonly [1, 2] | boolean>;
type Loaded = Unwrap<Promise<number> | Promise<string> | Date>;
type Whole = IsString<"a" | 1>;
type Nothing = ElementOf<never>;

const sizes = ["S", "M"] as const;
console.log(sizes.length);
`,
  },
  {
    title: "What runs",
    focus: "p",
    code: `interface Point {
  x: number;
  y: number;
}

function dist(a: Point, b: Point): number {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

const p = { x: 3, y: 4 } satisfies Point;
const origin: Point = { x: 0, y: 0 };
console.log(dist(origin, p) as number);
`,
  },
  {
    title: "Classes & exhaustiveness",
    focus: "kind",
    code: `interface Shape {
  area(): number;
}

abstract class Base implements Shape {
  static count = 0;
  #id: number;
  protected constructor() {
    this.#id = ++Base.count;
  }
  abstract area(): number;
  get id(): number {
    return this.#id;
  }
}

class Circle extends Base {
  readonly r: number;
  constructor(r: number) {
    super();
    this.r = r;
  }
  area(): number {
    return Math.PI * this.r ** 2;
  }
}

type Kind = "circle" | "square";
function label(kind: Kind): string {
  switch (kind) {
    case "circle":
      return "round";
    case "square":
      return "boxy";
    default: {
      const unreachable: never = kind;
      return unreachable;
    }
  }
}

console.log(new Circle(1).area().toFixed(2), label("square"));
`,
  },
  {
    title: "Strictness",
    focus: "s",
    code: `const scores: Record<string, number> = { ana: 3 };
const s = scores["bo"];
console.log(s.toFixed(1));

type Profile = { nick?: string };
const profile: Profile = { nick: undefined };

function lookup(table: { [key: string]: string }) {
  return table.missing;
}
console.log(profile, lookup({}));
`,
  },
];

type Flags = Record<string, boolean>;

/** The tsconfig explorer (M4-02): fixed programs, each tripping one flag. */
const SAMPLES: { title: string; flag: string; code: string }[] = [
  { title: "Implicit any", flag: "strict", code: "export function echo(x) {\n  return x;\n}\n" },
  {
    title: "Maybe-null value",
    flag: "strict",
    code: "export function len(s: string | null): number {\n  return s.length;\n}\n",
  },
  {
    title: "Caught value",
    flag: "strict",
    code: 'try {\n  JSON.parse("{");\n} catch (e) {\n  console.log(e.message);\n}\nexport {};\n',
  },
  {
    title: "Index read",
    flag: "noUncheckedIndexedAccess",
    code: "const xs = [1, 2, 3];\nexport const n: number = xs[5];\n",
  },
  {
    title: "Optional set to undefined",
    flag: "exactOptionalPropertyTypes",
    code: "type Profile = { nick?: string };\nexport const p: Profile = { nick: undefined };\n",
  },
  {
    title: "Dot on an index signature",
    flag: "noPropertyAccessFromIndexSignature",
    code: "export function get(t: { [key: string]: string }) {\n  return t.name;\n}\n",
  },
  {
    title: "A path with no return",
    flag: "noImplicitReturns",
    code: "export function sign(n: number): number | undefined {\n  if (n > 0) return 1;\n}\n",
  },
  {
    title: "Fallthrough",
    flag: "noFallthroughCasesInSwitch",
    code: 'export function say(k: number) {\n  switch (k) {\n    case 1:\n      console.log("one");\n    case 2:\n      console.log("two");\n  }\n}\n',
  },
];

type SampleResult = { title: string; flag: string; ok: boolean; first: string };
type ClassInfo = {
  name: string;
  abstract: boolean;
  extends: string;
  implements: string[];
  members: { name: string; kind: string; visibility: "+" | "-" | "#"; isStatic: boolean }[];
};
type NeverCheck = { line: number; ok: boolean; message: string };

const FLAG_INFO: { key: string; label: string; note: string }[] = [
  { key: "strict", label: "strict", note: "The family: null checks, no implicit any, strict function types…" },
  { key: "noUncheckedIndexedAccess", label: "noUncheckedIndexedAccess", note: "Every a[i] and record[key] may be undefined." },
  { key: "exactOptionalPropertyTypes", label: "exactOptionalPropertyTypes", note: "`prop?: T` no longer accepts an explicit undefined." },
  { key: "noPropertyAccessFromIndexSignature", label: "noPropertyAccessFromIndexSignature", note: "Index-signature keys must be read with brackets." },
  { key: "noImplicitReturns", label: "noImplicitReturns", note: "Every path of a function that returns must return." },
  { key: "noFallthroughCasesInSwitch", label: "noFallthroughCasesInSwitch", note: "A non-empty case must end in break/return." },
];

const DEFAULT_FLAGS: Flags = {
  strict: true,
  noUncheckedIndexedAccess: false,
  exactOptionalPropertyTypes: false,
  noPropertyAccessFromIndexSignature: false,
  noImplicitReturns: false,
  noFallthroughCasesInSwitch: false,
};

type Diag = { code: number; line: number; message: string };
type Row = { label: string; type: string; line?: number };
type StepMember = { member: string; branch: string; infers: { name: string; type: string }[]; result: string };
type Stepped = {
  name: string;
  application: string;
  arg: string | null;
  cond: { check: string; ext: string; yes: string; no: string };
  members: StepMember[];
  total: string;
};

type Analysis = {
  steps: Stepped[];
  types: Row[];
  values: Row[];
  narrowing: Row[];
  js: string;
  diags: Diag[];
  classes: ClassInfo[];
  nevers: NeverCheck[];
};

function flatten(message: unknown): string {
  if (typeof message === "string") return message;
  const m = message as { messageText?: string; next?: unknown[] };
  const head = m.messageText ?? "";
  const rest = (m.next ?? []).map(flatten).filter(Boolean);
  return [head, ...rest].join(" ");
}

function loadSaved(): { code: string; focus: string } {
  try {
    const raw = localStorage.getItem(STORE);
    if (raw) {
      const v = JSON.parse(raw) as { code?: unknown; focus?: unknown };
      if (typeof v.code === "string" && typeof v.focus === "string") return { code: v.code, focus: v.focus };
    }
  } catch {
    /* private mode or a bad value — start from the first example */
  }
  return { code: EXAMPLES[0]!.code, focus: EXAMPLES[0]!.focus };
}

export default function TsPlayground() {
  const saved = useMemo(loadSaved, []);
  const [code, setCode] = useState(saved.code);
  const [focus, setFocus] = useState(saved.focus);
  const [flags, setFlags] = useState<Flags>(DEFAULT_FLAGS);
  const [view, setView] = useState<"types" | "narrowing" | "js" | "compiler" | "classes" | "step" | "machines">("types");
  const [samples, setSamples] = useState<SampleResult[]>([]);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [stdin, setStdin] = useState("");
  const [run, setRun] = useState<ProcOut | null>(null);
  const [running, setRunning] = useState(false);
  const monaco = useMonaco();
  const seq = useRef(0);
  // M3-03: read from the source text directly — no compiler round trip needed.
  const machines = useMemo(() => findMachines(code), [code]);

  // The playground owns the compiler options while it is open.
  useEffect(() => {
    setPlaygroundCompilerOptions(flags);
  }, [flags]);
  useEffect(() => () => restoreJudgeCompilerOptions(), []);

  useEffect(() => {
    try {
      localStorage.setItem(STORE, JSON.stringify({ code, focus }));
    } catch {
      /* not worth surfacing */
    }
  }, [code, focus]);

  useEffect(() => {
    if (!monaco) return;
    const id = ++seq.current;
    const timer = setTimeout(async () => {
      try {
        const result = await analyse(monaco, focus);
        if (id === seq.current) setAnalysis(result);
      } catch {
        /* the worker restarts while options change — the next edit retries */
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [monaco, code, focus, flags]);

  useEffect(
    () => () => {
      monaco?.editor.getModel(monaco.Uri.parse(PROBE))?.dispose();
      monaco?.editor.getModel(monaco.Uri.parse(STEP_PROBE))?.dispose();
    },
    [monaco]
  );

  // The tsconfig explorer re-checks its sample programs whenever a flag flips.
  useEffect(() => {
    if (!monaco || view !== "compiler") return;
    let live = true;
    const timer = setTimeout(async () => {
      try {
        const out = await checkSamples(monaco);
        if (live) setSamples(out);
      } catch {
        /* retried on the next flip */
      }
    }, 400);
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [monaco, flags, view]);

  async function runIt() {
    setRunning(true);
    setRun(null);
    try {
      setRun(
        await api.runScratch(null, "typescript", code, stdin, flags.noUncheckedIndexedAccess ? "strict+indexed" : "")
      );
    } catch (e) {
      setRun({ stdout: "", stderr: String(e), exit_code: null, timed_out: false, runtime_ms: 0, memory_kb: null, truncated: false });
    } finally {
      setRunning(false);
    }
  }

  const errorText = (analysis?.diags ?? []).map((d) => `error TS${d.code}: ${d.message}`).join("\n");

  return (
    <div className="page">
      <h1 className="page-title">🧪 TypeScript playground</h1>
      <p className="page-sub">
        A scratch file, and what the compiler thinks of it — types expanded, narrowing line by line, the
        JavaScript that actually runs, and the strictness flags that change the verdict.{" "}
        <Link to="/ts-errors">Error glossary →</Link>
      </p>

      <div className="row gap-1 flex-wrap mb-2">
        <span className="dim quiz-note">Examples:</span>
        {EXAMPLES.map((ex) => (
          <button
            key={ex.title}
            className="ghost"
            onClick={() => {
              setCode(ex.code);
              setFocus(ex.focus);
            }}
          >
            {ex.title}
          </button>
        ))}
      </div>

      <div className="playground-grid">
        <div>
          <div className="playground-editor">
            <CodeEditor
              language="typescript"
              path={MAIN}
              value={code}
              onChange={setCode}
              onRun={runIt}
              tsOptionsManaged={false}
            />
          </div>
          <div className="row gap-2 mt-2 items-start">
            <textarea
              value={stdin}
              onChange={(e) => setStdin(e.target.value)}
              placeholder="stdin (optional)"
              style={{ flex: 1, minHeight: 38, fontFamily: "var(--font-mono)", fontSize: 12 }}
            />
            <button onClick={runIt} disabled={running} title="Ctrl+Enter">
              {running ? "Running…" : "▶ Run"}
            </button>
          </div>
          {run && (
            <div className="card mt-2">
              <div className="io-label">
                Output {run.exit_code !== 0 && run.exit_code !== null && `· exit ${run.exit_code}`}{" "}
                {run.timed_out && "· timed out"}
              </div>
              <pre className="code-output m-0">
                {run.stdout || "(no output)"}
              </pre>
              {run.stderr && (
                <>
                  <pre className="code-output" style={{ margin: "6px 0 0", color: "var(--bad)" }}>
                    {run.stderr}
                  </pre>
                  <TsErrorLinks text={run.stderr} />
                </>
              )}
            </div>
          )}
        </div>

        <div className="card playground-side">
          <div className="row gap-1 flex-wrap" role="tablist">
            {(
              [
                ["types", "Types"],
                ["narrowing", "Narrowing"],
                ["js", "What runs"],
                ["compiler", `Compiler${analysis && analysis.diags.length ? ` (${analysis.diags.length})` : ""}`],
                ["classes", `Classes${analysis && analysis.classes.length ? ` (${analysis.classes.length})` : ""}`],
                ["step", `Step${analysis && analysis.steps.length ? ` (${analysis.steps.length})` : ""}`],
                ["machines", `Machines${machines.length ? ` (${machines.length})` : ""}`],
              ] as const
            ).map(([key, label]) => (
              <button
                key={key}
                role="tab"
                aria-selected={view === key}
                className={view === key ? "" : "ghost"}
                onClick={() => setView(key)}
              >
                {label}
              </button>
            ))}
          </div>

          {!analysis && <p className="dim quiz-note">Asking the compiler…</p>}

          {analysis && view === "types" && (
            <>
              <p className="dim quiz-note">
                Every type alias and interface without type parameters, fully expanded — what{" "}
                <code>Partial&lt;Omit&lt;…&gt;&gt;</code> actually is. Then every top-level value.
              </p>
              {analysis.nevers.length > 0 && (
                <div style={{ margin: "6px 0" }}>
                  {analysis.nevers.map((n) => (
                    <div key={n.line} className={`assertion ${n.ok ? "ok" : "bad"}`}>
                      {n.ok ? (
                        <>
                          ✓ line {n.line}: <strong>exhaustive</strong> — every case is handled, so the leftover is{" "}
                          <code>never</code>.
                        </>
                      ) : (
                        <>
                          ✗ line {n.line}: <strong>a case is missing</strong> — {n.message}
                        </>
                      )}
                    </div>
                  ))}
                </div>
              )}
              {analysis.types.length === 0 && <p className="dim quiz-note">No type declarations yet.</p>}
              {analysis.types.map((r) => (
                <TypeRow key={"t" + r.label} row={r} />
              ))}
              {analysis.values.length > 0 && <div className="io-label mt-2">Values</div>}
              {analysis.values.map((r) => (
                <TypeRow key={"v" + r.label} row={r} />
              ))}
            </>
          )}

          {view === "machines" && (
            <>
              <p className="dim quiz-note">
                A union of string-literal states, with its moves read from a transition table (
                <code>{"{ draft: [\"review\"], … }"}</code>) or from a <code>switch</code> whose cases return
                states. The ringed state is the start; dashed states have no way out; red ones cannot be reached from
                the start.
              </p>
              {machines.length === 0 && (
                <p className="dim quiz-note">
                  No state machine found. Declare <code>type Status = "draft" | "review" | "live";</code> and a
                  table <code>{"const NEXT: Record<Status, readonly Status[]> = { … }"}</code>, or a{" "}
                  <code>switch</code> over a status that returns the next one.
                </p>
              )}
              {machines.map((m) => {
                const { terminal, unreachable } = analyseMachine(m);
                return (
                  <div key={m.name} className="card" style={{ margin: "8px 0", padding: "8px 10px" }}>
                    <strong>
                      <code>{m.name}</code>
                    </strong>{" "}
                    <span className="dim quiz-note">
                      {m.states.length} states · {m.edges.length} transitions · from a {m.via}
                    </span>
                    <StateDiagram machine={m} />
                    <div className="quiz-note">
                      {m.edges.map(([a, b]) => `${a} → ${b}`).join(" · ")}
                    </div>
                    {terminal.length > 0 && (
                      <div className="quiz-note">
                        No way out: <code>{terminal.join(", ")}</code>
                      </div>
                    )}
                    {unreachable.length > 0 && (
                      <div className="quiz-note c-bad">
                        Unreachable from <code>{m.states[0]}</code>: <code>{unreachable.join(", ")}</code>
                      </div>
                    )}
                  </div>
                );
              })}
            </>
          )}

          {analysis && view === "step" && (
            <>
              <p className="dim quiz-note">
                For every <code>type X = F&lt;…&gt;</code> where <code>F</code> is a conditional type: the checked
                argument split into its union members, and for each one the branch it takes, what every{" "}
                <code>infer</code> binds, and its result. The answers come from the compiler itself.
              </p>
              {analysis.steps.length === 0 && (
                <p className="dim quiz-note">
                  No applications to step. Declare a conditional type, e.g.{" "}
                  <code>type ElementOf&lt;T&gt; = T extends (infer E)[] ? E : never;</code>, then apply it:{" "}
                  <code>type X = ElementOf&lt;string[] | number&gt;;</code>
                </p>
              )}
              {analysis.steps.map((st) => (
                <div key={st.name} className="card" style={{ margin: "8px 0", padding: "8px 10px" }}>
                  <div>
                    <strong>
                      <code>{st.name}</code>
                    </strong>{" "}
                    = <code>{st.application}</code>
                  </div>
                  <div className="dim quiz-note" style={{ margin: "4px 0" }}>
                    <code>{st.cond.check}</code> extends <code>{st.cond.ext}</code> ? <code>{st.cond.yes}</code> :{" "}
                    <code>{st.cond.no}</code>
                  </div>
                  {st.arg !== null ? (
                    <div className="quiz-note" style={{ margin: "4px 0" }}>
                      1. <code>{st.cond.check}</code> is a bare type parameter, so the conditional{" "}
                      <strong>distributes</strong> over <code>{st.arg}</code> —{" "}
                      {st.members.length === 0 ? (
                        <>
                          which is <code>never</code>: no members, so the result is <code>never</code>.
                        </>
                      ) : (
                        <>{st.members.length} member{st.members.length === 1 ? "" : "s"}, each checked on its own:</>
                      )}
                    </div>
                  ) : (
                    <div className="quiz-note" style={{ margin: "4px 0" }}>
                      1. <code>{st.cond.check}</code> is not a bare type parameter, so the whole argument is checked
                      at once (no distribution):
                    </div>
                  )}
                  {st.members.map((m, i) => (
                    <div key={i} className="playground-row flex-wrap">
                      <span className="playground-label">
                        <code>{m.member}</code>
                      </span>
                      <span className="quiz-note">
                        {m.branch === "true" ? (
                          <span className="c-good">matches → true branch</span>
                        ) : m.branch === "false" ? (
                          <span className="c-bad">no match → false branch</span>
                        ) : (
                          <span>both branches ({m.branch})</span>
                        )}
                        {m.infers.map((b) => (
                          <span key={b.name}>
                            {" "}
                            · <code>{b.name}</code> = <code>{b.type}</code>
                          </span>
                        ))}{" "}
                        → <code className="playground-type">{m.result}</code>
                      </span>
                    </div>
                  ))}
                  <div className="quiz-note mt-1">
                    {st.arg !== null && st.members.length > 1 ? "2. The results, joined into one union" : "2. Result"}:{" "}
                    <code className="playground-type">{st.total}</code>
                  </div>
                </div>
              ))}
            </>
          )}

          {analysis && view === "narrowing" && (
            <>
              <div className="row" style={{ gap: 8, alignItems: "center", margin: "8px 0" }}>
                <label className="dim quiz-note" htmlFor="pg-focus">
                  Variable
                </label>
                <input
                  id="pg-focus"
                  value={focus}
                  onChange={(e) => setFocus(e.target.value.trim())}
                  style={{ width: 140, fontFamily: "var(--font-mono)" }}
                />
              </div>
              <p className="dim quiz-note">
                The type of <code>{focus || "…"}</code> at every place it appears — watch it narrow after each
                check.
              </p>
              {analysis.narrowing.length === 0 && (
                <p className="dim quiz-note">No uses of that name in the code.</p>
              )}
              {analysis.narrowing.map((r, i) => (
                <TypeRow key={i} row={r} />
              ))}
            </>
          )}

          {analysis && view === "js" && (
            <>
              <p className="dim quiz-note">
                Types are erased before anything runs: this is (up to spacing) the JavaScript Node executes.
                Anything that is not here — interfaces, annotations, <code>satisfies</code>, <code>as</code> — has
                no effect at runtime.
              </p>
              <pre className="code-output playground-js">{analysis.js || "(nothing emitted)"}</pre>
            </>
          )}

          {analysis && view === "classes" && (
            <>
              <p className="dim quiz-note">
                Every class in the file: what it extends and implements, and its members — <code>+</code> public,{" "}
                <code>#</code> protected, <code>-</code> private (<code>#field</code> or <code>private</code>), and{" "}
                <u>underlined</u> for static.
              </p>
              {analysis.classes.length === 0 && <p className="dim quiz-note">No classes in this file.</p>}
              <div className="class-diagram">
                {analysis.classes.map((c) => (
                  <div key={c.name} className="class-box">
                    <div className="class-name">
                      {c.abstract ? <em>«abstract» {c.name}</em> : <strong>{c.name}</strong>}
                    </div>
                    {(c.extends || c.implements.length > 0) && (
                      <div className="class-heritage">
                        {c.extends && <>▷ extends {c.extends}</>}
                        {c.extends && c.implements.length > 0 && <br />}
                        {c.implements.length > 0 && <>⇢ implements {c.implements.join(", ")}</>}
                      </div>
                    )}
                    {c.members.map((m) => (
                      <div key={m.kind + m.name} className="class-member">
                        <code>{m.visibility}</code>{" "}
                        <span style={{ textDecoration: m.isStatic ? "underline" : undefined }}>
                          {m.name}
                          {m.kind === "method" || m.kind === "constructor" ? "()" : ""}
                        </span>{" "}
                        <span className="dim">{m.kind}</span>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </>
          )}

          {view === "compiler" && (
            <>
              <p className="dim quiz-note">
                Flip a flag and watch errors appear and disappear. <strong>Run</strong> uses the judge&rsquo;s
                settings: <code>strict</code>, plus <code>noUncheckedIndexedAccess</code> when it is ticked.
              </p>
              {FLAG_INFO.map((f) => (
                <label key={f.key} style={{ display: "flex", gap: 8, alignItems: "baseline", fontSize: 13, margin: "4px 0" }}>
                  <input
                    type="checkbox"
                    checked={!!flags[f.key]}
                    onChange={(e) => setFlags({ ...flags, [f.key]: e.target.checked })}
                  />
                  <span>
                    <code>{f.label}</code> <span className="dim">— {f.note}</span>
                  </span>
                </label>
              ))}
              <div className="io-label mt-2">
                {analysis ? `${analysis.diags.length} error${analysis.diags.length === 1 ? "" : "s"}` : "Errors"}
              </div>
              {analysis?.diags.map((d, i) => (
                <div key={i} className="quiz-note" style={{ margin: "4px 0" }}>
                  <span className="badge">line {d.line}</span> <code>TS{d.code}</code> {d.message}
                </div>
              ))}
              {errorText && <TsErrorLinks text={errorText} />}
              <div className="io-label mt-3">
                tsconfig explorer — eight small programs under these flags
              </div>
              {samples.length === 0 && <p className="dim quiz-note">Checking…</p>}
              {samples.map((r) => (
                <div key={r.title} className={`assertion ${r.ok ? "ok" : "bad"}`}>
                  {r.ok ? "✓ compiles" : "✗ rejected"} — <strong>{r.title}</strong>{" "}
                  <span className="dim">(turned on by <code>{r.flag}</code>)</span>
                  {!r.ok && <div className="dim quiz-note">{r.first}</div>}
                </div>
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function TypeRow({ row }: { row: Row }) {
  return (
    <div className="playground-row">
      <span className="playground-label">
        {row.line !== undefined && <span className="badge">line {row.line}</span>} <code>{row.label}</code>
      </span>
      <code className="playground-type">{row.type}</code>
    </div>
  );
}

type Monaco = NonNullable<ReturnType<typeof useMonaco>>;
type NavItem = {
  text: string;
  kind: string;
  kindModifiers?: string;
  childItems?: NavItem[];
  nameSpan?: { start: number };
  spans?: { start: number }[];
};

/** Check the explorer's samples under the current options. */
async function checkSamples(monaco: Monaco): Promise<SampleResult[]> {
  const getWorker = await monaco.languages.typescript.getTypeScriptWorker();
  const out: SampleResult[] = [];
  for (let i = 0; i < SAMPLES.length; i++) {
    const sample = SAMPLES[i]!;
    const uri = monaco.Uri.parse(`file:///playground/samples/s${i}.ts`);
    const model = monaco.editor.getModel(uri) ?? monaco.editor.createModel(sample.code, "typescript", uri);
    const client = await getWorker(uri);
    const diags = await client.getSemanticDiagnostics(uri.toString());
    const first = diags[0];
    out.push({
      title: sample.title,
      flag: sample.flag,
      ok: diags.length === 0,
      first: first ? `TS${first.code}: ${flatten(first.messageText)}` : "",
    });
    void model;
  }
  return out;
}

async function analyse(monaco: Monaco, focus: string): Promise<Analysis> {
  const mainUri = monaco.Uri.parse(MAIN);
  const probeUri = monaco.Uri.parse(PROBE);
  const main = monaco.editor.getModel(mainUri);
  if (!main) throw new Error("no model yet");
  const getWorker = await monaco.languages.typescript.getTypeScriptWorker();
  const client = await getWorker(mainUri);
  const src = main.getValue();
  const quick = async (c: typeof client, file: string, offset: number) => {
    const info = await c.getQuickInfoAtPosition(file, offset);
    return info ? (info.displayParts ?? []).map((p: { text: string }) => p.text).join("") : "";
  };

  // Types, expanded through probes in a scratch copy of the file.
  const names = expandableTypes(src);
  const { text, offsets } = probeSource(src, names);
  const probe = monaco.editor.getModel(probeUri) ?? monaco.editor.createModel(text, "typescript", probeUri);
  if (probe.getValue() !== text) probe.setValue(text);
  const probeClient = await getWorker(probeUri);
  const types: Row[] = [];
  for (let i = 0; i < names.length; i++) {
    types.push({ label: names[i]!, type: probeType(await quick(probeClient, PROBE, offsets[i]!)) });
  }

  // M5-01: step conditional-type applications, in two rounds of probes —
  // first each checked argument's members, then each member's branch, infer
  // bindings and result.
  const steps: Stepped[] = [];
  const aliases = conditionalAliases(src);
  const apps = applications(src, new Set(aliases.keys())).slice(0, 6);
  if (apps.length > 0) {
    const stepUri = monaco.Uri.parse(STEP_PROBE);
    const stepModel = monaco.editor.getModel(stepUri) ?? monaco.editor.createModel("", "typescript", stepUri);
    const plans = apps.map((app, k) => planSteps(app, aliases.get(app.fn)!, k));
    const base =
      src.replace(/\s*$/, "") + "\n\n" + STEP_HELPER + "\n" + plans.flatMap((pl) => pl.helpers).join("\n") + "\n";
    const ask = async (questions: string[]) => {
      let text = base;
      const at: number[] = [];
      questions.forEach((q, i) => {
        at.push(text.length + "declare const ".length);
        text += `declare const __pq_${i}: ${q};\n`;
      });
      if (stepModel.getValue() !== text) stepModel.setValue(text);
      const c = await getWorker(stepUri);
      const out: string[] = [];
      for (const off of at) out.push(probeType(await quick(c, STEP_PROBE, off)));
      return out;
    };
    const argQs = plans.map((pl) => (pl.distributesOver === null ? "never" : `__PgId<${pl.app.args[pl.distributesOver]}>`));
    const argTypes = await ask(argQs);
    const rows = plans.map((pl, k) => {
      const members =
        pl.distributesOver === null ? [null] : splitUnion(argTypes[k] ?? "").slice(0, 12);
      return { pl, members };
    });
    const qs: string[] = [];
    const index: { k: number; member: string | null; branch: number; infers: number[]; result: number }[] = [];
    rows.forEach(({ pl, members }, k) => {
      for (const member of members) {
        const args = member === null ? pl.app.args.join(", ") : withArg(pl.app.args, pl.distributesOver!, member);
        const branch = qs.push(`${pl.branchHelper}<${args}>`) - 1;
        const infers = pl.infers.map((n) => qs.push(`__PgId<${pl.inferHelper(n)}<${args}>>`) - 1);
        const result = qs.push(`__PgId<${pl.app.fn}<${args}>>`) - 1;
        index.push({ k, member, branch, infers, result });
      }
      // The application, not the alias's name — asking about `Mixed` prints `Mixed`.
      qs.push(`__PgId<${pl.app.fn}<${pl.app.args.join(", ")}>>`);
    });
    const answers = await ask(qs);
    let cursor = 0;
    rows.forEach(({ pl, members }, k) => {
      const mine = index.filter((x) => x.k === k);
      cursor += mine.reduce((n, x) => n + 2 + x.infers.length, 0);
      const alias = aliases.get(pl.app.fn)!;
      steps.push({
        name: pl.app.name,
        application: `${pl.app.fn}<${pl.app.args.join(", ")}>`,
        arg: pl.distributesOver === null ? null : argTypes[k] ?? "",
        cond: alias.cond,
        members: mine.map((x) => ({
          member: x.member ?? pl.app.args.join(", "),
          branch: answers[x.branch] ?? "",
          infers: pl.infers.map((n, i) => ({ name: n, type: answers[x.infers[i]!] ?? "" })),
          result: answers[x.result] ?? "",
        })),
        total: answers[cursor] ?? "",
      });
      cursor += 1;
      void members;
    });
  }

  // Top-level values from the navigation tree.
  const values: Row[] = [];
  const tree = (await client.getNavigationTree(MAIN)) as NavItem | undefined;
  for (const item of tree?.childItems ?? []) {
    if (!["const", "let", "var", "function", "class"].includes(item.kind)) continue;
    const start = item.nameSpan?.start ?? item.spans?.[0]?.start;
    if (start === undefined) continue;
    const shown = await quick(client, MAIN, start);
    values.push({ label: item.text, type: shown.replace(/^(const|let|var|function|class)\s+/, ""), line: lineOf(src, start) });
  }

  // One variable, at every use.
  const narrowing: Row[] = [];
  for (const offset of occurrences(src, focus)) {
    const shown = await quick(client, MAIN, offset);
    const line = lineOf(src, offset);
    narrowing.push({
      label: (src.split("\n")[line - 1] ?? "").trim().slice(0, 60),
      type: probeType(shown.replace(/^\((parameter|local var|property)\)\s*/, "")),
      line,
    });
  }

  const emit = await client.getEmitOutput(MAIN);
  // Every playground file is treated as a module, so the emitter adds an empty
  // `export {}`; it is not part of what the learner wrote.
  const js = ((emit.outputFiles ?? []).find((f: { name: string }) => f.name.endsWith(".js"))?.text ?? "").replace(
    /\n?export \{\};\s*$/,
    "\n"
  );

  const raw = [
    ...(await client.getSyntacticDiagnostics(MAIN)),
    ...(await client.getSemanticDiagnostics(MAIN)),
  ];
  const diags: Diag[] = raw.map((d: { code: number; start?: number; messageText: unknown }) => ({
    code: d.code,
    line: lineOf(src, d.start ?? 0),
    message: flatten(d.messageText),
  }));

  // M3-02: `const x: never = …` / `satisfies never` lines — exhaustive when
  // the compiler has nothing to say about them.
  const nevers: NeverCheck[] = [];
  src.split("\n").forEach((text, i) => {
    if (!/:\s*never\s*=|satisfies\s+never\b/.test(text)) return;
    const line = i + 1;
    const hit = diags.find((d) => d.line === line);
    nevers.push({ line, ok: !hit, message: hit ? hit.message : "" });
  });

  // M6-04: classes from the navigation tree, heritage from the source.
  const classes: ClassInfo[] = [];
  const walk = (items: NavItem[]) => {
    for (const item of items) {
      if (item.kind === "class") {
        const head = new RegExp(
          `class\\s+${item.text}(?:<[^>]*>)?\\s*(?:extends\\s+([\\w.]+)(?:<[^>]*>)?)?\\s*(?:implements\\s+([^{]+))?\\{`
        ).exec(src);
        classes.push({
          name: item.text,
          abstract: (item.kindModifiers ?? "").includes("abstract"),
          extends: head?.[1] ?? "",
          implements: (head?.[2] ?? "").split(",").map((x) => x.trim()).filter(Boolean),
          members: (item.childItems ?? [])
            .filter((m) => ["property", "method", "getter", "setter", "constructor"].includes(m.kind))
            .map((m) => {
              const mods = m.kindModifiers ?? "";
              return {
                name: m.text,
                kind: m.kind,
                visibility: m.text.startsWith("#") || mods.includes("private") ? "-" : mods.includes("protected") ? "#" : "+",
                isStatic: mods.includes("static"),
              };
            }),
        });
      }
      walk(item.childItems ?? []);
    }
  };
  walk(tree?.childItems ?? []);

  return { steps, types, values, narrowing, js, diags, classes, nevers };
}
