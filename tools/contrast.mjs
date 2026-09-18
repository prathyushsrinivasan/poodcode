/**
 * Contrast audit for the design tokens.
 *
 * Reads the theme blocks out of `src/styles/parts/tokens.css` and checks every pair
 * that the UI actually puts together — faint text on a card, a button label on
 * its fill, a difficulty colour on the page background. WCAG AA wants 4.5:1 for
 * body text and 3:1 for large text and UI boundaries.
 *
 * Run: `node tools/contrast.mjs`  (add `--json` for machine-readable output)
 * Exits non-zero if any required pair fails, so CI can gate on it.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
// Tokens plus the appearance variants, concatenated in import order so a
// high-contrast override is seen after the value it overrides.
const css = ["src/styles/parts/tokens.css", "src/styles/parts/appearance.css"]
  .map((f) => fs.readFileSync(path.join(root, f), "utf8"))
  .join(String.fromCharCode(10));

/* --------------------------------------------------------------- parsing */

/** Pull `--name: value;` declarations out of one selector's block. */
function block(selector) {
  const i = css.indexOf(selector);
  if (i === -1) throw new Error(`no such selector: ${selector}`);
  const open = css.indexOf("{", i);
  const close = css.indexOf("}", open);
  const out = {};
  for (const line of css.slice(open + 1, close).split("\n")) {
    const m = line.match(/^\s*(--[\w-]+)\s*:\s*([^;]+);/);
    if (m) out[m[1]] = m[2].trim();
  }
  return out;
}

const base = block(":root {");
const themes = {
  dark: { ...base, ...block(':root[data-theme="dark"] {') },
  light: { ...base, ...block(':root[data-theme="light"] {') },
  "dark-hc": {
    ...base,
    ...block(':root[data-theme="dark"] {'),
    ...block(':root[data-theme="dark"][data-contrast="high"]'),
  },
  "light-hc": {
    ...base,
    ...block(':root[data-theme="light"] {'),
    ...block(':root[data-theme="light"][data-contrast="high"]'),
  },
};

/* ---------------------------------------------------------------- colour */

function parseHex(v) {
  const m = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(v.trim());
  if (!m) return null;
  let h = m[1];
  if (h.length === 3) h = h.split("").map((c) => c + c).join("");
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
}

function resolve(tokens, value) {
  let v = value.trim();
  for (let i = 0; i < 5; i++) {
    const m = /^var\((--[\w-]+)\)$/.exec(v);
    if (!m) break;
    v = (tokens[m[1]] ?? "").trim();
  }
  return parseHex(v);
}

function luminance([r, g, b]) {
  const f = (c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
}

function ratio(fg, bg) {
  const a = luminance(fg);
  const b = luminance(bg);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}

/* ----------------------------------------------------------------- pairs */

/** [foreground, background, minimum, what it is]. `#fff` is a literal. */
const PAIRS = [
  ["--text", "--bg", 4.5, "body text on the page"],
  ["--text", "--bg-elev", 4.5, "body text on a card"],
  ["--text-dim", "--bg", 4.5, "secondary text on the page"],
  ["--text-dim", "--bg-elev", 4.5, "secondary text on a card"],
  ["--text-faint", "--bg", 4.5, "faint text on the page"],
  ["--text-faint", "--bg-elev", 4.5, "faint text on a card"],
  ["--on-accent", "--accent", 4.5, "label on the primary button"],
  ["--on-good", "--good", 4.5, "label on the success button"],
  ["--on-bad", "--bad", 4.5, "label on the danger button"],
  ["--on-warn", "--warn", 4.5, "label on a warning fill"],
  ["--accent", "--bg", 4.5, "link on the page"],
  ["--accent", "--bg-elev", 4.5, "link on a card"],
  ["--good", "--bg-elev", 4.5, "pass verdict on a card"],
  ["--bad", "--bg-elev", 4.5, "fail verdict on a card"],
  ["--warn", "--bg-elev", 4.5, "warn verdict on a card"],
  ["--intro", "--bg-elev", 4.5, "Intro difficulty on a card"],
  ["--easy", "--bg-elev", 4.5, "Easy difficulty on a card"],
  ["--medium", "--bg-elev", 4.5, "Medium difficulty on a card"],
  ["--hard", "--bg-elev", 4.5, "Hard difficulty on a card"],
  ["--focus-ring", "--bg", 3, "focus ring on the page"],
  ["--focus-ring", "--bg-elev", 3, "focus ring on a card"],
];

/** Reported for information, not enforced. A card's edge is decorative — the
 * card is already identifiable by its background — so WCAG 1.4.11 does not
 * apply to it. `--border-strong` is the token to reach for when a border
 * genuinely is the only thing marking a control. */
const ADVISORY = [
  ["--border", "--bg", 3, "card edge against the page"],
  ["--border-strong", "--bg", 3, "strong border against the page"],
  ["--border-strong", "--bg-elev", 3, "strong border on a card"],
];

/* ----------------------------------------------------------------- report */

const json = process.argv.includes("--json");
const results = [];
let failures = 0;

for (const [themeName, tokens] of Object.entries(themes)) {
  for (const [fgTok, bgTok, min, label, advisory] of [
    ...PAIRS,
    ...ADVISORY.map((pair) => [...pair, true]),
  ]) {
    const fg = fgTok.startsWith("#") ? parseHex(fgTok) : resolve(tokens, tokens[fgTok] ?? "");
    const bg = bgTok.startsWith("#") ? parseHex(bgTok) : resolve(tokens, tokens[bgTok] ?? "");
    if (!fg || !bg) {
      results.push({ theme: themeName, label, fgTok, bgTok, ratio: null, min, ok: false, missing: true, advisory: !!advisory });
      if (!advisory) failures++;
      continue;
    }
    const r = ratio(fg, bg);
    const ok = r >= min;
    if (!ok && !advisory) failures++;
    results.push({ theme: themeName, label, fgTok, bgTok, ratio: +r.toFixed(2), min, ok, missing: false, advisory: !!advisory });
  }
}

if (json) {
  console.log(JSON.stringify({ failures, results }, null, 2));
} else {
  for (const theme of Object.keys(themes)) {
    console.log(`\n  ${theme.toUpperCase()}`);
    for (const r of results.filter((x) => x.theme === theme)) {
      const mark = r.missing ? "??" : r.ok ? "ok" : r.advisory ? "note" : "FAIL";
      const val = r.missing ? "unresolved" : `${r.ratio.toFixed(2)}:1`.padStart(7);
      console.log(
        `  ${mark.padEnd(4)} ${val}  (needs ${r.min})  ${r.label}  [${r.fgTok} on ${r.bgTok}]`
      );
    }
  }
  const required = results.filter((r) => !r.advisory).length;
  console.log(
    failures === 0
      ? `
  All ${required} required token pairs pass.
`
      : `
  ${failures} of ${required} required pairs fail.
`
  );

}

process.exit(failures === 0 ? 0 : 1);
