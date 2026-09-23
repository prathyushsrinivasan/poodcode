import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { Contest as ContestT } from "../types";
import { DiffBadge, Empty } from "../components/common";
import { formatClock } from "../lib/format";
import { contestScore, secondsLeft } from "../lib/contest";
import { useToast } from "../components/Toast";

/**
 * A timed checkpoint — the scoreboard for one contest.
 *
 * The Mastery programme has always seeded checkpoint contests (and the backend
 * has always scored them), but the page that ran them was removed in the UI
 * overhaul, so "Start the checkpoint" had nowhere to go. This is that page, cut
 * down to what a checkpoint needs: a clock, the problems, and the score.
 *
 * The clock runs from the contest's stored start time, not from when this page
 * was opened, so leaving to solve a problem and coming back doesn't reset it.
 * Submissions made from a problem opened here (`/solve/:id?contest=:cid`) are
 * recorded against the contest by the Solve page.
 */
export default function Contest() {
  const { id } = useParams();
  const cid = Number(id);
  const [contest, setContest] = useState<ContestT | null>(null);
  const [error, setError] = useState("");
  const [now, setNow] = useState(Date.now());
  const toast = useToast();
  const nav = useNavigate();

  const load = useCallback(() => {
    api
      .contest(cid)
      .then(setContest)
      .catch((e) => setError(String(e)));
  }, [cid]);
  useEffect(load, [load]);

  const running = contest?.status === "running";
  const left = contest ? secondsLeft(contest, now) : 0;

  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [running]);

  const finish = useCallback(async () => {
    try {
      await api.finishContest(cid);
      load();
    } catch (e) {
      toast(`Could not finish the checkpoint: ${e}`);
    }
  }, [cid, load, toast]);

  // Time's up: close it, exactly as pressing Finish would.
  useEffect(() => {
    if (running && left <= 0) void finish();
  }, [running, left, finish]);

  if (error) {
    return (
      <div className="page">
        <Empty icon="⏱" text={`This checkpoint could not be loaded. ${error}`} />
      </div>
    );
  }
  if (!contest) return <div className="page" />;

  const score = contestScore(contest);
  return (
    <div className="page">
      <div className="row">
        <h1 className="page-title">{contest.title}</h1>
        <span className="spacer" />
        {running ? (
          <span className={`contest-clock${left < 300 ? " warn" : ""}`} aria-live="polite">
            ⏱ {formatClock(left)}
          </span>
        ) : (
          <span className="badge contest-final">
            {score.solved}/{score.total} solved
          </span>
        )}
      </div>
      <p className="page-sub">
        {running
          ? "Solve as many as you can before the clock runs out. Open a problem, submit it there, and come back — the score updates on every submission."
          : `Finished. ${score.solved} of ${score.total} solved, ${score.wrongTries} wrong ${score.wrongTries === 1 ? "submission" : "submissions"}.`}
      </p>

      <div className="card contest-table">
        {contest.results.map((r) => (
          <div key={r.problem_id} className="row contest-row">
            <span aria-label={r.solved ? "solved" : "not solved"}>{r.solved ? "✅" : "⬜"}</span>
            <strong>{r.title}</strong>
            <DiffBadge d={r.difficulty} />
            <span className="spacer" />
            {r.wrong_tries > 0 && (
              <span className="dim">
                {r.wrong_tries} wrong
              </span>
            )}
            {running && (
              <button
                className={r.solved ? "ghost" : ""}
                onClick={() => nav(`/solve/${r.problem_id}?contest=${contest.id}`)}
              >
                {r.solved ? "Open" : "Solve →"}
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="row">
        {running ? (
          <button className="ghost" onClick={finish}>
            Finish now
          </button>
        ) : (
          <Link to="/mastery">Back to the programme</Link>
        )}
      </div>
    </div>
  );
}
