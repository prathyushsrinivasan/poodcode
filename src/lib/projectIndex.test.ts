import { describe, it, expect } from "vitest";
import type { Project, ProjectModule } from "../types";
import {
  buildCheatsheetIndex,
  buildCheckIndex,
  buildContractIndex,
  buildGlossaryIndex,
  buildPitfallIndex,
  buildSyntaxIndex,
  groupByModule,
  isRetired,
  matchesQuery,
} from "./projectIndex";

const syn = (form: string, means = "", note = "", recap = false) => ({
  form,
  means,
  example: "",
  note,
  recap,
});

const mod = (
  number: number,
  key: string,
  title: string,
  syntax: ReturnType<typeof syn>[],
  glossary: { term: string; def: string }[] = [],
  authored = true
) =>
  ({ number, key, title, phase: "network", authored, syntax, glossary }) as unknown as ProjectModule;

const proj = (modules: ProjectModule[]) => ({ modules }) as unknown as Project;

/** A module carrying steps and an acceptance list — what the pitfall and check
 * indexes read, and what `mod` above deliberately leaves off. */
const notesMod = (
  number: number,
  key: string,
  title: string,
  steps: { key: string; title: string; pitfalls: string[] }[],
  acceptance: string[] = [],
  authored = true
) =>
  ({
    number,
    key,
    title,
    phase: "crud",
    authored,
    syntax: [],
    glossary: [],
    steps,
    acceptance,
  }) as unknown as ProjectModule;

describe("buildSyntaxIndex", () => {
  it("gathers every module's primer in the order it is introduced", () => {
    const p = proj([
      mod(1, "m1", "Shape", [syn("type Todo = { … }")]),
      mod(2, "m2", "Store", [syn(".push(")], []),
    ]);
    expect(buildSyntaxIndex(p).map((e) => e.form)).toEqual(["type Todo = { … }", ".push("]);
  });

  it("carries the module each entry was taught in, so a row can link back", () => {
    const p = proj([mod(5, "todo-json", "Status codes and JSON", [syn("res.writeHead(")])]);
    expect(buildSyntaxIndex(p)[0]).toMatchObject({
      form: "res.writeHead(",
      moduleKey: "todo-json",
      moduleNumber: 5,
      moduleTitle: "Status codes and JSON",
    });
  });

  it("drops recaps — the index wants where a thing was explained, not reminded", () => {
    const p = proj([
      mod(5, "m5", "Five", [syn("send(")]),
      mod(6, "m6", "Six", [syn("req.url"), syn("send(", "", "", true)]),
    ]);
    const forms = buildSyntaxIndex(p).map((e) => e.form);
    expect(forms).toEqual(["send(", "req.url"]);
  });

  it("keeps the earliest module when a form is introduced twice", () => {
    const p = proj([
      mod(3, "m3", "Three", [syn("=>")]),
      mod(9, "m9", "Nine", [syn("=>")]),
    ]);
    const idx = buildSyntaxIndex(p);
    expect(idx).toHaveLength(1);
    expect(idx[0]?.moduleNumber).toBe(3);
  });

  it("ignores planned modules, which carry an empty primer anyway", () => {
    const p = proj([
      mod(1, "m1", "One", [syn("type ")]),
      mod(2, "m2", "Planned", [], [], false),
    ]);
    expect(buildSyntaxIndex(p)).toHaveLength(1);
  });

  it("reads modules in roadmap order even when the seed lists them out of order", () => {
    const p = proj([
      mod(6, "m6", "Six", [syn("dup", "later")]),
      mod(4, "m4", "Four", [syn("dup", "earlier")]),
    ]);
    expect(buildSyntaxIndex(p)[0]?.moduleNumber).toBe(4);
  });

  it("survives a module with no primer at all", () => {
    const p = proj([{ number: 1, key: "m", title: "M", authored: true } as ProjectModule]);
    expect(buildSyntaxIndex(p)).toEqual([]);
  });
});

