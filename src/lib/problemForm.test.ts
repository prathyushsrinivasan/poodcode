import { describe, expect, it } from "vitest";
import type { Problem, TestCase } from "../types";
import { errorsOf, messageFor, moveItem, slugify, validateProblem } from "./problemForm";

function problem(patch: Partial<Problem> = {}): Problem {
  return {
    id: 0,
    slug: "",
    title: "Sum of two",
    difficulty: "Easy",
    description: "Add them.",
    constraints: "",
    examples: [],
    editorial: "",
    optimal_time: "",
    optimal_space: "",
    optimal_explanation: "",
    starter_code: {},
    topics: [],
    subtopics: [],
    companies: [],
    patterns: [],
    hints: [],
    prerequisites: [],
    test_cases: [],
    function_spec: null,
    judge_mode: "exact",
    float_tolerance: 0,
    checker: "",
    time_limit_ms: 0,
    editorials: [],
    follow_ups: [],
    order: 0,
    is_favorite: false,
    solved_status: "unsolved",
    confidence: 0,
    last_solved_at: null,
    time_taken_seconds: 0,
    attempts_count: 0,
    success_count: 0,
    created_at: "",
    updated_at: "",
    ...patch,
  };
}

const tc = (patch: Partial<TestCase>): TestCase => ({
  id: 0,
  problem_id: 0,
  kind: "hidden",
  name: "Case",
  input: "1 2",
  expected_output: "3",
  ordering: 0,
  ...patch,
});

describe("validateProblem", () => {
  it("accepts a complete problem", () => {
    const p = problem({ test_cases: [tc({ kind: "example", name: "a" }), tc({ name: "b" })] });
    expect(validateProblem(p)).toEqual([]);
  });

  it("requires a title", () => {
    expect(messageFor(validateProblem(problem({ title: " " })), "title")?.severity).toBe("error");
  });

  it("rejects a malformed slug and a taken one, but not the problem's own", () => {
    expect(messageFor(validateProblem(problem({ slug: "Bad Slug" })), "slug")?.severity).toBe("error");
    const taken = new Map([["sum-of-two", 7]]);
    expect(messageFor(validateProblem(problem(), taken), "slug")?.message).toMatch(/already used/);
    expect(messageFor(validateProblem(problem({ id: 7 }), taken), "slug")).toBeUndefined();
  });

  it("warns, without blocking, when there is nothing to judge", () => {
    const issues = validateProblem(problem());
    expect(messageFor(issues, "test_cases")?.severity).toBe("warning");
    expect(errorsOf(issues)).toEqual([]);
  });

  it("flags duplicate and missing case names on the case itself", () => {
    const issues = validateProblem(problem({ test_cases: [tc({ name: "x" }), tc({ name: "x" }), tc({ name: "" })] }));
    expect(messageFor(issues, "test_cases.1.name")?.message).toMatch(/case 1/);
    expect(messageFor(issues, "test_cases.2.name")?.severity).toBe("error");
  });

  it("warns on an empty expected output, except for user cases", () => {
    const issues = validateProblem(problem({ test_cases: [tc({ expected_output: "" }), tc({ name: "u", kind: "user", expected_output: "" })] }));
    expect(messageFor(issues, "test_cases.0.expected_output")?.severity).toBe("warning");
    expect(messageFor(issues, "test_cases.1.expected_output")).toBeUndefined();
  });

  it("rejects empty hints, empty examples and duplicate prerequisite keys", () => {
    const issues = validateProblem(
      problem({
        hints: ["ok", ""],
        examples: [{ input: "", output: "", explanation: "" }],
        prerequisites: [
          { key: "", name: "Hash Maps", what: "", deep: "", java: "", how: "" },
          { key: "hash-maps", name: "Maps", what: "", deep: "", java: "", how: "" },
        ],
      })
    );
    expect(messageFor(issues, "hints.1")).toBeDefined();
    expect(messageFor(issues, "examples.0")).toBeDefined();
    expect(messageFor(issues, "prerequisites.1.key")?.message).toMatch(/twice/);
  });
});

describe("helpers", () => {
  it("slugifies", () => {
    expect(slugify("  Two Sum (II)! ")).toBe("two-sum-ii");
  });

  it("moves items and ignores moves off the ends", () => {
    expect(moveItem(["a", "b", "c"], 0, 2)).toEqual(["b", "c", "a"]);
    expect(moveItem(["a", "b"], 0, -1)).toEqual(["a", "b"]);
  });
});
