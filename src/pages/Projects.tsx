import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Navigate, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api } from "../api";
import type {
  BackendStep,
  Project,
  ProjectModule,
  ProjectTrack,
  SyntaxItem,
} from "../types";
import { Markdown } from "../components/Markdown";
import { ExerciseCard, QuizSection } from "../components/LearnExercise";
import { ExerciseSections } from "../components/ExerciseSections";
import { ReferenceReveal } from "../components/ReferenceReveal";
import { Section, useCollapse } from "../components/Collapsible";
import { ClickableRow, Empty } from "../components/common";
import { useToast } from "../components/Toast";
import {
  loadDoneChapters,
  setChapterDone,
  solvedExercises,
  markExerciseSolved,
  unmarkExercisesSolved,
} from "../lib/learnProgress";
import { collectExerciseIds, plural, solvedLabel, studyTime } from "../lib/trackProgress";

// Module completion is tracked in the same SQLite-backed chapter-done set as
// the Learn tab, the courses and the Backend Lab, under a namespaced key so it
// can never collide with a concept key, a course week or a backend project.
const moduleKey = (projectKey: string, key: string) => `project:${projectKey}:${key}`;

/** Every judged exercise required to complete a module. */
const requiredExerciseIds = (m: ProjectModule) => collectExerciseIds(m.steps, m.final_build);

export default function Projects() {
  const { project, module: moduleParam } = useParams();
  const [track, setTrack] = useState<ProjectTrack | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [done, setDone] = useState<Set<string>>(new Set());
  const nav = useNavigate();

  const load = useCallback(() => {
    setLoadError(null);
    api
      .projectsTrack()
      .then(setTrack)
      .catch((e: unknown) =>
        setLoadError(String((e as { message?: string })?.message ?? e) || "unknown error")
      );
  }, []);

  useEffect(() => {
    load();
    loadDoneChapters().then(setDone).catch(() => {});
  }, [load]);

  async function setModuleDone(projectKey: string, key: string, value: boolean) {
    setDone(await setChapterDone(done, moduleKey(projectKey, key), value));
  }

  // A failed load used to be indistinguishable from a slow one: the catch set
  // the track back to null and the page said "Loading…" forever. The realistic
  // failure is a regenerated seeds/projects.json that no longer deserializes
  // into `ProjectTrack` after a model change, and the message naming the field
  // that broke is the single most useful thing on the screen when it happens.
  if (loadError) {
    return (
      <div className="page">
        <Empty icon="⚠️" text="The Projects track could not be loaded." />
        <p className="dim mono" style={{ fontSize: 12, textAlign: "center" }}>
          {loadError}
        </p>
        <p className="faint" style={{ fontSize: 12, textAlign: "center" }}>
          This usually means <code>seeds/projects.json</code> and the Rust model have drifted
          apart — regenerate the seed with <code>python tools/gen_seed.py</code>.
        </p>
        <div className="row" style={{ justifyContent: "center", marginTop: 10 }}>
          <button onClick={load}>Try again</button>
        </div>
      </div>
    );
  }

  if (!track) return <div className="page">Loading…</div>;
  if (track.projects.length === 0) {
    return (
      <div className="page">
        <Empty icon="🧱" text="No projects are built yet." />
      </div>
    );
  }

  // With one project the track overview would be a single card, so `/projects`
  // redirects to that project rather than rendering the same view at a second
  // address the rest of the page never links to. The overview reappears — and
  // this redirect stops — the moment a second project lands.
  const only = track.projects.length === 1 ? track.projects[0] : undefined;
  if (project === undefined && only) {
    return <Navigate to={`/projects/${only.key}`} replace />;
  }

  const p = track.projects.find((x) => x.key === project);

  if (!p) {
    if (project !== undefined) {
      return (
        <div className="page">
          <Empty icon="🧱" text="Project not found." />
          <button onClick={() => nav("/projects")}>Back to Projects</button>
        </div>
      );
    }
    return <TrackOverview track={track} done={done} />;
  }

  if (moduleParam) {
    const m = p.modules.find((x) => x.key === moduleParam);
    if (!m) {
      return (
        <div className="page">
          <Empty icon="🧱" text="Module not found." />
          <button onClick={() => nav(`/projects/${p.key}`)}>Back to the project</button>
        </div>
      );
    }
    const authored = p.modules.filter((x) => x.authored);
    const idx = authored.findIndex((x) => x.key === m.key);
    return (
      <ModuleDetail
        key={m.key}
        project={p}
        module={m}
        harnessNote={track.harness_note}
        isDone={done.has(moduleKey(p.key, m.key))}
        onSetDone={(v) => setModuleDone(p.key, m.key, v)}
        prev={idx > 0 ? authored[idx - 1] : null}
        next={idx >= 0 && idx < authored.length - 1 ? authored[idx + 1] : null}
      />
    );
  }

  return <ProjectDetail track={track} project={p} done={done} />;
}

