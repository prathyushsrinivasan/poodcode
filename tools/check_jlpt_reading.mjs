// Run against npm run dev:mock. Like the other UI check tools, supply a local
// Chromium and playwright-core rather than adding browser binaries to the app.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
const arg = (name, fallback) => {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : fallback;
};
const base = arg("base", "http://localhost:5180");
const modulePath = arg("playwright", "playwright-core");
const { chromium } = await import(modulePath === "playwright-core" ? modulePath : pathToFileURL(modulePath).href);
const browser = await chromium.launch({ executablePath: arg("chromium", process.env.CHROMIUM_PATH), headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const page = await context.newPage();
page.setDefaultTimeout(12_000);
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
const root = "/japanese/n2/reading";
const go = async (route) => {
  const url = `${base}/#${route}`;
  if (page.url() === url) await page.reload();
  else await page.goto(url);
  await page.locator(".dokkai-page").waitFor();
};
const saved = () => page.evaluate(() => JSON.parse(JSON.parse(localStorage.getItem("poodcode.mock.v1") ?? "{}").settings?.["jlpt-n2-reading-v1"] ?? "{}"));
const waitSaved = async (predicate) => {
  for (let i = 0; i < 40; i++) { const value = await saved(); if (predicate(value)) return value; await page.waitForTimeout(50); }
  throw new Error("Expected reading progress was not persisted");
};
try {
  await go(root);
  const corpus = await page.evaluate(async () => {
    const { READING_PASSAGES } = await import("/src/data/dokkai/index.ts");
    const { characterCount, readingSegments } = await import("/src/lib/dokkaiText.ts");
    const { COMMON_READING_WORDS } = await import("/src/data/dokkai/vocabulary.ts");
    return { passages: READING_PASSAGES, sizes: READING_PASSAGES.map((p) => ({ id: p.id, kind: p.kind,
      lengths: p.texts.map((t) => characterCount(t.text)), glosses: p.texts.map((t) => readingSegments(t.text, COMMON_READING_WORDS).filter((s) => s.word).length) })) };
  });
  assert.equal(corpus.passages.filter((p) => p.kind === "short").length, 100);
  const medium = corpus.passages.filter((p) => p.kind === "medium");
  assert.equal(medium.length, 100);
  assert.equal(medium.flatMap((p) => p.questions).length, 200);
  assert.equal(corpus.passages.length, 208);
  assert.equal(corpus.passages.flatMap((p) => p.questions).length, 318);
  for (const size of corpus.sizes.filter((p) => p.kind === "medium" && Number(p.id.slice(7)) > 5)) {
    assert.ok(size.lengths.every((n) => n >= 450 && n <= 550), `${size.id}: new medium length`);
  }
  console.log("Corpus:", JSON.stringify(Object.fromEntries(["short", "medium", "ab", "long", "information"].map((kind) => {
    const texts = corpus.sizes.filter((p) => p.kind === kind).flatMap((p) => p.lengths);
    return [kind, { passages: corpus.sizes.filter((p) => p.kind === kind).length, min: Math.min(...texts), max: Math.max(...texts) }];
  }))));
  for (const section of ["short", "medium", "ab", "long", "information"]) {
    await go(`${root}/${section}`);
    assert.ok(await page.locator(".dokkai-library-card").count());
    const passage = corpus.passages.find((p) => p.kind === section);
    await go(`${root}/${section}/${passage.id}`);
    assert.equal(await page.locator(".dokkai-passage").count(), section === "ab" ? 2 : 1);
    assert.ok(await page.locator(".dokkai-word").count());
  }
  const first = corpus.passages[0];
  console.log("Five reading formats render; checking study results.");
  const q = first.questions[0];
  await go(`${root}/short/${first.id}`);
  console.log("Independent results persisted; checking assisted study and saved words.");
  await page.locator(`input[name="${q.id}"]`).nth(q.answer).check();
  await page.getByRole("button", { name: "Check answers", exact: true }).click();
  await page.getByText("Recorded as independent study.", { exact: true }).waitFor();
  assert.ok(await page.locator(".dokkai-evidence").count());
  await waitSaved((s) => s.results?.[q.id]?.independent?.lastCorrect === true);

  await go(`${root}/short/${first.id}`);
  await page.getByRole("button", { name: "Bookmark passage", exact: true }).click();
  const lookup = page.locator(".dokkai-reader .dokkai-word").first();
  await lookup.click();
  await page.getByRole("dialog").waitFor();
  assert.ok((await page.locator(".dokkai-kana").innerText()).length);
  await page.getByRole("button", { name: "Save for vocabulary review", exact: true }).click();
  await page.keyboard.press("Escape");
  await page.getByRole("dialog").waitFor({ state: "hidden" });
  await page.locator(`input[name="${q.id}"]`).nth((q.answer + 1) % 4).check();
  await page.getByRole("button", { name: "Check answers", exact: true }).click();
  await page.getByText("Recorded as study with help.", { exact: true }).waitFor();
  await waitSaved((s) => s.results?.[q.id]?.assisted?.lastCorrect === false && Object.keys(s.words ?? {}).length === 1 && s.bookmarks?.includes(first.id));
  await go(`${root}/short`);
  await page.getByRole("combobox", { name: /^Show/ }).selectOption("mistakes");
  assert.equal(await page.locator(".dokkai-library-card").count(), 1);
  await page.getByRole("combobox", { name: /^Show/ }).selectOption("bookmarks");
  assert.equal(await page.locator(".dokkai-library-card").count(), 1);
  await go(`${root}/vocabulary`);
  await page.getByRole("button", { name: "Review due words", exact: true }).click();
  await page.getByRole("button", { name: "Reveal reading and meaning", exact: true }).click();
  await page.getByRole("button", { name: "Remembered", exact: true }).click();
  await page.getByRole("heading", { name: "Vocabulary round complete", exact: true }).waitFor();
  await waitSaved((s) => Object.values(s.words ?? {}).some((w) => w.reviews === 1 && w.interval === 1));

  await go(`${root}/short/${first.id}?mode=timed&minutes=1`);
  console.log("Saved vocabulary review passed; checking timed submission.");
  await page.getByRole("button", { name: "Begin timed practice", exact: true }).click();
  assert.equal(await page.locator(".dokkai-word").count(), 0);
  assert.equal(await page.locator(".dokkai-evidence").count(), 0);
  await page.locator(`input[name="${q.id}"]`).nth(q.answer).check();
  await page.getByRole("button", { name: "Finish and review answers", exact: true }).click();
  await page.getByText(/Round submitted\./).waitFor();
  await waitSaved((s) => s.results?.[q.id]?.timed?.lastCorrect === true);

  const second = corpus.passages[1];
  console.log("Timed submission passed; checking timeout.");
  await page.clock.install();
  await go(`${root}/short/${second.id}?mode=timed&minutes=1`);
  await page.getByRole("button", { name: "Begin timed practice", exact: true }).click();
  await page.clock.fastForward(61_000);
  await page.getByText(/Time is up\./).waitFor();
  const result = await waitSaved((s) => s.results?.[second.questions[0].id]?.timed?.lastCorrect === false);
  assert.equal(result.results[second.questions[0].id].timed.attempts, 1);
  await page.clock.resume();

  console.log("Checking expanded 中文 sets, review, persistence and timed expiry.");
  await go(`${root}/medium`);
  await page.getByText("100 passages match · Set 1 of 10", { exact: true }).waitFor();
  for (let i = 1; i < 10; i++) await page.getByRole("button", { name: "Next set", exact: true }).click();
  await page.getByText("100 passages match · Set 10 of 10", { exact: true }).waitFor();
  assert.equal(await page.locator(".dokkai-library-card").count(), 10);
  const setLink = page.getByRole("link", { name: "Practice this set · 10 passages", exact: true });
  assert.equal(new URL(`${base}/${await setLink.getAttribute("href")}`).hash.includes("round=set"), true);
  await setLink.click();
  await page.getByRole("heading", { name: medium[90].title, exact: true }).waitFor();
  assert.equal(await page.locator(".n2-choice-group").count(), 2);

  const last = medium.at(-1);
  await go(`${root}/medium/${last.id}`);
  assert.equal(await page.getByText("English translation", { exact: true }).count(), 0);
  for (const question of last.questions) await page.locator(`input[name="${question.id}"]`).nth(question.answer).check();
  await page.getByRole("button", { name: "Check answers", exact: true }).click();
  await page.getByText("Recorded as independent study.", { exact: true }).waitFor();
  await page.getByText("English translation", { exact: true }).click();
  assert.equal(await page.getByText(last.texts[0].translation, { exact: true }).isVisible(), true);
  assert.ok(await page.locator(".dokkai-evidence").count());
  await waitSaved((s) => last.questions.every((q) => s.results?.[q.id]?.independent?.lastCorrect === true));
  await page.getByRole("button", { name: "Bookmark passage", exact: true }).click();
  await waitSaved((s) => s.bookmarks?.includes(last.id));
  await page.reload();
  await page.locator(".dokkai-page").waitFor();
  await page.getByRole("button", { name: "Bookmarked", exact: true }).waitFor();
  const restored = await saved();
  assert.ok(last.questions.every((q) => restored.results[q.id].independent.lastCorrect));

  await page.getByRole("checkbox", { name: "Show kana above annotated words", exact: true }).check();
  assert.ok(await page.locator(".dokkai-passage ruby rt").count());

  // Identical spellings keep the reading for their own occurrence.
  await go(`${root}/medium/medium-068`);
  await page.getByRole("button", { name: "Look up 生物", exact: true }).first().click();
  await page.getByRole("dialog").waitFor();
  assert.equal(await page.locator(".dokkai-kana").innerText(), "せいぶつ");
  await page.keyboard.press("Escape");
  await go(`${root}/medium/medium-096`);
  await page.getByRole("button", { name: "Look up 生物", exact: true }).first().click();
  await page.getByRole("dialog").waitFor();
  assert.equal(await page.locator(".dokkai-kana").innerText(), "なまもの");
  await page.keyboard.press("Escape");
  await go(`${root}/medium/${last.id}`);

  // A grammar lookup in a question must mark both answers as assisted too.
  await page.locator(".n2-choice-group legend .dokkai-word").first().click();
  await page.getByRole("dialog").waitFor();
  await page.getByRole("button", { name: "Save for vocabulary review", exact: true }).click();
  await page.keyboard.press("Escape");
  await page.getByRole("dialog").waitFor({ state: "hidden" });
  for (const question of last.questions) await page.locator(`input[name="${question.id}"]`).nth((question.answer + 1) % 4).check();
  await page.getByRole("button", { name: "Check answers", exact: true }).click();
  await page.getByText("Recorded as study with help.", { exact: true }).waitFor();
  await waitSaved((s) => last.questions.every((q) => s.results?.[q.id]?.assisted?.lastCorrect === false) &&
    Object.values(s.words ?? {}).some((w) => w.source === last.id));
  await go(`${root}/medium`);
  await page.getByRole("combobox", { name: /^Show/ }).selectOption("bookmarks");
  assert.equal(await page.locator(".dokkai-library-card").count(), 1);
  await page.getByRole("combobox", { name: /^Show/ }).selectOption("mistakes");
  assert.equal(await page.locator(".dokkai-library-card").count(), 1);
  await page.getByRole("combobox", { name: /^Result history/ }).selectOption("independent");
  assert.equal(await page.locator(".dokkai-library-card").count(), 0);
  await page.getByRole("combobox", { name: /^Result history/ }).selectOption("assisted");
  assert.equal(await page.locator(".dokkai-library-card").count(), 1);

  await go(`${root}/medium/${last.id}?mode=timed&minutes=1`);
  await page.getByRole("button", { name: "Begin timed practice", exact: true }).click();
  assert.equal(await page.locator(".dokkai-word, .dokkai-evidence, ruby").count(), 0);
  assert.equal(await page.getByText("English translation", { exact: true }).count(), 0);
  await page.locator(`input[name="${last.questions[0].id}"]`).nth(last.questions[0].answer).check();
  await page.clock.fastForward(61_000);
  await page.getByText(/Time is up\./).waitFor();
  const timedMedium = await waitSaved((s) => last.questions.every((q) => s.results?.[q.id]?.timed?.attempts === 1));
  assert.equal(timedMedium.results[last.questions[0].id].timed.lastCorrect, true);
  assert.equal(timedMedium.results[last.questions[1].id].timed.lastCorrect, false);
  assert.ok(last.questions.every((q) => timedMedium.results[q.id].independent.lastCorrect && !timedMedium.results[q.id].assisted.lastCorrect));
  assert.ok(await page.locator(".dokkai-word, .dokkai-evidence").count());
  await page.clock.resume();
  await page.reload();
  await page.locator(".dokkai-page").waitFor();
  assert.deepEqual((await saved()).results[last.questions[1].id], timedMedium.results[last.questions[1].id]);

  // Review rounds must keep their initial membership after a correct answer.
  console.log("Timeout passed; checking round navigation and responsive layouts.");
  await go(`${root}/short/practice?ids=${first.id},${second.id}&round=set`);
  await page.locator(`input[name="${q.id}"]`).nth(q.answer).check();
  await page.getByRole("button", { name: "Check answers", exact: true }).click();
  await page.getByRole("button", { name: "Next passage →", exact: true }).click();
  await page.getByRole("heading", { name: second.title, exact: true }).waitFor();
  await go(`${root}/short/practice?mode=timed&round=set&ids=${first.id},${second.id}`);
  await page.getByRole("button", { name: "Begin timed practice", exact: true }).click();
  await page.locator(`input[name="${q.id}"]`).nth(q.answer).check();
  await page.getByRole("button", { name: "Next passage →", exact: true }).click();
  await page.getByRole("button", { name: "Previous passage", exact: true }).click();
  assert.equal(await page.locator(`input[name="${q.id}"]`).nth(q.answer).isChecked(), true);

  for (const width of [390, 960, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    for (const route of [root, `${root}/short`, `${root}/medium`, `${root}/medium/medium-096`, `${root}/medium/medium-100`, `${root}/ab/ab-001`, `${root}/information/information-003`]) {
      await go(route);
      // Resizing crosses the shell's animated sidebar breakpoint. Wait for
      // settled geometry; an immediate read can inspect the outgoing layout.
      await page.waitForFunction(() => {
        const main = document.getElementById("main");
        return main && main.scrollWidth <= main.clientWidth;
      }, null, { timeout: 3_000 });
      assert.ok(await page.evaluate(() => { const main = document.getElementById("main"); return main.scrollWidth <= main.clientWidth; }), `${route} overflows at ${width}px`);
    }
  }
  if (arg("screenshot", "")) await page.screenshot({ path: arg("screenshot"), fullPage: true });
  if (arg("axe", "")) {
    const source = readFileSync(arg("axe"), "utf8");
    for (const theme of ["light", "dark"]) for (const route of [root, `${root}/short`, `${root}/medium`, `${root}/medium/medium-096`, `${root}/ab/ab-001`, `${root}/information/information-003`, `${root}/vocabulary`]) {
      await go(route);
      await page.evaluate((theme) => { document.documentElement.dataset.theme = theme; }, theme);
      await page.waitForTimeout(300);
      await page.addScriptTag({ content: source });
      const violations = await page.evaluate(async () => (await window.axe.run(document.querySelector(".dokkai-page"), {
        runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"] },
      })).violations.map((v) => ({ id: v.id, targets: v.nodes.map((n) => n.target) })));
      assert.deepEqual(violations, [], `${route} (${theme}) accessibility`);
    }
    console.log("Reading accessibility checks passed in light and dark themes.");
  }
  assert.deepEqual(errors, []);
  console.log("Reading browser checks passed: five formats, 100 中文 passages / ten sets, independent/assisted/timed results, translations, vocabulary save and recall, reload persistence, bookmarks, filtering, stable rounds, multi-question timeout and responsive layouts.");
} finally { await browser.close(); }
