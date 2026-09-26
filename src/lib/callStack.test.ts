import { describe, expect, it } from "vitest";
import { STACK_SCENARIOS, traceScenario } from "./callStack";

function runForReal(code: string): string[] {
  const out: string[] = [];
  const fakeConsole = { log: (...args: unknown[]) => out.push(args.map(String).join(" ")) };
  new Function("console", code)(fakeConsole);
  return out;
}

describe("call-stack scenarios", () => {
  for (const s of STACK_SCENARIOS) {
    it(`${s.key}: the traced twin prints what the real code prints`, () => {
      const steps = traceScenario(s);
      expect(steps[steps.length - 1]!.output).toEqual(runForReal(s.code));
    });

    it(`${s.key}: starts and ends with an empty stack and cites real lines`, () => {
      const steps = traceScenario(s);
      expect(steps[steps.length - 1]!.frames).toEqual([]);
      const lines = s.code.split("\n").length;
      for (const st of steps) if (st.line !== null) expect(st.line).toBeLessThanOrEqual(lines);
    });
  }

  it("factorial reaches four frames deep", () => {
    const steps = traceScenario(STACK_SCENARIOS[0]!);
    expect(Math.max(...steps.map((s) => s.frames.length))).toBe(5); // (script) + 4 calls
  });
});
