import { Link } from "react-router-dom";
import { useN2Study } from "../lib/useN2Study";

export default function JlptListPicker({ id }: { id: string }) {
  const state = useN2Study();
  if (!state.data) return null;
  const lists = state.data.workspace.lists;
  if (!lists.length) return <Link to="/japanese/n2/review?tab=vocabulary">Create a vocabulary list →</Link>;
  return <label className="study-field">Add to vocabulary list<select value="" onChange={(e) => { const listId = e.target.value; state.update((p) => ({ ...p, workspace: { ...p.workspace, lists: p.workspace.lists.map((l) => l.id === listId ? { ...l, items: [...new Set([...l.items, id])] } : l) } })); }}><option value="">Choose a list</option>{lists.map((l) => <option key={l.id} value={l.id} disabled={l.items.includes(id)}>{l.name}{l.items.includes(id) ? " · added" : ""}</option>)}</select></label>;
}
