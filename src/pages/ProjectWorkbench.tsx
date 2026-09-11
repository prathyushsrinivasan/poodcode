// Workbench — a place to poke at a module build with requests of your own.
//
// Every module ends with a "try it yourself" block of curl commands, which
// assumes Node on the learner's own machine, a terminal, and a server they have
// kept in step with the modules. That is the right end state and a steep first
// step. The judged exercises are the opposite: one fixed request script, graded
// and gone. Neither answers the question a learner actually has halfway through
// a module — "what does my handler do if I send it THIS?".
//
// So: load any module's build — your own attempt, or the reference — edit it,
// write any request script you like, and run it through the same judge the
// exercises use, type-check included. For a server program the replies are
// paired with the requests that produced them, since `201 {…}` on its own line
// is much harder to read than next to the `POST` it answers.
//
// Nothing here is graded or marks anything solved. "Check against the module's
// tests" is there to answer "did my experiment break it?", not to score it.

import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import type { Exercise, JudgeReport, ProcOut, Project, ProjectModule, TestCase } from "../types";
import { CodeEditor } from "../components/CodeEditor";
import { Feedback } from "../components/LearnExercise";
import { Empty } from "../components/common";
import { pairExchanges, sampleRequests } from "../lib/workbench";

/** Where the judged programs' given replayer starts. Mirrors `_GIVEN_MARKER` in
 * tools/projects_track.py — a program containing it boots a server. */
const REPLAYER_MARKER = "// ---- request replayer (given";

/** Where the exercise cards keep a learner's code, per exercise. Mirrors
 * `storeKey` in components/LearnExercise.tsx. */
const draftKey = (exerciseId: string) => `poodcode:learn-ex:${exerciseId}`;
const benchKey = (projectKey: string) => `poodcode:workbench:${projectKey}`;

interface BenchState {
  moduleKey: string;
  code: string;
  stdin: string;
}

function readBench(projectKey: string): BenchState | null {
  try {
    const raw = localStorage.getItem(benchKey(projectKey));
    if (!raw) return null;
    const v = JSON.parse(raw) as Partial<BenchState>;
    if (typeof v.code !== "string" || typeof v.stdin !== "string") return null;
    return { moduleKey: v.moduleKey ?? "", code: v.code, stdin: v.stdin };
  } catch {
    return null;
  }
}

function writeBench(projectKey: string, s: BenchState) {
  try {
    localStorage.setItem(benchKey(projectKey), JSON.stringify(s));
  } catch {
    // Storage full or blocked: the bench still works, it just won't persist.
  }
}

/** The learner's own draft of an exercise, if they have written one — a
 * starter still holding its blank does not count. */
function readDraft(ex: Exercise): string | null {
  try {
    const d = localStorage.getItem(draftKey(ex.id));
    return d && d !== ex.starter && !d.includes("____") ? d : null;
  } catch {
    return null;
  }
}

const statusColor = (s: number) =>
  s >= 500 ? "var(--bad)" : s >= 400 ? "var(--warn)" : s >= 300 ? "var(--accent)" : "var(--good)";

