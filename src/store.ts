import { useEffect } from "react";
import { create } from "zustand";
import { api } from "./api";
import type { LangInfo } from "./types";
import { pushRecent } from "./lib/recents";

/** "system" follows the OS; the resolved value is what reaches the DOM. */
export type ThemeChoice = "dark" | "light" | "system";

export interface Prefs {
  theme: ThemeChoice;
  /** A higher-contrast variant of whichever theme is active. */
  highContrast: boolean;
  /** Root font size as a percentage, 90-125. Everything is in tokens derived
   * from rem, so this scales the whole interface rather than just the text. */
  uiScale: number;
  /** Row and list padding. "compact" fits roughly a third more on screen. */
  density: "comfortable" | "compact";
  editorTheme: string; // monaco theme id
  fontSize: number;
  tabSize: number;
  minimap: boolean;
  wordWrap: boolean;
  lineNumbers: boolean;
  defaultLanguage: string;
  /** Icon-only sidebar. Remembered, and forced on for editor pages. */
  sidebarCollapsed: boolean;
}

const DEFAULT_PREFS: Prefs = {
  theme: "dark",
  highContrast: false,
  uiScale: 100,
  density: "comfortable",
  editorTheme: "poodcode-dark",
  fontSize: 14,
  tabSize: 4,
  // Off by default: Solve splits the window in two, so the editor is often
  // 370-600px wide and the minimap was spending ~80px of it on a thumbnail of
  // a file that fits on screen anyway.
  minimap: false,
  wordWrap: false,
  lineNumbers: true,
  defaultLanguage: "java",
  sidebarCollapsed: false,
};

interface AppStore {
  prefs: Prefs;
  languages: LangInfo[];
  paletteOpen: boolean;
  loaded: boolean;
  /** The real name of the page you are on, for the breadcrumb's last crumb.
   * Pages set it once their own data lands; the router only knows the id. */
  crumbLabel: string | null;
  /** A transient override of `prefs.sidebarCollapsed`, set by editor pages.
   * Kept out of `prefs` on purpose: borrowing the sidebar for Solve must not
   * overwrite what the user chose for everywhere else. */
  sidebarAuto: boolean | null;
  /** `sidebarAuto` when set, otherwise the saved preference. */
  sidebarCollapsed: () => boolean;
  setSidebarAuto: (v: boolean | null) => void;
  init: () => Promise<void>;
  setPref: <K extends keyof Prefs>(key: K, value: Prefs[K]) => void;
  toggleTheme: () => void;
  /** dark or light, with "system" already resolved. */
  resolvedTheme: () => "dark" | "light";
  setPalette: (open: boolean) => void;
  toggleSidebar: () => void;
  setCrumbLabel: (label: string | null) => void;
  /** Re-probe the toolchains and refresh `languages`. Resolves to how many
   * are installed, so the caller can say what changed. */
  redetectLanguages: () => Promise<number>;
}

const systemDark = () =>
  typeof window !== "undefined" &&
  window.matchMedia &&
  window.matchMedia("(prefers-color-scheme: dark)").matches;

export function resolveTheme(choice: ThemeChoice): "dark" | "light" {
  if (choice !== "system") return choice;
  return systemDark() ? "dark" : "light";
}

/** Push the whole appearance onto the root element in one place, so nothing
 * reads a preference and styles itself. */
function applyAppearance(prefs: Prefs) {
  const root = document.documentElement;
  root.dataset.theme = resolveTheme(prefs.theme);
  if (prefs.highContrast) root.dataset.contrast = "high";
  else delete root.dataset.contrast;
  root.dataset.density = prefs.density;
  // 100% => 14px, matching the body size the tokens were designed against.
  root.style.fontSize = `${(prefs.uiScale / 100) * 14}px`;
}

export const useStore = create<AppStore>((set, get) => ({
  prefs: DEFAULT_PREFS,
  languages: [],
  paletteOpen: false,
  loaded: false,
  crumbLabel: null,
  sidebarAuto: null,

  init: async () => {
    // Guarded: React StrictMode invokes mount effects twice in development, and
    // a second `set({ prefs })` landing after the UI has already changed a
    // preference would silently discard that change.
    if (get().loaded) return;
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
    applyAppearance(prefs);
    set({ prefs, languages, loaded: true });

    // Following the system means following it as it changes, not only at boot.
    if (window.matchMedia) {
      window
        .matchMedia("(prefers-color-scheme: dark)")
        .addEventListener("change", () => {
          const current = get().prefs;
          if (current.theme === "system") applyAppearance(current);
        });
    }
  },

  setPref: (key, value) => {
    const prefs = { ...get().prefs, [key]: value };
    applyAppearance(prefs);
    set({ prefs });
    void api.setSetting("prefs", JSON.stringify(prefs));
  },

  resolvedTheme: () => resolveTheme(get().prefs.theme),

  // The quick toggle steps dark → light → dark. Choosing "system" is a
  // deliberate act, so it lives in Settings rather than in the cycle.
  //
  // The editor theme is no longer dragged along: it is an independent choice
  // (UI_ROADMAP C8), and only follows when it is still on the app default for
  // the theme being left.
  toggleTheme: () => {
    const prefs = get().prefs;
    const from = resolveTheme(prefs.theme);
    const next = from === "dark" ? "light" : "dark";
    get().setPref("theme", next);
    if (prefs.editorTheme === `poodcode-${from}`) {
      get().setPref("editorTheme", `poodcode-${next}`);
    }
  },

  setPalette: (open) => set({ paletteOpen: open }),

  sidebarCollapsed: () => get().sidebarAuto ?? get().prefs.sidebarCollapsed,

  setSidebarAuto: (sidebarAuto) => set({ sidebarAuto }),

  // An explicit toggle is a decision about everywhere, so it drops whatever a
  // page had borrowed and writes the preference.
  toggleSidebar: () => {
    const next = !get().sidebarCollapsed();
    set({ sidebarAuto: null });
    get().setPref("sidebarCollapsed", next);
  },

  setCrumbLabel: (crumbLabel) => set({ crumbLabel }),

  redetectLanguages: async () => {
    const languages = await api.redetectLanguages();
    set({ languages });
    return languages.filter((l) => l.installed).length;
  },
}));

/** Name the current page for the breadcrumb, and clear the name on the way out
 * so the next page never inherits the last one's title.
 *
 * A page that knows its own name is also a page worth offering again, so the
 * same call records it in the palette's "Recent" list. Pass `hint` for the
 * one-line context shown beside it there. */
export function useCrumb(label: string | null | undefined, hint?: string) {
  const setCrumbLabel = useStore((s) => s.setCrumbLabel);
  useEffect(() => {
    setCrumbLabel(label ?? null);
    if (label) {
      pushRecent({
        // The hash is the app's address; strip it back to a router path.
        to: window.location.hash.replace(/^#/, "") || "/",
        label,
        hint,
      });
    }
    return () => setCrumbLabel(null);
  }, [label, hint, setCrumbLabel]);
}