describe("buildGlossaryIndex", () => {
  it("sorts terms A-Z rather than by module, because you arrive with a word", () => {
    const p = proj([
      mod(1, "m1", "One", [], [{ term: "port", def: "a number" }]),
      mod(2, "m2", "Two", [], [{ term: "handler", def: "a function" }]),
    ]);
    expect(buildGlossaryIndex(p).map((e) => e.term)).toEqual(["handler", "port"]);
  });

  it("deduplicates case-insensitively, keeping the earliest definition", () => {
    const p = proj([
      mod(2, "m2", "Two", [], [{ term: "Handler", def: "first" }]),
      mod(7, "m7", "Seven", [], [{ term: "handler", def: "second" }]),
    ]);
    const idx = buildGlossaryIndex(p);
    expect(idx).toHaveLength(1);
    expect(idx[0]).toMatchObject({ def: "first", moduleNumber: 2 });
  });

  it("skips a blank term rather than indexing an empty row", () => {
    const p = proj([mod(1, "m1", "One", [], [{ term: "   ", def: "nothing" }])]);
    expect(buildGlossaryIndex(p)).toEqual([]);
  });
});

describe("buildPitfallIndex", () => {
  it("gathers every step's traps in roadmap order, naming the step each came from", () => {
    const p = proj([
      notesMod(7, "m7", "Routing", [
        { key: "match", title: "One route", pitfalls: ["`||` where you meant `&&`"] },
      ]),
      notesMod(8, "m8", "Body", [
        { key: "stream", title: "The body is not there yet", pitfalls: ["answered too early"] },
        { key: "await", title: "async and await", pitfalls: ["forgetting `await`"] },
      ]),
    ]);
    expect(buildPitfallIndex(p)).toEqual([
      expect.objectContaining({ text: "`||` where you meant `&&`", moduleNumber: 7, stepKey: "match" }),
      expect.objectContaining({ text: "answered too early", stepTitle: "The body is not there yet" }),
      expect.objectContaining({ text: "forgetting `await`", stepKey: "await" }),
    ]);
  });

  it("keeps the same trap warned about twice in different words", () => {
    // Two modules describing one trap from different angles is the track
    // working, so only a byte-identical repeat is dropped.
    const p = proj([
      notesMod(4, "m4", "Server", [{ key: "a", title: "A", pitfalls: ["no res.end() hangs"] }]),
      notesMod(7, "m7", "Routing", [
        { key: "b", title: "B", pitfalls: ["no fall-through hangs", "no res.end() hangs"] },
      ]),
    ]);
    expect(buildPitfallIndex(p).map((e) => e.text)).toEqual([
      "no res.end() hangs",
      "no fall-through hangs",
    ]);
  });

  it("skips planned modules and steps with nothing to warn about", () => {
    const p = proj([
      notesMod(1, "m1", "One", [{ key: "s", title: "S", pitfalls: [] }]),
      notesMod(2, "m2", "Planned", [{ key: "s", title: "S", pitfalls: ["x"] }], [], false),
    ]);
    expect(buildPitfallIndex(p)).toEqual([]);
  });

  it("survives a module with no steps at all", () => {
    const p = proj([mod(1, "m", "M", [])]);
    expect(buildPitfallIndex(p)).toEqual([]);
  });
});

describe("buildCheckIndex", () => {
  it("gathers each module's acceptance list, in roadmap order", () => {
    const p = proj([
      notesMod(8, "m8", "Body", [], ["the echo returns what you posted"]),
      notesMod(7, "m7", "Routing", [], ["GET /todos returns the list", "/nonsense 404s"]),
    ]);
    expect(buildCheckIndex(p).map((e) => [e.moduleNumber, e.text])).toEqual([
      [7, "GET /todos returns the list"],
      [7, "/nonsense 404s"],
      [8, "the echo returns what you posted"],
    ]);
  });

  it("carries no step, because a check belongs to the whole module", () => {
    const p = proj([notesMod(5, "m5", "JSON", [], ["every response is JSON"])]);
    expect(buildCheckIndex(p)[0]).toMatchObject({ stepKey: "", stepTitle: "" });
  });

  it("drops blank rows rather than indexing an empty check", () => {
    const p = proj([notesMod(5, "m5", "JSON", [], ["  ", "real one"])]);
    expect(buildCheckIndex(p).map((e) => e.text)).toEqual(["real one"]);
  });
});

