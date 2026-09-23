// Configure Monaco to load entirely from the bundled package (no CDN) so the
// editor works fully offline, and wire up its web workers for Vite.
import * as monaco from "monaco-editor";
import { loader } from "@monaco-editor/react";

import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import tsWorker from "monaco-editor/esm/vs/language/typescript/ts.worker?worker";
import jsonWorker from "monaco-editor/esm/vs/language/json/json.worker?worker";
import cssWorker from "monaco-editor/esm/vs/language/css/css.worker?worker";
import htmlWorker from "monaco-editor/esm/vs/language/html/html.worker?worker";
// The judge's own ambient declarations (`fs`, `console`, `setTimeout`, …), so
// the editor and the judge resolve exactly the same host API.
import poodcodeEnvDts from "../src-tauri/tslib/poodcode-env.d.ts?raw";

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

// ---------------------------------------------------------------------------
// TypeScript: make the editor agree with the judge.
//
// The judge type-checks every TypeScript run at `--strict` against a small
// hand-written stand-in for @types/node (src-tauri/src/tscheck.rs). Monaco's
// defaults are the opposite on both counts — non-strict, with the DOM lib and
// no `fs` — so out of the box the editor underlined `import * as fs from "fs"`
// (which the judge accepts) and stayed silent about implicit `any` parameters
// (which the judge rejects). These options mirror `tsconfig_json()` in
// tscheck.rs and `optionsFor()` in tools/ts_typecheck.mjs, and load the same
// ambient declarations, so a red squiggle means what a failed run would mean,
// and hovering a name shows the type the judge will see.
//
// One known gap: Monaco bundles TypeScript 5.4 and the judge runs 5.9, so a
// few newer inferences (e.g. `filter` inferring a type predicate, 5.5) pass
// the judge while the editor still flags them.
// ---------------------------------------------------------------------------

const tsLang = monaco.languages.typescript;

/** Mirrors the judge's presets: "" / "strict", or "strict+indexed". */
function judgeCompilerOptions(strictness: string) {
  return {
    target: 9, // ES2022 — not in Monaco's ScriptTarget enum, but TS accepts it
    // The judge's list (tscheck.rs). Monaco's bundled 5.4 predates the iterator
    // helpers and the ES2025 Set methods, so those two stay unsquiggled-but-
    // unknown in the editor; the judge still checks them.
    lib: [
      "lib.es2024.d.ts",
      "lib.esnext.array.d.ts",
      "lib.esnext.collection.d.ts",
      "lib.esnext.iterator.d.ts",
      "lib.esnext.disposable.d.ts",
      "lib.esnext.promise.d.ts",
    ],
    module: tsLang.ModuleKind.ESNext,
    moduleResolution: tsLang.ModuleResolutionKind.NodeJs,
    // Every editor is its own module, so two open editors that both declare
    // `function solve` do not collide in one shared global scope.
    moduleDetection: 3, // ts.ModuleDetectionKind.Force
    strict: true,
    noUncheckedIndexedAccess: strictness === "strict+indexed",
    noEmit: true,
    allowNonTsExtensions: true,
    types: [],
  };
}

let appliedStrictness: string | null = null;

/** Point the TypeScript service at a strictness preset. The service is global
 * to the page, so the editor that has focus decides; switching is cheap and a
 * no-op when nothing changes. */
export function setTypeScriptStrictness(strictness = "") {
  const preset = strictness || "strict";
  if (preset === appliedStrictness) return;
  appliedStrictness = preset;
  tsLang.typescriptDefaults.setCompilerOptions(judgeCompilerOptions(preset));
}

tsLang.typescriptDefaults.addExtraLib(poodcodeEnvDts, "file:///poodcode-env.d.ts");
setTypeScriptStrictness("strict");

loader.config({ monaco });

export { monaco };
