// Generate real TypeScript starters for the Problem Library.
//
// Until this existed, every Library problem's TypeScript starter was its
// JavaScript starter copied verbatim ("plain JS is valid TS"). It is not — not
// under the judge, which type-checks every TypeScript run at `--strict` before
// executing it (src-tauri/src/tscheck.rs). All 607 copied starters failed that
// check before the learner typed a character: `require` is undeclared (TS2591),
// every parameter is an implicit `any` (TS7006), and the node classes assign
// fields they never declare (TS2339).
//
// This script converts each JavaScript starter into TypeScript that compiles:
//
//   1. `require('fs')` becomes `import * as fs from "fs"` — the one import the
//      judge's ambient declarations (tslib/poodcode-env.d.ts) support.
//   2. The handful of node classes (TreeNode, ListNode, the three `Node`s) are
//      swapped for hand-typed versions with declared, nullable fields.
//   3. TypeScript's own "Infer types from usage" code fix annotates every
//      remaining implicit `any` from how the value is used — the same fix the
//      editor offers, applied across the whole file.
//   4. Every function and method gets an explicit return type, taken from the
//      checker's inferred signature, so the starter documents its contract.
//
// Each result is then type-checked with the judge's exact options. Anything that
// still has diagnostics is reported and NOT written — a starter that fails the
// judge is worse than no starter.
//
// Output: tools/ts_starters.json — { slug: { js_sha, ts } }. `js_sha` pins the
// JavaScript starter it was converted from; gen_seed.py uses the TypeScript
// version only while that hash still matches, so an edited JS starter can never
// silently ship a stale TypeScript one.
//
// Usage: node tools/gen_ts_starters.mjs            (reads src-tauri/seeds/problems.json)

import * as fs from "fs";
import * as path from "path";
import * as crypto from "crypto";
import { fileURLToPath, pathToFileURL } from "url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");
const LIB_DIR = path.join(ROOT, "node_modules/typescript/lib");
const ENV_DTS = path.join(ROOT, "src-tauri/tslib/poodcode-env.d.ts");
const SEED = path.join(ROOT, "src-tauri/seeds/problems.json");
const OUT = path.join(HERE, "ts_starters.json");

const ts = (await import(pathToFileURL(path.join(LIB_DIR, "typescript.js")).href)).default;

// Must match optionsFor("strict") in tools/ts_typecheck.mjs and tsconfig_json()
// in src-tauri/src/tscheck.rs.
const OPTIONS = {
  target: ts.ScriptTarget.ES2022,
  lib: ["lib.es2022.d.ts"],
  module: ts.ModuleKind.ESNext,
  moduleResolution: ts.ModuleResolutionKind.Bundler,
  moduleDetection: ts.ModuleDetectionKind.Force,
  strict: true,
  noEmit: true,
  skipLibCheck: true,
  types: [],
};

export function sha(text) {
  return crypto.createHash("sha256").update(text, "utf8").digest("hex").slice(0, 16);
}

// ---------------------------------------------------------------------------
// Step 1 + 2: textual rewrites
// ---------------------------------------------------------------------------

const NODE_CLASSES = [
  [
    /^class TreeNode \{ constructor\(val\) \{ this\.val = val; this\.left = null; this\.right = null; \} \}$/m,
    "class TreeNode {\n  val: number;\n  left: TreeNode | null = null;\n  right: TreeNode | null = null;\n  constructor(val: number) { this.val = val; }\n}",
  ],
  [
    /^class ListNode \{ constructor\(val, next = null\) \{ this\.val = val; this\.next = next; \} \}$/m,
    "class ListNode {\n  val: number;\n  next: ListNode | null;\n  constructor(val: number, next: ListNode | null = null) { this.val = val; this.next = next; }\n}",
  ],
  [
    /^class Node \{ constructor\(val\) \{ this\.val = val; this\.next = null; this\.random = null; \} \}$/m,
    "class Node {\n  val: number;\n  next: Node | null = null;\n  random: Node | null = null;\n  constructor(val: number) { this.val = val; }\n}",
  ],
  [
    /^class Node \{ constructor\(val\) \{ this\.val = val; this\.prev = null; this\.next = null; this\.child = null; \} \}$/m,
    "class Node {\n  val: number;\n  prev: Node | null = null;\n  next: Node | null = null;\n  child: Node | null = null;\n  constructor(val: number) { this.val = val; }\n}",
  ],
  [
    /^class Node \{ constructor\(val\) \{ this\.val = val; this\.neighbors = \[\]; \} \}$/m,
    "class Node {\n  val: number;\n  neighbors: Node[] = [];\n  constructor(val: number) { this.val = val; }\n}",
  ],
];

