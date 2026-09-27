import { describe, expect, it } from "vitest";
import { emptyFilter } from "./filters";
import {
  BUILTIN_PRESETS,
  DEFAULT_COLUMNS,
  activeFilterCount,
  deletePreset,
  matchesPreset,
  nextRow,
  parseColumns,
  parsePresets,
  savePreset,
  toggleColumn,
  type BrowseState,
} from "./browse";

const state = (patch: Partial<BrowseState["filter"]> = {}, extra: Partial<BrowseState> = {}): BrowseState => ({
  filter: { ...emptyFilter, ...patch },
  mineOnly: false,
  solvableNow: false,
  ...extra,
});

describe("presets", () => {
  it("round-trips through storage", () => {
    const list = savePreset([], "Hard ones", state({ difficulties: ["Hard"] }), 42);
    const back = parsePresets(JSON.stringify(list));
    expect(back).toHaveLength(1);
    expect(back[0].name).toBe("Hard ones");
    expect(back[0].filter.difficulties).toEqual(["Hard"]);
    expect(back[0].id).toBe("user:42");
  });

  it("replaces a preset with the same name, ignoring case", () => {
    let list = savePreset([], "Mine", state({ status: "solved" }), 1);
    list = savePreset(list, "mine", state({ status: "unsolved" }), 2);
    expect(list).toHaveLength(1);
    expect(list[0].filter.status).toBe("unsolved");
  });

  it("refuses a blank name", () => {
    expect(savePreset([], "   ", state())).toEqual([]);
  });

  it("deletes by id", () => {
    const list = savePreset(savePreset([], "a", state(), 1), "b", state(), 2);
    expect(deletePreset(list, "user:1").map((p) => p.name)).toEqual(["b"]);
  });

  it("fills missing fields from an older stored shape", () => {
    const back = parsePresets(JSON.stringify([{ id: "x", name: "old", filter: { search: "tree" } }]));
    expect(back[0].filter.difficulties).toEqual([]);
    expect(back[0].filter.search).toBe("tree");
    expect(back[0].mineOnly).toBe(false);
  });

  it("survives garbage", () => {
    expect(parsePresets("not json")).toEqual([]);
    expect(parsePresets(JSON.stringify({ a: 1 }))).toEqual([]);
    expect(parsePresets(JSON.stringify([null, 3, { name: "no id" }]))).toEqual([]);
  });

  it("recognises the state a preset produces", () => {
    const p = BUILTIN_PRESETS[0];
    expect(matchesPreset(p, { filter: p.filter, mineOnly: false, solvableNow: false })).toBe(true);
    expect(matchesPreset(p, state())).toBe(false);
  });
});

describe("activeFilterCount", () => {
  it("counts each chosen value and flag", () => {
    expect(activeFilterCount(state())).toBe(0);
    expect(activeFilterCount(state({ difficulties: ["Easy", "Hard"], search: "x", favoritesOnly: true }))).toBe(4);
    expect(activeFilterCount(state({}, { mineOnly: true }))).toBe(1);
  });

  it("does not count the sort", () => {
    expect(activeFilterCount(state({ sort: "title" }))).toBe(0);
  });
});

describe("columns", () => {
  it("defaults when nothing is stored or it is unreadable", () => {
    expect(parseColumns(null)).toEqual(DEFAULT_COLUMNS);
    expect(parseColumns("{")).toEqual(DEFAULT_COLUMNS);
  });

  it("drops unknown keys and keeps table order", () => {
    expect(parseColumns(JSON.stringify(["solved", "bogus", "favorite"]))).toEqual(["favorite", "solved"]);
  });

  it("toggles a column in its table position", () => {
    expect(toggleColumn(["favorite", "solved"], "difficulty")).toEqual(["favorite", "difficulty", "solved"]);
    expect(toggleColumn(["favorite", "solved"], "favorite")).toEqual(["solved"]);
  });
});

describe("nextRow", () => {
  it("moves and clamps", () => {
    expect(nextRow("ArrowDown", 0, 3)).toBe(1);
    expect(nextRow("ArrowDown", 2, 3)).toBe(2);
    expect(nextRow("ArrowUp", 0, 3)).toBe(0);
    expect(nextRow("End", 0, 3)).toBe(2);
    expect(nextRow("Home", 2, 3)).toBe(0);
    expect(nextRow("PageDown", 0, 30, 10)).toBe(10);
  });

  it("ignores other keys and empty tables", () => {
    expect(nextRow("a", 0, 3)).toBeNull();
    expect(nextRow("ArrowDown", 0, 0)).toBeNull();
  });
});
