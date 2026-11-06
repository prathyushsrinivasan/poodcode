// npm run dev:mock -- --port 5180
// node tools/check_jlpt_workspace.mjs --playwright PATH/index.mjs --chromium PATH --axe PATH/axe.min.js
import assert from "node:assert/strict";
import { readFile, mkdir } from "node:fs/promises";
import { pathToFileURL } from "node:url";
const arg = (name, fallback) => { const at = process.argv.indexOf(`--${name}`); return at < 0 ? fallback : process.argv[at + 1]; };
const { chromium } = await import(arg("playwright") ? pathToFileURL(arg("playwright")).href : "playwright-core");
const browser = await chromium.launch({ executablePath: arg("chromium"), headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
page.setDefaultTimeout(20_000);
const base = arg("base", "http://127.0.0.1:5180");
const root = "/japanese/n2";
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
const go = async (route) => { await page.goto(`${base}/#${route}`); await page.locator(".n2-page").waitFor(); if (await page.locator(".study-page").count()) await page.getByText("Saved on this device", { exact: true }).waitFor(); };
const data = () => page.evaluate(async () => (await import("/src/lib/useN2Study.ts")).n2StudyStore.getSnapshot().data);
const save = async () => { await page.getByText("Saved on this device", { exact: true }).waitFor(); const revision = (await data()).revision; await page.waitForFunction((rev) => JSON.parse(JSON.parse(localStorage.getItem("poodcode.mock.v1") ?? "{}").settings?.["jlpt-n2-study-v1"] ?? "{}").revision >= rev, revision); };
const settings = () => page.evaluate(async () => (await import("/src/api.ts")).api.getSettings());
const saveNative = async (key) => { const raw = (await settings())[key]; await page.waitForFunction(([k, value]) => JSON.parse(localStorage.getItem("poodcode.mock.v1") ?? "{}").settings?.[k] === value, [key, raw]); };
const a11y = async (label) => {
  if (!arg("axe")) return;
  await page.addScriptTag({ content: await readFile(arg("axe"), "utf8") });
  const violations = await page.evaluate(async () => (await window.axe.run(document.querySelector(".n2-page"), { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21aa"] } })).violations.map((v) => ({ id: v.id, nodes: v.nodes.map((n) => n.target) })));
  assert.deepEqual(violations, [], `${label}: ${JSON.stringify(violations)}`);
};
try {
  await go(root);
  assert.equal(await page.locator(".jlpt-section").count(), 4);
  await page.getByRole("link", { name: "JLPT review · 0 due →" }).click();
  await page.getByRole("heading", { name: "0 due for review" }).waitFor();
  await a11y("review empty");

  await page.getByRole("button", { name: "Practice", exact: true }).click();
  await page.getByLabel("Practice type").selectOption("diagnostic");
  await page.getByText("12 questions ready", { exact: true }).waitFor();
  await page.getByText("Practice options", { exact: true }).click();
  await page.getByLabel("Round size", { exact: true }).selectOption("3");
  await save();
  await page.getByRole("button", { name: "Start round →", exact: true }).click();
  const first = await page.evaluate(async () => { const s = (await import("/src/lib/useN2Study.ts")).n2StudyStore.getSnapshot().data.session; const q = (await import("/src/data/n2Study/index.ts")).STUDY_QUESTION_MAP.get(s.questionIds[0]); return { id: q.id, kind: q.kind, answer: q.kind === "choice" ? String((q.answer + 1) % 4) : "あ" }; });
  if (first.kind === "typed") await page.getByLabel("Reading in hiragana").fill(first.answer);
  else await page.locator(`input[name="answer-${first.id}"][value="${first.answer}"]`).check();
  await page.getByLabel("Confident", { exact: true }).check();
  await page.getByRole("button", { name: "Save for later", exact: true }).click();
  await page.getByRole("button", { name: "Check answer", exact: true }).click();
  await page.getByText("Your mistake note & takeaway", { exact: true }).click();
  await page.getByLabel("What tripped you up?").selectOption("Grammar connection");
  await page.getByLabel("A clue to remember next time").fill("Check the clause before choosing.");
  await page.getByRole("button", { name: "Finish early", exact: true }).click();
  await page.getByRole("button", { name: "Finish & review", exact: true }).click();
  await page.getByRole("heading", { name: "Results & pacing" }).waitFor();
  await save();
  await go(`${root}/review`);
  await page.getByLabel("Review collection").selectOption("reason");
  await page.getByLabel("Mistake reason", { exact: true }).first().selectOption("Grammar connection");
  await page.getByText("1 items in this collection", { exact: true }).waitFor();
  await page.locator("p").filter({ hasText: "Check the clause before choosing." }).waitFor();
  await page.getByLabel("Review collection").selectOption("confident");
  await page.getByText("1 items in this collection", { exact: true }).waitFor();
  await a11y("mistake collection");

  await page.getByRole("button", { name: "Vocabulary", exact: true }).click();
  await page.getByLabel("New list name").fill("Workplace words");
  await page.getByRole("button", { name: "Create list", exact: true }).click();
  await page.getByLabel("Find words to add").fill("せいさん");
  const listId = (await data()).workspace.lists[0].id;
  await page.getByLabel("Add to vocabulary list").first().selectOption(listId);
  assert.equal((await data()).workspace.lists[0].items.length, 1);
  await save();
  await go(`${root}/review?tab=search`);
  await page.getByLabel("Search all JLPT content").fill("せいさん");
  await page.getByText(/results · showing up to 50/).waitFor();
  await a11y("content search");

  await go(`${root}/review?tab=practice`);
  await page.getByLabel("Practice type").selectOption("mini");
  await page.getByRole("button", { name: "Start round →", exact: true }).click();
  await page.getByRole("button", { name: "Flag for later", exact: true }).click();
  await page.locator(".study-answer-options input").first().check();
  const mock = (await data()).session;
  assert.equal(mock.questionIds.length, 10);
  assert.equal(mock.flags.length, 1);
  await save();
  await page.getByRole("button", { name: "← Save & return", exact: true }).click();
  await go(`${root}/study`);
  const restored = (await data()).session;
  assert.equal(restored.deadline, mock.deadline);
  assert.equal(restored.drafts[mock.questionIds[0]].answer, mock.drafts[mock.questionIds[0]].answer);
  await page.getByText(/^Answer sheet ·/).click();
  await page.getByRole("button", { name: "2 · Unanswered", exact: true }).click();
  await a11y("mock answer sheet");
  await page.evaluate(async () => (await import("/src/lib/useN2Study.ts")).n2StudyStore.update((p) => ({ ...p, session: { ...p.session, deadline: Date.now() - 1 } })));
  await page.getByRole("heading", { name: "Results & pacing" }).waitFor();
  assert.equal(Object.keys((await data()).session.results).length, 10);
  await save();
  const attempts = (await data()).attempts.length;
  await go(`${root}/study`);
  assert.equal((await data()).attempts.length, attempts);

  await go(`${root}/affixes/mixed?size=3`);
  await page.locator(".n2-choice input").first().check();
  await page.getByRole("button", { name: "Check answer", exact: true }).click();
  await page.getByRole("button", { name: "Save question", exact: true }).click();
  const affixBefore = await settings();
  await saveNative("jlpt-affixes-progress-v1");
  await page.reload();
  await page.locator(".n2-feedback").waitFor();
  assert.equal((await settings())["jlpt-affixes-progress-v1"], affixBefore["jlpt-affixes-progress-v1"]);
  await page.getByRole("button", { name: "Next question →", exact: true }).click();
  await page.locator(".n2-choice input").nth(1).check();
  const selected = await page.locator(".n2-choice input:checked").inputValue();
  await page.reload(); await page.locator(".n2-exercise").waitFor();
  assert.equal(await page.locator(".n2-choice input:checked").inputValue(), selected);

  await go(`${root}/kanji/mixed?skill=reading&size=3`);
  await page.getByLabel("Type the full word in hiragana").fill("あ");
  await page.getByRole("button", { name: "Check reading", exact: true }).click();
  await page.getByRole("heading", { name: "Check the reading" }).waitFor();
  await saveNative("jlpt-kanji-word-practice-v1");
  await page.reload();
  await page.getByRole("heading", { name: "Check the reading" }).waitFor();
  await a11y("recovered word practice");

  await go(`${root}/reading/short`);
  const passageHref = await page.getByRole("link", { name: "Continue practice", exact: true }).getAttribute("href");
  await go(passageHref.replace(/^#/, "") + "?mode=timed&minutes=1");
  await page.getByRole("button", { name: "Begin timed practice", exact: true }).click();
  await page.locator(".dokkai-choices input").first().check();
  const deadline = await page.evaluate(() => Object.entries(localStorage).find(([key]) => key.startsWith("jlpt-session:") && key.includes("/reading/") && key.endsWith(":deadline")));
  await page.reload(); await page.locator(".dokkai-choices input:checked").waitFor();
  assert.deepEqual(await page.evaluate(() => Object.entries(localStorage).find(([key]) => key.startsWith("jlpt-session:") && key.includes("/reading/") && key.endsWith(":deadline"))), deadline);
  await page.evaluate(([key]) => localStorage.setItem(key, String(Date.now() - 1)), deadline);
  await page.reload(); await page.getByText(/Time is up/).waitFor();
  const readerBefore = (await settings())["jlpt-n2-reading-v1"];
  await saveNative("jlpt-n2-reading-v1");
  await page.reload(); await page.getByText(/Time is up/).waitFor();
  assert.equal((await settings())["jlpt-n2-reading-v1"], readerBefore);

  // A saved-word identity includes its meaning, which can itself contain commas.
  // Personal-list links must preserve the entire identity as one query value.
  await page.evaluate(async () => {
    const { api } = await import("/src/api.ts");
    const { READING_PASSAGES } = await import("/src/data/dokkai/index.ts");
    const { n2StudyStore } = await import("/src/lib/useN2Study.ts"); await n2StudyStore.load();
    const reading = JSON.parse((await api.getSettings())["jlpt-n2-reading-v1"]);
    const word = { text: "確認", reading: "かくにん", meaning: "confirmation, checking", source: READING_PASSAGES[0].id, due: Date.now(), interval: 0, reviews: 0 };
    const key = "確認|かくにん|confirmation, checking"; reading.words[key] = word;
    await api.setSetting("jlpt-n2-reading-v1", JSON.stringify(reading));
    n2StudyStore.update((p) => ({ ...p, workspace: { ...p.workspace, lists: p.workspace.lists.map((l, i) => i === 0 ? { ...l, items: [...l.items, `word:${key}`] } : l) } }));
  });
  await saveNative("jlpt-n2-reading-v1");
  await page.waitForFunction(() => JSON.parse(JSON.parse(localStorage.getItem("poodcode.mock.v1") ?? "{}").settings?.["jlpt-n2-study-v1"] ?? "{}").workspace?.lists[0]?.items.includes("word:確認|かくにん|confirmation, checking"));
  await go(`${root}/review?tab=vocabulary`);
  await page.getByRole("link", { name: "Review saved word list →", exact: true }).click();
  await page.getByRole("heading", { name: "1 saved words · 1 due", exact: true }).waitFor();

  await go(`${root}/review?tab=backup`);
  const downloadEvent = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export JLPT progress", exact: true }).click();
  const download = await downloadEvent;
  const exported = JSON.parse(await readFile(await download.path(), "utf8"));
  assert.equal(exported.format, "poodcode-jlpt");
  assert.equal(JSON.parse(exported.settings["jlpt-n2-study-v1"]).workspace.lists[0].name, "Workplace words");
  await page.getByLabel("Choose a JLPT backup").setInputFiles({ name: "damaged.json", mimeType: "application/json", buffer: Buffer.from(JSON.stringify({ ...exported, settings: { ...exported.settings, theme: "dark" } })) });
  await page.getByRole("alert").filter({ hasText: "Unexpected backup setting" }).waitFor();
  assert.equal(await page.getByRole("button", { name: "Replace the listed JLPT progress" }).count(), 0);
  await page.getByLabel("Choose a JLPT backup").setInputFiles({ name: "jlpt.json", mimeType: "application/json", buffer: Buffer.from(JSON.stringify(exported)) });
  await page.getByRole("heading", { name: "Ready to import" }).waitFor();
  const beforeFailedImport = (await data()).workspace;
  await page.evaluate(async () => {
    const { api } = await import("/src/api.ts"); const original = api.setSetting; let fail = true;
    api.setSetting = (key, raw) => { if (key === "jlpt-affixes-progress-v1" && fail) { fail = false; return Promise.reject(new Error("Simulated import failure")); } return original(key, raw); };
  });
  await page.getByRole("button", { name: "Replace the listed JLPT progress" }).click();
  await page.getByRole("alert").filter({ hasText: "Previous progress was restored" }).waitFor();
  assert.deepEqual((await data()).workspace, beforeFailedImport);
  await page.getByRole("button", { name: "Replace the listed JLPT progress" }).click();
  await page.getByText("JLPT progress imported. Your pre-import backup is available above.", { exact: true }).waitFor();
  await a11y("backup import");
  await go(root);
  await page.getByText("Courses & personal tools", { exact: true }).click();
  await page.getByRole("link", { name: "Word Builder →", exact: true }).waitFor();
  await page.getByRole("link", { name: "Full Sentence Order course →", exact: true }).waitFor();
  await page.getByRole("link", { name: "Affix library →", exact: true }).waitFor();
  await page.setViewportSize({ width: 390, height: 844 });
  await a11y("mobile home");
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1));
  await go(`${root}/review?tab=practice`);
  await a11y("mobile practice");
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1));
  if (arg("screenshot")) { await mkdir(arg("screenshot"), { recursive: true }); await page.screenshot({ path: `${arg("screenshot")}/jlpt-workspace-mobile.png`, fullPage: true }); }
  assert.deepEqual(errors, []);
  console.log("JLPT workspace: guided review, diagnostics, lists, mocks, native recovery, backup, accessibility and mobile layout passed.");
} catch (error) { console.error("Failed at", page.url()); await page.screenshot({ path: "screenshots/jlpt-workspace-failure.png", fullPage: true }); throw error; }
finally { await browser.close(); }
