/**
 * Map static inline styles onto token classes (UI_ROADMAP C1, C2).
 *
 * C1 defined the tokens and said "then map every existing inline value onto a
 * token". Most of what was left were one-off static objects —
 * `style={{ fontSize: 12 }}`, `style={{ marginBottom: 12 }}`,
 * `style={{ color: "var(--good)" }}` — each choosing its own number. This
 * rewrites exactly those: a `style={{…}}` whose *every* property is a literal
 * this table knows becomes classes from styles/parts/utilities.css, merged
 * into the element's className. Anything dynamic (a width from data, a colour
 * from a variable), or any property not in the table, leaves the whole object
 * alone — so the ratchet's remaining count is the genuinely inline ones.
 *
 * Off-grid spacing snaps to the nearest step of the 4px scale (10 → 8, 6 → 8,
 * 14 → 16); that snapping is the point of the token scale.
 *
 *   node tools/style-codemod.mjs src/pages/Solve.tsx [more files…]   rewrite
 *   node tools/style-codemod.mjs --dry src/…                          report only
 */

import fs from "node:fs";
import ts from "typescript";

const SPACE = [0, 4, 8, 12, 16, 24, 32, 48, 64];
const step = (px) => {
  let best = 0;
  for (let i = 0; i < SPACE.length; i++) if (Math.abs(SPACE[i] - px) < Math.abs(SPACE[best] - px)) best = i;
  return best;
};

const SIDES = {
  margin: "m",
  marginTop: "mt",
  marginBottom: "mb",
  marginLeft: "ml",
  marginRight: "mr",
  padding: "p",
  gap: "gap",
};

const FONT = (px) => (px <= 12 ? "text-xs" : px <= 13.5 ? "text-sm" : px <= 14.5 ? "text-md" : px <= 17 ? "text-lg" : px <= 21 ? "text-xl" : "text-2xl");

const STRINGS = {
  color: {
    "var(--good)": "c-good",
    "var(--bad)": "c-bad",
    "var(--warn)": "c-warn",
    "var(--accent)": "c-accent",
    "var(--text-dim)": "c-dim",
    "var(--text-faint)": "c-faint",
    "var(--text)": "c-text",
    "var(--medium)": "c-medium",
  },
  borderColor: {
    "var(--good)": "border-good",
    "var(--bad)": "border-bad",
    "var(--accent)": "border-accent",
    "var(--warn)": "border-warn",
    "var(--medium)": "border-medium",
  },
  background: { "var(--accent-dim)": "bg-accent-dim", "var(--bg-elev-2)": "bg-elev-2" },
  textAlign: { center: "text-center", left: "text-left", right: "text-right" },
  whiteSpace: { nowrap: "ws-nowrap", "pre-wrap": "pre-wrap", pre: "pre" },
  cursor: { default: "cursor-default", pointer: "cursor-pointer" },
  display: { block: "d-block", flex: "d-flex", "inline-flex": "d-inline-flex", inline: "d-inline", grid: "d-grid" },
  flexDirection: { column: "flex-col" },
  alignItems: { center: "items-center", baseline: "items-baseline", "flex-start": "items-start", "flex-end": "items-end" },
  justifyContent: { "space-between": "justify-between", center: "justify-center", "flex-end": "justify-end" },
  flexWrap: { wrap: "flex-wrap" },
  overflowX: { auto: "overflow-x-auto" },
  overflow: { hidden: "overflow-hidden", auto: "overflow-auto" },
  fontFamily: { "var(--font-mono)": "ff-mono" },
  wordBreak: { "break-word": "break-word", "break-all": "wb-all" },
  fontStyle: { italic: "italic" },
  textDecoration: { underline: "underline", none: "no-underline" },
  width: { "100%": "w-full" },
  flexShrink: {},
  borderStyle: { dashed: "border-dashed" },
};

