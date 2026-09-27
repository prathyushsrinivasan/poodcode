// Build history — a project read as the sequence of edits that built it.
//
// Every written module carries a `reference`: the whole program as it stands at
// the end of that module. Laid side by side, consecutive references are the
// build ladder the track claims to be — and the diff between two of them is the
// module, stated in code rather than prose. Module 9's diff is a new route and
// two deleted seed calls; module 4's is the first server. Nothing here is new
// data; it is what the references always said, finally put next to each other.
//
// The comparison lives in the URL (`?to=`, `?from=`, `?code=`), so a link to
// "what module 8 changed" is a link, and the back button undoes a comparison.

import { useMemo } from "react";
import { Link, useSearchParams } from "react-router-dom";
import type { Project, ProjectModule } from "../../types";
import { DiffStatBadge, DiffView } from "../../components/DiffView";
import { Markdown } from "../../components/Markdown";
import { Section, useCollapse } from "../../components/Collapsible";
import { inlineCode } from "../../components/common";
import { useCrumb } from "../../store";
import { UnitPart } from "../../components/track/UnitParts";
import { countCodeLines, diffSources, diffStats, numberLines } from "../../lib/lineDiff";
import { plural } from "../../lib/trackProgress";
import { Badge, Button, Card, CardHeader, EmptyState, Icon, PageHeader, Toggle } from "../../components/ui";

interface Snapshot {
  module: ProjectModule;
  /** Lines of code, ignoring comments and blank lines. */
  code: number;
  /** Lines in total. */
  total: number;
  /** What this module changed against the one before it, code only. */
  added: number;
  removed: number;
}

/** The written modules that carry a reference, oldest first, each measured
 * against the one before it. */
export function buildSnapshots(project: Project): Snapshot[] {
  const mods = project.modules
    .filter((m) => m.authored && m.reference.trim())
    .sort((a, b) => a.number - b.number);
  return mods.map((m, i) => {
    const prev = i > 0 ? mods[i - 1]!.reference : "";
    const s = diffStats(diffSources(prev, m.reference, { codeOnly: true }));
    return {
      module: m,
      code: countCodeLines(m.reference),
      total: numberLines(m.reference).length,
      added: s.added,
      removed: s.removed,
    };
  });
}

/** Sentinel for "compare against nothing" — the first module's diff is the
 * whole file, which is a true statement about what module 1 did. */
const EMPTY = "empty";

