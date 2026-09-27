/**
 * One Learn chapter: the idea, the lesson, then the practice (UI_ROADMAP G4, G6).
 *
 * Sits on the reader layout, so a long chapter has an "On this page" rail with
 * the section in view highlighted, a reading-progress bar, and its completion
 * rule written out as a checklist that ticks itself — read to the end, solve
 * the exercises, pass the self-check — instead of a faint sentence at the
 * bottom that you only saw once you were already there.
 */

import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import type { Concept, Problem, SqlDataset } from "../../types";
import { useCrumb } from "../../store";
import { Markdown } from "../../components/Markdown";
import { LessonMarkdown } from "../../components/LessonMarkdown";
import { ChapterCheatSheet } from "../../components/ChapterCheatSheet";
import { CardStudy } from "../../components/CardStudy";
import { DatasetBrowser } from "../../components/SqlGrid";
import { DiffBadge } from "../../components/common";
import { Section, useCollapse } from "../../components/Collapsible";
import { TrackSkeleton } from "../../components/Skeleton";
import { ExerciseCard, QuizSection } from "../../components/exercise";
import { ReaderLayout, ReadStatus, useSeenBottom } from "../../components/reader/Reader";
import { Badge, Button, EmptyState, ErrorState, Segmented } from "../../components/ui";
import { loadSolvedExercises, markExerciseSolved, solvedExercises } from "../../lib/learnProgress";
import { loadFailed } from "../../lib/failures";
import { useNavigate } from "react-router-dom";
import { conceptLang, langLabel, studyVariant, useLearnData } from "./learnData";

export default function ConceptPage() {
  const { key } = useParams();
  const nav = useNavigate();
  const { concepts, error, reload, problems, datasets, done, markDone } = useLearnData();

  if (error) {
    return (
      <div className="page">
        <ErrorState title="The concept library could not be loaded." error={error} onRetry={reload} />
      </div>
    );
  }
  if (!concepts) return <TrackSkeleton cards={6} />;
  const concept = concepts.find((c) => c.key === key);
  if (!concept) {
    return (
      <div className="page">
        <EmptyState
          icon="learn"
          title="Concept not found."
          action={{ label: "Back to Learn", icon: "back", onClick: () => nav("/learn") }}
        />
      </div>
    );
  }
  const related = problems.filter((p) => p.prerequisites?.some((pr) => pr.key === concept.key));
  return (
    <ConceptDetail
      // Fresh state per chapter: the sentinel, the quiz score, the study mode.
      key={concept.key}
      concept={concept}
      related={related}
      problems={problems}
      datasets={datasets}
      isDone={done.has(concept.key)}
      onSetDone={(v) => markDone(concept.key, v)}
    />
  );
}

