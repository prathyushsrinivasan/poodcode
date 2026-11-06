import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { api } from "../api";
import { CodeEditor } from "../components/CodeEditor";
import { Markdown } from "../components/Markdown";
import { TestResults } from "../components/TestResults";
import { AtLevel } from "../components/ui/Heading";
import { loadSolvedExercises, markExerciseSolved } from "../lib/learnProgress";
import { useCrumb } from "../store";
import type { JudgeReport } from "../types";
import {
  PYTHON_EXERCISES, PYTHON_MODULES, pythonProgram, pythonTestCases, requiredPythonModules,
  type PythonExercise, type PythonModule,
} from "../data/python";

const MOCK = import.meta.env.VITE_MOCK === "1";
const ROOT = "/python-course";
const codeBlock = (code: string) => `\`\`\`python\n${code}\n\`\`\``;

export default function PythonCourse() {
  const { moduleId } = useParams();
  const location = useLocation();
  const module = PYTHON_MODULES.find((item) => item.id === moduleId);
  const [solved, setSolved] = useState<Set<string>>(new Set());
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState("");
  useCrumb(module?.title, module ? `Module ${module.number}` : undefined);

  useEffect(() => {
    let active = true;
    loadSolvedExercises().then((items) => {
      if (active) { setSolved((current) => new Set([...items, ...current])); setLoaded(true); }
    }).catch(() => {
      if (active) setError("Could not load saved progress. Reopen this course to retry; exercises remain available.");
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (location.hash !== "#syntax") return;
    const frame = requestAnimationFrame(() => document.getElementById("syntax")?.scrollIntoView());
    return () => cancelAnimationFrame(frame);
  }, [moduleId, location.hash, location.key]);

  if (moduleId && !module) return <div className="page"><h1 className="page-title">Module unavailable</h1><Link to={ROOT}>Return to the Python roadmap</Link></div>;
  const completed = PYTHON_EXERCISES.filter((exercise) => solved.has(exercise.id)).length;
  const next = PYTHON_MODULES.find((item) => item.exercises.some((exercise) => !solved.has(exercise.id)));

  return <div className="page python-course">
    <h1 className="page-title">{module ? `${module.number}. ${module.title}` : "Python: zero to interview problems"}</h1>
    <p className="page-sub">{module?.goal ?? "A coding-first roadmap. Start with no Python syntax; finish by solving mixed interview problems."}</p>
    {error && <p role="alert">{error}</p>}
    {module ? <>
      <nav className="python-actions" aria-label="Course navigation">
        <Link to={ROOT}>← Roadmap</Link>
        {module.number > 1 && <Link to={`${ROOT}/${PYTHON_MODULES[module.number - 2].id}`}>Previous module</Link>}
        {module.number < PYTHON_MODULES.length && <Link to={`${ROOT}/${PYTHON_MODULES[module.number].id}`}>Next module →</Link>}
      </nav>
      <ModuleLesson key={module.id} module={module} solved={solved} onSolved={setSolved} />
    </> : <>
      <div className="card python-intro">
        <p><strong>25 modules · 50 coding exercises · no prior Python required</strong></p>
        <p>Follow the numbered path. Each module teaches syntax, shows a worked example, then asks you to code two problems. Every exercise links back to the syntax lessons used by its starter and worked solution. All graded cases are visible.</p>
        <p>Type and modify the example, attempt both exercises, explain your time and space costs, and pass the exit check. Repeat missed problems from blank the next day and a week later. Move on by mastery, at your own pace.</p>
        <p>Allow about 60–90 minutes per early module and 2–4 hours per later module, plus review. You discover the algorithm; the required Python syntax is taught first.</p>
        <p>Use Python 3.9+ available as <code>python</code> on PATH in the desktop app. No extra Python packages are required. The app supplies function arguments; you write the return value.</p>
        <p role="status">{loaded ? `${completed} / ${PYTHON_EXERCISES.length} exercises passed` : "Loading saved progress…"}</p>
        <progress aria-label="Python course exercises passed" value={completed} max={PYTHON_EXERCISES.length} />
        {loaded && <p><Link className="ghost-link" to={`${ROOT}/${(next ?? PYTHON_MODULES[0]).id}`}>{completed === PYTHON_EXERCISES.length ? "Revisit the course" : completed > 0 ? "Continue with your next module →" : "Start with your first Python function →"}</Link></p>}
      </div>
      {[...new Set(PYTHON_MODULES.map((item) => item.stage))].map((stage) => <section key={stage} className="python-stage">
        <h2>{stage}</h2>
        <ol className="python-roadmap">
          {PYTHON_MODULES.filter((item) => item.stage === stage).map((item) => {
            const count = item.exercises.filter((exercise) => solved.has(exercise.id)).length;
            return <li key={item.id} value={item.number} className="card">
              <Link to={`${ROOT}/${item.id}`}><strong>{item.title}</strong></Link>
              <p>{item.goal}</p>
              <p className="dim">{item.exercises.map((exercise) => exercise.title).join(" · ")}</p>
              <span>{loaded ? `${count} / ${item.exercises.length} passed` : "Progress loading"}</span>
            </li>;
          })}
        </ol>
      </section>)}
      <div className="card"><h2>After this roadmap</h2><p>Practice more variations in the <Link to="/library">DSA Curriculum</Link>, then learn topological sorting, union-find, tries, weighted shortest paths and further DP patterns. The last module explains interview-platform signatures and type annotations.</p></div>
    </>}
  </div>;
}

function ModuleLesson({ module, solved, onSolved }: {
  module: PythonModule; solved: Set<string>; onSolved: (items: Set<string>) => void;
}) {
  const [checked, setChecked] = useState(false);
  return <>
    <section className="card python-lesson" id="syntax">
      <h2>Learn the syntax first</h2>
      {module.number > 1 && <p>Before starting: complete modules 1–{module.number - 1}, or use the exercise syntax links to review them.</p>}
      <AtLevel level={3}><Markdown>{module.explanation}</Markdown></AtLevel>
      <h3>Type, run and change this example</h3>
      <AtLevel level={4}><Markdown>{codeBlock(module.example)}</Markdown></AtLevel>
      <ExampleRunner key={module.id} initial={module.example} />
      <h3>Problem-solving model</h3>
      <AtLevel level={4}><Markdown>{module.pattern}</Markdown></AtLevel>
    </section>
    <h2>Code it yourself</h2>
    <p>Replace the starter return with your code. All cases below are graded; there are no hidden cases. The runner calls your function and displays the returned value. Do not add your own input parser or print driver.</p>
    {module.exercises.map((exercise) => <Exercise key={exercise.id} exercise={exercise} solved={solved.has(exercise.id)} onSolved={onSolved} />)}
    <section className="card python-exit">
      <h2>Before moving on</h2>
      <p>{module.gate}</p>
      <label><input type="checkbox" checked={checked} onChange={(event) => setChecked(event.target.checked)} /> I can explain this without looking at the example.</label>
      <p>{module.exercises.every((exercise) => solved.has(exercise.id)) ? "Both exercises have passed the published cases. Explain why your algorithm meets the requested costs, then repeat it from blank." : "Work through both exercises before continuing. The exit check is a self-assessment, separate from passed cases."}</p>
    </section>
  </>;
}

function ExampleRunner({ initial }: { initial: string }) {
  const [code, setCode] = useState(initial);
  const [output, setOutput] = useState("");
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);
  const run = async () => {
    if (pending.current || MOCK) return;
    pending.current = true;
    setBusy(true);
    setOutput("");
    try {
      const result = await api.runScratch(null, "python", code, "");
      setOutput([result.stdout, result.stderr, result.timed_out ? "Execution timed out." : "", result.exit_code !== 0 ? `Exit code: ${result.exit_code}` : ""].filter(Boolean).join("\n") || "Program finished without output.");
    } catch (error) { setOutput(String(error)); }
    finally { pending.current = false; setBusy(false); }
  };
  return <details className="python-example"><summary>Run and experiment with the example</summary>
    <label className="python-editor-label" htmlFor="python-example">Example code (four spaces per indent)</label>
    <textarea id="python-example" className="python-example-code" spellCheck={false} value={code} onChange={(event) => setCode(event.target.value)} />
    <button disabled={busy || MOCK} onClick={run}>{busy ? "Running…" : "Run example"}</button>
    {MOCK && <p>Real Python execution is available in the desktop app. Browser mock mode only previews the course.</p>}
    {output && <pre className="io-block" role="status">{output}</pre>}
  </details>;
}

function Exercise({ exercise, solved, onSolved }: { exercise: PythonExercise; solved: boolean; onSolved: (items: Set<string>) => void }) {
  const key = `poodcode:python-draft:${exercise.id}`;
  const [code, setCode] = useState(() => {
    try { return localStorage.getItem(key) ?? exercise.starter; } catch { return exercise.starter; }
  });
  const [report, setReport] = useState<JudgeReport | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [draftError, setDraftError] = useState("");
  const pending = useRef(false);
  const edited = useRef(0);
  const edit = (value: string) => {
    edited.current += 1;
    setCode(value);
    setReport(null);
    try { localStorage.setItem(key, value); setDraftError(""); }
    catch { setDraftError("Draft could not be saved on this device. Copy your code before leaving."); }
  };
  const run = async () => {
    if (pending.current || MOCK) return;
    pending.current = true;
    setBusy(true);
    setError("");
    setReport(null);
    const revision = edited.current;
    try {
      const result = await api.runTests(null, "python", pythonProgram(code, exercise.tests), pythonTestCases(exercise.tests));
      // A report only describes the submitted revision, never a newer edit.
      if (revision === edited.current) {
        setReport(result);
        if (result.status === "accepted" && result.total === exercise.tests.length && result.passed === result.total) {
          onSolved(markExerciseSolved(exercise.id));
        }
      }
    } catch (error) { setError(String(error)); }
    finally { pending.current = false; setBusy(false); }
  };
  const [head, fragment] = exercise.id.split(":");
  const anchor = `${head}-${fragment}`;
  return <section className="card python-exercise" id={anchor} aria-labelledby={`${anchor}-title`}>
    <h3 id={`${anchor}-title`}>{exercise.title}{solved ? " · Passed once" : ""}</h3>
    <AtLevel level={4}><Markdown>{exercise.prompt}</Markdown></AtLevel>
    <details className="python-syntax" open><summary>Syntax you need — taught before this problem</summary>
      <ul>{requiredPythonModules(exercise).map((module) => <li key={module.id}><Link to={`${ROOT}/${module.id}#syntax`}>{module.number}. {module.title}</Link></li>)}</ul>
      <p>These cover the starter and worked answer. You can always use explicit loops; unexplained shortcuts such as lambdas, Counter and generators are never required.</p>
    </details>
    <details><summary>All {exercise.tests.length} graded cases</summary>
      {exercise.tests.map((test) => <div key={test.name} className="python-case"><strong>{test.name}</strong><AtLevel level={4}><Markdown>{codeBlock(`${test.setup}${test.call}\n# Expected return: ${test.expected}`)}</Markdown></AtLevel></div>)}
    </details>
    <p id={`${anchor}-editor`}>Your Python solution · Ctrl/Cmd+Enter runs all cases. Drafts save on this device.</p>
    <div className="python-editor" role="group" aria-labelledby={`${anchor}-editor`}>
      <CodeEditor language="python" value={code} onChange={edit} onRun={run} readOnly={busy} tabSize={4} path={`file:///python-course/${anchor}.py`} />
    </div>
    <div className="python-actions">
      <button className="primary" disabled={busy || MOCK} onClick={run}>{busy ? "Running…" : "Run all cases"}</button>
      <details><summary>Restore starter</summary><p>This replaces this exercise's saved draft.</p><button disabled={busy} onClick={() => edit(exercise.starter)}>Replace draft with starter</button></details>
    </div>
    {MOCK && <p>Run this exercise in the desktop app to execute real Python; browser mock mode cannot grade solutions.</p>}
    {(error || draftError) && <p role="alert">{error || draftError}</p>}
    {report && <div aria-live="polite"><TestResults report={report} /></div>}
    <details><summary>Hint</summary><p>{exercise.hint}</p></details>
    <details><summary>Worked answer — open after attempting</summary>
      <AtLevel level={4}><Markdown>{codeBlock(exercise.solution)}</Markdown></AtLevel>
      <p>{exercise.explanation}</p><p><strong>Cost:</strong> {exercise.complexity}</p>
      <p>Close this answer and rewrite the solution yourself. Passed cases do not check your algorithm's asymptotic complexity.</p>
    </details>
  </section>;
}
