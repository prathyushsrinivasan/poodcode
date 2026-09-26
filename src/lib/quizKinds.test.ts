import { describe, expect, it } from "vitest";
import type { QuizQuestion } from "../types";
import {
  answerText,
  bannedIn,
  expectedPick,
  isSelected,
  maskOf,
  MULTI,
  questionText,
  reorderOptions,
  toggleMulti,
  typeAnswerProgram,
} from "./quizKinds";

const base: QuizQuestion = { question: "q", options: ["a", "b", "c", "d"], answer: 0, explanation: "" };

describe("quizKinds", () => {
  it("grades a plain question by its index, after a shuffle too", () => {
    const q = reorderOptions(base, ["c", "a", "d", "b"]);
    expect(q.answer).toBe(1);
    expect(expectedPick(q)).toBe(1);
  });

  it("toggles multi-select picks and unanswers an empty selection", () => {
    let p = toggleMulti(-1, 2);
    expect(p).toBe(MULTI + 4);
    p = toggleMulti(p, 0);
    expect(isSelected(p, 0) && isSelected(p, 2) && !isSelected(p, 1)).toBe(true);
    p = toggleMulti(toggleMulti(p, 0), 2);
    expect(p).toBe(-1);
  });

  it("makes a multi-select's answer the mask of its right options, following a shuffle", () => {
    const q = reorderOptions({ ...base, kind: "multi", answers: [0, 2] }, ["d", "c", "b", "a"]);
    expect(q.answers).toEqual([1, 3]);
    expect(q.answer).toBe(MULTI + maskOf([1, 3]));
    const picked = toggleMulti(toggleMulti(-1, 3), 1);
    expect(picked).toBe(q.answer);
    expect(toggleMulti(picked, 0)).not.toBe(q.answer);
  });

  it("grades a typed answer as 0", () => {
    const q = reorderOptions({ ...base, kind: "type", options: ["string"], type_answer: "string" }, ["string"]);
    expect(q.answer).toBe(0);
    expect(answerText(q)).toBe("`string`");
    expect(typeAnswerProgram({ code: "const x = 1;\n" }, " 1 ")).toBe("const x = 1;\ntype Answer = 1;\n");
  });

  it("writes the right answer out for a flashcard", () => {
    expect(answerText({ ...base, answer: 2 })).toBe("c");
    expect(answerText({ ...base, kind: "multi", answers: [1, 3] })).toBe("- b\n- d");
    expect(answerText({ ...base, kind: "output", options: ["42"] })).toBe("```text\n42\n```");
    expect(questionText({ question: "What prints?", code: "log(1)\n" })).toBe("What prints?\n\n```ts\nlog(1)\n```");
  });
});

describe("bannedIn", () => {
  it("rejects answers that ask the compiler instead of spelling the type out", () => {
    expect(bannedIn("typeof x")).toBe("typeof");
    expect(bannedIn("keyof typeof handlers")).toBe("typeof");
    expect(bannedIn("ReturnType<typeof f>")).toBe("typeof");
    expect(bannedIn('"save" | "load"')).toBeNull();
    expect(bannedIn("{ typeofThing: string }")).toBeNull();
  });
});

describe("why_not", () => {
  it("moves with the options when they are shuffled", () => {
    const q = reorderOptions({ ...base, why_not: ["", "not b", "not c", "not d"] }, ["c", "a", "d", "b"]);
    expect(q.why_not).toEqual(["not c", "", "not d", "not b"]);
    expect(q.options[q.answer]).toBe("a");
  });
});
