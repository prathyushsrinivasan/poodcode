import type { Difficulty } from "../types";

export function DiffBadge({ d }: { d: Difficulty }) {
  return <span className={`badge diff ${d}`}>{d}</span>;
}

export function Confidence({
  value,
  onChange,
  size = 5,
}: {
  value: number;
  onChange?: (v: number) => void;
  size?: number;
}) {
  return (
    <span className="conf" title={`Confidence: ${value}/${size}`}>
      {Array.from({ length: size }).map((_, i) => (
        <span
          key={i}
          className={`dot ${i < value ? "on" : ""}`}
          onClick={
            onChange
              ? (e) => {
                  e.stopPropagation();
                  // Clicking the active last dot clears it.
                  onChange(value === i + 1 ? i : i + 1);
                }
              : undefined
          }
          style={{ cursor: onChange ? "pointer" : "default" }}
        />
      ))}
    </span>
  );
}

export function Stat({ value, label }: { value: React.ReactNode; label: string }) {
  return (
    <div className="card">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

export function Empty({ icon, text }: { icon: string; text: string }) {
  return (
    <div className="empty">
      <div className="big">{icon}</div>
      <div>{text}</div>
    </div>
  );
}

export function Tag({ children }: { children: React.ReactNode }) {
  return <span className="badge tag">{children}</span>;
}

/** A div that behaves like a button: click, Enter and Space all activate it,
 * and it can be tabbed to.
 *
 * List rows that navigate somewhere are the common case — a module in a
 * roadmap, a step in a contents list. They cannot be real `<button>`s without
 * losing the layout, so they need the role, the tab stop and the key handling
 * spelled out; `Section`'s header does exactly this inline, and this is the
 * same thing where a whole row is the target.
 *
 * `disabled` renders the row inert rather than hiding it — a module that is not
 * authored yet still belongs on the roadmap, it just cannot be opened, so it
 * also leaves the tab order. */
export function ClickableRow({
  onActivate,
  disabled = false,
  className,
  style,
  title,
  children,
}: {
  onActivate: () => void;
  disabled?: boolean;
  className?: string;
  style?: React.CSSProperties;
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <div
      className={className}
      style={{ cursor: disabled ? "default" : "pointer", ...style }}
      role={disabled ? undefined : "button"}
      tabIndex={disabled ? undefined : 0}
      aria-disabled={disabled || undefined}
      title={title}
      onClick={disabled ? undefined : onActivate}
      onKeyDown={
        disabled
          ? undefined
          : (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onActivate();
              }
            }
      }
    >
      {children}
    </div>
  );
}
