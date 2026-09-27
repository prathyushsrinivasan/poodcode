// The capstone week's interview practice (TS_MASTERY_ROADMAP week 27): the
// conceptual interview bank, three timed mock interviews, and code-review
// exercises. None of it gates anything — the capstone week is optional.
//
// State that should survive a restart (a mock's attempts and self-scores, a
// review's draft and which model comments it caught) lives in the settings
// table as JSON, so it is in backups like everything else.

import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import type {
  Exercise,
  MasteryCodeReview,
  MasteryInterviewQ,
  MasteryMockSession,
  MasteryWeek,
} from "../types";
import { Markdown } from "./Markdown";
import { ExerciseSections } from "./ExerciseSections";
import { inlineCode } from "./common";
import { markMasterySolved } from "../lib/learnProgress";
import {
  mockAttemptSummary,
  parseMockState,
  parseReviewState,
  type MockState,
  type ReviewState,
} from "../lib/capstone";
import { saveFailed } from "../lib/failures";
import { Icon } from "./ui/Icon";

const mockKey = (track: string, week: number, i: number) => `mastery-mock:${track}:${week}:${i}`;
const reviewKey = (track: string, id: string) => `mastery-review:${track}:${id}`;

export function CapstonePractice({ week, trackKey }: { week: MasteryWeek; trackKey: string }) {
  const bank = week.interview_bank ?? [];
  const mocks = week.mock_sessions ?? [];
  const reviews = week.code_reviews ?? [];
  const [settings, setSettings] = useState<Record<string, string> | null>(null);

  useEffect(() => {
    api.getSettings().then(setSettings).catch(() => setSettings({}));
  }, []);

  const save = (key: string, value: unknown) => {
    const raw = JSON.stringify(value);
    setSettings((s) => ({ ...(s ?? {}), [key]: raw }));
    api.setSetting(key, raw).catch(saveFailed("your capstone progress"));
  };

  if (bank.length + mocks.length + reviews.length === 0) return null;
  if (settings === null) return null;

  return (
    <>
      {mocks.length > 0 && (
        <details className="card mastery-practice" open>
          <summary>
            <strong>🎙 Mock interviews</strong>{" "}
            <span className="dim quiz-note">
              {mocks.length} timed sessions · idiom questions, a problem and a type puzzle ·
              self-scored
            </span>
          </summary>
          {mocks.map((m, i) => (
            <MockSessionCard
              key={i}
              session={m}
              bank={bank}
              problemSet={week.problem_set ?? []}
              state={parseMockState(settings[mockKey(trackKey, week.week, i)])}
              onChange={(st) => save(mockKey(trackKey, week.week, i), st)}
            />
          ))}
        </details>
      )}

      {bank.length > 0 && <InterviewBank bank={bank} />}

      {reviews.length > 0 && (
        <details className="card mastery-practice">
          <summary>
            <strong>🔍 Code review</strong>{" "}
            <span className="dim quiz-note">
              {reviews.filter((r) => parseReviewState(settings[reviewKey(trackKey, r.id)]).compared).length}/
              {reviews.length} reviewed · write the comments, then compare with the model review
            </span>
          </summary>
          <p className="dim quiz-note">
            Each snippet compiles and runs — and has problems a reviewer should catch. Write your review
            comments first; then open the model review, tick the points you caught, and read the
            corrected version. What each version prints was produced by running it.
          </p>
          {reviews.map((r) => (
            <CodeReviewCard
              key={r.id}
              review={r}
              state={parseReviewState(settings[reviewKey(trackKey, r.id)])}
              onChange={(st) => save(reviewKey(trackKey, r.id), st)}
            />
          ))}
        </details>
      )}
    </>
  );
}

