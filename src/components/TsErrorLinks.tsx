import { Link } from "react-router-dom";
import { entriesIn } from "../lib/tsErrors";
import { inlineCode } from "./common";

/**
 * Under a compile error: one link per TypeScript error code in it that the
 * glossary explains. `TS2322: Type 'string' is not assignable to type 'number'`
 * is exact but assumes the vocabulary; the glossary entry says what it means,
 * shows a minimal program that produces it, and the same program fixed.
 *
 * Renders nothing for output with no known codes (Java, Python, runtime errors).
 */
export function TsErrorLinks({ text }: { text: string }) {
  const entries = entriesIn(text);
  if (entries.length === 0) return null;
  return (
    <div className="ts-error-links">
      <span className="dim">What do these mean?</span>
      {entries.map((e) => (
        <Link key={e.code} className="ts-error-chip" to={`/ts-errors?code=${e.code}`} title={e.meaning}>
          TS{e.code} <span className="dim">— {inlineCode(e.meaning)}</span>
        </Link>
      ))}
    </div>
  );
}
