/** Unified N2 browser checks. Uses external playwright-core and Chromium, like
 * the other UI checks; no browser dependency is shipped in the desktop app.
 * npm run dev:mock -- --port 5180
 * node tools/check_n2_study.mjs --playwright PATH/index.mjs --chromium PATH --axe PATH/axe.min.js --screenshot PATH.png
 */
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
const arg = (name, fallback) => { const i = process.argv.indexOf(`--${name}`); return i < 0 ? fallback : process.argv[i + 1]; };
const modulePath = arg("playwright");
const { chromium } = modulePath ? await import(pathToFileURL(modulePath).href) : await import("playwright-core");
const browser = await chromium.launch({ executablePath: arg("chromium"), headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
page.setDefaultTimeout(20_000);
const base = arg("base", "http://localhost:5180");
const root = "/japanese/n2";
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
const go = async (path) => {
  await page.goto(`${base}/#${path}`);
  await page.locator(".n2-page").waitFor();
  if (await page.locator(".study-page").count()) await page.getByText("Saved on this device", { exact: true }).waitFor();
};
const data = () => page.evaluate(async () => (await import("/src/lib/useN2Study.ts")).n2StudyStore.getSnapshot().data);
const waitSave = async () => {
  await page.getByText("Saved on this device", { exact: true }).waitFor();
  // The mock backend debounces localStorage for 200ms after acknowledging IPC.
  // Native SQLite acknowledges after writing. Wait for the fixture's disk copy
  // before forcing a browser reload in this test.
  const revision = (await data()).revision;
  await page.waitForFunction((value) => {
    const db = JSON.parse(localStorage.getItem("poodcode.mock.v1") ?? "{}");
    return JSON.parse(db.settings?.["jlpt-n2-study-v1"] ?? "{}").revision >= value;
  }, revision);
};
const accessibility = async (label) => {
  if (!arg("axe")) return;
  await page.addScriptTag({ content: await readFile(arg("axe"), "utf8") });
  const violations = await page.evaluate(async () => (await window.axe.run(document.querySelector(".n2-page"), { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21aa"] } })).violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.map((n) => n.target) })));
  assert.deepEqual(violations, [], `${label}: accessibility violations ${JSON.stringify(violations)}`);
};
try {
  await go(root);
  await page.getByRole("heading", { name: "JLPT", exact: true }).waitFor();
  assert.equal(await page.getByRole("tab").count(), 0);
  assert.equal(await page.locator(".jlpt-section").count(), 4);
  assert.equal(await page.locator(".jlpt-practice-link").count(), 14);
  assert.equal(await page.locator(".jlpt-practice-unavailable").count(), 5);
  await accessibility("JLPT home");
  if (arg("screenshot")) await page.screenshot({ path: arg("screenshot").replace(/\.png$/, "-home.png"), fullPage: true });
  // Every available home entry resolves to its intended practice page.
  const destinations = await page.locator(".jlpt-practice-link").evaluateAll((links) => links.map((link) => ({ label: link.textContent.trim(), href: link.getAttribute("href").replace(/^#/, "") })));
  for (const destination of destinations) {
    await go(destination.href);
    assert.equal(await page.getByRole("heading", { name: /not found/i }).count(), 0, destination.label);
    if (destination.href.includes("/reading/")) {
      await page.getByRole("link", { name: "Continue practice", exact: true }).waitFor();
      assert.equal(await page.getByLabel("Search passages").isVisible(), false);
      await page.getByText("Filters & more practice options", { exact: true }).click();
      await page.getByLabel("Search passages").fill("no-matching-passage-xyz");
      await page.getByRole("heading", { name: "No matching passages" }).waitFor();
    } else if (destination.href.includes("/practice/")) {
      await page.getByRole("button", { name: "Start practice →", exact: true }).waitFor();
      for (const detail of await page.locator(".jlpt-tips").all()) assert.equal(await detail.getAttribute("open"), null);
    } else {
      await page.locator(".n2-exercise").waitFor();
    }
    await accessibility(destination.label);
  }
  await go(`${root}/library`);
  await page.waitForURL(`**/#${root}`);
  await page.getByRole("link", { name: "Kanji Reading", exact: true }).click();
  await page.getByRole("button", { name: "Start practice →", exact: true }).click();
  await page.getByLabel("Reading in hiragana", { exact: true }).waitFor();
  await accessibility("Typed question");
  const s = await data(); const first = s.session.questionIds[0];
  const answer = await page.evaluate(async (id) => (await import("/src/data/n2Study/index.ts")).STUDY_QUESTION_MAP.get(id).answers[0], first);
  await page.getByLabel("Reading in hiragana", { exact: true }).fill(answer);
  await page.getByLabel("Confident", { exact: true }).check();
  await page.getByRole("button", { name: "Save for later", exact: true }).click();
  await page.getByRole("button", { name: "Check answer", exact: true }).click();
  await page.getByRole("heading", { name: "Why it fits", exact: true }).waitFor();
  await page.getByText("Your mistake note & takeaway", { exact: true }).click();
  await page.getByLabel("A clue to remember next time").fill("Remember the complete compound.");
  await waitSave();
  assert.equal((await data()).attempts.length, 1);
  await page.getByRole("button", { name: "Next question →", exact: true }).click();
  if (await page.getByRole("button", { name: "Try the questions →", exact: true }).isVisible()) await page.getByRole("button", { name: "Try the questions →", exact: true }).click();
  await page.getByLabel("Reading in hiragana", { exact: true }).fill("とちゅう");
  await page.getByRole("button", { name: "← Save & return", exact: true }).click();
  await page.getByRole("link", { name: "Continue round →", exact: true }).click();
  await page.getByRole("button", { name: "Resume round", exact: true }).click();
  assert.equal(await page.getByLabel("Reading in hiragana", { exact: true }).inputValue(), "とちゅう");
  await page.reload();
  await page.getByRole("button", { name: "Resume round", exact: true }).click();
  assert.equal(await page.getByLabel("Reading in hiragana", { exact: true }).inputValue(), "とちゅう");
  await page.getByRole("button", { name: "Show a hint", exact: true }).click();
  await page.getByRole("button", { name: "Reveal & revisit", exact: true }).click();
  await page.getByRole("button", { name: "Finish early", exact: true }).click();
  await page.getByRole("button", { name: "Finish & review", exact: true }).click();
  await page.getByRole("heading", { name: "A little clearer than before" }).waitFor();
  assert.equal((await data()).attempts.length, 2);
  await accessibility("Round recap");
  assert.ok(await page.locator(".study-recap-item").count() >= 1);
  await accessibility("Review recap");
  // A timed round hides explanations and hints, preserves editable answers,
  // and keeps the original deadline across an app reload.
  await go(`${root}/lesson/wake`);
  await page.getByLabel("Timed practice", { exact: true }).check();
  await page.getByRole("button", { name: "Start practice →", exact: true }).click();
  await page.locator(".study-answer-options").waitFor();
  assert.equal(await page.getByRole("button", { name: "Show a hint", exact: true }).count(), 0);
  const before = await data(); const deadline = before.session.deadline;
  await page.locator(".study-answer-options input").nth(0).check();
  await page.locator(".study-answer-options input").nth(1).check();
  await waitSave(); await page.reload(); await page.locator(".study-answer-options").waitFor();
  assert.equal((await data()).session.deadline, deadline);
  assert.equal(await page.locator(".study-answer-options input").nth(1).isChecked(), true);
  assert.equal((await data()).attempts.length, 2);
  // Simulate background time passing. The real interval effect must finalize
  // once, and a reload must not produce duplicate attempts.
  await page.evaluate(async () => { const { n2StudyStore } = await import("/src/lib/useN2Study.ts"); n2StudyStore.update((p) => ({ ...p, session: { ...p.session, deadline: Date.now() - 1 } })); });
  await page.getByRole("heading", { name: "A little clearer than before" }).waitFor();
  await waitSave(); assert.equal((await data()).attempts.length, 4);
  await page.reload(); await page.getByRole("heading", { name: "A little clearer than before" }).waitFor();
  assert.equal((await data()).attempts.length, 4);
  // Verify all assembly controls through an actual full-order submission.
  await go(`${root}/lesson/assembly-links`);
  await page.getByRole("button", { name: "Start practice →", exact: true }).click();
  await page.locator(".study-fragments").waitFor();
  const order = await page.evaluate(async () => { const p = (await import("/src/lib/useN2Study.ts")).n2StudyStore.getSnapshot().data; const q = (await import("/src/data/n2Study/index.ts")).STUDY_QUESTION_MAP.get(p.session.questionIds[0]); return q.acceptedOrders?.[0] ?? q.order; });
  for (const n of order) await page.locator(".study-fragments button").nth(n).click();
  await page.getByRole("button", { name: "Undo last", exact: true }).click();
  await page.locator(".study-fragments button").nth(order[3]).click();
  await page.getByRole("button", { name: "Check answer", exact: true }).click();
  assert.equal(Object.values((await data()).session.results)[0].correct, true);
  await accessibility("Assembly explanation");
  await page.getByRole("button", { name: "Finish early", exact: true }).click();
  await page.getByRole("button", { name: "Finish & review", exact: true }).click();
  await go(`${root}/lesson/paragraph-links`);
  await page.getByRole("button", { name: "Start practice →", exact: true }).click();
  await page.locator(".study-passage").waitFor();
  assert.equal(await page.getByText("English translation", { exact: true }).count(), 0);
  const paragraphAnswer = await page.evaluate(async () => { const p = (await import("/src/lib/useN2Study.ts")).n2StudyStore.getSnapshot().data; return (await import("/src/data/n2Study/index.ts")).STUDY_QUESTION_MAP.get(p.session.questionIds[0]).answer; });
  await page.locator(".study-answer-options input").nth(paragraphAnswer).check();
  await page.getByRole("button", { name: "Check answer", exact: true }).click();
  assert.ok(await page.locator("mark.dokkai-evidence").count() > 0);
  await accessibility("Text grammar evidence");
  await page.getByRole("button", { name: "Finish early", exact: true }).click();
  await page.getByRole("button", { name: "Finish & review", exact: true }).click();
  await go(`${root}/lesson/reading-ab`);
  await page.getByRole("button", { name: "Start practice →", exact: true }).click();
  await page.locator(".study-passage").first().waitFor();
  assert.equal(await page.locator(".study-passage").count(), 2);
  await accessibility("Paired reading");
  await page.getByRole("button", { name: "Reveal & revisit", exact: true }).click();
  await page.getByText("English translation", { exact: true }).click();
  if (arg("screenshot")) await page.screenshot({ path: arg("screenshot").replace(/\.png$/, "-reading.png"), fullPage: true });
  await page.getByRole("button", { name: "Finish early", exact: true }).click();
  await page.getByRole("button", { name: "Finish & review", exact: true }).click();
  await page.getByRole("button", { name: "Back to JLPT", exact: true }).click();
  for (const theme of ["dark", "light"]) {
    await page.evaluate((value) => document.documentElement.dataset.theme = value, theme);
    for (const width of [390, 960, 1440]) {
      await page.setViewportSize({ width, height: 1000 }); await go(root);
      await page.evaluate(async () => { await document.fonts.ready; await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))); });
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `${theme} ${width}px: horizontal page overflow`);
      await accessibility(`${theme} ${width}px JLPT`);
    }
  }
  if (arg("screenshot")) { await page.evaluate(() => document.documentElement.dataset.theme = "dark"); await page.screenshot({ path: arg("screenshot"), fullPage: true }); }
  assert.deepEqual(errors, []);
  process.stdout.write("JLPT UI passed: four groups, direct practice links, collapsed reading filters, library redirect, guided learning, notes, pause/reload recovery, timed expiry, assembly, recaps, accessibility and responsive themes.\n");
} catch (error) {
  if (arg("screenshot")) await page.screenshot({ path: arg("screenshot"), fullPage: true });
  process.stderr.write(`At ${page.url()}\n${(await page.locator(".n2-page").innerText().catch(() => "No JLPT page")).slice(0, 2000)}\n`);
  throw error;
} finally { await browser.close(); }
