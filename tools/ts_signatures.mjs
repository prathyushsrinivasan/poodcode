// Function signatures in TypeScript programs, for deriving "retype" exercises
// (tools/gen_ts_retypes.py). Reads a JSON array of {id, src} on stdin and
// writes [{id, fns: [{name, params: [{start, end, text}], ret: {start, end, text}}]}]:
// every top-level, non-generic, non-overloaded function declaration whose
// parameters and return type are all annotated, with the source span of each
// annotation. Parsing only — no type checking.

import * as fs from "fs";
import * as path from "path";
import { fileURLToPath, pathToFileURL } from "url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ts = (await import(pathToFileURL(path.join(HERE, "..", "node_modules/typescript/lib/typescript.js")).href)).default;

const input = fs.readFileSync(0, "utf8");
const out = JSON.parse(input).map(({ id, src }) => {
  const file = ts.createSourceFile("main.ts", src, ts.ScriptTarget.ES2022, true);
  const counts = new Map();
  for (const st of file.statements) {
    if (ts.isFunctionDeclaration(st) && st.name) counts.set(st.name.text, (counts.get(st.name.text) ?? 0) + 1);
  }
  const fns = [];
  for (const st of file.statements) {
    if (!ts.isFunctionDeclaration(st) || !st.name || !st.body || st.typeParameters) continue;
    if (counts.get(st.name.text) !== 1 || st.asteriskToken) continue;
    if (!st.type || st.parameters.length === 0) continue;
    if (!st.parameters.every((p) => p.type && ts.isIdentifier(p.name) && p.name.text !== "this" && !p.dotDotDotToken && !p.questionToken && !p.initializer)) continue;
    const span = (node) => ({ start: node.getStart(file), end: node.getEnd(), text: node.getText(file) });
    const isAsync = (st.modifiers ?? []).some((m) => m.kind === ts.SyntaxKind.AsyncKeyword);
    fns.push({ name: st.name.text, async: isAsync, params: st.parameters.map((p) => span(p.type)), ret: span(st.type) });
  }
  // Top-level, non-generic type declarations, for "design" drills
  // (tools/gen_ts_designs.py): the statement's span, its name, and its shape as
  // a type expression (an interface without `extends` becomes its `{ … }`).
  const types = [];
  for (const st of file.statements) {
    const span = { start: st.getStart(file), end: st.getEnd() };
    if (ts.isTypeAliasDeclaration(st) && !st.typeParameters) {
      types.push({ name: st.name.text, ...span, shape: st.type.getText(file) });
    } else if (ts.isInterfaceDeclaration(st) && !st.typeParameters && !st.heritageClauses) {
      const open = st.members.pos;
      const text = src.slice(st.getStart(file), st.getEnd());
      const brace = text.indexOf("{");
      types.push({ name: st.name.text, ...span, shape: brace >= 0 ? text.slice(brace) : "" });
      void open;
    }
  }
  return { id, fns, types };
});
process.stdout.write(JSON.stringify(out));
