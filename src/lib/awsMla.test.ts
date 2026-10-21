import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { AWS_LESSONS } from "../data/awsMla/lessons";
import { AWS_DOMAINS, AWS_SKILLS, AWS_TASKS } from "../data/awsMla/syllabus";
import { AWS_DAY, awsStatus, awsStudyMinutes, awsStudyStreak, emptyAwsProgress, gradeAwsQuestion, parseAwsProgress, planAwsSession, recordAwsAttempt, setAwsNote } from "./awsMla";
import { todayISO } from "./srs";

const NOW = new Date(2026, 9, 21, 12).getTime();
const lesson = AWS_LESSONS[0];
const correct = lesson.questions.map((question) => question.answers);
const miss = lesson.questions.map((question) => [question.options.findIndex((_, index) => !question.answers.includes(index))]);

describe("MLA-C02 blueprint integrity", () => {
  it("maps every published skill once, with domain counts and roadmap parity", () => {
    expect(AWS_SKILLS).toHaveLength(107);
    expect(AWS_TASKS).toHaveLength(12);
    expect(AWS_DOMAINS.reduce((sum, domain) => sum + domain.weight, 0)).toBe(100);
    expect(AWS_DOMAINS.map((domain) => AWS_SKILLS.filter((skill) => skill.domain === domain.id).length)).toEqual([25, 27, 30, 25]);
    const mapped = AWS_LESSONS.flatMap((item) => item.skills);
    expect(new Set(mapped).size).toBe(mapped.length);
    expect([...mapped].sort()).toEqual(AWS_SKILLS.map((skill) => skill.id).sort());
    const roadmap = readFileSync(new URL("../../AWS_MLA_C02_ROADMAP.md", import.meta.url), "utf8");
    const ids = [...roadmap.matchAll(/- \[ \] \*\*(\d\.\d\.\d+)\*\*/g)].map((match) => match[1]);
    expect(ids.sort()).toEqual(AWS_SKILLS.map((skill) => skill.id).sort());
    for (const skill of AWS_SKILLS) expect(roadmap).toContain(`**${skill.id}** ${skill.title}`);
  });

  it("has coherent unique lessons, source links, and valid single/multiple response items", () => {
    expect(AWS_LESSONS).toHaveLength(24);
    expect(new Set(AWS_LESSONS.map((item) => item.id)).size).toBe(AWS_LESSONS.length);
    const questions = AWS_LESSONS.flatMap((item) => item.questions);
    expect(questions).toHaveLength(72);
    expect(new Set(questions.map((question) => question.id)).size).toBe(questions.length);
    expect(questions.some((question) => question.answers.length > 1)).toBe(true);
    for (const item of AWS_LESSONS) {
      expect(item.skills.every((id) => id.startsWith(item.task + "."))).toBe(true);
      expect(item.references.every((reference) => {
        const url = new URL(reference.url);
        return url.protocol === "https:" && ["docs.aws.amazon.com", "aws.amazon.com", "www.youtube.com", "scikit-learn.org"].includes(url.hostname);
      })).toBe(true);
      for (const question of item.questions) {
        expect(question.options.length).toBeGreaterThanOrEqual(4);
        expect(new Set(question.options.map((option) => option.text)).size).toBe(question.options.length);
        expect(question.answers.length).toBeGreaterThan(0);
        expect(question.answers.length).toBeLessThan(question.options.length);
        expect(question.answers.every((answer) => Number.isInteger(answer) && answer >= 0 && answer < question.options.length)).toBe(true);
        expect(gradeAwsQuestion(question, question.answers)).toBe(true);
      }
    }
  });

  it("provides full module-one lessons with taught sections, curated sources and assessed skill coverage", () => {
    const full = AWS_LESSONS.filter((item) => item.teaching);
    expect(full.map((item) => item.id)).toEqual(AWS_LESSONS.filter((item) => item.task.startsWith("1.")).map((item) => item.id));
    expect(full).toHaveLength(6);
    const assessed = new Set(full.flatMap((item) => item.questions.flatMap((question) => question.skills ?? [])));
    expect([...assessed].sort()).toEqual(AWS_SKILLS.filter((skill) => skill.domain === 1).map((skill) => skill.id).sort());
    for (const item of full) {
      expect(item.teaching!.sections.length).toBeGreaterThanOrEqual(4);
      expect(item.teaching!.sections.every((section) => section.title && section.body.length > 500)).toBe(true);
      expect(new Set(item.teaching!.sections.map((section) => section.id)).size).toBe(item.teaching!.sections.length);
      expect(item.questions).toHaveLength(6);
      expect(item.references.every((reference) => reference.kind && reference.focus)).toBe(true);
      expect(item.references.some((reference) => reference.kind === "Video" || reference.kind === "Article")).toBe(true);
      for (const question of item.questions) {
        expect(item.teaching!.sections.some((section) => section.id === question.section)).toBe(true);
        expect(question.skills?.length).toBeGreaterThan(0);
        expect(question.skills!.every((skill) => item.skills.includes(skill))).toBe(true);
        expect(question.options.every((option) => option.why.trim().length > 0)).toBe(true);
      }
    }
  });
});

