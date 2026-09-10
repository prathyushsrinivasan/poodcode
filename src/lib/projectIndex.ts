// A project's syntax primer and glossary, gathered from every module into one
// searchable list.
//
// WHY THIS EXISTS. The Projects track's whole pitch is that no module uses a
// piece of syntax an earlier one has not taught — a claim enforced at build time
// by `_lint_syntax_taught` in tools/projects_track.py. But the evidence for it
// was scattered one card at a time across module pages: by module 7 the Todo API
// teaches roughly forty forms and names fifty terms, and the only way to answer
// "where was `writeHead` explained?" was to remember which module it was in and
// navigate there. The data to answer it was always in the seed; nothing ever
// gathered it.
//
// FIRST-TAUGHT WINS. A module marks an entry `recap: true` when an earlier
// module introduced it and this one is only reminding you. Those are dropped:
// an index wants the place a thing was EXPLAINED, and a recap card is a pointer,
// not an explanation. Should a form somehow appear un-recapped twice, the lower
// module number wins for the same reason.

import type { Endpoint, GlossaryItem, Project, ProjectModule, SyntaxItem } from "../types";

/** Where a module sits, carried on every entry so a row can link back to it. */
export interface ModuleRef {
  moduleKey: string;
  moduleNumber: number;
  moduleTitle: string;
  phase: string;
}

export interface SyntaxEntry extends ModuleRef, SyntaxItem {}

export interface GlossaryEntry extends ModuleRef, GlossaryItem {}

/**
 * One line of prose that belongs to a module — a pitfall or an acceptance
 * check. A pitfall additionally names the step it was written in, so a row can
 * deep-link to the exact step rather than the top of a long module page.
 */
export interface NoteEntry extends ModuleRef {
  text: string;
  /** Empty for module-level notes (acceptance checks). */
  stepKey: string;
  stepTitle: string;
}

/** Field separator for the joined strings below.
 *
 * A NUL rather than a space, so that a search can never match text spanning two
 * fields ("headers" ending one and "Status" starting the next) and two endpoint
 * rows can never compare equal by coincidence of where their fields end. It was
 * previously a literal NUL byte inside the string, which made this file binary
 * to every tool that looked at it. */
const SEP = "\u0000";

const refTo = (m: ProjectModule): ModuleRef => ({
  moduleKey: m.key,
  moduleNumber: m.number,
  moduleTitle: m.title,
  phase: m.phase,
});

/** Modules that have actually been written, in roadmap order. A planned
 * placeholder has an empty syntax primer, so including them would only add
 * noise — but filtering explicitly says why. */
const authoredModules = (project: Project): ProjectModule[] =>
  (project.modules ?? []).filter((m) => m.authored).sort((a, b) => a.number - b.number);

/**
 * Every piece of syntax the project teaches, in the order it is introduced.
 *
 * Recaps are dropped and the earliest module wins, so this is a syllabus: read
 * top to bottom it is the exact order the track puts TypeScript in front of you.
 */
export function buildSyntaxIndex(project: Project): SyntaxEntry[] {
  const seen = new Map<string, SyntaxEntry>();
  for (const m of authoredModules(project)) {
    for (const item of m.syntax ?? []) {
      if (item.recap) continue;
      // Modules are walked in order, so the first sighting is the earliest.
      if (!seen.has(item.form)) seen.set(item.form, { ...item, ...refTo(m) });
    }
  }
  return [...seen.values()];
}

/**
 * Every term the project defines, A-Z.
 *
 * Sorted by term rather than by module because this is the list you arrive at
 * with a word in hand — the opposite of the syntax index, which you read in
 * order. Terms are deduplicated case-insensitively, keeping the earliest module.
 */
export function buildGlossaryIndex(project: Project): GlossaryEntry[] {
  const seen = new Map<string, GlossaryEntry>();
  for (const m of authoredModules(project)) {
    for (const item of m.glossary ?? []) {
      const key = item.term.trim().toLowerCase();
      if (key && !seen.has(key)) seen.set(key, { ...item, ...refTo(m) });
    }
  }
  return [...seen.values()].sort((a, b) =>
    a.term.localeCompare(b.term, undefined, { sensitivity: "base" })
  );
}

/**
 * Every mistake the project warns you about, in the order you would hit them.
 *
 * WHY THIS IS AN INDEX AND NOT JUST A CARD. A step's "things that will cost you
 * an hour" list is the most concentrated writing in the track — by module 8 the
 * Todo API carries forty-odd of them — and every one lives inside a collapsed
 * step inside a module you have already finished. That is exactly backwards:
 * you want the list when something is broken, which is precisely when you are
 * not reading the module it was written in.
 *
 * Unlike the syntax index this one is NOT deduplicated per module: two modules
 * warning about the same trap from different angles is the track working, not a
 * duplicate. Only a byte-identical repeat is dropped.
 */
export function buildPitfallIndex(project: Project): NoteEntry[] {
  const seen = new Set<string>();
  const out: NoteEntry[] = [];
  for (const m of authoredModules(project)) {
    for (const step of m.steps ?? []) {
      for (const text of step.pitfalls ?? []) {
        const t = text.trim();
        if (!t || seen.has(t)) continue;
        seen.add(t);
        out.push({ ...refTo(m), text: t, stepKey: step.key, stepTitle: step.title });
      }
    }
  }
  return out;
}

/**
 * Every module's acceptance checklist, gathered — the project's definition of
 * done, module by module.
 *
 * The project page already carries the *finished* application's acceptance
 * list, which is eight lines about something that does not exist yet. This is
 * the other one: what has to be true at the module you are on, and what was
 * supposed to be true at every module you have already passed. It is the list
 * to walk down when something that used to work has stopped.
 */
