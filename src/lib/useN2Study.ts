import { useEffect, useSyncExternalStore } from "react";
import { api } from "../api";
import { STUDY_KEY } from "./n2Study";
import { createStudyStore } from "./n2StudyStore";

export const n2StudyStore = createStudyStore({
  read: async () => (await api.getSettings())[STUDY_KEY],
  write: (raw) => api.setSetting(STUDY_KEY, raw),
  readJournal: () => localStorage.getItem(`${STUDY_KEY}-recovery`),
  writeJournal: (raw) => raw === null ? localStorage.removeItem(`${STUDY_KEY}-recovery`) : localStorage.setItem(`${STUDY_KEY}-recovery`, raw),
});
export function useN2Study() {
  const snapshot = useSyncExternalStore(n2StudyStore.subscribe, n2StudyStore.getSnapshot);
  useEffect(() => { void n2StudyStore.load(); }, []);
  return { ...snapshot, update: n2StudyStore.update, retryLoad: n2StudyStore.load, retrySave: n2StudyStore.retrySave };
}
export type N2StudyController = ReturnType<typeof useN2Study> & { data: NonNullable<ReturnType<typeof useN2Study>["data"]> };
