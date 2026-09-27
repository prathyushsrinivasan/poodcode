/**
 * The layout contract, checked (UI_ROADMAP J1).
 *
 * src/lib/layout.ts names three layout classes — compact below 1180px,
 * regular to 1440px, wide beyond — and what each page template does in each.
 * This loads every page at 960, 1180 and 1440 wide and fails when the page
 * scrolls sideways, when the app frame reports the wrong class, or when
 * Solve's Run and Submit are not both on screen.
 *
 *   node tools/layout-check.mjs [--base http://localhost:5174] [--chromium PATH]
 *
 * Like tools/screenshots.mjs it needs `npm run dev:mock` running and
 * playwright-core with a Chromium, passed in rather than vendored.
 */

const arg = (name, fallback) => {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
};

const BASE = arg("base", "http://localhost:5174");
const EXECUTABLE = arg("chromium", process.env.CHROMIUM_PATH);

const WIDTHS = [
  [960, "compact"],
  [1180, "regular"],
  [1440, "wide"],
];

const PAGES = [
  "/",
  "/insights",
  "/library",
  "/library/browse",
  "/library/unit/io-and-arithmetic",
  "/learn",
  "/learn/sql_join_model",
  "/japanese",
  "/paths",
  "/course/1",
  "/java-course/3",
  "/backend/first-server",
  "/projects/todo-api",
  "/projects/todo-api/todo-shape",
  "/projects/todo-api/reference",
  "/projects/todo-api/history",
  "/projects/todo-api/workbench",
  "/mastery",
  "/settings",
  "/problem/new",
  "/solve/1",
];

let chromium;
try {
  ({ chromium } = await import("playwright-core"));
} catch {
  console.error("playwright-core is not installed (npm i -D playwright-core) — this is a dev tool.");
  process.exit(2);
}

const browser = await chromium.launch({ executablePath: EXECUTABLE });
const failures = [];

for (const [width, expected] of WIDTHS) {
  const page = await browser.newPage({ viewport: { width, height: 800 } });
  for (const route of PAGES) {
    await page.goto(`${BASE}/#${route}`, { waitUntil: "networkidle" });
    await page.waitForTimeout(600);
    const r = await page.evaluate(() => {
      const main = document.getElementById("main");
      const toolbar = [...document.querySelectorAll(".solve-toolbar")].at(-1);
      const visible = (label) => {
        if (!toolbar) return true;
        const bar = toolbar.getBoundingClientRect();
        const b = [...toolbar.querySelectorAll("button")].find((x) => x.textContent?.trim() === label);
        if (!b) return false;
        const box = b.getBoundingClientRect();
        return box.left >= bar.left - 1 && box.right <= bar.right + 1;
      };
      return {
        overflow: main ? main.scrollWidth - main.clientWidth : -1,
        layout: document.querySelector(".app")?.getAttribute("data-layout"),
        actions: visible("Run") && visible("Submit"),
      };
    });
    const problems = [];
    if (r.overflow > 0) problems.push(`scrolls sideways by ${r.overflow}px`);
    if (r.layout !== expected) problems.push(`layout "${r.layout}", expected "${expected}"`);
    if (!r.actions) problems.push("Run/Submit off screen");
    if (problems.length) failures.push(`${width}px ${route}: ${problems.join("; ")}`);
  }
  await page.close();
}

await browser.close();

if (failures.length) {
  console.error(`Layout contract broken in ${failures.length} place(s):\n  ${failures.join("\n  ")}`);
  process.exit(1);
}
console.log(`Layout contract holds: ${PAGES.length} pages at ${WIDTHS.map(([w]) => w).join(", ")}px.`);
