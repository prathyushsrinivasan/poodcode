import { create } from "zustand";
import { api } from "./api";
import type { LangInfo } from "./types";

export interface Prefs {
  theme: "dark" | "light";
  editorTheme: string; // monaco theme id
  fontSize: number;
  tabSize: number;
  minimap: boolean;
  wordWrap: boolean;
  lineNumbers: boolean;
  defaultLanguage: string;
}

const DEFAULT_PREFS: Prefs = {
  theme: "dark",
  editorTheme: "poodcode-dark",
  fontSize: 14,
  tabSize: 4,
  minimap: true,
  wordWrap: false,
  lineNumbers: true,
  defaultLanguage: "java",
};

interface AppStore {
  prefs: Prefs;
  languages: LangInfo[];
  paletteOpen: boolean;
  loaded: boolean;
  init: () => Promise<void>;
  setPref: <K extends keyof Prefs>(key: K, value: Prefs[K]) => void;
  toggleTheme: () => void;
  setPalette: (open: boolean) => void;
}

function applyTheme(theme: "dark" | "light") {
  document.documentElement.dataset.theme = theme;
}

export const useStore = create<AppStore>((set, get) => ({
  prefs: DEFAULT_PREFS,
  languages: [],
  paletteOpen: false,
  loaded: false,

  init: async () => {
    const [settings, languages] = await Promise.all([
      api.getSettings().catch(() => ({}) as Record<string, string>),
      api.languages().catch(() => [] as LangInfo[]),
    ]);
    const prefs: Prefs = { ...DEFAULT_PREFS };
    if (settings.prefs) {
      try {
        Object.assign(prefs, JSON.parse(settings.prefs));
      } catch {
        /* ignore corrupt prefs */
      }
    }
    applyTheme(prefs.theme);
    set({ prefs, languages, loaded: true });
  },

  setPref: (key, value) => {
    const prefs = { ...get().prefs, [key]: value };
    if (key === "theme") applyTheme(value as "dark" | "light");
    set({ prefs });
    void api.setSetting("prefs", JSON.stringify(prefs));
  },

  toggleTheme: () => {
    const next = get().prefs.theme === "dark" ? "light" : "dark";
    get().setPref("theme", next);
    get().setPref("editorTheme", next === "dark" ? "poodcode-dark" : "poodcode-light");
  },

  setPalette: (open) => set({ paletteOpen: open }),
}));