function InterviewBank({ bank }: { bank: MasteryInterviewQ[] }) {
  const topics = useMemo(() => [...new Set(bank.map((q) => q.topic))], [bank]);
  const [topic, setTopic] = useState<string>("");
  const [open, setOpen] = useState<Set<number>>(new Set());
  const [drill, setDrill] = useState<number | null>(null);
  const [drillShown, setDrillShown] = useState(false);

  const toggle = (i: number) =>
    setOpen((s) => {
      const n = new Set(s);
      if (n.has(i)) n.delete(i);
      else n.add(i);
      return n;
    });

  function randomQuestion() {
    const pool = bank.map((_, i) => i).filter((i) => !topic || bank[i].topic === topic);
    if (pool.length === 0) return;
    let next = pool[Math.floor(Math.random() * pool.length)];
    if (pool.length > 1 && next === drill) next = pool[(pool.indexOf(next) + 1) % pool.length];
    setDrill(next);
    setDrillShown(false);
  }

  return (
    <details className="card mastery-practice">
      <summary>
        <strong>🎤 Interview question bank</strong>{" "}
        <span className="dim quiz-note">
          {bank.length} questions across {topics.length} topics, each with a model answer
        </span>
      </summary>
      <p className="dim quiz-note">
        Answer out loud first — in a real interview nobody hands you the options. Then compare with the
        model answer: did you say the one sentence that matters, and could you give an example?
      </p>
      <div className="row gap-1 flex-wrap mb-2">
        <button className={topic === "" ? "" : "ghost"} onClick={() => setTopic("")}>
          All
        </button>
        {topics.map((t) => (
          <button key={t} className={topic === t ? "" : "ghost"} onClick={() => setTopic(t)}>
            {t}
          </button>
        ))}
        <span className="spacer" />
        <button className="ghost" onClick={randomQuestion}>
          🎲 Ask me one
        </button>
      </div>

      {drill !== null && (
        <div className="card border-accent">
          <div className="io-label c-accent">
            {bank[drill].topic}
          </div>
          <strong>{inlineCode(bank[drill].question)}</strong>
          <div className="row gap-2 mt-2">
            <button className="ghost" onClick={() => setDrillShown((s) => !s)}>
              {drillShown ? "Hide the model answer" : "I've answered — show the model answer"}
            </button>
            <button className="ghost" onClick={randomQuestion}>
              Next question
            </button>
          </div>
          {drillShown && (
            <div className="mt-2">
              <Markdown>{bank[drill].answer}</Markdown>
            </div>
          )}
        </div>
      )}

      {bank.map((q, i) =>
        topic && q.topic !== topic ? null : (
          <div key={i} className="card mb-2">
            <button type="button" className="disclosure-row" aria-expanded={open.has(i)} onClick={() => toggle(i)}>
              <Icon name="chevronRight" size={14} className={`caret ${open.has(i) ? "open" : ""}`} />
              <span className="disclosure-row-text">{inlineCode(q.question)}</span>
              {!topic && <span className="badge">{q.topic}</span>}
            </button>
            {open.has(i) && (
              <div className="mt-2">
                <Markdown>{q.answer}</Markdown>
              </div>
            )}
          </div>
        )
      )}
    </details>
  );
}

function formatClock(seconds: number): string {
  const s = Math.max(0, Math.round(seconds));
  const m = Math.floor(s / 60);
  return `${m}:${String(s % 60).padStart(2, "0")}`;
}

