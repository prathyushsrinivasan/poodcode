import { describe, it, expect } from "vitest";
import {
  codeLines,
  countCodeLines,
  diffLines,
  diffSources,
  diffStats,
  foldUnchanged,
  isCommentOrBlank,
  numberLines,
  type DiffLine,
} from "./lineDiff";

/** Render a diff the way a unified diff would, for readable assertions. */
const render = (lines: DiffLine[]) =>
  lines.map((l) => (l.op === "add" ? "+" : l.op === "del" ? "-" : " ") + l.text);

describe("numberLines", () => {
  it("numbers from 1 and ignores the one trailing newline", () => {
    expect(numberLines("a\nb\n")).toEqual([
      { no: 1, text: "a" },
      { no: 2, text: "b" },
    ]);
  });

  it("drops carriage returns so a CRLF file diffs clean against an LF one", () => {
    expect(numberLines("a\r\nb").map((l) => l.text)).toEqual(["a", "b"]);
  });
});

describe("diffLines", () => {
  it("reports identical texts as all unchanged", () => {
    const d = diffSources("a\nb\nc\n", "a\nb\nc\n");
    expect(d.every((l) => l.op === "same")).toBe(true);
    expect(diffStats(d)).toEqual({ added: 0, removed: 0 });
  });

  it("finds a line inserted in the middle, numbering both sides", () => {
    const d = diffSources("a\nc\n", "a\nb\nc\n");
    expect(render(d)).toEqual([" a", "+b", " c"]);
    expect(d[1]).toEqual({ op: "add", text: "b", oldNo: null, newNo: 2 });
    expect(d[2]).toMatchObject({ oldNo: 2, newNo: 3 });
  });

  it("puts deletions before additions within a replaced run", () => {
    expect(render(diffSources("a\nold\nz\n", "a\nnew\nz\n"))).toEqual([" a", "-old", "+new", " z"]);
  });

  it("handles one side being empty", () => {
    expect(render(diffSources("", "x\ny\n"))).toEqual(["+x", "+y"]);
    expect(render(diffSources("x\ny\n", ""))).toEqual(["-x", "-y"]);
  });

  it("keeps the longest common run rather than the first match it sees", () => {
    // A naive greedy walk matches the first "}" and reports the whole function
    // as rewritten. The LCS keeps the function and adds the route above it.
    const before = "function f() {\n  return 1;\n}\n";
    const after = "if (x) {\n}\nfunction f() {\n  return 1;\n}\n";
    expect(render(diffSources(before, after))).toEqual([
      "+if (x) {",
      "+}",
      " function f() {",
      "   return 1;",
      " }",
    ]);
  });

  it("ignores trailing whitespace but not a change of indentation", () => {
    expect(diffStats(diffSources("a  \n", "a\n"))).toEqual({ added: 0, removed: 0 });
    expect(diffStats(diffSources("a\n", "  a\n"))).toEqual({ added: 1, removed: 1 });
  });

  it("is a valid edit: replaying it turns the old text into the new one", () => {
    const before = "one\ntwo\nthree\nfour\nfive\n";
    const after = "zero\none\nthree\nfour and a half\nfive\nsix\n";
    const d = diffLines(numberLines(before), numberLines(after));
    expect(d.filter((l) => l.op !== "add").map((l) => l.text)).toEqual(
      numberLines(before).map((l) => l.text)
    );
    expect(d.filter((l) => l.op !== "del").map((l) => l.text)).toEqual(
      numberLines(after).map((l) => l.text)
    );
  });
});

describe("code-only diffs", () => {
  it("treats blank lines and whole-line comments as carrying no code", () => {
    expect(isCommentOrBlank("")).toBe(true);
    expect(isCommentOrBlank("   // the store owns identity")).toBe(true);
    expect(isCommentOrBlank("send(res, 201, todo); // created")).toBe(false);
    expect(isCommentOrBlank('const base = "http://localhost";')).toBe(false);
  });

  it("keeps each surviving line's original number", () => {
    expect(codeLines("// header\n\nconst a = 1;\n// note\nconst b = 2;\n")).toEqual([
      { no: 3, text: "const a = 1;" },
      { no: 5, text: "const b = 2;" },
    ]);
    expect(countCodeLines("// header\n\nconst a = 1;\n")).toBe(1);
  });

  it("hides a rewritten comment but still shows the code that changed", () => {
    const before = "// old comment\nconst a = 1;\n";
    const after = "// a much better comment\nconst a = 2;\n";
    expect(diffStats(diffSources(before, after))).toEqual({ added: 2, removed: 2 });
    expect(render(diffSources(before, after, { codeOnly: true }))).toEqual([
      "-const a = 1;",
      "+const a = 2;",
    ]);
  });
});

describe("foldUnchanged", () => {
  const lines = (spec: string): DiffLine[] =>
    [...spec].map((c, i) => ({
      op: c === "+" ? "add" : c === "-" ? "del" : "same",
      text: `L${i}`,
      oldNo: i,
      newNo: i,
    }));

  it("folds a long unchanged middle, keeping context on both sides", () => {
    const chunks = foldUnchanged(lines("+" + "=".repeat(10) + "-"), 2);
    expect(chunks.map((c) => `${c.kind}:${c.lines.length}`)).toEqual([
      "lines:3",
      "gap:6",
      "lines:3",
    ]);
  });

  it("keeps context only on the side of a leading or trailing run that touches a change", () => {
    const chunks = foldUnchanged(lines("=".repeat(8) + "+" + "=".repeat(8)), 3);
    expect(chunks.map((c) => `${c.kind}:${c.lines.length}`)).toEqual([
      "gap:5",
      "lines:7",
      "gap:5",
    ]);
  });

  it("does not fold a run too short to be worth it", () => {
    const chunks = foldUnchanged(lines("+====-"), 2);
    expect(chunks).toHaveLength(1);
    expect(chunks[0]!.kind).toBe("lines");
  });

  it("folds an identical file into a single gap", () => {
    const chunks = foldUnchanged(lines("====="), 3);
    expect(chunks.map((c) => c.kind)).toEqual(["gap"]);
  });

  it("loses no lines", () => {
    const src = lines("==+=========-==-=========+=");
    const total = foldUnchanged(src, 2).reduce((n, c) => n + c.lines.length, 0);
    expect(total).toBe(src.length);
  });
});
