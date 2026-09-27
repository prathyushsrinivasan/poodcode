import { describe, expect, it } from "vitest";
import { cheatSheet, cheatSheetMarkdown } from "./cheatSheet";

const LESSON = `### Why it exists
Text.

### Worked examples
#### Reading a number
\`\`\`ts
const n = 1;
\`\`\`
Prints:
\`\`\`text
1
\`\`\`

### What the compiler says
\`\`\`ts
let x = 1; x = "a";
\`\`\`
\`\`\`text
line 1: error TS2322: Type 'string' is not assignable to type 'number'.
\`\`\`

### Pitfalls
#### \`||\` swallows zero
\`\`\`ts
const n = 0 || 5;
\`\`\`
Prints:
\`\`\`text
5
\`\`\`

\`0\` is falsy, so it is replaced. Use \`??\` instead.

### In an interview

**What does \`??\` do?**

Answer.
`;

describe("cheatSheet", () => {
  it("collects examples, errors, pitfalls and questions from the lesson", () => {
    const s = cheatSheet(LESSON, new Map([[2322, "Type 'A' is not assignable to type 'B'"]]));
    expect(s.examples).toEqual(["Reading a number"]);
    expect(s.errors).toEqual([{ code: 2322, title: "Type 'A' is not assignable to type 'B'" }]);
    expect(s.pitfalls).toEqual([{ title: "`||` swallows zero", gist: "`0` is falsy, so it is replaced." }]);
    expect(s.questions).toEqual(["What does `??` do?"]);
    const md = cheatSheetMarkdown("Nullish", "Absent values.", s);
    expect(md).toContain("- `TS2322` — Type 'A'");
    expect(md).toContain("- **`||` swallows zero** — `0` is falsy");
  });
});

describe("cheatSheet key terms", () => {
  it("reads the Key terms section", () => {
    const s = cheatSheet("### Key terms\n- **narrowing** — Proving a value's type.\n- **guard** — A check.", new Map());
    expect(s.terms).toEqual([
      { term: "narrowing", def: "Proving a value's type." },
      { term: "guard", def: "A check." },
    ]);
    expect(cheatSheetMarkdown("N", "w", s)).toContain("**Key terms**\n\n- **narrowing** — Proving a value's type.");
  });
});
