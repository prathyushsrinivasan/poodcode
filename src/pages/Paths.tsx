/**
 * Topic playlists (UI_ROADMAP A3).
 *
 * These were "Learning Paths" — curated, ordered problem lists — and they
 * predate the DSA Curriculum, which is also problems in a taught order, with
 * lessons, rungs and review. Two things called a path of problems, with no
 * word on how they related, left you guessing which one to follow.
 *
 * They are what they always were, named for it: short playlists for a focused
 * session on one topic. The curriculum is the course. Each playlist now says
 * which curriculum units teach its problems and links to them, so a playlist
 * is a way into the curriculum rather than a rival to it.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { Path, Problem } from "../types";
import { DiffBadge } from "../components/common";
import { useCurriculumData } from "../components/CurriculumData";
import { TrackSkeleton } from "../components/Skeleton";
import { Badge, Card, CardHeader, EmptyState, ErrorState, Icon, PageHeader, ProgressBar } from "../components/ui";
import { loadFailed } from "../lib/failures";

export default function Paths() {
  const [paths, setPaths] = useState<Path[] | null>(null);
  const [error, setError] = useState("");
  const [problems, setProblems] = useState<Problem[]>([]);
  const { data: curriculum } = useCurriculumData();

  const load = useCallback(() => {
    setError("");
    api
      .listPaths()
      .then(setPaths)
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    load();
    api.listProblems().then(setProblems).catch(loadFailed("the problem list"));
  }, [load]);

  const slugById = useMemo(() => new Map(problems.map((p) => [p.id, p.slug])), [problems]);
  const unitOf = (problemId: number) => {
    const slug = slugById.get(problemId);
    return slug ? curriculum?.unitBySlug.get(slug) : undefined;
  };

  if (error) {
    return (
      <div className="page">
        <PageHeader title="Topic playlists" />
        <ErrorState title="The playlists could not be loaded." error={error} onRetry={load} />
      </div>
    );
  }
  if (!paths) return <TrackSkeleton cards={4} />;

  return (
    <div className="page page-wide">
      <PageHeader
        title="Topic playlists"
        subtitle={
          <>
            Short, ordered problem lists for a focused session on one topic. The{" "}
            <Link to="/library">DSA Curriculum</Link> is the course — lessons, rungs and review; each playlist says which
            of its units teach these problems, so you can go there for the idea.
          </>
        }
      />

      {paths.length === 0 && <EmptyState icon="paths" title="No playlists yet." />}

      <ul className="playlist-grid">
        {paths.map((p) => {
          const solved = p.items.filter((i) => i.solved_status === "solved").length;
          // The first unsolved item is the current step.
          const next = p.items.find((i) => i.solved_status !== "solved");
          // The units behind this playlist, in the order the playlist meets them.
          const units = [...new Map(p.items.map((i) => unitOf(i.problem_id)).filter((u) => !!u).map((u) => [u!.key, u!])).values()];
          return (
            <li key={p.id}>
              <Card as="section" className="playlist" labelledBy={`pl-${p.id}`}>
                <CardHeader
                  id={`pl-${p.id}`}
                  level={2}
                  title={p.title}
                  subtitle={p.description}
                  actions={
                    <span className="mono dim cell-small">
                      {solved}/{p.items.length}
                    </span>
                  }
                />
                <ProgressBar value={solved} max={p.items.length} tone={solved === p.items.length ? "good" : "accent"} label={`${p.title} progress`} size="sm" />
                {units.length > 0 && (
                  <p className="playlist-units">
                    <span className="exercise-note">Taught in:</span>
                    {units.map((u) => (
                      <Link key={u.key} to={`/library/unit/${u.key}`} className="badge badge-link">
                        {u.title}
                      </Link>
                    ))}
                  </p>
                )}
                <ol className="playlist-items">
                  {p.items.map((it, idx) => {
                    const done = it.solved_status === "solved";
                    const isNext = next && it.problem_id === next.problem_id;
                    return (
                      <li key={it.problem_id}>
                        <Link to={`/solve/${it.problem_id}`} className={`path-row ${isNext ? "is-next" : ""}`} aria-current={isNext ? "step" : undefined}>
                          <span className="playlist-mark">
                            {done ? <Icon name="done" size={14} label="Solved" className="is-good" /> : isNext ? <Icon name="run" size={13} label="Next" /> : `${idx + 1}.`}
                          </span>
                          <span className={done ? "dim" : ""}>{it.title}</span>
                          <span className="spacer" />
                          <DiffBadge d={it.difficulty} />
                        </Link>
                      </li>
                    );
                  })}
                </ol>
                {next ? (
                  <Link className="btn primary-link" to={`/solve/${next.problem_id}`}>
                    Continue: {next.title} <Icon name="forward" size={14} />
                  </Link>
                ) : (
                  p.items.length > 0 && (
                    <Badge tone="good" icon="done">
                      Playlist complete
                    </Badge>
                  )
                )}
              </Card>
            </li>
          );
        })}
      </ul>
      <p className="faint page-note">
        Looking for what to learn next rather than what to practise?{" "}
        <Link to="/library" className="btn ghost btn-sm">
          Open the curriculum <Icon name="forward" size={13} />
        </Link>
      </p>
    </div>
  );
}
