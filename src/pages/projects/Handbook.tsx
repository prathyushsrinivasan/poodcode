/**
 * The project's handbook: everything four kinds of module writing add up to,
 * gathered into one searchable page (UI_ROADMAP G7).
 *
 * The track's claim is that nothing is used before it is taught, and the
 * evidence for that was spread one card at a time across module pages. By
 * module 8 the Todo API teaches around fifty forms, names sixty terms, warns
 * about forty traps and carries sixty acceptance checks — every one inside a
 * module already finished, half of them inside a collapsed step. Nothing here
 * is new data (see src/lib/projectIndex.ts); what each tab is FOR matters,
 * because they are read at different moments:
 *
 *   Syntax     read in order — top to bottom it is the syllabus
 *   Glossary   arrived at with a word in hand — A-Z
 *   Pitfalls   read when something is broken, which is never in the module
 *              that warned you about it
 *   Checks     read when something that used to work has stopped
 *
 * Every module reference here is a link — they were `div`s acting as buttons.
 */

import { useMemo, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import type { Project, SyntaxItem } from "../../types";
import { useCrumb } from "../../store";
import { InlineMarkdown, Markdown } from "../../components/Markdown";
import { Badge, Chip, EmptyState, Icon, PageHeader, Tabs, type IconName } from "../../components/ui";
import { plural } from "../../lib/trackProgress";
import {
  buildCheatsheetIndex,
  buildCheckIndex,
  buildContractIndex,
  buildGlossaryIndex,
  buildPitfallIndex,
  buildSyntaxIndex,
  groupByModule,
  isRetired,
  matchesQuery,
  type ContractEntry,
  type GlossaryEntry,
  type NoteEntry,
} from "../../lib/projectIndex";

type RefTab = "syntax" | "glossary" | "pitfalls" | "checks" | "contract" | "cheatsheets";

const REF_TABS: {
  key: RefTab;
  label: string;
  icon: IconName;
  /** What one row is, for the "n of m … match" line and the empty state. */
  unit: string;
  placeholder: string;
  blurb: string;
}[] = [
  {
    key: "syntax",
    label: "Syntax",
    icon: "braces",
    unit: "form",
    placeholder: "Search syntax, meanings, gotchas…",
    blurb:
      "Every piece of TypeScript the project teaches, in the order it is introduced. Read top to bottom and this is the exact order the project puts the language in front of you.",
  },
  {
    key: "glossary",
    label: "Glossary",
    icon: "learn",
    unit: "term",
    placeholder: "Search terms and definitions…",
    blurb: "Every term the project defines, A-Z — because this is the list you arrive at with a word in hand rather than one you read through.",
  },
  {
    key: "pitfalls",
    label: "Pitfalls",
    icon: "warning",
    unit: "trap",
    placeholder: "Search by symptom — “hangs”, “headers sent”, “404”…",
    blurb:
      "Every mistake the project warns you about, gathered out of the steps they were written in. Search by the symptom you are looking at, not by what you think caused it.",
  },
  {
    key: "checks",
    label: "Checks",
    icon: "checklist",
    unit: "check",
    placeholder: "Search the acceptance checks…",
    blurb:
      "Every module's acceptance checklist. The project page has the finished application's list; this is what has to be true at each module along the way — the list to walk down when something that used to work has stopped.",
  },
  {
    key: "contract",
    label: "Contract",
    icon: "document",
    unit: "route",
    placeholder: "Search by path, verb, status or purpose…",
    blurb:
      "The contract as it stands today, in the order the project builds it — which module each route arrived in, and which later modules changed it. Rows a module merely re-lists unchanged are not counted as changes.",
  },
  {
    key: "cheatsheets",
    label: "Cheat sheets",
    icon: "notes",
    unit: "sheet",
    placeholder: "Search every cheat sheet…",
    blurb:
      "Every module's cheat sheet, end to end. The one tab meant to be read as a single page — the shortest complete description of everything the project has built so far.",
  },
];

export default function Handbook({ project }: { project: Project }) {
  useCrumb(project.title, "Handbook");
  const [tab, setTab] = useState<RefTab>("syntax");
  const [q, setQ] = useState("");

  const syntax = useMemo(() => buildSyntaxIndex(project), [project]);
  const glossary = useMemo(() => buildGlossaryIndex(project), [project]);
  const pitfalls = useMemo(() => buildPitfallIndex(project), [project]);
  const checks = useMemo(() => buildCheckIndex(project), [project]);
  const contract = useMemo(() => buildContractIndex(project), [project]);
  const sheets = useMemo(() => buildCheatsheetIndex(project), [project]);

  const shownSyntax = useMemo(() => syntax.filter((e) => matchesQuery(e, q)), [syntax, q]);
  const shownGlossary = useMemo(() => glossary.filter((e) => matchesQuery(e, q)), [glossary, q]);
  const shownPitfalls = useMemo(() => pitfalls.filter((e) => matchesQuery(e, q)), [pitfalls, q]);
  const shownChecks = useMemo(() => checks.filter((e) => matchesQuery(e, q)), [checks, q]);
  const shownContract = useMemo(() => contract.filter((e) => matchesQuery(e, q)), [contract, q]);
  const shownSheets = useMemo(() => sheets.filter((e) => matchesQuery(e, q)), [sheets, q]);

  const syntaxGroups = useMemo(() => groupByModule(shownSyntax), [shownSyntax]);
  const pitfallGroups = useMemo(() => groupByModule(shownPitfalls), [shownPitfalls]);
  const checkGroups = useMemo(() => groupByModule(shownChecks), [shownChecks]);

  const authored = project.modules.filter((m) => m.authored).length;
  const total = project.modules.length;

  const counts: Record<RefTab, number> = {
    syntax: syntax.length,
    glossary: glossary.length,
    pitfalls: pitfalls.length,
    checks: checks.length,
    contract: contract.length,
    cheatsheets: sheets.length,
  };
  const shownCounts: Record<RefTab, number> = {
    syntax: shownSyntax.length,
    glossary: shownGlossary.length,
    pitfalls: shownPitfalls.length,
    checks: shownChecks.length,
    contract: shownContract.length,
    cheatsheets: shownSheets.length,
  };
  const active = REF_TABS.find((t) => t.key === tab) ?? REF_TABS[0]!;
  const shown = shownCounts[tab];
  const all = counts[tab];
  /** Tabs other than this one that the current query also hits: a query that
   * finds nothing here is very often sitting in the next tab along. */
  const elsewhere = REF_TABS.filter((t) => t.key !== tab && shownCounts[t.key] > 0);

  const moduleHref = (key: string) => `/projects/${project.key}/${key}`;
  /** Deep-link to the step a pitfall was written in. The module page reads
   * `?step=` and opens and scrolls to it, so a trap found here lands on the
   * paragraph that explains it rather than the top of a long module page. */
  const stepHref = (moduleKey: string, stepKey: string) => `${moduleHref(moduleKey)}${stepKey ? `?step=${stepKey}` : ""}`;

  return (
    <div className="page handbook">
      <PageHeader
        eyebrow={<Link to={`/projects/${project.key}`}>{project.title}</Link>}
        title="Handbook"
        subtitle={
          <>
            Everything {project.title} teaches, gathered from all {authored} written {authored === 1 ? "module" : "modules"}{" "}
            — the syllabus, the vocabulary, every trap it warns you about and every check it asks you to run.
          </>
        }
        // The tabs carry the per-tab counts, so this says the thing they
        // cannot: how much of the project is in here at all.
        actions={
          <Badge>
            {authored}/{total} modules written
          </Badge>
        }
      />

      <Tabs
        idBase="handbook"
        active={tab}
        onChange={setTab}
        tabs={REF_TABS.map((t) => ({
          key: t.key,
          label: (
            <>
              <Icon name={t.icon} size={14} />
              <span className="tab-label-text">{t.label}</span>
            </>
          ),
          count: q ? shownCounts[t.key] : counts[t.key],
        }))}
      />

      <div id="handbook-panel" role="tabpanel" aria-labelledby={`handbook-tab-${tab}`} className="handbook-panel">
        <div className="learn-filters" role="search">
          <label className="learn-search">
            <Icon name="search" size={15} />
            <span className="sr-only">Search the handbook</span>
            <input type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder={active.placeholder} />
          </label>
        </div>

        <p className="section-lead">{active.blurb}</p>

        {q && (
          <p className="learn-result-count" role="status">
            {plural(shown, active.unit)} of {all} match “{q}”
            {elsewhere.length > 0 && (
              <span className="learn-elsewhere">
                also:{" "}
                {elsewhere.map((t) => (
                  <Chip key={t.key} onClick={() => setTab(t.key)} count={shownCounts[t.key]} title={`Show the matches under ${t.label}`}>
                    {t.label}
                  </Chip>
                ))}
              </span>
            )}
          </p>
        )}

        {shown === 0 ? (
          <EmptyState
            icon={q ? "search" : "document"}
            title={q ? `No ${active.unit} in ${active.label} matches “${q}”.` : `This project has not written any ${active.unit}s yet.`}
            action={q ? { label: "Clear search", icon: "close", onClick: () => setQ("") } : undefined}
          />
        ) : tab === "syntax" ? (
          syntaxGroups.map((group) => (
            <ModuleGroup key={group.ref.moduleKey} group={group} count={group.entries.length} unit="form" href={moduleHref}>
              {group.entries.map((e) => (
                <SyntaxCard key={e.form} item={e} />
              ))}
            </ModuleGroup>
          ))
        ) : tab === "glossary" ? (
          <div className="card">
            <dl className="glossary">
              {shownGlossary.map((e) => (
                <GlossaryRow key={e.term} entry={e} href={moduleHref} />
              ))}
            </dl>
          </div>
        ) : tab === "pitfalls" ? (
          pitfallGroups.map((group) => (
            <ModuleGroup key={group.ref.moduleKey} group={group} count={group.entries.length} unit="trap" href={moduleHref}>
              <ul className="card card-bad note-list">
                {group.entries.map((e, i) => (
                  <NoteRow key={`${e.stepKey}:${i}`} entry={e} icon="warning" href={stepHref} />
                ))}
              </ul>
            </ModuleGroup>
          ))
        ) : tab === "checks" ? (
          checkGroups.map((group) => (
            <ModuleGroup key={group.ref.moduleKey} group={group} count={group.entries.length} unit="check" href={moduleHref}>
              <ul className="card card-good note-list">
                {group.entries.map((e, i) => (
                  <NoteRow key={i} entry={e} icon="todo" href={stepHref} />
                ))}
              </ul>
            </ModuleGroup>
          ))
        ) : tab === "contract" ? (
          <ContractTable rows={shownContract} href={moduleHref} />
        ) : (
          shownSheets.map((sheet) => (
            <section key={sheet.moduleKey} className="handbook-group">
              <Link className="handbook-group-head" to={moduleHref(sheet.moduleKey)}>
                <span className="mono handbook-num">{sheet.moduleNumber}</span>
                <strong>{sheet.moduleTitle}</strong>
              </Link>
              <Markdown>{sheet.text}</Markdown>
            </section>
          ))
        )}

        {authored < total && (
          <p className="faint page-note">
            {authored} of {total} modules are written. This page grows with them.
          </p>
        )}
      </div>
    </div>
  );
}

/** The contract as built so far: every route, when it arrived, and every later
 * module that changed it. The one view in the app that reads the project as a
 * *ladder* rather than a list — the "Added" column in order is the order the
 * API grew. */
function ContractTable({ rows, href }: { rows: ContractEntry[]; href: (key: string) => string }) {
  return (
    <div className="card table-card">
      <table className="data static">
        <thead>
          <tr>
            <th scope="col">Method</th>
            <th scope="col">Path</th>
            <th scope="col">Purpose</th>
            <th scope="col">Request</th>
            <th scope="col">Response</th>
            <th scope="col">Status</th>
            <th scope="col">Added</th>
            <th scope="col">Changed in</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((e) => {
            // A route a later module removed. Kept rather than dropped: "this
            // used to exist and does not any more" is part of the history.
            const gone = isRetired(e);
            return (
              <tr key={`${e.method} ${e.path}`} className={gone ? "is-retired" : undefined}>
                <td className="mono nowrap endpoint-method">{e.method}</td>
                <td className="mono nowrap endpoint-path">{e.path}</td>
                <td>{e.purpose}</td>
                <td className="mono faint cell-small">{e.request || "—"}</td>
                <td className="mono faint cell-small">{e.response || "—"}</td>
                <td className="mono nowrap cell-small">{e.status}</td>
                <td>
                  <Link className="badge badge-link" to={href(e.moduleKey)} title={`Added in module ${e.moduleNumber}: ${e.moduleTitle}`}>
                    M{e.moduleNumber}
                  </Link>
                </td>
                <td className="nowrap">
                  {e.revisions.length === 0 ? (
                    <span className="faint">—</span>
                  ) : (
                    e.revisions.map((r) => (
                      <Link
                        key={r.moduleKey}
                        className="badge badge-link"
                        to={href(r.moduleKey)}
                        title={
                          gone && r === e.revisions[e.revisions.length - 1]
                            ? `Retired in module ${r.moduleNumber}: ${r.moduleTitle}`
                            : `Changed in module ${r.moduleNumber}: ${r.moduleTitle}`
                        }
                      >
                        M{r.moduleNumber}
                      </Link>
                    ))
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

/** A module heading with its rows underneath — shared by the three tabs that
 * group by module, so they cannot drift apart in spacing or wording. */
function ModuleGroup({
  group,
  count,
  unit,
  href,
  children,
}: {
  group: { ref: { moduleKey: string; moduleNumber: number; moduleTitle: string } };
  count: number;
  unit: string;
  href: (key: string) => string;
  children: ReactNode;
}) {
  return (
    <section className="handbook-group">
      <Link className="handbook-group-head" to={href(group.ref.moduleKey)} title={`Open module ${group.ref.moduleNumber}`}>
        <span className="mono handbook-num">{group.ref.moduleNumber}</span>
        <strong>{group.ref.moduleTitle}</strong>
        <span className="spacer" />
        <span className="mono faint cell-small">{plural(count, unit)}</span>
      </Link>
      {children}
    </section>
  );
}

/** One pitfall or acceptance check. A pitfall carries the step it was written
 * in and links straight to it; a check belongs to the module as a whole. */
function NoteRow({
  entry,
  icon,
  href,
}: {
  entry: NoteEntry;
  icon: IconName;
  href: (moduleKey: string, stepKey: string) => string;
}) {
  return (
    <li>
      <Link
        className="note-row"
        to={href(entry.moduleKey, entry.stepKey)}
        title={entry.stepTitle ? `Open module ${entry.moduleNumber}, step “${entry.stepTitle}”` : `Open module ${entry.moduleNumber}`}
      >
        <Icon name={icon} size={14} className="note-row-icon" />
        <span className="note-row-text">
          <InlineMarkdown>{entry.text}</InlineMarkdown>
        </span>
        {entry.stepTitle && <Badge>{entry.stepTitle}</Badge>}
      </Link>
    </li>
  );
}

function GlossaryRow({ entry, href }: { entry: GlossaryEntry; href: (key: string) => string }) {
  return (
    <div className="glossary-row">
      <dt>
        <code>{entry.term}</code>
      </dt>
      <dd>{entry.def}</dd>
      <Link className="badge badge-link" to={href(entry.moduleKey)} title={`Taught in module ${entry.moduleNumber}`}>
        M{entry.moduleNumber}
      </Link>
    </div>
  );
}

export function SyntaxCard({ item, dim = false }: { item: SyntaxItem; dim?: boolean }) {
  return (
    <div className={`card syntax-card ${dim ? "is-recap" : ""}`}>
      <code className="mono syntax-form">{item.form}</code>
      {item.means && <p className="syntax-means">{item.means}</p>}
      {item.example && <Markdown>{"```ts\n" + item.example.trimEnd() + "\n```"}</Markdown>}
      {item.note && (
        <p className="syntax-note">
          <Icon name="warning" size={13} /> {item.note}
        </p>
      )}
    </div>
  );
}