export function buildCheckIndex(project: Project): NoteEntry[] {
  const out: NoteEntry[] = [];
  for (const m of authoredModules(project)) {
    for (const text of m.acceptance ?? []) {
      const t = text.trim();
      if (t) out.push({ ...refTo(m), text: t, stepKey: "", stepTitle: "" });
    }
  }
  return out;
}

/**
 * Every module's cheat sheet, in roadmap order.
 *
 * Reusing `NoteEntry` rather than inventing a type: a cheat sheet is one blob
 * of markdown belonging to a module, which is exactly what the shape says. The
 * `text` is markdown and the caller renders it as such.
 */
export function buildCheatsheetIndex(project: Project): NoteEntry[] {
  const out: NoteEntry[] = [];
  for (const m of authoredModules(project)) {
    const t = (m.cheatsheet ?? "").trim();
    if (t) out.push({ ...refTo(m), text: t, stepKey: "", stepTitle: "" });
  }
  return out;
}

/**
 * One row of the API contract, plus its history.
 *
 * `ModuleRef` on the entry is where the row was **added**; the fields hold its
 * **current** description; `revisions` names every later module where that
 * description actually changed.
 */
export interface ContractEntry extends ModuleRef, Endpoint {
  /** Modules that changed this row after it was introduced, earliest first. */
  revisions: ModuleRef[];
}

/** The contract-bearing part of an endpoint: what a client must send, what it
 * gets back, and under which codes.
 *
 * `purpose` is deliberately NOT in here. It is prose, and a later module often
 * words an unchanged route better than the one that introduced it — module 9
 * describes `GET /todos` as returning "`[]` on a fresh server", which is a
 * clearer sentence about a route that has not moved. Counting rewordings as
 * revisions turns the column into noise, and a noisy column is one nobody
 * reads. */
const describes = (e: Endpoint) => [e.request, e.response, e.status].join(SEP);

/** A route the project has retired.
 *
 * The convention lives in the data rather than the schema: a module that
 * removes a route re-declares it with an em-dash status. Module 8's
 * `POST /echo` is scaffolding with a stated expiry date and module 9 spends it
 * — without a way to say so, the contract index would go on advertising a
 * route the application no longer has. */
export const isRetired = (e: Endpoint): boolean => {
  const s = e.status.trim();
  return s === "" || s === "—";
};

/**
 * The API contract, assembled from every module that declared a piece of it —
 * in the order the project builds it, with the modules that later changed each
 * row.
 *
 * WHY THIS IS WORTH GATHERING. The project page shows the *finished*
 * application's contract, which is a promise about code that does not exist
 * yet, and each module page shows only its own rows. Neither answers the two
 * questions people actually have: "when does `DELETE /todos/:id` start
 * working?" and "did `GET /todos` change under me?" — and the second one really
 * happens, because module 18 replaces the bare array with an envelope on
 * purpose. A row that a module merely re-lists unchanged is not a revision and
 * is not reported as one.
 */
export function buildContractIndex(project: Project): ContractEntry[] {
  const byRoute = new Map<string, ContractEntry>();
  for (const m of authoredModules(project)) {
    for (const e of m.endpoints ?? []) {
      const key = `${e.method} ${e.path}`;
      const seen = byRoute.get(key);
      if (!seen) {
        byRoute.set(key, { ...e, ...refTo(m), revisions: [] });
        continue;
      }
      if (describes(seen) === describes(e)) {
        // Re-listed, not changed. Keep the row's origin and its history, but
        // take the newer prose: a later module has often had more to say about
        // a route it did not move.
        byRoute.set(key, { ...seen, purpose: e.purpose });
        continue;
      }
      // Keep the row's origin, adopt its newest description.
      const { moduleKey, moduleNumber, moduleTitle, phase, revisions } = seen;
      byRoute.set(key, {
        ...e,
        moduleKey,
        moduleNumber,
        moduleTitle,
        phase,
        revisions: [...revisions, refTo(m)],
      });
    }
  }
  return [...byRoute.values()];
}

/** The fields of an entry a search looks at, kept as separate strings so that a
 * query cannot match text spanning two of them — see the NUL join below. */
function searchFields(
  entry: SyntaxEntry | GlossaryEntry | NoteEntry | ContractEntry
): string[] {
  if ("form" in entry) return [entry.form, entry.means, entry.note, entry.moduleTitle];
  if ("term" in entry) return [entry.term, entry.def, entry.moduleTitle];
  if ("method" in entry) {
    return [
      `${entry.method} ${entry.path}`,
      entry.purpose,
      entry.request,
      entry.response,
      entry.status,
      entry.moduleTitle,
    ];
  }
  return [entry.text, entry.stepTitle, entry.moduleTitle];
}

/** Case-insensitive substring match over every field worth searching.
 *
 * The `note` is included on purpose: a lot of what these cards are worth lives
 * in the gotcha rather than the form, and "headers sent" should find
 * `res.writeHead` even though those words appear nowhere in the syntax itself. */
export function matchesQuery(
  entry: SyntaxEntry | GlossaryEntry | NoteEntry | ContractEntry,
  query: string
): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  const haystack = searchFields(entry);
  return haystack.join(SEP).toLowerCase().includes(q);
}

/** Group entries by the module that introduced them, preserving input order
 * within each group and ordering the groups by module number. */
export function groupByModule<T extends ModuleRef>(entries: readonly T[]): {
  ref: ModuleRef;
  entries: T[];
}[] {
  const groups = new Map<string, { ref: ModuleRef; entries: T[] }>();
  for (const e of entries) {
    const g = groups.get(e.moduleKey);
    if (g) g.entries.push(e);
    else groups.set(e.moduleKey, { ref: e, entries: [e] });
  }
  return [...groups.values()].sort((a, b) => a.ref.moduleNumber - b.ref.moduleNumber);
}