describe("buildContractIndex", () => {
  const ep = (method: string, path: string, response = "", status = "200") => ({
    method,
    path,
    purpose: "",
    request: "",
    response,
    status,
  });
  const epMod = (
    number: number,
    key: string,
    endpoints: ReturnType<typeof ep>[],
    authored = true
  ) =>
    ({
      number,
      key,
      title: `M${number}`,
      phase: "crud",
      authored,
      syntax: [],
      glossary: [],
      steps: [],
      acceptance: [],
      endpoints,
    }) as unknown as ProjectModule;

  it("dates each row to the module that introduced it", () => {
    const p = proj([
      epMod(7, "m7", [ep("GET", "/todos", "[Todo]")]),
      epMod(9, "m9", [ep("GET", "/todos", "[Todo]"), ep("POST", "/todos", "Todo", "201")]),
    ]);
    expect(buildContractIndex(p).map((e) => [e.method, e.moduleNumber])).toEqual([
      ["GET", 7],
      ["POST", 9],
    ]);
  });

  it("does not call a re-listed identical row a revision", () => {
    // Modules 8 and 9 both list GET /todos unchanged, because a module's
    // endpoint table shows the routes it touches, not only the ones it adds.
    const p = proj([
      epMod(7, "m7", [ep("GET", "/todos", "[Todo]")]),
      epMod(8, "m8", [ep("GET", "/todos", "[Todo]")]),
      epMod(9, "m9", [ep("GET", "/todos", "[Todo]")]),
    ]);
    expect(buildContractIndex(p)[0]?.revisions).toEqual([]);
  });

  it("records a real change, keeps the origin and adopts the newest wording", () => {
    // The project's one deliberate breaking change: module 18 replaces the
    // bare array with an {items,total} envelope.
    const p = proj([
      epMod(7, "m7", [ep("GET", "/todos", "[Todo]")]),
      epMod(18, "m18", [ep("GET", "/todos", "{items,total}")]),
    ]);
    const [row] = buildContractIndex(p);
    expect(row).toMatchObject({ moduleNumber: 7, response: "{items,total}" });
    expect(row?.revisions.map((r) => r.moduleNumber)).toEqual([18]);
  });

  it("does not call a reworded purpose a revision", () => {
    // Module 9 describes GET /todos as "`[]` on a fresh server" — a clearer
    // sentence about a route that has not moved since module 7.
    const p = proj([
      epMod(7, "m7", [{ ...ep("GET", "/todos", "[Todo]"), purpose: "List every todo" }]),
      epMod(9, "m9", [
        { ...ep("GET", "/todos", "[Todo]"), purpose: "List every todo — [] on a fresh server" },
      ]),
    ]);
    const [row] = buildContractIndex(p);
    expect(row?.revisions).toEqual([]);
    expect(row?.purpose).toBe("List every todo — [] on a fresh server"); // newest wording wins
  });

  it("carries a retirement through, so a removed route stops being advertised", () => {
    const p = proj([
      epMod(8, "m8", [ep("POST", "/echo", '{"echo":"…"}', "200")]),
      epMod(9, "m9", [ep("POST", "/echo", "—", "—")]),
    ]);
    const [row] = buildContractIndex(p);
    expect(row).toMatchObject({ moduleNumber: 8 }); // still dated to where it arrived
    expect(row?.revisions.map((r) => r.moduleNumber)).toEqual([9]);
    expect(isRetired(row!)).toBe(true);
  });

  it("does not call a live route retired", () => {
    expect(isRetired(ep("GET", "/todos", "[Todo]", "200"))).toBe(false);
    expect(isRetired(ep("GET", "/todos", "[Todo]", "   "))).toBe(true);
  });

  it("treats the same path under a different verb as its own row", () => {
    const p = proj([epMod(9, "m9", [ep("GET", "/todos"), ep("POST", "/todos", "", "201")])]);
    expect(buildContractIndex(p)).toHaveLength(2);
  });

  it("ignores planned modules and modules that declare no routes", () => {
    const p = proj([
      epMod(9, "m9", [ep("GET", "/todos")]),
      epMod(10, "m10", [ep("GET", "/todos/:id")], false),
      mod(11, "m11", "No routes", []),
    ]);
    expect(buildContractIndex(p).map((e) => e.path)).toEqual(["/todos"]);
  });
});

