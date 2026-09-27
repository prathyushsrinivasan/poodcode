import { describe, expect, it } from "vitest";
import { popoutLabel } from "./popout";

describe("popoutLabel", () => {
  it("makes a label Tauri accepts, stable per path", () => {
    expect(popoutLabel("/popout/lesson/ts_generics")).toBe("popout-popout-lesson-ts_generics");
    expect(popoutLabel("/popout/editorial/12")).toMatch(/^popout-[a-zA-Z0-9_-]+$/);
  });

  it("matches the capability's popout-* window glob", () => {
    expect(popoutLabel("/x y/é")).toMatch(/^popout-/);
  });
});
