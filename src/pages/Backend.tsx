import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { BackendProject, BackendStep, BackendTrack, Exercise } from "../types";
import { Markdown } from "../components/Markdown";
import { ExerciseCard, QuizSection } from "../components/LearnExercise";
import { ReferenceReveal } from "../components/ReferenceReveal";
import { Section, useCollapse } from "../components/Collapsible";
import { Empty } from "../components/common";
import { useToast } from "../components/Toast";
import {
  loadDoneChapters,
  setChapterDone,
  solvedExercises,
  loadSolvedExercises,
  markExerciseSolved,
} from "../lib/learnProgress";
import { collectExerciseIds, solvedLabel, studyTime } from "../lib/trackProgress";
import { TrackSkeleton } from "../components/Skeleton";
import {
  TrackOverview,
  UnitPager,
  type TrackGroup,
  type TrackSpec,
} from "../components/track/TrackShell";

// Project completion is tracked in the same SQLite-backed chapter-done set as
// the Learn tab and the TypeScript course, under a namespaced key so it can
// never collide with a concept key or a course week.
const projectKey = (key: string) => `backend:${key}`;

// Every judged exercise required to complete a project: all step exercises plus
// the closing final build.
const requiredExerciseIds = (p: BackendProject) => collectExerciseIds(p.steps, p.final_build);

const LEVEL_COLOR: Record<string, string> = {
  Starter: "var(--good)",
  Core: "var(--accent)",
  Advanced: "var(--hard)",
};

export default function Backend() {
  const { project } = useParams();
  const [track, setTrack] = useState<BackendTrack | null>(null);
  const [done, setDone] = useState<Set<string>>(new Set());
  const nav = useNavigate();

  useEffect(() => {
    api.backendTrack().then(setTrack).catch(() => setTrack(null));
    loadDoneChapters().then(setDone).catch(() => {});
  }, []);

  async function setProjectDone(key: string, value: boolean) {
    setDone(await setChapterDone(done, projectKey(key), value));
  }

  if (!track) return <TrackSkeleton cards={4} />;
  if (track.projects.length === 0) {
    return (
      <div className="page">
        <Empty icon="🛠️" text="The Backend Lab isn't built yet." />
      </div>
    );
  }

  if (project) {
    const p = track.projects.find((x) => x.key === project);
    if (!p) {
      return (
        <div className="page">
          <Empty icon="🛠️" text="Project not found." />
          <button onClick={() => nav("/backend")}>Back to the Backend Lab</button>
        </div>
      );
    }
    const authored = track.projects.filter((x) => x.authored);
    const idx = authored.findIndex((x) => x.key === p.key);
    return (
      <ProjectDetail
        key={p.key}
        project={p}
        harnessNote={track.harness_note}
        isDone={done.has(projectKey(p.key))}
        onSetDone={(v) => setProjectDone(p.key, v)}
        prev={idx > 0 ? authored[idx - 1] : null}
        next={idx >= 0 && idx < authored.length - 1 ? authored[idx + 1] : null}
      />
    );
  }

  return <Overview track={track} done={done} />;
}

/**
 * The Backend Lab overview, on the shared track template.
 *
 * Its projects group by level — Starter, Core, Advanced — which is the rail.
 * Everything else (the hero, the progress arithmetic, the unit rows) is the
 * same code the courses use (UI_ROADMAP G1).
 */
function Overview({ track, done }: { track: BackendTrack; done: Set<string> }) {
  const sec = useCollapse("backend-overview", false);

  const spec = useMemo<TrackSpec>(() => {
    // Levels, in the order they first appear, so the rail follows the ladder
    // rather than an alphabetical accident.
    const groups: TrackGroup[] = [];
    const seen = new Set<string>();
    for (const p of track.projects) {
      const level = p.level || "Projects";
      if (seen.has(level)) continue;
      seen.add(level);
      groups.push({ key: level, title: level });
    }

    return {
      title: track.title,
      subtitle: track.subtitle,
      base: "/backend",
      unitLabel: "Project",
      groupLabel: "Level",
      intro: track.intro,
      groups,
      units: track.projects.map((p) => ({
        slug: p.key,
        number: p.number,
        title: p.title,
        tagline: p.goal || p.tagline,
        group: p.level || "Projects",
        done: done.has(projectKey(p.key)),
        authored: p.authored,
        estMinutes: p.est_minutes,
        badges: (
          <>
            {(p.steps?.length ?? 0) > 0 && (
              <span className="badge">{p.steps.length} steps</span>
            )}
            {requiredExerciseIds(p).length > 0 && (
              <span className="badge">{requiredExerciseIds(p).length} exercises</span>
            )}
            {p.concepts.slice(0, 3).map((c) => (
              <span key={c} className="badge tag">
                {c}
              </span>
            ))}
          </>
        ),
      })),
      children: track.harness_note ? (
        <Section
          title="🧪 How the drills are judged"
          open={sec.isOpen("harness")}
          onToggle={() => sec.toggle("harness")}
          meta={<span className="badge">read once</span>}
        >
          <Markdown>{track.harness_note}</Markdown>
        </Section>
      ) : undefined,
    };
  }, [track, done, sec]);

  return <TrackOverview spec={spec} />;
}

