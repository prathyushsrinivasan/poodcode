/** Browser smoke test against dev:mock. Optional --playwright MODULE_PATH and
 * --chromium EXE_PATH reuse an existing browser installation without adding deps.
 * Checks all 300 answers, filtered rounds, saved progress, reveal/mistake review,
 * keyboard submission, navigation, empty selections and responsive layouts. */
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { pathToFileURL } from "node:url";
import ts from "typescript";

const arg = (name, fallback) => {
  const i = process.argv.indexOf(`--${name}`);
  return i < 0 ? fallback : process.argv[i + 1];
};
const base = arg("base", "http://127.0.0.1:5181");
const modulePath = arg("playwright");
const { chromium } = modulePath ? await import(pathToFileURL(modulePath).href) : await import("playwright-core");
const source = await fs.readFile(new URL("../src/data/jlptAffixes.ts", import.meta.url), "utf8");
const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext } }).outputText;
const { AFFIX_LESSONS, AFFIX_QUESTIONS } = await import(`data:text/javascript;base64,${Buffer.from(js).toString("base64")}`);
const byId = new Map(AFFIX_QUESTIONS.map((q) => [q.id, q]));
const browser = await chromium.launch({ executablePath: arg("chromium", process.env.CHROMIUM_PATH) });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
const route = "/japanese/n2/affixes";
const go = async (path = route) => {
  await page.goto(`${base}/#${path}`);
  await page.getByRole("heading", { level: 1 }).waitFor();
};
const current = async () => {
  const name = await page.locator('.n2-choice input').first().getAttribute("name");
  const q = byId.get(name.replace(/^affix-/, ""));
  assert(q, `Unknown rendered question ${name}`);
  return q;
};
const answer = async (q, value = q.answer) => {
  await page.locator(`.n2-choice input[value="${value}"]`).check();
  await page.getByRole("button", { name: "Check answer", exact: true }).click();
};
const correct = () => page.getByText("Correct answer", { exact: true }).waitFor();
const next = () => page.getByRole("button", { name: /^(Next question →|Finish round)$/ }).click();
// The mock backend debounces localStorage writes. Wait for durable state before
// a hard reload; feedback appears before the asynchronous save has completed.
const saved = (id, lastCorrect) => page.waitForFunction(({ id, lastCorrect }) => {
  const state = JSON.parse(localStorage.getItem("poodcode.mock.v1") ?? "null");
  const progress = JSON.parse(state?.settings?.["jlpt-affixes-progress-v1"] ?? "{}");
  return progress[id]?.lastCorrect === lastCorrect;
}, { id, lastCorrect });