export default function ProjectWorkbench({ project }: { project: Project }) {
  const nav = useNavigate();
  const [params, setParams] = useSearchParams();
  const builds = useMemo(
    () => project.modules.filter((m): m is ProjectModule & { final_build: Exercise } =>
      m.authored && m.final_build !== null
    ),
    [project]
  );
  const latest = builds[builds.length - 1];

  const [bench, setBench] = useState<BenchState>(() => {
    const saved = readBench(project.key);
    if (saved) return saved;
    return latest
      ? {
          moduleKey: latest.key,
          code: latest.final_build.solution,
          stdin: latest.final_build.tests[0]?.input ?? "",
        }
      : { moduleKey: "", code: "", stdin: "" };
  });
  const [pick, setPick] = useState(bench.moduleKey || latest?.key || "");
  const [out, setOut] = useState<ProcOut | null>(null);
  const [compileError, setCompileError] = useState("");
  const [report, setReport] = useState<JudgeReport | null>(null);
  const [running, setRunning] = useState<"" | "run" | "check">("");

  useEffect(() => writeBench(project.key, bench), [project.key, bench]);

  // `?load=<module>` — a module page's "Open in the workbench" link. It never
  // silently replaces code already on the bench; it asks first (see below).
  const loadParam = params.get("load");
  const loadTarget = builds.find((m) => m.key === loadParam) ?? null;
  const clearLoadParam = () =>
    setParams(
      (prev) => {
        const next = new URLSearchParams(prev);
        next.delete("load");
        return next;
      },
      { replace: true }
    );

  const current = builds.find((m) => m.key === bench.moduleKey) ?? null;
  const picked = builds.find((m) => m.key === pick) ?? null;
  const pickedDraft = picked ? readDraft(picked.final_build) : null;
  const isServer = bench.code.includes(REPLAYER_MARKER);
  const exchanges = out && !out.timed_out ? pairExchanges(bench.stdin, out.stdout) : null;

  function clearResults() {
    setOut(null);
    setCompileError("");
    setReport(null);
  }

  function load(m: ProjectModule & { final_build: Exercise }, which: "mine" | "reference" | "starter") {
    const code =
      which === "reference"
        ? m.final_build.solution
        : which === "starter"
          ? m.final_build.starter
          : (readDraft(m.final_build) ?? m.final_build.solution);
    setBench({ moduleKey: m.key, code, stdin: m.final_build.tests[0]?.input ?? "" });
    setPick(m.key);
    clearResults();
    // Any load answers a pending `?load=` offer; leaving the parameter behind
    // would re-offer it the next time the bench holds a different module.
    if (loadParam) clearLoadParam();
  }

  // Loading over code the learner has edited is the one destructive action on
  // the page, so it says what it is about to replace.
  function confirmLoad(m: ProjectModule & { final_build: Exercise }, which: "mine" | "reference" | "starter") {
    // Code that also exists somewhere else — the reference, the starter, or the
    // learner's own draft, which the exercise card keeps — is not lost by a load.
    const recoverable =
      current !== null &&
      [current.final_build.solution, current.final_build.starter, readDraft(current.final_build)].includes(
        bench.code
      );
    if (bench.code.trim() && !recoverable) {
      const ok = window.confirm(
        `Replace the code on the workbench with module ${m.number}'s ` +
          `${which === "mine" ? "build (your version)" : which === "reference" ? "reference build" : "starter"}?\n\n` +
          "What is there now will be lost."
      );
      if (!ok) return;
    }
    load(m, which);
  }

  async function run() {
    setRunning("run");
    clearResults();
    try {
      setOut(await api.runScratch(null, "typescript", bench.code, bench.stdin, "strict+indexed"));
    } catch (e) {
      // run_scratch rejects with the compiler's message when the type-check fails.
      setCompileError(String((e as { message?: string })?.message ?? e));
    } finally {
      setRunning("");
    }
  }

  async function check() {
    if (!current) return;
    setRunning("check");
    clearResults();
    const cases: TestCase[] = current.final_build.tests.map((t, i) => ({
      id: 0,
      problem_id: 0,
      kind: "example",
      name: `Test ${i + 1}`,
      input: t.input,
      expected_output: t.output,
      ordering: i,
    }));
    try {
      setReport(
        await api.runTests(null, "typescript", bench.code, cases, {
          strictness: current.final_build.strictness,
        })
      );
    } catch (e) {
      setCompileError(String((e as { message?: string })?.message ?? e));
    } finally {
      setRunning("");
    }
  }

  function addRequest(line: string) {
    const s = bench.stdin.replace(/\s+$/, "");
    setBench({ ...bench, stdin: s ? `${s}\n${line}` : line });
  }

  if (builds.length === 0) {
    return (
      <div className="page">
        <button className="ghost" onClick={() => nav(`/projects/${project.key}`)}>
          ← {project.title}
        </button>
        <Empty icon="🧪" text="No module of this project has a build to load yet." />
      </div>
    );
  }

  return (
    <div className="page">
      <div className="row" style={{ marginBottom: 4 }}>
        <button className="ghost" onClick={() => nav(`/projects/${project.key}`)}>
          ← {project.title}
        </button>
        {current && <span className="badge">on the bench: module {current.number}</span>}
      </div>

      <h1 className="page-title" style={{ marginTop: 6 }}>
        Workbench
      </h1>
      <p className="page-sub">
        Load a module build, change it, and throw your own {isServer ? "requests" : "input"} at it.
        It runs through the same judge as the exercises — type-check first, at{" "}
        <code>strict</code> + <code>noUncheckedIndexedAccess</code> — and nothing here is graded.
      </p>

      {loadTarget && loadTarget.key !== bench.moduleKey && (
        <div className="card" style={{ marginBottom: 12, borderColor: "var(--accent)" }}>
          <div className="row" style={{ gap: 8, flexWrap: "wrap", alignItems: "center" }}>
            <span style={{ flex: 1 }}>
              Load <strong>module {loadTarget.number}'s build</strong> onto the workbench?
              {bench.code.trim() && " It replaces the code there now."}
            </span>
            <button
              className="primary"
              onClick={() => load(loadTarget, "mine")}
            >
              {readDraft(loadTarget.final_build) ? "Load my version" : "Load the reference"}
            </button>
            <button className="ghost" onClick={clearLoadParam}>
              Keep what is there
            </button>
          </div>
        </div>
      )}

      <div className="card" style={{ marginBottom: 12 }}>
        <div className="row" style={{ gap: 8, flexWrap: "wrap", alignItems: "center" }}>
          <span className="dim" style={{ fontSize: 13 }}>
            Load
          </span>
          <select value={pick} onChange={(e) => setPick(e.target.value)} aria-label="Module build to load">
            {builds.map((m) => (
              <option key={m.key} value={m.key}>
                module {m.number} — {m.title}
              </option>
            ))}
          </select>
          {picked && (
            <>
              <button
                onClick={() => confirmLoad(picked, "mine")}
                disabled={!pickedDraft}
                title={
                  pickedDraft
                    ? "Your own attempt at this module's build, as you last left it"
                    : "You have not written this module's build yet"
                }
              >
                My version
              </button>
              <button className="ghost" onClick={() => confirmLoad(picked, "reference")}>
                Reference
              </button>
              <button
                className="ghost"
                onClick={() => confirmLoad(picked, "starter")}
                title="The build with its blank still in it"
              >
                Starter
              </button>
            </>
          )}
          <span className="spacer" />
          {current && (
            <button
              className="ghost"
              onClick={() => nav(`/projects/${project.key}/${current.key}`)}
              title={`Open module ${current.number}`}
            >
              Module {current.number} →
            </button>
          )}
        </div>
      </div>

      <div
        style={{
          height: 460,
          border: "1px solid var(--border)",
          borderRadius: 6,
          overflow: "hidden",
          marginBottom: 12,
        }}
      >
        <CodeEditor
          language="typescript"
          value={bench.code}
          onChange={(code) => setBench((b) => ({ ...b, code }))}
          onRun={run}
        />
      </div>

      <div className="card" style={{ marginBottom: 12 }}>
        <div className="row" style={{ marginBottom: 6, alignItems: "baseline" }}>
          <div className="io-label" style={{ margin: 0 }}>
            {isServer ? "Request script — one per line: METHOD /path [json body]" : "stdin"}
          </div>
          <span className="spacer" />
          {current && current.final_build.tests[0] && (
            <button
              className="ghost"
              style={{ padding: "2px 8px", fontSize: 12 }}
              onClick={() => setBench({ ...bench, stdin: current.final_build.tests[0]!.input })}
              title="Put back the request script from the module's own test"
            >
              ↺ module {current.number}'s script
            </button>
          )}
        </div>
        <textarea
          value={bench.stdin}
          onChange={(e) => setBench({ ...bench, stdin: e.target.value })}
          rows={Math.min(12, Math.max(4, bench.stdin.split("\n").length + 1))}
          spellCheck={false}
          placeholder={isServer ? 'GET /todos\nPOST /todos {"title":"Buy milk"}' : "1 + 2"}
          style={{ width: "100%", fontFamily: "var(--font-mono)", fontSize: 13, resize: "vertical" }}
        />
        {isServer && project.endpoints.length > 0 && (
          <div className="row" style={{ gap: 6, flexWrap: "wrap", marginTop: 8 }}>
            <span className="faint" style={{ fontSize: 12 }}>
              Add:
            </span>
            {sampleRequests(project).map((r) => (
              <button
                key={r}
                className="ghost mono"
                style={{ padding: "1px 7px", fontSize: 11.5 }}
                onClick={() => addRequest(r)}
                title="Append this request to the script"
              >
                {r}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="row" style={{ gap: 8, marginBottom: 12 }}>
        <button className="primary" onClick={run} disabled={!!running}>
          {running === "run" ? "Running…" : "▶ Run"}
        </button>
        {current && (
          <button
            className="ghost"
            onClick={check}
            disabled={!!running}
            title={`Run module ${current.number}'s build tests against what is on the bench. Nothing is marked solved.`}
          >
            {running === "check" ? "Checking…" : `Check against module ${current.number}'s tests`}
          </button>
        )}
        <span className="faint" style={{ fontSize: 12, alignSelf: "center" }}>
          Ctrl+Enter runs
        </span>
      </div>

      {compileError && (
        <div className="card" style={{ borderColor: "var(--bad)" }}>
          <div className="io-label" style={{ color: "var(--bad)" }}>
            Didn't compile — nothing ran
          </div>
          <pre style={{ margin: 0, whiteSpace: "pre-wrap", fontSize: 12 }}>{compileError}</pre>
        </div>
      )}

      {report && <Feedback report={report} />}

      {out && (
        <div className="card" style={{ borderColor: out.exit_code === 0 ? "var(--border)" : "var(--bad)" }}>
          <div className="row" style={{ marginBottom: 8 }}>
            <div className="io-label" style={{ margin: 0 }}>
              {exchanges ? `${exchanges.length} requests, ${exchanges.length} replies` : "Output"}
            </div>
            <span className="spacer" />
            <span className="dim mono" style={{ fontSize: 12 }}>
              {out.timed_out ? "timed out" : `exit ${out.exit_code ?? "?"} · ${out.runtime_ms} ms`}
            </span>
          </div>

          {out.timed_out && (
            <p style={{ color: "var(--bad)", marginTop: 0 }}>
              The program never finished.{" "}
              {isServer ? (
                <>
                  On a server program that almost always means a request was never answered — a
                  route with no <code>send</code> or <code>res.end</code>, or a handler with no
                  fall-through. Module 4 step 3 is the one about this.
                </>
              ) : (
                "Look for a loop whose condition never becomes false."
              )}
            </p>
          )}

          {exchanges ? (
            <div style={{ overflowX: "auto" }}>
              <table className="data" style={{ cursor: "default" }}>
                <thead>
                  <tr>
                    <th style={{ cursor: "default" }}>Request</th>
                    <th style={{ cursor: "default" }}>Status</th>
                    <th style={{ cursor: "default" }}>Body</th>
                  </tr>
                </thead>
                <tbody>
                  {exchanges.map((x, i) => (
                    <tr key={i} style={{ cursor: "default" }}>
                      <td className="mono" style={{ fontSize: 12, whiteSpace: "nowrap" }}>
                        {x.request}
                      </td>
                      <td className="mono" style={{ color: statusColor(x.status), fontWeight: 600 }}>
                        {x.status}
                      </td>
                      <td className="mono" style={{ fontSize: 12, wordBreak: "break-all" }}>
                        {x.body || <span className="faint">(empty)</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            !out.timed_out && (
              <pre style={{ margin: 0, whiteSpace: "pre-wrap", fontSize: 12.5 }}>
                {out.stdout || <span className="faint">(nothing on stdout)</span>}
              </pre>
            )
          )}

          {out.stderr.trim() && (
            <details style={{ marginTop: 10 }} open={out.exit_code !== 0}>
              <summary className="dim" style={{ fontSize: 12, cursor: "pointer" }}>
                stderr{isServer ? " — including anything the replayer's error boundary caught" : ""}
              </summary>
              <pre style={{ margin: "6px 0 0", whiteSpace: "pre-wrap", fontSize: 12 }}>{out.stderr}</pre>
            </details>
          )}
          {out.truncated && (
            <p className="faint" style={{ fontSize: 12, margin: "8px 0 0" }}>
              Output was truncated.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
