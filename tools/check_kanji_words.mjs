// Run against dev:mock with an existing local browser installation.
// node tools/check_kanji_words.mjs --playwright PATH_TO_INDEX_MJS --chromium PATH_TO_CHROME
import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";
const arg = (name, fallback) => {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : fallback;
};
const base = arg("base", "http://127.0.0.1:5183");
const modulePath = arg("playwright");
const { chromium } = await import(modulePath ? pathToFileURL(modulePath).href : "playwright-core");
const browser = await chromium.launch({ executablePath: arg("chromium", process.env.CHROMIUM_PATH), headless: true });
const page = await browser.newPage({ viewport: { width: 1360, height: 950 } });
page.setDefaultTimeout(10_000);
page.setDefaultNavigationTimeout(60_000);
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
const go = async (path = "") => {
  await page.goto(`${base}/#/japanese/n2/kanji${path}`, { waitUntil: "domcontentloaded" });
  await page.locator(".kw-page h1").waitFor({ timeout: 60_000 });
};
const stored = () => page.evaluate(async () => {
  const { api } = await import("/src/api.ts");
  return JSON.parse((await api.getSettings())["jlpt-kanji-word-practice-v1"] ?? '{"version":1,"words":{}}');
});
const waitSaved = async (id, skill, attempts) => page.waitForFunction(({ id, skill, attempts }) => {
  const mock = JSON.parse(localStorage.getItem("poodcode.mock.v1") ?? "null");
  const progress = JSON.parse(mock?.settings?.["jlpt-kanji-word-practice-v1"] ?? "null");
  return (progress?.words[id]?.[skill]?.attempts ?? 0) >= attempts;
}, { id, skill, attempts });
const finish = async (word, { reading = word.readings[0], wrongMeaning = false } = {}) => {
  const before = (await stored()).words[word.id];
  await page.getByLabel("Type the full word in hiragana", { exact: true }).fill(reading);
  await page.getByRole("button", { name: "Check reading", exact: true }).click();
  await page.getByRole("heading", { name: "Reading correct", exact: true }).waitFor();
  assert.equal(await page.locator(".kw-option-reason").count(), 0);
  assert.equal(await page.locator(".kw-note").count(), 0);
  await page.getByRole("button", { name: "Continue to meaning", exact: true }).click();
  const picks = word.options.flatMap((option, index) => option.correct ? [index] : []);
  if (wrongMeaning) picks[picks.length - 1] = word.options.length - 1;
  if (picks.length > 1) {
    await page.locator(`.kw-meaning-options input[value="${picks[0]}"]`).check();
    assert.equal(await page.getByRole("button", { name: "Check meaning", exact: true }).isDisabled(), true);
  }
  for (const index of picks) await page.locator(`.kw-meaning-options input[value="${index}"]`).check();
  await page.getByRole("button", { name: "Check meaning", exact: true }).click();
  await page.getByRole("heading", { name: wrongMeaning ? "Review the meanings" : "Meaning correct", exact: true }).waitFor();
  assert.equal(await page.locator(".kw-option-reason").count(), word.options.length);
  await waitSaved(word.id, "meaning", (before?.meaning?.attempts ?? 0) + 1);
  await waitSaved(word.id, "reading", (before?.reading?.attempts ?? 0) + 1);
  await page.getByRole("button", { name: "Next word / results", exact: true }).click();
};
try {
  await go();
  const { words, groups } = await page.evaluate(async () => {
    const data = await import("/src/data/kanjiWords/index.ts");
    return { words: data.KANJI_WORDS, groups: data.KANJI_GROUPS };
  });
  assert.equal(groups.length, 20);
  assert.equal(await page.locator(".kw-kanji-card").count(), 20);
  // Every family exposes every applicable bank entry without leaking its answers.
  for (const group of groups) {
    await go(`/${group.id}`);
    assert.equal(await page.locator(".kw-word-card").count(), words.filter((word) => word.written.includes(group.kanji)).length);
    assert.equal(await page.locator(".kw-library-answer").count(), 0);
  }
  await go("/life");
  await page.getByLabel("Show readings & meanings", { exact: true }).check();
  assert.ok(await page.locator(".kw-library-answer").count() > 20);
  await page.getByLabel("Show readings & meanings", { exact: true }).uncheck();
  await page.getByRole("searchbox").fill("生地");
  assert.equal(await page.locator(".kw-word-card").count(), 2);
  await page.getByRole("searchbox").fill("nomatchingword");
  await page.getByText("No words match these filters.", { exact: false }).waitFor();
  // Representative entries from every group, plus all distinct homograph readings.
  const samples = new Map();
  for (const group of groups) {
    const word = words.find((word) => word.written.includes(group.kanji) && !samples.has(word.id));
    samples.set(word.id, word);
  }
  for (const word of words) if (["生地", "人気", "表", "分別", "心中", "生物"].includes(word.written)) samples.set(word.id, word);
  for (const word of samples.values()) {
    await go(`/word/${word.id}`);
    await finish(word);
    await page.getByRole("heading", { name: "1 / 1 words correct in both steps", exact: true }).waitFor();
  }
  console.log(`All 20 family libraries and ${samples.size} two-step representative quizzes passed.`);
  const shared = words.find((word) => word.written === "生産性");
  await go(`/word/${shared.id}`);
  const input = page.getByLabel("Type the full word in hiragana", { exact: true });
  await input.fill("seisansei");
  assert.equal(await page.getByRole("button", { name: "Check reading", exact: true }).isDisabled(), true);
  await input.fill("セイサンセイ");
  assert.equal(await page.getByRole("button", { name: "Check reading", exact: true }).isDisabled(), true);
  await input.fill(shared.readings[0]);
  await input.dispatchEvent("compositionstart");
  await input.press("Enter");
  assert.equal(await page.locator(".n2-feedback").count(), 0, "IME Enter must not grade during composition");
  await input.dispatchEvent("compositionend");
  await input.press("Enter");
  await page.getByRole("heading", { name: "Reading correct", exact: true }).waitFor();
  await waitSaved(shared.id, "reading", 1);
  await page.reload();
  await page.locator(".kw-exercise").waitFor();
  assert.equal((await stored()).words[shared.id].reading.lastCorrect, true);
  assert.equal((await stored()).words[shared.id].meaning, undefined);
  await finish(shared);
  await go("/life");
  assert.match(await page.locator(".kw-word-card").filter({ has: page.getByRole("heading", { name: "生産性", exact: true }) }).innerText(), /Reading: correct · Meaning: correct/);
  await go("/nature");
  assert.match(await page.locator(".kw-word-card").filter({ has: page.getByRole("heading", { name: "生産性", exact: true }) }).innerText(), /Reading: correct · Meaning: correct/);
  // Missing a single meaning makes only that skill incorrect and reviewable.
  const multi = words.find((word) => word.written === "生地" && word.readings.includes("きじ"));
  await go(`/word/${multi.id}`);
  await finish(multi, { wrongMeaning: true });
  const failed = (await stored()).words[multi.id];
  assert.equal(failed.reading.lastCorrect, true);
  assert.equal(failed.meaning.lastCorrect, false);
  await go("/review");
  await page.getByRole("heading", { name: multi.written, exact: true }).waitFor();
  await finish(multi);
  await go();
  await go("/review");
  await page.getByRole("heading", { name: "No matching words to practice", exact: true }).waitFor();
  // Filters must constrain the practice pool as well as the visible library.
  await go("/learning");
  await page.getByLabel("Estimated level", { exact: true }).selectOption("N1");
  await page.getByRole("link", { name: "Practice up to 10 words", exact: true }).click();
  await page.locator(".kw-exercise").waitFor();
  assert.match(await page.locator(".kw-exercise").innerText(), /N1/);
  await go("/mixed");
  await page.getByText("Word 1 of 5", { exact: true }).waitFor();
  // Failed writes remain visible and can be retried.
  await go(`/word/${shared.id}`);
  await page.evaluate(async () => {
    const { api } = await import("/src/api.ts");
    const original = api.setSetting;
    window.__restoreKanjiSave = () => { api.setSetting = original; };
    api.setSetting = async (key, value) => { if (key === "jlpt-kanji-word-practice-v1") throw Error("Simulated disk failure"); return original(key, value); };
  });
  await page.getByRole("button", { name: "Reveal reading", exact: true }).click();
  await page.getByRole("button", { name: "Retry saving progress", exact: true }).waitFor();
  await page.evaluate(() => window.__restoreKanjiSave());
  await page.getByRole("button", { name: "Retry saving progress", exact: true }).click();
  await page.getByRole("button", { name: "Retry saving progress", exact: true }).waitFor({ state: "detached" });
  for (const width of [1360, 768, 390]) {
    await page.setViewportSize({ width, height: 950 });
    for (const route of ["", "/life", `/word/${multi.id}`]) {
      await go(route);
      assert.equal(await page.locator(".kw-page").evaluate((element) => element.scrollWidth > element.clientWidth + 1), false, `${width}px overflow on ${route}`);
    }
  }
  await page.setViewportSize({ width: 1360, height: 1000 });
  await go();
  if (arg("screenshot")) await page.screenshot({ path: arg("screenshot"), fullPage: true });
  assert.deepEqual(errors, []);
  console.log("Kanji: reading/meaning separation, homographs, exact multiple answers, IME, persistence, shared progress, review, filters, save retry and responsive layouts passed.");
} finally { await browser.close(); }
