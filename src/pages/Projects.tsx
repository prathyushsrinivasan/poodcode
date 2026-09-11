import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { Navigate, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api } from "../api";
import type {
  BackendStep,
  Project,
  ProjectModule,
  ProjectTrack,
  SyntaxItem,
} from "../types";
import { InlineMarkdown, Markdown } from "../components/Markdown";
import { ExerciseCard, QuizSection } from "../components/LearnExercise";
import { ExerciseSections } from "../components/ExerciseSections";
import { ReferenceReveal } from "../components/ReferenceReveal";
import { DiffStatBadge, DiffView } from "../components/DiffView";
import { Section, useCollapse } from "../components/Collapsible";
import ProjectHistory from "./ProjectHistory";
import ProjectReview from "./ProjectReview";
import ProjectWorkbench from "./ProjectWorkbench";
import { diffSources, diffStats } from "../lib/lineDiff";
import { collectQuestions } from "../lib/projectReview";
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
import {
  buildCheatsheetIndex,
  buildCheckIndex,
  buildContractIndex,
  buildGlossaryIndex,
  buildPitfallIndex,
  buildSyntaxIndex,
  groupByModule,
  isRetired,
  matchesQuery,
  type ContractEntry,
  type GlossaryEntry,
  type NoteEntry,
} from "../lib/projectIndex";

// Module completion is tracked in the same SQLite-backed chapter-done set as
// the Learn tab, the courses and the Backend Lab, under a namespaced key so it
// can never collide with a concept key, a course week or a backend project.
const moduleKey = (projectKey: string, key: string) => `project:${projectKey}:${key}`;

/** Every judged exercise required to complete a module. */
const requiredExerciseIds = (m: ProjectModule) => collectExerciseIds(m.steps, m.final_build);

/** The project-level pages that are not a module. Each has a static route in
 * App.tsx, so none can be shadowed by a module that one day takes the key. */
export type ProjectView = "reference" | "history" | "workbench" | "review";

