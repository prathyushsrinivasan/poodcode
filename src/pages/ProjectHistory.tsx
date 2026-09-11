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
import { useNavigate, useSearchParams } from "react-router-dom";
import type { Project, ProjectModule } from "../types";
import { DiffStatBadge, DiffView } from "../components/DiffView";
import { Markdown } from "../components/Markdown";
import { Section, useCollapse } from "../components/Collapsible";
import { ClickableRow, Empty } from "../components/common";
import { countCodeLines, diffSources, diffStats, numberLines } from "../lib/lineDiff";
import { plural } from "../lib/trackProgress";

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
  const nav = useNavigate();
  const [params, setParams] = useSearchParams();
  const sec = useCollapse(`project-history:${project.key}`, false);
  const snaps = useMemo(() => buildSnapshots(project), [project]);

  if (snaps.length === 0) {
    return (
      <div className="page">
        <button className="ghost" onClick={() => nav(`/projects/${project.key}`)}>
          ← {project.title}
        </button>
        <Empty icon="🕰️" text="No module of this project has a reference implementation yet." />
      </div>
    );
  }

  const idxOf = (key: string | null) => snaps.findIndex((s) => s.module.key === key);
  const toIdx = idxOf(params.get("to")) >= 0 ? idxOf(params.get("to")) : snaps.length - 1;
  const fromParam = params.get("from");
  // Default "from" is the module immediately before "to" — the question a
  // reader nearly always has is "what did THIS module do?".
  const fromIdx =
    fromParam === EMPTY ? -1 : idxOf(fromParam) >= 0 ? idxOf(fromParam) : toIdx - 1;
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
  const select = (i: number) =>
    update({ to: snaps[i]!.module.key, from: null });

  const maxCode = Math.max(...snaps.map((s) => s.code), 1);
  const first = snaps[0]!;
  const last = snaps[snaps.length - 1]!;
  const phases = project.roadmap.filter((ph) => snaps.some((s) => s.module.phase === ph.key));

  return (
    <div className="page">
      <div className="row" style={{ marginBottom: 4 }}>
        <button className="ghost" onClick={() => nav(`/projects/${project.key}`)}>
          ← {project.title}
        </button>
        <span className="badge">{plural(snaps.length, "snapshot")}</span>
      </div>

      <h1 className="page-title" style={{ marginTop: 6 }}>
        Build history
      </h1>
      <p className="page-sub">
        {project.title}, one module at a time — each module's reference implementation compared
        with the one before it. The track claims every module adds exactly one capability; this is
        that claim, stated in code.
      </p>

      {/* Growth chart. Bars are code lines (comments excluded) so a module that
          rewrote its comments does not look like it grew. */}
      <div className="card" style={{ marginBottom: 14 }}>
        <div className="row" style={{ marginBottom: 10, alignItems: "baseline" }}>
          <strong>How the file grew</strong>
          <span className="spacer" />
          <span className="dim mono" style={{ fontSize: 12 }}>
            {first.code} → {last.code} lines of code over {plural(snaps.length, "module")}
          </span>
        </div>
        <div style={{ overflowX: "auto" }}>
          <div className="row" style={{ alignItems: "flex-end", gap: 14, minWidth: "min-content" }}>
            {phases.map((ph) => {
              const inPhase = snaps
                .map((s, i) => ({ s, i }))
                .filter(({ s }) => s.module.phase === ph.key);
              return (
                <div key={ph.key} style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <div className="row" style={{ alignItems: "flex-end", gap: 4, height: 120 }}>
                    {inPhase.map(({ s, i }) => {
                      const selected = i === toIdx;
                      const h = Math.max(6, Math.round((s.code / maxCode) * 116));
                      return (
                        <ClickableRow
                          key={s.module.key}
                          title={
                            `Module ${s.module.number}: ${s.module.title}\n` +
                            `${s.code} lines of code · +${s.added} −${s.removed} against the module before`
                          }
                          onActivate={() => select(i)}
                          style={{
                            width: 26,
                            height: h,
                            borderRadius: "4px 4px 0 0",
                            background: selected ? "var(--accent)" : "var(--accent-dim)",
                            outline: selected ? "2px solid var(--accent)" : undefined,
                            outlineOffset: 1,
                          }}
                        >
                          <span />
                        </ClickableRow>
                      );
                    })}
                  </div>
                  <div className="row" style={{ gap: 4 }}>
                    {inPhase.map(({ s, i }) => (
                      <span
                        key={s.module.key}
                        className="mono"
                        style={{
                          width: 26,
                          textAlign: "center",
                          fontSize: 11,
                          color: i === toIdx ? "var(--accent)" : "var(--text-faint)",
                        }}
                      >
                        {s.module.number}
                      </span>
                    ))}
                  </div>
                  <span
                    className="faint"
                    style={{
                      fontSize: 11,
                      borderTop: "1px solid var(--border)",
                      paddingTop: 3,
                      whiteSpace: "nowrap",
                    }}
                  >
                    {ph.title.replace(/^Phase (\d+) · /, "P$1 · ")}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* The selected module, and the comparison controls. */}
      <div className="card" style={{ marginBottom: 12, borderColor: "var(--accent)" }}>
        <div className="row" style={{ alignItems: "flex-start", gap: 10 }}>
          <div style={{ flex: 1 }}>
            <div className="io-label" style={{ color: "var(--accent)", marginBottom: 2 }}>
              Module {to.module.number}
            </div>
            <strong style={{ fontSize: 16 }}>{to.module.title}</strong>
            {to.module.deliverable && (
              <p className="dim" style={{ margin: "4px 0 0", fontSize: 13 }}>
                📦 {to.module.deliverable}
              </p>
            )}
          </div>
          <button onClick={() => nav(`/projects/${project.key}/${to.module.key}`)}>
            Open module →
          </button>
        </div>

        <div className="row" style={{ gap: 8, marginTop: 12, flexWrap: "wrap", alignItems: "center" }}>
          <button
            className="ghost"
            disabled={toIdx === 0}
            onClick={() => select(toIdx - 1)}
            title="The module before"
          >
            ← prev
          </button>
          <button
            className="ghost"
            disabled={toIdx === snaps.length - 1}
            onClick={() => select(toIdx + 1)}
            title="The module after"
          >
            next →
          </button>
          <span className="dim" style={{ fontSize: 13, marginLeft: 6 }}>
            Compare with
          </span>
          <select
            value={from ? from.module.key : EMPTY}
            onChange={(e) => update({ from: e.target.value })}
            aria-label="Compare with"
          >
            <option value={EMPTY}>an empty file</option>
            {snaps.map((s, i) =>
              i === toIdx ? null : (
                <option key={s.module.key} value={s.module.key}>
                  module {s.module.number} — {s.module.title}
                </option>
              )
            )}
          </select>
          <label className="row" style={{ gap: 6, fontSize: 13, cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={codeOnly}
              onChange={(e) => update({ code: e.target.checked ? null : "0" })}
            />
            Code only
          </label>
          <span className="spacer" />
          <DiffStatBadge added={stats.added} removed={stats.removed} />
        </div>

        <p className="faint" style={{ fontSize: 12, margin: "8px 0 0" }}>
          {older === null
            ? `Everything in module ${to.module.number}'s file, as if written from nothing.`
            : isStep
              ? `What module ${newer.module.number} changed in the file module ${older.module.number} left behind.`
              : `Everything modules ${older.module.number + 1}–${newer.module.number} changed, taken together.`}
          {codeOnly
            ? " Comment-only and blank lines are ignored — untick “Code only” to see the commentary change too."
            : " Comments are included, and the references rewrite theirs as the project learns more."}
        </p>
      </div>

      <DiffView before={before} after={after} codeOnly={codeOnly} />

      <Section
        title={`📄 Module ${to.module.number}'s whole file`}
        open={sec.isOpen("whole")}
        onToggle={() => sec.toggle("whole")}
        meta={
          <span className="dim mono" style={{ fontSize: 12 }}>
            {to.total} lines · {to.code} code
          </span>
        }
      >
        <Markdown>{"```ts\n" + to.module.reference.trimEnd() + "\n```"}</Markdown>
      </Section>

      <h3 style={{ margin: "22px 0 6px" }}>Every module, in one table</h3>
      <div className="card" style={{ overflowX: "auto", padding: 0 }}>
        <table className="data" style={{ cursor: "default" }}>
          <thead>
            <tr>
              <th style={{ cursor: "default" }}>#</th>
              <th style={{ cursor: "default" }}>Module</th>
              <th style={{ cursor: "default", textAlign: "right" }}>Code lines</th>
              <th style={{ cursor: "default", textAlign: "right" }}>Changed</th>
            </tr>
          </thead>
          <tbody>
            {snaps.map((s, i) => (
              <tr
                key={s.module.key}
                onClick={() => select(i)}
                style={{
                  cursor: "pointer",
                  background: i === toIdx ? "var(--accent-dim)" : undefined,
                }}
              >
                <td className="mono">{s.module.number}</td>
                <td>
                  {s.module.title}
                  <span className="faint" style={{ fontSize: 12 }}>
                    {" "}
                    — {s.module.what}
                  </span>
                </td>
                <td className="mono" style={{ textAlign: "right" }}>
                  {s.code}
                </td>
                <td style={{ textAlign: "right" }}>
                  <DiffStatBadge added={s.added} removed={s.removed} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
