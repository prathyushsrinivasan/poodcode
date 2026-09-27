/**
 * One Projects module: the whole development process for one slice of the
 * application (UI_ROADMAP G7, G4).
 *
 * WHY (the problem the last module left behind) → WHERE (goal, deliverable) →
 * SYNTAX (everything it needs, before it is used) → DO IT (ordered steps) →
 * DID I GET IT (the module build, the checks, the reveal).
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import type { BackendStep, Project, ProjectModule } from "../../types";
import { useCrumb } from "../../store";
import { InlineMarkdown, Markdown } from "../../components/Markdown";
import { ExerciseCard, QuizSection, ReferenceReveal, VerdictPanel } from "../../components/exercise";
import { ExerciseSections } from "../../components/ExerciseSections";
import { DiffStatBadge, DiffView } from "../../components/DiffView";
import { Section, useCollapse } from "../../components/Collapsible";
import { UnitPager } from "../../components/track/TrackShell";
import { EndpointTable } from "../../components/track/EndpointTable";
import {
  Glossary,
  Milestone,
  SubHeading,
  UnitContents,
  UnitGoal,
  UnitList,
  UnitPart,
  scrollToPart,
} from "../../components/track/UnitParts";
import { ReaderLayout, ReadStatus, useSeenBottom } from "../../components/reader/Reader";
import { Badge, Button, ConfirmDialog, Icon, PageHeader, ProgressBar, Toggle } from "../../components/ui";
import { useToast } from "../../components/Toast";
import { loadSolvedExercises, markExerciseSolved, solvedExercises, unmarkExercisesSolved } from "../../lib/learnProgress";
import { loadFailed } from "../../lib/failures";
import { plural, solvedLabel, studyTime } from "../../lib/trackProgress";
import { diffSources, diffStats } from "../../lib/lineDiff";
import { SyntaxCard } from "./Handbook";
import { requiredExerciseIds } from "./shared";
import { inlineCode } from "../../components/common";

export default function ModulePage({
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
  useCrumb(mod.title, `Module ${mod.number}`, [project.title]);
  const toast = useToast();
  const [params, setParams] = useSearchParams();
  const [solvedEx, setSolvedEx] = useState<Set<string>>(() => solvedExercises());
  // Bumped by "Start over": auto-completion then needs the module read to the
  // bottom *again*, or a module with nothing to solve would re-complete itself
  // the instant it was reset.
  const [readRound, setReadRound] = useState(0);
  const [bottomRef, seenBottom] = useSeenBottom(`${mod.key}:${readRound}`);
  const celebrated = useRef(false);
  // Steps start collapsed: each open step mounts a Monaco editor per exercise.
  // Keyed by project as well as module, because module keys are only unique
  // within a project.
  const sec = useCollapse(`project-sec:${project.key}:${mod.key}`, false);
  const steps = mod.steps ?? [];
  const stepKeys = useMemo(() => steps.map((s) => s.key), [steps]);
  const phase = project.roadmap.find((p) => p.key === mod.phase);

  // Which step the URL points at. A module is a long page, so without this a
  // reload — or a link to "the bit about routing" — always lands at the top.
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
    scrollToPart(`step-${key}`);
  }

  /** A step's own header was clicked: keep the URL pointing at what is open.
   * Closing a step only clears `?step=` when it is the step the URL names, and
   * `appliedStep` tracks that either way, so folding away some other step
   * cannot yank the page back up to the linked one. */
  function toggleStep(key: string) {
    const opening = !sec.isOpen(key);
    const nextParam = opening ? key : stepParam === key ? null : stepParam;
    appliedStep.current = nextParam;
    sec.toggle(key);
    setStepParam(nextParam);
  }

  // Apply `?step=` once per value. The guard matters because `sec.isOpen`
  // changes identity whenever any section toggles.
  useEffect(() => {
    if (!stepParam || appliedStep.current === stepParam) return;
    if (!steps.some((s) => s.key === stepParam)) return;
    appliedStep.current = stepParam;
    if (!sec.isOpen(stepParam)) sec.toggle(stepParam);
    scrollToPart(`step-${stepParam}`);
  }, [stepParam, steps, sec]);

  const gradableIds = useMemo(() => requiredExerciseIds(mod), [mod]);
  const allSolved = gradableIds.every((id) => solvedEx.has(id));
  const solvedCount = gradableIds.filter((id) => solvedEx.has(id)).length;
  const [confirmReset, setConfirmReset] = useState(false);

  // Where "pick up where I left off" goes: the first step still holding an
  // unsolved exercise, or the module build if the steps are all done.
  const firstUnsolvedStep = steps.find((s) => (s.exercises ?? []).some((e) => !solvedEx.has(e.id)));
  const finalBuildUnsolved = !!mod.final_build && !solvedEx.has(mod.final_build.id);
  const canResume = !!firstUnsolvedStep || finalBuildUnsolved;

  function resume() {
    if (firstUnsolvedStep) openStep(firstUnsolvedStep.key);
    else scrollToPart("module-build");
  }

  function handleSolved(id: string) {
    setSolvedEx(new Set(markExerciseSolved(id)));
  }

  /** Start the module over: forget its solved exercises and its ✓, so it can be
   * worked again from scratch. Drafts are deliberately kept. */
  function resetModule() {
    setConfirmReset(false);
    setSolvedEx(new Set(unmarkExercisesSolved(gradableIds)));
    celebrated.current = false; // so finishing it again celebrates again
    setReadRound((n) => n + 1);
    if (isDone) onSetDone(false);
    toast(`Module ${mod.number} reset.`);
  }

  // Hydrate the solved set from SQLite (the initialiser reads a warm cache).
  useEffect(() => {
    loadSolvedExercises().then(setSolvedEx).catch(loadFailed("your solved exercises"));
  }, []);

  useEffect(() => {
    if (!isDone && seenBottom && allSolved && !celebrated.current) {
      celebrated.current = true;
      onSetDone(true);
      toast.success(mod.milestone ? `Module ${mod.number} complete! ${mod.milestone}` : `Module ${mod.number} complete!`);
    }
  }, [isDone, seenBottom, allSolved, onSetDone, toast, mod.milestone, mod.number]);

  const checklist = [
    { label: "Read to the end", met: seenBottom || isDone },
    ...(gradableIds.length > 0
      ? [{ label: `Solve the exercises (${solvedCount}/${gradableIds.length})`, met: allSolved }]
      : []),
  ];

  const newSyntax = (mod.syntax ?? []).filter((s) => !s.recap);
  const recapSyntax = (mod.syntax ?? []).filter((s) => s.recap);

  return (
    <div className="page project-module">
      <ReaderLayout
        aside={
          <>
            <ReadStatus steps={checklist} complete={isDone} onToggle={() => onSetDone(!isDone)} />
            {(isDone || solvedCount > 0) && (
              <Button
                variant="ghost"
                size="sm"
                icon="reset"
                onClick={() => setConfirmReset(true)}
                title="Forget this module's solved exercises so you can work it again"
              >
                Start this module over
              </Button>
            )}
          </>
        }
      >
        <PageHeader
          eyebrow={
            <>
              <Link to={`/projects/${project.key}`}>{project.title}</Link> · Module {mod.number} of {project.modules.length}
              {phase && ` · ${phase.title}`}
              {mod.est_minutes > 0 && (
                <>
                  {" "}
                  · <Icon name="clock" size={12} /> {studyTime(mod.est_minutes)}
                </>
              )}
            </>
          }
          title={mod.title}
          subtitle={mod.what}
        >
          {/* How far through the module you are — previously the only word on
              that was a line of small print below the very last section. */}
          {gradableIds.length > 0 && (
            <ProgressBar
              className="module-progress"
              value={solvedCount}
              max={gradableIds.length}
              tone={allSolved ? "good" : "accent"}
              label="Exercises solved in this module"
              showValue
            />
          )}
        </PageHeader>

        {/* 1. WHY — the problem the last module left behind. */}
        {mod.why && (
          <VerdictPanel tone="info" icon="hint" title="Why this module exists" className="unit-block">
            <p className="verdict-para">{inlineCode(mod.why)}</p>
          </VerdictPanel>
        )}

        {/* 2. WHERE — roadmap position and the thing it delivers. */}
        <UnitGoal
          label="Goal"
          goal={mod.goal}
          why={undefined}
          buildsOn={mod.builds_on.length > 0 ? [...mod.builds_on, ...mod.concepts] : undefined}
        />
        {mod.deliverable && (
          <p className="unit-why module-deliverable">
            <Icon name="projects" size={13} /> You will end up with: {inlineCode(mod.deliverable)}
          </p>
        )}
        <UnitList label="By the end of this module you can…" items={mod.objectives} />
        {mod.brief && <Markdown>{mod.brief}</Markdown>}

        {mod.endpoints.length > 0 && (
          <UnitPart title="This module's rows" icon="document" lead="The part of the contract this module implements.">
            <EndpointTable endpoints={mod.endpoints} />
          </UnitPart>
        )}

        {/* 3. SYNTAX — everything the module needs, before it is used. */}
        {newSyntax.length > 0 && (
          <UnitPart
            title="The syntax you need"
            icon="braces"
            lead="Everything this module uses, taught before it is used. Nothing below assumes syntax the project has not already shown you."
          >
            {newSyntax.map((s, i) => (
              <SyntaxCard key={i} item={s} />
            ))}
          </UnitPart>
        )}

        {recapSyntax.length > 0 && (
          <Section
            title="Already covered — a reminder"
            outline="Syntax recap"
            open={sec.isOpen("recap")}
            onToggle={() => sec.toggle("recap")}
            meta={<Badge>{recapSyntax.length} from earlier modules</Badge>}
          >
            {recapSyntax.map((s, i) => (
              <SyntaxCard key={i} item={s} dim />
            ))}
          </Section>
        )}

        {/* 4. DO IT — ordered steps, each with a checkpoint. */}
        {canResume && solvedCount > 0 && (
          <div className="module-resume">
            <Button variant="primary" size="sm" icon="forward" onClick={resume} title="Open the first step with an exercise you haven't solved">
              Pick up where I left off
            </Button>
          </div>
        )}
        <UnitContents
          title="Build it — these are in order"
          icon="build"
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
              onToggle={() => toggleStep(step.key)}
              meta={<span className="learn-cat-count">{solvedLabel(step.exercises, solvedEx)}</span>}
            >
              <StepBody step={step} onSolved={handleSolved} />
            </Section>
          </div>
        ))}

        {/* 5. DID I GET IT — the module build, then the reveal. */}
        {mod.final_build && (
          <div id="module-build">
            <UnitPart title="Module build" icon="build" lead="Everything above, assembled. This is the module.">
              <div className="module-build-actions">
                <Link
                  className="btn ghost btn-sm"
                  to={`/projects/${project.key}/workbench?load=${mod.key}`}
                  title="Load this build into the workbench and send it requests of your own"
                >
                  <Icon name="playground" size={14} /> Open in the workbench
                </Link>
              </div>
              <ExerciseCard index={1} exercise={mod.final_build} challenge onSolved={handleSolved} />
            </UnitPart>
          </div>
        )}

        {mod.acceptance.length > 0 && (
          <UnitPart
            title="Acceptance checklist"
            icon="checklist"
            lead={
              <>
                Run through these against <em>your own</em> file before moving on.
              </>
            }
          >
            <UnitList items={mod.acceptance} />
          </UnitPart>
        )}

        {mod.manual_test && (
          <Section title="Try it yourself" open={sec.isOpen("manual")} onToggle={() => sec.toggle("manual")} meta={<Badge icon="terminal">curl</Badge>}>
            <Markdown>{mod.manual_test}</Markdown>
          </Section>
        )}

        {mod.reference && prev?.reference && (
          <Section
            title={`What changed since module ${prev.number}`}
            outline="What changed"
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
            title="Take it further"
            open={sec.isOpen("stretch")}
            onToggle={() => sec.toggle("stretch")}
            meta={<Badge>{mod.stretch.length} ideas</Badge>}
          >
            <UnitList items={mod.stretch} />
          </Section>
        )}

        {mod.self_check.length > 0 && (
          <UnitPart title="Self-check" icon="checklist" lead="Before you move on, make sure you can honestly say yes to each of these:">
            <UnitList items={mod.self_check} />
          </UnitPart>
        )}

        {mod.review.length > 0 && (
          <UnitPart
            title="End-of-module review"
            outline="Review"
            icon="refresh"
            lead="A quick mixed quiz — some of these reach back to earlier modules."
          >
            <QuizSection questions={mod.review} />
          </UnitPart>
        )}

        {mod.glossary.length > 0 && (
          <Section
            title="Glossary"
            open={sec.isOpen("glossary")}
            onToggle={() => sec.toggle("glossary")}
            meta={<Badge>{mod.glossary.length} terms</Badge>}
          >
            <Glossary terms={mod.glossary} />
          </Section>
        )}

        {mod.cheatsheet && (
          <Section title="Cheat sheet" open={sec.isOpen("cheatsheet")} onToggle={() => sec.toggle("cheatsheet")}>
            <Markdown>{mod.cheatsheet}</Markdown>
          </Section>
        )}

        {mod.milestone && <Milestone text={mod.milestone} />}

        {harnessNote && (
          <Section title="How the exercises are judged" open={sec.isOpen("harness")} onToggle={() => sec.toggle("harness")}>
            <Markdown>{harnessNote}</Markdown>
          </Section>
        )}

        <div className="concept-end">
          <ReadStatus steps={checklist} complete={isDone} compact />
        </div>

        <UnitPager
          base={`/projects/${project.key}`}
          unitLabel="Module"
          prev={prev ? { slug: prev.key, number: prev.number, title: prev.title } : null}
          next={next ? { slug: next.key, number: next.number, title: next.title } : null}
          backTo={`/projects/${project.key}`}
          backLabel="The roadmap"
        />

        {/* Sentinel: intersecting means the module has been read to the bottom. */}
        <div ref={bottomRef} className="read-sentinel" />
      </ReaderLayout>

      <ConfirmDialog
        open={confirmReset}
        onClose={() => setConfirmReset(false)}
        onConfirm={resetModule}
        title={`Start module ${mod.number} over?`}
        consequence={
          <>
            This clears {plural(solvedCount, "solved exercise")} and this module's ✓ Done mark, so it can be worked again
            from scratch. <strong>The code you have written is kept.</strong>
          </>
        }
        confirmLabel="Start over"
      />
    </div>
  );
}

