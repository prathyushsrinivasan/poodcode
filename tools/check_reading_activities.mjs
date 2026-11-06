// Checks optional evidence selection and saved-word transfer against dev:mock.
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
const arg = (name, fallback) => { const i = process.argv.indexOf(`--${name}`); return i < 0 ? fallback : process.argv[i + 1]; };
const { chromium } = await import(arg("playwright") ? pathToFileURL(arg("playwright")).href : "playwright-core");
const browser = await chromium.launch({ executablePath: arg("chromium"), headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const base = arg("base", "http://127.0.0.1:5189");
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
const go = async (path) => {
  await page.goto(`${base}/#/japanese/n2/reading/${path}`);
  await page.locator(".dokkai-page").waitFor();
};
const axe = async () => {
  if (!arg("axe")) return;
  await page.addScriptTag({ content: await readFile(arg("axe"), "utf8") });
  const violations = await page.evaluate(async () => (await window.axe.run(document.querySelector(".dokkai-page"), {
    runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21aa"] },
  })).violations.map((v) => ({ id: v.id, nodes: v.nodes.map((n) => n.target) })));
  assert.deepEqual(violations, []);
};
try {
  await go("short");
  const fixture = await page.evaluate(async () => {
    const { READING_PASSAGES } = await import("/src/data/dokkai/index.ts");
    const { COMMON_READING_WORDS } = await import("/src/data/dokkai/vocabulary.ts");
    const { readingSegments, wordKey } = await import("/src/lib/dokkaiText.ts");
    const { readingTransferExamples } = await import("/src/lib/readingTransfer.ts");
    for (const passage of READING_PASSAGES.filter((p) => p.kind === "short")) {
      for (const segment of readingSegments(passage.texts[0].text, COMMON_READING_WORDS)) {
        if (segment.word && readingTransferExamples(segment.word, passage.id).length) {
          return { passage, word: segment.word, key: wordKey(segment.word) };
        }
      }
    }
    throw Error("No transfer fixture found");
  });
  await go(`short/${fixture.passage.id}`);
  await page.locator(".dokkai-reader").waitFor();
  assert.equal(await page.locator(".reading-evidence-practice input").first().isVisible(), false);
  await page.getByText("Choose supporting sentences", { exact: true }).click();
  const indices = await page.evaluate(async (passage) => {
    const { evidenceSentences, compareEvidence } = await import("/src/lib/readingEvidence.ts");
    return evidenceSentences(passage.texts).flatMap((sentence, index) => compareEvidence(passage.texts, passage.questions[0].evidence, [sentence.id]).matching.length ? [index] : []);
  }, fixture.passage);
  assert.ok(indices.length);
  for (const index of indices) await page.locator(".reading-evidence-practice input").nth(index).check();
  assert.equal(await page.getByText("Your selected sentences overlap all of the supplied evidence.", { exact: true }).count(), 0);
  await page.locator(`input[name="${fixture.passage.questions[0].id}"]`).nth(fixture.passage.questions[0].answer).check();
  await page.getByRole("button", { name: "Check answers", exact: true }).click();
  await page.getByText("Your selected sentences overlap all of the supplied evidence.", { exact: true }).waitFor();
  await axe();
  const mode = await page.evaluate(async (id) => {
    const { api } = await import("/src/api.ts");
    return JSON.parse((await api.getSettings())["jlpt-n2-reading-v1"]).results[id];
  }, fixture.passage.questions[0].id);
  assert.equal(mode.independent.lastCorrect, true, "Choosing evidence must not count as using an answer hint");
  await page.locator(".dokkai-reader").getByRole("button", { name: `Look up ${fixture.word.text}`, exact: true }).first().hover();
  await page.getByRole("dialog", { name: fixture.word.text, exact: true }).waitFor();
  await page.getByRole("button", { name: "Save for vocabulary review", exact: true }).click();
  await page.waitForFunction((key) => {
    const db = JSON.parse(localStorage.getItem("poodcode.mock.v1") ?? "{}");
    return JSON.parse(db.settings?.["jlpt-n2-reading-v1"] ?? "{}").words?.[key];
  }, fixture.key);
  await go("vocabulary");
  await page.locator(".reading-transfer summary").click();
  await page.locator(".reading-transfer a").first().waitFor();
  assert.ok(await page.locator(".reading-transfer a").count());
  for (const href of await page.locator(".reading-transfer a").evaluateAll((links) => links.map((a) => a.getAttribute("href")))) assert.ok(!href.endsWith(`/${fixture.passage.id}`));
  await page.getByRole("button", { name: "Review due words", exact: true }).click();
  await page.locator(".reading-transfer summary").first().click();
  assert.equal(await page.getByRole("button", { name: "Reveal reading and meaning", exact: true }).isVisible(), true);
  await page.getByRole("button", { name: "Reveal reading and meaning", exact: true }).click();
  await page.getByRole("button", { name: "Remembered", exact: true }).click();
  await page.getByRole("heading", { name: "Vocabulary round complete", exact: true }).waitFor();
  for (const width of [390, 960, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.waitForFunction(() => document.documentElement.scrollWidth <= innerWidth + 1, undefined, { timeout: 3000 });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await axe();
  }
  assert.deepEqual(errors, []);
  console.log("Reading activities: evidence selection/feedback, independent grading, exact-sense transfer contexts, review, accessibility and responsive layouts passed.");
} catch (error) {
  console.error(`At ${page.url()}\n${await page.locator(".dokkai-page").innerText().catch(() => "No reader")}`);
  throw error;
} finally { await browser.close(); }
