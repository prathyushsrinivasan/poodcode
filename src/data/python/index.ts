import course from "./course.json";
import type { TestCase } from "../../types";

export interface PythonCase {
  name: string;
  setup: string;
  call: string;
  expected: string;
}

export interface PythonExercise {
  id: string;
  title: string;
  prompt: string;
  hint: string;
  starter: string;
  solution: string;
  explanation: string;
  complexity: string;
  requires: string[];
  tests: PythonCase[];
}

export interface PythonModule {
  id: string;
  number: number;
  title: string;
  stage: string;
  goal: string;
  explanation: string;
  example: string;
  pattern: string;
  gate: string;
  syntax: string[];
  exercises: PythonExercise[];
}

export const PYTHON_MODULES: PythonModule[] = course;
export const PYTHON_EXERCISES = PYTHON_MODULES.flatMap((module) => module.exercises);

/** The supplied driver owns I/O; learners only implement the taught function.
 * Cases are explicit branches so no eval, serialization API, or new learner
 * syntax is needed. Each case runs in a fresh process through the real judge. */
export function pythonProgram(code: string, tests: PythonCase[]): string {
  const branches = tests.map((test, index) => {
    const lines = [test.setup.trimEnd(), `print(repr(${test.call}))`].filter(Boolean).join("\n");
    return `${index === 0 ? "if" : "elif"} _course_case == ${JSON.stringify(String(index))}:\n` +
      lines.split("\n").map((line) => `    ${line}`).join("\n");
  });
  return `${code}\n\n# Supplied course driver: no input parsing is required in solve.\n` +
    `import sys as _course_sys\n_course_case = _course_sys.stdin.read().strip()\n${branches.join("\n")}\n`;
}

export function pythonTestCases(tests: PythonCase[]): TestCase[] {
  return tests.map((test, index) => ({
    id: index, problem_id: 0, kind: "example", name: test.name,
    input: String(index), expected_output: test.expected, ordering: index,
  }));
}

/** Each syntax requirement resolves to the earliest demonstrated lesson.
 * Earlier modules stay accessible for review; the roadmap recommends an order. */
export function requiredPythonModules(exercise: PythonExercise): PythonModule[] {
  return exercise.requires.map((id) => PYTHON_MODULES.find((module) => module.id === id)!);
}
