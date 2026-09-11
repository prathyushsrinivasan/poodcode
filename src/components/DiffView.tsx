import { useMemo, useState } from "react";
import { diffSources, diffStats, foldUnchanged, type DiffLine } from "../lib/lineDiff";

const TINT: Record<DiffLine["op"], string | undefined> = {
  add: "color-mix(in srgb, var(--good) 16%, transparent)",
  del: "color-mix(in srgb, var(--bad) 16%, transparent)",
  same: undefined,
};
const SIGN: Record<DiffLine["op"], string> = { add: "+", del: "−", same: " " };
const SIGN_COLOR: Record<DiffLine["op"], string | undefined> = {
  add: "var(--good)",
  del: "var(--bad)",
  same: undefined,
};

/** `+12 −3`, coloured, for a heading or a badge. */
export function DiffStatBadge({ added, removed }: { added: number; removed: number }) {
  return (
    <span className="mono" style={{ fontSize: 12, whiteSpace: "nowrap" }}>
      <span style={{ color: "var(--good)" }}>+{added}</span>{" "}
      <span style={{ color: "var(--bad)" }}>−{removed}</span>
    </span>
  );
}

/**
 * A unified diff of two versions of one file, with long unchanged stretches
 * folded away and unfoldable in place.
 *
 * Both line-number gutters are shown because the two questions a reader has
 * are different: "where is this in the file I have now?" (the new number) and
 * "where did this go?" (the old one).
 */
export function DiffView({
  before,
  after,
  codeOnly = false,
  context = 3,
  maxHeight,
}: {
  before: string;
  after: string;
  codeOnly?: boolean;
  context?: number;
  maxHeight?: number;
}) {
  const lines = useMemo(() => diffSources(before, after, { codeOnly }), [before, after, codeOnly]);
  const chunks = useMemo(() => foldUnchanged(lines, context), [lines, context]);
  // Unfolded gaps, by position. Reset whenever the diff itself changes, since
  // the positions then mean something else.
  const [open, setOpen] = useState<Set<number>>(new Set());
  const [openFor, setOpenFor] = useState(chunks);
  if (openFor !== chunks) {
    setOpenFor(chunks);
    setOpen(new Set());
  }

  const stats = diffStats(lines);
  if (stats.added === 0 && stats.removed === 0) {
    return (
      <p className="faint" style={{ fontSize: 13, margin: "6px 0" }}>
        {codeOnly
          ? "No code changed — only comments and spacing."
          : "The two versions are identical."}
      </p>
    );
  }

  return (
    <div
      className="card"
      style={{
        padding: 0,
        overflow: "auto",
        maxHeight,
        fontFamily: "var(--font-mono)",
        fontSize: 12.5,
        lineHeight: 1.55,
      }}
    >
      <table style={{ borderCollapse: "collapse", width: "100%" }}>
        <tbody>
          {chunks.map((c, ci) =>
            c.kind === "gap" && !open.has(ci) ? (
              <tr key={`g${ci}`}>
                <td
                  colSpan={4}
                  role="button"
                  tabIndex={0}
                  title="Show these lines"
                  onClick={() => setOpen((s) => new Set(s).add(ci))}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setOpen((s) => new Set(s).add(ci));
                    }
                  }}
                  style={{
                    cursor: "pointer",
                    padding: "3px 10px",
                    color: "var(--text-faint)",
                    background: "var(--accent-dim)",
                    fontSize: 11.5,
                  }}
                >
                  ⋯ {c.lines.length} unchanged {c.lines.length === 1 ? "line" : "lines"} — click to
                  show
                </td>
              </tr>
            ) : (
              c.lines.map((l, li) => (
                <tr key={`${ci}:${li}`} style={{ background: TINT[l.op] }}>
                  <td style={gutter}>{l.oldNo ?? ""}</td>
                  <td style={gutter}>{l.newNo ?? ""}</td>
                  <td
                    style={{
                      width: 16,
                      textAlign: "center",
                      color: SIGN_COLOR[l.op],
                      userSelect: "none",
                    }}
                  >
                    {SIGN[l.op]}
                  </td>
                  <td style={{ whiteSpace: "pre", paddingRight: 12 }}>{l.text || " "}</td>
                </tr>
              ))
            )
          )}
        </tbody>
      </table>
    </div>
  );
}

const gutter: React.CSSProperties = {
  width: 1,
  minWidth: 34,
  padding: "0 6px",
  textAlign: "right",
  color: "var(--text-faint)",
  userSelect: "none",
  borderRight: "1px solid var(--border)",
};
