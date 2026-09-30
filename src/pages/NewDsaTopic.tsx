import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api } from "../api";
import type { NdSection, NdTopic, NewDsa, Problem } from "../types";
import { useCrumb } from "../store";
import { Markdown, InlineMarkdown } from "../components/Markdown";
import { DiffBadge } from "../components/common";
import { Badge, Button, Chip, EmptyState, ErrorState, Icon, IconButton, ProgressBar, ScrollX } from "../components/ui";
import { VerdictPanel } from "../components/exercise";
import { Code, GuidedFlow, QuestionCard, Sitting, TrackedExercise, WindowStepper } from "../components/newdsa/Parts";
import { loadSolvedExercises, markExerciseSolved } from "../lib/learnProgress";
import { useCollapse } from "../components/Collapsible";
import {
  READING_SECTIONS,
  isSectionDone,
  lessonProgress,
  masteryGates,
  nextSection,
  questionId,
  readId,
  sectionProgress,
  sittingId,
  solvedSlugSet,
  topicStatus,
  type Gate,
  type SectionKey,
  type TopicStatus,
} from "../lib/newDsa";

/**
 * One NEW_DSA topic, taught in the sixteen sections of NEW_DSA.md.
 *
 * One section at a time, like the Library's stages: the sections are a rail on
 * the left, the selected one fills the right, and the selection lives in `?s=`
 * so a trip to the Solve view comes back to the same place. Nothing is locked —
 * the order is the recommended curve (Understand → See → Copy → Complete →
 * Implement → Recognize → Apply → Combine → Master), not a gate.
 *
 * Two measures, kept apart on purpose: **lessons** (sections 1-15) and
 * **mastery** (section 16, five separate abilities). Finishing the first never
 * implies the second. See src/lib/newDsa.ts.
 */

let seedPromise: Promise<NewDsa> | null = null;
function loadSeed(): Promise<NewDsa> {
  if (!seedPromise) {
    seedPromise = api.newDsa().catch((e) => {
      seedPromise = null;
      throw e;
    });
  }
  return seedPromise;
}

const STATUS_LABEL: Record<TopicStatus, { label: string; tone: "neutral" | "accent" | "good" | "warn" }> = {
  new: { label: "Not started", tone: "neutral" },
  learning: { label: "Learning", tone: "accent" },
  "lessons-done": { label: "Lessons done · not yet mastered", tone: "warn" },
  mastered: { label: "Mastered", tone: "good" },
};

export default function NewDsaTopic() {
  const { key = "" } = useParams();
  const [course, setCourse] = useState<NewDsa | null>(null);
  const [problems, setProblems] = useState<Problem[]>([]);
  const [solved, setSolved] = useState<Set<string>>(new Set());
  const [error, setError] = useState("");

  const load = useCallback(() => {
    setError("");
    Promise.all([loadSeed(), api.listProblems(), loadSolvedExercises()])
      .then(([c, ps, s]) => {
        setCourse(c);
        setProblems(ps);
        setSolved(s);
      })
      .catch((e) => setError(String(e)));
  }, []);
  useEffect(load, [load]);

  const topic = course?.topics.find((t) => t.key === key) ?? null;
  useCrumb(topic?.title ?? null, "Topic");

  if (error) {
    return (
      <div className="page cur-page">
        <h1 className="page-title">NEW DSA</h1>
        <ErrorState title="Could not load the topic." error={error} onRetry={load} />
      </div>
    );
  }
  if (!course) return <div className="page cur-page" aria-busy="true" />;
  if (!topic) {
    return (
      <div className="page cur-page">
        <h1 className="page-title">{course.title}</h1>
        <EmptyState icon="curriculum" title={`No topic called “${key}”.`} />
      </div>
    );
  }
  return (
    <TopicPage
      course={course}
      topic={topic}
      problems={problems}
      solved={solved}
      onMark={(id) => setSolved(markExerciseSolved(id))}
    />
  );
}

