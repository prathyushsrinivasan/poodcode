import { describe, expect, it } from "vitest";
import { SCENARIOS, settle, simulate, type Combinator, type TimedPromise } from "./eventLoop";

/** Run a scenario's real JavaScript and collect what it prints. */
async function runForReal(code: string): Promise<string[]> {
  const out: string[] = [];
  const fakeConsole = { log: (...args: unknown[]) => out.push(args.map(String).join(" ")) };
  new Function("console", code)(fakeConsole);
  await new Promise((r) => setTimeout(r, 120));
  return out;
}

describe("event-loop scenarios", () => {
  for (const s of SCENARIOS) {
    it(`${s.key}: the simulator prints what the engine prints`, async () => {
      const steps = simulate(s.program);
      const simulated = steps[steps.length - 1]!.output;
      expect(simulated).toEqual(await runForReal(s.code));
    });

    it(`${s.key}: every highlighted line exists in the code`, () => {
      const lines = s.code.split("\n").length;
      for (const step of simulate(s.program)) {
        if (step.line !== null) expect(step.line).toBeLessThanOrEqual(lines);
      }
    });
  }

  it("ends with an empty stack and empty queues", () => {
    const steps = simulate(SCENARIOS[0]!.program);
    const last = steps[steps.length - 1]!;
    expect(last.stack).toEqual([]);
    expect(last.microtasks).toEqual([]);
    expect(last.tasks).toEqual([]);
  });
});

/** What a real combinator does with real timers: outcome and value. */
async function realSettle(comb: Combinator, items: TimedPromise[]) {
  const make = (p: TimedPromise) =>
    new Promise<string>((resolve, reject) =>
      setTimeout(() => (p.ok ? resolve(p.label) : reject(new Error(p.label))), p.ms)
    );
  const promises = items.map(make);
  // Unobserved rejections are expected here (race/any leave losers behind).
  promises.forEach((p) => p.catch(() => {}));
  try {
    const v = await (Promise[comb] as (ps: Promise<string>[]) => Promise<unknown>)(promises);
    return { outcome: "fulfilled", v };
  } catch (e) {
    return { outcome: "rejected", v: e instanceof AggregateError ? "aggregate" : (e as Error).message };
  }
}

describe("settle", () => {
  const items: TimedPromise[] = [
    { label: "a", ms: 30, ok: true },
    { label: "b", ms: 10, ok: false },
    { label: "c", ms: 50, ok: true },
  ];

  const cases: [Combinator, TimedPromise[]][] = [
    ["all", items],
    ["all", items.map((p) => ({ ...p, ok: true }))],
    ["allSettled", items],
    ["race", items],
    ["any", items],
    ["any", items.map((p) => ({ ...p, ok: false }))],
  ];

  for (const [comb, list] of cases) {
    it(`${comb} over ${list.map((p) => `${p.label}${p.ok ? "✓" : "✗"}@${p.ms}`).join(" ")} matches the real one`, async () => {
      const model = settle(comb, list);
      const real = await realSettle(comb, list);
      expect(model.outcome).toBe(real.outcome);
      if (comb === "race" || (comb === "any" && real.outcome === "fulfilled")) {
        expect(model.value).toContain(String(real.v));
      }
      if (comb === "all" && real.outcome === "rejected") expect(model.value).toContain(String(real.v));
    });
  }

  it("names the settle time", () => {
    expect(settle("all", items).at).toBe(10);
    expect(settle("allSettled", items).at).toBe(50);
    expect(settle("race", items).at).toBe(10);
    expect(settle("any", items).at).toBe(30);
    expect(settle("race", []).outcome).toBe("pending");
  });
});
