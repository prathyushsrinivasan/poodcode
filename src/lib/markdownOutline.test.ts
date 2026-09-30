import { describe, expect, it } from "vitest";
import { topHeadingLevel } from "./markdownOutline";

describe("topHeadingLevel", () => {
  it("finds the shallowest heading", () => {
    expect(topHeadingLevel("### Input\n\ntext\n\n## Why\n\n#### Detail")).toBe(2);
  });

  it("is null for prose with no headings", () => {
    expect(topHeadingLevel("Just a paragraph with a # in it.")).toBeNull();
  });

  it("ignores lines inside fenced code", () => {
    expect(topHeadingLevel("### Run it\n\n```bash\n# install first\nnpm i\n```")).toBe(3);
    expect(topHeadingLevel("~~~\n# not a heading\n~~~\n\n#### Real")).toBe(4);
  });

  it("needs a space after the hashes", () => {
    expect(topHeadingLevel("#hashtag\n\n### Heading")).toBe(3);
  });
});
