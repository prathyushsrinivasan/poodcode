import { describe, expect, it } from "vitest";
import { analyseMachine, findMachines, literalUnions } from "./stateMachine";

describe("stateMachine", () => {
  it("finds unions of string literals only", () => {
    const src = 'type S = "a" | "b";\ntype N = 1 | 2;\ntype M = "x" | string;\n// type C = "c" | "d";\n';
    expect(literalUnions(src)).toEqual([{ name: "S", states: ["a", "b"] }]);
  });

  it("reads edges from a transition table", () => {
    const src = `type Status = "draft" | "review" | "live" | "archived";
const NEXT: Record<Status, readonly Status[]> = {
  draft: ["review"],
  review: ["draft", "live"],
  live: ["archived"],
  archived: [],
};`;
    const [m] = findMachines(src);
    expect(m!.via).toBe("table");
    expect(m!.edges).toEqual([
      ["draft", "review"],
      ["review", "draft"],
      ["review", "live"],
      ["live", "archived"],
    ]);
    expect(analyseMachine(m!)).toEqual({ terminal: ["archived"], unreachable: [] });
  });

  it("reads edges from a switch that returns states, fall-through included", () => {
    const src = `type Light = "red" | "green" | "amber" | "off";
function next(l: Light, fault: boolean): Light {
  switch (l) {
    case "red":
      return "green";
    case "green":
      return fault ? "off" : "amber";
    case "amber":
    case "off":
      return "red";
  }
}`;
    const [m] = findMachines(src);
    expect(m!.via).toBe("switch");
    expect(m!.edges).toEqual([
      ["red", "green"],
      ["green", "off"],
      ["green", "amber"],
      ["amber", "red"],
      ["off", "red"],
    ]);
    expect(analyseMachine(m!).terminal).toEqual([]);
  });

  it("reports states the start cannot reach", () => {
    const src = 'type S = "a" | "b" | "c";\nconst T = { a: ["b"], b: ["a"], c: ["a"] };';
    expect(analyseMachine(findMachines(src)[0]!).unreachable).toEqual(["c"]);
  });
});
