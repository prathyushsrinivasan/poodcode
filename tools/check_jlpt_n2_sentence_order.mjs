/** Browser smoke test against dev:mock. Reuses a local Playwright install:
 * node tools/check_jlpt_n2_sentence_order.mjs --playwright PATH --chromium PATH
 * Covers all 125 solutions, navigation, review, resume, persistence and layout. */
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { pathToFileURL } from "node:url";
import ts from "typescript";

const arg = (name, fallback) => {
  const index = process.argv.indexOf(`--${name}`);
  return index < 0 ? fallback : process.argv[index + 1];
};
const modulePath = arg("playwright");
const { chromium } = modulePath ? await import(pathToFileURL(modulePath).href) : await import("playwright-core");
const source = await fs.readFile(new URL("../src/data/jlptN2SentenceOrder.ts", import.meta.url), "utf8");
const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext } }).outputText;
const { N2_ASSEMBLY_LESSONS, assemblyAnswer } = await import(`data:text/javascript;base64,${Buffer.from(js).toString("base64")}`);
const browser = await chromium.launch({ executablePath: arg("chromium", process.env.CHROMIUM_PATH) });
const page = await browser.newPage({ viewport: { width: 1360, height: 900 } });
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
const base = arg("base", "http://127.0.0.1:5174");
const course = "/japanese/n2/sentence-order";
const go = async (path) => {
  if (page.url().startsWith(base)) {
    // Match in-app navigation. Full page loads can interrupt the mock backend's
    // debounced localStorage write even after its setting promise has resolved.
    await page.evaluate((path) => { window.location.hash = path; }, path);
    await page.waitForURL(`${base}/#${path}`);
  } else await page.goto(`${base}/#${path}`);
  await page.locator(".n2-page").waitFor();
};
const check = async (n) => {
  await page.locator(`input[type=radio][value="${n}"]`).check();
  await page.getByRole("button", { name: "Check answer", exact: true }).click();
};
const next = () => page.getByRole("button", { name: /^(Next question →|Finish round)$/ }).click();
try {
  await go("/japanese/n2");
  assert.equal(await page.locator(".n2-lesson").count(), 2);
  await page.getByRole("link", { name: /Sentence Assembly ★.*Open course/ }).click();
  await page.getByRole("heading", { name: "How to solve ★ questions", exact: true }).waitFor();
  assert.equal(await page.locator(".n2-lesson").count(), 25);
  await page.getByLabel("Find an assembly pattern or sentence").fill("かねない");
  assert.ok(await page.locator(".n2-lesson").count() > 0);
  await page.getByLabel("Find an assembly pattern or sentence").fill("no-such-pattern-xyz");
  await page.getByText("No lessons match this search.", { exact: true }).waitFor();

  // Both a reveal and a wrong answer persist for review. Correcting the first
  // review item must not remove/skip the second item in the frozen round.
  await go(`${course}/examples`);
  assert.equal(await page.locator(".n2-slot").count(), 4);
  assert.equal(await page.getByRole("button", { name: "Check answer", exact: true }).isEnabled(), false);
  await page.getByRole("button", { name: "Show answer · revisit later" }).click();
  await next();
  await check(1);
  await page.getByText("Not quite · added to review", { exact: true }).waitFor();
  await go(`${course}/review`);
  await check(2);
  await next();
  await page.getByText("朝ご飯はなるべく", { exact: false }).first().waitFor();
  await check(3);
  await next();
  await page.getByRole("heading", { name: "2 / 2 correct this round" }).waitFor();
  await go(course);
  await page.getByText("2 / 125 correct on latest attempt", { exact: true }).waitFor();
  // This check deliberately reloads the document, so first wait for the mock
  // backend to finish its debounced durable write (the desktop uses SQLite).
  await page.waitForFunction(() => Object.values(localStorage).some((raw) => {
    try {
      const settings = JSON.parse(raw).settings;
      const progress = JSON.parse(settings?.["jlpt-n2-sentence-order-progress-v1"] ?? "{}");
      return progress["examples-13"]?.lastCorrect && progress["examples-14"]?.lastCorrect;
    } catch { return false; }
  }));
  await page.reload();
  await page.getByText("2 / 125 correct on latest attempt", { exact: true }).waitFor();

  // All data solutions work through the radio-button UI. The supplied lesson
  // resumes at its first unanswered question (15), then wraps to 13 and 14.
  for (const lesson of N2_ASSEMBLY_LESSONS) {
    await go(`${course}/${lesson.id}`);
    const questions = lesson.id === "examples"
      ? [...lesson.questions.slice(2), ...lesson.questions.slice(0, 2)] : lesson.questions;
    for (const q of questions) {
      await check(assemblyAnswer(q));
      await page.getByText("Correct ★ answer", { exact: true }).waitFor();
      await page.getByText(q.translation, { exact: true }).waitFor();
      await page.getByText(q.explanation, { exact: true }).waitFor();
      await next();
    }
    await page.getByRole("heading", { name: "5 / 5 correct this round" }).waitFor();
  }
  await go(course);
  await page.getByText("125 / 125 correct on latest attempt", { exact: true }).waitFor();
  await go(`${course}/review`);
  await page.getByRole("heading", { name: "No assembly mistakes waiting" }).waitFor();

  // Scratchpad uses all four fragments once and selects the starred choice.
  await go(`${course}/s01`);
  await page.getByText("Build the full sentence (optional scratchpad)", { exact: true }).click();
  const q = N2_ASSEMBLY_LESSONS[1].questions[0];
  for (const n of q.order) await page.locator(".n2-scratch").getByRole("button", { name: `${n}. ${q.choices[n - 1]}`, exact: true }).click();
  assert.equal(await page.locator(`input[value="${assemblyAnswer(q)}"]`).isChecked(), true);
  await page.getByRole("button", { name: "Clear arrangement", exact: true }).click();
  assert.equal(await page.getByRole("button", { name: "Check answer", exact: true }).isEnabled(), false);
  await page.getByRole("button", { name: "Show pattern hint", exact: true }).click();
  await page.locator(".n2-hint").waitFor();

  // Old progress and old lesson URLs continue to work after the course move.
  await go("/japanese/n2/a01");
  await page.getByLabel("Your answer", { exact: true }).fill("制");
  await page.getByRole("button", { name: "Check answer", exact: true }).click();
  await page.getByText("Accepted answer", { exact: true }).waitFor();
  await go("/japanese/n2/patterns");
  await page.getByText("1 / 120 correct on latest attempt", { exact: true }).waitFor();
  await go(course);
  await page.getByText("125 / 125 correct on latest attempt", { exact: true }).waitFor();

  await go(`${course}/mixed`);
  const seen = new Set();
  for (let i = 0; i < 5; i++) {
    const sentence = await page.locator(".n2-sentence").first().textContent();
    assert.equal(seen.has(sentence), false);
    seen.add(sentence);
    await page.getByRole("button", { name: "Show answer · revisit later" }).click();
    await next();
  }
  await page.getByRole("heading", { name: "0 / 5 correct this round" }).waitFor();
  await page.getByRole("button", { name: "Try another 5", exact: true }).click();
  await page.getByText("Question 1 of 5", { exact: true }).waitFor();

  await fs.mkdir(new URL("../src-tauri/target/jlpt-check/", import.meta.url), { recursive: true });
  for (const width of [700, 960, 1180, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    for (const route of ["/japanese/n2", course, `${course}/s24`]) {
      await go(route);
      assert.equal(await page.getByRole("heading", { level: 1 }).count(), 1);
      assert.equal(await page.evaluate(() => {
        const main = document.querySelector("main");
        return main.scrollWidth > main.clientWidth + 1;
      }), false, `${route} overflows at ${width}px`);
    }
    const url = new URL(`../src-tauri/target/jlpt-check/assembly-${width}.png`, import.meta.url);
    await page.screenshot({ path: url.pathname.replace(/^\/(\w:)/, "$1") });
  }
  assert.deepEqual(errors, []);
  console.log("PASS: 125 assembly solutions, translations, explanations, course menu, search, resume, review, persistence, scratchpad, hints, mixed sets, legacy routes, independent progress and 700–1440px layouts.");
} finally {
  await browser.close();
}
