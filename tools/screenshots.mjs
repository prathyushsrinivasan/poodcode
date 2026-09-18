/**
 * Visual regression shots of the key pages, in both themes.
 *
 * Possible only because of the mock backend (UI_ROADMAP L1): the app runs in an
 * ordinary browser against the JSON fixtures, and the fixtures are
 * deterministic — progress is hashed from each problem's slug — so the same
 * page renders identically on every run and a diff means something.
 *
 *   node tools/screenshots.mjs --update    write the baseline
 *   node tools/screenshots.mjs             compare against it
 *
 * Requires a dev server on --base (default http://localhost:5174), started with
 * `npm run dev:mock`, and playwright-core with a Chromium available. Both are
 * passed in rather than vendored, so this stays a dev tool and not a dependency
 * of the app.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const arg = (name, fallback) => {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
};

const BASE = arg("base", "http://localhost:5174");
const OUT = path.resolve(root, arg("out", "screenshots"));
const UPDATE = process.argv.includes("--update");
const EXECUTABLE = arg("chromium", process.env.CHROMIUM_PATH);

/** The pages worth watching, and the themes to watch them in. */
const PAGES = [
  ["today", "/"],
  ["gallery", "/ui"],
  ["curriculum", "/library"],
  ["unit", "/library/unit/two-pointers"],
  ["browse", "/library/browse"],
  ["solve", "/solve/12"],
  ["course", "/course"],
  ["settings", "/settings"],
];
const THEMES = ["dark", "light"];

let chromium;
try {
  ({ chromium } = await import("playwright-core"));
} catch {
  console.error(
    "playwright-core is not installed. This is a dev tool, not an app dependency:\n" +
      "  npm i -D playwright-core\n" +
      "and point --chromium (or CHROMIUM_PATH) at a Chromium binary."
  );
  process.exit(2);
}

const dir = path.join(OUT, UPDATE ? "baseline" : "current");
fs.mkdirSync(dir, { recursive: true });

const browser = await chromium.launch(EXECUTABLE ? { executablePath: EXECUTABLE } : {});
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });

const problems = [];

for (const theme of THEMES) {
  for (const [name, route] of PAGES) {
    const file = `${name}-${theme}.png`;
    await page.goto(`${BASE}/#${route}`, { waitUntil: "networkidle" });
    // The theme is a data attribute on the root; setting it directly avoids
    // depending on where the toggle happens to live.
    await page.evaluate((t) => {
      document.documentElement.dataset.theme = t;
    }, theme);
    // Mask the genuinely time-dependent bits. Solve runs a wall-clock timer
    // that ticks every second, so two identical runs produce different pixels
    // and every comparison fails — which was found the first time this script
    // was run twice in a row. Masking beats freezing the clock: the layout
    // these occupy is still checked, only their contents are not.
    await page.addStyleTag({
      content: `.timer, .save-state, .stat-trend { visibility: hidden !important; }`,
    });
    // Seeds are megabytes and parse asynchronously; wait for the page to settle
    // rather than racing it.
    await page.waitForTimeout(3500);
    await page.screenshot({ path: path.join(dir, file), fullPage: false });
    process.stdout.write(`  ${file}\n`);
  }
}

await browser.close();

if (UPDATE) {
  console.log(`\nBaseline written to ${path.relative(root, dir)}.\n`);
  process.exit(0);
}

// Byte comparison. It is strict — an antialiasing difference between machines
// will trip it — which is why the baseline is regenerated on the machine that
// checks it rather than committed blindly.
const baseline = path.join(OUT, "baseline");
if (!fs.existsSync(baseline)) {
  console.error(`\nNo baseline at ${path.relative(root, baseline)}. Run with --update first.\n`);
  process.exit(2);
}

for (const file of fs.readdirSync(dir)) {
  const a = path.join(baseline, file);
  if (!fs.existsSync(a)) {
    problems.push(`${file}: new page, no baseline`);
    continue;
  }
  const before = fs.readFileSync(a);
  const after = fs.readFileSync(path.join(dir, file));
  if (!before.equals(after)) problems.push(`${file}: differs from the baseline`);
}

if (problems.length === 0) {
  console.log(`\n  ${fs.readdirSync(dir).length} screenshots match the baseline.\n`);
  process.exit(0);
}

console.error("\n  Visual differences:\n");
for (const p of problems) console.error(`  ${p}`);
console.error(
  `\n  Compare ${path.relative(root, dir)} against ${path.relative(root, baseline)}.\n` +
    "  If the change is intended, re-run with --update.\n"
);
process.exit(1);
