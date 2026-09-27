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
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../../api";
import type { Exercise, JudgeReport, ProcOut, Project, ProjectModule, TestCase } from "../../types";
import { CodeEditor } from "../../components/CodeEditor";
import { ErrorText, JudgeFeedback as Feedback, VerdictPanel } from "../../components/exercise";
import { pairExchanges, sampleRequests } from "../../lib/workbench";
import { Badge, Button, Card, CardHeader, Chip, ConfirmDialog, EmptyState, Icon, PageHeader } from "../../components/ui";
import { useCrumb } from "../../store";

/** Where the judged programs' given replayer starts. Mirrors `_GIVEN_MARKER` in
 * tools/projects_track.py — a program containing it boots a server. */
const REPLAYER_MARKER = "// ---- request replayer (given";

/** Where the exercise cards keep a learner's code, per exercise. Mirrors
 * `storeKey` in components/exercise/ExerciseCard.tsx. */
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

const statusClass = (s: number) => (s >= 500 ? "is-bad" : s >= 400 ? "is-warn" : s >= 300 ? "is-accent" : "is-good");

export default function ProjectWorkbench({ project }: { project: Project }) {
  useCrumb(project.title, "Workbench");
  const [params, setParams] = useSearchParams();
  const builds = useMemo(
    () => project.modules.filter((m): m is ProjectModule & { final_build: Exercise } =>
      m.authored && m.final_build !== null
    ),
    [project]
  );
  const latest = builds[builds.length - 1];

  /** A load waiting on confirmation, because it would overwrite unsaved code. */
  const [pendingLoad, setPendingLoad] = useState<{
    module: ProjectModule & { final_build: Exercise };
    which: "mine" | "reference" | "starter";
  } | null>(null);
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
      setPendingLoad({ module: m, which });
      return;
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
        <PageHeader eyebrow={<Link to={`/projects/${project.key}`}>{project.title}</Link>} title="Workbench" />
        <EmptyState icon="build" title="No module of this project has a build to load yet." />
      </div>
    );
  }

  return (
    <div className="page workbench">
      <PageHeader
        eyebrow={<Link to={`/projects/${project.key}`}>{project.title}</Link>}
        title="Workbench"
        subtitle={
          <>
            Load a module build, change it, and throw your own {isServer ? "requests" : "input"} at it. It runs through the
            same judge as the exercises — type-check first, at <code>strict</code> + <code>noUncheckedIndexedAccess</code>{" "}
            — and nothing here is graded.
          </>
        }
        actions={current && <Badge icon="build">on the bench: module {current.number}</Badge>}
      />

      {loadTarget && loadTarget.key !== bench.moduleKey && (
        <Card tone="accent" className="unit-block">
          <div className="bench-row">
            <span className="bench-grow">
              Load <strong>module {loadTarget.number}'s build</strong> onto the workbench?
              {bench.code.trim() && " It replaces the code there now."}
            </span>
            <Button variant="primary" onClick={() => load(loadTarget, "mine")}>
              {readDraft(loadTarget.final_build) ? "Load my version" : "Load the reference"}
            </Button>
            <Button variant="ghost" onClick={clearLoadParam}>
              Keep what is there
            </Button>
          </div>
        </Card>
      )}

      <Card className="unit-block">
        <div className="bench-row">
          <label className="history-compare">
            <span className="dim">Load</span>
            <select value={pick} onChange={(e) => setPick(e.target.value)}>
              {builds.map((m) => (
                <option key={m.key} value={m.key}>
                  module {m.number} — {m.title}
                </option>
              ))}
            </select>
          </label>
          {picked && (
            <>
              <Button
                onClick={() => confirmLoad(picked, "mine")}
                disabled={!pickedDraft}
                title={pickedDraft ? "Your own attempt at this module's build, as you last left it" : "You have not written this module's build yet"}
              >
                My version
              </Button>
              <Button variant="ghost" onClick={() => confirmLoad(picked, "reference")}>
                Reference
              </Button>
              <Button variant="ghost" onClick={() => confirmLoad(picked, "starter")} title="The build with its blank still in it">
                Starter
              </Button>
            </>
          )}
          <span className="spacer" />
          {current && (
            <Link className="btn ghost" to={`/projects/${project.key}/${current.key}`} title={`Open module ${current.number}`}>
              Module {current.number} <Icon name="forward" size={14} />
            </Link>
          )}
        </div>
      </Card>

      <div className="exercise-editor bench-editor">
        <CodeEditor language="typescript" value={bench.code} onChange={(code) => setBench((b) => ({ ...b, code }))} onRun={run} />
      </div>

      <Card className="unit-block">
        <CardHeader
          level={2}
          title={
            <label htmlFor="bench-stdin" className="io-label bench-label">
              {isServer ? "Request script — one per line: METHOD /path [json body]" : "stdin"}
            </label>
          }
          actions={
            current &&
            current.final_build.tests[0] && (
              <Button
                variant="ghost"
                size="sm"
                icon="reset"
                onClick={() => setBench({ ...bench, stdin: current.final_build.tests[0]!.input })}
                title="Put back the request script from the module's own test"
              >
                Module {current.number}'s script
              </Button>
            )
          }
        />
        <textarea
          id="bench-stdin"
          className="bench-stdin"
          value={bench.stdin}
          onChange={(e) => setBench({ ...bench, stdin: e.target.value })}
          rows={Math.min(12, Math.max(4, bench.stdin.split("\n").length + 1))}
          spellCheck={false}
          placeholder={isServer ? 'GET /todos\nPOST /todos {"title":"Buy milk"}' : "1 + 2"}
        />
        {isServer && project.endpoints.length > 0 && (
          <div className="bench-samples">
            <span className="faint cell-small">Add:</span>
            {sampleRequests(project).map((r) => (
              <Chip key={r} className="mono" onClick={() => addRequest(r)} title="Append this request to the script">
                {r}
              </Chip>
            ))}
          </div>
        )}
      </Card>

      <div className="exercise-actions unit-block">
        <Button variant="primary" icon="run" onClick={run} loading={running === "run"} disabled={!!running} shortcut="Ctrl+Enter">
          {running === "run" ? "Running…" : "Run"}
        </Button>
        {current && (
          <Button
            variant="ghost"
            icon="checklist"
            onClick={check}
            loading={running === "check"}
            disabled={!!running}
            title={`Run module ${current.number}'s build tests against what is on the bench. Nothing is marked solved.`}
          >
            {running === "check" ? "Checking…" : `Check against module ${current.number}'s tests`}
          </Button>
        )}
      </div>

      {compileError && (
        <VerdictPanel tone="bad" title="Didn't compile — nothing ran">
          <ErrorText>{compileError}</ErrorText>
        </VerdictPanel>
      )}

      {report && <Feedback report={report} />}

      {out && (
        <Card tone={out.exit_code === 0 && !out.timed_out ? undefined : "bad"} className="unit-block">
          <CardHeader
            level={2}
            title={exchanges ? `${exchanges.length} requests, ${exchanges.length} replies` : "Output"}
            actions={
              <span className="dim mono cell-small">
                {out.timed_out ? "timed out" : `exit ${out.exit_code ?? "?"} · ${out.runtime_ms} ms`}
              </span>
            }
          />

          {out.timed_out && (
            <p className="is-bad">
              The program never finished.{" "}
              {isServer ? (
                <>
                  On a server program that almost always means a request was never answered — a route with no{" "}
                  <code>send</code> or <code>res.end</code>, or a handler with no fall-through. Module 4 step 3 is the one
                  about this.
                </>
              ) : (
                "Look for a loop whose condition never becomes false."
              )}
            </p>
          )}

          {exchanges ? (
            <div className="table-card">
              <table className="data static">
                <thead>
                  <tr>
                    <th scope="col">Request</th>
                    <th scope="col">Status</th>
                    <th scope="col">Body</th>
                  </tr>
                </thead>
                <tbody>
                  {exchanges.map((x, i) => (
                    <tr key={i}>
                      <td className="mono nowrap cell-small">{x.request}</td>
                      <td className={`mono status-code ${statusClass(x.status)}`}>{x.status}</td>
                      <td className="mono cell-small break-all">{x.body || <span className="faint">(empty)</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            !out.timed_out && <pre className="verdict-pre">{out.stdout || <span className="faint">(nothing on stdout)</span>}</pre>
          )}

          {out.stderr.trim() && (
            <details className="verdict-details" open={out.exit_code !== 0}>
              <summary className="dim cell-small">
                stderr{isServer ? " — including anything the replayer's error boundary caught" : ""}
              </summary>
              <pre className="verdict-pre">{out.stderr}</pre>
            </details>
          )}
          {out.truncated && <p className="exercise-note">Output was truncated.</p>}
        </Card>
      )}
      <ConfirmDialog
        open={pendingLoad !== null}
        onClose={() => setPendingLoad(null)}
        onConfirm={() => {
          if (pendingLoad) load(pendingLoad.module, pendingLoad.which);
          setPendingLoad(null);
        }}
        title="Replace the code on the workbench?"
        consequence={
          pendingLoad && (
            <>
              This loads module {pendingLoad.module.number}'s{" "}
              {pendingLoad.which === "mine"
                ? "build (your version)"
                : pendingLoad.which === "reference"
                  ? "reference build"
                  : "starter"}{" "}
              over what is on the workbench now. What is there has not been saved anywhere else, so it will be lost.
            </>
          )
        }
        confirmLabel="Replace it"
      />
    </div>
  );
}
