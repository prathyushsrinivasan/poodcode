/** Additive state. Old study snapshots acquire these defaults without changing
 * any of the separate course progress records. */
export interface VocabularyList { id: string; name: string; items: string[] }
export interface WorkspaceState {
  pagePreferences: Record<string, Record<string, string | boolean | number>>;
  lists: VocabularyList[];
  support: { readings: boolean; translations: boolean };
}
export const emptyWorkspace = (): WorkspaceState => ({ pagePreferences: {}, lists: [], support: { readings: false, translations: false } });
export function parseWorkspace(value: unknown): WorkspaceState {
  if (value === undefined) return emptyWorkspace();
  const fail = (): never => { throw new Error("JLPT workspace data cannot be read safely. Saved data has not been changed."); };
  if (!value || typeof value !== "object" || Array.isArray(value)) return fail();
  const p = value as WorkspaceState;
  if (!p.support || typeof p.support.readings !== "boolean" || typeof p.support.translations !== "boolean" || !Array.isArray(p.lists) || !p.pagePreferences || typeof p.pagePreferences !== "object" || Array.isArray(p.pagePreferences)) return fail();
  if (p.lists.length > 100 || new Set(p.lists.map((l) => l.id)).size !== p.lists.length) return fail();
  for (const l of p.lists) if (!l || typeof l.id !== "string" || !l.id || typeof l.name !== "string" || !l.name.trim() || l.name.length > 80 || !Array.isArray(l.items) || l.items.length > 5000 || !l.items.every((i) => typeof i === "string")) return fail();
  for (const prefs of Object.values(p.pagePreferences)) {
    if (!prefs || typeof prefs !== "object" || Array.isArray(prefs)) return fail();
    for (const v of Object.values(prefs)) if (!(typeof v === "boolean" || typeof v === "string" && v.length <= 4000 || typeof v === "number" && Number.isFinite(v))) return fail();
  }
  return { ...p, lists: p.lists.map((l) => ({ ...l, items: [...new Set(l.items)] })) };
}
