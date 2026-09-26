import { describe, expect, it } from "vitest";
import { fileNameProblem, isMultiFile, joinFiles, splitFiles, toWorkspace } from "./projectFiles";

const WS = `// @file money.ts
export const cents = 1;

// @file main.ts
import { cents } from "./money";
console.log(cents);
`;

describe("splitFiles / joinFiles", () => {
  it("leaves single-file code alone", () => {
    expect(isMultiFile("console.log(1);\n")).toBe(false);
    expect(splitFiles("console.log(1);\n")).toBeNull();
  });

  it("splits on markers and trims trailing blank lines", () => {
    expect(splitFiles(WS)).toEqual([
      { name: "money.ts", content: "export const cents = 1;" },
      { name: "main.ts", content: 'import { cents } from "./money";\nconsole.log(cents);' },
    ]);
  });

  it("round-trips", () => {
    const files = splitFiles(WS)!;
    expect(splitFiles(joinFiles(files))).toEqual(files);
    expect(joinFiles(files)).toBe(WS);
  });

  it("keeps text before the first marker as its own file", () => {
    expect(splitFiles("const a = 1;\n// @file b.ts\nconst b = 2;\n")).toEqual([
      { name: "untitled.ts", content: "const a = 1;" },
      { name: "b.ts", content: "const b = 2;" },
    ]);
  });

  it("wraps a single file as main.ts", () => {
    expect(toWorkspace("x();\n\n")).toEqual([{ name: "main.ts", content: "x();" }]);
  });
});

describe("fileNameProblem", () => {
  it("accepts a fresh .ts name", () => {
    expect(fileNameProblem("utils.ts", ["main.ts"])).toBeNull();
  });
  it("rejects spaces, other extensions and duplicates", () => {
    expect(fileNameProblem("my utils.ts", [])).not.toBeNull();
    expect(fileNameProblem("utils.js", [])).not.toBeNull();
    expect(fileNameProblem("main.ts", ["main.ts"])).toBe("main.ts already exists");
  });
});
