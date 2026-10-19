/** Browser smoke test against dev:mock, using an existing Playwright install.
 * node tools/check_jlpt_n2.mjs --playwright PATH_TO_INDEX_MJS --chromium PATH
 * Covers all 120 answers, persistence, mistake review, filters and layout.
 */
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { pathToFileURL } from "node:url";
import ts from "typescript";

const arg = (name, fallback) => {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : fallback;
};
const base = arg("base", "http://127.0.0.1:5174");
const modulePath = arg("playwright");
const { chromium } = modulePath ? await import(pathToFileURL(modulePath).href) : await import("playwright-core");
const source = await fs.readFile(new URL("../src/data/jlptN2.ts", import.meta.url), "utf8");
const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext } }).outputText;
const { N2_LESSONS } = await import(`data:text/javascript;base64,${Buffer.from(js).toString("base64")}`);
const browser = await chromium.launch({ executablePath: arg("chromium", process.env.CHROMIUM_PATH) });
const page = await browser.newPage({ viewport: { width: 1360, height: 900 } });
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
const go = async (path) => {
  await page.goto(`${base}/#${path}`);
  await page.locator(".n2-page").waitFor();
};
const answer = async (value) => {
  await page.getByLabel("Your answer", { exact: true }).fill(value);
  await page.getByRole("button", { name: "Check answer", exact: true }).click();
};
const next = () => page.getByRole("button", { name: /^(Next question →|Finish round)$/ }).click();
try {
  await go("/japanese/n2");
  assert.equal(await page.locator(".n2-lesson").count(), 24);
  await page.getByRole("button", { name: "One kanji · 60 questions" }).click();
  assert.equal(await page.locator(".n2-lesson").count(), 12);
  await page.getByRole("button", { name: "All families · 24" }).click();
  await page.getByLabel("Find a pattern or word").fill("調整");
  assert.equal(await page.locator(".n2-lesson").count(), 1);
  await page.getByLabel("Find a pattern or word").fill("no-such-pattern-xyz");
  await page.getByText("No families match this search.", { exact: false }).waitFor();
  await page.getByLabel("Find a pattern or word").fill("");

  // Both an incorrect submission and a reveal must survive reload for review.
  await go("/japanese/n2/a01");
  assert.equal(await page.getByRole("button", { name: "Check answer", exact: true }).isEnabled(), false);
  await answer("大統領制");
  await page.getByText("Compare with the teaching target", { exact: true }).waitFor();
  await next();
  await page.getByRole("button", { name: "Show answer · revisit later" }).click();
  await next();
  await go("/japanese/n2/review");
  await answer("制");
  await page.getByText("Accepted answer", { exact: true }).waitFor();
  await next();
  // Correcting review item 1 must not remove/skip item 2.
  await page.locator(".n2-sentence").filter({ hasText: "記述" }).waitFor();
  await answer("式");
  await next();
  await page.getByRole("heading", { name: "2 / 2 correct this round" }).waitFor();
  await go("/japanese/n2");
  await page.getByText("2 / 120 correct on latest attempt", { exact: true }).waitFor();

  // Resume rotates a partially completed family to its first unanswered item.
  // Complete fresh families first; finish a01 in its resumed order last.
  for (const lesson of [...N2_LESSONS.slice(1), N2_LESSONS[0]]) {
    await go(`/japanese/n2/${lesson.id}`);
    const questions = lesson.id === "a01"
      ? [...lesson.questions.slice(2), ...lesson.questions.slice(0, 2)] : lesson.questions;
    for (const q of questions) {
      await answer(q.answer);
      await page.getByText("Accepted answer", { exact: true }).waitFor();
      await next();
    }
    await page.getByRole("heading", { name: "5 / 5 correct this round" }).waitFor();
  }
  await go("/japanese/n2");
  await page.getByText("120 / 120 correct on latest attempt", { exact: true }).waitFor();
  await go("/japanese/n2/review");
  await page.getByRole("heading", { name: "No mistakes waiting" }).waitFor();

  // Accepted alternative and IME Enter support on a vocabulary blank.
  await go("/japanese/n2/b01");
  await page.getByLabel("Your answer", { exact: true }).fill("決定");
  await page.getByLabel("Your answer", { exact: true }).dispatchEvent("keydown", { key: "Enter", isComposing: true, keyCode: 229 });
  assert.equal(await page.getByRole("button", { name: "Check answer", exact: true }).count(), 1);
  await page.getByRole("button", { name: "Check answer", exact: true }).click();
  await page.getByText("Accepted answer", { exact: true }).waitFor();

  await fs.mkdir(new URL("../src-tauri/target/jlpt-check/", import.meta.url), { recursive: true });
  for (const width of [960, 1180, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    for (const route of ["/japanese/n2", "/japanese/n2/b12"]) {
      await go(route);
      const overflow = await page.evaluate(() => {
        const main = document.querySelector("main");
        return main.scrollWidth > main.clientWidth + 1;
      });
      assert.equal(overflow, false, `${route} overflows at ${width}px`);
      assert.equal(await page.getByRole("heading", { level: 1 }).count(), 1);
    }
    await page.screenshot({ path: new URL(`../src-tauri/target/jlpt-check/lesson-${width}.png`, import.meta.url).pathname.replace(/^\/(\w:)/, "$1") });
  }
  assert.deepEqual(errors, [], "No browser runtime errors");
  console.log("PASS: all 120 answers, alternative answers, progress reload, resume, mistake/reveal review, IME Enter, filters, and 960/1180/1440px layouts.");
} finally {
  await browser.close();
}
