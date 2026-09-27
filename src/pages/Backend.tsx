import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { BackendProject, BackendStep, BackendTrack, Exercise } from "../types";
import { Markdown } from "../components/Markdown";
import { ExerciseCard, QuizSection, ReferenceReveal, VerdictPanel } from "../components/exercise";
import { Section, useCollapse } from "../components/Collapsible";
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
import { Badge, EmptyState, ErrorState, Icon, PageHeader, type Tone } from "../components/ui";
import { ReaderLayout, ReadStatus, useSeenBottom } from "../components/reader/Reader";
import { Glossary, Milestone, SubHeading, UnitContents, UnitGoal, UnitList, UnitPart, scrollToPart } from "../components/track/UnitParts";
import { inlineCode } from "../components/common";
import { useCrumb } from "../store";
import { loadFailed } from "../lib/failures";

// Project completion is tracked in the same SQLite-backed chapter-done set as
// the Learn tab and the TypeScript course, under a namespaced key so it can
// never collide with a concept key or a course week.
const projectKey = (key: string) => `backend:${key}`;

// Every judged exercise required to complete a project: all step exercises plus
// the closing final build.
const requiredExerciseIds = (p: BackendProject) => collectExerciseIds(p.steps, p.final_build);

export default function Backend() {
  const { project } = useParams();
  const [track, setTrack] = useState<BackendTrack | null>(null);
  const [done, setDone] = useState<Set<string>>(new Set());
  const [error, setError] = useState("");
  const nav = useNavigate();

  useEffect(() => {
    api.backendTrack().then(setTrack).catch((e) => setError(String(e)));
    loadDoneChapters().then(setDone).catch(loadFailed("your completed chapters"));
  }, []);

  async function setProjectDone(key: string, value: boolean) {
    setDone(await setChapterDone(done, projectKey(key), value));
  }

  if (error) {
    return (
      <div className="page">
        <ErrorState
          title="The Backend Lab could not be loaded."
          error={error}
          onRetry={() => {
            setError("");
            api.backendTrack().then(setTrack).catch((e) => setError(String(e)));
          }}
        />
      </div>
    );
  }
  if (!track) return <TrackSkeleton cards={4} />;
  if (track.projects.length === 0) {
    return (
      <div className="page">
        <EmptyState icon="backend" title="The Backend Lab isn't built yet." />
      </div>
    );
  }

  if (project) {
    const p = track.projects.find((x) => x.key === project);
    if (!p) {
      return (
        <div className="page">
          <EmptyState
            icon="backend"
            title="Project not found."
            action={{ label: "Back to the Backend Lab", icon: "back", onClick: () => nav("/backend") }}
          />
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
          title="How the drills are judged"
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

const LEVEL_TONE: Record<string, Tone> = {
  Starter: "good",
  Core: "accent",
  Advanced: "bad",
};

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
  const toast = useToast();
  useCrumb(project.title, `Project ${project.number}`);
  const [solvedEx, setSolvedEx] = useState<Set<string>>(() => solvedExercises());
  const [bottomRef, seenBottom] = useSeenBottom(project.key);
  const celebrated = useRef(false);
  // Steps start collapsed: each open step mounts a Monaco editor per exercise,
  // and the contents list below is how you navigate them.
  const sec = useCollapse(`backend-sec:${project.key}`, false);
  const steps = project.steps ?? [];
  const stepKeys = useMemo(() => steps.map((s) => s.key), [steps]);

  function openStep(key: string) {
    if (!sec.isOpen(key)) sec.toggle(key);
    scrollToPart(`step-${key}`);
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
    loadSolvedExercises().then(setSolvedEx).catch(loadFailed("your solved exercises"));
  }, []);

  useEffect(() => {
    if (!isDone && seenBottom && allSolved && !celebrated.current) {
      celebrated.current = true;
      onSetDone(true);
      toast.success(
        project.milestone
          ? `Project ${project.number} complete! ${project.milestone}`
          : `Project ${project.number} complete!`
      );
    }
  }, [isDone, seenBottom, allSolved, onSetDone, toast, project.milestone, project.number]);

  const checklist = [
    { label: "Read to the end", met: seenBottom || isDone },
    ...(gradableIds.length > 0
      ? [{ label: `Solve the exercises (${solvedCount}/${gradableIds.length})`, met: allSolved }]
      : []),
  ];

  return (
    <div className="page backend-project">
      <ReaderLayout aside={<ReadStatus steps={checklist} complete={isDone} onToggle={() => onSetDone(!isDone)} />}>
        <PageHeader
          eyebrow={
            <>
              Project {project.number}
              {project.est_minutes > 0 && (
                <>
                  {" "}
                  · <Icon name="clock" size={12} /> {studyTime(project.est_minutes)}
                </>
              )}
            </>
          }
          title={project.title}
          subtitle={project.tagline}
          actions={project.level ? <Badge tone={LEVEL_TONE[project.level] ?? "neutral"}>{project.level}</Badge> : undefined}
        />

        <UnitGoal label="What you're building" goal={project.goal} why={project.why} buildsOn={project.builds_on} />
        <UnitList label="By the end of this project you can…" items={project.objectives} />
        {project.brief && <Markdown>{project.brief}</Markdown>}

        {project.endpoints.length > 0 && (
          <UnitPart
            title="The contract"
            icon="document"
            lead="Build against this. Every row is something you can check with curl when you're done."
          >
            <div className="card table-card">
              <table className="data static">
                <thead>
                  <tr>
                    <th scope="col">Method</th>
                    <th scope="col">Path</th>
                    <th scope="col">Purpose</th>
                    <th scope="col">Request</th>
                    <th scope="col">Response</th>
                    <th scope="col">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {project.endpoints.map((e, i) => (
                    <tr key={i}>
                      <td className="mono nowrap endpoint-method">{e.method}</td>
                      <td className="mono nowrap">{e.path}</td>
                      <td>{e.purpose}</td>
                      <td className="mono faint cell-small">{e.request || "—"}</td>
                      <td className="mono faint cell-small">{e.response || "—"}</td>
                      <td className="mono nowrap cell-small">{e.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </UnitPart>
        )}

        {project.setup && (
          <UnitPart title="Set up" icon="tools">
            <Markdown>{project.setup}</Markdown>
          </UnitPart>
        )}

        <UnitContents
          title="Steps — do these in order"
          icon="checklist"
          rows={steps.map((s) => {
            const ids = (s.exercises ?? []).map((e) => e.id);
            return { key: s.key, title: s.title, what: s.what, solved: ids.filter((id) => solvedEx.has(id)).length, total: ids.length };
          })}
          onOpen={openStep}
          onExpandAll={() => sec.setAll(stepKeys, true)}
          onCollapseAll={() => sec.setAll(stepKeys, false)}
        />

        {steps.map((step, si) => (
          <div key={step.key} id={`step-${step.key}`}>
            <Section
              title={`Step ${si + 1}. ${step.title}`}
              outline={step.title}
              open={sec.isOpen(step.key)}
              onToggle={() => sec.toggle(step.key)}
              meta={<span className="learn-cat-count">{solvedLabel(step.exercises, solvedEx)}</span>}
            >
              <StepBody step={step} onSolved={handleSolved} />
            </Section>
          </div>
        ))}

        {project.final_build && (
          <UnitPart title="Final build" icon="build" lead="Everything above, assembled. This is the project.">
            <ExerciseCard index={1} exercise={project.final_build} challenge onSolved={handleSolved} />
          </UnitPart>
        )}

        {project.acceptance.length > 0 && (
          <UnitPart
            title="Acceptance checklist"
            icon="checklist"
            lead={
              <>
                Run through these against <em>your own</em> server before calling it done.
              </>
            }
          >
            <UnitList items={project.acceptance} />
          </UnitPart>
        )}

        {project.manual_test && (
          <Section
            title="Try it yourself"
            open={sec.isOpen("manual")}
            onToggle={() => sec.toggle("manual")}
            meta={<Badge icon="terminal">curl</Badge>}
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
            title="Take it further"
            open={sec.isOpen("stretch")}
            onToggle={() => sec.toggle("stretch")}
            meta={<Badge>{project.stretch.length} ideas</Badge>}
          >
            <UnitList items={project.stretch} />
          </Section>
        )}

        {project.self_check.length > 0 && (
          <UnitPart
            title="Self-check"
            icon="checklist"
            lead="Before you move on, make sure you can honestly say yes to each of these:"
          >
            <UnitList items={project.self_check} />
          </UnitPart>
        )}

        {project.review.length > 0 && (
          <UnitPart
            title="End-of-project review"
            outline="Review"
            icon="refresh"
            lead="A quick mixed quiz — some of these reach back to earlier projects."
          >
            <QuizSection questions={project.review} />
          </UnitPart>
        )}

        {project.glossary.length > 0 && (
          <Section
            title="Glossary"
            open={sec.isOpen("glossary")}
            onToggle={() => sec.toggle("glossary")}
            meta={<Badge>{project.glossary.length} terms</Badge>}
          >
            <Glossary terms={project.glossary} />
          </Section>
        )}

        {project.cheatsheet && (
          <Section title="Cheat sheet" open={sec.isOpen("cheatsheet")} onToggle={() => sec.toggle("cheatsheet")}>
            <Markdown>{project.cheatsheet}</Markdown>
          </Section>
        )}

        {project.milestone && <Milestone text={project.milestone} />}

        {harnessNote && (
          <Section
            title="How the drills are judged"
            open={sec.isOpen("harness")}
            onToggle={() => sec.toggle("harness")}
          >
            <Markdown>{harnessNote}</Markdown>
          </Section>
        )}

        <div className="concept-end">
          <ReadStatus steps={checklist} complete={isDone} compact />
        </div>

        <UnitPager
          base="/backend"
          unitLabel="Project"
          prev={prev ? { slug: prev.key, number: prev.number, title: prev.title } : null}
          next={next ? { slug: next.key, number: next.number, title: next.title } : null}
          backTo="/backend"
          backLabel="All projects"
        />

        {/* Sentinel: intersecting means the project has been read to the bottom. */}
        <div ref={bottomRef} className="read-sentinel" />
      </ReaderLayout>
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
    <div className="lesson-body">
      {step.what && <p className="section-lead">{step.what}</p>}

      <Markdown>{step.instructions}</Markdown>

      {step.checkpoint && (
        <VerdictPanel tone="good" icon="checklist" title="Checkpoint — you're done with this step when…">
          <Markdown>{step.checkpoint}</Markdown>
        </VerdictPanel>
      )}

      {step.pitfalls.length > 0 && (
        <VerdictPanel tone="warn" title="Things that will cost you an hour">
          <ul>
            {step.pitfalls.map((p, i) => (
              <li key={i}>{inlineCode(p)}</li>
            ))}
          </ul>
        </VerdictPanel>
      )}

      {warmup.length > 0 && (
        <>
          <SubHeading icon="sparkles">Predict the response</SubHeading>
          <p className="section-lead">Work it out before you read on.</p>
          <QuizSection questions={warmup} />
        </>
      )}

      {drills.length > 0 && (
        <>
          <SubHeading icon="edit">Practice — fill in the blank</SubHeading>
          {drills.map((ex, i) => (
            <ExerciseCard key={ex.id} index={i + 1} exercise={ex} onSolved={onSolved} />
          ))}
        </>
      )}

      {fixes.length > 0 && (
        <>
          <SubHeading icon="tools">Fix the bug</SubHeading>
          <p className="section-lead">This server runs but answers wrongly. Find the bug and fix it so the tests pass.</p>
          {fixes.map((ex, i) => (
            <ExerciseCard key={ex.id} index={i + 1} exercise={ex} onSolved={onSolved} />
          ))}
        </>
      )}

      {challenges.length > 0 && (
        <>
          <SubHeading icon="build">Build it</SubHeading>
          {challenges.map((ex, i) => (
            <ExerciseCard key={ex.id} index={i + 1} exercise={ex} challenge onSolved={onSolved} />
          ))}
        </>
      )}

      {quiz.length > 0 && (
        <>
          <SubHeading icon="help">Check yourself</SubHeading>
          <QuizSection questions={quiz} />
        </>
      )}
    </div>
  );
}
