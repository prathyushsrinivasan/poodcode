/**
 * Settings, in sections.
 *
 * It was one flat page of five cards with no way to find anything in it, and
 * two of its controls did not do what they said: "re-detect" was a `span` that
 * toasted "restart the app", and "show the welcome again" cleared a flag and
 * reloaded the whole application. There was also nowhere to look up the app
 * version, where the database lives, or what any keyboard shortcut is.
 *
 * Now there is a section rail, a search that filters across every section, and
 * the appearance controls the roadmap asked for: follow-the-system theme, a
 * high-contrast variant, an independent editor theme, interface scale and
 * density (C8/C11), plus goals per track (K5) and an About section (K4).
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { open as openDialog, save as saveDialog } from "@tauri-apps/plugin-dialog";
import { useStore } from "../store";
import { api } from "../api";
import { useToast } from "../components/Toast";
import { ConfirmDialog } from "../components/ui/Modal";
import { SHORTCUTS, Keys } from "../components/shell/ShortcutSheet";

/** One labelled control. `keywords` feed the section search. */
function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="setting-row">
      <div className="setting-label">
        <span>{label}</span>
        {hint && <span className="faint setting-hint">{hint}</span>}
      </div>
      <div className="setting-control">{children}</div>
    </div>
  );
}

function Toggle({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  label: string;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      className={`toggle ${checked ? "on" : ""}`}
      onClick={() => onChange(!checked)}
    >
      <span className="toggle-knob" aria-hidden />
    </button>
  );
}

