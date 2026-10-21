/** Run against dev:mock with an existing Playwright installation.
 * node tools/check_aws_mla.mjs --base http://127.0.0.1:5180 --playwright PATH --chromium PATH
 * Covers reading, exact-choice grading, explanations, retries, persistence and layout.
 */
import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";

const arg = (name, fallback) => {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : fallback;
};
const base = arg("base", "http://127.0.0.1:5180");
const modulePath = arg("playwright");
const { chromium } = await import(modulePath ? pathToFileURL(modulePath).href : "playwright-core");
const browser = await chromium.launch({ executablePath: arg("chromium", process.env.CHROMIUM_PATH) });
const page = await browser.newPage({ viewport: { width: 1360, height: 900 } });
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
const go = async (id = "") => {
  await page.goto(`${base}/#/aws-mla${id ? `/${id}` : ""}`);
  await page.locator(".aws-page h1").waitFor();
};
try {
  await go();
  const lessons = await page.evaluate(async () => (await import("/src/data/awsMla/lessons.ts")).AWS_LESSONS);
  const full = lessons.filter((lesson) => lesson.teaching);
  assert.equal(full.length, 6);
  assert.equal(await page.locator(".aws-module-sequence li").count(), 6);
  await page.getByRole("link", { name: /Start 1-lesson session/ }).waitFor();
  for (const lesson of lessons) {
    await go(lesson.id);
    assert.equal(await page.locator("textarea").count(), 0);
    if (!lesson.teaching) continue;
    assert.equal(await page.locator(".aws-teaching-section").count(), lesson.teaching.sections.length);
    assert.equal(await page.locator(".aws-resources a").count(), lesson.references.length);
    // Learning is available immediately; switching views does not lose selections.
    await page.getByRole("button", { name: "Start scenario checks", exact: true }).click();
    const submit = page.getByRole("button", { name: "Check answers & schedule review", exact: true });
    assert.equal(await submit.isEnabled(), false);
    for (const question of lesson.questions) {
      for (const index of question.answers) {
        await page.getByRole(question.answers.length > 1 ? "checkbox" : "radio", { name: question.options[index].text, exact: true }).check();
      }
    }
    await page.getByRole("button", { name: "1 · Learn the topic", exact: true }).click();
    await page.getByRole("button", { name: /^2 · Scenario checks/ }).click();
    assert.equal(await submit.isEnabled(), true);
    await submit.click();
    await page.getByRole("heading", { name: "6 / 6 correct", exact: true }).waitFor();
    assert.equal(await page.locator(".aws-option-reason").count(), lesson.questions.reduce((sum, question) => sum + question.options.length, 0));
    // Feedback links remain usable after the answer inputs are disabled.
    await page.getByRole("button", { name: "Revisit the explanation", exact: true }).first().click();
    assert.equal(await page.locator(".aws-teaching-section").count(), lesson.teaching.sections.length);
    await page.getByRole("button", { name: /^2 · Scenario checks/ }).click();
    await page.getByRole("heading", { name: "6 / 6 correct", exact: true }).waitFor();
    await page.getByRole("button", { name: "Try these checks again", exact: true }).click();
    assert.equal(await page.locator(".aws-quiz input:checked").count(), 0);
    assert.equal(await submit.isEnabled(), false);
  }
  // Miss a correct multi-response option while selecting the required count.
  const first = full[0];
  await go(first.id);
  await page.getByRole("button", { name: "Start scenario checks", exact: true }).click();
  for (const question of first.questions) {
    const picks = [...question.answers];
    if (question.answers.length > 1) picks[0] = question.options.findIndex((_, index) => !question.answers.includes(index));
    for (const index of picks) await page.getByRole(question.answers.length > 1 ? "checkbox" : "radio", { name: question.options[index].text, exact: true }).check();
  }
  await page.getByRole("button", { name: "Check answers & schedule review", exact: true }).click();
  await page.getByRole("heading", { name: "5 / 6 correct", exact: true }).waitFor();
  assert.equal(await page.getByText("Missed correct option.", { exact: true }).count(), 1);
  await go();
  await page.reload();
  await page.locator(".aws-summary strong").first().waitFor();
  assert.equal((await page.locator(".aws-summary strong").first().innerText()).split(/\s/)[0], "6");
  for (const width of [600, 960, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    for (const id of ["", first.id, full.at(-1).id]) {
      await go(id);
      const overflow = await page.locator(".aws-page").evaluate((element) => element.scrollWidth > element.clientWidth + 1);
      assert.equal(overflow, false, `Horizontal overflow at ${width}px on ${id || "home"}`);
    }
  }
  assert.deepEqual(errors, []);
  console.log("AWS course: 24 reading routes, 36 full-lesson answers, feedback, retries, persistence and responsive layout passed.");
} finally {
  await browser.close();
}
