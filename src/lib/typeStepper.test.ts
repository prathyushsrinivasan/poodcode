import { describe, expect, it } from "vitest";
import {
  applications,
  conditionalAliases,
  inferNames,
  planSteps,
  splitConditional,
  splitTop,
  splitUnion,
  withArg,
} from "./typeStepper";

describe("typeStepper parsing", () => {
  it("splits at the top level only", () => {
    expect(splitTop("A<B, C>, [D, E], (x: F, y: G) => H", ",")).toEqual(["A<B, C>", "[D, E]", "(x: F, y: G) => H"]);
    expect(splitTop('"a,b", c', ",")).toEqual(['"a,b"', "c"]);
  });

  it("splits a printed union, and never has no members", () => {
    expect(splitUnion('"a" | "b" | { x: 1 | 2; }')).toEqual(['"a"', '"b"', "{ x: 1 | 2; }"]);
    expect(splitUnion("| string\n| number")).toEqual(["string", "number"]);
    expect(splitUnion("never")).toEqual([]);
    expect(splitUnion("(a: string) => number | boolean")).toEqual(["(a: string) => number", "boolean"]);
  });

  it("finds the parts of a conditional type, nested ones included", () => {
    expect(splitConditional("T extends readonly (infer E)[] ? E : never")).toEqual({
      check: "T",
      ext: "readonly (infer E)[]",
      yes: "E",
      no: "never",
    });
    expect(splitConditional("T extends string ? U extends 1 ? 'a' : 'b' : 'c'")).toEqual({
      check: "T",
      ext: "string",
      yes: "U extends 1 ? 'a' : 'b'",
      no: "'c'",
    });
    expect(splitConditional("{ a?: string }")).toBeNull();
    expect(splitConditional("[T] extends [string] ? 1 : 2")?.check).toBe("[T]");
  });

  it("lists infer bindings", () => {
    expect(inferNames("[infer H extends string, ...infer R]")).toEqual(["H", "R"]);
  });

  it("finds conditional aliases and their applications", () => {
    const src = `// type Nope<T> = T extends 1 ? 2 : 3;
type ElementOf<T> = T extends readonly (infer E)[] ? E : never;
type Wrap<T> = { value: T };
type X = ElementOf<string[] | number>;
type Y = Wrap<number>;
const z = 1;
`;
    const aliases = conditionalAliases(src);
    expect([...aliases.keys()]).toEqual(["ElementOf"]);
    const apps = applications(src, new Set(aliases.keys()));
    expect(apps).toEqual([{ name: "X", fn: "ElementOf", args: ["string[] | number"] }]);
    const plan = planSteps(apps[0]!, aliases.get("ElementOf")!, 0);
    expect(plan.distributesOver).toBe(0);
    expect(plan.infers).toEqual(["E"]);
    expect(plan.helpers[0]).toBe("type __PgBranch0<T> = T extends readonly (infer E)[] ? true : false;");
    expect(plan.helpers[1]).toBe("type __PgInfer0_E<T> = T extends readonly (infer E)[] ? E : never;");
  });

  it("does not distribute when the checked type is wrapped", () => {
    const src = "type IsStr<T> = [T] extends [string] ? true : false;\ntype A = IsStr<string | number>;\n";
    const aliases = conditionalAliases(src);
    const plan = planSteps(applications(src, new Set(aliases.keys()))[0]!, aliases.get("IsStr")!, 3);
    expect(plan.distributesOver).toBeNull();
  });

  it("keeps constraints and defaults in helper parameters, and multi-line bodies", () => {
    const src = "type Pick2<T, K extends keyof T = keyof T> =\n  K extends string ? T[K] : never;\ntype P = Pick2<{ a: 1 }, \"a\">;\n";
    const alias = conditionalAliases(src).get("Pick2")!;
    expect(alias.params).toEqual(["T", "K"]);
    expect(alias.cond.check).toBe("K");
    const plan = planSteps(applications(src, new Set(["Pick2"]))[0]!, alias, 1);
    expect(plan.distributesOver).toBe(1);
    expect(plan.helpers[0]).toContain("<T, K extends keyof T = keyof T>");
    expect(withArg(["{ a: 1 }", '"a"'], 1, '"b"')).toBe('{ a: 1 }, "b"');
  });
});
