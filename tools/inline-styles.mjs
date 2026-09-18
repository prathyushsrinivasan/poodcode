/**
 * A ratchet on inline `style={{…}}` objects.
 *
 * The audit behind UI_ROADMAP counted ~1,500 of them across the pages and
 * components — Projects alone had 171 — each picking its own 10, 12, 14 or 16.
 * That is why nothing lined up, and it is why the design tokens exist.
 *
 * Deleting them all at once is not realistic and not always right: a width
 * computed from data, or a colour chosen per difficulty, genuinely belongs
 * inline. So this does not ban them. It records how many each file has and
 * fails if that number *grows* — the count can only go down, and every file
 * moved onto tokens lowers the baseline permanently.
 *
 *   node tools/inline-styles.mjs            check (CI)
 *   node tools/inline-styles.mjs --update   rewrite the baseline after a cleanup
 *   node tools/inline-styles.mjs --report   show the worst offenders
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SRC = path.join(root, "src");
const BASELINE = path.join(root, "tools", "inline-styles.baseline.json");

/** Every .tsx under src/, repo-relative, with forward slashes. */
function sources(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...sources(full));
    else if (entry.name.endsWith(".tsx")) out.push(full);
  }
  return out;
}

function count(file) {
  const text = fs.readFileSync(file, "utf8");
  // `style={{` is the JSX object form. `style={someVar}` is deliberately not
  // matched: passing a prepared object through is not the problem this guards.
  return (text.match(/style=\{\{/g) ?? []).length;
}

const counts = {};
for (const file of sources(SRC)) {
  const n = count(file);
  if (n > 0) counts[path.relative(root, file).replaceAll("\\", "/")] = n;
}

const total = Object.values(counts).reduce((a, b) => a + b, 0);

if (process.argv.includes("--update")) {
  fs.writeFileSync(BASELINE, JSON.stringify({ total, files: counts }, null, 2) + "\n");
  console.log(`Baseline written: ${total} inline style objects across ${Object.keys(counts).length} files.`);
  process.exit(0);
}

if (process.argv.includes("--report")) {
  const worst = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  console.log(`\n  ${total} inline style objects in ${worst.length} files\n`);
  for (const [file, n] of worst.slice(0, 20)) {
    console.log(`  ${String(n).padStart(4)}  ${file}`);
  }
  console.log("");
  process.exit(0);
}

if (!fs.existsSync(BASELINE)) {
  console.error("No baseline. Run: node tools/inline-styles.mjs --update");
  process.exit(1);
}

const baseline = JSON.parse(fs.readFileSync(BASELINE, "utf8"));
const grew = [];
const added = [];
for (const [file, n] of Object.entries(counts)) {
  const was = baseline.files[file];
  if (was === undefined) added.push([file, n]);
  else if (n > was) grew.push([file, was, n]);
}

// A file that lost its inline styles entirely is progress, not a failure — but
// it should be recorded so the baseline cannot drift back up later.
const improved = Object.entries(baseline.files).filter(
  ([file, was]) => (counts[file] ?? 0) < was
);

if (grew.length === 0 && added.length === 0) {
  console.log(
    `\n  ${total} inline style objects (baseline ${baseline.total}).` +
      (improved.length
        ? `\n  ${improved.length} file(s) improved — run --update to lock it in.\n`
        : "\n")
  );
  process.exit(0);
}

console.error("\n  Inline styles grew. Use a class and the design tokens instead.\n");
for (const [file, was, now] of grew) {
  console.error(`  ${file}: ${was} → ${now}`);
}
for (const [file, n] of added) {
  console.error(`  ${file}: new file with ${n} inline style object(s)`);
}
console.error(
  "\n  If the value is genuinely dynamic (a width from data, a colour per\n" +
    "  difficulty), keep it inline and run: node tools/inline-styles.mjs --update\n"
);
process.exit(1);
