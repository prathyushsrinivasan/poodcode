import { readingSegments } from "../lib/dokkaiText";
import { COMMON_READING_WORDS } from "../data/dokkai/vocabulary";
import { useN2Study } from "../lib/useN2Study";

/** Uses the same occurrence-aware vocabulary as the native reading course.
 * Never infer a kanji reading from its characters. */
export function SupportedJapanese({ text }: { text: string }) {
  return <>{readingSegments(text, COMMON_READING_WORDS).map((s, i) => s.word ? <ruby key={i}>{s.text}<rt>{s.word.reading}</rt></ruby> : s.text)}</>;
}
export default function JlptReadingSupport({ disabled = false, onAssist }: { disabled?: boolean; onAssist?: () => void }) {
  const state = useN2Study();
  if (!state.data || disabled) return null;
  const support = state.data.workspace.support;
  return <details className="jlpt-tips"><summary>Reading support</summary>
    <p className="n2-meta">Kana is available for annotated vocabulary. Using support in a round counts as help.</p>
    {(["readings", "translations"] as const).map((key) => <label className="dokkai-check" key={key}><input type="checkbox" checked={support[key]} onChange={(e) => { if (e.target.checked) onAssist?.(); state.update((p) => ({ ...p, workspace: { ...p.workspace, support: { ...p.workspace.support, [key]: e.target.checked } } })); }} />{key === "readings" ? "Show annotated readings" : "Show English translations"}</label>)}
  </details>;
}