describe("buildCheatsheetIndex", () => {
  const sheetMod = (number: number, key: string, cheatsheet: string, authored = true) =>
    ({
      number,
      key,
      title: `M${number}`,
      phase: "crud",
      authored,
      syntax: [],
      glossary: [],
      steps: [],
      acceptance: [],
      cheatsheet,
    }) as unknown as ProjectModule;

  it("gathers one sheet per module that wrote one, in roadmap order", () => {
    const p = proj([
      sheetMod(9, "m9", "## nine"),
      sheetMod(7, "m7", "## seven"),
      sheetMod(8, "m8", "   "),
    ]);
    expect(buildCheatsheetIndex(p).map((e) => [e.moduleNumber, e.text])).toEqual([
      [7, "## seven"],
      [9, "## nine"],
    ]);
  });

  it("skips planned modules", () => {
    expect(buildCheatsheetIndex(proj([sheetMod(9, "m9", "## nine", false)]))).toEqual([]);
  });
});

describe("matchesQuery", () => {
  const p = proj([
    mod(5, "m5", "Status codes and JSON", [
      syn("res.writeHead(", "Set the status and headers", "Throws once headers are sent"),
    ]),
  ]);
  const entry = buildSyntaxIndex(p)[0]!;

  it("matches an empty query, so an unsearched list renders whole", () => {
    expect(matchesQuery(entry, "")).toBe(true);
    expect(matchesQuery(entry, "   ")).toBe(true);
  });

  it("matches the form, ignoring case", () => {
    expect(matchesQuery(entry, "WRITEHEAD")).toBe(true);
  });

  it("matches the gotcha, where half the value of a card lives", () => {
    expect(matchesQuery(entry, "headers are sent")).toBe(true);
  });

  it("matches the module title, so you can search by where you read it", () => {
    expect(matchesQuery(entry, "status codes")).toBe(true);
  });

  it("does not match across two fields joined together", () => {
    // "headers" ends one field and "Status" starts another; the separator keeps
    // a query from matching text that is not contiguous in any one of them.
    expect(matchesQuery(entry, "headers Status")).toBe(false);
  });

  it("searches a pitfall by its symptom, which is how you arrive at it", () => {
    const [trap] = buildPitfallIndex(
      proj([
        notesMod(8, "m8", "Reading a request body", [
          {
            key: "await",
            title: "async and await",
            pitfalls: ["Forgetting `await`. The client gets a cheerful 200 with `{\"echo\":{}}`."],
          },
        ]),
      ])
    );
    expect(matchesQuery(trap!, "cheerful 200")).toBe(true);
    expect(matchesQuery(trap!, "async and await")).toBe(true); // the step title
    expect(matchesQuery(trap!, "request body")).toBe(true); // the module title
    expect(matchesQuery(trap!, "writeHead")).toBe(false);
  });

  it("searches a contract row by verb, path, status and purpose", () => {
    const [route] = buildContractIndex(
      proj([
        {
          number: 9,
          key: "m9",
          title: "POST /todos — create",
          phase: "crud",
          authored: true,
          syntax: [],
          glossary: [],
          steps: [],
          acceptance: [],
          endpoints: [
            {
              method: "POST",
              path: "/todos",
              purpose: "Create a todo from the body's title",
              request: '{"title":"Buy milk"}',
              response: "Todo",
              status: "201 · 500 on bad JSON",
            },
          ],
        } as unknown as ProjectModule,
      ])
    );
    expect(matchesQuery(route!, "POST /todos")).toBe(true);
    expect(matchesQuery(route!, "201")).toBe(true);
    expect(matchesQuery(route!, "create a todo")).toBe(true);
    expect(matchesQuery(route!, "DELETE")).toBe(false);
  });

  it("searches a glossary entry's definition too", () => {
    const g = buildGlossaryIndex(
      proj([mod(4, "m4", "Server", [], [{ term: "port", def: "the number a server listens on" }])])
    )[0]!;
    expect(matchesQuery(g, "listens on")).toBe(true);
    expect(matchesQuery(g, "writeHead")).toBe(false);
  });
});

describe("groupByModule", () => {
  it("groups by module and orders the groups by module number", () => {
    const p = proj([
      mod(7, "m7", "Seven", [syn("a"), syn("b")]),
      mod(2, "m2", "Two", [syn("c")]),
    ]);
    const groups = groupByModule(buildSyntaxIndex(p));
    expect(groups.map((g) => g.ref.moduleNumber)).toEqual([2, 7]);
    expect(groups[1]?.entries.map((e) => e.form)).toEqual(["a", "b"]);
  });

  it("returns nothing for nothing", () => {
    expect(groupByModule([])).toEqual([]);
  });
});
