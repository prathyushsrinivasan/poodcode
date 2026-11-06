/** Course progress keeps its original SQLite key. A journal contains the newest
 * complete snapshot until that exact snapshot is acknowledged by SQLite. */
export function readJlptJournal(key: string, database?: string): string | undefined {
  return localStorage.getItem(`${key}-recovery`) ?? database;
}
export function writeJlptJournal(key: string, raw: string) { localStorage.setItem(`${key}-recovery`, raw); }
export function clearJlptJournal(key: string, raw: string) {
  if (localStorage.getItem(`${key}-recovery`) === raw) localStorage.removeItem(`${key}-recovery`);
}
export function withJlptJournals(settings: Record<string, string>, keys: string[]): Record<string, string> {
  const out = { ...settings };
  for (const key of keys) {
    const raw = localStorage.getItem(`${key}-recovery`);
    if (raw !== null) out[key] = raw;
  }
  return out;
}
