import { emptyStudy, parseStudy, type StudyState } from "./n2Study";

export interface StudyStorage {
  read: () => Promise<string | undefined>;
  write: (raw: string) => Promise<void>;
  readJournal: () => string | null;
  writeJournal: (raw: string | null) => void;
}
export interface StudySnapshot { data: StudyState | null; loadError: string; saveError: string; saving: boolean }

/** One store per window. Serial SQLite writes plus a synchronous recovery journal
 * protect rapid edits, navigation and app closure. Never reset unreadable data. */
export function createStudyStore(storage: StudyStorage) {
  let snapshot: StudySnapshot = { data: null, loadError: "", saveError: "", saving: false };
  const listeners = new Set<() => void>();
  let loading: Promise<void> | null = null;
  let pending: Promise<void> = Promise.resolve();
  const publish = (patch: Partial<StudySnapshot>) => { snapshot = { ...snapshot, ...patch }; listeners.forEach((fn) => fn()); };
  function save(data: StudyState) {
    const raw = JSON.stringify(data);
    let journalError = "";
    try { storage.writeJournal(raw); } catch (e) { journalError = String(e); }
    publish({ saving: true });
    pending = pending.catch(() => undefined).then(() => storage.write(raw)).then(() => {
      if (snapshot.data?.revision !== data.revision) return;
      try { storage.writeJournal(null); } catch { /* A stale journal loses to the database's equal revision. */ }
      publish({ saveError: "", saving: false });
    }).catch((e) => {
      publish({ saving: false, saveError: `Database save failed: ${String(e)}${journalError ? ". Recovery journal is also unavailable; keep this window open." : ". Your latest changes are kept in a local recovery journal."}` });
    });
    return pending;
  }
  function load() {
    if (snapshot.data) return Promise.resolve();
    if (loading) return loading;
    publish({ loadError: "" });
    loading = pending.then(async () => {
      const database = parseStudy(await storage.read());
      const journalRaw = storage.readJournal();
      const journal = journalRaw ? parseStudy(journalRaw) : emptyStudy();
      const recovered = journal.revision > database.revision;
      let data = recovered ? journal : database;
      if (data.session?.mode === "learn" && data.session.phase !== "summary") {
        data = { ...data, session: { ...data.session, paused: true } };
      }
      publish({ data, loadError: "" });
      if (recovered) await save(data);
    }).catch((e) => publish({ loadError: String(e) })).finally(() => { loading = null; });
    return loading;
  }
  function update(fn: (data: StudyState) => StudyState) {
    if (!snapshot.data) return;
    const next = fn(snapshot.data);
    if (next === snapshot.data) return;
    const data = { ...next, revision: snapshot.data.revision + 1 };
    publish({ data });
    void save(data);
  }
  return { subscribe: (fn: () => void) => { listeners.add(fn); return () => { listeners.delete(fn); }; },
    getSnapshot: () => snapshot, load, update,
    retrySave: () => snapshot.data ? save(snapshot.data) : Promise.resolve(),
    flush: () => pending };
}