function TopicPage({
  course,
  topic,
  problems,
  solved,
  onMark,
}: {
  course: NewDsa;
  topic: NdTopic;
  problems: Problem[];
  solved: Set<string>;
  onMark: (id: string) => void;
}) {
  const [params, setParams] = useSearchParams();
  const fold = useCollapse("ndsa-rail", false);
  const compact = fold.isOpen("rail");
  const sections = course.sections;
  const bySlug = useMemo(() => new Map(problems.map((p) => [p.slug, p])), [problems]);
  const solvedSlugs = useMemo(() => solvedSlugSet(problems), [problems]);

  const lessons = lessonProgress(topic, sections, solved, solvedSlugs);
  const gates = masteryGates(topic, solved, solvedSlugs);
  const status = topicStatus(lessons, gates);
  const continueAt = nextSection(topic, sections, solved, solvedSlugs);

  const requested = sections.findIndex((s) => s.key === params.get("s"));
  const index = requested >= 0 ? requested : sections.findIndex((s) => s.key === continueAt);
  const section = sections[index]!;
  const select = (k: string) => {
    setParams({ s: k }, { replace: true });
    document.getElementById("main")?.scrollTo({ top: 0 });
    window.scrollTo({ top: 0 });
  };

  /** Moving on from a reading section is what finishes it. */
  const advance = () => {
    if (READING_SECTIONS.has(section.key)) {
      const id = readId(topic.key, section.key);
      if (!solved.has(id)) onMark(id);
    }
    const next = sections[index + 1];
    if (next) select(next.key);
  };

  const ctx: Ctx = { topic, solved, solvedSlugs, bySlug, onMark, gates };
  const passedGates = gates.filter((g) => g.passed).length;

  return (
    <div className="page cur-page ndsa-page">
      <div className="cur-head">
        <div>
          <div className="cur-eyebrow">
            {course.title} · {topic.phase}
          </div>
          <h1 className="page-title">
            {topic.icon} {topic.title}
          </h1>
          <p className="page-sub">
            {topic.tagline}{" "}
            <span className="faint">
              · about {Math.round(topic.est_minutes / 60)} h · builds on {topic.prereqs.join(", ")}
            </span>
          </p>
        </div>
        <div className="ndsa-head-side">
          <Badge tone={STATUS_LABEL[status].tone} icon={status === "mastered" ? "trophy" : undefined}>
            {STATUS_LABEL[status].label}
          </Badge>
          <ProgressBar value={lessons.done} max={lessons.total} label="Lessons, sections 1 to 15" size="sm" />
          <span className="dim text-xs">
            Lessons {lessons.done} / {lessons.total}
          </span>
          <ProgressBar value={passedGates} max={gates.length} tone="good" label="Mastery gates passed" size="sm" />
          <span className="dim text-xs">
            Mastery {passedGates} / {gates.length} abilities
          </span>
        </div>
      </div>

      <div className={`cur-layout ${compact ? "rail-compact" : ""}`}>
        <nav className="cur-stages ndsa-rail" aria-label="Sections">
          <div className="cur-stages-head">
            <span className="cur-eyebrow cur-stages-label">Sections</span>
            <IconButton
              size="sm"
              icon={compact ? "sidebarOpen" : "sidebarClose"}
              label={compact ? "Show section names" : "Fold the section rail to numbers"}
              aria-expanded={!compact}
              onClick={() => fold.toggle("rail")}
            />
          </div>
          {sections.map((s, i) => (
            <SectionButton
              key={s.key}
              section={s}
              number={i + 1}
              active={i === index}
              here={s.key === continueAt && status !== "mastered"}
              compact={compact}
              progress={
                s.key === "mastery"
                  ? { done: passedGates, total: gates.length }
                  : sectionProgress(topic, s.key, solved, solvedSlugs)
              }
              onSelect={() => select(s.key)}
            />
          ))}
        </nav>

        <main className="ndsa-section" aria-labelledby="ndsa-section-title">
          <div className="ndsa-section-head">
            <span className="cur-eyebrow">
              Section {index + 1} of {sections.length} · {section.phase}
            </span>
            <h2 id="ndsa-section-title" className="ndsa-h2">
              {section.title}
            </h2>
          </div>
          <SectionBody sectionKey={section.key} ctx={ctx} />
          <div className="ndsa-section-foot">
            {index > 0 && (
              <Button variant="ghost" icon="chevronLeft" onClick={() => select(sections[index - 1]!.key)}>
                {sections[index - 1]!.title}
              </Button>
            )}
            <span className="spacer" />
            {index < sections.length - 1 && (
              <Button variant="primary" iconRight="chevronRight" onClick={advance}>
                {READING_SECTIONS.has(section.key) && !solved.has(readId(topic.key, section.key)) ? "Done · next: " : "Next: "}
                {sections[index + 1]!.title}
              </Button>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

function SectionButton({
  section,
  number,
  active,
  here,
  compact,
  progress,
  onSelect,
}: {
  section: NdSection;
  number: number;
  active: boolean;
  here: boolean;
  compact: boolean;
  progress: { done: number; total: number };
  onSelect: () => void;
}) {
  const done = isSectionDone(progress);
  const started = progress.done > 0;
  const counted = progress.total > 1;
  return (
    <button
      className={`cur-stage-btn ndsa-rail-btn ${active ? "active" : ""} ${compact ? "compact" : ""}`}
      onClick={onSelect}
      aria-current={active ? "true" : undefined}
      aria-label={compact ? `${number}. ${section.title}${done ? ", done" : ""}` : undefined}
      title={compact ? section.title : undefined}
    >
      <span className={`cur-num ${done ? "complete" : started ? "started" : ""}`}>
        {done ? <Icon name="check" size={14} /> : number}
      </span>
      <span className="cur-stage-text">
        <span className="cur-stage-name">{section.title}</span>
        <span className="cur-stage-meta">
          {counted && (
            <span>
              {progress.done}/{progress.total}
            </span>
          )}
          {here && <span className="cur-here">{counted ? "· " : ""}continue here</span>}
        </span>
      </span>
    </button>
  );
}

// ---------------------------------------------------------------------------
// Sections
// ---------------------------------------------------------------------------

interface Ctx {
  topic: NdTopic;
  solved: Set<string>;
  solvedSlugs: Set<string>;
  bySlug: Map<string, Problem>;
  onMark: (id: string) => void;
  gates: Gate[];
}

function SectionBody({ sectionKey, ctx }: { sectionKey: SectionKey; ctx: Ctx }) {
  switch (sectionKey) {
    case "concept":
      return <ConceptSection ctx={ctx} />;
    case "mental_model":
      return <MentalModelSection ctx={ctx} />;
    case "ts_fundamentals":
      return <TsSection ctx={ctx} />;
    case "patterns":
      return <PatternsSection ctx={ctx} />;
    case "when_to_use":
      return <WhenToUseSection ctx={ctx} />;
    case "when_not":
      return <WhenNotSection ctx={ctx} />;
    case "examples":
      return <ExamplesSection ctx={ctx} />;
    case "implementation":
      return <ImplementationSection ctx={ctx} />;
    case "complexity":
      return <ComplexitySection ctx={ctx} />;
    case "mistakes":
      return <MistakesSection ctx={ctx} />;
    case "recognition":
      return <RecognitionSection ctx={ctx} />;
    case "guided":
      return <GuidedSection ctx={ctx} />;
    case "independent":
      return <IndependentSection ctx={ctx} />;
    case "variations":
      return <VariationsSection ctx={ctx} />;
    case "review":
      return <ReviewSection ctx={ctx} />;
    case "mastery":
      return <MasterySection ctx={ctx} />;
    default:
      return null;
  }
}

function Block({ title, children, tone }: { title?: ReactNode; children: ReactNode; tone?: "accent" | "good" | "bad" }) {
  return (
    <section className={`cur-panel ndsa-block ${tone ? `ndsa-tone-${tone}` : ""}`}>
      {title && <h3 className="ndsa-h3">{title}</h3>}
      {children}
    </section>
  );
}

// 1 ------------------------------------------------------------------------

function ConceptSection({ ctx }: { ctx: Ctx }) {
  const c = ctx.topic.concept;
  return (
    <>
      <Block>
        <Markdown>{c.body}</Markdown>
      </Block>
      <Block title="Terminology">
        <dl className="ndsa-terms">
          {c.terms.map((t) => (
            <div key={t.term} className="ndsa-term">
              <dt>
                <InlineMarkdown>{t.term}</InlineMarkdown>
              </dt>
              <dd>
                <InlineMarkdown>{t.meaning}</InlineMarkdown>
              </dd>
            </div>
          ))}
        </dl>
      </Block>
      <Block title="An analogy" tone="accent">
        <Markdown>{c.analogy}</Markdown>
      </Block>
    </>
  );
}

// 2 ------------------------------------------------------------------------

function MentalModelSection({ ctx }: { ctx: Ctx }) {
  const m = ctx.topic.mental_model;
  return (
    <>
      <Block>
        <Markdown>{m.body}</Markdown>
      </Block>
      <Block>
        <WindowStepper stepper={m.stepper} />
      </Block>
    </>
  );
}

// 3 ------------------------------------------------------------------------

function TsSection({ ctx }: { ctx: Ctx }) {
  const ts = ctx.topic.ts_fundamentals;
  return (
    <>
      <Markdown>{ts.intro}</Markdown>
      <div className="ndsa-grid">
        {ts.items.map((it) => (
          <Block key={it.name} title={<InlineMarkdown>{it.name}</InlineMarkdown>}>
            <Code code={it.code} />
            <Markdown>{it.explain}</Markdown>
          </Block>
        ))}
      </div>
      <h3 className="ndsa-h3 mt-4">Try it</h3>
      {ts.drills.map((d, i) => (
        <TrackedExercise key={d.id} index={i + 1} exercise={d} onSolved={ctx.onMark} />
      ))}
    </>
  );
}

// 4 ------------------------------------------------------------------------

function PatternsSection({ ctx }: { ctx: Ctx }) {
  const p = ctx.topic.patterns;
  return (
    <>
      <Block>
        <Markdown>{p.intro}</Markdown>
      </Block>
      {p.items.map((it, i) => (
        <Block key={it.name} title={`${i + 1}. ${it.name}`}>
          <p className="dim mt-0">
            <strong>Reach for it when:</strong> <InlineMarkdown>{it.when}</InlineMarkdown>
          </p>
          <Code code={it.code} />
          <p className="mb-0">
            <InlineMarkdown>{it.note}</InlineMarkdown>
          </p>
        </Block>
      ))}
    </>
  );
}

// 5 ------------------------------------------------------------------------

function WhenToUseSection({ ctx }: { ctx: Ctx }) {
  const w = ctx.topic.when_to_use;
  return (
    <>
      <Markdown>{w.intro}</Markdown>
      <ScrollX label="Clues" className="card p-0">
        <table className="ndsa-table">
          <thead>
            <tr>
              <th>If the problem says…</th>
              <th>…it is a clue because</th>
            </tr>
          </thead>
          <tbody>
            {w.clues.map((c) => (
              <tr key={c.clue}>
                <td className="ndsa-clue">
                  <InlineMarkdown>{c.clue}</InlineMarkdown>
                </td>
                <td>
                  <InlineMarkdown>{c.why}</InlineMarkdown>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </ScrollX>
      <Block tone="accent">
        <Markdown>{w.test}</Markdown>
      </Block>
    </>
  );
}

// 6 ------------------------------------------------------------------------

function WhenNotSection({ ctx }: { ctx: Ctx }) {
  const w = ctx.topic.when_not;
  return (
    <>
      <Markdown>{w.intro}</Markdown>
      {w.cases.map((c) => (
        <div key={c.looks_like + c.but} className="cur-panel ndsa-lookalike">
          <div className="ndsa-flow">
            <div className="ndsa-flow-step">
              <span className="cur-eyebrow">Looks like</span>
              <InlineMarkdown>{c.looks_like}</InlineMarkdown>
            </div>
            <Icon name="chevronDown" size={16} />
            <div className="ndsa-flow-step is-bad">
              <span className="cur-eyebrow">But</span>
              <InlineMarkdown>{c.but}</InlineMarkdown>
            </div>
            <Icon name="chevronDown" size={16} />
            <div className="ndsa-flow-step is-good">
              <span className="cur-eyebrow">Use instead</span>
              <strong>
                <InlineMarkdown>{c.use_instead}</InlineMarkdown>
              </strong>
            </div>
          </div>
          <p className="ndsa-flow-why">
            <InlineMarkdown>{c.why}</InlineMarkdown>
          </p>
        </div>
      ))}
    </>
  );
}

// 7 ------------------------------------------------------------------------

function Trace({ headers, rows, label }: { headers: string[]; rows: string[][]; label: string }) {
  return (
    <ScrollX label={label} className="card p-0">
      <table className="ndsa-table ndsa-trace">
        <thead>
          <tr>
            {headers.map((h) => (
              <th key={h}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              {r.map((cell, j) => (
                <td key={j}>
                  <code>{cell}</code>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </ScrollX>
  );
}

function ExamplesSection({ ctx }: { ctx: Ctx }) {
  const { topic, solved, onMark } = ctx;
  return (
    <>
      <p className="dim mt-0">
        Three examples, each explained less than the one before: every line, then only what changed, then the
        technique on a real problem.
      </p>
      {topic.examples.map((e, i) => (
        <Block
          key={e.title}
          title={
            <>
              <Badge tone="accent">
                Example {i + 1} · {e.level}
              </Badge>{" "}
              {e.title}
            </>
          }
        >
          <Markdown>{e.problem}</Markdown>
          <Code code={e.code} />
          {e.lines.length > 0 && (
            <ScrollX label="Line by line" className="card p-0">
              <table className="ndsa-table">
                <thead>
                  <tr>
                    <th>Line</th>
                    <th>What it does</th>
                  </tr>
                </thead>
                <tbody>
                  {e.lines.map((l) => (
                    <tr key={l.code}>
                      <td className="ndsa-line-code">
                        <code>{l.code}</code>
                      </td>
                      <td>
                        <InlineMarkdown>{l.explain}</InlineMarkdown>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </ScrollX>
          )}
          {e.question && (
            <QuestionCard
              index="?"
              question={e.question}
              done={solved.has(questionId(topic.key, "examples", i))}
              onCorrect={() => onMark(questionId(topic.key, "examples", i))}
            />
          )}
          {e.trace && <Trace headers={e.trace.headers} rows={e.trace.rows} label={`Trace of example ${i + 1}`} />}
          {e.notes.length > 0 && (
            <ul className="ndsa-notes">
              {e.notes.map((n) => (
                <li key={n}>
                  <InlineMarkdown>{n}</InlineMarkdown>
                </li>
              ))}
            </ul>
          )}
          {e.takeaway && <Markdown>{e.takeaway}</Markdown>}
        </Block>
      ))}
    </>
  );
}

// 8 ------------------------------------------------------------------------

function Stage({ letter, title, children }: { letter: string; title: string; children: ReactNode }) {
  return (
    <section className="ndsa-stage">
      <div className="ndsa-stage-head">
        <span className="ndsa-stage-letter">{letter}</span>
        <h3 className="ndsa-h3">{title}</h3>
      </div>
      {children}
    </section>
  );
}

function ImplementationSection({ ctx }: { ctx: Ctx }) {
  const im = ctx.topic.implementation;
  const numbered = im.read.code
    .trimEnd()
    .split("\n")
    .map((l, i) => `${String(i + 1).padStart(2, " ")}  ${l}`)
    .join("\n");
  return (
    <>
      <p className="dim mt-0">Four stages, each with less support than the one before.</p>
      <Stage letter="A" title="Read the code">
        <Block title={im.read.title}>
          <Markdown>{im.read.problem}</Markdown>
          <Code code={numbered} />
          <ul className="ndsa-notes">
            {im.read.notes.map((n) => (
              <li key={n.line}>
                <strong>Line {n.line}</strong>: <InlineMarkdown>{n.text}</InlineMarkdown>
              </li>
            ))}
          </ul>
          <Markdown>{im.read.why_it_works}</Markdown>
        </Block>
      </Stage>
      <Stage letter="B" title="Complete the code">
        <TrackedExercise index={1} exercise={im.complete} onSolved={ctx.onMark} />
      </Stage>
      <Stage letter="C" title="Pseudocode → TypeScript">
        <Block title={im.pseudocode.title}>
          <Markdown>{im.pseudocode.problem}</Markdown>
          <Code code={im.pseudocode.pseudocode} lang="text" />
        </Block>
        <TrackedExercise index={2} exercise={im.pseudocode.exercise} onSolved={ctx.onMark} />
      </Stage>
      <Stage letter="D" title="From scratch">
        <TrackedExercise index={3} exercise={im.scratch} onSolved={ctx.onMark} challenge />
      </Stage>
    </>
  );
}

// 9 ------------------------------------------------------------------------

function ComplexitySection({ ctx }: { ctx: Ctx }) {
  const { topic, solved, onMark } = ctx;
  const c = topic.complexity;
  return (
    <>
      <div className="ndsa-bigo">
        <div className="cur-panel">
          <span className="cur-eyebrow">Time</span>
          <div className="cur-big-stat">{c.time}</div>
        </div>
        <div className="cur-panel">
          <span className="cur-eyebrow">Space</span>
          <div className="ndsa-space">{c.space}</div>
        </div>
      </div>
      <Block>
        <Markdown>{c.body}</Markdown>
      </Block>
      <h3 className="ndsa-h3">Compared with the alternatives</h3>
      <ScrollX label="Approaches" className="card p-0">
        <table className="ndsa-table">
          <thead>
            <tr>
              <th>Approach</th>
              <th>Time</th>
              <th>Space</th>
              <th>Why</th>
            </tr>
          </thead>
          <tbody>
            {c.compare.map((a) => (
              <tr key={a.approach}>
                <td>{a.approach}</td>
                <td>
                  <code>{a.time}</code>
                </td>
                <td>
                  <code>{a.space}</code>
                </td>
                <td>
                  <InlineMarkdown>{a.note}</InlineMarkdown>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </ScrollX>
      <Block title="Why did it improve?">
        <Markdown>{c.why_improved}</Markdown>
        <div className="ndsa-rewrite">
          <div>
            <span className="cur-eyebrow">Slow</span>
            <Code code={c.rewrite.slow} />
          </div>
          <div>
            <span className="cur-eyebrow">Fast</span>
            <Code code={c.rewrite.fast} />
          </div>
        </div>
        <p className="mb-0">
          <strong>The edit:</strong> <InlineMarkdown>{c.rewrite.edit}</InlineMarkdown>
        </p>
      </Block>
      <h3 className="ndsa-h3">Price it yourself</h3>
      {c.questions.map((q, i) => (
        <QuestionCard
          key={q.question}
          index={i + 1}
          question={q}
          done={solved.has(questionId(topic.key, "complexity", i))}
          onCorrect={() => onMark(questionId(topic.key, "complexity", i))}
        />
      ))}
    </>
  );
}

// 10 -----------------------------------------------------------------------

function MistakesSection({ ctx }: { ctx: Ctx }) {
  const mistakes = ctx.topic.mistakes;
  const categories = [...new Set(mistakes.map((m) => m.category))];
  const [filter, setFilter] = useState<string | null>(null);
  const shown = filter ? mistakes.filter((m) => m.category === filter) : mistakes;
  return (
    <>
      <div className="cur-chips mb-3">
        <Chip pressed={filter === null} onClick={() => setFilter(null)} count={mistakes.length}>
          All
        </Chip>
        {categories.map((c) => (
          <Chip
            key={c}
            pressed={filter === c}
            onClick={() => setFilter(c)}
            count={mistakes.filter((m) => m.category === c).length}
          >
            {c}
          </Chip>
        ))}
      </div>
      {shown.map((m) => (
        <Block
          key={m.title}
          title={
            <>
              {m.title} <Badge>{m.category}</Badge>
            </>
          }
        >
          <div className="ndsa-mistake">
            <div className="ndsa-mistake-code is-bad">
              <span className="cur-eyebrow">❌ Mistake</span>
              <Code code={m.wrong} />
            </div>
            <div className="ndsa-mistake-code is-good">
              <span className="cur-eyebrow">✅ Correct approach</span>
              <Code code={m.right} />
            </div>
          </div>
          <dl className="ndsa-terms">
            <div className="ndsa-term">
              <dt>Why it happens</dt>
              <dd>
                <InlineMarkdown>{m.why}</InlineMarkdown>
              </dd>
            </div>
            <div className="ndsa-term">
              <dt>How to recognise it</dt>
              <dd>
                <InlineMarkdown>{m.recognise}</InlineMarkdown>
              </dd>
            </div>
          </dl>
        </Block>
      ))}
    </>
  );
}

// 11 -----------------------------------------------------------------------

function RecognitionSection({ ctx }: { ctx: Ctx }) {
  const { topic, solved, onMark } = ctx;
  const r = topic.recognition;
  const right = r.questions.filter((_, i) => solved.has(questionId(topic.key, "recognition", i))).length;
  return (
    <>
      <Markdown>{r.intro}</Markdown>
      <p className="dim">
        {right} / {r.questions.length} answered correctly.
      </p>
      {r.questions.map((q, i) => (
        <QuestionCard
          key={q.question}
          index={i + 1}
          question={q}
          done={solved.has(questionId(topic.key, "recognition", i))}
          onCorrect={() => onMark(questionId(topic.key, "recognition", i))}
        />
      ))}
    </>
  );
}

// 12 -----------------------------------------------------------------------

function GuidedSection({ ctx }: { ctx: Ctx }) {
  return (
    <>
      <p className="dim mt-0">
        The curriculum still teaches here. Each problem is walked in order: understand the input and output, identify
        the concept, choose an approach, write pseudocode, implement, test. The hints come in four layers, and each
        one is shown only when you ask.
      </p>
      {ctx.topic.guided.map((g, i) => (
        <GuidedFlow
          key={g.key}
          topicKey={ctx.topic.key}
          guided={g}
          index={i + 1}
          solved={ctx.solved.has(g.exercise.id)}
          onSolved={ctx.onMark}
        />
      ))}
    </>
  );
}

// 13 -----------------------------------------------------------------------

function ProblemRow({ slug, problem, note, noteLabel }: { slug: string; problem?: Problem; note: string; noteLabel: string }) {
  const nav = useNavigate();
  const [show, setShow] = useState(false);
  const done = problem?.solved_status === "solved";
  return (
    <div className="ndsa-problem">
      <div className="ndsa-problem-row">
        <span className={`cur-num ${done ? "complete" : ""}`}>{done ? <Icon name="check" size={14} /> : <Icon name="code" size={14} />}</span>
        <span className="ndsa-problem-title">{problem?.title ?? slug}</span>
        {problem && <DiffBadge d={problem.difficulty} />}
        <span className="spacer" />
        {note && (
          <Button variant="ghost" size="sm" icon={show ? "hide" : "hint"} onClick={() => setShow((s) => !s)} aria-expanded={show}>
            {show ? `Hide ${noteLabel}` : noteLabel}
          </Button>
        )}
        <Button size="sm" variant={done ? "ghost" : "primary"} onClick={() => problem && nav(`/solve/${problem.id}`)} disabled={!problem}>
          {done ? "Solve again" : "Open"}
        </Button>
      </div>
      {show && (
        <p className="ndsa-problem-note">
          <InlineMarkdown>{note}</InlineMarkdown>
        </p>
      )}
    </div>
  );
}

function IndependentSection({ ctx }: { ctx: Ctx }) {
  const ind = ctx.topic.independent;
  return (
    <>
      <Markdown>{ind.intro}</Markdown>
      <div className="cur-panel ndsa-problems">
        {ind.problems.map((p) => (
          <ProblemRow key={p.slug} slug={p.slug} problem={ctx.bySlug.get(p.slug)} note={p.nudge} noteLabel="Nudge" />
        ))}
      </div>
    </>
  );
}

// 14 -----------------------------------------------------------------------

function VariationsSection({ ctx }: { ctx: Ctx }) {
  let n = 0;
  return (
    <>
      <p className="dim mt-0">
        The same technique, deliberately changed one step at a time, so you learn what to change rather than memorising
        one solution.
      </p>
      <ol className="ndsa-ladder">
        {ctx.topic.variations.map((v) => (
          <li key={v.step} className="ndsa-ladder-step">
            <span className="cur-eyebrow">{v.step}</span>
            <Block title={v.title}>
              <Markdown>{v.change}</Markdown>
              <VerdictPanel tone="info" icon="sparkles" title="The insight">
                <Markdown>{v.insight}</Markdown>
              </VerdictPanel>
              {v.exercise && <TrackedExercise index={++n} exercise={v.exercise} onSolved={ctx.onMark} challenge />}
              {v.slug && (
                <div className="ndsa-problems">
                  <ProblemRow slug={v.slug} problem={ctx.bySlug.get(v.slug)} note="" noteLabel="" />
                </div>
              )}
            </Block>
          </li>
        ))}
      </ol>
    </>
  );
}

// 15 -----------------------------------------------------------------------

function ReviewSection({ ctx }: { ctx: Ctx }) {
  const r = ctx.topic.review;
  const q = r.quick_ref;
  return (
    <>
      <div className="ndsa-review">
        <Block title="Must know">
          <dl className="ndsa-terms">
            {r.must_know.map((k) => (
              <div key={k.label} className="ndsa-term">
                <dt>{k.label}</dt>
                <dd>
                  <InlineMarkdown>{k.text}</InlineMarkdown>
                </dd>
              </div>
            ))}
          </dl>
        </Block>
        <Block title="Must be able to">
          <ul className="ndsa-checklist">
            {r.must_do.map((d) => (
              <li key={d}>
                <Icon name="todo" size={14} /> <InlineMarkdown>{d}</InlineMarkdown>
              </li>
            ))}
          </ul>
        </Block>
      </div>
      <Block title="Quick reference" tone="accent">
        <dl className="ndsa-terms ndsa-quickref">
          <div className="ndsa-term">
            <dt>Pattern</dt>
            <dd>{q.pattern}</dd>
          </div>
          <div className="ndsa-term">
            <dt>Typical syntax</dt>
            <dd>
              <Code code={q.syntax} />
            </dd>
          </div>
          <div className="ndsa-term">
            <dt>Time</dt>
            <dd>{q.time}</dd>
          </div>
          <div className="ndsa-term">
            <dt>Space</dt>
            <dd>{q.space}</dd>
          </div>
          <div className="ndsa-term">
            <dt>Think of this when</dt>
            <dd>{q.think_when}</dd>
          </div>
          <div className="ndsa-term">
            <dt>Be careful about</dt>
            <dd>
              <InlineMarkdown>{q.careful}</InlineMarkdown>
            </dd>
          </div>
        </dl>
      </Block>
    </>
  );
}

// 16 -----------------------------------------------------------------------

function GateHead({ gate, n }: { gate: Gate; n: number }) {
  return (
    <div className="ndsa-gate-head">
      <span className={`cur-num ${gate.passed ? "complete" : ""}`}>{gate.passed ? <Icon name="check" size={14} /> : n}</span>
      <div>
        <strong>{gate.label}</strong>
        <div className="dim text-xs">
          {gate.test}
          {gate.detail && ` · ${gate.detail}`}
        </div>
      </div>
      <span className="spacer" />
      <Badge tone={gate.passed ? "good" : "neutral"}>{gate.passed ? "passed" : "not yet"}</Badge>
    </div>
  );
}

function MasterySection({ ctx }: { ctx: Ctx }) {
  const { topic, onMark, gates } = ctx;
  const m = topic.mastery;
  const g = Object.fromEntries(gates.map((x) => [x.ability, x])) as Record<Gate["ability"], Gate>;
  const all = gates.every((x) => x.passed);
  return (
    <>
      <Markdown>{m.intro}</Markdown>
      <div className="ndsa-gates" role="list">
        {gates.map((x) => (
          <div key={x.ability} role="listitem" className={`ndsa-gate-chip ${x.passed ? "is-passed" : ""}`}>
            <Icon name={x.passed ? "done" : "todo"} size={14} /> {x.label}
          </div>
        ))}
      </div>
      {all && (
        <VerdictPanel tone="good" icon="trophy" title={`${topic.title} mastered`}>
          <p className="verdict-para">
            All five abilities passed. Come back to the Recognition and Application gates in a few weeks: mastery that is
            never re-tested fades.
          </p>
        </VerdictPanel>
      )}

      <Block title={<GateHead gate={g.understanding} n={1} />}>
        <Sitting
          title="Explain it"
          questions={m.understanding.questions}
          pass={m.understanding.pass}
          passed={g.understanding.passed}
          onPass={() => onMark(sittingId(topic.key, "understanding"))}
        />
      </Block>
      <Block title={<GateHead gate={g.syntax} n={2} />}>
        <TrackedExercise index={1} exercise={m.syntax} onSolved={onMark} />
      </Block>
      <Block title={<GateHead gate={g.recognition} n={3} />}>
        <Sitting
          title="Name the technique"
          questions={m.recognition.questions}
          pass={m.recognition.pass}
          passed={g.recognition.passed}
          onPass={() => onMark(sittingId(topic.key, "recognition"))}
        />
      </Block>
      <Block title={<GateHead gate={g.implementation} n={4} />}>
        <p className="dim mt-0">No scaffold, no hints: the signature and the examples only.</p>
        <TrackedExercise index={2} exercise={m.implementation} onSolved={onMark} challenge />
      </Block>
      <Block title={<GateHead gate={g.application} n={5} />}>
        <Markdown>{m.application.intro}</Markdown>
        <div className="ndsa-problems">
          {m.application.problems.map((p) => (
            <ProblemRow key={p.slug} slug={p.slug} problem={ctx.bySlug.get(p.slug)} note={p.reveal} noteLabel="Reveal the reframing" />
          ))}
        </div>
      </Block>
    </>
  );
}

