import { describe, expect, it } from "vitest";
import { breadcrumb, segments, withLeafLabel } from "./breadcrumb";

const labels = (path: string) => breadcrumb(path).map((c) => c.label);
const hrefs = (path: string) => breadcrumb(path).map((c) => c.href);

describe("segments", () => {
  it("drops empties from both ends", () => {
    expect(segments("/library/browse/")).toEqual(["library", "browse"]);
    expect(segments("/")).toEqual([]);
  });
});

describe("breadcrumb", () => {
  it("is just Today at the root, and Today is not a link there", () => {
    expect(labels("/")).toEqual(["Today"]);
    expect(hrefs("/")).toEqual([null]);
  });

  it("always offers a way home", () => {
    expect(labels("/settings")[0]).toBe("Today");
    expect(hrefs("/settings")[0]).toBe("/");
  });

  it("never links the page you are already on", () => {
    const crumbs = breadcrumb("/library/browse");
    expect(crumbs[crumbs.length - 1].href).toBeNull();
  });

  it("names a static trail", () => {
    expect(labels("/library/browse")).toEqual(["Today", "DSA Curriculum", "Browse problems"]);
  });

  it("skips plumbing segments that carry no label", () => {
    // "/library/unit/two-pointers" is three segments but two crumbs — "unit"
    // is routing, not a place.
    expect(labels("/library/unit/two-pointers")).toEqual([
      "Today",
      "DSA Curriculum",
      "Unit",
    ]);
  });

  it("marks dynamic segments so a page can fill them in", () => {
    const crumbs = breadcrumb("/solve/12");
    expect(crumbs.map((c) => c.label)).toEqual(["Today", "Problem"]);
    expect(crumbs[1].dynamic).toBe(true);
  });

  it("links the parent of a dynamic leaf", () => {
    expect(hrefs("/library/unit/heaps")).toEqual(["/", "/library", null]);
  });

  it("handles a nested project module", () => {
    expect(labels("/projects/http-api/routing")).toEqual([
      "Today",
      "Projects",
      "Project",
      "Module",
    ]);
  });

  it("prefers a named child over the wildcard", () => {
    // "workbench" is a real page, not a module key.
    expect(labels("/projects/http-api/workbench")).toEqual([
      "Today",
      "Projects",
      "Project",
      "Workbench",
    ]);
  });

  it("handles a course week", () => {
    expect(labels("/java-course/7")).toEqual(["Today", "Java Course", "Module"]);
  });

  it("stops cleanly on an unknown path rather than inventing crumbs", () => {
    expect(labels("/nonsense/deeper")).toEqual(["Today"]);
  });
});

describe("withLeafLabel", () => {
  it("sharpens the last placeholder", () => {
    const crumbs = withLeafLabel(breadcrumb("/solve/12"), "Count Inversions");
    expect(crumbs.map((c) => c.label)).toEqual(["Today", "Count Inversions"]);
    expect(crumbs[1].dynamic).toBe(false);
  });

  it("targets the last dynamic crumb, not an earlier one", () => {
    const crumbs = withLeafLabel(breadcrumb("/projects/api/routing"), "Routing");
    expect(crumbs.map((c) => c.label)).toEqual(["Today", "Projects", "Project", "Routing"]);
  });

  it("leaves a static trail alone", () => {
    const before = breadcrumb("/library/browse");
    expect(withLeafLabel(before, "Nope")).toEqual(before);
  });

  it("is a no-op for a null label", () => {
    const before = breadcrumb("/solve/12");
    expect(withLeafLabel(before, null)).toEqual(before);
  });
});
