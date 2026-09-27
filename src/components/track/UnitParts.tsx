/**
 * The pieces of a unit page — a course week, a Backend Lab project, a Projects
 * module — shared (UI_ROADMAP G1, G4, C2).
 *
 * G1 put the three tracks' *overviews* on one template. Their unit pages were
 * still three copies of the same layout: a goal card, an objectives list, a
 * clickable-row contents card, "parts" with an emoji heading and a divider, a
 * checklist, a glossary, a milestone — each with its own inline styles and its
 * own `div onClick` rows. These are that layout once.
 */

import type { ReactNode } from "react";
import { inlineCode } from "../common";
import { Button, Card, CardHeader, Icon, type IconName } from "../ui";
import { Deeper, H } from "../ui/Heading";

/** "What this unit is for": the goal, why it matters, what it builds on. */
export function UnitGoal({
  label,
  goal,
  why,
  buildsOn,
}: {
  label: string;
  goal: string;
  why?: string;
  buildsOn?: string[];
}) {
  return (
    <Card tone="accent" className="unit-goal">
      <div className="io-label">
        <Icon name="target" size={13} /> {label}
      </div>
      <p>{inlineCode(goal)}</p>
      {why && (
        <p className="unit-why">
          <Icon name="hint" size={13} /> Why it matters: {inlineCode(why)}
        </p>
      )}
      {buildsOn && buildsOn.length > 0 && (
        <p className="unit-why">
          <Icon name="layers" size={13} /> Continues from: {buildsOn.join(", ")}
        </p>
      )}
    </Card>
  );
}

/** A titled bullet list in a card: objectives, a rubric, a checklist. */
export function UnitList({ label, items, tone }: { label?: ReactNode; items: string[]; tone?: "good" }) {
  if (items.length === 0) return null;
  return (
    <Card className="unit-block" tone={tone}>
      {label && <div className={`io-label ${tone === "good" ? "is-good" : ""}`}>{label}</div>}
      <ul className="unit-list">
        {items.map((o, i) => (
          <li key={i}>{inlineCode(o)}</li>
        ))}
      </ul>
    </Card>
  );
}

export interface ContentsRow {
  key: string;
  title: string;
  what?: string;
  /** Solved / total exercises; omit both for a row with none. */
  solved?: number;
  total?: number;
}

/**
 * The unit's own table of contents, with progress per row. Rows are buttons
 * (they were `div`s with `onClick`, unreachable by keyboard — D3), and
 * activating one opens that part and scrolls to it.
 */
export function UnitContents({
  title,
  icon = "learn",
  rows,
  onOpen,
  onExpandAll,
  onCollapseAll,
  numberPrefix = "",
}: {
  title: string;
  icon?: IconName;
  rows: ContentsRow[];
  onOpen: (key: string) => void;
  onExpandAll: () => void;
  onCollapseAll: () => void;
  numberPrefix?: string;
}) {
  if (rows.length === 0) return null;
  return (
    <Card className="unit-block unit-contents">
      <CardHeader
        level={2}
        icon={icon}
        title={title}
        actions={
          <>
            <Button variant="ghost" size="sm" icon="chevronDown" onClick={onExpandAll}>
              Expand all
            </Button>
            <Button variant="ghost" size="sm" icon="chevronRight" onClick={onCollapseAll}>
              Collapse all
            </Button>
          </>
        }
      />
      <ol className="unit-lessons">
        {rows.map((r, i) => {
          const complete = (r.total ?? 0) > 0 && r.solved === r.total;
          return (
            <li key={r.key}>
              <button type="button" className="unit-lesson" onClick={() => onOpen(r.key)}>
                <span className={`unit-lesson-mark ${complete ? "is-good" : ""}`}>
                  {complete ? <Icon name="check" size={14} label="Complete" /> : `${numberPrefix}${i + 1}`}
                </span>
                <span className="unit-lesson-title">
                  {r.title}
                  {r.what && <span className="faint"> — {r.what}</span>}
                </span>
                {(r.total ?? 0) > 0 && (
                  <span className="unit-lesson-count">
                    {r.solved}/{r.total}
                  </span>
                )}
              </button>
            </li>
          );
        })}
      </ol>
    </Card>
  );
}

/** Open a folded part and scroll to it once its body has mounted. */
export function scrollToPart(id: string) {
  requestAnimationFrame(() => {
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    document.getElementById(id)?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  });
}

/** A top-level part of a unit page (Practice, Capstone, Self-check…), named for the outline. */
export function UnitPart({
  title,
  icon,
  outline,
  lead,
  children,
}: {
  title: ReactNode;
  icon: IconName;
  /** The outline label, when `title` is not a plain string. */
  outline?: string;
  lead?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="unit-part">
      <H className="unit-part-title">
        {/* The outline reads `data-outline`; on the heading so a jump lands on it. */}
        <span data-outline={outline ?? (typeof title === "string" ? title : undefined)} className="unit-part-anchor">
          <Icon name={icon} size={18} /> {title}
        </span>
      </H>
      {lead && <p className="section-lead">{lead}</p>}
      <Deeper>{children}</Deeper>
    </section>
  );
}

/** A heading inside a part or a lesson body (Predict the output, Fix the bug…). */
export function SubHeading({ icon, children }: { icon: IconName; children: ReactNode }) {
  return (
    <H className="unit-subtitle">
      <Icon name={icon} size={15} /> {children}
    </H>
  );
}

export function Glossary({ terms }: { terms: { term: string; def: string }[] }) {
  return (
    <Card>
      <dl className="glossary">
        {terms.map((g, i) => (
          <div key={i} className="glossary-row">
            <dt>
              <code>{g.term}</code>
            </dt>
            <dd>{inlineCode(g.def)}</dd>
          </div>
        ))}
      </dl>
    </Card>
  );
}

export function Milestone({ text }: { text: string }) {
  return (
    <Card tone="good" className="unit-block unit-milestone">
      <div className="io-label is-good">
        <Icon name="trophy" size={13} /> Milestone
      </div>
      <p>{inlineCode(text)}</p>
    </Card>
  );
}
