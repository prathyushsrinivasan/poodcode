import { describe, expect, it } from "vitest";
import type { CardReview, MasteryProgress, MasteryTrack, WeeklyCourse } from "../types";
import { courseInsight, deckOf, masteryInsight, orderTracks, reviewByDeck, reviewHealth, share, type TrackInsight } from "./insights";

const card = (id: string, patch: Partial<CardReview> = {}): CardReview => ({
  card_id: id,
  ease: 2.5,
  reps: 1,
  lapses: 0,
  interval_days: 1,
  due_date: "2026-09-30",
  last_quality: 2,
  ...patch,
});

describe("reviewHealth", () => {
  it("counts due, mature and the lapse rate", () => {
    const h = reviewHealth(
      [card("a", { due_date: "2026-09-01" }), card("b", { interval_days: 30, reps: 5, lapses: 1 }), card("c", { last_quality: 0 })],
      "2026-09-28"
    );
    expect(h.total).toBe(3);
    expect(h.due).toBe(1);
    expect(h.mature).toBe(1);
    expect(h.young).toBe(2);
    // 7 passes + 1 lapse = 8 reviews, one of them forgotten.
    expect(h.lapseRate).toBeCloseTo(1 / 8);
    expect(h.lastPass).toBeCloseTo(2 / 3);
  });

  it("is all zeros for no cards", () => {
    expect(reviewHealth([], "2026-01-01")).toMatchObject({ total: 0, lapseRate: 0, lastPass: 0 });
  });
});

describe("decks", () => {
  it("reads the namespace", () => {
    expect(deckOf("jp-vocab#w1")).toBe("日本語 vocabulary");
    expect(deckOf("dsa-check:arrays:0")).toBe("Curriculum self-checks");
    expect(deckOf("dsa-route:arrays")).toBe("Curriculum recognition");
    expect(deckOf("jp_basics#配列")).toBe("日本語 glossaries");
    expect(deckOf("ts_generics#T")).toBe("Learn decks");
  });

  it("groups and sorts by size", () => {
    const out = reviewByDeck([card("jp-vocab#1"), card("dsa-check:x:0"), card("dsa-check:x:1")], "2026-09-28");
    expect(out.map((d) => d.deck)).toEqual(["Curriculum self-checks", "日本語 vocabulary"]);
  });
});

describe("track insights", () => {
  it("counts authored course weeks marked done under the prefix", () => {
    const course = {
      unit_label: "Module",
      weeks: [
        { number: 1, authored: true },
        { number: 2, authored: true },
        { number: 3, authored: false },
      ],
    } as unknown as WeeklyCourse;
    const t = courseInsight(course, "java-course", new Set(["java-course:w1", "ts-course:w2"]), {
      key: "java",
      label: "Java",
      icon: "java",
      href: "/java-course",
    });
    expect([t.done, t.total, t.unit]).toEqual([1, 2, "module"]);
    expect(t.note).toMatch(/1 more module/);
  });

  it("counts Mastery core weeks with a completion, ignoring optional weeks and other tracks", () => {
    const track = { key: "ts", title: "TS", weeks: [{ week: 1 }, { week: 2 }, { week: 3, optional: true }] } as unknown as MasteryTrack;
    const rows = [
      { track_key: "ts", week: 1, completed_at: "x", study_seconds: 3600 },
      { track_key: "ts", week: 3, completed_at: "x", study_seconds: 0 },
      { track_key: "java", week: 2, completed_at: "x", study_seconds: 0 },
    ] as unknown as MasteryProgress[];
    const t = masteryInsight(track, rows);
    expect([t.done, t.total]).toEqual([1, 2]);
    expect(t.note).toBe("1 h studied there");
  });

  it("orders in-progress tracks first, untouched ones last", () => {
    const t = (key: string, done: number, total: number): TrackInsight => ({ key, label: key, icon: "x", href: "/", done, total, unit: "u" });
    expect(orderTracks([t("none", 0, 5), t("done", 3, 3), t("half", 2, 4), t("empty", 0, 0)]).map((x) => x.key)).toEqual([
      "half",
      "done",
      "none",
      "empty",
    ]);
    expect(share(t("x", 1, 4))).toBe(0.25);
  });
});
