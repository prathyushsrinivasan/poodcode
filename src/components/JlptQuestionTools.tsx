import { Button } from "./ui";
import { MISTAKE_REASONS } from "../lib/n2Study";
import { useN2Study } from "../lib/useN2Study";
import { STUDY_QUESTION_MAP } from "../data/n2Study";

/** Shared collection and notebook for native courses. Namespaced IDs prevent
 * unrelated legacy courses from colliding with guided question IDs. */
export default function JlptQuestionTools({ id, review = false }: { id: string; review?: boolean }) {
  const alias = id.startsWith("order:") ? `assembly-${id.slice(6)}` : id.startsWith("reading:") ? `study-${id.slice(8)}` : id;
  if (STUDY_QUESTION_MAP.has(alias)) id = alias;
  const state = useN2Study();
  if (!state.data) return null;
  const saved = state.data.bookmarks.includes(id);
  const note = state.data.notes[id] ?? { text: "", reason: "" };
  return <div className="jlpt-question-tools">
    <Button size="sm" variant="ghost" aria-pressed={saved} onClick={() => state.update((p) => ({ ...p, bookmarks: saved ? p.bookmarks.filter((q) => q !== id) : [...p.bookmarks, id] }))}>{saved ? "Saved ★" : "Save question"}</Button>
    {review && <details><summary>Mistake note &amp; takeaway</summary>
      <label className="study-field">Mistake reason<select value={note.reason} onChange={(e) => state.update((p) => ({ ...p, notes: { ...p.notes, [id]: { ...note, reason: e.target.value } } }))}><option value="">Choose a reason</option>{MISTAKE_REASONS.map((r) => <option key={r}>{r}</option>)}</select></label>
      <label className="study-field">Takeaway<textarea maxLength={4000} rows={3} value={note.text} onChange={(e) => state.update((p) => ({ ...p, notes: { ...p.notes, [id]: { ...note, text: e.target.value } } }))} /></label>
    </details>}
    {(state.loadError || state.saveError) && <p role="alert">{state.loadError || state.saveError}</p>}
  </div>;
}
