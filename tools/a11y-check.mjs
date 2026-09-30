/**
 * Accessibility, checked by axe (UI_ROADMAP L6).
 *
 * `npm run check:contrast` proves the token pairs pass AA on paper; this loads
 * every route in the mock app, in both themes, and runs axe-core against what
 * actually rendered — names on controls, ARIA that is valid, landmarks, one
 * h1, ordered headings, and contrast as the browser computed it.
 *
 *   node tools/a11y-check.mjs [--base http://localhost:5174] [--chromium PATH]
 *                             [--only /route] [--verbose]
 *
 * Like tools/layout-check.mjs it needs `npm run dev:mock` running, and
 * playwright-core and axe-core installed — passed in rather than vendored,
 * because this is a dev tool and not a dependency of the app.
 */

const arg = (name, fallback) => {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
};

const BASE = arg("base", "http://localhost:5174");
const EXECUTABLE = arg("chromium", process.env.CHROMIUM_PATH);
const ONLY = arg("only", null);
const VERBOSE = process.argv.includes("--verbose");

/** Every route in App.tsx, with a real parameter where it takes one. */
const PAGES = [
  "/",
  "/insights",
  "/library",
  "/library/browse",
  "/library/unit/io-and-arithmetic",
  "/library/placement",
  "/library/mixed/1",
  "/learn",
  "/learn/sql_join_model",
  "/japanese",
  "/jp-bridge",
  "/paths",
  "/course",
  "/course/1",
  "/java-course",
  "/java-course/3",
  "/backend",
  "/backend/first-server",
  "/projects",
  "/projects/todo-api",
  "/projects/todo-api/todo-shape",
  "/projects/todo-api/reference",
  "/projects/todo-api/history",
  "/projects/todo-api/workbench",
  "/projects/todo-api/review",
  "/mastery",
  "/flashcards",
  "/ts-errors",
  "/playground/ts",
  "/visualise/async",
  "/settings",
  "/problem/new",
  "/problem/1/edit",
  "/solve/1",
  "/ui",
  "/no-such-page",
].filter((r) => !ONLY || r === ONLY);

/** [theme, contrast]: both themes, and each in the high-contrast variant. */
const THEMES = [
  ["dark", "normal"],
  ["light", "normal"],
  ["dark", "high"],
  ["light", "high"],
];

/**
 * WCAG 2.1 A and AA, plus axe's best practices — which is where "one h1",
 * "headings in order" and "content inside landmarks" live (D9).
 */
const TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"];

/**
 * Rules switched off, each with the reason. Keep this list short: a rule goes
 * here only when what it flags is not a defect in this app.
 */
const DISABLED = {};

/**
 * Monaco renders its own editor DOM — a hidden textarea and hundreds of
 * positioned spans — which the app does not own and cannot relabel.
 */
const EXCLUDE = [".monaco-editor", ".monaco-aria-container"];

let chromium, axeSource;
try {
  ({ chromium } = await import("playwright-core"));
  ({ source: axeSource } = (await import("axe-core")).default);
} catch {
  console.error(
    "playwright-core and axe-core are not installed. This is a dev tool, not an app dependency:\n" +
      "  npm i -D playwright-core axe-core\n" +
      "and point --chromium (or CHROMIUM_PATH) at a Chromium binary."
  );
  process.exit(2);
}

const browser = await chromium.launch(EXECUTABLE ? { executablePath: EXECUTABLE } : {});
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });

/** rule id → { impact, help, where: Set of "route (theme): target" } */
const found = new Map();

for (const [themeName, contrastMode] of THEMES) {
  const theme = contrastMode === "high" ? `${themeName}, high contrast` : themeName;
  for (const route of PAGES) {
    await page.goto(`${BASE}/#${route}`, { waitUntil: "networkidle" });
    // Set on the root directly, as tools/screenshots.mjs does, rather than
    // depending on where the Settings controls happen to live.
    await page.evaluate(
      ([t, c]) => {
        document.documentElement.dataset.theme = t;
        if (c === "high") document.documentElement.dataset.contrast = "high";
        else delete document.documentElement.dataset.contrast;
      },
      [themeName, contrastMode]
    );
    // Seeds are megabytes and parse asynchronously; let the page settle, and
    // let entry transitions finish so contrast is measured at full opacity.
    await page.waitForTimeout(1500);
    await page.addScriptTag({ content: axeSource });
    const violations = await page.evaluate(
      async ({ tags, rules, exclude }) => {
        const r = await window.axe.run(
          { include: [document], exclude: exclude.map((s) => [s]) },
          { runOnly: { type: "tag", values: tags }, rules: Object.fromEntries(Object.keys(rules).map((k) => [k, { enabled: false }])) }
        );
        return r.violations.map((v) => ({
          id: v.id,
          impact: v.impact,
          help: v.help,
          targets: v.nodes.map((n) => `${n.target.join(" ")}${n.any[0]?.message ? ` — ${n.any[0].message}` : ""}`),
        }));
      },
      { tags: TAGS, rules: DISABLED, exclude: EXCLUDE }
    );
    for (const v of violations) {
      const entry = found.get(v.id) ?? { impact: v.impact, help: v.help, where: new Set() };
      for (const t of v.targets) entry.where.add(`${route} (${theme}): ${t}`);
      found.set(v.id, entry);
    }
    if (VERBOSE) process.stdout.write(`  ${theme} ${route}: ${violations.length} rule(s)\n`);
  }
}

await browser.close();

if (found.size) {
  const order = { critical: 0, serious: 1, moderate: 2, minor: 3 };
  const rules = [...found.entries()].sort((a, b) => order[a[1].impact] - order[b[1].impact]);
  console.error(`axe found ${rules.length} rule(s) broken:\n`);
  for (const [id, { impact, help, where }] of rules) {
    console.error(`  ${impact}  ${id} — ${help} (${where.size})`);
    const list = [...where];
    for (const w of list.slice(0, VERBOSE ? list.length : 6)) console.error(`      ${w}`);
    if (!VERBOSE && list.length > 6) console.error(`      … and ${list.length - 6} more (--verbose)`);
  }
  process.exit(1);
}
console.log(`axe: no violations on ${PAGES.length} routes, in both themes, each at normal and high contrast.`);