function ConceptDetail({
  concept,
  related,
  problems,
  datasets,
  isDone,
  onSetDone,
}: {
  concept: Concept;
  related: Problem[];
  problems: Problem[];
  datasets: Map<string, SqlDataset>;
  isDone: boolean;
  onSetDone: (done: boolean) => void;
}) {
  useCrumb(concept.name, "Lesson");
  const lang = conceptLang(concept);
  const bySlug = useMemo(() => new Map(problems.map((p) => [p.slug, p])), [problems]);

  const exercises = concept.exercises ?? [];
  const drills = exercises.filter((e) => (e.kind || "drill") !== "challenge");
  const challenges = exercises.filter((e) => e.kind === "challenge");
  const cards = concept.cards ?? [];
  const quiz = concept.quiz ?? [];

  // Completion: read to the bottom AND solve every exercise AND pass the quiz.
  // A glossary set has no exercises, so without the quiz rule reaching the
  // bottom used to be the whole bar.
  const [solvedEx, setSolvedEx] = useState<Set<string>>(() => solvedExercises());
  const [bottomRef, seenBottom] = useSeenBottom(concept.key);
  const [quizCorrect, setQuizCorrect] = useState(0);
  const onSolved = (id: string) => setSolvedEx(new Set(markExerciseSolved(id)));

  // The initialiser reads a module-level cache (warm after the first load of
  // the session); this fills it on a cold start.
  useEffect(() => {
    loadSolvedExercises().then(setSolvedEx).catch(loadFailed("your solved exercises"));
  }, []);

  const solvedN = exercises.filter((e) => solvedEx.has(e.id)).length;
  const allSolved = solvedN === exercises.length;
  const quizPassed = quiz.length === 0 || quizCorrect === quiz.length;

  useEffect(() => {
    if (!isDone && seenBottom && allSolved && quizPassed) onSetDone(true);
  }, [isDone, seenBottom, allSolved, quizPassed, onSetDone]);

  const steps = [
    { label: "Read to the end", met: seenBottom || isDone },
    ...(exercises.length > 0
      ? [{ label: `Solve the exercises (${solvedN}/${exercises.length})`, met: allSolved }]
      : []),
    ...(quiz.length > 0 ? [{ label: `Pass the self-check (${quizCorrect}/${quiz.length})`, met: quizPassed }] : []),
  ];

  const practiceRefs = (concept.practice ?? [])
    .map((pr) => ({ note: pr.note, problem: bySlug.get(pr.slug) }))
    .filter((x): x is { note: string; problem: Problem } => !!x.problem);
  const [mode, setMode] = useState<"lesson" | "cards">("lesson");

  // The datasets this chapter's exercises query, in first-use order. Shown once
  // at the top rather than on every card: joins are unlearnable without being
  // able to see the rows you are joining.
  const usedDatasets = useMemo(() => {
    const keys: string[] = [];
    for (const ex of exercises) if (ex.dataset && !keys.includes(ex.dataset)) keys.push(ex.dataset);
    return keys.map((k) => datasets.get(k)).filter((d): d is SqlDataset => !!d);
  }, [exercises, datasets]);
  const [activeDataset, setActiveDataset] = useState(0);

  // Sections fold per concept, so a long chapter can be narrowed down to just
  // the drills (or just the lesson) and stay that way when you come back.
  const sec = useCollapse(`learn-sec:${concept.key}`);
  const secKeys = ["idea", "lesson", "dataset", "quiz", "practice", "drills", "challenges", "library"];

  const ideaLabel =
    lang === "japanese"
      ? "How to read this"
      : lang === "algorithms"
        ? "At a glance"
        : lang === "java_vocab"
          ? "How to use this set"
          : `In ${langLabel(lang)}`;

  return (
    <div className="page concept-page">
      <ReaderLayout
        aside={
          <ReadStatus steps={steps} complete={isDone} onToggle={() => onSetDone(!isDone)} />
        }
      >
        <header className="page-header concept-header">
          <div className="page-header-text">
            <div className="page-eyebrow">
              <Link to={`/learn?track=${lang}`}>{langLabel(lang)}</Link> · {concept.category}
            </div>
            <h1 className="page-title">{concept.name}</h1>
            <p className="page-sub">{concept.what}</p>
          </div>
          <div className="page-header-actions">
            <Button variant="ghost" size="sm" icon="chevronDown" onClick={() => sec.setAll(secKeys, true)}>
              Expand all
            </Button>
            <Button variant="ghost" size="sm" icon="chevronRight" onClick={() => sec.setAll(secKeys, false)}>
              Collapse all
            </Button>
          </div>
        </header>

        <Section title="The idea" open={sec.isOpen("idea")} onToggle={() => sec.toggle("idea")}>
          <div className="card concept-deep">
            <p>{concept.deep}</p>
          </div>
          <div className="card card-accent concept-lang">
            <div className="io-label">{ideaLabel}</div>
            <Markdown>{concept.java}</Markdown>
          </div>
        </Section>

        <Section
          title={cards.length > 0 ? "Reference" : "Lesson"}
          open={sec.isOpen("lesson")}
          onToggle={() => sec.toggle("lesson")}
        >
          {cards.length > 0 && (
            <div className="concept-mode">
              <Segmented
                label="Show"
                value={mode}
                onChange={setMode}
                options={[
                  { value: "lesson", label: "Glossary" },
                  { value: "cards", label: "Study cards" },
                ]}
              />
            </div>
          )}
          {cards.length > 0 && mode === "cards" ? (
            <CardStudy conceptKey={concept.key} cards={cards} variant={studyVariant(concept)} />
          ) : (
            <div className="lesson-body">
              <LessonMarkdown>{concept.lesson}</LessonMarkdown>
            </div>
          )}
        </Section>

        {lang === "typescript" && (
          <Section
            title="Cheat sheet"
            // Folded by default: useCollapse opens sections unless toggled, so
            // this one reads the inverse of its own key.
            open={!sec.isOpen("cheatsheet")}
            onToggle={() => sec.toggle("cheatsheet")}
          >
            <ChapterCheatSheet name={concept.name} what={concept.what} lesson={concept.lesson} />
          </Section>
        )}

        {usedDatasets.length > 0 && (
          <Section
            title="The dataset"
            open={sec.isOpen("dataset")}
            onToggle={() => sec.toggle("dataset")}
            meta={
              <Badge icon="database">
                {usedDatasets.length === 1 ? usedDatasets[0].key : `${usedDatasets.length} databases`}
              </Badge>
            }
          >
            <p className="section-lead">
              Every exercise below runs against a <strong>fresh copy</strong> of one of these, rebuilt from scratch each
              time — so nothing you run can break anything. Read the rows before you write the query.
            </p>
            {usedDatasets.length > 1 && (
              <Segmented
                label="Dataset"
                value={String(activeDataset)}
                onChange={(v) => setActiveDataset(Number(v))}
                options={usedDatasets.map((d, i) => ({ value: String(i), label: d.title }))}
              />
            )}
            <DatasetBrowser dataset={usedDatasets[Math.min(activeDataset, usedDatasets.length - 1)]} />
          </Section>
        )}

        {quiz.length > 0 && (
          <Section
            title="Check yourself"
            open={sec.isOpen("quiz")}
            onToggle={() => sec.toggle("quiz")}
            meta={<Badge>{quiz.length} questions</Badge>}
          >
            <p className="section-lead">
              {quiz.length} quick questions. Pick an answer to see whether it&rsquo;s right and <strong>why</strong>.
              No code to run — just recall.
            </p>
            <QuizSection questions={quiz} onScore={setQuizCorrect} />
          </Section>
        )}

        {practiceRefs.length > 0 && (
          <Section
            title="Practice this technique"
            open={sec.isOpen("practice")}
            onToggle={() => sec.toggle("practice")}
            meta={<Badge>{practiceRefs.length} problems</Badge>}
          >
            <p className="section-lead">
              Real problems from the Library where this idea is the key. Solve them in whatever language you like.
            </p>
            <ProblemLinks items={practiceRefs} />
          </Section>
        )}

        {drills.length > 0 && (
          <Section
            title="Warm-up drills — fill in the blank"
            outline="Warm-up drills"
            open={sec.isOpen("drills")}
            onToggle={() => sec.toggle("drills")}
            meta={<Badge>{drills.length} drills</Badge>}
          >
            <p className="section-lead">
              Everything is written except the one piece this lesson teaches. Replace <code>____</code>, then press{" "}
              <strong>Check</strong>.
            </p>
            {drills.map((ex, i) => (
              <ExerciseCard
                key={ex.id}
                index={i + 1}
                exercise={ex}
                dataset={ex.dataset ? datasets.get(ex.dataset) : undefined}
                source={ex.source_slug ? bySlug.get(ex.source_slug) : undefined}
                onSolved={onSolved}
              />
            ))}
          </Section>
        )}

        {challenges.length > 0 && (
          <Section
            title={challenges.length > 1 ? "Coding challenges" : "Coding challenge"}
            open={sec.isOpen("challenges")}
            onToggle={() => sec.toggle("challenges")}
            accent="accent"
            meta={
              <Badge tone="accent" icon="trophy">
                {challenges.length} challenge{challenges.length > 1 ? "s" : ""}
              </Badge>
            }
          >
            <p className="section-lead">
              Now put it together: a complete little problem using only what you&rsquo;ve learned so far. Write the
              whole solution where you see <code>____</code>, then <strong>Check</strong>. Stuck? Reveal the solution.
            </p>
            {challenges.map((ex, i) => (
              <ExerciseCard
                key={ex.id}
                index={i + 1}
                exercise={ex}
                challenge
                dataset={ex.dataset ? datasets.get(ex.dataset) : undefined}
                source={ex.source_slug ? bySlug.get(ex.source_slug) : undefined}
                onSolved={onSolved}
              />
            ))}
          </Section>
        )}

        {lang !== "japanese" && related.length > 0 && (
          <Section
            title="Practice more in the Library"
            open={sec.isOpen("library")}
            onToggle={() => sec.toggle("library")}
            meta={<Badge>{related.length}</Badge>}
          >
            <ProblemLinks items={related.map((problem) => ({ problem, note: "" }))} />
          </Section>
        )}

        <div className="concept-end">
          <ReadStatus steps={steps} complete={isDone} compact />
        </div>

        {/* Sentinel: intersecting means the page has been read to the bottom. */}
        <div ref={bottomRef} className="read-sentinel" />
      </ReaderLayout>
    </div>
  );
}

/** Problems as links — Ctrl-click opens them, Tab reaches them (D3). */
function ProblemLinks({ items }: { items: { problem: Problem; note: string }[] }) {
  return (
    <ul className="problem-links">
      {items.map(({ problem, note }) => (
        <li key={problem.id}>
          <Link to={`/solve/${problem.id}`} className="card problem-link">
            <span className="problem-link-head">
              <strong>{problem.title}</strong>
              <DiffBadge d={problem.difficulty} />
            </span>
            {note && <span className="problem-link-note">{note}</span>}
          </Link>
        </li>
      ))}
    </ul>
  );
}
