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