try {
  await go("/japanese/n2");
  await page.getByRole("link", { name: "Prefixes & Suffixes N3–N1 →", exact: true }).waitFor();
  await page.getByRole("link", { name: "Full course library →", exact: true }).click();
  await page.getByRole("link", { name: /300 questions.*30 families/ }).click();
  await page.getByRole("heading", { name: "Prefixes & Suffixes", exact: true }).waitFor();
  assert.equal(await page.locator(".n2-lesson").count(), 30);
  await page.getByLabel("Study level").selectOption("N2");
  await page.getByLabel("Word position").selectOption("prefix");
  await page.getByText("50 matching questions · 5 families", { exact: true }).waitFor();
  await page.getByLabel("Target affix").selectOption("非");
  await page.getByText("3 matching questions · 1 family", { exact: true }).waitFor();
  await page.reload();
  await page.getByText("3 matching questions · 1 family", { exact: true }).waitFor();
  await page.getByRole("link", { name: "Clear filters", exact: true }).click();
  await page.getByLabel("Find an affix, word, reading or meaning").fill("名選手");
  await page.getByText("1 matching question · 1 family", { exact: true }).waitFor();
  await page.getByLabel("Find an affix, word, reading or meaning").fill("nothing-matches-xyz");
  await page.getByRole("heading", { name: "No questions match these filters" }).waitFor();
  await page.getByRole("link", { name: "Show all 300 questions" }).click();

  await go(`${route}/n3-praise`);
  assert.equal(await page.getByRole("button", { name: "Check answer", exact: true }).isEnabled(), false);
  let q = await current();
  assert.equal(q.word, "名選手");
  await answer(q, "優");
  await page.getByText("Not quite · added to review", { exact: true }).waitFor();
  await next();
  await page.getByRole("button", { name: "Show answer · revisit later", exact: true }).click();
  await page.getByText("Answer revealed · added to review", { exact: true }).waitFor();
  await saved("n3-praise-2", false);
  await page.reload();
  await go(`${route}/review`);
  await answer(await current()); await correct(); await next();
  q = await current();
  assert.equal(q.word, "名作", "Correcting the first review item must not skip the second");
  await answer(q); await correct(); await next();
  await page.getByRole("heading", { name: "2 / 2 correct this round" }).waitFor();
  await saved("n3-praise-2", true);
  await page.reload();
  await page.getByRole("heading", { name: "No affix mistakes waiting" }).waitFor();
  console.log("Passed filters, incorrect/revealed answers, persistence and review snapshots");

  // A constrained mixed round must retain the selection, size and unique IDs.
  await go(`${route}/mixed?level=N1&kind=suffix&size=20`);
  const mixedIds = new Set();
  for (let i = 0; i < 20; i++) {
    q = await current();
    assert.equal(q.level, "N1"); assert.equal(q.kind, "suffix");
    assert(!mixedIds.has(q.id)); mixedIds.add(q.id);
    await answer(q); await correct(); await next();
  }
  await page.getByRole("heading", { name: "20 / 20 correct this round" }).waitFor();

  let checked = 0;
  const allIds = new Set();
  for (const lesson of AFFIX_LESSONS) {
    await go(`${route}/${lesson.id}`);
    for (let i = 0; i < lesson.questions.length; i++) {
      q = await current();
      assert.equal(q.lessonId, lesson.id);
      assert(!allIds.has(q.id)); allIds.add(q.id);
      if (checked === 0) {
        await page.locator(`.n2-choice input[value="${q.answer}"]`).check();
        await page.getByRole("button", { name: "Check answer", exact: true }).focus();
        await page.keyboard.press("Enter");
      } else await answer(q);
      await correct();
      const feedback = await page.locator(".n2-feedback").innerText();
      assert(feedback.includes(q.reading), `${q.id}: reading missing`);
      assert(feedback.includes(q.translation), `${q.id}: translation missing`);
      assert(feedback.includes(q.explanation), `${q.id}: explanation missing`);
      await next(); checked++;
      if (checked % 50 === 0) console.log(`Checked ${checked}/300 answers`);
    }
    await page.getByRole("heading", { name: "10 / 10 correct this round" }).waitFor();
  }
  assert.equal(allIds.size, 300);
  await page.waitForFunction(() => {
    const state = JSON.parse(localStorage.getItem("poodcode.mock.v1") ?? "null");
    const progress = JSON.parse(state?.settings?.["jlpt-affixes-progress-v1"] ?? "{}");
    return Object.values(progress).filter((row) => row.lastCorrect).length === 300;
  });
  await go(); await page.reload();
  await page.getByText("300 / 300 correct on latest attempt", { exact: true }).waitFor();
  await go(`${route}/mixed?level=N3&affix=かねる`);
  await page.getByRole("heading", { name: "No questions in this selection" }).waitFor();
  await go(`${route}/not-a-lesson`);
  await page.getByRole("heading", { name: "Lesson not found" }).waitFor();

  const output = new URL("../src-tauri/target/jlpt-affixes-check/", import.meta.url);
  await fs.mkdir(output, { recursive: true });
  for (const width of [640, 960, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const path of [route, `${route}/n1-verb-endings`]) {
      await go(path);
      assert.equal(await page.getByRole("heading", { level: 1 }).count(), 1);
      assert.equal(await page.locator("main").evaluate((el) => el.scrollWidth > el.clientWidth + 1), false, `Overflow at ${width}px: ${path}`);
    }
    await page.screenshot({ path: new URL(`exercise-${width}.png`, output).pathname.replace(/^\/(\w:)/, "$1"), fullPage: true });
  }
  assert.deepEqual(errors, [], "No browser runtime errors");
  console.log("PASS: 300 answers, filtered mixed practice, saved progress, review snapshots, keyboard submission, navigation and 640/960/1440px layouts.");
} catch (error) {
  console.error("Current page:", (await page.locator("main").innerText()).slice(0, 2000));
  throw error;
} finally {
  await browser.close();
}