/** A segmented choice — clearer than a select for two or three options. */
function Segmented<T extends string>({
  value,
  options,
  onChange,
  label,
}: {
  value: T;
  options: { value: T; label: string }[];
  onChange: (v: T) => void;
  label: string;
}) {
  return (
    <div className="pill-toggle" role="group" aria-label={label}>
      {options.map((o) => (
        <button
          key={o.value}
          className={`pill ${value === o.value ? "on" : ""}`}
          aria-pressed={value === o.value}
          onClick={() => onChange(o.value)}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

const SECTIONS = [
  { id: "appearance", label: "Appearance", icon: "🎨" },
  { id: "editor", label: "Editor", icon: "⌨️" },
  { id: "goals", label: "Goals", icon: "🎯" },
  { id: "data", label: "Data", icon: "💾" },
  { id: "toolchains", label: "Toolchains", icon: "🔧" },
  { id: "shortcuts", label: "Shortcuts", icon: "⇧" },
  { id: "about", label: "About", icon: "ℹ️" },
] as const;

type SectionId = (typeof SECTIONS)[number]["id"];

const EDITOR_THEMES = [
  { id: "poodcode-dark", label: "Poodcode Dark" },
  { id: "poodcode-light", label: "Poodcode Light" },
  { id: "vs-dark", label: "VS Dark" },
  { id: "vs", label: "VS Light" },
  { id: "hc-black", label: "High Contrast Black" },
];

export default function Settings() {
  const { prefs, setPref, languages, redetectLanguages } = useStore();
  const toast = useToast();
  const [redetecting, setRedetecting] = useState(false);
  const [goals, setGoals] = useState({
    intro: 3,
    easy: 2,
    medium: 1,
    hard: 0,
    reviews: 3,
    weeks: 0,
    units: 0,
    cards: 0,
  });
  const [confirmRestore, setConfirmRestore] = useState(false);
  const [restoring, setRestoring] = useState(false);
  const [active, setActive] = useState<SectionId>("appearance");
  const [query, setQuery] = useState("");
  const bodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.getSettings().then((s) => {
      const n = (k: string, d: number) => Number(s[k] ?? d);
      setGoals({
        intro: n("goal_intro", 3),
        easy: n("goal_easy", 2),
        medium: n("goal_medium", 1),
        hard: n("goal_hard", 0),
        reviews: n("goal_reviews", 3),
        weeks: n("goal_weeks", 0),
        units: n("goal_units", 0),
        cards: n("goal_cards", 0),
      });
    });
  }, []);

  const saveGoal = (key: keyof typeof goals, value: number) => {
    setGoals((g) => ({ ...g, [key]: value }));
    api.setSetting(`goal_${key}`, String(value)).catch((e) =>
      toast.error("Could not save that target", { detail: String(e) })
    );
  };

  const doBackup = async () => {
    const stamp = new Date().toISOString().slice(0, 10);
    const path = await saveDialog({
      defaultPath: `poodcode-backup-${stamp}.sqlite`,
      filters: [{ name: "SQLite database", extensions: ["sqlite", "db"] }],
    });
    if (!path) return false;
    try {
      await api.backupDatabase(path);
      toast.success("Backup written", {
        detail: "Problems, notes, attempts, drafts and the review schedule are all in the file.",
      });
      return true;
    } catch (e) {
      toast.error("Backup failed", { detail: String(e) });
      return false;
    }
  };

  /** The confirmed half of Restore. Everything destructive happens here, after
   * the dialog; `doBackup` is offered alongside it so the current database can
   * be saved without losing the thread. */
  const doRestore = async () => {
    setRestoring(true);
    try {
      const path = await openDialog({
        filters: [{ name: "SQLite database", extensions: ["sqlite", "db"] }],
      });
      if (typeof path !== "string") return;
      await api.restoreDatabase(path);
      setConfirmRestore(false);
      toast.success("Database restored — reloading…");
      setTimeout(() => window.location.reload(), 600);
    } catch (e) {
      toast.error("Restore failed", {
        detail: String(e) + "\n\nYour current database has not been changed.",
      });
    } finally {
      setRestoring(false);
    }
  };

  // Searching jumps to whichever section matches rather than filtering rows in
  // place, so the page never shows a section with one orphaned control in it.
  const matches = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return null;
    const text: Record<SectionId, string> = {
      appearance: "theme dark light system high contrast accent interface size scale density compact comfortable appearance colour color",
      editor: "editor font size tab minimap word wrap line numbers language monaco theme default language",
      goals: "daily goals intro easy medium hard reviews curriculum units course weeks vocabulary cards targets streak",
      data: "backup restore database export import data sqlite file",
      toolchains: "toolchain compiler runtime java python typescript node detect install path",
      shortcuts: "keyboard shortcuts keys palette back forward run submit",
      about: "about version seed database location build",
    };
    return SECTIONS.filter((s) => (s.label + " " + text[s.id]).toLowerCase().includes(q)).map(
      (s) => s.id
    );
  }, [query]);

  const visible = matches ?? [active];

  const show = (id: SectionId) => visible.includes(id);

  return (
    <div className="page settings-page">
      <h1 className="page-title">Settings</h1>
      <p className="page-sub">Everything is stored locally. No account, no cloud.</p>

      <div className="settings-layout">
        <nav className="settings-rail" aria-label="Settings sections">
          <input
            className="settings-search"
            type="search"
            placeholder="Search settings…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Search settings"
          />
          {SECTIONS.map((s) => (
            <button
              key={s.id}
              className={`settings-rail-item ${!query && active === s.id ? "active" : ""} ${
                matches && !matches.includes(s.id) ? "dimmed" : ""
              }`}
              onClick={() => {
                setQuery("");
                setActive(s.id);
                bodyRef.current?.scrollTo({ top: 0 });
              }}
            >
              <span aria-hidden>{s.icon}</span>
              {s.label}
            </button>
          ))}
        </nav>

        <div className="settings-body" ref={bodyRef}>
          {matches?.length === 0 && (
            <div className="card empty-state">
              <p>Nothing in settings matches “{query}”.</p>
              <button onClick={() => setQuery("")}>Clear search</button>
            </div>
          )}

          {/* ---- Appearance ---- */}
          {show("appearance") && (
            <section className="card" aria-labelledby="s-appearance">
              <h2 id="s-appearance" className="card-title">
                Appearance
              </h2>
              <Field label="Theme" hint="“System” follows your OS setting as it changes.">
                <Segmented
                  label="Theme"
                  value={prefs.theme}
                  onChange={(v) => setPref("theme", v)}
                  options={[
                    { value: "dark", label: "🌙 Dark" },
                    { value: "light", label: "☀️ Light" },
                    { value: "system", label: "🖥 System" },
                  ]}
                />
              </Field>
              <Field
                label="High contrast"
                hint="Stronger text and visible borders, in whichever theme is active."
              >
                <Toggle
                  label="High contrast"
                  checked={prefs.highContrast}
                  onChange={(v) => setPref("highContrast", v)}
                />
              </Field>
              <Field label="Interface size" hint={`${prefs.uiScale}% — scales the whole app.`}>
                <input
                  type="range"
                  min={90}
                  max={125}
                  step={5}
                  value={prefs.uiScale}
                  onChange={(e) => setPref("uiScale", Number(e.target.value))}
                  aria-label="Interface size percentage"
                />
              </Field>
              <Field label="Density" hint="Compact tightens rows and lists.">
                <Segmented
                  label="Density"
                  value={prefs.density}
                  onChange={(v) => setPref("density", v)}
                  options={[
                    { value: "comfortable", label: "Comfortable" },
                    { value: "compact", label: "Compact" },
                  ]}
                />
              </Field>
              <Field label="Welcome tour">
                <button onClick={() => window.dispatchEvent(new Event("poodcode:show-welcome"))}>
                  ↻ Show again
                </button>
              </Field>
            </section>
          )}

          {/* ---- Editor ---- */}
          {show("editor") && (
            <section className="card" aria-labelledby="s-editor">
              <h2 id="s-editor" className="card-title">
                Editor
              </h2>
              <Field
                label="Editor theme"
                hint="Independent of the app theme — a light app with a dark editor is fine."
              >
                <select
                  value={prefs.editorTheme}
                  onChange={(e) => setPref("editorTheme", e.target.value)}
                >
                  {EDITOR_THEMES.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label="Font size">
                <input
                  type="number"
                  min={10}
                  max={28}
                  value={prefs.fontSize}
                  onChange={(e) => setPref("fontSize", Number(e.target.value))}
                />
              </Field>
              <Field label="Tab size">
                <input
                  type="number"
                  min={2}
                  max={8}
                  value={prefs.tabSize}
                  onChange={(e) => setPref("tabSize", Number(e.target.value))}
                />
              </Field>
              <Field label="Minimap" hint="Off by default — the Solve editor is a half-width pane.">
                <Toggle
                  label="Minimap"
                  checked={prefs.minimap}
                  onChange={(v) => setPref("minimap", v)}
                />
              </Field>
              <Field label="Word wrap">
                <Toggle
                  label="Word wrap"
                  checked={prefs.wordWrap}
                  onChange={(v) => setPref("wordWrap", v)}
                />
              </Field>
              <Field label="Line numbers">
                <Toggle
                  label="Line numbers"
                  checked={prefs.lineNumbers}
                  onChange={(v) => setPref("lineNumbers", v)}
                />
              </Field>
              <Field label="Default language">
                <select
                  value={prefs.defaultLanguage}
                  onChange={(e) => setPref("defaultLanguage", e.target.value)}
                >
                  {languages.map((l) => (
                    <option key={l.id} value={l.id}>
                      {l.label}
                    </option>
                  ))}
                </select>
              </Field>
            </section>
          )}

          {/* ---- Goals ---- */}
          {show("goals") && (
            <section className="card" aria-labelledby="s-goals">
              <h2 id="s-goals" className="card-title">
                Daily goals
              </h2>
              <p className="dim card-intro">
                What Today measures you against. Set a target to 0 to hide it.
              </p>
              {(
                [
                  ["intro", "Intro problems"],
                  ["easy", "Easy problems"],
                  ["medium", "Medium problems"],
                  ["hard", "Hard problems"],
                  ["reviews", "Curriculum reviews"],
                ] as const
              ).map(([k, label]) => (
                <Field key={k} label={label}>
                  <input
                    type="number"
                    min={0}
                    max={20}
                    value={goals[k]}
                    onChange={(e) => saveGoal(k, Number(e.target.value))}
                  />
                </Field>
              ))}

              <h3 className="settings-subhead">Per track</h3>
              <p className="dim card-intro">
                Daily goals only knew problem difficulties. These cover the rest of the app.
              </p>
              <Field label="Course units per week">
                <input
                  type="number"
                  min={0}
                  max={14}
                  value={goals.weeks}
                  onChange={(e) => saveGoal("weeks", Number(e.target.value))}
                />
              </Field>
              <Field label="Curriculum units per week">
                <input
                  type="number"
                  min={0}
                  max={14}
                  value={goals.units}
                  onChange={(e) => saveGoal("units", Number(e.target.value))}
                />
              </Field>
              <Field label="日本語 cards per day">
                <input
                  type="number"
                  min={0}
                  max={100}
                  value={goals.cards}
                  onChange={(e) => saveGoal("cards", Number(e.target.value))}
                />
              </Field>
            </section>
          )}

          {/* ---- Data ---- */}
          {show("data") && (
            <section className="card" aria-labelledby="s-data">
              <h2 id="s-data" className="card-title">
                Backup &amp; restore
              </h2>
              <p className="dim card-intro">
                A backup is a single-file snapshot of your entire database — problems, notes,
                attempts, solutions, drafts, review schedule and settings. Keep one somewhere safe.
              </p>
              <div className="row">
                <button className="primary" onClick={doBackup}>
                  ⬇ Back up database…
                </button>
                <button onClick={() => setConfirmRestore(true)}>⬆ Restore from backup…</button>
              </div>
            </section>
          )}

          {/* ---- Toolchains ---- */}
          {show("toolchains") && (
            <section className="card" aria-labelledby="s-tool">
              <h2 id="s-tool" className="card-title">
                Toolchains detected
              </h2>
              <p className="dim card-intro">
                Languages available for code execution on this machine.
              </p>
              <div className="tag-row">
                {languages.map((l) => (
                  <span
                    key={l.id}
                    className={`badge toolchain ${l.installed ? "on" : ""}`}
                    title={l.installed ? "Installed" : l.install_hint}
                  >
                    {l.installed ? "✓" : "○"} {l.label}
                  </span>
                ))}
              </div>
              <p className="faint settings-note">
                Install a compiler or runtime and put it on your PATH, then re-detect — no restart
                needed.{" "}
                <button
                  className="ghost link-button"
                  disabled={redetecting}
                  onClick={async () => {
                    setRedetecting(true);
                    try {
                      const n = await redetectLanguages();
                      toast.success(`Re-detected toolchains — ${n} installed.`);
                    } catch (e) {
                      toast.error("Could not re-detect toolchains", { detail: String(e) });
                    } finally {
                      setRedetecting(false);
                    }
                  }}
                >
                  {redetecting ? "Checking…" : "Re-detect now"}
                </button>
              </p>
            </section>
          )}

          {/* ---- Shortcuts ---- */}
          {show("shortcuts") && (
            <section className="card" aria-labelledby="s-keys">
              <h2 id="s-keys" className="card-title">
                Keyboard shortcuts
              </h2>
              <p className="dim card-intro">
                Press <span className="kbd">?</span> anywhere to bring this up as a sheet.
              </p>
              {SHORTCUTS.map((g) => (
                <div key={g.group} className="settings-keys">
                  <h3 className="settings-subhead">{g.group}</h3>
                  <table className="shortcut-table">
                    <tbody>
                      {g.items.map((sc) => (
                        <tr key={sc.what + sc.keys.join()}>
                          <td className="shortcut-keys">
                            <Keys keys={sc.keys} />
                          </td>
                          <td>{sc.what}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}
            </section>
          )}

          {/* ---- About ---- */}
          {show("about") && <About />}
        </div>
      </div>

      <ConfirmDialog
        open={confirmRestore}
        onClose={() => setConfirmRestore(false)}
        onConfirm={doRestore}
        busy={restoring}
        title="Restore from a backup?"
        consequence={
          <>
            This <strong>replaces your current database</strong> with the one in the file you pick —
            every problem, note, attempt, draft and review date in it now. It cannot be undone. Back
            up first if you are not sure.
          </>
        }
        confirmLabel="Choose a file and restore"
        extraAction={{ label: "Back up first", onClick: doBackup }}
      />
    </div>
  );
}

/** Version, content counts and where the data lives — none of which had a home
 * anywhere in the app before (UI_ROADMAP K4). */
function About() {
  const [counts, setCounts] = useState<{ problems: number; concepts: number } | null>(null);

  useEffect(() => {
    Promise.all([api.listProblems(), api.concepts()])
      .then(([p, c]) => setCounts({ problems: p.length, concepts: c.length }))
      .catch(() => setCounts(null));
  }, []);

  return (
    <section className="card" aria-labelledby="s-about">
      <h2 id="s-about" className="card-title">
        About Poodcode
      </h2>
      <Field label="Version">
        <span className="mono">{__APP_VERSION__}</span>
      </Field>
      <Field label="Problems in the bank">
        <span className="mono">{counts ? counts.problems : "…"}</span>
      </Field>
      <Field label="Concepts in Learn">
        <span className="mono">{counts ? counts.concepts : "…"}</span>
      </Field>
      <Field label="Database" hint="A single SQLite file in the app's data directory.">
        <span className="mono faint">poodcode.sqlite</span>
      </Field>
      <p className="faint settings-note">
        Everything runs offline: your code is executed by the toolchains on this machine and nothing
        is sent anywhere. Back up the database from time to time — it is the only copy.
      </p>
    </section>
  );
}
