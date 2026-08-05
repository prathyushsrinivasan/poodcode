import Editor, { type OnMount } from "@monaco-editor/react";
import { forwardRef, useImperativeHandle, useRef } from "react";
import type { editor } from "monaco-editor";
import { defineThemes } from "../monacoSetup";
import { useStore } from "../store";

interface Props {
  language: string; // monaco language id
  value: string;
  onChange: (v: string) => void;
  /** Interview mode disables suggestions/autocomplete. */
  disableIntellisense?: boolean;
  readOnly?: boolean;
  onRun?: () => void;
  onSubmit?: () => void;
}

/** Imperative actions callers can trigger on the editor (format, find, replace). */
export interface CodeEditorHandle {
  format: () => void;
  find: () => void;
  replace: () => void;
}

/** Monaco wrapper honoring user editor preferences and app theme. */
export const CodeEditor = forwardRef<CodeEditorHandle, Props>(function CodeEditor(
  { language, value, onChange, disableIntellisense, readOnly, onRun, onSubmit },
  ref
) {
  const prefs = useStore((s) => s.prefs);
  const runRef = useRef(onRun);
  const submitRef = useRef(onSubmit);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  runRef.current = onRun;
  submitRef.current = onSubmit;

  useImperativeHandle(ref, () => ({
    format: () => editorRef.current?.getAction("editor.action.formatDocument")?.run(),
    find: () => editorRef.current?.getAction("actions.find")?.run(),
    replace: () =>
      editorRef.current?.getAction("editor.action.startFindReplaceAction")?.run(),
  }));

  const onMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    defineThemes();
    monaco.editor.setTheme(prefs.editorTheme);
    // Keyboard shortcuts: Ctrl/Cmd+Enter runs, Ctrl/Cmd+Shift+Enter submits.
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () =>
      runRef.current?.()
    );
    editor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Enter,
      () => submitRef.current?.()
    );
  };

  return (
    <Editor
      language={language}
      value={value}
      theme={prefs.editorTheme}
      onChange={(v) => onChange(v ?? "")}
      onMount={onMount}
      options={{
        fontSize: prefs.fontSize,
        tabSize: prefs.tabSize,
        minimap: { enabled: prefs.minimap },
        wordWrap: prefs.wordWrap ? "on" : "off",
        lineNumbers: prefs.lineNumbers ? "on" : "off",
        readOnly,
        fontFamily: "var(--font-mono)",
        smoothScrolling: true,
        cursorBlinking: "smooth",
        automaticLayout: true,
        scrollBeyondLastLine: false,
        renderWhitespace: "selection",
        quickSuggestions: !disableIntellisense,
        suggestOnTriggerCharacters: !disableIntellisense,
        parameterHints: { enabled: !disableIntellisense },
        wordBasedSuggestions: disableIntellisense ? "off" : "currentDocument",
        formatOnPaste: true,
        bracketPairColorization: { enabled: true },
      }}
    />
  );
});
