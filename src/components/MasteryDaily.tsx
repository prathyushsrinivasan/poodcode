// Small cards on the Mastery page: the daily type puzzle (M5-02) and the
// Week 0 guide for a newcomer (M1-01).

import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import type { Exercise, MasteryTrack } from "../types";
import { ExerciseSections } from "./ExerciseSections";
import { loadSolvedExercises, markMasterySolved, solvedExercises } from "../lib/learnProgress";
import { dailyKey, localDay, parseDaily, streak, todaysPuzzle, typeLadder } from "../lib/typeLadder";

export function DailyTypePuzzle({
  track,
  reachedWeek,
  settings,
  saveSetting,
}: {
  track: MasteryTrack;
  /** The furthest week unlocked; puzzles come from weeks up to it. */
  reachedWeek: number;
  settings: Record<string, string>;
  saveSetting: (key: string, value: string) => void;
}) {
  const ladder = useMemo(() => typeLadder(track.weeks), [track.weeks]);
  const [solved, setSolved] = useState<Set<string>>(() => solvedExercises());
  const today = localDay();
  const key = dailyKey(track.key);
  const state = parseDaily(settings[key]);
  const rung = todaysPuzzle(ladder, reachedWeek, solved, state, today);
  const done = state.days.includes(today);
  const run = streak(state.days, today);

  useEffect(() => {
    loadSolvedExercises().then(setSolved).catch(() => {});
  }, []);

  // Pin today's pick so a reload serves the same puzzle.
  useEffect(() => {
    if (rung && state.pick?.day !== today) {
      saveSetting(key, JSON.stringify({ ...state, pick: { day: today, id: rung.exercise.id } }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rung?.exercise.id, today]);

  if (!rung) return null;

  const onSolved = (id: string) => {
    setSolved(new Set(markMasterySolved(id)));
    if (id !== rung.exercise.id || done) return;
    saveSetting(key, JSON.stringify({ pick: { day: today, id }, days: [...state.days, today] }));
  };

  const index = ladder.findIndex((r) => r.exercise.id === rung.exercise.id);
  return (
    <details className="card mastery-practice" style={{ marginBottom: 18 }} open={!done}>
      <summary>
        <strong>🧬 Today&rsquo;s type puzzle</strong>{" "}
        <span className="dim quiz-note">
          {done ? "✓ done today" : "one a day"} · rung {index + 1} of {ladder.length}, from week {rung.week}
          {run > 0 && ` · 🔥 ${run}-day streak`}
        </span>
      </summary>
      <p className="dim quiz-note">
        Every type-graded exercise in the programme, easiest first — one a day from the weeks you have
        reached. Small and daily beats long and rare.
      </p>
      <ExerciseSections exercises={[rung.exercise]} onSolved={onSolved} />
    </details>
  );
}

const W0_KEY = (track: string) => `mastery-week0-dismissed:${track}`;

export function WeekZero({
  track,
  exercise,
  settings,
  saveSetting,
  onOpenWeek,
}: {
  track: MasteryTrack;
  exercise: Exercise | null;
  settings: Record<string, string>;
  saveSetting: (key: string, value: string) => void;
  onOpenWeek: (week: number) => void;
}) {
  if (settings[W0_KEY(track.key)] === "1") return null;
  return (
    <details className="card mastery-practice mastery-today" style={{ marginBottom: 18 }} open>
      <summary>
        <strong>👋 Week 0 — how this programme works</strong>{" "}
        <span className="dim quiz-note">thirty minutes, before Week 1 · not part of any gate</span>
      </summary>
      <ol className="week0-steps">
        <li>
          <strong>Programs read stdin and print stdout.</strong> A test gives your program some input and
          compares what it prints with the expected output — line by line, ignoring trailing spaces. The
          scaffold already reads the input: <code>const input = fs.readFileSync(0, &quot;utf8&quot;).trim();</code>
        </li>
        <li>
          <strong>Run as often as you like.</strong> <kbd>Ctrl</kbd>+<kbd>Enter</kbd> judges your code. When a test
          fails you see its input line by line, the expected output beside yours, and a caret under the first
          character that differs.
        </li>
        <li>
          <strong>Hover to see types.</strong> The editor knows exactly what the judge knows: hover a name to see the
          type TypeScript inferred, and red squiggles are real errors. The{" "}
          <Link to="/playground/ts">playground</Link> shows every type at once.
        </li>
        <li>
          <strong>Each week has a gate:</strong> mark its chapters done, pass the quiz at {track.pass_mark}%, and get
          the coding final accepted. Practice, problem sets and the project are optional — and where most of the
          learning happens.
        </li>
        <li>
          <strong>Pace yourself.</strong> Start the programme to get a schedule and a daily plan; pause it for a
          holiday. Finished weeks feed review cards into <Link to="/flashcards">Flashcards</Link>.
        </li>
      </ol>
      {exercise && (
        <>
          <p className="quiz-note" style={{ marginBottom: 0 }}>
            Try it once, now: a first program, judged exactly like every exercise to come.
          </p>
          <ExerciseSections exercises={[exercise]} onSolved={(id) => markMasterySolved(id)} />
        </>
      )}
      <div className="row" style={{ gap: 8, marginTop: 8 }}>
        <button onClick={() => onOpenWeek(1)}>Go to Week 1</button>
        <button className="ghost" onClick={() => saveSetting(W0_KEY(track.key), "1")}>
          Hide this guide
        </button>
      </div>
    </details>
  );
}
