import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useStore } from "../store";
import { starterFor } from "../lib/templates";
import { formatClock } from "../lib/format";
import { analyzeComplexity, compareComplexity } from "../lib/complexity";
import { Markdown } from "../components/Markdown";
import { CodeEditor, type CodeEditorHandle } from "../components/CodeEditor";
import { TestResults } from "../components/TestResults";
import { TestCaseManager } from "../components/TestCaseManager";
import { Confidence, DiffBadge, Stat } from "../components/common";
import { useToast } from "../components/Toast";
import { formatMemory } from "../lib/format";
import { lineDiff, diffStats } from "../lib/diff";
import type { Attempt, JudgeReport, Mistake, Note, Problem, Solution, TestCase } from "../types";

const INTERVIEW_SECONDS = 45 * 60;

type LeftTab =
  | "description"
  | "prerequisites"
  | "notes"
  | "solutions"
  | "attempts"
  | "reflect"
  | "editorial";

export default function Solve({ onProgress }: { onProgress?: () => void }) {
  const { id } = useParams();
  const pid = Number(id);
  const nav = useNavigate();
  const toast = useToast();
  const [params] = useSearchParams();
  const interview = params.get("mode") === "interview";
  const contestId = params.get("contest") ? Number(params.get("contest")) : null;
  const drill = params.get("drill") === "1";
  const languages = useStore((s) => s.languages);
  const prefs = useStore((s) => s.prefs);

  const [problem, setProblem] = useState<Problem | null>(null);
  const [cases, setCases] = useState<TestCase[]>([]);
  const [tab, setTab] = useState<LeftTab>("description");
  const [langId, setLangId] = useState(prefs.defaultLanguage);
  const [codeByLang, setCodeByLang] = useState<Record<string, string>>({});
  const [split, setSplit] = useState(false);
  const [splitLangId, setSplitLangId] = useState(prefs.defaultLanguage);
  const [report, setReport] = useState<JudgeReport | null>(null);
  const [running, setRunning] = useState(false);
  const [rightTab, setRightTab] = useState<"results" | "tests" | "complexity">("results");
  const [customStdin, setCustomStdin] = useState("");
  const [revealed, setRevealed] = useState(0);
  const [showEditorial, setShowEditorial] = useState(false);
  const [knownPrereqs, setKnownPrereqs] = useState<Set<string>>(new Set());
  const [showSummary, setShowSummary] = useState(false);
  const [drillLocked, setDrillLocked] = useState(drill);
  const [approach, setApproach] = useState("");
  const [plannedComplexity, setPlannedComplexity] = useState("");
  const leftEditor = useRef<CodeEditorHandle>(null);
  const draftTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});

  // Timer for time-on-problem + interview countdown (wall-clock based so it
  // stays accurate even when the window is backgrounded / interval-throttled).
  const [elapsed, setElapsed] = useState(0);
  const startRef = useRef(Date.now());
  const creditedRef = useRef(0);
  const [locked, setLocked] = useState(false);

  const langInfo = useMemo(
    () => languages.find((l) => l.id === langId) ?? languages[0],
    [languages, langId]
  );
  const monacoLang = langInfo?.monaco ?? "plaintext";
  const code = codeByLang[langId] ?? "";

  const splitLangInfo = useMemo(
    () => languages.find((l) => l.id === splitLangId) ?? languages[0],
    [languages, splitLangId]
  );
  const splitMonacoLang = splitLangInfo?.monaco ?? "plaintext";
  const splitCode = codeByLang[splitLangId] ?? "";
  const openBuffers = Object.keys(codeByLang);
  const labelFor = (id: string) => languages.find((l) => l.id === id)?.label ?? id;

  // Load problem + related data.
  useEffect(() => {
    if (!pid) return;
    api.getProblem(pid).then((p) => {
      setProblem(p);
      setCases(p.test_cases);
    });
    api.getHintsRevealed(pid).then(setRevealed).catch(() => setRevealed(0));
    api.knownPrereqs(pid).then((keys) => setKnownPrereqs(new Set(keys)));
  }, [pid]);

  const togglePrereq = async (key: string) => {
    const known = !knownPrereqs.has(key);
    setKnownPrereqs((prev) => {
      const next = new Set(prev);
      known ? next.add(key) : next.delete(key);
      return next;
    });
    await api.setPrereqStatus(pid, key, known);
  };

  // Initialize a language buffer from its saved SQLite draft, falling back to
  // the starter template. Runs for whichever language buffers are open.
  useEffect(() => {
    if (!problem) return;
    const wanted = new Set([langId, ...(split ? [splitLangId] : [])]);
    for (const l of wanted) {
      if (codeByLang[l] !== undefined) continue;
      // Mark as loading immediately to avoid duplicate fetches.
      setCodeByLang((m) => (m[l] !== undefined ? m : { ...m, [l]: "" }));
      api
        .getDraft(pid, l)
        .then((saved) =>
          setCodeByLang((m) => ({
            ...m,
            [l]: saved ?? starterFor(problem.starter_code, l),
          }))
        )
        .catch(() =>
          setCodeByLang((m) => ({ ...m, [l]: starterFor(problem.starter_code, l) }))
        );
    }
  }, [problem, langId, splitLangId, split, pid, codeByLang]);

  // Wall-clock timer: derive elapsed from a start timestamp each tick.
  useEffect(() => {
    startRef.current = Date.now();
    creditedRef.current = 0;
    setElapsed(0);
    const t = setInterval(
      () => setElapsed(Math.floor((Date.now() - startRef.current) / 1000)),
      1000
    );
    return () => clearInterval(t);
  }, [pid]);

  // Interview lock on expiry — also surface the end-of-interview summary.
  useEffect(() => {
    if (interview && elapsed >= INTERVIEW_SECONDS && !locked) {
      setLocked(true);
      setShowSummary(true);
      toast("⏰ Time's up! Editor locked.");
    }
  }, [interview, elapsed, locked, toast]);

  // Keep a ref of the latest elapsed value for the unmount handler below.
  const elapsedRef = useRef(0);
  elapsedRef.current = elapsed;

  // Credit uncredited study time on unmount (time not already logged by submit).
  useEffect(() => {
    return () => {
      const delta = Math.max(0, elapsedRef.current - creditedRef.current);
      if (delta > 3) api.logStudyTime(delta).catch(() => {});
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Persist a draft to SQLite, debounced per language so typing doesn't spam the
  // backend. Drafts live in the DB (not localStorage) so they survive cache
  // clears and are captured by backups.
  const persistDraft = useCallback(
    (lang: string, v: string) => {
      const timers = draftTimers.current;
      if (timers[lang]) clearTimeout(timers[lang]);
      timers[lang] = setTimeout(() => {
        api.saveDraft(pid, lang, v).catch(() => {});
      }, 500);
    },
    [pid]
  );

  const writeCode = useCallback(
    (lang: string, v: string) => {
      setCodeByLang((m) => ({ ...m, [lang]: v }));
      persistDraft(lang, v);
    },
    [persistDraft]
  );

  const setCode = useCallback((v: string) => writeCode(langId, v), [writeCode, langId]);

  // Flush any pending draft writes when leaving the problem.
  useEffect(() => {
    const timers = draftTimers.current;
    return () => {
      for (const t of Object.values(timers)) clearTimeout(t);
    };
  }, [pid]);

  const nonHidden = cases.filter((c) => c.kind !== "hidden");

  const run = useCallback(async () => {
    if (!langInfo || running || locked || drillLocked) return;
    setRunning(true);
    setRightTab("results");
    try {
      if (nonHidden.some((c) => c.expected_output.trim() !== "")) {
        const rep = await api.runTests(pid, langInfo.id, code, nonHidden);
        setReport(rep);
      } else {
        const out = await api.runScratch(pid, langInfo.id, code, customStdin);
        setReport({
          status: out.timed_out ? "error" : "accepted",
          passed: 0,
          total: 0,
          runtime_ms: out.runtime_ms,
          memory_kb: out.memory_kb,
          compile_error: out.stderr,
          not_installed_hint: "",
          results: [
            {
              name: "Scratch run",
              kind: "example",
              input: customStdin,
              expected: "",
              actual: out.stdout,
              stderr: out.stderr,
              passed: !out.timed_out && out.exit_code === 0,
              timed_out: out.timed_out,
              runtime_ms: out.runtime_ms,
              memory_kb: out.memory_kb,
              truncated: out.truncated,
              verdict: out.timed_out ? "tle" : out.exit_code === 0 ? "pass" : "re",
            },
          ],
        });
      }
    } catch (e) {
      toast(`Run error: ${e}`);
    } finally {
      setRunning(false);
    }
  }, [langInfo, running, locked, drillLocked, nonHidden, code, customStdin, toast, pid]);

  const submit = useCallback(async () => {
    if (!langInfo || running || locked || drillLocked || !problem) return;
    setRunning(true);
    setRightTab("results");
    const delta = Math.max(1, elapsed - creditedRef.current);
    creditedRef.current = elapsed;
    try {
      const rep = await api.submit(problem.id, langInfo.id, code, delta);
      setReport(rep);
      if (rep.status === "accepted") {
        toast("✅ Accepted! Added to revision schedule.");
        const fresh = await api.getProblem(problem.id);
        setProblem(fresh);
      } else if (rep.status === "not_installed") {
        toast("Toolchain not installed for this language.");
      } else if (rep.status === "tle") {
        toast(`⏰ Time limit exceeded — ${rep.passed}/${rep.total} passed. Log why in Reflect.`);
      } else {
        toast(`${rep.passed}/${rep.total} tests passed — tag the mistake in Reflect.`);
      }
      if (contestId) {
        api.recordContestResult(contestId, problem.id, rep.status === "accepted").catch(() => {});
      }
      onProgress?.();
    } catch (e) {
      toast(`Submit error: ${e}`);
    } finally {
      setRunning(false);
    }
  }, [langInfo, running, locked, drillLocked, problem, elapsed, code, toast, onProgress, contestId]);

  const revealHint = () => {
    const n = revealed + 1;
    setRevealed(n);
    api.setHintsRevealed(pid, n).catch(() => {});
  };

  const setConfidence = async (v: number) => {
    if (!problem) return;
    await api.setConfidence(problem.id, v);
    setProblem({ ...problem, confidence: v });
  };
  const toggleFav = async () => {
    if (!problem) return;
    await api.setFavorite(problem.id, !problem.is_favorite);
    setProblem({ ...problem, is_favorite: !problem.is_favorite });
  };

  if (!problem) return <div className="page">Loading problem…</div>;

  const overtime = interview && elapsed >= INTERVIEW_SECONDS;
  const remaining = INTERVIEW_SECONDS - elapsed;

  return (
    <div className="solve">
      {/* LEFT PANE */}
      <div className="solve-pane">
        <div className="solve-toolbar">
          <button className="ghost" onClick={() => nav(-1)}>
            ←
          </button>
          <strong>{problem.title}</strong>
          <DiffBadge d={problem.difficulty} />
          <span className={`star ${problem.is_favorite ? "on" : ""}`} onClick={toggleFav} style={{ cursor: "pointer" }}>
            {problem.is_favorite ? "★" : "☆"}
          </span>
          <span className="spacer" />
          {interview ? (
            <>
              <span className={`timer ${remaining < 300 ? "warn" : ""}`}>
                ⏱ {formatClock(Math.max(0, remaining))}
              </span>
              {!locked && (
                <button
                  className="ghost"
                  title="End the interview now and see your summary"
                  onClick={() => {
                    setLocked(true);
                    setShowSummary(true);
                  }}
                >
                  ⏹ End
                </button>
              )}
            </>
          ) : (
            <span className="timer dim">⏱ {formatClock(elapsed)}</span>
          )}
          {!interview && (
            <button className="ghost" onClick={() => nav(`/problem/${problem.id}/edit`)}>
              ✎ Edit
            </button>
          )}
        </div>

        <div className="tabs">
          {(["description", "prerequisites", "notes", "solutions", "attempts", "reflect", "editorial"] as LeftTab[]).map((t) => {
            const unknown =
              t === "prerequisites" && !interview
                ? problem.prerequisites.filter((p) => !knownPrereqs.has(p.key)).length
                : 0;
            return (
              <div key={t} className={`tab ${tab === t ? "active" : ""}`} onClick={() => setTab(t)}>
                {t[0].toUpperCase() + t.slice(1)}
                {unknown > 0 && <span className="nav-badge" style={{ marginLeft: 6 }}>{unknown}</span>}
              </div>
            );
          })}
        </div>

        <div className="pane-body">
          {tab === "description" && (
            <DescriptionTab
              problem={problem}
              interview={interview}
              revealed={revealed}
              onReveal={revealHint}
              confidence={problem.confidence}
              onConfidence={setConfidence}
            />
          )}
          {tab === "prerequisites" && (
            <PrerequisitesTab
              problem={problem}
              interview={interview}
              known={knownPrereqs}
              onToggle={togglePrereq}
            />
          )}
          {tab === "notes" && <NotesTab problemId={problem.id} />}
          {tab === "solutions" && (
            <SolutionsTab problemId={problem.id} currentCode={code} currentLang={langInfo?.id ?? "python"} />
          )}
          {tab === "attempts" && <AttemptsTab problemId={problem.id} />}
          {tab === "reflect" && <ReflectTab problemId={problem.id} />}
          {tab === "editorial" && (
            <EditorialTab problem={problem} interview={interview} showEditorial={showEditorial} onShow={() => setShowEditorial(true)} />
          )}
        </div>
      </div>

      {/* RIGHT PANE */}
      <div className="solve-pane" style={{ borderRight: "none" }}>
        <div className="solve-toolbar">
          <select value={langId} onChange={(e) => setLangId(e.target.value)}>
            {languages.map((l) => (
              <option key={l.id} value={l.id}>
                {l.label} {l.installed ? "" : "· (not installed)"}
              </option>
            ))}
          </select>
          {openBuffers.length > 1 && (
            <div className="pill-toggle" style={{ marginLeft: 4 }}>
              {openBuffers.map((l) => (
                <span
                  key={l}
                  className={`pill ${l === langId ? "on" : ""}`}
                  onClick={() => setLangId(l)}
                  title={`Switch to your ${labelFor(l)} buffer`}
                >
                  {labelFor(l)}
                </span>
              ))}
            </div>
          )}
          <span className="spacer" />
          <button onClick={() => leftEditor.current?.format()} title="Format document">
            ⌗ Format
          </button>
          <button
            className={split ? "primary" : ""}
            onClick={() => setSplit((s) => !s)}
            title="Split editor (edit two language buffers side by side)"
          >
            ⊟ Split
          </button>
          <button
            onClick={() => setCode(starterFor(problem.starter_code, langId))}
            title="Reset to starter code"
          >
            ↺ Reset
          </button>
          <button onClick={run} disabled={running || locked}>
            ▶ Run
          </button>
          <button className="primary" onClick={submit} disabled={running || locked}>
            ⏎ Submit
          </button>
        </div>

        {langInfo && !langInfo.installed && (
          <div className="card" style={{ margin: 10, borderColor: "var(--medium)" }}>
            <strong>{langInfo.label} isn't installed.</strong>{" "}
            <span className="dim">{langInfo.install_hint}</span>
          </div>
        )}

        {drillLocked && (
          <div className="card" style={{ margin: 10, borderColor: "var(--accent)" }}>
            <strong>🧠 Explain-first drill.</strong>
            <p className="dim" style={{ marginTop: 4 }}>
              Before the editor unlocks, state your plan out loud (in writing). This builds the
              interview habit of thinking before coding.
            </p>
            <div className="io-label">Your approach</div>
            <textarea
              rows={3}
              style={{ width: "100%" }}
              placeholder="Which pattern? What are the steps?"
              value={approach}
              onChange={(e) => setApproach(e.target.value)}
            />
            <div className="io-label" style={{ marginTop: 6 }}>
              Target complexity
            </div>
            <input
              style={{ width: 200 }}
              placeholder="e.g. O(n) time, O(1) space"
              value={plannedComplexity}
              onChange={(e) => setPlannedComplexity(e.target.value)}
            />
            <div className="row" style={{ marginTop: 8 }}>
              <button
                className="primary"
                disabled={approach.trim().length < 10}
                onClick={() => setDrillLocked(false)}
              >
                Unlock editor →
              </button>
              <span className="faint" style={{ fontSize: 12 }}>
                {approach.trim().length < 10 ? "Write at least a sentence." : "Looks good."}
              </span>
            </div>
          </div>
        )}

        <div className="editor-host" style={{ display: "flex", minHeight: 0 }}>
          <div style={{ flex: 1, minWidth: 0, height: "100%" }}>
            <CodeEditor
              ref={leftEditor}
              language={monacoLang}
              value={code}
              onChange={setCode}
              readOnly={locked || drillLocked}
              disableIntellisense={interview}
              onRun={run}
              onSubmit={submit}
            />
          </div>
          {split && (
            <div
              style={{
                flex: 1,
                minWidth: 0,
                height: "100%",
                display: "flex",
                flexDirection: "column",
                borderLeft: "1px solid var(--border)",
              }}
            >
              <div className="row" style={{ padding: "4px 6px" }}>
                <select value={splitLangId} onChange={(e) => setSplitLangId(e.target.value)}>
                  {languages.map((l) => (
                    <option key={l.id} value={l.id}>
                      {l.label}
                    </option>
                  ))}
                </select>
                <span className="faint" style={{ fontSize: 12 }}>
                  Reference / second buffer
                </span>
              </div>
              <div style={{ flex: 1, minHeight: 0 }}>
                <CodeEditor
                  language={splitMonacoLang}
                  value={splitCode}
                  onChange={(v) => writeCode(splitLangId, v)}
                  readOnly={locked}
                  disableIntellisense={interview}
                  onRun={run}
                  onSubmit={submit}
                />
              </div>
            </div>
          )}
        </div>

        <div className="tabs">
          {(["results", "tests", "complexity"] as const).map((t) => (
            <div key={t} className={`tab ${rightTab === t ? "active" : ""}`} onClick={() => setRightTab(t)}>
              {t === "results" ? "Results" : t === "tests" ? "Test Cases" : "Complexity"}
            </div>
          ))}
          <span className="spacer" />
          <span className="dim" style={{ padding: "9px 12px", fontSize: 12 }}>
            Ctrl+Enter run · Ctrl+Shift+Enter submit
          </span>
        </div>

        <div className="pane-body" style={{ maxHeight: "34vh" }}>
          {interview && showSummary && (
            <InterviewSummary
              problemId={problem.id}
              elapsed={elapsed}
              expired={overtime}
              onGoAttempts={() => setTab("attempts")}
              onGoNotes={() => setTab("notes")}
              onClose={() => setShowSummary(false)}
            />
          )}
          {rightTab === "results" && (
            <>
              {nonHidden.every((c) => c.expected_output.trim() === "") && (
                <div style={{ marginBottom: 10 }}>
                  <div className="io-label">Custom stdin (for Run)</div>
                  <textarea
                    rows={3}
                    style={{ width: "100%" }}
                    value={customStdin}
                    onChange={(e) => setCustomStdin(e.target.value)}
                    placeholder="Type input to feed your program on stdin…"
                  />
                </div>
              )}
              <TestResults report={report} />
            </>
          )}
          {rightTab === "tests" && (
            <TestCaseManager problemId={problem.id} cases={cases} onChange={setCases} />
          )}
          {rightTab === "complexity" && <ComplexityTab code={code} problem={problem} />}
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ Tabs */

function DescriptionTab({
  problem,
  interview,
  revealed,
  onReveal,
  confidence,
  onConfidence,
}: {
  problem: Problem;
  interview: boolean;
  revealed: number;
  onReveal: () => void;
  confidence: number;
  onConfidence: (v: number) => void;
}) {
  return (
    <div>
      <div className="tag-row" style={{ marginBottom: 12 }}>
        {problem.patterns.map((t) => (
          <span key={t} className="badge" style={{ borderColor: "var(--accent)", color: "var(--accent)" }}>
            ◆ {t}
          </span>
        ))}
        {problem.topics.map((t) => (
          <span key={t} className="badge tag">
            {t}
          </span>
        ))}
        {problem.subtopics.map((t) => (
          <span key={t} className="badge">
            {t}
          </span>
        ))}
        {problem.companies.map((c) => (
          <span key={c} className="badge">
            🏢 {c}
          </span>
        ))}
      </div>

      {problem.function_spec && (
        <div className="card" style={{ marginBottom: 12, borderColor: "var(--accent)" }}>
          <strong>ƒ Function mode.</strong>{" "}
          <span className="dim">
            Implement <span className="mono">{problem.function_spec.name}(
            {problem.function_spec.params.map((p) => `${p.name}: ${p.type}`).join(", ")}) → {problem.function_spec.returns}</span>
            . The app parses input and reads your return value — no I/O boilerplate. Available in Python and Java.
          </span>
        </div>
      )}

      <Markdown>{problem.description}</Markdown>

      {problem.constraints && (
        <>
          <h3>Constraints</h3>
          <Markdown>{problem.constraints.split("\n").map((l) => `- ${l}`).join("\n")}</Markdown>
        </>
      )}

      {problem.examples.length > 0 && (
        <>
          <h3>Examples</h3>
          {problem.examples.map((ex, i) => (
            <div key={i} className="card" style={{ marginBottom: 10 }}>
              <div className="io-label">Input</div>
              <div className="io-block">{ex.input}</div>
              <div className="io-label" style={{ marginTop: 6 }}>
                Output
              </div>
              <div className="io-block">{ex.output}</div>
              {ex.explanation && <p className="dim" style={{ marginBottom: 0 }}>{ex.explanation}</p>}
            </div>
          ))}
        </>
      )}

      <div className="divider" />
      <div className="row">
        <span className="dim">Your confidence:</span>
        <Confidence value={confidence} onChange={onConfidence} />
      </div>

      {!interview && problem.hints.length > 0 && (
        <>
          <div className="divider" />
          <h3>Hints</h3>
          {problem.hints.map((h, i) => (
            <div key={i} className="hint">
              <div className="hint-label">Hint {i + 1}</div>
              {i < revealed ? <div>{h}</div> : <div className="locked">Hidden — reveal to view</div>}
            </div>
          ))}
          {revealed < problem.hints.length && (
            <button onClick={onReveal}>💡 Reveal hint {revealed + 1}</button>
          )}
        </>
      )}
      {interview && <p className="faint" style={{ marginTop: 16 }}>Hints are disabled in interview mode.</p>}
    </div>
  );
}

function PrerequisitesTab({
  problem,
  interview,
  known,
  onToggle,
}: {
  problem: Problem;
  interview: boolean;
  known: Set<string>;
  onToggle: (key: string) => void;
}) {
  const [open, setOpen] = useState<string | null>(null);
  const nav = useNavigate();

  if (interview) {
    return <p className="faint">Prerequisites are hidden during interview mode.</p>;
  }
  if (problem.prerequisites.length === 0) {
    return <div className="dim">No prerequisites listed for this problem.</div>;
  }

  const knownCount = problem.prerequisites.filter((p) => known.has(p.key)).length;
  const total = problem.prerequisites.length;
  const ready = knownCount === total;

  return (
    <div>
      <p className="dim" style={{ marginTop: 0 }}>
        Concepts that help you solve this problem. Tick the ones you already know; expand any you
        don't to learn what it is and how it applies here.
      </p>
      <div className="row" style={{ marginBottom: 12 }}>
        <div className="progress" style={{ flex: 1 }}>
          <span style={{ width: `${(knownCount / total) * 100}%`, background: ready ? "var(--good)" : "var(--accent)" }} />
        </div>
        <span className="dim mono">{knownCount}/{total} known</span>
      </div>
      {ready && (
        <div className="card" style={{ marginBottom: 12, borderColor: "var(--good)" }}>
          <strong style={{ color: "var(--good)" }}>You know all the prerequisites 🎯</strong>{" "}
          <span className="dim">Go get it.</span>
        </div>
      )}

      {problem.prerequisites.map((p) => {
        const isKnown = known.has(p.key);
        const isOpen = open === p.key;
        return (
          <div key={p.key} className={`result ${isKnown ? "pass" : ""}`}>
            <div className="result-head">
              <input
                type="checkbox"
                checked={isKnown}
                onChange={() => onToggle(p.key)}
                onClick={(e) => e.stopPropagation()}
                title={isKnown ? "I know this" : "Mark as known"}
                style={{ width: 16, height: 16, cursor: "pointer" }}
              />
              <strong
                style={{ textDecoration: isKnown ? "none" : "none", cursor: "pointer" }}
                onClick={() => setOpen(isOpen ? null : p.key)}
              >
                {p.name}
              </strong>
              {isKnown ? (
                <span className="badge" style={{ color: "var(--good)", borderColor: "var(--good)" }}>known</span>
              ) : (
                <span className="badge" style={{ color: "var(--medium)", borderColor: "var(--medium)" }}>
                  learn
                </span>
              )}
              <span className="spacer" />
              <button className="ghost" onClick={() => setOpen(isOpen ? null : p.key)}>
                {isOpen ? "Hide" : "Dive deeper"} {isOpen ? "▲" : "▼"}
              </button>
            </div>
            {isOpen && (
              <div className="result-body">
                <div>
                  <div className="io-label">What it is</div>
                  <p style={{ margin: 0 }}>{p.what || "—"}</p>
                </div>
                {p.deep && (
                  <div>
                    <div className="io-label">Deeper dive</div>
                    <p style={{ margin: 0 }}>{p.deep}</p>
                  </div>
                )}
                {p.java && (
                  <div>
                    <div className="io-label" style={{ color: "var(--accent)" }}>In Java</div>
                    <p style={{ margin: 0 }} className="mono" >{p.java}</p>
                  </div>
                )}
                <div>
                  <div className="io-label">How it helps here</div>
                  <p style={{ margin: 0 }}>{p.how || "—"}</p>
                </div>
                <div className="row">
                  <button onClick={() => nav(`/learn/${p.key}`)}>📘 Open full lesson</button>
                  {!isKnown && (
                    <button className="success" onClick={() => onToggle(p.key)}>
                      ✓ Got it — mark as known
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function NotesTab({ problemId }: { problemId: number }) {
  const [note, setNote] = useState<Note | null>(null);
  const [preview, setPreview] = useState(false);
  const toast = useToast();
  const TEMPLATE = `## Key Idea\n\n## Mistakes\n\n## Complexity\n\n## Alternative Solutions\n\n## Patterns\n\n## Things To Remember\n`;

  useEffect(() => {
    api.getNote(problemId).then(setNote);
  }, [problemId]);

  const save = async (content: string) => {
    setNote((n) => (n ? { ...n, content } : { problem_id: problemId, content, updated_at: "" }));
    await api.saveNote(problemId, content);
  };

  if (!note) return <div className="dim">Loading…</div>;

  return (
    <div>
      <div className="row" style={{ marginBottom: 8 }}>
        <button className={preview ? "" : "primary"} onClick={() => setPreview(false)}>
          Edit
        </button>
        <button className={preview ? "primary" : ""} onClick={() => setPreview(true)}>
          Preview
        </button>
        <span className="spacer" />
        {!note.content && (
          <button
            className="ghost"
            onClick={() => {
              save(TEMPLATE);
              toast("Inserted note template");
            }}
          >
            Insert section template
          </button>
        )}
      </div>
      {preview ? (
        <Markdown>{note.content || "_No notes yet._"}</Markdown>
      ) : (
        <textarea
          style={{ width: "100%", minHeight: "50vh" }}
          value={note.content}
          onChange={(e) => save(e.target.value)}
          placeholder="Markdown notes — supports headings, code blocks, tables, checklists, links…"
        />
      )}
      <div className="faint" style={{ fontSize: 12, marginTop: 6 }}>
        Autosaved.
      </div>
    </div>
  );
}

function SolutionsTab({
  problemId,
  currentCode,
  currentLang,
}: {
  problemId: number;
  currentCode: string;
  currentLang: string;
}) {
  const [list, setList] = useState<Solution[]>([]);
  const [editing, setEditing] = useState<Solution | null>(null);
  const toast = useToast();

  const load = () => api.listSolutions(problemId).then(setList);
  useEffect(() => {
    load();
  }, [problemId]);

  const blank = (): Solution => ({
    id: 0,
    problem_id: problemId,
    title: "Optimized",
    language: currentLang,
    code: "",
    time_complexity: "",
    space_complexity: "",
    approach_kind: "Optimized",
    notes: "",
    created_at: "",
    updated_at: "",
  });

  const save = async (s: Solution) => {
    await api.saveSolution(s);
    setEditing(null);
    load();
    toast("Solution saved");
  };
  const del = async (id: number) => {
    await api.deleteSolution(id);
    load();
  };

  return (
    <div>
      <div className="row" style={{ marginBottom: 10 }}>
        <button onClick={() => setEditing(blank())}>+ New approach</button>
        <button
          className="ghost"
          onClick={() => setEditing({ ...blank(), code: currentCode, title: "From editor" })}
        >
          Save current code
        </button>
      </div>

      {editing && (
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="row wrap" style={{ marginBottom: 8 }}>
            <input placeholder="Title" value={editing.title} onChange={(e) => setEditing({ ...editing, title: e.target.value })} />
            <select value={editing.approach_kind} onChange={(e) => setEditing({ ...editing, approach_kind: e.target.value })}>
              {["Brute Force", "Optimized", "Recursive", "Iterative", "Dynamic Programming", "Two Pointers", "Greedy"].map((k) => (
                <option key={k}>{k}</option>
              ))}
            </select>
            <input placeholder="Time e.g. O(n)" style={{ width: 120 }} value={editing.time_complexity} onChange={(e) => setEditing({ ...editing, time_complexity: e.target.value })} />
            <input placeholder="Space e.g. O(1)" style={{ width: 120 }} value={editing.space_complexity} onChange={(e) => setEditing({ ...editing, space_complexity: e.target.value })} />
          </div>
          <textarea rows={10} style={{ width: "100%" }} value={editing.code} onChange={(e) => setEditing({ ...editing, code: e.target.value })} placeholder="Solution code" />
          <textarea rows={2} style={{ width: "100%", marginTop: 8 }} value={editing.notes} onChange={(e) => setEditing({ ...editing, notes: e.target.value })} placeholder="Notes on this approach" />
          <div className="row" style={{ marginTop: 8 }}>
            <button className="primary" onClick={() => save(editing)}>Save</button>
            <button className="ghost" onClick={() => setEditing(null)}>Cancel</button>
          </div>
        </div>
      )}

      {list.length === 0 && !editing && <div className="dim">No stored approaches yet.</div>}
      {list.map((s) => (
        <div key={s.id} className="card" style={{ marginBottom: 10 }}>
          <div className="row">
            <strong>{s.title}</strong>
            <span className="badge">{s.approach_kind}</span>
            {s.time_complexity && <span className="badge">⏱ {s.time_complexity}</span>}
            {s.space_complexity && <span className="badge">💾 {s.space_complexity}</span>}
            <span className="badge">{s.language}</span>
            <span className="spacer" />
            <button className="ghost danger" onClick={() => del(s.id)}>Delete</button>
          </div>
          {s.notes && <p className="dim">{s.notes}</p>}
          <pre className="io-block" style={{ maxHeight: 260 }}>{s.code}</pre>
        </div>
      ))}
    </div>
  );
}

type SnapshotKey = "first" | "best" | "latest";

function AttemptsTab({ problemId }: { problemId: number }) {
  const [list, setList] = useState<Attempt[]>([]);
  const [open, setOpen] = useState<number | null>(null);
  const [compare, setCompare] = useState(false);
  const [leftKey, setLeftKey] = useState<SnapshotKey>("first");
  const [rightKey, setRightKey] = useState<SnapshotKey>("latest");

  useEffect(() => {
    api.listAttempts(problemId).then(setList);
  }, [problemId]);

  if (list.length === 0) return <div className="dim">No submissions yet.</div>;

  const accepted = list.filter((a) => a.status === "accepted");
  const first = list[list.length - 1];
  const latest = list[0];
  // The "best" solution: the fastest accepted attempt, falling back to the
  // earliest accepted one (the moment it was first solved).
  const best =
    accepted.length > 0
      ? [...accepted].sort(
          (a, b) => (a.runtime_ms ?? Infinity) - (b.runtime_ms ?? Infinity)
        )[0]
      : null;

  const snapshots: Record<SnapshotKey, Attempt | null> = { first, best, latest };
  const snapLabel: Record<SnapshotKey, string> = {
    first: "First attempt",
    best: "Best (fastest accepted)",
    latest: "Latest attempt",
  };
  const available: SnapshotKey[] = (["first", "best", "latest"] as SnapshotKey[]).filter(
    (k) => snapshots[k] !== null
  );
  const left = snapshots[leftKey];
  const right = snapshots[rightKey];

  const statusColor = (s: string) =>
    s === "accepted" ? "var(--good)" : s === "wrong" ? "var(--medium)" : "var(--bad)";

  return (
    <div>
      <div className="row" style={{ marginBottom: 10 }}>
        <span className="dim">{list.length} submissions · {accepted.length} accepted</span>
        <span className="spacer" />
        {list.length >= 2 && (
          <button className={compare ? "primary" : ""} onClick={() => setCompare(!compare)}>
            ⇄ Compare attempts
          </button>
        )}
      </div>

      {compare && (
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="row wrap" style={{ marginBottom: 8, gap: 8 }}>
            <label className="dim">
              Left{" "}
              <select value={leftKey} onChange={(e) => setLeftKey(e.target.value as SnapshotKey)}>
                {available.map((k) => (
                  <option key={k} value={k}>
                    {snapLabel[k]}
                  </option>
                ))}
              </select>
            </label>
            <label className="dim">
              Right{" "}
              <select value={rightKey} onChange={(e) => setRightKey(e.target.value as SnapshotKey)}>
                {available.map((k) => (
                  <option key={k} value={k}>
                    {snapLabel[k]}
                  </option>
                ))}
              </select>
            </label>
          </div>
          {left && right ? (
            <CodeDiff
              a={left.code}
              b={right.code}
              aLabel={`${snapLabel[leftKey]} · ${new Date(left.created_at.replace(" ", "T")).toLocaleDateString()}`}
              bLabel={`${snapLabel[rightKey]} · ${new Date(right.created_at.replace(" ", "T")).toLocaleDateString()}`}
            />
          ) : (
            <div className="dim">Not enough distinct snapshots to compare yet.</div>
          )}
        </div>
      )}

      {list.map((a, i) => (
        <div key={a.id} className="result">
          <div className="result-head" onClick={() => setOpen(open === i ? null : i)}>
            <span style={{ color: statusColor(a.status), fontWeight: 700 }}>
              {a.status === "accepted" ? "Accepted" : a.status === "wrong" ? "Wrong" : "Error"}
            </span>
            <span className="badge">{a.language}</span>
            {best && a.id === best.id && (
              <span className="badge" style={{ color: "var(--good)", borderColor: "var(--good)" }}>
                ★ best
              </span>
            )}
            <span className="dim">{a.passed}/{a.total}</span>
            <span className="spacer" />
            {a.memory_kb != null && a.memory_kb > 0 && (
              <span className="dim">{formatMemory(a.memory_kb)}</span>
            )}
            <span className="dim">{a.runtime_ms ?? 0} ms</span>
            <span className="dim">{new Date(a.created_at.replace(" ", "T")).toLocaleString()}</span>
          </div>
          {open === i && (
            <div className="result-body">
              {a.error_text && <div className="io-block" style={{ color: "var(--bad)" }}>{a.error_text}</div>}
              <pre className="io-block" style={{ maxHeight: 320 }}>{a.code}</pre>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

/** Line-level diff of two code snapshots with add/remove highlighting. */
function CodeDiff({
  a,
  b,
  aLabel,
  bLabel,
}: {
  a: string;
  b: string;
  aLabel: string;
  bLabel: string;
}) {
  const ops = useMemo(() => lineDiff(a, b), [a, b]);
  const { added, removed } = diffStats(ops);
  const bg = (t: string) =>
    t === "add"
      ? "color-mix(in srgb, var(--good) 18%, transparent)"
      : t === "del"
      ? "color-mix(in srgb, var(--bad) 18%, transparent)"
      : "transparent";
  const sign = (t: string) => (t === "add" ? "+" : t === "del" ? "−" : " ");

  return (
    <div>
      <div className="row" style={{ marginBottom: 6 }}>
        <span className="dim" style={{ fontSize: 12 }}>
          {aLabel} → {bLabel}
        </span>
        <span className="spacer" />
        <span className="badge" style={{ color: "var(--good)", borderColor: "var(--good)" }}>
          +{added}
        </span>
        <span className="badge" style={{ color: "var(--bad)", borderColor: "var(--bad)" }}>
          −{removed}
        </span>
      </div>
      <pre className="io-block" style={{ maxHeight: 360, overflow: "auto" }}>
        {ops.map((op, i) => (
          <div key={i} style={{ background: bg(op.type), whiteSpace: "pre-wrap" }}>
            <span className="faint" style={{ userSelect: "none" }}>{sign(op.type)} </span>
            {op.text || " "}
          </div>
        ))}
      </pre>
      {added === 0 && removed === 0 && (
        <div className="dim" style={{ marginTop: 6 }}>These two snapshots are identical.</div>
      )}
    </div>
  );
}

/** End-of-interview recap: time, submissions, last result, and next steps. */
function InterviewSummary({
  problemId,
  elapsed,
  expired,
  onGoAttempts,
  onGoNotes,
  onClose,
}: {
  problemId: number;
  elapsed: number;
  expired: boolean;
  onGoAttempts: () => void;
  onGoNotes: () => void;
  onClose: () => void;
}) {
  const [attempts, setAttempts] = useState<Attempt[]>([]);
  useEffect(() => {
    api.listAttempts(problemId).then(setAttempts);
  }, [problemId]);

  const accepted = attempts.filter((a) => a.status === "accepted").length;
  const last = attempts[0];
  const lastLabel = last
    ? last.status === "accepted"
      ? "Accepted"
      : last.status === "wrong"
      ? "Wrong answer"
      : "Runtime error"
    : "—";

  return (
    <div className="card" style={{ marginBottom: 10, borderColor: "var(--hard)" }}>
      <div className="row">
        <strong style={{ fontSize: 15 }}>
          {expired ? "⏰ Interview finished — time expired" : "⏹ Interview ended"}
        </strong>
        <span className="spacer" />
        <button className="ghost" onClick={onClose}>
          Dismiss
        </button>
      </div>
      <div className="grid cols-4" style={{ margin: "10px 0" }}>
        <Stat value={formatClock(elapsed)} label="Time spent" />
        <Stat value={attempts.length} label="Submissions" />
        <Stat value={accepted} label="Accepted" />
        <Stat value={last ? `${last.passed}/${last.total}` : "—"} label="Last result" />
      </div>
      {last && (
        <div className="dim" style={{ marginBottom: 8 }}>
          Last submission: {lastLabel} · {last.runtime_ms ?? 0} ms
          {last.memory_kb ? ` · ${formatMemory(last.memory_kb)}` : ""}.
        </div>
      )}
      <p className="dim" style={{ marginTop: 0 }}>
        {accepted > 0
          ? "Nice — you solved it under interview conditions. Capture what made it click."
          : "You didn't land an accepted solution — that's the most valuable kind of practice. Write down where you got stuck."}
      </p>
      <div className="row">
        <button onClick={onGoAttempts}>Review attempts</button>
        <button className="primary" onClick={onGoNotes}>
          Write a retro note
        </button>
      </div>
    </div>
  );
}

const MISTAKE_CATEGORIES = [
  "off-by-one",
  "wrong-data-structure",
  "missed-edge-case",
  "tle",
  "misread-problem",
  "wrong-algorithm",
  "implementation-bug",
  "complexity",
];

/** Log post-mortem mistakes with a taxonomy, for later aggregation in Stats. */
function ReflectTab({ problemId }: { problemId: number }) {
  const [list, setList] = useState<Mistake[]>([]);
  const [category, setCategory] = useState(MISTAKE_CATEGORIES[0]);
  const [note, setNote] = useState("");
  const toast = useToast();

  const load = () => api.listMistakes(problemId).then(setList);
  useEffect(() => {
    load();
  }, [problemId]);

  const add = async () => {
    await api.addMistake({
      id: 0,
      problem_id: problemId,
      attempt_id: null,
      category,
      note,
      created_at: "",
    });
    setNote("");
    load();
    toast("Logged — this feeds your mistake patterns in Statistics.");
  };
  const del = async (id: number) => {
    await api.deleteMistake(id);
    load();
  };

  return (
    <div>
      <p className="dim" style={{ marginTop: 0 }}>
        Capture <em>why</em> a solve went wrong. Tagged mistakes roll up into "your top mistake
        types" on the Statistics page — the fastest way to see your recurring blind spots.
      </p>
      <div className="card" style={{ marginBottom: 12 }}>
        <div className="row wrap" style={{ gap: 8, marginBottom: 8 }}>
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            {MISTAKE_CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <input
            style={{ flex: 1, minWidth: 160 }}
            placeholder="What happened? (optional)"
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
          <button className="primary" onClick={add}>
            + Log mistake
          </button>
        </div>
      </div>
      {list.length === 0 ? (
        <div className="dim">No mistakes logged for this problem.</div>
      ) : (
        list.map((m) => (
          <div key={m.id} className="result">
            <div className="result-head">
              <span className="badge" style={{ color: "var(--bad)", borderColor: "var(--bad)" }}>
                {m.category}
              </span>
              <span className="dim">{m.note}</span>
              <span className="spacer" />
              <button className="ghost danger" onClick={() => del(m.id)}>
                Delete
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

function EditorialTab({
  problem,
  interview,
  showEditorial,
  onShow,
}: {
  problem: Problem;
  interview: boolean;
  showEditorial: boolean;
  onShow: () => void;
}) {
  if (interview) {
    return <p className="faint">The editorial is hidden during interview mode.</p>;
  }
  return (
    <div>
      <div className="card" style={{ marginBottom: 12 }}>
        <div className="io-label">Optimal complexity</div>
        <div className="row" style={{ marginTop: 4 }}>
          <span className="badge">⏱ Time: {problem.optimal_time || "—"}</span>
          <span className="badge">💾 Space: {problem.optimal_space || "—"}</span>
        </div>
        {problem.optimal_explanation && <p className="dim" style={{ marginBottom: 0, marginTop: 8 }}>{problem.optimal_explanation}</p>}
      </div>

      {!showEditorial ? (
        <div className="empty">
          <div className="big">📖</div>
          <p>The full editorial reveals the complete approach.</p>
          <button className="primary" onClick={onShow}>
            Reveal editorial
          </button>
        </div>
      ) : (
        <>
          {problem.editorials.length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <div className="io-label">Approaches (brute force → optimal)</div>
              {problem.editorials.map((e, i) => (
                <div key={i} className="card" style={{ marginBottom: 8 }}>
                  <div className="row">
                    <strong>{e.title}</strong>
                    <span className="spacer" />
                    {e.time && <span className="badge">⏱ {e.time}</span>}
                    {e.space && <span className="badge">💾 {e.space}</span>}
                  </div>
                  {e.body && <p className="dim" style={{ marginBottom: 0 }}>{e.body}</p>}
                </div>
              ))}
            </div>
          )}
          <Markdown>{problem.editorial || "_No editorial provided._"}</Markdown>
          {problem.follow_ups.length > 0 && (
            <>
              <div className="divider" />
              <h3>Follow-ups</h3>
              {problem.follow_ups.map((f, i) => (
                <FollowUpLink key={i} slug={f.slug} title={f.title} note={f.note} />
              ))}
            </>
          )}
        </>
      )}
    </div>
  );
}

function FollowUpLink({ slug, title, note }: { slug: string; title: string; note: string }) {
  const nav = useNavigate();
  const [problems, setProblems] = useState<Problem[] | null>(null);
  useEffect(() => {
    api.listProblems().then(setProblems);
  }, []);
  const target = problems?.find((p) => p.slug === slug);
  return (
    <div className="card" style={{ marginBottom: 8 }}>
      <div className="row">
        <strong>{title}</strong>
        <span className="spacer" />
        {target && (
          <button className="ghost" onClick={() => nav(`/solve/${target.id}`)}>
            Open →
          </button>
        )}
      </div>
      {note && <p className="dim" style={{ marginBottom: 0 }}>{note}</p>}
    </div>
  );
}

function ComplexityTab({ code, problem }: { code: string; problem: Problem }) {
  const est = useMemo(() => analyzeComplexity(code), [code]);
  const timeVerdict = compareComplexity(est.time, problem.optimal_time);

  const verdictText: Record<string, { t: string; c: string }> = {
    better: { t: "Better than the reference optimal (double-check correctness!)", c: "var(--good)" },
    equal: { t: "Matches the optimal complexity 🎯", c: "var(--good)" },
    worse: { t: "Slower than optimal — there's room to improve", c: "var(--medium)" },
    unknown: { t: "Couldn't compare against the stated optimal", c: "var(--text-dim)" },
  };

  return (
    <div>
      <div className="grid cols-2">
        <div className="card">
          <div className="io-label">Your solution (estimated)</div>
          <div style={{ fontSize: 20, fontWeight: 700, marginTop: 4 }}>{est.time}</div>
          <div className="dim">space {est.space}</div>
        </div>
        <div className="card">
          <div className="io-label">Optimal</div>
          <div style={{ fontSize: 20, fontWeight: 700, marginTop: 4 }}>{problem.optimal_time || "—"}</div>
          <div className="dim">space {problem.optimal_space || "—"}</div>
        </div>
      </div>
      <div className="card" style={{ marginTop: 12, borderColor: verdictText[timeVerdict].c }}>
        <strong style={{ color: verdictText[timeVerdict].c }}>{verdictText[timeVerdict].t}</strong>
        <ul style={{ marginBottom: 0 }}>
          {est.signals.map((s, i) => (
            <li key={i} className="dim">{s}</li>
          ))}
        </ul>
        <p className="faint" style={{ fontSize: 12, marginTop: 8, marginBottom: 0 }}>
          Estimates are heuristic (based on loop nesting, recursion, sorting) — treat them as a prompt, not a proof.
        </p>
      </div>
    </div>
  );
}