function MockSessionCard({
  session,
  bank,
  problemSet,
  state,
  onChange,
}: {
  session: MasteryMockSession;
  bank: MasteryInterviewQ[];
  problemSet: Exercise[];
  state: MockState;
  onChange: (next: MockState) => void;
}) {
  const [now, setNow] = useState(() => Date.now());
  const [shown, setShown] = useState<Set<number>>(new Set());
  const [scores, setScores] = useState<number[]>(() => session.rubric.map(() => 0));
  const running = state.startedAt !== null;
  const problem = problemSet.find((e) => e.id === session.problem);
  const puzzle = problemSet.find((e) => e.id === session.puzzle);

  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [running]);

  const elapsed = running ? (now - Date.parse(state.startedAt!)) / 1000 : 0;
  const left = session.minutes * 60 - elapsed;
  const summary = mockAttemptSummary(state.attempts, session.rubric.length);

  function start() {
    setShown(new Set());
    setScores(session.rubric.map(() => 0));
    setNow(Date.now());
    onChange({ ...state, startedAt: new Date().toISOString() });
  }

  function finish() {
    onChange({
      startedAt: null,
      attempts: [
        ...state.attempts,
        { date: new Date().toISOString(), seconds: Math.round(elapsed), scores },
      ],
    });
  }

  return (
    <div className="card" style={{ borderColor: running ? "var(--accent)" : undefined }}>
      <div className="row items-center gap-2 flex-wrap">
        <strong>{session.title}</strong>
        <span className="badge">{session.minutes} min</span>
        {summary && (
          <span className="dim quiz-note">
            {summary.count} attempt{summary.count === 1 ? "" : "s"} · best {summary.best}/
            {summary.max} · last {summary.last}/{summary.max}
          </span>
        )}
        <span className="spacer" />
        {running ? (
          <span
            className="badge"
            style={{ fontFamily: "var(--font-mono)", color: left < 0 ? "var(--bad)" : undefined }}
            title="Time left in the session"
          >
            {left >= 0 ? `⏱ ${formatClock(left)} left` : `⏱ ${formatClock(-left)} over`}
          </span>
        ) : (
          <button onClick={start}>Start the clock</button>
        )}
      </div>
      <p className="dim quiz-note" style={{ margin: "6px 0 0" }}>
        {session.brief}
      </p>

      {running && (
        <div className="mt-2">
          <div className="io-label">1 · Idiom questions — answer out loud, then compare</div>
          {session.questions.map((qi) => {
            const q = bank[qi];
            if (!q) return null;
            return (
              <div key={qi} className="card mb-2">
                <strong>{inlineCode(q.question)}</strong>
                <div>
                  <button
                    className="ghost"
                    style={{ marginTop: 6, fontSize: 12, padding: "2px 10px" }}
                    onClick={() =>
                      setShown((s) => {
                        const n = new Set(s);
                        if (n.has(qi)) n.delete(qi);
                        else n.add(qi);
                        return n;
                      })
                    }
                  >
                    {shown.has(qi) ? "Hide model answer" : "Show model answer"}
                  </button>
                </div>
                {shown.has(qi) && (
                  <div className="mt-1">
                    <Markdown>{q.answer}</Markdown>
                  </div>
                )}
              </div>
            );
          })}

          <div className="io-label">2 · The problem, then 3 · the type puzzle</div>
          <ExerciseSections
            exercises={[problem, puzzle].filter((e): e is Exercise => !!e)}
            onSolved={(id) => markMasterySolved(id)}
          />

          <div className="io-label mt-2">
            4 · Score yourself — 1 (not yet) to 4 (interview-ready)
          </div>
          {session.rubric.map((item, ri) => (
            <div key={ri} className="row" style={{ gap: 8, alignItems: "center", margin: "4px 0" }}>
              <span className="flex-1 text-sm">{inlineCode(item)}</span>
              {[1, 2, 3, 4].map((v) => (
                <button
                  key={v}
                  className={scores[ri] === v ? "" : "ghost"}
                  style={{ padding: "2px 10px" }}
                  onClick={() => setScores((s) => s.map((x, k) => (k === ri ? v : x)))}
                >
                  {v}
                </button>
              ))}
            </div>
          ))}
          <div className="row gap-2 mt-2">
            <button onClick={finish} disabled={scores.some((s) => s === 0)}>
              Finish and record the attempt
            </button>
            <button className="ghost" onClick={() => onChange({ ...state, startedAt: null })}>
              Abandon
            </button>
            {scores.some((s) => s === 0) && (
              <span className="dim quiz-note">Score every rubric line to finish.</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function CodeReviewCard({
  review,
  state,
  onChange,
}: {
  review: MasteryCodeReview;
  state: ReviewState;
  onChange: (next: ReviewState) => void;
}) {
  const [text, setText] = useState(state.text);
  const caught = new Set(state.caught);

  return (
    <div className="card" style={{ borderColor: state.compared ? "var(--good)" : undefined }}>
      <div className="row gap-2 items-baseline">
        <strong>
          {state.compared && <span className="c-good">✓ </span>}
          {review.title}
        </strong>
        {state.compared && (
          <span className="dim quiz-note">
            caught {caught.size}/{review.comments.length}
          </span>
        )}
      </div>
      <p className="dim quiz-note" style={{ margin: "4px 0 6px" }}>
        {review.context}
      </p>
      <Markdown>{"```ts\n" + review.code + "```"}</Markdown>
      <div className="io-label">It prints</div>
      <pre className="code-output" style={{ margin: "0 0 8px" }}>
        {review.runs || "(nothing)"}
      </pre>
      <div className="io-label">Your review comments</div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onBlur={() => text !== state.text && onChange({ ...state, text })}
        placeholder="One comment per problem: what is wrong, why it matters, what to do instead."
        style={{ width: "100%", minHeight: 80 }}
      />
      {!state.compared ? (
        <button className="mt-2"
          disabled={text.trim().length === 0}
          onClick={() => onChange({ ...state, text, compared: true })}
          title={text.trim() ? undefined : "Write your review first."}
        >
          Compare with the model review
        </button>
      ) : (
        <>
          <div className="io-label mt-2">
            The model review — tick what you caught
          </div>
          {review.comments.map((c, i) => (
            <label
              key={i}
              style={{ display: "flex", gap: 8, alignItems: "baseline", fontSize: 13, margin: "4px 0" }}
            >
              <input
                type="checkbox"
                checked={caught.has(i)}
                onChange={() => {
                  const n = new Set(caught);
                  if (n.has(i)) n.delete(i);
                  else n.add(i);
                  onChange({ ...state, text, caught: [...n].sort((a, b) => a - b) });
                }}
              />
              <span>{inlineCode(c)}</span>
            </label>
          ))}
          <div className="io-label mt-2">
            After the review
          </div>
          <Markdown>{"```ts\n" + review.fixed + "```"}</Markdown>
          <div className="io-label">It prints</div>
          <pre className="code-output m-0">
            {review.fixed_runs || "(nothing)"}
          </pre>
        </>
      )}
    </div>
  );
}