describe("MLA-C02 review scheduling", () => {
  it("requires exact multi-response selections and rejects duplicates or extras", () => {
    const question = AWS_LESSONS.flatMap((item) => item.questions).find((item) => item.answers.length > 1)!;
    expect(gradeAwsQuestion(question, [...question.answers].reverse())).toBe(true);
    expect(gradeAwsQuestion(question, question.answers.slice(1))).toBe(false);
    expect(gradeAwsQuestion(question, [...question.answers, question.answers[0]])).toBe(false);
    expect(gradeAwsQuestion(question, [...question.answers, 999])).toBe(false);
  });

  it("earns retention only after three spaced perfect checks", () => {
    let progress = recordAwsAttempt(emptyAwsProgress(), lesson.id, correct, NOW);
    expect(progress.lessons[lesson.id]).toMatchObject({ attempts: 1, streak: 1, interval: 1, due: NOW + AWS_DAY });
    expect(awsStatus(progress.lessons[lesson.id], NOW)).toBe("learning");
    progress = recordAwsAttempt(progress, lesson.id, correct, NOW + AWS_DAY);
    expect(progress.lessons[lesson.id]).toMatchObject({ streak: 2, interval: 3, due: NOW + 4 * AWS_DAY });
    progress = recordAwsAttempt(progress, lesson.id, correct, NOW + 4 * AWS_DAY);
    expect(progress.lessons[lesson.id]).toMatchObject({ streak: 3, interval: 7, due: NOW + 11 * AWS_DAY });
    expect(awsStatus(progress.lessons[lesson.id], NOW + 4 * AWS_DAY)).toBe("retained");
    expect(awsStatus(progress.lessons[lesson.id], NOW + 11 * AWS_DAY)).toBe("due");
  });

  it("does not let early repeats advance the spacing ladder", () => {
    const progress = recordAwsAttempt(emptyAwsProgress(), lesson.id, correct, NOW);
    const repeat = recordAwsAttempt(progress, lesson.id, correct, NOW + 60_000);
    expect(repeat.lessons[lesson.id]).toMatchObject({ attempts: 2, streak: 1, interval: 1, due: NOW + AWS_DAY });
  });

  it("resets a failed check for a ten-minute retry and preserves notes", () => {
    let progress = setAwsNote(emptyAwsProgress(), lesson.id, "Columnar scans");
    expect(awsStatus(progress.lessons[lesson.id], NOW)).toBe("new");
    progress = recordAwsAttempt(progress, lesson.id, correct, NOW);
    progress = recordAwsAttempt(progress, lesson.id, miss, NOW + AWS_DAY);
    expect(progress.lessons[lesson.id]).toMatchObject({ streak: 0, interval: 0, lastScore: 0, due: NOW + AWS_DAY + 600_000, note: "Columnar scans" });
    expect(awsStatus(progress.lessons[lesson.id], NOW + AWS_DAY)).toBe("learning");
  });

  it("ignores unknown lessons and incomplete submissions", () => {
    const progress = emptyAwsProgress();
    expect(recordAwsAttempt(progress, "missing", correct, NOW)).toBe(progress);
    expect(recordAwsAttempt(progress, lesson.id, [[]], NOW)).toBe(progress);
    expect(recordAwsAttempt(progress, lesson.id, [correct[0], []], NOW)).toBe(progress);
  });

  it("caps later intervals at thirty days", () => {
    let progress = emptyAwsProgress();
    let time = NOW;
    for (let count = 0; count < 8; count++) {
      progress = recordAwsAttempt(progress, lesson.id, correct, time);
      time = progress.lessons[lesson.id].due;
    }
    expect(progress.lessons[lesson.id].interval).toBe(30);
  });
});

