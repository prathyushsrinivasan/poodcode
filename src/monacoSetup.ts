// Configure Monaco to load entirely from the bundled package (no CDN) so the
// editor works fully offline, and wire up its web workers for Vite.
import * as monaco from "monaco-editor";
import { loader } from "@monaco-editor/react";

import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import tsWorker from "monaco-editor/esm/vs/language/typescript/ts.worker?worker";
import jsonWorker from "monaco-editor/esm/vs/language/json/json.worker?worker";
import cssWorker from "monaco-editor/esm/vs/language/css/css.worker?worker";
import htmlWorker from "monaco-editor/esm/vs/language/html/html.worker?worker";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
(self as any).MonacoEnvironment = {
  getWorker(_moduleId: string, label: string) {
    switch (label) {
      case "typescript":
      case "javascript":
        return new tsWorker();
      case "json":
        return new jsonWorker();
      case "css":
      case "scss":
      case "less":
        return new cssWorker();
      case "html":
      case "handlebars":
      case "razor":
        return new htmlWorker();
      default:
        return new editorWorker();
    }
  },
};

let themesDefined = false;
export function defineThemes() {
  if (themesDefined) return;
  themesDefined = true;
  monaco.editor.defineTheme("poodcode-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [],
    colors: {
      "editor.background": "#0e1116",
      "editor.lineHighlightBackground": "#161b22",
      "editorLineNumber.foreground": "#4a5563",
      "editorGutter.background": "#0e1116",
    },
  });
  monaco.editor.defineTheme("poodcode-light", {
    base: "vs",
    inherit: true,
    rules: [],
    colors: {
      "editor.background": "#ffffff",
    },
  });
}

loader.config({ monaco });

export { monaco };
