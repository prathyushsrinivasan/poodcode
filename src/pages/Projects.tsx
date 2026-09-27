/**
 * The Projects track: routing between its pages (UI_ROADMAP G7).
 *
 * This file was 1,880 lines and the heaviest page in the app — 171 inline
 * styles, its own copies of the contract table, the goal card and the step
 * contents, and `ClickableRow` divs where links belonged. The pages live in
 * `pages/projects/` now:
 *
 *   Overview     the track (several projects) and one project's roadmap
 *   ModulePage   one module, on the reader layout
 *   Handbook     every form, term, trap and check, searchable
 *   History      what each module changed, as diffs
 *   Workbench    load a build, edit it, run your own input
 *   Review       mixed questions, misses first
 */

import { useCallback, useEffect, useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import type { ProjectTrack } from "../types";
import { loadDoneChapters, setChapterDone } from "../lib/learnProgress";
import { loadFailed } from "../lib/failures";
import { TrackSkeleton } from "../components/Skeleton";
import { EmptyState, ErrorState } from "../components/ui";
import { ProjectDetail, TrackOverview } from "./projects/Overview";
import ModulePage from "./projects/ModulePage";
import Handbook from "./projects/Handbook";
import ProjectHistory from "./projects/History";
import ProjectReview from "./projects/Review";
import ProjectWorkbench from "./projects/Workbench";
import { moduleKey, type ProjectView } from "./projects/shared";

export type { ProjectView };

export default function Projects({ view }: { view?: ProjectView } = {}) {
  const { project, module: moduleParam } = useParams();
  const [track, setTrack] = useState<ProjectTrack | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [done, setDone] = useState<Set<string>>(new Set());
  // The review page chooses its default scope from what is finished, so it
  // must not render against the empty set that stands in until this loads.
  const [doneLoaded, setDoneLoaded] = useState(false);
  const nav = useNavigate();

  const load = useCallback(() => {
    setLoadError(null);
    api
      .projectsTrack()
      .then(setTrack)
      .catch((e: unknown) => setLoadError(String((e as { message?: string })?.message ?? e) || "unknown error"));
  }, []);

  useEffect(() => {
    load();
    loadDoneChapters()
      .then(setDone)
      .catch(loadFailed("your completed modules"))
      .finally(() => setDoneLoaded(true));
  }, [load]);

  async function setModuleDone(projectKey: string, key: string, value: boolean) {
    setDone(await setChapterDone(done, moduleKey(projectKey, key), value));
  }

  // A failed load used to be indistinguishable from a slow one. The realistic
  // failure is a regenerated seeds/projects.json that no longer deserializes
  // into `ProjectTrack` after a model change, and the message naming the field
  // that broke is the single most useful thing on the screen when it happens.
  if (loadError) {
    return (
      <div className="page">
        <ErrorState title="The Projects track could not be loaded." error={loadError} onRetry={load} />
        <p className="faint page-note">
          This usually means <code>seeds/projects.json</code> and the Rust model have drifted apart — regenerate the
          seed with <code>python tools/gen_seed.py</code>.
        </p>
      </div>
    );
  }

  if (!track) return <TrackSkeleton cards={4} />;
  if (track.projects.length === 0) {
    return (
      <div className="page">
        <EmptyState icon="projects" title="No projects are built yet." />
      </div>
    );
  }

  // With one project the track overview would be a single card, so `/projects`
  // redirects to that project rather than rendering the same view at a second
  // address. The overview reappears the moment a second project lands.
  const only = track.projects.length === 1 ? track.projects[0] : undefined;
  if (project === undefined && only) {
    return <Navigate to={`/projects/${only.key}`} replace />;
  }

  const p = track.projects.find((x) => x.key === project);

  if (!p) {
    if (project !== undefined) {
      return (
        <div className="page">
          <EmptyState
            icon="projects"
            title="Project not found."
            action={{ label: "Back to Projects", icon: "back", onClick: () => nav("/projects") }}
          />
        </div>
      );
    }
    return <TrackOverview track={track} done={done} />;
  }

  if (view === "reference") return <Handbook project={p} />;
  if (view === "history") return <ProjectHistory project={p} />;
  // Keyed by project: both hold per-project state initialised on mount.
  if (view === "workbench") return <ProjectWorkbench key={p.key} project={p} />;
  if (view === "review") {
    if (!doneLoaded) return <TrackSkeleton cards={2} />;
    const doneKeys = new Set(p.modules.filter((m) => done.has(moduleKey(p.key, m.key))).map((m) => m.key));
    return <ProjectReview key={p.key} project={p} doneKeys={doneKeys} />;
  }

  if (moduleParam) {
    const m = p.modules.find((x) => x.key === moduleParam);
    if (!m) {
      return (
        <div className="page">
          <EmptyState
            icon="projects"
            title="Module not found."
            action={{ label: "Back to the project", icon: "back", onClick: () => nav(`/projects/${p.key}`) }}
          />
        </div>
      );
    }
    const authored = p.modules.filter((x) => x.authored);
    const idx = authored.findIndex((x) => x.key === m.key);
    return (
      <ModulePage
        key={m.key}
        project={p}
        module={m}
        harnessNote={track.harness_note}
        isDone={done.has(moduleKey(p.key, m.key))}
        onSetDone={(v) => setModuleDone(p.key, m.key, v)}
        prev={idx > 0 ? authored[idx - 1] : null}
        next={idx >= 0 && idx < authored.length - 1 ? authored[idx + 1] : null}
      />
    );
  }

  return <ProjectDetail track={track} project={p} done={done} />;
}
