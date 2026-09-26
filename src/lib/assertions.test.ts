import { describe, expect, it } from "vitest";
import {
  assertionFailed,
  failingCheckLines,
  hasOwnCodeErrors,
  parseAssertions,
  splitTopLevel,
} from "./assertions";

const HARNESS = `// Supplied by the checker.
type Equal<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

type _1 = Expect<Equal<Pick<Task, "id">, { id: number }>>;
type _2 = Expect<Equal<Validators<{ name: string }>, {
  name: (value: unknown) => value is string;
}>>;
// @ts-expect-error — K must be a key of T
type _3 = WithRequired<Task, "owner">;
const asNumber: number = u;
`;

describe("splitTopLevel", () => {
  it("splits at the first top-level comma only", () => {
    expect(splitTopLevel('Pick<T, "a" | "b">, { a: 1, b: 2 }')).toEqual(['Pick<T, "a" | "b">', "{ a: 1, b: 2 }"]);
  });
  it("is not fooled by arrows or strings", () => {
    expect(splitTopLevel('(x: number) => string, "a,b"')).toEqual(["(x: number) => string", '"a,b"']);
  });
  it("returns null with no top-level comma", () => {
    expect(splitTopLevel("Record<string, number>")).toBeNull();
  });
});

describe("parseAssertions", () => {
  const a = parseAssertions(HARNESS);

  it("finds each claim with its line span", () => {
    expect(a.map((x) => [x.kind, x.from, x.to])).toEqual([
      ["equal", 6, 6],
      ["equal", 7, 9],
      ["rejects", 10, 10],
    ]);
  });

  it("separates the two sides of Equal", () => {
    expect(a[0]!.left).toBe('Pick<Task, "id">');
    expect(a[0]!.right).toBe("{ id: number }");
    expect(a[1]!.left).toBe("Validators<{ name: string }>");
  });

  it("keeps the reason on an expected error", () => {
    expect(a[2]!.note).toBe("K must be a key of T");
    expect(a[2]!.text).toBe('type _3 = WithRequired<Task, "owner">;');
  });
});

describe("matching errors to claims", () => {
  const a = parseAssertions(HARNESS);
  const msg =
    "checks.ts(8,3): error TS2344: Type 'false' does not satisfy the constraint 'true'.\n" +
    "checks.ts(10,1): error TS2578: Unused '@ts-expect-error' directive.";
  const failing = failingCheckLines(msg);

  it("marks a claim failed when any of its lines has an error", () => {
    expect(a.map((x) => assertionFailed(x, failing))).toEqual([false, true, true]);
  });

  it("tells the learner's own errors apart from the checks'", () => {
    expect(hasOwnCodeErrors(msg)).toBe(false);
    expect(hasOwnCodeErrors("main.ts(2,5): error TS2322: nope")).toBe(true);
  });
});
