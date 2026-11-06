// Run with dev:mock and the same --playwright/--chromium/--axe arguments as check_n2_study.mjs.
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
const arg = (name, fallback) => { const i = process.argv.indexOf(`--${name}`); return i < 0 ? fallback : process.argv[i + 1]; };
const { chromium } = await import(arg("playwright") ? pathToFileURL(arg("playwright")).href : "playwright-core");
const browser = await chromium.launch({ executablePath: arg("chromium"), headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
const base = arg("base", "http://127.0.0.1:5187");
const go = async (path) => {
  await page.goto(`${base}/#/japanese/n2/${path}`);
  await page.getByText("Saved on this device", { exact: true }).waitFor();
};
const current = () => page.evaluate(async () => {
  const state = (await import("/src/lib/useN2Study.ts")).n2StudyStore.getSnapshot().data;
  const { STUDY_QUESTION_MAP } = await import("/src/data/n2Study/index.ts");
  return { question: STUDY_QUESTION_MAP.get(state.session.questionIds[state.session.position]), state,
    questions: state.session.questionIds.map((id) => STUDY_QUESTION_MAP.get(id)) };
});
const start = async () => page.getByRole("button", { name: "Start practice →", exact: true }).click();
const finish = async () => {
  await page.getByRole("button", { name: "Finish early", exact: true }).click();
  await page.getByRole("button", { name: "Finish & review", exact: true }).click();
  await page.getByRole("heading", { name: "A little clearer than before", exact: true }).waitFor();
  await page.getByText("Saved on this device", { exact: true }).waitFor();
  const revision = (await current()).state.revision;
  // The mock IPC acknowledges before its debounced localStorage write.
  await page.waitForFunction((value) => {
    const db = JSON.parse(localStorage.getItem("poodcode.mock.v1") ?? "{}");
    return JSON.parse(db.settings?.["jlpt-n2-study-v1"] ?? "{}").revision >= value;
  }, revision);
};
const choose = async () => {
  const { question } = await current();
  assert.equal(question.kind, "choice");
  await page.locator(".study-answer-options input").nth(question.answer).check();
  await page.getByRole("button", { name: "Check answer", exact: true }).click();
  await page.getByRole("heading", { name: "Why it fits", exact: true }).waitFor();
  assert.equal((await current()).state.session.results[question.id].correct, true);
};
const axe = async () => {
  if (!arg("axe")) return;
  await page.addScriptTag({ content: await readFile(arg("axe"), "utf8") });
  const violations = await page.evaluate(async () => (await window.axe.run(document.querySelector(".study-page"), {
    runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21aa"] },
  })).violations.map((v) => ({ id: v.id, nodes: v.nodes.map((n) => n.target) })));
  assert.deepEqual(violations, []);
};
try {
  for (const focus of ["kanji-spelling", "visual-kanji", "homophone-spelling", "okurigana"]) {
    await go("practice/kanji-spelling");
    await page.getByText("Practice options", { exact: true }).click();
    await page.getByLabel("Focus", { exact: true }).selectOption(focus);
    await start();
    const { question, questions } = await current();
    assert.ok(questions.every((q) => q.lessonId === focus));
    assert.equal(await page.locator(".study-target").innerText(), question.focus);
    assert.equal(await page.getByRole("heading", { name: "Why it fits", exact: true }).count(), 0);
    await axe(); await choose(); await finish();
  }
  await go("practice/kanji-reading");
  await page.getByText("Practice options", { exact: true }).click();
  await page.getByLabel("Focus", { exact: true }).selectOption("compound-sound-changes");
  await page.getByLabel("Answer format", { exact: true }).selectOption("choice");
  assert.equal(await page.getByRole("button", { name: "Start practice →", exact: true }).isDisabled(), true);
  await page.getByLabel("Answer format", { exact: true }).selectOption("typed");
  await start();
  const { question: typed } = await current();
  await page.getByLabel("Reading in hiragana", { exact: true }).fill(typed.answers[0].slice(0, -1));
  await page.getByRole("button", { name: "Check answer", exact: true }).click();
  assert.ok(await page.locator(".study-explanation mark").count());
  await axe(); await finish();
  await go("practice/kanji-reading");
  await page.getByText("Practice options", { exact: true }).click();
  await page.getByLabel("Focus", { exact: true }).selectOption("reading-choice");
  await start(); await choose(); await finish();
  for (const [practice, focus] of [
    ["context", "collocations"], ["context", "confused-words"], ["context", "vocabulary-particles"],
    ["context", "transitivity"], ["context", "adverbs"], ["paraphrase", "word-senses"],
    ["usage", "vocabulary-register"], ["usage", "usage-repair"],
  ]) {
    await go(`practice/${practice}`);
    await page.getByText("Practice options", { exact: true }).click();
    await page.getByLabel("Focus", { exact: true }).selectOption(focus);
    await start();
    assert.ok((await current()).questions.every((q) => q.lessonId === focus));
    await choose(); await finish();
  }
  await go("practice/context");
  await page.getByText("Practice options", { exact: true }).click();
  // Drill preferences now persist. Verify that behavior, then broaden the
  // focus before independently testing the topic filter.
  assert.equal(await page.getByLabel("Focus", { exact: true }).inputValue(), "adverbs");
  await page.getByLabel("Focus", { exact: true }).selectOption("");
  await page.getByLabel("Topic", { exact: true }).selectOption("Environment");
  await start();
  assert.ok((await current()).questions.every((q) => q.tags.includes("topic:Environment")));
  await choose(); await finish();
  await go("practice/grammar");
  assert.equal(await page.getByLabel("Find a grammar pattern", { exact: true }).isVisible(), false);
  await page.getByText("Grammar reference", { exact: true }).click();
  await page.getByLabel("Find a grammar pattern", { exact: true }).fill("かねない");
  assert.equal(await page.locator(".study-reference").count(), 1);
  await page.getByLabel("Reference meaning group", { exact: true }).selectOption("Possibility");
  await page.locator(".study-reference summary").click();
  await page.getByRole("link", { name: "Practise かねない", exact: true }).click();
  await start();
  assert.ok((await current()).questions.every((q) => q.lessonId === "grammar-risk"));
  await choose(); await finish();
  for (const exercise of ["Formation", "Comparison", "Correction", "Register"]) {
    await go("practice/grammar");
    await page.getByText("Practice options", { exact: true }).click();
    await page.getByLabel("Meaning group", { exact: true }).selectOption("");
    await page.getByLabel("Exercise", { exact: true }).selectOption(exercise);
    if (exercise === "Formation") await page.getByLabel("Meaning group", { exact: true }).selectOption("Cause");
    await start();
    assert.ok((await current()).questions.every((q) => q.tags.includes(`exercise:${exercise}`)));
    if (exercise === "Formation") assert.ok((await current()).questions.every((q) => q.tags.includes("group:Cause")));
    await choose(); await finish();
  }
  await go("practice/text-grammar");
  await page.getByText("Practice options", { exact: true }).click();
  await page.getByLabel("Exercise", { exact: true }).selectOption("Passage grammar");
  await start();
  assert.equal((await current()).question.texts[0].text.split("\n\n").length, 3);
  await axe(); await choose();
  assert.ok(await page.locator(".dokkai-evidence").count());
  await finish();
  for (const focus of ["reading-main-point", "reading-reference", "reading-argument", "reading-fact-opinion", "reading-answer-strength", "reading-summary", "reading-structure", "reading-tables"]) {
    await go("practice/reading-skills");
    await page.getByText("Practice options", { exact: true }).click();
    await page.getByLabel("Focus", { exact: true }).selectOption(focus);
    await start();
    assert.ok((await current()).questions.every((q) => q.lessonId === focus));
    if (focus === "reading-structure") assert.equal(await page.getByText("Sentence breakdown", { exact: true }).count(), 0);
    if (focus === "reading-tables") {
      assert.equal(await page.locator(".study-table-scroll table").count(), 1);
      await page.setViewportSize({ width: 390, height: 950 });
      await page.waitForFunction(() => document.documentElement.scrollWidth <= innerWidth + 1, undefined, { timeout: 3000 });
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    }
    await axe(); await choose();
    if (focus === "reading-structure") {
      await page.getByText("Sentence breakdown", { exact: true }).click();
      assert.ok(await page.locator(".study-explanation").getByText("Main clause:", { exact: false }).count());
    }
    await finish();
    await page.setViewportSize({ width: 1440, height: 1000 });
  }
  for (const width of [390, 960, 1440]) {
    await page.setViewportSize({ width, height: 950 });
    await go("practice/context");
    await page.getByText("Practice options", { exact: true }).click();
    await page.waitForFunction(() => document.documentElement.scrollWidth <= innerWidth + 1, undefined, { timeout: 3000 });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    for (const theme of ["light", "dark"]) {
      await page.evaluate((value) => { document.documentElement.dataset.theme = value; }, theme);
      await axe();
    }
  }
  assert.deepEqual(errors, []);
  console.log("JLPT expansion: spelling, reading corrections/choices, vocabulary topics, grammar reference/drills, multi-blank passages, reading skills/breakdowns/tables, grading, accessibility and responsive options passed.");
} catch (error) {
  console.error(`At ${page.url()}\n${await page.locator(".study-page").innerText().catch(() => "No study page")}`);
  throw error;
} finally { await browser.close(); }
