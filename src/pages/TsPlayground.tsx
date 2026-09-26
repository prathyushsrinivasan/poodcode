// The TypeScript playground (TS_MASTERY_ROADMAP X-67, with X-64, X-65, M3-01
// and M5-01): a scratch file, and four views of it computed by the editor's own
// TypeScript service —
//   * Types      every declared type fully expanded, every top-level value's type
//   * Narrowing  one variable's type at each place it is used
//   * What runs  the JavaScript the types erase to
//   * Compiler   strictness flags to flip, and the errors they produce
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

const MAIN = "file:///playground/main.ts";
const PROBE = "file:///playground/__probe.ts";
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
type Analysis = {
  types: Row[];
  values: Row[];
  narrowing: Row[];
  js: string;
  diags: Diag[];
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
  const [view, setView] = useState<"types" | "narrowing" | "js" | "compiler">("types");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [stdin, setStdin] = useState("");
  const [run, setRun] = useState<ProcOut | null>(null);
  const [running, setRunning] = useState(false);
  const monaco = useMonaco();
  const seq = useRef(0);

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
    },
    [monaco]
  );

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

      <div className="row" style={{ gap: 6, flexWrap: "wrap", marginBottom: 10 }}>
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
          <div className="row" style={{ gap: 8, marginTop: 8, alignItems: "flex-start" }}>
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
            <div className="card" style={{ marginTop: 8 }}>
              <div className="io-label">
                Output {run.exit_code !== 0 && run.exit_code !== null && `· exit ${run.exit_code}`}{" "}
                {run.timed_out && "· timed out"}
              </div>
              <pre className="code-output" style={{ margin: 0 }}>
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
          <div className="row" style={{ gap: 4, flexWrap: "wrap" }} role="tablist">
            {(
              [
                ["types", "Types"],
                ["narrowing", "Narrowing"],
                ["js", "What runs"],
                ["compiler", `Compiler${analysis && analysis.diags.length ? ` (${analysis.diags.length})` : ""}`],
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
              {analysis.types.length === 0 && <p className="dim quiz-note">No type declarations yet.</p>}
              {analysis.types.map((r) => (
                <TypeRow key={"t" + r.label} row={r} />
              ))}
              {analysis.values.length > 0 && <div className="io-label" style={{ marginTop: 10 }}>Values</div>}
              {analysis.values.map((r) => (
                <TypeRow key={"v" + r.label} row={r} />
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
              <div className="io-label" style={{ marginTop: 10 }}>
                {analysis ? `${analysis.diags.length} error${analysis.diags.length === 1 ? "" : "s"}` : "Errors"}
              </div>
              {analysis?.diags.map((d, i) => (
                <div key={i} className="quiz-note" style={{ margin: "4px 0" }}>
                  <span className="badge">line {d.line}</span> <code>TS{d.code}</code> {d.message}
                </div>
              ))}
              {errorText && <TsErrorLinks text={errorText} />}
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

  // Top-level values from the navigation tree.
  const values: Row[] = [];
  const tree = await client.getNavigationTree(MAIN);
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

  return { types, values, narrowing, js, diags };
}
