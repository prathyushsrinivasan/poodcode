import { useEffect, useState } from "react";
import { open as openDialog, save as saveDialog } from "@tauri-apps/plugin-dialog";
import { useStore } from "../store";
import { api } from "../api";
import { useToast } from "../components/Toast";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="row" style={{ padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
      <span>{label}</span>
      <span className="spacer" />
      {children}
    </div>
  );
}

export default function Settings() {
  const { prefs, setPref, toggleTheme, languages } = useStore();
  const toast = useToast();
  const [goals, setGoals] = useState({ intro: 3, easy: 2, medium: 1, hard: 0, reviews: 3 });

  useEffect(() => {
    api.getSettings().then((s) => {
      setGoals({
        intro: Number(s.goal_intro ?? 3),
        easy: Number(s.goal_easy ?? 2),
        medium: Number(s.goal_medium ?? 1),
        hard: Number(s.goal_hard ?? 0),
        reviews: Number(s.goal_reviews ?? 3),
      });
    });
  }, []);

  const saveGoal = (key: keyof typeof goals, value: number) => {
    setGoals((g) => ({ ...g, [key]: value }));
    api.setSetting(`goal_${key}`, String(value));
  };

  const doBackup = async () => {
    const stamp = new Date().toISOString().slice(0, 10);
    const path = await saveDialog({
      defaultPath: `poodcode-backup-${stamp}.sqlite`,
      filters: [{ name: "SQLite database", extensions: ["sqlite", "db"] }],
    });
    if (!path) return;
    try {
      await api.backupDatabase(path);
      toast("Backup written — everything (problems, notes, attempts, drafts, schedule).");
    } catch (e) {
      toast(`Backup failed: ${e}`);
    }
  };

  const doRestore = async () => {
    const ok = window.confirm(
      "Restore will REPLACE your current database with the chosen backup. This cannot be undone. Continue?"
    );
    if (!ok) return;
    const path = await openDialog({
      filters: [{ name: "SQLite database", extensions: ["sqlite", "db"] }],
    });
    if (typeof path !== "string") return;
    try {
      await api.restoreDatabase(path);
      toast("Database restored — reloading…");
      setTimeout(() => window.location.reload(), 600);
    } catch (e) {
      toast(`Restore failed: ${e}`);
    }
  };

  return (
    <div className="page">
      <h1 className="page-title">Settings</h1>
      <p className="page-sub">Everything is stored locally. No account, no cloud.</p>

      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ marginTop: 0 }}>Appearance</h3>
        <Field label="Theme">
          <button onClick={toggleTheme}>{prefs.theme === "dark" ? "🌙 Dark" : "☀️ Light"}</button>
        </Field>
        <Field label="Editor font size">
          <input
            type="number"
            min={10}
            max={28}
            style={{ width: 80 }}
            value={prefs.fontSize}
            onChange={(e) => setPref("fontSize", Number(e.target.value))}
          />
        </Field>
        <Field label="Tab size">
          <input type="number" min={2} max={8} style={{ width: 80 }} value={prefs.tabSize} onChange={(e) => setPref("tabSize", Number(e.target.value))} />
        </Field>
        <Field label="Minimap">
          <input type="checkbox" checked={prefs.minimap} onChange={(e) => setPref("minimap", e.target.checked)} />
        </Field>
        <Field label="Word wrap">
          <input type="checkbox" checked={prefs.wordWrap} onChange={(e) => setPref("wordWrap", e.target.checked)} />
        </Field>
        <Field label="Line numbers">
          <input type="checkbox" checked={prefs.lineNumbers} onChange={(e) => setPref("lineNumbers", e.target.checked)} />
        </Field>
        <Field label="Default language">
          <select value={prefs.defaultLanguage} onChange={(e) => setPref("defaultLanguage", e.target.value)}>
            {languages.map((l) => (
              <option key={l.id} value={l.id}>{l.label}</option>
            ))}
          </select>
        </Field>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ marginTop: 0 }}>Daily goals</h3>
        {(["intro", "easy", "medium", "hard", "reviews"] as const).map((k) => (
          <Field key={k} label={k[0].toUpperCase() + k.slice(1)}>
            <input type="number" min={0} max={20} style={{ width: 80 }} value={goals[k]} onChange={(e) => saveGoal(k, Number(e.target.value))} />
          </Field>
        ))}
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ marginTop: 0 }}>Backup &amp; restore</h3>
        <p className="dim" style={{ marginTop: 0 }}>
          A backup is a single-file snapshot of your entire database — problems, notes, attempts,
          solutions, drafts, review schedule, and settings. Keep one somewhere safe.
        </p>
        <div className="row">
          <button className="primary" onClick={doBackup}>
            ⬇ Back up database…
          </button>
          <button onClick={doRestore}>⬆ Restore from backup…</button>
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Toolchains detected</h3>
        <p className="dim">Languages available for code execution on this machine.</p>
        <div className="tag-row">
          {languages.map((l) => (
            <span
              key={l.id}
              className="badge"
              title={l.installed ? "Installed" : l.install_hint}
              style={{ borderColor: l.installed ? "var(--good)" : "var(--border)", color: l.installed ? "var(--good)" : "var(--text-faint)" }}
            >
              {l.installed ? "✓" : "○"} {l.label}
            </span>
          ))}
        </div>
        <p className="faint" style={{ fontSize: 12, marginTop: 10 }}>
          Not-installed languages activate automatically once their compiler/runtime is on your PATH and the app restarts. — <span onClick={() => toast("Restart the app to re-detect toolchains.")} style={{ cursor: "pointer", textDecoration: "underline" }}>re-detect</span>
        </p>
      </div>
    </div>
  );
}