// ---------------------------------------------------------------------------
// Track overview — only reachable once there is more than one project.
// ---------------------------------------------------------------------------

function TrackOverview({ track, done }: { track: ProjectTrack; done: Set<string> }) {
  const nav = useNavigate();
  return (
    <div className="page">
      <h1 className="page-title">{track.title}</h1>
      <p className="page-sub">{track.subtitle}</p>
      {track.intro && (
        <div className="card" style={{ marginBottom: 14 }}>
          <Markdown>{track.intro}</Markdown>
        </div>
      )}
      <div className="grid cols-2">
        {track.projects.map((p) => {
          const authored = p.modules.filter((m) => m.authored);
          const n = authored.filter((m) => done.has(moduleKey(p.key, m.key))).length;
          return (
            <ClickableRow
              key={p.key}
              className="card"
              style={{ opacity: p.authored ? 1 : 0.55 }}
              disabled={!p.authored}
              onActivate={() => nav(`/projects/${p.key}`)}
            >
              <strong>
                {p.number}. {p.title}
              </strong>
              <p className="dim" style={{ margin: "6px 0 0", fontSize: 13 }}>
                {p.tagline}
              </p>
              <p className="faint" style={{ margin: "6px 0 0", fontSize: 12 }}>
                {n}/{authored.length} modules · {p.stack.join(" · ")}
              </p>
            </ClickableRow>
          );
        })}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Project detail — the destination, the contract, and the roadmap.
// ---------------------------------------------------------------------------

function ProjectDetail({
  track,
  project,
  done,
}: {
  track: ProjectTrack;
  project: Project;
  done: Set<string>;
}) {
  const nav = useNavigate();
  const sec = useCollapse(`project-overview:${project.key}`, false);
  // "How to work through this" is orientation, so it opens by default and gets
  // its own namespace to say so. On a single-project track the overview page
  // never renders, and this is the only place the track intro is ever shown.
  const introSec = useCollapse(`project-intro:${project.key}`, true);

  const authored = project.modules.filter((m) => m.authored);
  const doneCount = authored.filter((m) => done.has(moduleKey(project.key, m.key))).length;
  const nextModule =
    authored.find((m) => !done.has(moduleKey(project.key, m.key))) ?? authored[0];
  const pct = authored.length ? Math.round((doneCount / authored.length) * 100) : 0;
  const totalModules = project.modules.length;

  return (
    <div className="page">
      <h1 className="page-title">{project.title}</h1>
      <p className="page-sub">{project.tagline}</p>

      <div className="card" style={{ marginBottom: 18 }}>
        <div className="row" style={{ alignItems: "center", gap: 12 }}>
          <div style={{ flex: 1 }}>
            <div className="row" style={{ marginBottom: 6 }}>
              <strong>Your progress</strong>
              <span className="spacer" />
              <span className="dim mono">
                {doneCount}/{authored.length} built · {totalModules} planned
              </span>
            </div>
            <div className="progress">
              <span
                style={{
                  width: `${pct}%`,
                  background: pct === 100 ? "var(--good)" : "var(--accent)",
                }}
              />
            </div>
          </div>
          {nextModule && (
            <button className="primary" onClick={() => nav(`/projects/${project.key}/${nextModule.key}`)}>
              {doneCount === 0 ? "Start module 1 →" : `Resume · module ${nextModule.number} →`}
            </button>
          )}
        </div>
        <p className="faint" style={{ fontSize: 12, margin: "10px 0 0" }}>
          {project.stack.join(" · ")} · about {studyTime(project.est_minutes)} of building in
          total.{project.completion_note ? ` ${project.completion_note}` : ""}
        </p>
      </div>

      <div className="card" style={{ marginBottom: 14, borderColor: "var(--accent)" }}>
        <div className="io-label" style={{ color: "var(--accent)" }}>
          🎯 What you are building
        </div>
        <p style={{ marginBottom: project.why ? 8 : 0 }}>{project.goal}</p>
        {project.why && (
          <p className="dim" style={{ margin: 0, fontSize: 13 }}>
            💡 Why it matters: {project.why}
          </p>
        )}
      </div>

      {track.intro && (
        <Section
          title="📌 How to work through this"
          open={introSec.isOpen("intro")}
          onToggle={() => introSec.toggle("intro")}
        >
          <Markdown>{track.intro}</Markdown>
        </Section>
      )}

      {project.brief && <Markdown>{project.brief}</Markdown>}

      {project.endpoints.length > 0 && <EndpointTable endpoints={project.endpoints} caption="The finished application's contract. Every module below chips away at one or two of these rows." />}

      {project.setup && (
        <>
          <h3 style={{ margin: "18px 0 6px" }}>⚙️ Set up</h3>
          <Markdown>{project.setup}</Markdown>
        </>
      )}

      <h3 style={{ margin: "22px 0 4px" }}>🗺️ The roadmap</h3>
      <p className="dim" style={{ marginTop: 0, fontSize: 13 }}>
        {plural(totalModules, "module")} in {plural(project.roadmap.length, "phase")}. Each phase
        ends with something you can demonstrate — that is what makes it a phase rather than an
        arbitrary grouping.
      </p>

      {project.roadmap.map((phase) => {
        const mods = project.modules.filter((m) => m.phase === phase.key);
        const phaseDone = mods.filter(
          (m) => m.authored && done.has(moduleKey(project.key, m.key))
        ).length;
        const phaseAuthored = mods.filter((m) => m.authored).length;
        return (
          <div key={phase.key} className="card" style={{ marginBottom: 12 }}>
            <div className="row" style={{ alignItems: "flex-start", marginBottom: 4 }}>
              <strong>{phase.title}</strong>
              <span className="spacer" />
              {phaseAuthored > 0 && (
                <span className="dim mono" style={{ fontSize: 12 }}>
                  {phaseDone}/{phaseAuthored}
                </span>
              )}
            </div>
            <p className="dim" style={{ margin: "0 0 6px", fontSize: 13 }}>
              {phase.summary}
            </p>
            <p className="faint" style={{ margin: "0 0 10px", fontSize: 12 }}>
              🏁 Ends with: {phase.outcome}
            </p>
            {mods.map((m, i) => {
              const isDone = m.authored && done.has(moduleKey(project.key, m.key));
              return (
                <ClickableRow
                  key={m.key}
                  className="row"
                  style={{
                    gap: 8,
                    padding: "5px 0",
                    alignItems: "flex-start",
                    opacity: m.authored ? 1 : 0.5,
                    borderBottom: i < mods.length - 1 ? "1px solid var(--border)" : undefined,
                  }}
                  disabled={!m.authored}
                  title={m.authored ? `Open module ${m.number}` : "Not written yet"}
                  onActivate={() => nav(`/projects/${project.key}/${m.key}`)}
                >
                  <span
                    className="mono"
                    style={{ color: isDone ? "var(--good)" : "var(--accent)", width: 24 }}
                  >
                    {isDone ? "✓" : m.number}
                  </span>
                  <span style={{ flex: 1 }}>
                    {m.title}
                    {m.what && (
                      <span className="faint" style={{ fontSize: 12 }}>
                        {" "}
                        — {m.what}
                      </span>
                    )}
                  </span>
                  {m.authored ? (
                    m.est_minutes > 0 && (
                      <span className="dim mono" style={{ fontSize: 12 }}>
                        {studyTime(m.est_minutes)}
                      </span>
                    )
                  ) : (
                    <span className="badge">soon</span>
                  )}
                </ClickableRow>
              );
            })}
          </div>
        );
      })}

      {track.harness_note && (
        <Section
          title="🧪 How the exercises are judged"
          open={sec.isOpen("harness")}
          onToggle={() => sec.toggle("harness")}
          meta={<span className="badge">read once</span>}
        >
          <Markdown>{track.harness_note}</Markdown>
        </Section>
      )}

      {project.acceptance.length > 0 && (
        <Section
          title="✅ Acceptance — the finished application"
          open={sec.isOpen("acceptance")}
          onToggle={() => sec.toggle("acceptance")}
          meta={<span className="badge">{project.acceptance.length} checks</span>}
        >
          <div className="card" style={{ marginTop: 0 }}>
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {project.acceptance.map((a, i) => (
                <li key={i} style={{ marginBottom: 4 }}>
                  {a}
                </li>
              ))}
            </ul>
          </div>
        </Section>
      )}

      {project.manual_test && (
        <Section
          title="🔌 Try the finished thing yourself"
          open={sec.isOpen("manual")}
          onToggle={() => sec.toggle("manual")}
          // The badge names the tool the block actually uses. A project with a
          // contract is driven over HTTP; one without is driven from a shell.
          meta={<span className="badge">{project.endpoints.length > 0 ? "curl" : "shell"}</span>}
        >
          <Markdown>{project.manual_test}</Markdown>
        </Section>
      )}

      {project.stretch.length > 0 && (
        <Section
          title="🚀 Once it is done"
          open={sec.isOpen("stretch")}
          onToggle={() => sec.toggle("stretch")}
          meta={<span className="badge">{project.stretch.length} ideas</span>}
        >
          <div className="card" style={{ marginTop: 0 }}>
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {project.stretch.map((s, i) => (
                <li key={i} style={{ marginBottom: 6 }}>
                  {s}
                </li>
              ))}
            </ul>
          </div>
        </Section>
      )}

      {project.milestone && (
        <div className="card" style={{ marginTop: 16, borderColor: "var(--good)" }}>
          <div className="io-label" style={{ color: "var(--good)" }}>
            🎉 When you finish
          </div>
          <p style={{ margin: 0 }}>{project.milestone}</p>
        </div>
      )}
    </div>
  );
}

function EndpointTable({
  endpoints,
  caption,
  heading = "📋 The contract",
}: {
  endpoints: Project["endpoints"];
  caption: string;
  heading?: string;
}) {
  return (
    <>
      <h3 style={{ marginBottom: 6 }}>{heading}</h3>
      <p className="dim" style={{ marginTop: 0, fontSize: 13 }}>
        {caption}
      </p>
      <div className="card" style={{ overflowX: "auto", padding: 0 }}>
        <table className="data" style={{ cursor: "default" }}>
          <thead>
            <tr>
              <th style={{ cursor: "default" }}>Method</th>
              <th style={{ cursor: "default" }}>Path</th>
              <th style={{ cursor: "default" }}>Purpose</th>
              <th style={{ cursor: "default" }}>Request</th>
              <th style={{ cursor: "default" }}>Response</th>
              <th style={{ cursor: "default" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {endpoints.map((e, i) => (
              <tr key={i} style={{ cursor: "default" }}>
                <td className="mono" style={{ color: "var(--accent)", whiteSpace: "nowrap" }}>
                  {e.method}
                </td>
                <td className="mono" style={{ whiteSpace: "nowrap" }}>
                  {e.path}
                </td>
                <td>{e.purpose}</td>
                <td className="mono faint" style={{ fontSize: 12 }}>
                  {e.request || "—"}
                </td>
                <td className="mono faint" style={{ fontSize: 12 }}>
                  {e.response || "—"}
                </td>
                <td className="mono" style={{ whiteSpace: "nowrap", fontSize: 12 }}>
                  {e.status}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

// ---------------------------------------------------------------------------
// Module detail — the whole development process for one slice.
// ---------------------------------------------------------------------------

function ModuleDetail({
  project,
  module: mod,
  harnessNote,
  isDone,
  onSetDone,
  prev,
  next,
}: {
  project: Project;
  module: ProjectModule;
  harnessNote: string;
  isDone: boolean;
  onSetDone: (done: boolean) => void;
  prev: ProjectModule | null;
  next: ProjectModule | null;
}) {
  const nav = useNavigate();
  const toast = useToast();
  const [params, setParams] = useSearchParams();
  const [solvedEx, setSolvedEx] = useState<Set<string>>(() => solvedExercises());
  const [scrolledToBottom, setScrolledToBottom] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const celebrated = useRef(false);
  // Steps start collapsed: each open step mounts a Monaco editor per exercise,
  // and the contents card below is how you navigate them. Keyed by project as
  // well as module, because module keys are only unique within a project.
  const sec = useCollapse(`project-sec:${project.key}:${mod.key}`, false);
  const steps = mod.steps ?? [];
  const stepKeys = useMemo(() => steps.map((s) => s.key), [steps]);
  const phase = project.roadmap.find((p) => p.key === mod.phase);

  const scrollTo = (id: string) =>
    requestAnimationFrame(() =>
      document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" })
    );

  // Which step the URL points at. A module is a long page, so without this a
  // reload — or a link to "the bit about routing" — always lands at the top and
  // you scroll back down hunting for where you were.
  const stepParam = params.get("step");
  // The last `?step=` value acted on, so opening a step by hand does not get
  // undone by the effect below re-applying the URL.
  const appliedStep = useRef<string | null>(null);
  const setStepParam = useCallback(
    (key: string | null) =>
      setParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (key) next.set("step", key);
          else next.delete("step");
          return next;
        },
        { replace: true }
      ),
    [setParams]
  );

  function openStep(key: string) {
    appliedStep.current = key; // opened here, so the effect below needn't repeat it
    if (!sec.isOpen(key)) sec.toggle(key);
    setStepParam(key);
    scrollTo(`step-${key}`);
  }

  /** A step's own header was clicked: keep the URL pointing at what is open.
   *
   * Closing a step only clears `?step=` when it is the step the URL names —
   * and `appliedStep` tracks that either way, so folding away some other step
   * cannot leave the effect below thinking it has a link to re-apply and
   * yanking the page back up to it. */
  function toggleStep(key: string) {
    const opening = !sec.isOpen(key);
    const nextParam = opening ? key : stepParam === key ? null : stepParam;
    appliedStep.current = nextParam;
    sec.toggle(key);
    setStepParam(nextParam);
  }

  // Apply `?step=` once per value: open that step and scroll to it. The guard
  // matters because `sec.isOpen` changes identity whenever any section toggles,
  // and re-running this would yank the page back to the linked step.
  useEffect(() => {
    if (!stepParam || appliedStep.current === stepParam) return;
    if (!steps.some((s) => s.key === stepParam)) return;
    appliedStep.current = stepParam;
    if (!sec.isOpen(stepParam)) sec.toggle(stepParam);
    scrollTo(`step-${stepParam}`);
  }, [stepParam, steps, sec]);

  const gradableIds = useMemo(() => requiredExerciseIds(mod), [mod]);
  const allSolved = gradableIds.every((id) => solvedEx.has(id));
  const solvedCount = gradableIds.filter((id) => solvedEx.has(id)).length;

  // Where "pick up where I left off" goes: the first step still holding an
  // unsolved exercise, or the module build if the steps are all done.
  const firstUnsolvedStep = steps.find((s) =>
    (s.exercises ?? []).some((e) => !solvedEx.has(e.id))
  );
  const finalBuildUnsolved = !!mod.final_build && !solvedEx.has(mod.final_build.id);
  const canResume = !!firstUnsolvedStep || finalBuildUnsolved;

  function resume() {
    if (firstUnsolvedStep) openStep(firstUnsolvedStep.key);
    else scrollTo("module-build");
  }

  function handleSolved(id: string) {
    setSolvedEx(new Set(markExerciseSolved(id)));
  }

  /** Start the module over: forget its solved exercises and its ✓, so it can be
   * worked again from scratch. Drafts are deliberately kept — see
   * `unmarkExercisesSolved`. */
  function resetModule() {
    const ok = window.confirm(
      `Start module ${mod.number} over?\n\n` +
        `This clears ${plural(solvedCount, "solved exercise")} and its ✓ Done mark. ` +
        `The code you have written is kept.`
    );
    if (!ok) return;
    setSolvedEx(new Set(unmarkExercisesSolved(gradableIds)));
    celebrated.current = false; // so finishing it again celebrates again
    // Auto-completion needs the module read to the bottom *again*. Without this
    // a module with nothing to solve would re-complete itself the instant it
    // was reset, since "every exercise solved" is vacuously true for none.
    setScrolledToBottom(false);
    if (isDone) onSetDone(false);
    toast(`Module ${mod.number} reset.`);
  }

  useEffect(() => {
    const el = bottomRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) setScrolledToBottom(true);
      },
      { threshold: 0.01 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [mod.key]);

  useEffect(() => {
    if (!isDone && scrolledToBottom && allSolved && !celebrated.current) {
      celebrated.current = true;
      onSetDone(true);
      toast(
        mod.milestone
          ? `🎉 Module ${mod.number} complete! ${mod.milestone}`
          : `🎉 Module ${mod.number} complete!`
      );
    }
  }, [isDone, scrolledToBottom, allSolved, onSetDone, toast, mod.milestone, mod.number]);

  const newSyntax = (mod.syntax ?? []).filter((s) => !s.recap);
  const recapSyntax = (mod.syntax ?? []).filter((s) => s.recap);

  return (
    <div className="page">
      <div className="row" style={{ marginBottom: 4, justifyContent: "space-between" }}>
        <div className="row">
          <button className="ghost" onClick={() => nav(`/projects/${project.key}`)}>
            ← {project.title}
          </button>
          <span className="badge">Module {mod.number} of {project.modules.length}</span>
          {phase && <span className="badge">{phase.title}</span>}
          {mod.est_minutes > 0 && <span className="badge">⏱️ {studyTime(mod.est_minutes)}</span>}
        </div>
        <div className="row">
          {(isDone || solvedCount > 0) && (
            <button
              className="ghost"
              onClick={resetModule}
              title="Forget this module's solved exercises so you can work it again"
            >
              ↺ Reset
            </button>
          )}
          <button
            className="ghost"
            style={isDone ? { borderColor: "var(--good)", color: "var(--good)" } : undefined}
            onClick={() => onSetDone(!isDone)}
            title={isDone ? "Marked complete — click to undo" : "Mark this module complete"}
          >
            {isDone ? "✓ Done" : "Mark done"}
          </button>
        </div>
      </div>

      <h1 className="page-title" style={{ marginTop: 6 }}>
        {mod.title}
      </h1>
      <p className="page-sub">{mod.what}</p>

      {/* The same progress bar the project page shows, scoped to this module —
          previously the only word on how far through you were was a line of
          small print below the very last section. */}
      {gradableIds.length > 0 && (
        <div className="row" style={{ alignItems: "center", gap: 10, margin: "0 0 16px" }}>
          <div className="progress" style={{ flex: 1 }}>
            <span
              style={{
                width: `${Math.round((solvedCount / gradableIds.length) * 100)}%`,
                background: allSolved ? "var(--good)" : "var(--accent)",
              }}
            />
          </div>
          <span className="dim mono" style={{ fontSize: 12, whiteSpace: "nowrap" }}>
            {solvedCount}/{gradableIds.length} solved
          </span>
        </div>
      )}

      {/* 1. WHY — the problem the last module left behind. */}
      {mod.why && (
        <div className="card" style={{ marginBottom: 14, borderColor: "var(--accent)" }}>
          <div className="io-label" style={{ color: "var(--accent)" }}>
            💡 Why this module exists
          </div>
          <p style={{ margin: 0 }}>{mod.why}</p>
        </div>
      )}

      {/* 2. WHERE — roadmap position and the thing it delivers. */}
      <div className="card" style={{ marginBottom: 14 }}>
        <div className="io-label">🎯 Goal</div>
        <p style={{ margin: "0 0 8px" }}>{mod.goal}</p>
        {mod.deliverable && (
          <p className="dim" style={{ margin: 0, fontSize: 13 }}>
            📦 You will end up with: {mod.deliverable}
          </p>
        )}
        {mod.builds_on.length > 0 && (
          <p className="faint" style={{ margin: "8px 0 0", fontSize: 12 }}>
            🧱 Builds on: {mod.builds_on.join(", ")}
            {mod.concepts.length > 0 && ` · ${mod.concepts.join(" · ")}`}
          </p>
        )}
      </div>

      {mod.objectives.length > 0 && (
        <div className="card" style={{ marginBottom: 14 }}>
          <div className="io-label">By the end of this module you can…</div>
          <ul style={{ margin: "6px 0 0", paddingLeft: 20 }}>
            {mod.objectives.map((o, i) => (
              <li key={i} style={{ marginBottom: 2 }}>
                {o}
              </li>
            ))}
          </ul>
        </div>
      )}

      {mod.brief && <Markdown>{mod.brief}</Markdown>}

      {mod.endpoints.length > 0 && (
        <EndpointTable
          endpoints={mod.endpoints}
          heading="📋 This module's rows"
          caption="The part of the contract this module implements."
        />
      )}

      {/* 3. SYNTAX — everything the module needs, before it is used. */}
      {newSyntax.length > 0 && (
        <>
          <h3 style={{ margin: "22px 0 4px" }}>🔤 The syntax you need</h3>
          <p className="dim" style={{ marginTop: 0, fontSize: 13 }}>
            Everything this module uses, taught before it is used. Nothing below assumes syntax the
            project has not already shown you.
          </p>
          {newSyntax.map((s, i) => (
            <SyntaxCard key={i} item={s} />
          ))}
        </>
      )}

      {recapSyntax.length > 0 && (
        <Section
          title="↩️ Already covered — a reminder"
          open={sec.isOpen("recap")}
          onToggle={() => sec.toggle("recap")}
          meta={<span className="badge">{recapSyntax.length} from earlier modules</span>}
        >
          {recapSyntax.map((s, i) => (
            <SyntaxCard key={i} item={s} dim />
          ))}
        </Section>
      )}

      {/* 4. DO IT — ordered steps, each with a checkpoint. */}
      {steps.length > 0 && (
        <div className="card" style={{ marginBottom: 14, marginTop: 18 }}>
          <div className="row" style={{ marginBottom: 8 }}>
            <div className="io-label" style={{ margin: 0 }}>
              🪜 Build it — these are in order
            </div>
            <span className="spacer" />
            {canResume && solvedCount > 0 && (
              <button
                className="ghost"
                style={{ padding: "2px 8px", fontSize: 12 }}
                onClick={resume}
                title="Open the first step with an exercise you haven't solved"
              >
                ↳ Pick up where I left off
              </button>
            )}
            <button
              className="ghost"
              style={{ padding: "2px 8px", fontSize: 12 }}
              onClick={() => sec.setAll(stepKeys, true)}
            >
              Expand all
            </button>
            <button
              className="ghost"
              style={{ padding: "2px 8px", fontSize: 12 }}
              onClick={() => sec.setAll(stepKeys, false)}
            >
              Collapse all
            </button>
          </div>
          {steps.map((step, si) => {
            const ids = (step.exercises ?? []).map((e) => e.id);
            const n = ids.filter((id) => solvedEx.has(id)).length;
            const complete = ids.length > 0 && n === ids.length;
            return (
              <ClickableRow
                key={step.key}
                className="row"
                style={{
                  gap: 8,
                  padding: "5px 0",
                  borderBottom: si < steps.length - 1 ? "1px solid var(--border)" : undefined,
                }}
                title={`Jump to step ${si + 1}`}
                onActivate={() => openStep(step.key)}
              >
                <span style={{ color: complete ? "var(--good)" : "var(--accent)", width: 18 }}>
                  {complete ? "✓" : si + 1}
                </span>
                <span style={{ flex: 1 }}>
                  {step.title}
                  {step.what && (
                    <span className="faint" style={{ fontSize: 12 }}>
                      {" "}
                      — {step.what}
                    </span>
                  )}
                </span>
                {ids.length > 0 && (
                  <span className="dim mono" style={{ fontSize: 12 }}>
                    {n}/{ids.length}
                  </span>
                )}
              </ClickableRow>
            );
          })}
        </div>
      )}

      {steps.map((step, si) => (
        <div key={step.key} id={`step-${step.key}`}>
          <Section
            title={`Step ${si + 1}. ${step.title}`}
            open={sec.isOpen(step.key)}
            onToggle={() => toggleStep(step.key)}
            meta={
              <span className="dim" style={{ fontSize: 12 }}>
                {solvedLabel(step.exercises, solvedEx)}
              </span>
            }
          >
            <StepBody step={step} onSolved={handleSolved} />
          </Section>
        </div>
      ))}

      {/* 5. DID I GET IT — the module build, then the reveal. */}
      {mod.final_build && (
        <div id="module-build">
          <div className="divider" />
          <h2 style={{ marginBottom: 4 }}>🏁 Module build</h2>
          <p className="dim" style={{ marginTop: 0 }}>
            Everything above, assembled. This is the module.
          </p>
          <ExerciseCard index={1} exercise={mod.final_build} challenge onSolved={handleSolved} />
        </div>
      )}

      {mod.acceptance.length > 0 && (
        <>
          <div className="divider" />
          <h3>✅ Acceptance checklist</h3>
          <p className="dim" style={{ marginTop: -4 }}>
            Run through these against <em>your own</em> file before moving on.
          </p>
          <div className="card">
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {mod.acceptance.map((a, i) => (
                <li key={i} style={{ marginBottom: 4 }}>
                  {a}
                </li>
              ))}
            </ul>
          </div>
        </>
      )}

      {mod.manual_test && (
        <Section
          title="🔌 Try it yourself"
          open={sec.isOpen("manual")}
          onToggle={() => sec.toggle("manual")}
          meta={<span className="badge">curl</span>}
        >
          <Markdown>{mod.manual_test}</Markdown>
        </Section>
      )}

      {mod.reference && (
        <ReferenceReveal
          reference={mod.reference}
          revealLabel="Reveal the solution for this module"
          hideLabel="Hide the reference implementation"
          note="One way to write it — not the only way. Compare it with yours rather than replacing yours with it; where it differs, work out which of you is right."
        />
      )}

      {mod.stretch.length > 0 && (
        <Section
          title="🚀 Take it further"
          open={sec.isOpen("stretch")}
          onToggle={() => sec.toggle("stretch")}
          meta={<span className="badge">{mod.stretch.length} ideas</span>}
        >
          <div className="card" style={{ marginTop: 0 }}>
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {mod.stretch.map((s, i) => (
                <li key={i} style={{ marginBottom: 6 }}>
                  {s}
                </li>
              ))}
            </ul>
          </div>
        </Section>
      )}

      {mod.self_check.length > 0 && (
        <>
          <div className="divider" />
          <h3>🧠 Self-check</h3>
          <p className="dim" style={{ marginTop: -4 }}>
            Before you move on, make sure you can honestly say yes to each of these:
          </p>
          <div className="card">
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {mod.self_check.map((s, i) => (
                <li key={i} style={{ marginBottom: 4 }}>
                  {s}
                </li>
              ))}
            </ul>
          </div>
        </>
      )}

      {mod.review.length > 0 && (
        <>
          <div className="divider" />
          <h3>🔁 End-of-module review</h3>
          <p className="dim" style={{ marginTop: -4 }}>
            A quick mixed quiz — some of these reach back to earlier modules.
          </p>
          <QuizSection questions={mod.review} />
        </>
      )}

      {mod.glossary.length > 0 && (
        <Section
          title="📖 Glossary"
          open={sec.isOpen("glossary")}
          onToggle={() => sec.toggle("glossary")}
          meta={<span className="badge">{mod.glossary.length} terms</span>}
        >
          <div className="card" style={{ marginTop: 0 }}>
            {mod.glossary.map((g, i) => (
              <div
                key={i}
                style={{
                  padding: "5px 0",
                  borderBottom: i < mod.glossary.length - 1 ? "1px solid var(--border)" : undefined,
                }}
              >
                <code style={{ color: "var(--accent)" }}>{g.term}</code> — {g.def}
              </div>
            ))}
          </div>
        </Section>
      )}

      {mod.cheatsheet && (
        <Section
          title="🧾 Cheat sheet"
          open={sec.isOpen("cheatsheet")}
          onToggle={() => sec.toggle("cheatsheet")}
        >
          <Markdown>{mod.cheatsheet}</Markdown>
        </Section>
      )}

      {mod.milestone && (
        <div className="card" style={{ marginTop: 16, borderColor: "var(--good)" }}>
          <div className="io-label" style={{ color: "var(--good)" }}>
            🎉 Milestone
          </div>
          <p style={{ margin: 0 }}>{mod.milestone}</p>
        </div>
      )}

      {harnessNote && (
        <Section
          title="🧪 How the exercises are judged"
          open={sec.isOpen("harness")}
          onToggle={() => sec.toggle("harness")}
        >
          <Markdown>{harnessNote}</Markdown>
        </Section>
      )}

      {!isDone && (
        <p className="faint" style={{ fontSize: 12, marginTop: 24, textAlign: "center" }}>
          {gradableIds.length > 0
            ? `This module marks itself ✓ Done once you've read to here and solved its ${gradableIds.length} exercise${gradableIds.length === 1 ? "" : "s"}${allSolved ? " — all solved!" : ` (${solvedCount}/${gradableIds.length} solved)`}.`
            : "This module marks itself ✓ Done once you've read to here."}
        </p>
      )}

      <div className="row" style={{ marginTop: 20, justifyContent: "space-between" }}>
        {prev ? (
          <button className="ghost" onClick={() => nav(`/projects/${project.key}/${prev.key}`)}>
            ← {prev.number}. {prev.title}
          </button>
        ) : (
          <span />
        )}
        {next ? (
          <button className="primary" onClick={() => nav(`/projects/${project.key}/${next.key}`)}>
            {next.number}. {next.title} →
          </button>
        ) : (
          <button className="ghost" onClick={() => nav(`/projects/${project.key}`)}>
            Back to the roadmap
          </button>
        )}
      </div>

      {/* Sentinel: intersecting means the module has been read to the bottom. */}
      <div ref={bottomRef} style={{ height: 1 }} />
    </div>
  );
}

function SyntaxCard({ item, dim = false }: { item: SyntaxItem; dim?: boolean }) {
  return (
    <div className="card" style={{ marginBottom: 10, opacity: dim ? 0.75 : 1 }}>
      <code
        className="mono"
        style={{ color: "var(--accent)", fontSize: 13, display: "block", marginBottom: 6 }}
      >
        {item.form}
      </code>
      {item.means && <p style={{ margin: "0 0 8px", fontSize: 14 }}>{item.means}</p>}
      {item.example && <Markdown>{"```ts\n" + item.example.trimEnd() + "\n```"}</Markdown>}
      {item.note && (
        <p className="dim" style={{ margin: "6px 0 0", fontSize: 13 }}>
          ⚠️ {item.note}
        </p>
      )}
    </div>
  );
}

// This track's own wording for the shared exercise sections. Only the two that
// mean something different here are retuned: a challenge is not a puzzle, it is
// the next piece of the application.
const STEP_SECTION_WORDING = {
  fix: { blurb: "This program is wrong. Find the mistake and fix it so the tests pass." },
  challenge: { heading: "🏗️ Build it" },
};

function StepBody({ step, onSolved }: { step: BackendStep; onSolved: (id: string) => void }) {
  const exercises = step.exercises ?? [];
  const warmup = step.warmup ?? [];
  const quiz = step.quiz ?? [];

  return (
    <div>
      {step.what && (
        <p className="dim" style={{ marginTop: 0 }}>
          {step.what}
        </p>
      )}

      <Markdown>{step.instructions}</Markdown>

      {step.checkpoint && (
        <div className="card" style={{ borderColor: "var(--good)", marginTop: 12 }}>
          <div className="io-label" style={{ color: "var(--good)" }}>
            ✅ Checkpoint — you're done with this step when…
          </div>
          <Markdown>{step.checkpoint}</Markdown>
        </div>
      )}

      {step.pitfalls.length > 0 && (
        <div className="card" style={{ borderColor: "var(--bad)", marginTop: 12 }}>
          <div className="io-label" style={{ color: "var(--bad)" }}>
            ⚠️ Things that will cost you an hour
          </div>
          <ul style={{ margin: "4px 0 0", paddingLeft: 20 }}>
            {step.pitfalls.map((p, i) => (
              <li key={i} style={{ marginBottom: 4 }}>
                {p}
              </li>
            ))}
          </ul>
        </div>
      )}

      {warmup.length > 0 && (
        <>
          <h4>🔮 Work it out first</h4>
          <p className="dim" style={{ marginTop: -4 }}>
            Answer before you read on.
          </p>
          <QuizSection questions={warmup} />
        </>
      )}

      <ExerciseSections
        exercises={exercises}
        onSolved={onSolved}
        overrides={STEP_SECTION_WORDING}
      />

      {quiz.length > 0 && (
        <>
          <h4>❓ Check yourself</h4>
          <QuizSection questions={quiz} />
        </>
      )}
    </div>
  );
}