export default function Projects({ view }: { view?: ProjectView } = {}) {
  const { project, module: moduleParam } = useParams();
  const [track, setTrack] = useState<ProjectTrack | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [done, setDone] = useState<Set<string>>(new Set());
  // The review page chooses its default scope from what is finished, so it
  // must not render against the empty set that stands in until this loads.
  const [doneLoaded, setDoneLoaded] = useState(false);
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
    loadDoneChapters()
      .then(setDone)
      .catch(() => {})
      .finally(() => setDoneLoaded(true));
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

  if (view === "reference") return <ProjectReference project={p} />;
  if (view === "history") return <ProjectHistory project={p} />;
  // Keyed by project: both hold per-project state initialised on mount.
  if (view === "workbench") return <ProjectWorkbench key={p.key} project={p} />;
  if (view === "review") {
    if (!doneLoaded) return <div className="page">Loading…</div>;
    const doneKeys = new Set(
      p.modules.filter((m) => done.has(moduleKey(p.key, m.key))).map((m) => m.key)
    );
    return <ProjectReview key={p.key} project={p} doneKeys={doneKeys} />;
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

      <ProjectTools project={project} doneCount={doneCount} />

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

/** The four project-level pages, each with the one line that says when you
 * would open it — they are used at very different moments, and a row of bare
 * icons would not say that. */
function ProjectTools({ project, doneCount }: { project: Project; doneCount: number }) {
  const nav = useNavigate();
  const snapshots = project.modules.filter((m) => m.authored && m.reference.trim()).length;
  const builds = project.modules.filter((m) => m.authored && m.final_build).length;
  const questions = useMemo(() => collectQuestions(project).length, [project]);
  const tools = [
    {
      path: "reference",
      icon: "📚",
      title: "Handbook",
      blurb: "Every form, term, trap and check, searchable. Open it when something is broken.",
      meta: "6 indexes",
    },
    {
      path: "history",
      icon: "🕰️",
      title: "Build history",
      blurb: "What each module changed in the file, as a diff. The build ladder, in code.",
      meta: `${snapshots} snapshots`,
    },
    {
      path: "workbench",
      icon: "🧪",
      title: "Workbench",
      blurb: "Load any module's build, edit it, and run your own input against it.",
      meta: `${builds} builds`,
    },
    {
      path: "review",
      icon: "🔁",
      title: "Review",
      blurb:
        doneCount > 0
          ? "Mixed questions from the modules you've finished — misses come back first."
          : "Mixed questions from across the project, asked again out of order.",
      meta: `${questions} questions`,
    },
  ];
  return (
    <div className="grid cols-4" style={{ marginBottom: 18 }}>
      {tools.map((t) => (
        <ClickableRow
          key={t.path}
          className="card"
          style={{ marginBottom: 0 }}
          title={`Open ${t.title}`}
          onActivate={() => nav(`/projects/${project.key}/${t.path}`)}
        >
          <div className="row" style={{ alignItems: "baseline" }}>
            <strong>
              {t.icon} {t.title}
            </strong>
            <span className="spacer" />
            <span className="faint mono" style={{ fontSize: 11 }}>
              {t.meta}
            </span>
          </div>
          <p className="dim" style={{ margin: "6px 0 0", fontSize: 12.5 }}>
            {t.blurb}
          </p>
        </ClickableRow>
      ))}
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
// Reference — the project's handbook: everything four kinds of module writing
// add up to, gathered into one searchable page.
//
// The track's claim is that nothing is used before it is taught, and until now
// the evidence for that was spread one card at a time across module pages. By
// module 8 the Todo API teaches around fifty forms, names sixty terms, warns
// about forty traps and carries sixty acceptance checks — every one of them
// inside a module you have already finished, half of them inside a collapsed
// step. Nothing here is new data; see src/lib/projectIndex.ts for the
// gathering, and note what each tab is FOR, because they are read at different
// moments:
//
//   Syntax     read in order — top to bottom it is the syllabus
//   Glossary   arrived at with a word in hand — A-Z
//   Pitfalls   read when something is broken, which is never in the module
//              that warned you about it
//   Checks     read when something that used to work has stopped
//
// The last two are why this stopped being "the reference" and became the
// handbook: they are the tabs you open in a hurry.
// ---------------------------------------------------------------------------

type RefTab = "syntax" | "glossary" | "pitfalls" | "checks" | "contract" | "cheatsheets";

const REF_TABS: {
  key: RefTab;
  label: string;
  /** What one row is, for the "n of m … match" line and the empty state. */
  unit: string;
  placeholder: string;
  blurb: string;
}[] = [
  {
    key: "syntax",
    label: "🔤 Syntax",
    unit: "form",
    placeholder: "Search syntax, meanings, gotchas…",
    blurb:
      "Every piece of TypeScript the project teaches, in the order it is introduced. Read top to " +
      "bottom and this is the exact order the project puts the language in front of you.",
  },
  {
    key: "glossary",
    label: "📖 Glossary",
    unit: "term",
    placeholder: "Search terms and definitions…",
    blurb:
      "Every term the project defines, A-Z — because this is the list you arrive at with a word " +
      "in hand rather than one you read through.",
  },
  {
    key: "pitfalls",
    label: "⚠️ Pitfalls",
    unit: "trap",
    placeholder: "Search by symptom — “hangs”, “headers sent”, “404”…",
    blurb:
      "Every mistake the project warns you about, gathered out of the steps they were written in. " +
      "Search by the symptom you are looking at, not by what you think caused it.",
  },
  {
    key: "checks",
    label: "✅ Checks",
    unit: "check",
    placeholder: "Search the acceptance checks…",
    blurb:
      "Every module's acceptance checklist. The project page has the finished application's list; " +
      "this is what has to be true at each module along the way — the list to walk down when " +
      "something that used to work has stopped.",
  },
  {
    key: "contract",
    label: "📋 Contract",
    unit: "route",
    placeholder: "Search by path, verb, status or purpose…",
    blurb:
      "The contract as it stands today, in the order the project builds it — which module each " +
      "route arrived in, and which later modules changed it. Rows a module merely re-lists " +
      "unchanged are not counted as changes.",
  },
  {
    key: "cheatsheets",
    label: "🧾 Cheat sheets",
    unit: "sheet",
    placeholder: "Search every cheat sheet…",
    blurb:
      "Every module's cheat sheet, end to end. The one tab meant to be read as a single page — " +
      "the shortest complete description of everything the project has built so far.",
  },
];

function ProjectReference({ project }: { project: Project }) {
  const nav = useNavigate();
  const [tab, setTab] = useState<RefTab>("syntax");
  const [q, setQ] = useState("");

  const syntax = useMemo(() => buildSyntaxIndex(project), [project]);
  const glossary = useMemo(() => buildGlossaryIndex(project), [project]);
  const pitfalls = useMemo(() => buildPitfallIndex(project), [project]);
  const checks = useMemo(() => buildCheckIndex(project), [project]);
  const contract = useMemo(() => buildContractIndex(project), [project]);
  const sheets = useMemo(() => buildCheatsheetIndex(project), [project]);

  const shownSyntax = useMemo(() => syntax.filter((e) => matchesQuery(e, q)), [syntax, q]);
  const shownGlossary = useMemo(() => glossary.filter((e) => matchesQuery(e, q)), [glossary, q]);
  const shownPitfalls = useMemo(() => pitfalls.filter((e) => matchesQuery(e, q)), [pitfalls, q]);
  const shownChecks = useMemo(() => checks.filter((e) => matchesQuery(e, q)), [checks, q]);
  const shownContract = useMemo(() => contract.filter((e) => matchesQuery(e, q)), [contract, q]);
  const shownSheets = useMemo(() => sheets.filter((e) => matchesQuery(e, q)), [sheets, q]);

  const syntaxGroups = useMemo(() => groupByModule(shownSyntax), [shownSyntax]);
  const pitfallGroups = useMemo(() => groupByModule(shownPitfalls), [shownPitfalls]);
  const checkGroups = useMemo(() => groupByModule(shownChecks), [shownChecks]);

  const authored = project.modules.filter((m) => m.authored).length;
  const total = project.modules.length;

  const counts: Record<RefTab, number> = {
    syntax: syntax.length,
    glossary: glossary.length,
    pitfalls: pitfalls.length,
    checks: checks.length,
    contract: contract.length,
    cheatsheets: sheets.length,
  };
  const shownCounts: Record<RefTab, number> = {
    syntax: shownSyntax.length,
    glossary: shownGlossary.length,
    pitfalls: shownPitfalls.length,
    checks: shownChecks.length,
    contract: shownContract.length,
    cheatsheets: shownSheets.length,
  };
  const active = REF_TABS.find((t) => t.key === tab) ?? REF_TABS[0]!;
  const shown = shownCounts[tab];
  const all = counts[tab];
  /** Tabs other than this one that the current query also hits. One search box
   * over four indexes makes these the most useful thing on screen: a query that
   * finds nothing here is very often sitting in the next tab along. */
  const elsewhere = REF_TABS.filter((t) => t.key !== tab && shownCounts[t.key] > 0);

  const openModule = (key: string) => nav(`/projects/${project.key}/${key}`);
  /** Deep-link to the step a pitfall was written in. `ModuleDetail` reads
   * `?step=` and opens and scrolls to it, so a trap found here lands on the
   * paragraph that explains it rather than the top of a long module page. */
  const openStep = (moduleKey: string, stepKey: string) =>
    nav(`/projects/${project.key}/${moduleKey}${stepKey ? `?step=${stepKey}` : ""}`);

  return (
    <div className="page">
      <div className="row" style={{ marginBottom: 4 }}>
        <button className="ghost" onClick={() => nav(`/projects/${project.key}`)}>
          ← {project.title}
        </button>
        {/* The tab buttons carry the per-tab counts, so this says the thing
            they cannot: how much of the project is in here at all. */}
        <span className="badge">
          {authored}/{total} modules written
        </span>
      </div>

      <h1 className="page-title" style={{ marginTop: 6 }}>
        Handbook
      </h1>
      <p className="page-sub">
        Everything {project.title} teaches, gathered from all {authored} written{" "}
        {authored === 1 ? "module" : "modules"} — the syllabus, the vocabulary, every trap it warns
        you about and every check it asks you to run.
      </p>

      <div className="row" style={{ gap: 8, margin: "0 0 10px", alignItems: "center", flexWrap: "wrap" }}>
        {REF_TABS.map((t) => (
          <button
            key={t.key}
            className={tab === t.key ? "primary" : "ghost"}
            onClick={() => setTab(t.key)}
            aria-pressed={tab === t.key}
          >
            {t.label} · {counts[t.key]}
          </button>
        ))}
        <span className="spacer" />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={active.placeholder}
          style={{ minWidth: 240 }}
          aria-label="Search the handbook"
        />
        {q && (
          <button className="ghost" onClick={() => setQ("")} title="Clear the search">
            ✕
          </button>
        )}
      </div>

      <p className="dim" style={{ fontSize: 13, margin: "0 0 12px" }}>
        {active.blurb}
      </p>

      {q && (
        <p className="faint" style={{ fontSize: 12, margin: "0 0 10px" }}>
          {plural(shown, active.unit)} of {all} match “{q}”
          {elsewhere.length > 0 && (
            <>
              {" · also "}
              {elsewhere.map((t, i) => (
                <span key={t.key}>
                  {i > 0 && ", "}
                  <ClickableRow
                    style={{
                      display: "inline",
                      color: "var(--accent)",
                      textDecoration: "underline",
                    }}
                    title={`Show the ${shownCounts[t.key]} matching under ${t.label}`}
                    onActivate={() => setTab(t.key)}
                  >
                    {shownCounts[t.key]} in {t.label}
                  </ClickableRow>
                </span>
              ))}
            </>
          )}
        </p>
      )}

      {shown === 0 ? (
        <Empty
          icon="🔍"
          text={
            q
              ? `No ${active.unit} in ${active.label} matches “${q}”.`
              : `This project has not written any ${active.unit}s yet.`
          }
        />
      ) : tab === "syntax" ? (
        syntaxGroups.map((group) => (
          <ModuleGroup
            key={group.ref.moduleKey}
            group={group}
            count={group.entries.length}
            unit="form"
            onOpenModule={openModule}
          >
            {group.entries.map((e) => (
              <SyntaxCard key={e.form} item={e} />
            ))}
          </ModuleGroup>
        ))
      ) : tab === "glossary" ? (
        <div className="card">
          {shownGlossary.map((e, i) => (
            <GlossaryRow
              key={e.term}
              entry={e}
              last={i === shownGlossary.length - 1}
              onOpenModule={openModule}
            />
          ))}
        </div>
      ) : tab === "pitfalls" ? (
        pitfallGroups.map((group) => (
          <ModuleGroup
            key={group.ref.moduleKey}
            group={group}
            count={group.entries.length}
            unit="trap"
            onOpenModule={openModule}
          >
            <div className="card" style={{ borderColor: "var(--bad)" }}>
              {group.entries.map((e, i) => (
                <NoteRow
                  key={`${e.stepKey}:${i}`}
                  entry={e}
                  last={i === group.entries.length - 1}
                  marker="⚠️"
                  onOpen={openStep}
                />
              ))}
            </div>
          </ModuleGroup>
        ))
      ) : tab === "checks" ? (
        checkGroups.map((group) => (
          <ModuleGroup
            key={group.ref.moduleKey}
            group={group}
            count={group.entries.length}
            unit="check"
            onOpenModule={openModule}
          >
            <div className="card" style={{ borderColor: "var(--good)" }}>
              {group.entries.map((e, i) => (
                <NoteRow
                  key={i}
                  entry={e}
                  last={i === group.entries.length - 1}
                  marker="☐"
                  onOpen={openStep}
                />
              ))}
            </div>
          </ModuleGroup>
        ))
      ) : tab === "contract" ? (
        <ContractTable rows={shownContract} onOpenModule={openModule} />
      ) : (
        shownSheets.map((sheet) => (
          <div key={sheet.moduleKey} style={{ marginBottom: 22 }}>
            <ClickableRow
              className="row"
              style={{ alignItems: "baseline", gap: 8, marginBottom: 6 }}
              title={`Open module ${sheet.moduleNumber}`}
              onActivate={() => openModule(sheet.moduleKey)}
            >
              <span className="mono" style={{ color: "var(--accent)" }}>
                {sheet.moduleNumber}
              </span>
              <strong>{sheet.moduleTitle}</strong>
            </ClickableRow>
            <Markdown>{sheet.text}</Markdown>
          </div>
        ))
      )}

      {authored < total && (
        <p className="faint" style={{ fontSize: 12, marginTop: 20, textAlign: "center" }}>
          {authored} of {total} modules are written. This page grows with them.
        </p>
      )}
    </div>
  );
}

/** The contract as built so far: every route, when it arrived, and every later
 * module that changed it.
 *
 * This is the one view in the app that reads the project as a *ladder* rather
 * than a list — the "Added" column in order is the order the API grew. The
 * "Changed in" column is the part that could not be got any other way: module
 * 18 replaces `GET /todos`'s bare array with an envelope on purpose, and until
 * now the only record of that was a paragraph inside module 18. */
function ContractTable({
  rows,
  onOpenModule,
}: {
  rows: ContractEntry[];
  onOpenModule: (key: string) => void;
}) {
  return (
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
            <th style={{ cursor: "default" }}>Added</th>
            <th style={{ cursor: "default" }}>Changed in</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((e) => {
            // A route a later module removed. Kept in the table rather than
            // dropped, because "this used to exist and does not any more" is
            // part of the contract's history and answers a real question.
            const gone = isRetired(e);
            return (
            <tr key={`${e.method} ${e.path}`} style={{ cursor: "default", opacity: gone ? 0.5 : 1 }}>
              <td className="mono" style={{ color: "var(--accent)", whiteSpace: "nowrap" }}>
                {e.method}
              </td>
              <td
                className="mono"
                style={{ whiteSpace: "nowrap", textDecoration: gone ? "line-through" : undefined }}
              >
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
              <td>
                <ClickableRow
                  className="badge"
                  title={`Added in module ${e.moduleNumber}: ${e.moduleTitle}`}
                  onActivate={() => onOpenModule(e.moduleKey)}
                >
                  M{e.moduleNumber}
                </ClickableRow>
              </td>
              <td>
                {e.revisions.length === 0 ? (
                  <span className="faint">—</span>
                ) : (
                  e.revisions.map((r) => (
                    <ClickableRow
                      key={r.moduleKey}
                      className="badge"
                      style={{ marginRight: 4 }}
                      title={
                        gone && r === e.revisions[e.revisions.length - 1]
                          ? `Retired in module ${r.moduleNumber}: ${r.moduleTitle}`
                          : `Changed in module ${r.moduleNumber}: ${r.moduleTitle}`
                      }
                      onActivate={() => onOpenModule(r.moduleKey)}
                    >
                      M{r.moduleNumber}
                    </ClickableRow>
                  ))
                )}
              </td>
            </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

/** A module heading with its rows underneath — shared by the three tabs that
 * group by module, so they cannot drift apart in spacing or wording. */
function ModuleGroup({
  group,
  count,
  unit,
  onOpenModule,
  children,
}: {
  group: { ref: { moduleKey: string; moduleNumber: number; moduleTitle: string } };
  count: number;
  unit: string;
  onOpenModule: (key: string) => void;
  children: ReactNode;
}) {
  return (
    <div style={{ marginBottom: 18 }}>
      <ClickableRow
        className="row"
        style={{ alignItems: "baseline", gap: 8, marginBottom: 6 }}
        title={`Open module ${group.ref.moduleNumber}`}
        onActivate={() => onOpenModule(group.ref.moduleKey)}
      >
        <span className="mono" style={{ color: "var(--accent)" }}>
          {group.ref.moduleNumber}
        </span>
        <strong>{group.ref.moduleTitle}</strong>
        <span className="spacer" />
        <span className="dim mono" style={{ fontSize: 12 }}>
          {plural(count, unit)}
        </span>
      </ClickableRow>
      {children}
    </div>
  );
}

/** One pitfall or acceptance check. A pitfall carries the step it was written
 * in and links straight to it; a check belongs to the module as a whole. */
function NoteRow({
  entry,
  last,
  marker,
  onOpen,
}: {
  entry: NoteEntry;
  last: boolean;
  marker: string;
  onOpen: (moduleKey: string, stepKey: string) => void;
}) {
  return (
    <ClickableRow
      className="row"
      style={{
        gap: 8,
        alignItems: "flex-start",
        padding: "6px 0",
        borderBottom: last ? undefined : "1px solid var(--border)",
      }}
      title={
        entry.stepTitle
          ? `Open module ${entry.moduleNumber}, step “${entry.stepTitle}”`
          : `Open module ${entry.moduleNumber}`
      }
      onActivate={() => onOpen(entry.moduleKey, entry.stepKey)}
    >
      <span style={{ width: 18, flexShrink: 0 }}>{marker}</span>
      <span style={{ flex: 1 }}>
        <InlineMarkdown>{entry.text}</InlineMarkdown>
      </span>
      {entry.stepTitle && (
        <span className="badge" style={{ flexShrink: 0 }}>
          {entry.stepTitle}
        </span>
      )}
    </ClickableRow>
  );
}

function GlossaryRow({
  entry,
  last,
  onOpenModule,
}: {
  entry: GlossaryEntry;
  last: boolean;
  onOpenModule: (key: string) => void;
}) {
  return (
    <div
      style={{
        padding: "6px 0",
        borderBottom: last ? undefined : "1px solid var(--border)",
      }}
    >
      <div className="row" style={{ alignItems: "baseline", gap: 8 }}>
        <code style={{ color: "var(--accent)" }}>{entry.term}</code>
        <span style={{ flex: 1 }}>— {entry.def}</span>
        <ClickableRow
          className="badge"
          title={`Taught in module ${entry.moduleNumber}`}
          onActivate={() => onOpenModule(entry.moduleKey)}
        >
          M{entry.moduleNumber}
        </ClickableRow>
      </div>
    </div>
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
          <div className="row" style={{ alignItems: "baseline" }}>
            <h2 style={{ marginBottom: 4 }}>🏁 Module build</h2>
            <span className="spacer" />
            <button
              className="ghost"
              style={{ padding: "2px 8px", fontSize: 12 }}
              onClick={() => nav(`/projects/${project.key}/workbench?load=${mod.key}`)}
              title="Load this build into the workbench and send it requests of your own"
            >
              🧪 Open in the workbench
            </button>
          </div>
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

      {mod.reference && prev?.reference && (
        <Section
          title={`🔀 What changed since module ${prev.number}`}
          open={sec.isOpen("changes")}
          onToggle={() => sec.toggle("changes")}
          meta={<ChangeBadge before={prev.reference} after={mod.reference} />}
        >
          <ModuleChanges project={project} prev={prev} mod={mod} />
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

function ChangeBadge({ before, after }: { before: string; after: string }) {
  const s = useMemo(() => diffStats(diffSources(before, after, { codeOnly: true })), [before, after]);
  return <DiffStatBadge added={s.added} removed={s.removed} />;
}

/** This module's reference against the previous module's: the module, stated
 * as the edit it makes. Mounted only while its section is open, since the
 * reveal below is the same file in full and most readers want one or other. */
function ModuleChanges({
  project,
  prev,
  mod,
}: {
  project: Project;
  prev: ProjectModule;
  mod: ProjectModule;
}) {
  const nav = useNavigate();
  const [codeOnly, setCodeOnly] = useState(true);
  return (
    <div>
      <div className="row" style={{ gap: 10, marginBottom: 8, alignItems: "center", flexWrap: "wrap" }}>
        <span className="dim" style={{ fontSize: 13, flex: 1 }}>
          Module {prev.number}'s finished file, edited into module {mod.number}'s. If this module adds
          exactly one capability, it should be visible here as one thing.
        </span>
        <label className="row" style={{ gap: 6, fontSize: 13, cursor: "pointer" }}>
          <input type="checkbox" checked={codeOnly} onChange={(e) => setCodeOnly(e.target.checked)} />
          Code only
        </label>
        <button
          className="ghost"
          style={{ padding: "2px 8px", fontSize: 12 }}
          onClick={() => nav(`/projects/${project.key}/history?to=${mod.key}`)}
        >
          Build history →
        </button>
      </div>
      <DiffView before={prev.reference} after={mod.reference} codeOnly={codeOnly} maxHeight={560} />
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
                <InlineMarkdown>{p}</InlineMarkdown>
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