describe("MLA-C02 daily planning and persistence", () => {
  it("offers a full first lesson even for a short target without skipping prerequisites", () => {
    const progress = emptyAwsProgress();
    expect(planAwsSession(progress, NOW)).toEqual([lesson.id]);
    progress.target = 10;
    expect(planAwsSession(progress, NOW)).toEqual([lesson.id]);
    progress.target = 25;
    expect(planAwsSession(progress, NOW)).toEqual([lesson.id]);
    const studied = recordAwsAttempt({ ...progress, target: 10 }, lesson.id, correct, NOW);
    expect(planAwsSession(studied, NOW)).toEqual([]);
    expect(planAwsSession(studied, NOW + AWS_DAY)[0]).toBe(lesson.id);
  });

  it("puts weak overdue reviews ahead of new material and avoids duplicates", () => {
    let progress = recordAwsAttempt(emptyAwsProgress(), lesson.id, correct, NOW);
    const second = AWS_LESSONS[1];
    progress = recordAwsAttempt(progress, second.id, miss, NOW);
    const queue = planAwsSession(progress, NOW + AWS_DAY);
    expect(queue[0]).toBe(second.id);
    expect(queue[1]).toBe(lesson.id);
    expect(new Set(queue).size).toBe(queue.length);
    expect(queue).toHaveLength(2);
    expect(queue).not.toContain(AWS_LESSONS[6].id);
  });

  it("records the full lesson estimate and uses a shorter review estimate", () => {
    const first = recordAwsAttempt(emptyAwsProgress(), lesson.id, correct, NOW);
    expect(first.days[todayISO(new Date(NOW))].minutes).toBe(awsStudyMinutes(lesson));
    const review = recordAwsAttempt(first, lesson.id, correct, NOW + AWS_DAY);
    expect(review.days[todayISO(new Date(NOW + AWS_DAY))].minutes).toBe(awsStudyMinutes(lesson, true));
    expect(awsStudyMinutes(AWS_LESSONS[6])).toBe(6);
    expect(awsStudyMinutes(AWS_LESSONS[6], true)).toBe(3);
  });

  it("roundtrips saved progress and recovers valid rows from malformed state", () => {
    const progress = recordAwsAttempt(emptyAwsProgress(), lesson.id, correct, NOW);
    expect(parseAwsProgress(JSON.stringify(progress))).toEqual(progress);
    expect(parseAwsProgress("bad json")).toEqual(emptyAwsProgress());
    expect(parseAwsProgress('{"version":2}')).toEqual(emptyAwsProgress());
    const malformed = { ...progress, lessons: { ...progress.lessons, [AWS_LESSONS[1].id]: { ...progress.lessons[lesson.id], due: "tomorrow" } } };
    expect(Object.keys(parseAwsProgress(JSON.stringify(malformed)).lessons)).toEqual([lesson.id]);
  });

  it("counts study days in local time and carries yesterday's streak until today is studied", () => {
    let progress = recordAwsAttempt(emptyAwsProgress(), lesson.id, correct, NOW - AWS_DAY);
    expect(awsStudyStreak(progress, new Date(NOW))).toBe(1);
    progress = recordAwsAttempt(progress, lesson.id, correct, NOW);
    expect(awsStudyStreak(progress, new Date(NOW))).toBe(2);
    expect(progress.days[todayISO(new Date(NOW))].lessons).toEqual([lesson.id]);
    expect(awsStudyStreak(progress, new Date(NOW + 2 * AWS_DAY))).toBe(0);
  });
});