function classFor(name, init) {
  // Numbers.
  if (ts.isNumericLiteral(init) || (ts.isPrefixUnaryExpression(init) && init.operator === ts.SyntaxKind.MinusToken)) {
    const negative = ts.isPrefixUnaryExpression(init);
    const n = Number(negative ? init.operand.getText() : init.text);
    if (Number.isNaN(n)) return null;
    if (name in SIDES) {
      if (negative) return n === 0 ? `${SIDES[name]}-0` : null;
      return `${SIDES[name]}-${step(n)}`;
    }
    if (name === "fontSize") return FONT(n);
    if (name === "fontWeight") return n >= 600 ? "fw-bold" : n >= 500 ? "fw-medium" : "fw-normal";
    if (name === "flex" && n === 1) return "flex-1";
    if (name === "minWidth" && n === 0) return "min-w-0";
    if (name === "flexShrink" && n === 0) return "flex-none";
    if (name === "opacity") return n <= 0.6 ? "o-60" : n <= 0.8 ? "o-75" : null;
    return null;
  }
  // Strings.
  if (ts.isStringLiteral(init) || ts.isNoSubstitutionTemplateLiteral(init)) {
    const v = init.text;
    if (name === "margin" && v === "0") return "m-0";
    if (name === "flex" && (v === "1" || v === "1 1 0%")) return "flex-1";
    const table = STRINGS[name];
    if (table && table[v]) return table[v];
    return null;
  }
  return null;
}

/** Returns { edits, converted, kept } for one file. */
function transform(file, text) {
  const sf = ts.createSourceFile(file, text, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
  const edits = [];
  let converted = 0;
  let kept = 0;

  const visit = (node) => {
    if (ts.isJsxAttributes(node)) {
      const styleAttr = node.properties.find((p) => ts.isJsxAttribute(p) && p.name.getText() === "style");
      if (
        styleAttr &&
        styleAttr.initializer &&
        ts.isJsxExpression(styleAttr.initializer) &&
        styleAttr.initializer.expression &&
        ts.isObjectLiteralExpression(styleAttr.initializer.expression)
      ) {
        const obj = styleAttr.initializer.expression;
        const classes = [];
        let ok = obj.properties.length > 0;
        for (const prop of obj.properties) {
          if (!ts.isPropertyAssignment(prop)) {
            ok = false;
            break;
          }
          const name = prop.name.getText().replace(/^["']|["']$/g, "");
          const cls = classFor(name, prop.initializer);
          if (!cls) {
            ok = false;
            break;
          }
          classes.push(cls);
        }
        if (ok) {
          converted++;
          const classAttr = node.properties.find((p) => ts.isJsxAttribute(p) && p.name.getText() === "className");
          const add = [...new Set(classes)].join(" ");
          // Remove the style attribute (with the whitespace before it).
          let start = styleAttr.getFullStart();
          edits.push({ start, end: styleAttr.getEnd(), text: "" });
          if (!classAttr) {
            const tagName = node.parent.tagName;
            edits.push({ start: tagName.getEnd(), end: tagName.getEnd(), text: ` className="${add}"` });
          } else if (classAttr.initializer && ts.isStringLiteral(classAttr.initializer)) {
            const cur = classAttr.initializer.text;
            edits.push({
              start: classAttr.initializer.getStart(),
              end: classAttr.initializer.getEnd(),
              text: `"${[cur, add].filter(Boolean).join(" ")}"`,
            });
          } else if (classAttr.initializer && ts.isJsxExpression(classAttr.initializer) && classAttr.initializer.expression) {
            const expr = classAttr.initializer.expression;
            if (ts.isTemplateExpression(expr) || ts.isNoSubstitutionTemplateLiteral(expr)) {
              // Append inside the template literal, before its closing backtick.
              const end = expr.getEnd() - 1;
              edits.push({ start: end, end, text: ` ${add}` });
            } else {
              edits.push({
                start: expr.getStart(),
                end: expr.getEnd(),
                text: `\`\${${expr.getText()}} ${add}\``,
              });
            }
          } else {
            // Unusual className form: leave the style alone after all.
            edits.pop();
            converted--;
            kept++;
          }
        } else {
          kept++;
        }
      }
    }
    ts.forEachChild(node, visit);
  };
  visit(sf);
  return { edits, converted, kept };
}

const dry = process.argv.includes("--dry");
const files = process.argv.slice(2).filter((a) => !a.startsWith("--"));
let total = 0;
for (const file of files) {
  const text = fs.readFileSync(file, "utf8");
  const { edits, converted, kept } = transform(file, text);
  total += converted;
  if (!dry && edits.length) {
    let out = text;
    for (const e of edits.sort((a, b) => b.start - a.start)) out = out.slice(0, e.start) + e.text + out.slice(e.end);
    fs.writeFileSync(file, out);
  }
  console.log(`${file}: ${converted} converted, ${kept} left inline`);
}
console.log(`${dry ? "Would convert" : "Converted"} ${total} inline style objects.`);
