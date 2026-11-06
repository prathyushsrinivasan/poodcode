import { spawnSync } from "node:child_process";
import { describe, expect, it } from "vitest";
import { breadcrumb } from "../../lib/breadcrumb";
import { PYTHON_EXERCISES, PYTHON_MODULES, pythonProgram, pythonTestCases, requiredPythonModules } from "./index";

describe("Python course prerequisite and runner contract", () => {
  it("places every prerequisite at or before its exercise, with actual instruction", () => {
    expect(PYTHON_MODULES).toHaveLength(25);
    expect(PYTHON_EXERCISES).toHaveLength(50);
    expect(new Set(PYTHON_EXERCISES.map((exercise) => exercise.id)).size).toBe(50);
    for (const module of PYTHON_MODULES) {
      for (const exercise of module.exercises) {
        const prerequisites = requiredPythonModules(exercise);
        expect(prerequisites.length).toBeGreaterThan(0);
        for (const prerequisite of prerequisites) {
          expect(prerequisite.number).toBeLessThanOrEqual(module.number);
          expect(prerequisite.explanation.length).toBeGreaterThan(500);
          expect(prerequisite.example).toContain("print(");
        }
      }
    }
  });

  it("exposes every graded case and preserves return-value representations", () => {
    for (const exercise of PYTHON_EXERCISES) {
      const cases = pythonTestCases(exercise.tests);
      expect(cases).toHaveLength(exercise.tests.length);
      expect(new Set(cases.map((test) => test.input)).size).toBe(cases.length);
      for (const [i, test] of cases.entries()) {
        expect(test.kind).toBe("example");
        expect(test.expected_output).toBe(exercise.tests[i].expected);
      }
    }
  });

  it("runs the actual generated driver with numeric, string, dict, cyclic-list and tree answers", () => {
    const fixtures = ["add", "reverse-words", "frequencies", "cycle", "middle", "tree-inorder", "coin-change"];
    for (const id of fixtures) {
      const exercise = PYTHON_EXERCISES.find((item) => item.id === `python:${id}`)!;
      const code = pythonProgram(exercise.solution, exercise.tests);
      const cases = pythonTestCases(exercise.tests);
      for (const test of cases) {
        const result = spawnSync("python", ["-c", code], { input: test.input, encoding: "utf8", timeout: 5000 });
        expect(result.error, "Python 3.9+ is required for this execution check").toBeUndefined();
        expect(result.stderr).toBe("");
        expect(result.status).toBe(0);
        expect(result.stdout.trim()).toBe(test.expected_output);
      }
    }
  }, 30000);

  it("runs only the selected case and makes learner errors visible", () => {
    const exercise = PYTHON_EXERCISES[0];
    const wrong = spawnSync("python", ["-c", pythonProgram(exercise.starter, exercise.tests)], { input: "0", encoding: "utf8" });
    expect(wrong.stdout.trim()).not.toBe(exercise.tests[0].expected);
    expect(wrong.stdout.trim()).toBe("0");
    const error = spawnSync("python", ["-c", pythonProgram("def solve(a, b):\n    return missing_name", exercise.tests)], { input: "0", encoding: "utf8" });
    expect(error.status).not.toBe(0);
    expect(error.stderr).toContain("NameError");
  });

  it("provides roadmap and module breadcrumbs", () => {
    expect(breadcrumb("/python-course/p01").map((crumb) => crumb.label)).toEqual(["Today", "Python Course", "Module"]);
  });
});
