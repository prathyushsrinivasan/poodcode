// Batch TypeScript type-checker for the course verifier.
//
// Reads a JSON array of {id, src, preset} on stdin and writes a JSON array of
// {id, diagnostics:[{code, line, msg}]} on stdout.
//
// Why batch: spawning `tsc` costs ~1.5 s of start-up, and the course has 551
// exercises (1,100+ programs with starters). One process that reuses a parsed
// lib cache across every program turns a ~15-minute CI step into a ~1-minute
// one. The app's judge still spawns `tsc` per run — there it is one program at
// a time and start-up does not dominate.
//
// The compiler options here MUST stay in step with `tsconfig_json()` in
// src-tauri/src/tscheck.rs, or the verifier and the judge disagree about what
// passes. The two are checked against each other by
// `presets_match_the_rust_judge` in tools/verify_ts_course.py.

import * as fs from "fs";
import * as path from "path";
import { fileURLToPath, pathToFileURL } from "url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");
const LIB_DIR = path.join(ROOT, "node_modules/typescript/lib");
const ENV_DTS = path.join(ROOT, "src-tauri/tslib/poodcode-env.d.ts");

if (!fs.existsSync(path.join(LIB_DIR, "typescript.js"))) {
  console.error(`error: TypeScript not found at ${LIB_DIR} — run \`npm install\``);
  process.exit(2);
}
if (!fs.existsSync(ENV_DTS)) {
  console.error(`error: ambient declarations not found at ${ENV_DTS}`);
  process.exit(2);
}
const ts = (await import(pathToFileURL(path.join(LIB_DIR, "typescript.js")).href)).default;

const MAIN = "/virtual/main.ts";
const libCache = new Map();
const readLib = (f) => {
  if (!libCache.has(f)) libCache.set(f, fs.existsSync(f) ? fs.readFileSync(f, "utf8") : undefined);
  return libCache.get(f);
};
const sourceCache = new Map();

function optionsFor(preset) {
  return {
    target: ts.ScriptTarget.ES2022,
    lib: ["lib.es2022.d.ts"],
    module: ts.ModuleKind.ESNext,
    moduleResolution: ts.ModuleResolutionKind.Bundler,
    moduleDetection: ts.ModuleDetectionKind.Force,
    strict: true,
    noUncheckedIndexedAccess: preset === "strict+indexed",
    noEmit: true,
    skipLibCheck: true,
    types: [],
  };
}

function makeHost(src) {
  return {
    fileExists: (f) => f === MAIN || fs.existsSync(f),
    readFile: (f) => (f === MAIN ? src : readLib(f)),
    getSourceFile(fileName, langVersion) {
      if (fileName === MAIN) return ts.createSourceFile(fileName, src, langVersion, true);
      const key = fileName + "|" + langVersion;
      if (!sourceCache.has(key)) {
        const text = readLib(fileName);
        sourceCache.set(
          key,
          text === undefined ? undefined : ts.createSourceFile(fileName, text, langVersion, true)
        );
      }
      return sourceCache.get(key);
    },
    getDefaultLibFileName: () => path.join(LIB_DIR, "lib.es2022.d.ts"),
    getDefaultLibLocation: () => LIB_DIR,
    writeFile: () => {},
    getCurrentDirectory: () => ROOT,
    getDirectories: () => [],
    getCanonicalFileName: (f) => f.toLowerCase(),
    useCaseSensitiveFileNames: () => false,
    getNewLine: () => "\n",
  };
}

function diagnose(src, preset) {
  const program = ts.createProgram([ENV_DTS, MAIN], optionsFor(preset), makeHost(src));
  return [...program.getSyntacticDiagnostics(), ...program.getSemanticDiagnostics()]
    // Only the learner's file. A diagnostic in the ambient declarations is our
    // bug, not theirs, and must never be reported as an exercise failure.
    .filter((d) => !d.file || d.file.fileName === MAIN)
    .map((d) => ({
      code: d.code,
      line: d.file && d.start !== undefined
        ? d.file.getLineAndCharacterOfPosition(d.start).line + 1
        : 0,
      msg: ts.flattenDiagnosticMessageText(d.messageText, " "),
    }));
}

const input = await new Promise((resolve, reject) => {
  let buf = "";
  process.stdin.setEncoding("utf8");
  process.stdin.on("data", (c) => (buf += c));
  process.stdin.on("end", () => resolve(buf));
  process.stdin.on("error", reject);
});

const items = JSON.parse(input);
const out = items.map(({ id, src, preset }) => ({
  id,
  diagnostics: diagnose(src, preset || "strict"),
}));
process.stdout.write(JSON.stringify(out));