export default function ProjectHistory({ project }: { project: Project }) {
  useCrumb(project.title, "Build history");
  const [params, setParams] = useSearchParams();
  const sec = useCollapse(`project-history:${project.key}`, false);
  const snaps = useMemo(() => buildSnapshots(project), [project]);

  if (snaps.length === 0) {
    return (
      <div className="page">
        <PageHeader eyebrow={<Link to={`/projects/${project.key}`}>{project.title}</Link>} title="Build history" />
        <EmptyState icon="history" title="No module of this project has a reference implementation yet." />
      </div>
    );
  }

  const idxOf = (key: string | null) => snaps.findIndex((s) => s.module.key === key);
  const toIdx = idxOf(params.get("to")) >= 0 ? idxOf(params.get("to")) : snaps.length - 1;
  const fromParam = params.get("from");
  // Default "from" is the module immediately before "to" — the question a
  // reader nearly always has is "what did THIS module do?".
  const fromIdx = fromParam === EMPTY ? -1 : idxOf(fromParam) >= 0 ? idxOf(fromParam) : toIdx - 1;
  const codeOnly = params.get("code") !== "0";

  const to = snaps[toIdx]!;
  const from = fromIdx >= 0 ? snaps[fromIdx]! : null;
  // A diff always reads older → newer, whichever way round the two were
  // picked: "what changed between 5 and 9" is one question, not two.
  const older = from && fromIdx > toIdx ? to : from;
  const newer = from && fromIdx > toIdx ? from : to;
  const before = older ? older.module.reference : "";
  const after = newer.module.reference;
  const stats = diffStats(diffSources(before, after, { codeOnly }));
  const isStep = Math.abs(fromIdx - toIdx) === 1;

  const update = (patch: Record<string, string | null>) =>
    setParams((prev) => {
      const next = new URLSearchParams(prev);
      for (const [k, v] of Object.entries(patch)) {
        if (v === null) next.delete(k);
        else next.set(k, v);
      }
      return next;
    });

  /** Select a module and compare it with the one before it. */
  const select = (i: number) => update({ to: snaps[i]!.module.key, from: null });

  const maxCode = Math.max(...snaps.map((s) => s.code), 1);
  const first = snaps[0]!;
  const last = snaps[snaps.length - 1]!;
  const phases = project.roadmap.filter((ph) => snaps.some((s) => s.module.phase === ph.key));

  return (
    <div className="page">
      <PageHeader
        eyebrow={<Link to={`/projects/${project.key}`}>{project.title}</Link>}
        title="Build history"
        subtitle={
          <>
            {project.title}, one module at a time — each module's reference implementation compared with the one before
            it. The track claims every module adds exactly one capability; this is that claim, stated in code.
          </>
        }
        actions={<Badge icon="history">{plural(snaps.length, "snapshot")}</Badge>}
      />

      {/* Growth chart. Bars are code lines (comments excluded) so a module that
          rewrote its comments does not look like it grew. */}
      <Card className="unit-block">
        <CardHeader
          level={2}
          title="How the file grew"
          actions={
            <span className="dim mono cell-small">
              {first.code} → {last.code} lines of code over {plural(snaps.length, "module")}
            </span>
          }
        />
        <div className="growth-scroll">
          <div className="growth" role="group" aria-label="Lines of code per module — pick one to compare">
            {phases.map((ph) => {
              const inPhase = snaps.map((s, i) => ({ s, i })).filter(({ s }) => s.module.phase === ph.key);
              return (
                <div key={ph.key} className="growth-phase">
                  <div className="growth-bars">
                    {inPhase.map(({ s, i }) => (
                      <button
                        key={s.module.key}
                        type="button"
                        className={`growth-bar ${i === toIdx ? "selected" : ""}`}
                        aria-pressed={i === toIdx}
                        aria-label={`Module ${s.module.number}: ${s.module.title}, ${s.code} lines of code, +${s.added} −${s.removed}`}
                        title={`Module ${s.module.number}: ${s.module.title}\n${s.code} lines of code · +${s.added} −${s.removed} against the module before`}
                        onClick={() => select(i)}
                        // The height is the module's line count — data.
                        style={{ height: Math.max(6, Math.round((s.code / maxCode) * 116)) }}
                      />
                    ))}
                  </div>
                  <div className="growth-labels" aria-hidden>
                    {inPhase.map(({ s, i }) => (
                      <span key={s.module.key} className={`mono ${i === toIdx ? "selected" : ""}`}>
                        {s.module.number}
                      </span>
                    ))}
                  </div>
                  <span className="faint growth-phase-name">{ph.title.replace(/^Phase (\d+) · /, "P$1 · ")}</span>
                </div>
              );
            })}
          </div>
        </div>
      </Card>

      {/* The selected module, and the comparison controls. */}
      <Card tone="accent" className="unit-block">
        <CardHeader
          level={2}
          title={
            <>
              <span className="handbook-num">Module {to.module.number}</span> {to.module.title}
            </>
          }
          subtitle={to.module.deliverable ? inlineCode(to.module.deliverable) : undefined}
          actions={
            <Link className="btn" to={`/projects/${project.key}/${to.module.key}`}>
              Open module <Icon name="forward" size={14} />
            </Link>
          }
        />

        <div className="history-controls">
          <Button variant="ghost" size="sm" icon="back" disabled={toIdx === 0} onClick={() => select(toIdx - 1)} title="The module before">
            Previous
          </Button>
          <Button
            variant="ghost"
            size="sm"
            iconRight="forward"
            disabled={toIdx === snaps.length - 1}
            onClick={() => select(toIdx + 1)}
            title="The module after"
          >
            Next
          </Button>
          <label className="history-compare">
            <span className="dim">Compare with</span>
            <select value={from ? from.module.key : EMPTY} onChange={(e) => update({ from: e.target.value })}>
              <option value={EMPTY}>an empty file</option>
              {snaps.map((s, i) =>
                i === toIdx ? null : (
                  <option key={s.module.key} value={s.module.key}>
                    module {s.module.number} — {s.module.title}
                  </option>
                )
              )}
            </select>
          </label>
          <span className="module-changes-toggle">
            <Toggle checked={codeOnly} onChange={(v) => update({ code: v ? null : "0" })} label="Code only" />
            <span aria-hidden>Code only</span>
          </span>
          <span className="spacer" />
          <DiffStatBadge added={stats.added} removed={stats.removed} />
        </div>

        <p className="exercise-note history-explain">
          {older === null
            ? `Everything in module ${to.module.number}'s file, as if written from nothing.`
            : isStep
              ? `What module ${newer.module.number} changed in the file module ${older.module.number} left behind.`
              : `Everything modules ${older.module.number + 1}–${newer.module.number} changed, taken together.`}
          {codeOnly
            ? " Comment-only and blank lines are ignored — turn off “Code only” to see the commentary change too."
            : " Comments are included, and the references rewrite theirs as the project learns more."}
        </p>
      </Card>

      <DiffView before={before} after={after} codeOnly={codeOnly} />

      <Section
        title={`Module ${to.module.number}'s whole file`}
        outline={false}
        open={sec.isOpen("whole")}
        onToggle={() => sec.toggle("whole")}
        meta={
          <span className="dim mono cell-small">
            {to.total} lines · {to.code} code
          </span>
        }
      >
        <Markdown>{"```ts\n" + to.module.reference.trimEnd() + "\n```"}</Markdown>
      </Section>

      <UnitPart title="Every module, in one table" icon="columns">
        <div className="card table-card">
          <table className="data static">
            <thead>
              <tr>
                <th scope="col">#</th>
                <th scope="col">Module</th>
                <th scope="col" className="num">
                  Code lines
                </th>
                <th scope="col" className="num">
                  Changed
                </th>
              </tr>
            </thead>
            <tbody>
              {snaps.map((s, i) => (
                <tr key={s.module.key} className={i === toIdx ? "selected" : undefined}>
                  <td className="mono">{s.module.number}</td>
                  <td>
                    {/* A button in the row, so the row is reachable by Tab. */}
                    <button type="button" className="link-button row-link" onClick={() => select(i)} aria-pressed={i === toIdx}>
                      {s.module.title}
                    </button>
                    <span className="faint cell-small"> — {s.module.what}</span>
                  </td>
                  <td className="mono num">{s.code}</td>
                  <td className="num">
                    <DiffStatBadge added={s.added} removed={s.removed} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </UnitPart>
    </div>
  );
}
