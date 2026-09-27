/**
 * The Projects track overview and one project's page: the destination, the
 * contract and the roadmap (UI_ROADMAP G7).
 */

import { useMemo } from "react";
import { Link } from "react-router-dom";
import type { Project, ProjectTrack } from "../../types";
import { useCrumb } from "../../store";
import { Markdown } from "../../components/Markdown";
import { Section, useCollapse } from "../../components/Collapsible";
import { TrackBody, TrackHero, trackProgress, type TrackGroup, type TrackSpec } from "../../components/track/TrackShell";
import { EndpointTable } from "../../components/track/EndpointTable";
import { Milestone, UnitGoal, UnitList, UnitPart } from "../../components/track/UnitParts";
import { Badge, Icon, PageHeader, type IconName } from "../../components/ui";
import { collectQuestions } from "../../lib/projectReview";
import { plural, studyTime } from "../../lib/trackProgress";
import { moduleKey } from "./shared";

/** Every project — only reachable once there is more than one. */
export function TrackOverview({ track, done }: { track: ProjectTrack; done: Set<string> }) {
  return (
    <div className="page">
      <PageHeader title={track.title} subtitle={track.subtitle} />
      {track.intro && (
        <div className="card unit-block">
          <Markdown>{track.intro}</Markdown>
        </div>
      )}
      <ul className="project-cards">
        {track.projects.map((p) => {
          const authored = p.modules.filter((m) => m.authored);
          const n = authored.filter((m) => done.has(moduleKey(p.key, m.key))).length;
          const body = (
            <>
              <strong>
                {p.number}. {p.title}
              </strong>
              <span className="concept-card-what">{p.tagline}</span>
              <span className="faint project-card-meta">
                {n}/{authored.length} modules · {p.stack.join(" · ")}
              </span>
            </>
          );
          return (
            <li key={p.key}>
              {p.authored ? (
                <Link to={`/projects/${p.key}`} className="card concept-card">
                  {body}
                </Link>
              ) : (
                // Not written yet: on the map, but not a link.
                <div className="card concept-card is-unwritten" aria-disabled>
                  {body}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export function ProjectDetail({ track, project, done }: { track: ProjectTrack; project: Project; done: Set<string> }) {
  useCrumb(project.title, "Project");
  const sec = useCollapse(`project-overview:${project.key}`, false);
  // "How to work through this" is orientation, so it opens by default and gets
  // its own namespace to say so. On a single-project track the overview page
  // never renders, and this is the only place the track intro is ever shown.
  const introSec = useCollapse(`project-intro:${project.key}`, true);

  const authored = project.modules.filter((m) => m.authored);
  const doneCount = authored.filter((m) => done.has(moduleKey(project.key, m.key))).length;
  const totalModules = project.modules.length;

  /* A project *is* a track: its modules are the units and its roadmap phases
     are the groups. Describing it that way gets the same hero, rail and rows
     the courses use (UI_ROADMAP G1). */
  const spec = useMemo<TrackSpec>(
    () => ({
      title: project.title,
      subtitle: project.tagline,
      base: `/projects/${project.key}`,
      unitLabel: "Module",
      groupLabel: "Phase",
      groups: project.roadmap.map<TrackGroup>((ph) => ({ key: ph.key, title: ph.title })),
      units: project.modules.map((m) => ({
        slug: m.key,
        number: m.number,
        title: m.title,
        tagline: m.what,
        group: m.phase,
        done: m.authored && done.has(moduleKey(project.key, m.key)),
        authored: m.authored,
        estMinutes: m.est_minutes,
      })),
    }),
    [project, done]
  );
  const progress = useMemo(() => trackProgress(spec.units), [spec.units]);

  return (
    <div className="page">
      <PageHeader title={project.title} subtitle={project.tagline} />

      <TrackHero spec={spec} progress={progress} />

      <p className="faint project-stack">
        {project.stack.join(" · ")} · {studyTime(project.est_minutes)} of building.{" "}
        {authored.length < totalModules
          ? `${authored.length} of ${totalModules} planned modules are written.`
          : `${plural(totalModules, "module")}.`}
        {project.completion_note ? ` ${project.completion_note}` : ""}
      </p>

      <ProjectTools project={project} doneCount={doneCount} />

      <UnitGoal label="What you are building" goal={project.goal} why={project.why} />

      {track.intro && (
        <Section title="How to work through this" open={introSec.isOpen("intro")} onToggle={() => introSec.toggle("intro")}>
          <Markdown>{track.intro}</Markdown>
        </Section>
      )}

      {project.brief && <Markdown>{project.brief}</Markdown>}

      {project.endpoints.length > 0 && (
        <UnitPart
          title="The contract"
          icon="document"
          lead="The finished application's contract. Every module below chips away at one or two of these rows."
        >
          <EndpointTable endpoints={project.endpoints} />
        </UnitPart>
      )}

      {project.setup && (
        <UnitPart title="Set up" icon="tools">
          <Markdown>{project.setup}</Markdown>
        </UnitPart>
      )}

      <UnitPart
        title="The roadmap"
        icon="map"
        lead={
          <>
            {plural(totalModules, "module")} in {plural(project.roadmap.length, "phase")}. Each phase ends with something
            you can demonstrate — that is what makes it a phase rather than an arbitrary grouping.
          </>
        }
      >
        <TrackBody spec={spec} progress={progress} />
      </UnitPart>

      {track.harness_note && (
        <Section
          title="How the exercises are judged"
          open={sec.isOpen("harness")}
          onToggle={() => sec.toggle("harness")}
          meta={<Badge>read once</Badge>}
        >
          <Markdown>{track.harness_note}</Markdown>
        </Section>
      )}

      {project.acceptance.length > 0 && (
        <Section
          title="Acceptance — the finished application"
          outline="Acceptance"
          open={sec.isOpen("acceptance")}
          onToggle={() => sec.toggle("acceptance")}
          meta={<Badge>{project.acceptance.length} checks</Badge>}
        >
          <UnitList items={project.acceptance} />
        </Section>
      )}

      {project.manual_test && (
        <Section
          title="Try the finished thing yourself"
          open={sec.isOpen("manual")}
          onToggle={() => sec.toggle("manual")}
          // The badge names the tool the block actually uses. A project with a
          // contract is driven over HTTP; one without is driven from a shell.
          meta={<Badge icon="terminal">{project.endpoints.length > 0 ? "curl" : "shell"}</Badge>}
        >
          <Markdown>{project.manual_test}</Markdown>
        </Section>
      )}

      {project.stretch.length > 0 && (
        <Section
          title="Once it is done"
          open={sec.isOpen("stretch")}
          onToggle={() => sec.toggle("stretch")}
          meta={<Badge>{project.stretch.length} ideas</Badge>}
        >
          <UnitList items={project.stretch} />
        </Section>
      )}

      {project.milestone && <Milestone text={project.milestone} />}
    </div>
  );
}

/** The four project-level pages, each with the one line that says when you
 * would open it — they are used at very different moments, and a row of bare
 * icons would not say that. Links, so they can be Ctrl-clicked and tabbed to. */
function ProjectTools({ project, doneCount }: { project: Project; doneCount: number }) {
  const snapshots = project.modules.filter((m) => m.authored && m.reference.trim()).length;
  const builds = project.modules.filter((m) => m.authored && m.final_build).length;
  const questions = useMemo(() => collectQuestions(project).length, [project]);
  const tools: { path: string; icon: IconName; title: string; blurb: string; meta: string }[] = [
    {
      path: "reference",
      icon: "learn",
      title: "Handbook",
      blurb: "Every form, term, trap and check, searchable. Open it when something is broken.",
      meta: "6 indexes",
    },
    {
      path: "history",
      icon: "history",
      title: "Build history",
      blurb: "What each module changed in the file, as a diff. The build ladder, in code.",
      meta: `${snapshots} snapshots`,
    },
    {
      path: "workbench",
      icon: "playground",
      title: "Workbench",
      blurb: "Load any module's build, edit it, and run your own input against it.",
      meta: `${builds} builds`,
    },
    {
      path: "review",
      icon: "refresh",
      title: "Review",
      blurb:
        doneCount > 0
          ? "Mixed questions from the modules you've finished — misses come back first."
          : "Mixed questions from across the project, asked again out of order.",
      meta: `${questions} questions`,
    },
  ];
  return (
    <ul className="project-tools">
      {tools.map((t) => (
        <li key={t.path}>
          <Link to={`/projects/${project.key}/${t.path}`} className="card concept-card project-tool">
            <span className="project-tool-head">
              <strong>
                <Icon name={t.icon} size={15} /> {t.title}
              </strong>
              <span className="faint mono project-card-meta">{t.meta}</span>
            </span>
            <span className="concept-card-what">{t.blurb}</span>
          </Link>
        </li>
      ))}
    </ul>
  );
}