function ProjectDetail({
  project,
  harnessNote,
  isDone,
  onSetDone,
  prev,
  next,
}: {
  project: BackendProject;
  harnessNote: string;
  isDone: boolean;
  onSetDone: (done: boolean) => void;
  prev: BackendProject | null;
  next: BackendProject | null;
}) {
  const nav = useNavigate();
  const toast = useToast();
  const [solvedEx, setSolvedEx] = useState<Set<string>>(() => solvedExercises());
  const [scrolledToBottom, setScrolledToBottom] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const celebrated = useRef(false);
  // Steps start collapsed: each open step mounts a Monaco editor per exercise,
  // and the contents card below is how you navigate them.
  const sec = useCollapse(`backend-sec:${project.key}`, false);
  const steps = project.steps ?? [];
  const stepKeys = useMemo(() => steps.map((s) => s.key), [steps]);

  function openStep(key: string) {
    if (!sec.isOpen(key)) sec.toggle(key);
    requestAnimationFrame(() =>
      document.getElementById(`step-${key}`)?.scrollIntoView({ behavior: "smooth", block: "start" })
    );
  }

  const gradableIds = useMemo(() => requiredExerciseIds(project), [project]);
  const allSolved = gradableIds.every((id) => solvedEx.has(id));
  const solvedCount = gradableIds.filter((id) => solvedEx.has(id)).length;

  function handleSolved(id: string) {
    setSolvedEx(new Set(markExerciseSolved(id)));
  }

  // Hydrate the solved set from SQLite. The initialiser above reads a
  // module-level cache — warm after the first load of the session — and this
  // is what fills it on a cold start.
  useEffect(() => {
    loadSolvedExercises().then(setSolvedEx).catch(() => {});
  }, []);

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
  }, [project.key]);

  useEffect(() => {
    if (!isDone && scrolledToBottom && allSolved && !celebrated.current) {
      celebrated.current = true;
      onSetDone(true);
      toast(
        project.milestone
          ? `🎉 Project ${project.number} complete! ${project.milestone}`
          : `🎉 Project ${project.number} complete!`
      );
    }
  }, [isDone, scrolledToBottom, allSolved, onSetDone, toast, project.milestone, project.number]);

  return (
    <div className="page">
      <div className="row" style={{ marginBottom: 4, justifyContent: "space-between" }}>
        <div className="row">
          <button className="ghost" onClick={() => nav("/backend")}>
            ← Backend Lab
          </button>
          <span className="badge">Project {project.number}</span>
          {project.level && (
            <span
              className="badge"
              style={{ borderColor: LEVEL_COLOR[project.level], color: LEVEL_COLOR[project.level] }}
            >
              {project.level}
            </span>
          )}
          {project.est_minutes > 0 && (
            <span className="badge">⏱️ {studyTime(project.est_minutes)}</span>
          )}
        </div>
        <button
          className="ghost"
          style={isDone ? { borderColor: "var(--good)", color: "var(--good)" } : undefined}
          onClick={() => onSetDone(!isDone)}
          title={isDone ? "Marked complete — click to undo" : "Mark this project complete"}
        >
          {isDone ? "✓ Done" : "Mark done"}
        </button>
      </div>

      <h1 className="page-title" style={{ marginTop: 6 }}>
        {project.title}
      </h1>
      <p className="page-sub">{project.tagline}</p>

      <div className="card" style={{ marginBottom: 14, borderColor: "var(--accent)" }}>
        <div className="io-label" style={{ color: "var(--accent)" }}>
          🎯 What you're building
        </div>
        <p style={{ marginBottom: project.why ? 8 : 0 }}>{project.goal}</p>
        {project.why && (
          <p className="dim" style={{ margin: 0, fontSize: 13 }}>
            💡 Why it matters: {project.why}
          </p>
        )}
        {project.builds_on.length > 0 && (
          <p className="faint" style={{ margin: "8px 0 0", fontSize: 12 }}>
            🧱 Continues from: {project.builds_on.join(", ")}
          </p>
        )}
      </div>

      {project.objectives.length > 0 && (
        <div className="card" style={{ marginBottom: 14 }}>
          <div className="io-label">By the end of this project you can…</div>
          <ul style={{ margin: "6px 0 0", paddingLeft: 20 }}>
            {project.objectives.map((o, i) => (
              <li key={i} style={{ marginBottom: 2 }}>
                {o}
              </li>
            ))}
          </ul>
        </div>
      )}

      {project.brief && <Markdown>{project.brief}</Markdown>}

      {project.endpoints.length > 0 && (
        <>
          <h3 style={{ marginBottom: 6 }}>📋 The contract</h3>
          <p className="dim" style={{ marginTop: 0, fontSize: 13 }}>
            Build against this. Every row is something you can check with curl when you're done.
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
                {project.endpoints.map((e, i) => (
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
      )}

      {project.setup && (
        <>
          <h3 style={{ margin: "18px 0 6px" }}>⚙️ Set up</h3>
          <Markdown>{project.setup}</Markdown>
        </>
      )}

      {steps.length > 0 && (
        <div className="card" style={{ marginBottom: 14 }}>
          <div className="row" style={{ marginBottom: 8 }}>
            <div className="io-label" style={{ margin: 0 }}>
              🪜 Steps — do these in order
            </div>
            <span className="spacer" />
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
              <div
                key={step.key}
                className="row"
                style={{
                  cursor: "pointer",
                  gap: 8,
                  padding: "5px 0",
                  borderBottom: si < steps.length - 1 ? "1px solid var(--border)" : undefined,
                }}
                onClick={() => openStep(step.key)}
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
              </div>
            );
          })}
        </div>
      )}

      {steps.map((step, si) => (
        <div key={step.key} id={`step-${step.key}`}>
          <Section
            title={`Step ${si + 1}. ${step.title}`}
            open={sec.isOpen(step.key)}
            onToggle={() => sec.toggle(step.key)}
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

      {project.final_build && (
        <>
          <div className="divider" />
          <h2 style={{ marginBottom: 4 }}>🏁 Final build</h2>
          <p className="dim" style={{ marginTop: 0 }}>
            Everything above, assembled. This is the project.
          </p>
          <ExerciseCard index={1} exercise={project.final_build} challenge onSolved={handleSolved} />
        </>
      )}

      {project.acceptance.length > 0 && (
        <>
          <div className="divider" />
          <h3>✅ Acceptance checklist</h3>
          <p className="dim" style={{ marginTop: -4 }}>
            Run through these against <em>your own</em> server before calling it done.
          </p>
          <div className="card">
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {project.acceptance.map((a, i) => (
                <li key={i} style={{ marginBottom: 4 }}>
                  {a}
                </li>
              ))}
            </ul>
          </div>
        </>
      )}

      {project.manual_test && (
        <Section
          title="🔌 Try it yourself"
          open={sec.isOpen("manual")}
          onToggle={() => sec.toggle("manual")}
          meta={<span className="badge">curl</span>}
        >
          <Markdown>{project.manual_test}</Markdown>
        </Section>
      )}

      {/* The Backend Lab is JavaScript, so its reveal is fenced as `js`. */}
      {project.reference && (
        <ReferenceReveal
          reference={project.reference}
          language="js"
          revealLabel="Reveal a reference implementation"
          hideLabel="Hide the reference implementation"
        />
      )}

      {project.stretch.length > 0 && (
        <Section
          title="🚀 Take it further"
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

      {project.self_check.length > 0 && (
        <>
          <div className="divider" />
          <h3>🧠 Self-check</h3>
          <p className="dim" style={{ marginTop: -4 }}>
            Before you move on, make sure you can honestly say yes to each of these:
          </p>
          <div className="card">
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {project.self_check.map((s, i) => (
                <li key={i} style={{ marginBottom: 4 }}>
                  {s}
                </li>
              ))}
            </ul>
          </div>
        </>
      )}

      {project.review.length > 0 && (
        <>
          <div className="divider" />
          <h3>🔁 End-of-project review</h3>
          <p className="dim" style={{ marginTop: -4 }}>
            A quick mixed quiz — some of these reach back to earlier projects.
          </p>
          <QuizSection questions={project.review} />
        </>
      )}

      {project.glossary.length > 0 && (
        <Section
          title="📖 Glossary"
          open={sec.isOpen("glossary")}
          onToggle={() => sec.toggle("glossary")}
          meta={<span className="badge">{project.glossary.length} terms</span>}
        >
          <div className="card" style={{ marginTop: 0 }}>
            {project.glossary.map((g, i) => (
              <div
                key={i}
                style={{
                  padding: "5px 0",
                  borderBottom:
                    i < project.glossary.length - 1 ? "1px solid var(--border)" : undefined,
                }}
              >
                <code style={{ color: "var(--accent)" }}>{g.term}</code> — {g.def}
              </div>
            ))}
          </div>
        </Section>
      )}

      {project.cheatsheet && (
        <Section
          title="🧾 Cheat sheet"
          open={sec.isOpen("cheatsheet")}
          onToggle={() => sec.toggle("cheatsheet")}
        >
          <Markdown>{project.cheatsheet}</Markdown>
        </Section>
      )}

      {project.milestone && (
        <div className="card" style={{ marginTop: 16, borderColor: "var(--good)" }}>
          <div className="io-label" style={{ color: "var(--good)" }}>
            🎉 Milestone
          </div>
          <p style={{ margin: 0 }}>{project.milestone}</p>
        </div>
      )}

      {harnessNote && (
        <Section
          title="🧪 How the drills are judged"
          open={sec.isOpen("harness")}
          onToggle={() => sec.toggle("harness")}
        >
          <Markdown>{harnessNote}</Markdown>
        </Section>
      )}

      {!isDone && (
        <p className="faint" style={{ fontSize: 12, marginTop: 24, textAlign: "center" }}>
          {gradableIds.length > 0
            ? `This project marks itself ✓ Done once you've read to here and solved its ${gradableIds.length} exercise${gradableIds.length === 1 ? "" : "s"}${allSolved ? " — all solved!" : ` (${solvedCount}/${gradableIds.length} solved)`}.`
            : "This project marks itself ✓ Done once you've read to here."}
        </p>
      )}

      <UnitPager
        base="/backend"
        unitLabel="Project"
        prev={prev ? { slug: prev.key, number: prev.number, title: prev.title } : null}
        next={next ? { slug: next.key, number: next.number, title: next.title } : null}
        backTo="/backend"
        backLabel="All projects"
      />

      {/* Sentinel: intersecting means the project has been read to the bottom. */}
      <div ref={bottomRef} style={{ height: 1 }} />
    </div>
  );
}

function StepBody({ step, onSolved }: { step: BackendStep; onSolved: (id: string) => void }) {
  const exercises = step.exercises ?? [];
  const kindOf = (e: Exercise) => e.kind || "drill";
  const drills = exercises.filter((e) => kindOf(e) === "drill");
  const fixes = exercises.filter((e) => kindOf(e) === "fix");
  const challenges = exercises.filter((e) => kindOf(e) === "challenge");
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
          <h4>🔮 Predict the response</h4>
          <p className="dim" style={{ marginTop: -4 }}>
            Work it out before you read on.
          </p>
          <QuizSection questions={warmup} />
        </>
      )}

      {drills.length > 0 && (
        <>
          <h4>🧩 Practice — fill in the blank</h4>
          {drills.map((ex, i) => (
            <ExerciseCard key={ex.id} index={i + 1} exercise={ex} onSolved={onSolved} />
          ))}
        </>
      )}

      {fixes.length > 0 && (
        <>
          <h4>🐞 Fix the bug</h4>
          <p className="dim" style={{ marginTop: -4 }}>
            This server runs but answers wrongly. Find the bug and fix it so the tests pass.
          </p>
          {fixes.map((ex, i) => (
            <ExerciseCard key={ex.id} index={i + 1} exercise={ex} onSolved={onSolved} />
          ))}
        </>
      )}

      {challenges.length > 0 && (
        <>
          <h4>🏗️ Build it</h4>
          {challenges.map((ex, i) => (
            <ExerciseCard key={ex.id} index={i + 1} exercise={ex} challenge onSolved={onSolved} />
          ))}
        </>
      )}

      {quiz.length > 0 && (
        <>
          <h4>❓ Check yourself</h4>
          <QuizSection questions={quiz} />
        </>
      )}
    </div>
  );
}
