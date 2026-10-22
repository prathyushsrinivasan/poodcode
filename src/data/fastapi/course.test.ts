import { describe, expect, it } from "vitest";
import { FASTAPI_COURSE } from "./index";
import { courseInsight } from "../../lib/insights";
import { breadcrumb } from "../../lib/breadcrumb";

describe("FastAPI practical course", () => {
  it("ships the whole learning path with substantive code, labs, checks and worked files", () => {
    expect(FASTAPI_COURSE.weeks).toHaveLength(12);
    const lessonKeys: string[] = [];
    for (const [i, module] of FASTAPI_COURSE.weeks.entries()) {
      expect(module.number).toBe(i + 1);
      expect(module.authored).toBe(true);
      expect(module.lessons).toHaveLength(2);
      expect(module.capstone?.kind).toBe("brief");
      expect(module.capstone?.rubric.length).toBeGreaterThanOrEqual(4);
      expect(module.capstone?.reference).toContain("```python");
      expect(module.summary).toContain("Mark done now");
      for (const lesson of module.lessons) {
        lessonKeys.push(lesson.key);
        expect(lesson.lesson.length).toBeGreaterThan(1500);
        expect(lesson.lesson).toMatch(/```(?:python|text|powershell|dockerfile)/);
        expect(lesson.lesson).toContain("## Lab:");
        expect(lesson.lesson).not.toContain("<!-- lesson -->");
        expect(lesson.lesson.match(/^```/gm)?.length ?? 0).toSatisfy((n: number) => n > 0 && n % 2 === 0);
      }
    }
    expect(new Set(lessonKeys).size).toBe(24);
    expect(new Set(FASTAPI_COURSE.weeks.map((m) => m.month))).toEqual(new Set([1, 2, 3, 4]));
  });

  it("has distinct questions with valid answers and explanations", () => {
    const questions = FASTAPI_COURSE.weeks.flatMap((m) => m.review);
    expect(questions).toHaveLength(36);
    expect(new Set(questions.map((q) => q.question)).size).toBe(36);
    for (const question of questions) {
      expect(question.options.length).toBeGreaterThanOrEqual(3);
      expect(new Set(question.options).size).toBe(question.options.length);
      expect(Number.isInteger(question.answer)).toBe(true);
      expect(question.answer).toBeGreaterThanOrEqual(0);
      expect(question.answer).toBeLessThan(question.options.length);
      expect(question.explanation.length).toBeGreaterThan(40);
    }
  });

  it("isolates FastAPI progress from the other course namespaces", () => {
    const insight = courseInsight(FASTAPI_COURSE, "fastapi-course", new Set([
      "fastapi-course:w1", "fastapi-course:w12", "ts-course:w2", "java-course:w3",
    ]), { key: "fastapi", label: "FastAPI", icon: "backend", href: "/fastapi-course" });
    expect(insight.done).toBe(2);
    expect(insight.total).toBe(12);
    expect(insight.unit).toBe("module");
  });

  it("provides course and module wayfinding", () => {
    expect(breadcrumb("/fastapi-course/7").map((crumb) => crumb.label)).toEqual(["Today", "FastAPI Course", "Module"]);
  });

  it("keeps early references within the learner's current prerequisites", () => {
    const [first, second] = FASTAPI_COURSE.weeks;
    expect(first.capstone?.reference).toContain('def hello(');
    expect(second.capstone?.reference).toContain('class TaskPatch');
    for (const module of [first, second]) {
      expect(module.capstone?.reference).not.toMatch(/from \.security|from \.db|import jwt|sqlalchemy/);
    }
    expect(FASTAPI_COURSE.subtitle).toContain("Beginner to intermediate");
    for (const [i, module] of FASTAPI_COURSE.weeks.entries()) {
      expect(module.summary).toContain("Before you start:");
      if (i > 0) expect(module.summary).toContain(`#/fastapi-course/${i}`);
    }
    expect(FASTAPI_COURSE.weeks[5].capstone?.brief).toContain("/auth/login-check");
  });
});
