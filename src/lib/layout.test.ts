import { describe, expect, it } from "vitest";
import { layoutClass, shouldAutoCollapse } from "./layout";

describe("layout contract", () => {
  it("classes the three bands at their edges", () => {
    expect(layoutClass(960)).toBe("compact");
    expect(layoutClass(1179)).toBe("compact");
    expect(layoutClass(1180)).toBe("regular");
    expect(layoutClass(1439)).toBe("regular");
    expect(layoutClass(1440)).toBe("wide");
  });

  it("folds the sidebar on editor pages and in compact windows only", () => {
    expect(shouldAutoCollapse("compact", false)).toBe(true);
    expect(shouldAutoCollapse("regular", true)).toBe(true);
    expect(shouldAutoCollapse("wide", false)).toBe(false);
  });
});
