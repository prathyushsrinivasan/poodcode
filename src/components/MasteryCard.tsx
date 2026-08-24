import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { MasteryTrack } from "../types";
import { loadDoneChapters } from "../lib/learnProgress";
import { pacing, progressByWeek, startDateKey, unlockedWeeks, weekProgress } from "../lib/mastery";

/** Dashboard summary of whichever mastery track is furthest along: where you
 * are, what is still outstanding this week, and whether you are behind pace.
 *
 * Renders nothing until a track has actually been started, so the dashboard
 * stays quiet for anyone not following the programme. */
export function MasteryCard() {
  const [state, setState] = useState<{
    track: MasteryTrack;
    week: number;
    outstanding: string[];
    percent: number;
    behind: number | null;
  } | null>(null);
  const nav = useNavigate();

  useEffect(() => {
    (async () => {
      const [tracks, problems, rows, done, settings] = await Promise.all([
        api.mastery(),
        api.listProblems(),
        api.masteryProgress(),
        loadDoneChapters(),
        api.getSettings(),
      ]);
      const solved = new Set(
        problems.filter((p) => p.solved_status === "solved").map((p) => p.slug)
      );

      // Only tracks the learner has explicitly started are worth surfacing.
      const started = tracks.filter((t) => settings[startDateKey(t.key)]);
      if (started.length === 0) return;

      const summaries = started.map((track) => {
        const progress = progressByWeek(rows, track.key);
        const per = track.weeks.map((w) =>
          weekProgress(w, track, done, solved, progress)
        );
        const unlocked = unlockedWeeks(track, done, solved, progress);
        const current =
          track.weeks.find((w) => unlocked.has(w.week) && !per[w.week - 1].complete)?.week ??
          track.weeks.length;
        return { track, progress, per, current, completed: per.filter((p) => p.complete).length };
      });
      // Show whichever programme is furthest along.
      summaries.sort((a, b) => b.completed - a.completed);
      const best = summaries[0];
      const week = best.track.weeks[best.current - 1];
      const wp = best.per[best.current - 1];

      const outstanding: string[] = [];
      if (wp.conceptsDone < wp.conceptsTotal) {
        outstanding.push(`${wp.conceptsTotal - wp.conceptsDone} chapters`);
      }
      if (!wp.quizPassed) outstanding.push("the quiz");
      if (week.exam && !wp.examPassed) outstanding.push("the coding final");
      if (wp.problemsSolved < wp.problemsTotal) {
        outstanding.push(`${wp.problemsTotal - wp.problemsSolved} problems (optional)`);
      }

      const startedRaw = settings[startDateKey(best.track.key)];
      const pace = startedRaw
        ? pacing(new Date(startedRaw), best.current, best.track.weeks.length)
        : null;

      setState({
        track: best.track,
        week: best.current,
        outstanding,
        percent: wp.percent,
        behind: pace ? pace.weeksBehind : null,
      });
    })().catch(() => {});
  }, []);

  if (!state) return null;
  const { track, week, outstanding, percent, behind } = state;

  return (
    <div
      className="card"
      style={{ cursor: "pointer", borderColor: "var(--accent)", marginBottom: 18 }}
      onClick={() => nav("/mastery")}
    >
      <div className="row" style={{ justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
        <div style={{ minWidth: 0 }}>
          <strong>
            🎓 {track.title} · Week {week} of {track.weeks.length}
          </strong>
          <p className="dim" style={{ margin: "4px 0 0", fontSize: 13 }}>
            {outstanding.length === 0
              ? "This week is done — the next one is open."
              : `Still to do: ${outstanding.join(", ")}.`}
          </p>
        </div>
        <span className="row" style={{ gap: 6, flexWrap: "wrap", justifyContent: "flex-end" }}>
          {behind !== null && behind > 0 && (
            <span className="badge" style={{ borderColor: "var(--bad)", color: "var(--bad)" }}>
              {behind} week{behind > 1 ? "s" : ""} behind
            </span>
          )}
          {behind !== null && behind <= 0 && (
            <span className="badge" style={{ borderColor: "var(--good)", color: "var(--good)" }}>
              on track
            </span>
          )}
          <span className="badge">Open →</span>
        </span>
      </div>
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{
            width: `${percent}%`,
            background: percent === 100 ? "var(--good)" : "var(--accent)",
          }}
        />
      </div>
    </div>
  );
}
