// The programme's final exam (TS_MASTERY_ROADMAP X-36) and the completion
// summary it feeds (X-68). The exam opens once every core week is complete:
// one timed sitting of questions drawn from every week's bank, judged problems
// and type puzzles. Its state lives in the settings table (lib/finalExam.ts).

import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { api } from "../api";
import type { MasteryFinalExam, MasteryTrack, MasteryWeek } from "../types";
import { ExerciseSections } from "./ExerciseSections";
import { inlineCode } from "./common";
import { QuizChoices } from "./QuizChoices";
import { QuizCard } from "./exercise/Quiz";
import { H } from "./ui/Heading";
import { markMasterySolved } from "../lib/learnProgress";
import { formatStudyTime, type WeekProgress } from "../lib/mastery";
import {
  drawFinalPaper,
  finalExamKey,
  headlineAttempt,
  parseFinalExamState,
  scoreSitting,
  type FinalAttempt,
  type FinalExamState,
} from "../lib/finalExam";
import { useToast } from "./Toast";
import { saveFailed } from "../lib/failures";
import { Icon } from "./ui";

function clock(seconds: number): string {
  const s = Math.max(0, Math.round(seconds));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  return `${h}:${String(m).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
}

/** Loads and saves the exam state; shared by the panel and the summary. */
export function useFinalExamState(trackKey: string) {
  const [state, setState] = useState<FinalExamState | null>(null);
  useEffect(() => {
    if (!trackKey) return;
    let live = true;
    api
      .getSettings()
      .then((s) => live && setState(parseFinalExamState(s[finalExamKey(trackKey)])))
      .catch(() => live && setState({ sitting: null, attempts: [] }));
    return () => {
      live = false;
    };
  }, [trackKey]);
  const save = (next: FinalExamState) => {
    setState(next);
    api.setSetting(finalExamKey(trackKey), JSON.stringify(next)).catch(saveFailed("your final-exam answers"));
  };
  return [state, save] as const;
}

export function FinalExamPanel({
  exam,
  weeks,
  finished,
  remaining,
  state,
  onChange,
}: {
  exam: MasteryFinalExam;
  /** The core weeks whose banks the paper draws on. */
  weeks: MasteryWeek[];
  finished: boolean;
  remaining: number;
  state: FinalExamState;
  onChange: (next: FinalExamState) => void;
}) {
  const toast = useToast();
  const sitting = state.sitting;
  const [now, setNow] = useState(() => Date.now());
  const [result, setResult] = useState<FinalAttempt | null>(null);
  const paper = useMemo(
    () => (sitting ? drawFinalPaper(weeks, exam.quiz_size, sitting.seed) : []),
    [sitting, weeks, exam.quiz_size]
  );

  useEffect(() => {
    if (!sitting) return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [sitting]);

  if (!finished) {
    return (
      <div className="card week-card locked mb-4">
        <div className="row items-center gap-2">
          <span className="week-num">
          <Icon name="locked" size={14} label="Locked" />
        </span>
          <div>
            <strong className="dim">{exam.title}</strong>
            <p className="dim" style={{ margin: "4px 0 0", fontSize: 13 }}>
              Opens when every core week is complete — {remaining} to go. Three hours: {exam.quiz_size}{" "}
              questions from all {weeks.length} weeks, {exam.problems.length} problems and{" "}
              {exam.type_section.length} type puzzles.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const passedBefore = state.attempts.some((a) => a.passed);
  const headline = headlineAttempt(state.attempts);

  function start() {
    setResult(null);
    const seed = (Date.now() ^ Math.floor(Math.random() * 0x7fffffff)) >>> 0;
    const draft = { seed, startedAt: new Date().toISOString(), picked: [] as number[], solved: [] as string[] };
    draft.picked = drawFinalPaper(weeks, exam.quiz_size, seed).map(() => -1);
    onChange({ ...state, sitting: draft });
  }

  function pick(i: number, option: number) {
    if (!sitting) return;
    const picked = [...sitting.picked];
    picked[i] = option;
    onChange({ ...state, sitting: { ...sitting, picked } });
  }

  function solved(id: string) {
    markMasterySolved(id);
    if (!sitting || sitting.solved.includes(id)) return;
    onChange({ ...state, sitting: { ...sitting, solved: [...sitting.solved, id] } });
  }

  function submit() {
    if (!sitting) return;
    const score = scoreSitting(exam, paper, sitting);
    const attempt: FinalAttempt = {
      date: new Date().toISOString(),
      seconds: Math.round((Date.now() - Date.parse(sitting.startedAt)) / 1000),
      ...score,
    };
    setResult(attempt);
    onChange({ sitting: null, attempts: [...state.attempts, attempt] });
    if (attempt.passed) toast.success("Final exam passed 🎉");
    else toast("Final exam recorded — not a pass yet");
  }

  function abandon() {
    onChange({ ...state, sitting: null });
  }

  if (!sitting) {
    return (
      <div className="card" style={{ marginBottom: 18, borderColor: passedBefore ? "var(--good)" : "var(--accent)" }}>
        <div className="io-label" style={{ color: passedBefore ? "var(--good)" : "var(--accent)" }}>
          <Icon name="mastery" size={15} /> {exam.title} {passedBefore && "— passed"}
        </div>
        <p className="mt-0">{inlineCode(exam.intro)}</p>
        {result && <AttemptLine attempt={result} exam={exam} label="This sitting" />}
        {headline && !result && <AttemptLine attempt={headline} exam={exam} label={passedBefore ? "Passed" : "Best so far"} />}
        <div className="row gap-2 items-center mt-2">
          <button onClick={start}>{state.attempts.length > 0 ? "Sit it again" : "Start the final exam"}</button>
          <span className="dim quiz-note">
            {exam.minutes / 60} hours · the clock keeps running if you leave the page · {state.attempts.length}{" "}
            attempt{state.attempts.length === 1 ? "" : "s"} so far
          </span>
        </div>
      </div>
    );
  }

  const elapsed = (now - Date.parse(sitting.startedAt)) / 1000;
  const left = exam.minutes * 60 - elapsed;
  const answered = sitting.picked.filter((p) => p >= 0).length;
  const solvedSet = new Set(sitting.solved);

  return (
    <div className="card mb-4 border-accent">
      <div className="row items-center gap-2 flex-wrap">
        <div className="io-label m-0 c-accent">
          <Icon name="mastery" size={15} /> {exam.title} — in progress
        </div>
        <span className="spacer" />
        <span
          className="badge"
          style={{ fontFamily: "var(--font-mono)", color: left < 0 ? "var(--bad)" : undefined }}
        >
          <Icon name="timer" size={12} /> {left >= 0 ? `${clock(left)} left` : `${clock(-left)} over time`}
        </span>
      </div>

      <H className="unit-subtitle">Part A — {paper.length} questions from across the programme</H>
      <p className="dim quiz-note" style={{ marginTop: -4 }}>
        {answered}/{paper.length} answered · {exam.pass_mark}% to pass this part. Answers are saved as you go.
      </p>
      {paper.map((q, i) => (
        <QuizCard key={i} index={i + 1} question={inlineCode(q.question)} revealed={false} right={false}>
          <QuizChoices question={q} picked={sitting.picked[i] ?? -1} revealed={false} onPick={(v) => pick(i, v)} />
        </QuizCard>
      ))}

      <H className="unit-subtitle">
        Part B — problems ({exam.problems.filter((p) => solvedSet.has(p.id)).length}/{exam.problems.length}{" "}
        accepted this sitting · {exam.min_problems} needed)
      </H>
      <ExerciseSections
        exercises={exam.problems}
        onSolved={solved}
        overrides={{ challenge: { heading: "Problems" } }}
      />

      <H className="unit-subtitle">
        Part C — type puzzles ({exam.type_section.filter((p) => solvedSet.has(p.id)).length}/
        {exam.type_section.length} accepted this sitting · {exam.min_types} needed)
      </H>
      <ExerciseSections exercises={exam.type_section} onSolved={solved} />

      <div className="row gap-2 items-center mt-3">
        <button onClick={submit}>Hand in the exam</button>
        <button className="ghost" onClick={abandon}>
          Abandon this sitting
        </button>
        <span className="dim quiz-note">
          Only problems and puzzles accepted during this sitting count — submit each one here.
        </span>
      </div>
    </div>
  );
}

function AttemptLine({ attempt, exam, label }: { attempt: FinalAttempt; exam: MasteryFinalExam; label: string }) {
  return (
    <p className="dim quiz-note" style={{ margin: "0 0 6px" }}>
      <strong style={{ color: attempt.passed ? "var(--good)" : "var(--bad)" }}>
        {label}: {attempt.passed ? "pass" : "not yet"}
      </strong>{" "}
      — questions {attempt.quizPercent}% (need {exam.pass_mark}%) · problems {attempt.problems}/
      {exam.problems.length} (need {exam.min_problems}) · puzzles {attempt.types}/{exam.type_section.length} (need{" "}
      {exam.min_types}) · {formatStudyTime(attempt.seconds)} · {new Date(attempt.date).toLocaleDateString()}
    </p>
  );
}

// ---------------------------------------------------------------------------
// Completion summary (X-68)
// ---------------------------------------------------------------------------

type PhaseRow = { phase: string; weeks: number; study: number; quizAvg: number; projects: number };

export function ProgrammeSummary({
  track,
  weeks,
  perWeek,
  totalStudy,
  exam,
  attempts,
}: {
  track: MasteryTrack;
  weeks: MasteryWeek[];
  perWeek: WeekProgress[];
  totalStudy: number;
  exam: MasteryFinalExam | null;
  attempts: FinalAttempt[];
}) {
  const [printing, setPrinting] = useState(false);
  const scores = perWeek.map((p) => p.score ?? 0);
  const avg = scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
  const problems = perWeek.reduce((s, p) => s + p.problemsSolved, 0);
  const projects = perWeek.filter((p) => p.projectDone).length;
  const passed = attempts.find((a) => a.passed) ?? null;

  const phases: PhaseRow[] = [];
  weeks.forEach((w, i) => {
    const p = perWeek[i];
    if (!p) return;
    let row = phases.find((r) => r.phase === w.phase);
    if (!row) {
      row = { phase: w.phase, weeks: 0, study: 0, quizAvg: 0, projects: 0 };
      phases.push(row);
    }
    row.weeks++;
    row.study += p.studySeconds;
    row.quizAvg += p.score ?? 0;
    row.projects += p.projectDone ? 1 : 0;
  });
  for (const r of phases) r.quizAvg = Math.round(r.quizAvg / Math.max(1, r.weeks));

  // The weeks to revisit: the lowest best quiz scores, then the most time spent.
  const revisit = weeks
    .map((w, i) => ({ w, p: perWeek[i] }))
    .filter((x): x is { w: MasteryWeek; p: WeekProgress } => !!x.p)
    .sort((a, b) => (a.p.score ?? 0) - (b.p.score ?? 0) || b.p.studySeconds - a.p.studySeconds)
    .slice(0, 3);

  useEffect(() => {
    if (!printing) return;
    document.body.classList.add("printing-certificate");
    const done = () => {
      document.body.classList.remove("printing-certificate");
      setPrinting(false);
    };
    window.addEventListener("afterprint", done);
    const t = setTimeout(() => window.print(), 50);
    return () => {
      clearTimeout(t);
      window.removeEventListener("afterprint", done);
      document.body.classList.remove("printing-certificate");
    };
  }, [printing]);

  const lastCompleted = new Date().toLocaleDateString();

  return (
    <div className="card mb-4 border-good">
      <div className="row items-center">
        <div className="io-label c-good m-0">
          🎉 Programme complete
        </div>
        <span className="spacer" />
        <button className="ghost" onClick={() => setPrinting(true)}>
          <Icon name="document" size={14} /> Print a certificate
        </button>
      </div>
      <p>
        Every week of <strong>{track.title}</strong> is finished — all {perWeek.length} weeks of chapters
        studied, both exams passed each week.{" "}
        {exam &&
          (passed
            ? `The final exam is passed (${passed.quizPercent}% on the questions, ${passed.problems}/${exam.problems.length} problems, ${passed.types}/${exam.type_section.length} puzzles).`
            : "The final exam below is the last step.")}
      </p>
      <div className="grid cols-4">
        <div className="card mb-0">
          <div className="stat-value">{perWeek.length}</div>
          <div className="stat-label">weeks completed</div>
        </div>
        <div className="card mb-0">
          <div className="stat-value">{avg}%</div>
          <div className="stat-label">average best quiz score</div>
        </div>
        <div className="card mb-0">
          <div className="stat-value">{problems}</div>
          <div className="stat-label">curated problems solved</div>
        </div>
        <div className="card mb-0">
          <div className="stat-value">{formatStudyTime(totalStudy)}</div>
          <div className="stat-label">time invested · {projects} projects shipped</div>
        </div>
      </div>

      <div className="io-label mt-3">
        By month
      </div>
      <table className="summary-table">
        <thead>
          <tr>
            <th>Phase</th>
            <th>Weeks</th>
            <th>Best quiz (avg)</th>
            <th>Projects</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {phases.map((r) => (
            <tr key={r.phase}>
              <td>{r.phase}</td>
              <td>{r.weeks}</td>
              <td>{r.quizAvg}%</td>
              <td>
                {r.projects}/{r.weeks}
              </td>
              <td>{formatStudyTime(r.study)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {revisit.length > 0 && (
        <p className="dim quiz-note mb-0">
          Worth a second look:{" "}
          {revisit.map((x, i) => (
            <span key={x.w.week}>
              {i > 0 && " · "}Week {x.w.week} ({x.w.title}, best quiz {x.p.score ?? 0}%)
            </span>
          ))}
        </p>
      )}

      {printing &&
        createPortal(
          <div className="certificate-print">
            <div className="certificate">
              <div className="certificate-kicker">Certificate of completion</div>
              <h1>{track.title}</h1>
              <p>
                {perWeek.length} weeks · {weeks.reduce((n, w) => n + w.concepts.length, 0)} chapters ·{" "}
                {projects} projects shipped · {formatStudyTime(totalStudy)} of study
              </p>
              {exam && passed && (
                <p>
                  Final exam passed on {new Date(passed.date).toLocaleDateString()} — {passed.quizPercent}% on{" "}
                  {exam.quiz_size} questions, {passed.problems}/{exam.problems.length} problems,{" "}
                  {passed.types}/{exam.type_section.length} type puzzles.
                </p>
              )}
              <table className="summary-table">
                <tbody>
                  {phases.map((r) => (
                    <tr key={r.phase}>
                      <td>{r.phase}</td>
                      <td>{r.quizAvg}% best quiz average</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="certificate-date">Printed {lastCompleted} · Poodcode</p>
            </div>
          </div>,
          document.body
        )}
    </div>
  );
}
