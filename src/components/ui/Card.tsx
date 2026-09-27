/**
 * Cards, page headers, badges and progress (UI_ROADMAP C3).
 *
 * Each of these was rebuilt by hand on every page: `div.card` with an inline
 * `h3 style={{marginTop: 0}}` dozens of times, a dozen `.progress > span
 * style={{width}}` bars with no ARIA, and `h1.page-title` + `p.page-sub` with
 * the actions floated wherever that page put them.
 */

import type { ReactNode } from "react";
import { Icon, type IconName } from "./Icon";

type HeadingLevel = 1 | 2 | 3 | 4;

function Heading({ level, className, children, id }: { level: HeadingLevel; className: string; children: ReactNode; id?: string }) {
  const Tag = `h${level}` as "h1" | "h2" | "h3" | "h4";
  return (
    <Tag className={className} id={id}>
      {children}
    </Tag>
  );
}

export function Card({
  children,
  className = "",
  as = "div",
  tone,
  labelledBy,
}: {
  children: ReactNode;
  className?: string;
  /** `section` when the card is a region of the page with its own heading. */
  as?: "div" | "section" | "article";
  /** A coloured left edge, for a card that carries a verdict. */
  tone?: "good" | "bad" | "warn" | "accent";
  labelledBy?: string;
}) {
  const Tag = as;
  return (
    <Tag className={`card ${tone ? `card-${tone}` : ""} ${className}`.trim()} aria-labelledby={labelledBy}>
      {children}
    </Tag>
  );
}

/** A card's title row: heading, optional subtitle, actions at the right. */
export function CardHeader({
  title,
  subtitle,
  icon,
  actions,
  level = 2,
  id,
}: {
  title: ReactNode;
  subtitle?: ReactNode;
  icon?: IconName;
  actions?: ReactNode;
  level?: HeadingLevel;
  id?: string;
}) {
  return (
    <div className="card-header">
      <div className="card-header-text">
        <Heading level={level} className="card-title" id={id}>
          {icon && <Icon name={icon} size={16} className="card-title-icon" />}
          {title}
        </Heading>
        {subtitle && <p className="card-subtitle">{subtitle}</p>}
      </div>
      {actions && <div className="card-header-actions">{actions}</div>}
    </div>
  );
}

/** The top of a page: an optional eyebrow, the one `h1`, a subtitle and actions. */
export function PageHeader({
  title,
  subtitle,
  eyebrow,
  actions,
  children,
}: {
  title: ReactNode;
  subtitle?: ReactNode;
  eyebrow?: ReactNode;
  actions?: ReactNode;
  /** Anything that belongs to the header but below the subtitle (a progress line, chips). */
  children?: ReactNode;
}) {
  return (
    <header className="page-header">
      <div className="page-header-text">
        {eyebrow && <div className="page-eyebrow">{eyebrow}</div>}
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="page-sub">{subtitle}</p>}
        {children}
      </div>
      {actions && <div className="page-header-actions">{actions}</div>}
    </header>
  );
}

export type Tone = "neutral" | "accent" | "good" | "bad" | "warn";

/** A static label. For something you can click, use `Chip`. */
export function Badge({
  children,
  tone = "neutral",
  icon,
  title,
  className = "",
}: {
  children: ReactNode;
  tone?: Tone;
  icon?: IconName;
  title?: string;
  className?: string;
}) {
  return (
    <span className={`badge badge-${tone} ${className}`.trim()} title={title}>
      {icon && <Icon name={icon} size={12} />}
      {children}
    </span>
  );
}

/**
 * A clickable pill — a filter, a suggestion, a toggle. It is a real button, so
 * it is in the tab order and Enter/Space work; the Dashboard's recommendation
 * chips were `span`s with `onClick` and a keyboard could not reach them (B4).
 * `pressed` makes it a toggle and says so to assistive tech.
 */
export function Chip({
  children,
  onClick,
  pressed,
  icon,
  count,
  title,
  disabled,
  className = "",
}: {
  children: ReactNode;
  onClick: () => void;
  pressed?: boolean;
  disabled?: boolean;
  icon?: IconName;
  count?: number;
  title?: string;
  className?: string;
}) {
  return (
    <button
      type="button"
      className={`pill chip ${pressed ? "on" : ""} ${className}`.trim()}
      aria-pressed={pressed}
      onClick={onClick}
      title={title}
      disabled={disabled}
    >
      {icon && <Icon name={icon} size={12} />}
      {children}
      {count !== undefined && <span className="chip-count">{count}</span>}
    </button>
  );
}

/**
 * A progress bar with the ARIA a bar needs to be more than a coloured stripe.
 * `value` and `max` are counts; the width is the one inline style that is
 * genuinely data.
 */
export function ProgressBar({
  value,
  max = 100,
  tone = "accent",
  label,
  showValue = false,
  size = "md",
  className = "",
}: {
  value: number;
  max?: number;
  tone?: "accent" | "good" | "warn" | "bad";
  /** The accessible name — what this is the progress *of*. */
  label: string;
  /** Show "12 / 40" after the bar. */
  showValue?: boolean;
  size?: "sm" | "md";
  className?: string;
}) {
  const pct = max > 0 ? Math.max(0, Math.min(100, (value / max) * 100)) : 0;
  return (
    <div className={`progress-wrap ${className}`.trim()}>
      <div
        className={`progress progress-${tone} ${size === "sm" ? "progress-sm" : ""}`}
        role="progressbar"
        aria-label={label}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-valuenow={value}
        aria-valuetext={`${value} of ${max}`}
      >
        <span style={{ width: `${pct}%` }} />
      </div>
      {showValue && (
        <span className="progress-value">
          {value} / {max}
        </span>
      )}
    </div>
  );
}

/** A keyboard key, or a chord: `<Kbd keys="Ctrl+Enter" />`. */
export function Kbd({ keys }: { keys: string }) {
  const parts = keys.split("+");
  return (
    <span className="kbd-chord">
      {parts.map((k, i) => (
        <span key={i}>
          <kbd className="kbd">{k}</kbd>
          {i < parts.length - 1 && <span className="kbd-plus">+</span>}
        </span>
      ))}
    </span>
  );
}
