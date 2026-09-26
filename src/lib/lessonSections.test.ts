import { describe, expect, it } from "vitest";
import { splitPitfalls } from "./lessonSections";

const LESSON = `### Why it exists
Because.

### Pitfalls
#### \`||\` swallows zero
\`\`\`ts
// #### not a heading inside code
const n = 0 || 5;
\`\`\`
Prints 5.

#### Forgetting to trim
Trim it.

### Where it shows up later
- week 3`;

describe("splitPitfalls", () => {
  it("splits the pitfalls section into cards and keeps what surrounds it", () => {
    const parts = splitPitfalls(LESSON)!;
    expect(parts.before).toBe("### Why it exists\nBecause.");
    expect(parts.heading).toBe("### Pitfalls");
    expect(parts.pitfalls.map((p) => p.title)).toEqual(["`||` swallows zero", "Forgetting to trim"]);
    expect(parts.pitfalls[0]!.body).toContain("// #### not a heading inside code");
    expect(parts.pitfalls[0]!.body.endsWith("Prints 5.")).toBe(true);
    expect(parts.after).toBe("### Where it shows up later\n- week 3");
  });

  it("returns null without a pitfalls section", () => {
    expect(splitPitfalls("### Idea\ntext")).toBeNull();
  });

  it("runs to the end when pitfalls is the last section", () => {
    const parts = splitPitfalls("intro\n\n### Pitfalls\n#### One\nbody")!;
    expect(parts.after).toBe("");
    expect(parts.pitfalls).toEqual([{ title: "One", body: "body" }]);
  });
});