// The shared helpers the node-based starters repeat verbatim. Usage alone can't
// type them well (`build(tokens)` infers `string | any[]` from `.length` and
// indexing), so their parameters are written down.
const HELPER_PARAMS = [
  [/^function build\(tokens\)/m, "function build(tokens: string[])"],
  [/^function build\(vals\)/m, "function build(vals: number[])"],
];

function rewrite(js) {
  let src = js;
  let usesFs = false;
  src = src.replace(/require\((['"])fs\1\)/g, () => {
    usesFs = true;
    return "fs";
  });
  const classes = [];
  for (const [re, typed] of NODE_CLASSES) {
    if (re.test(src)) {
      src = src.replace(re, typed);
      classes.push(typed.match(/^class (\w+)/)[1]);
    }
  }
  // An adjacency list built empty has element type `never[]` until something
  // says otherwise; every graph starter stores neighbour indices.
  src = src.replace(/Array\.from\(\{ length: (\w+) \}, \(\) => \[\]\)/g, "Array.from({ length: $1 }, (): number[] => [])");
  // A predicate over indices whose only caller is the learner's TODO.
  src = src.replace(/^const f = \(i\) =>/m, "const f = (i: number): boolean =>");
  if (classes.length === 1) {
    const cls = classes[0];
    for (const [re, typed] of HELPER_PARAMS) src = src.replace(re, typed);
    // The printing helpers take "a node or nothing", and walk with a cursor
    // that ends at null; a BFS queue that records gaps holds nulls too.
    src = src.replace(/^function (dump|level)\((\w+)\)/gm, `function $1($2: ${cls} | null)`);
    src = src.replace(/for \(let p = (\w+); p;/g, `for (let p: ${cls} | null = $1; p;`);
    src = src.replace(/let prev = null;/g, `let prev: ${cls} | null = null;`);
    src = src.replace(/const out = \[\], q = \[root\];/g, `const out: string[] = [], q: (${cls} | null)[] = [root];`);
    // A placeholder `return null;` carries no type, so inference would type
    // the result — and every parameter it later flows into — as `null`. In a
    // file built around one node class, a function that can return null is
    // returning "a node or nothing".
    src = src.replace(/^function (\w+)\(([^)]*)\) \{/gm, (whole, name, params, offset) => {
      const body = bodyAt(src, offset + whole.length - 1);
      return /\breturn null\b/.test(body) ? `function ${name}(${params}): ${cls} | null {` : whole;
    });
  }
  if (usesFs) src = 'import * as fs from "fs";\n' + src;
  return src;
}

/** The text of the `{ … }` block whose opening brace is at `open`. */
function bodyAt(text, open) {
  let depth = 0;
  for (let i = open; i < text.length; i++) {
    if (text[i] === "{") depth++;
    else if (text[i] === "}" && --depth === 0) return text.slice(open, i + 1);
  }
  return text.slice(open);
}

// ---------------------------------------------------------------------------
// Step 3 + 4: language-service fixes
// ---------------------------------------------------------------------------

const MAIN = path.join(ROOT, "__starter__.ts").replace(/\\/g, "/");
const libCache = new Map();
const readLib = (f) => {
  if (!libCache.has(f)) libCache.set(f, fs.existsSync(f) ? fs.readFileSync(f, "utf8") : undefined);
  return libCache.get(f);
};

let current = "";
let version = 0;
const host = {
  getScriptFileNames: () => [ENV_DTS, MAIN],
  getScriptVersion: (f) => (f === MAIN ? String(version) : "1"),
  getScriptSnapshot: (f) => {
    const text = f === MAIN ? current : readLib(f);
    return text === undefined ? undefined : ts.ScriptSnapshot.fromString(text);
  },
  getCurrentDirectory: () => ROOT,
  getCompilationSettings: () => OPTIONS,
  getDefaultLibFileName: () => path.join(LIB_DIR, "lib.es2022.d.ts"),
  fileExists: (f) => f === MAIN || fs.existsSync(f),
  readFile: (f) => (f === MAIN ? current : readLib(f)),
  readDirectory: ts.sys.readDirectory,
  directoryExists: ts.sys.directoryExists,
  getDirectories: ts.sys.getDirectories,
};
const service = ts.createLanguageService(host, ts.createDocumentRegistry());
const FORMAT = ts.getDefaultFormatCodeSettings("\n");
FORMAT.indentSize = 2;
FORMAT.tabSize = 2;
const PREFS = { quotePreference: "double" };

function setSource(text) {
  current = text;
  version++;
}

function applyEdits(text, changes) {
  const edits = changes.flatMap((c) => c.textChanges).sort((a, b) => b.span.start - a.span.start);
  let out = text;
  for (const e of edits) out = out.slice(0, e.span.start) + e.newText + out.slice(e.span.start + e.span.length);
  return out;
}

function diagnostics() {
  return [...service.getSyntacticDiagnostics(MAIN), ...service.getSemanticDiagnostics(MAIN)];
}

function inferFromUsage() {
  for (let pass = 0; pass < 4; pass++) {
    const diags = diagnostics();
    const codes = new Set(diags.map((d) => d.code));
    // The implicit-any family the "Infer types from usage" fix handles.
    if (![7005, 7006, 7008, 7010, 7011, 7019, 7031, 7032, 7033, 7034, 7043, 7044, 7045, 7046, 7047, 7048, 7049, 7050].some((c) => codes.has(c))) return;
    const fix = service.getCombinedCodeFix({ type: "file", fileName: MAIN }, "inferFromUsage", FORMAT, PREFS);
    if (!fix.changes.length) return;
    const next = applyEdits(current, fix.changes);
    if (next === current) return;
    setSource(next);
  }
}

/** Functions and methods whose return type is not written down. */
function unannotatedFunctions(sf) {
  const found = [];
  const visit = (node) => {
    if (
      (ts.isFunctionDeclaration(node) || ts.isMethodDeclaration(node)) &&
      !node.type &&
      node.body
    ) {
      found.push(node);
    }
    ts.forEachChild(node, visit);
  };
  visit(sf);
  return found;
}

function annotateReturns() {
  const program = service.getProgram();
  const checker = program.getTypeChecker();
  const sf = program.getSourceFile(MAIN);
  const edits = [];
  for (const fn of unannotatedFunctions(sf)) {
    const sig = checker.getSignatureFromDeclaration(fn);
    if (!sig) continue;
    const ret = checker.getReturnTypeOfSignature(sig);
    const text = checker.typeToString(ret, fn, ts.TypeFormatFlags.NoTruncation | ts.TypeFormatFlags.UseFullyQualifiedType);
    // `any` in a return position teaches nothing and hides the contract; leave
    // those for inference rather than writing the word down.
    if (!text || /\bany\b/.test(text) || text.length > 60) continue;
    const closeParen = fn.parameters.end; // position of the ')' after the parameter list
    const at = current.indexOf(")", closeParen) + 1;
    edits.push({ span: { start: at, length: 0 }, newText: `: ${text}` });
  }
  if (!edits.length) return;
  setSource(applyEdits(current, [{ textChanges: edits }]));
}

/** Swap each written `any` for `unknown` wherever the file still compiles.
 * Inference writes `any` when usage says nothing (`const out = []` that is only
 * ever joined); a starter should never be the thing that teaches `any`. */
function preferUnknown() {
  if (diagnostics().length) return;
  const collect = () => {
    const sf = service.getProgram().getSourceFile(MAIN);
    const spots = [];
    const visit = (node) => {
      if (node.kind === ts.SyntaxKind.AnyKeyword) spots.push(node.getStart(sf));
      ts.forEachChild(node, visit);
    };
    visit(sf);
    return spots.sort((a, b) => b - a);
  };
  for (const at of collect()) {
    const before = current;
    setSource(current.slice(0, at) + "unknown" + current.slice(at + 3));
    if (diagnostics().length) setSource(before);
  }
}

export function convert(js) {
  setSource(rewrite(js));
  inferFromUsage();
  annotateReturns();
  preferUnknown();
  const remaining = diagnostics().map((d) => ({
    code: d.code,
    line: d.file && d.start !== undefined ? d.file.getLineAndCharacterOfPosition(d.start).line + 1 : 0,
    msg: ts.flattenDiagnosticMessageText(d.messageText, " "),
  }));
  return { ts: current, diagnostics: remaining };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const problems = JSON.parse(fs.readFileSync(SEED, "utf8"));
  const out = {};
  const failures = [];
  for (const p of problems) {
    // Function-harness problems get stubs generated from their signature
    // (stub_ts in gen_seed.py); only full stdin programs need converting.
    if (p.function_spec) continue;
    const js = p.starter_code?.javascript;
    if (!js) continue;
    const { ts: tsSrc, diagnostics: diags } = convert(js);
    if (diags.length) {
      failures.push({ slug: p.slug, diags });
      continue;
    }
    out[p.slug] = { js_sha: sha(js), ts: tsSrc };
  }
  const sorted = Object.fromEntries(Object.entries(out).sort(([a], [b]) => a.localeCompare(b)));
  fs.writeFileSync(OUT, JSON.stringify(sorted, null, 1) + "\n");
  console.log(`converted ${Object.keys(out).length} starters -> ${path.relative(ROOT, OUT)}`);
  if (failures.length) {
    console.log(`${failures.length} still fail the type-check and were NOT written:`);
    for (const f of failures) {
      console.log(`  ${f.slug}`);
      for (const d of f.diags.slice(0, 4)) console.log(`    L${d.line} TS${d.code} ${d.msg}`);
    }
    process.exitCode = 1;
  }
}
