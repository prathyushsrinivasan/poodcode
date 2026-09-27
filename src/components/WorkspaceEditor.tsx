// A code box that can hold several files (TS_MASTERY_ROADMAP X-45). The value
// is still one string — `// @file name.ts` markers separate the files, and the
// judge bundles them (src-tauri/src/tsbundle.rs) — but the learner sees a tab
// per file. Every file gets its own Monaco model under one folder, so the
// TypeScript service resolves `import … from "./parse"` between the tabs.

import { useEffect, useMemo, useState } from "react";
import { useMonaco } from "@monaco-editor/react";
import { CodeEditor } from "./CodeEditor";
import {
  fileNameProblem,
  joinFiles,
  splitFiles,
  toWorkspace,
  type WorkspaceFile,
} from "../lib/projectFiles";
import { useToast } from "./Toast";

export function WorkspaceEditor({
  workspaceId,
  language,
  value,
  onChange,
  onRun,
  tsStrictness,
}: {
  /** Unique per workspace; becomes the models' folder. */
  workspaceId: string;
  language: string;
  value: string;
  onChange: (v: string) => void;
  onRun?: () => void;
  tsStrictness?: string;
}) {
  const files = useMemo(() => splitFiles(value), [value]);
  const [active, setActive] = useState(0);
  const [naming, setNaming] = useState<{ mode: "add" | "rename"; text: string } | null>(null);
  const toast = useToast();
  const monaco = useMonaco();
  const folder = `file:///ws/${workspaceId.replace(/[^A-Za-z0-9_-]/g, "-")}/`;
  const index = files ? Math.min(active, files.length - 1) : 0;

  // Keep a model for every file that is not on screen, so the language service
  // sees the whole workspace; the visible one belongs to the editor.
  useEffect(() => {
    if (!monaco || !files) return;
    files.forEach((f, i) => {
      if (i === index) return;
      const uri = monaco.Uri.parse(folder + f.name);
      const model = monaco.editor.getModel(uri) ?? monaco.editor.createModel(f.content, "typescript", uri);
      if (model.getValue() !== f.content) model.setValue(f.content);
    });
  }, [monaco, files, index, folder]);

  // Drop this workspace's models when it closes, or when files go away.
  useEffect(() => {
    if (!monaco) return;
    const names = new Set((files ?? []).map((f) => folder + f.name));
    for (const m of monaco.editor.getModels()) {
      const u = m.uri.toString();
      if (u.startsWith(folder) && !names.has(u)) m.dispose();
    }
  }, [monaco, files, folder]);
  useEffect(
    () => () => {
      if (!monaco) return;
      for (const m of monaco.editor.getModels()) if (m.uri.toString().startsWith(folder)) m.dispose();
    },
    [monaco, folder]
  );

  if (!files) {
    return (
      <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
        <div style={{ flex: 1, minHeight: 0 }}>
          <CodeEditor
            language={language}
            value={value}
            onChange={onChange}
            onRun={onRun}
            tsStrictness={tsStrictness}
          />
        </div>
        {language === "typescript" && (
          <div className="workspace-tabs">
            <button
              className="ghost workspace-tab"
              title="Turn this into a workspace of several files. The judge bundles them in tab order."
              onClick={() => onChange(joinFiles(toWorkspace(value)))}
            >
              ⧉ Split into files
            </button>
          </div>
        )}
      </div>
    );
  }

  const update = (next: WorkspaceFile[]) => onChange(joinFiles(next));
  const current = files[index]!;
  const names = files.map((f) => f.name);
  const problem =
    naming === null
      ? null
      : fileNameProblem(naming.text, naming.mode === "rename" ? names.filter((_, i) => i !== index) : names);

  function commitName() {
    if (!naming || problem || !files) return;
    if (naming.mode === "add") {
      update([...files, { name: naming.text, content: "" }]);
      setActive(files.length);
    } else {
      update(files.map((f, i) => (i === index ? { ...f, name: naming.text } : f)));
    }
    setNaming(null);
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div className="workspace-tabs" role="tablist">
        {files.map((f, i) => (
          <span key={f.name} className={`workspace-tab ${i === index ? "active" : ""}`} role="tab" aria-selected={i === index}>
            <button
              className="ghost"
              onClick={() => setActive(i)}
              onDoubleClick={() => {
                setActive(i);
                setNaming({ mode: "rename", text: f.name });
              }}
              title="Double-click to rename"
            >
              {f.name}
            </button>
            {files.length > 1 && i === index && (
              <button
                className="ghost workspace-close"
                aria-label={`Delete ${f.name}`}
                title={`Delete ${f.name}`}
                onClick={() => {
                  // Undo rather than a confirm: deleting is one click to
                  // reverse, and a dialog on every close is friction (E5).
                  const before = files;
                  update(files.filter((_, k) => k !== i));
                  setActive(Math.max(0, i - 1));
                  toast(`Deleted ${f.name}.`, {
                    action: {
                      label: "Undo",
                      onClick: () => {
                        update(before);
                        setActive(i);
                      },
                    },
                  });
                }}
              >
                ×
              </button>
            )}
          </span>
        ))}
        {naming ? (
          <span className="workspace-tab">
            <input
              autoFocus
              value={naming.text}
              onChange={(e) => setNaming({ ...naming, text: e.target.value.trim() })}
              onKeyDown={(e) => {
                if (e.key === "Enter") commitName();
                if (e.key === "Escape") setNaming(null);
              }}
              onBlur={() => (problem ? setNaming(null) : commitName())}
              style={{ width: 130 }}
              aria-label={naming.mode === "add" ? "New file name" : "Rename file"}
            />
            {problem && naming.text && <span className="dim quiz-note"> {problem}</span>}
          </span>
        ) : (
          <button className="ghost workspace-tab" onClick={() => setNaming({ mode: "add", text: "utils.ts" })}>
            + file
          </button>
        )}
        <span className="dim quiz-note workspace-note">
          Judged as one program, files in tab order — sibling imports are dropped and top-level names must not repeat.
        </span>
      </div>
      <div style={{ flex: 1, minHeight: 0 }}>
        {/* One editor for every tab: switching `path` swaps its model without
            disposing the others, so the language service keeps the whole
            workspace and its diagnostics stay current. */}
        <CodeEditor
          language={language}
          path={folder + current.name}
          value={current.content}
          onChange={(v) => update(files.map((f, i) => (i === index ? { ...f, content: v } : f)))}
          onRun={onRun}
          tsStrictness={tsStrictness}
        />
      </div>
    </div>
  );
}
