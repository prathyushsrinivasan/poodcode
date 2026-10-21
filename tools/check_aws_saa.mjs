// Run against dev:mock using an existing local Playwright/Chromium installation.
// node tools/check_aws_saa.mjs --base http://127.0.0.1:5182 --playwright PATH --chromium PATH
import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";
const arg = (name, fallback) => {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : fallback;
};
const base = arg("base", "http://127.0.0.1:5182");
const modulePath = arg("playwright");
const { chromium } = await import(modulePath ? pathToFileURL(modulePath).href : "playwright-core");
const browser = await chromium.launch({ executablePath: arg("chromium", process.env.CHROMIUM_PATH), headless: true });
const context = await browser.newContext({ viewport: { width: 1360, height: 900 } });
const page = await context.newPage();
page.setDefaultTimeout(10_000);
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
const go = async (route = "") => {
  await page.goto(`${base}/#/aws-saa${route}`);
  await page.locator(".saa-page h1").waitFor();
};
const stored = () => page.evaluate(async () => {
  const { api } = await import("/src/api.ts");
  const { SAA_PROGRESS_KEY } = await import("/src/lib/awsSaa.ts");
  return JSON.parse((await api.getSettings())[SAA_PROGRESS_KEY] ?? "null");
});
const answer = async (question, picks = question.correct) => {
  const previousAttempts = (await stored())?.questions[question.id]?.attempts ?? 0;
  const inputs = page.locator(".saa-question input");
  assert.equal(await page.getByRole("button", { name: "Check answer", exact: true }).isEnabled(), false);
  for (const pick of picks) await page.locator(`.saa-question input[value="${pick}"]`).check();
  await page.getByRole("button", { name: "Check answer", exact: true }).click();
  await page.locator(".aws-result").waitFor();
  assert.equal(await page.locator(".aws-option-reason").count(), question.options.length);
  assert.equal(await inputs.evaluateAll((elements) => elements.every((input) => input.disabled)), true);
  // The mock backend debounces its localStorage writes after the IPC promise.
  // Wait for the durable fixture before navigation/reload; do not use a fixed delay.
  await page.waitForFunction(({ id, attempts }) => {
    const mock = JSON.parse(localStorage.getItem("poodcode.mock.v1") ?? "null");
    const progress = JSON.parse(mock?.settings?.["aws-saa-c03-quizzes-v1"] ?? "null");
    return (progress?.questions[id]?.attempts ?? 0) >= attempts;
  }, { id: question.id, attempts: previousAttempts + 1 });
};
try {
  await go();
  const questions = await page.evaluate(async () => (await import("/src/data/awsSaa/questions.ts")).SAA_QUESTIONS);
  const topics = await page.evaluate(async () => (await import("/src/data/awsSaa/schema.ts")).SAA_TOPICS);
  const byId = new Map(questions.map((question) => [question.id, question]));
  assert.equal(await page.locator(".aws-lesson-card").count(), 10);
  await page.getByRole("searchbox").fill("Aurora");
  assert.equal(await page.locator(".aws-lesson-card").count(), 1);
  await page.getByRole("searchbox").fill("doesnotexist");
  await page.getByText("No topics match.", { exact: false }).waitFor();
  await page.getByRole("searchbox").fill("");
  // Exercise every authored answer and explanation through actual rendered inputs.
  for (const topic of topics) {
    await go(`/topic/${topic.id}`);
    const items = questions.filter((question) => question.topic === topic.id);
    for (let index = 0; index < items.length; index++) {
      const question = items[index];
      await page.getByText(question.prompt, { exact: true }).waitFor();
      if (question.correct.length > 1) {
        await page.locator(`.saa-question input[value="${question.correct[0]}"]`).check();
        assert.equal(await page.getByRole("button", { name: "Check answer", exact: true }).isEnabled(), false);
        await page.locator(`.saa-question input[value="${question.correct[0]}"]`).uncheck();
      }
      await answer(question);
      await page.getByRole("heading", { name: "Correct", exact: true }).waitFor();
      await page.getByRole("button", { name: index === items.length - 1 ? "View results" : "Next question", exact: true }).click();
    }
    await page.getByRole("heading", { name: "10 / 10 correct", exact: true }).waitFor();
    console.log(`${topic.id}: 10 answers and explanations passed`);
  }
  await go("/daily");
  await page.locator(".saa-question").waitFor();
  const before = await stored();
  const day = Object.keys(before.days)[0];
  const ids = before.days[day].ids;
  const first = byId.get(ids[0]);
  const wrong = first.correct.length === 1 ? [1] : [0, 2];
  await answer(first, wrong);
  await page.getByRole("heading", { name: "Not quite", exact: true }).waitFor();
  // A reload resumes at the next unanswered question with the same fixed IDs.
  await page.reload();
  await page.getByText(byId.get(ids[1]).prompt, { exact: true }).waitFor();
  assert.deepEqual((await stored()).days[day].ids, ids);
  for (let index = 1; index < ids.length; index++) {
    await answer(byId.get(ids[index]));
    await page.getByRole("button", { name: index === ids.length - 1 ? "View results" : "Next question", exact: true }).click();
  }
  await page.getByRole("heading", { name: "4 / 5 correct", exact: true }).waitFor();
  await page.reload();
  await page.getByRole("heading", { name: "4 / 5 correct", exact: true }).waitFor();
  const completed = await stored();
  assert.equal(Object.keys(completed.days[day].answers).length, 5);
  await page.getByRole("button", { name: "Review explanations", exact: true }).click();
  assert.equal(await page.getByRole("button", { name: "Check answer", exact: true }).count(), 0);
  await go("/review");
  await page.getByText(first.prompt, { exact: true }).waitFor();
  await answer(first);
  await page.getByRole("button", { name: "View results", exact: true }).click();
  await page.getByRole("heading", { name: "1 / 1 correct", exact: true }).waitFor();
  await go();
  await go("/review");
  await page.getByRole("heading", { name: "No mistakes waiting", exact: true }).waitFor();
  assert.deepEqual((await stored()).days[day], completed.days[day]);
  // Save failure is visible and retryable, without overwriting stored history.
  await go("/topic/identity");
  await page.evaluate(async () => {
    const { api } = await import("/src/api.ts");
    const original = api.setSetting;
    window.__restoreSaaSave = () => { api.setSetting = original; };
    api.setSetting = async (key, value) => {
      if (key.startsWith("aws-saa-")) throw new Error("Simulated disk error");
      return original(key, value);
    };
  });
  // This submission intentionally cannot persist until retry succeeds.
  await page.locator('.saa-question input[value="0"]').check();
  await page.getByRole("button", { name: "Check answer", exact: true }).click();
  await page.getByRole("button", { name: "Retry saving", exact: true }).waitFor();
  await page.evaluate(() => window.__restoreSaaSave());
  await page.getByRole("button", { name: "Retry saving", exact: true }).click();
  await page.locator(".saa-save-error").waitFor({ state: "detached" });
  // Unmount the SAA section before simulating a fresh failed load.
  await page.evaluate(() => { window.location.hash = "/"; });
  await page.locator(".saa-page").waitFor({ state: "detached" });
  await page.evaluate(async () => {
    const { api } = await import("/src/api.ts");
    const original = api.getSettings;
    window.__restoreSaaLoad = () => { api.getSettings = original; };
    api.getSettings = async () => { throw new Error("Simulated read failure"); };
    window.location.hash = "/aws-saa";
  });
  await page.getByRole("button", { name: "Retry loading", exact: true }).waitFor();
  await page.evaluate(() => window.__restoreSaaLoad());
  await page.getByRole("button", { name: "Retry loading", exact: true }).click();
  await page.getByRole("heading", { name: "AWS SAA-C03", exact: true }).waitFor();
  await go("/practice");
  await page.getByText("Question 1 of 10", { exact: true }).waitFor();
  await go("/topic/not-a-topic");
  await page.getByRole("heading", { name: "Topic not found", exact: true }).waitFor();
  for (const width of [1360, 768, 390]) {
    await page.setViewportSize({ width, height: 900 });
    for (const route of ["", "/topic/identity", "/daily"]) {
      await go(route);
      assert.equal(await page.locator(".saa-page").evaluate((element) => element.scrollWidth > element.clientWidth + 1), false, `${width}px overflow on ${route}`);
    }
  }
  await page.setViewportSize({ width: 1360, height: 1000 });
  await go();
  if (arg("screenshot")) await page.screenshot({ path: arg("screenshot"), fullPage: true });
  assert.deepEqual(errors, []);
  console.log("SAA: all 100 answers and explanations, daily resume, immutable daily score, mistake review, save retry, routes and responsive layouts passed.");
} finally { await browser.close(); }
