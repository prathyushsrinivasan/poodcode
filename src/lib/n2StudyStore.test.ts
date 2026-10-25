import { describe, expect, it } from "vitest";
import { emptyStudy } from "./n2Study";
import { createStudyStore, type StudyStorage } from "./n2StudyStore";
function fixture() {
  let database: string | undefined; let journal: string | null = null; let fail = false;
  const writes: string[] = [];
  const storage: StudyStorage = { read: async () => database, write: async (raw) => { if (fail) throw new Error("Disk unavailable"); writes.push(raw); database = raw; }, readJournal: () => journal, writeJournal: (raw) => { journal = raw; } };
  return { storage, writes, db: () => database, journal: () => journal, fail: (v: boolean) => { fail = v; }, setDb: (v: string) => { database = v; }, setJournal: (v: string) => { journal = v; } };
}
describe("N2 durable study store", () => {
  it("serializes rapid writes and keeps the newest snapshot after remount", async () => {
    const f = fixture(); const store = createStudyStore(f.storage); await store.load();
    for (let i = 0; i < 8; i++) store.update((p) => ({ ...p, preferences: { ...p.preferences, dailyMinutes: 20 + i } }));
    expect(JSON.parse(f.journal()!).revision).toBe(8);
    await store.flush(); expect(JSON.parse(f.db()!).preferences.dailyMinutes).toBe(27); expect(f.journal()).toBeNull();
    const remount = createStudyStore(f.storage); await remount.load(); expect(remount.getSnapshot().data?.revision).toBe(8);
  });
  it("recovers a newer journal after an interrupted database write", async () => {
    const f = fixture(); f.setDb(JSON.stringify(emptyStudy()));
    f.setJournal(JSON.stringify({ ...emptyStudy(), revision: 7, bookmarks: ["read-production"] }));
    const store = createStudyStore(f.storage); await store.load();
    expect(store.getSnapshot().data?.bookmarks).toEqual(["read-production"]);
    expect(JSON.parse(f.db()!).revision).toBe(7); expect(f.journal()).toBeNull();
  });
  it("keeps unsaved changes and a recovery journal on failure, then retries", async () => {
    const f = fixture(); const store = createStudyStore(f.storage); await store.load(); f.fail(true);
    store.update((p) => ({ ...p, bookmarks: ["read-production"] })); await store.flush();
    expect(store.getSnapshot().saveError).toContain("Disk unavailable"); expect(f.journal()).not.toBeNull();
    f.fail(false); await store.retrySave(); expect(store.getSnapshot().saveError).toBe(""); expect(f.journal()).toBeNull();
    expect(JSON.parse(f.db()!).bookmarks).toEqual(["read-production"]);
  });
  it("shares one initialization across simultaneous readers", async () => {
    const f = fixture(); let reads = 0; const store = createStudyStore({ ...f.storage, read: async () => { reads++; return undefined; } });
    await Promise.all([store.load(), store.load(), store.load()]); expect(reads).toBe(1);
  });
  it("does not overwrite an unreadable or unsupported database", async () => {
    const f = fixture(); f.setDb('{"version":2}'); const store = createStudyStore(f.storage); await store.load();
    expect(store.getSnapshot().data).toBeNull(); expect(store.getSnapshot().loadError).not.toBe("");
    store.update((p) => ({ ...p, bookmarks: [] })); await store.flush(); expect(f.writes).toHaveLength(0);
  });
});