function ChangeBadge({ before, after }: { before: string; after: string }) {
  const s = useMemo(() => diffStats(diffSources(before, after, { codeOnly: true })), [before, after]);
  return <DiffStatBadge added={s.added} removed={s.removed} />;
}

/** This module's reference against the previous module's: the module, stated
 * as the edit it makes. Mounted only while its section is open. */
function ModuleChanges({ project, prev, mod }: { project: Project; prev: ProjectModule; mod: ProjectModule }) {
  const [codeOnly, setCodeOnly] = useState(true);
  return (
    <div>
      <div className="module-changes-bar">
        <span className="section-lead module-changes-lead">
          Module {prev.number}'s finished file, edited into module {mod.number}'s. If this module adds exactly one
          capability, it should be visible here as one thing.
        </span>
        <span className="module-changes-toggle">
          <Toggle checked={codeOnly} onChange={setCodeOnly} label="Code only" />
          <span aria-hidden>Code only</span>
        </span>
        <Link className="btn ghost btn-sm" to={`/projects/${project.key}/history?to=${mod.key}`}>
          Build history <Icon name="forward" size={14} />
        </Link>
      </div>
      <DiffView before={prev.reference} after={mod.reference} codeOnly={codeOnly} maxHeight={560} />
    </div>
  );
}

// This track's own wording for the shared exercise sections: a challenge is
// not a puzzle, it is the next piece of the application.
const STEP_SECTION_WORDING = {
  fix: { blurb: "This program is wrong. Find the mistake and fix it so the tests pass." },
  challenge: { heading: "Build it" },
};

function StepBody({ step, onSolved }: { step: BackendStep; onSolved: (id: string) => void }) {
  const exercises = step.exercises ?? [];
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
              <li key={i}>
                <InlineMarkdown>{p}</InlineMarkdown>
              </li>
            ))}
          </ul>
        </VerdictPanel>
      )}

      {warmup.length > 0 && (
        <>
          <SubHeading icon="sparkles">Work it out first</SubHeading>
          <p className="section-lead">Answer before you read on.</p>
          <QuizSection questions={warmup} />
        </>
      )}

      <ExerciseSections exercises={exercises} onSolved={onSolved} overrides={STEP_SECTION_WORDING} />

      {quiz.length > 0 && (
        <>
          <SubHeading icon="help">Check yourself</SubHeading>
          <QuizSection questions={quiz} />
        </>
      )}
    </div>
  );
}
