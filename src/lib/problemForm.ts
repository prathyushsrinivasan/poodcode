/**
 * Validation for the problem form (UI_ROADMAP H3).
 *
 * The form used to check one thing — a title — and report it in a toast that
 * vanished before it could be read, while a duplicate slug or a test case with
 * no expected output only failed later, in the backend or on first Submit.
 * Every rule lives here, keyed by the field it belongs to, so the form can put
 * the message beside the field and the tests can pin the rules down.
 */

import type { Problem } from "../types";

export const slugify = (s: string) =>
  s
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

export type Severity = "error" | "warning";

export interface Issue {
  /** A field path: "title", "slug", "test_cases.2.expected_output", … */
  field: string;
  message: string;
  severity: Severity;
}

/**
 * Check a problem before saving. Errors block the save; warnings are shown but
 * allowed (a problem with no hidden tests is legal, just not much of a test).
 */
export function validateProblem(p: Problem, takenSlugs: ReadonlyMap<string, number> = new Map()): Issue[] {
  const out: Issue[] = [];
  const err = (field: string, message: string) => out.push({ field, message, severity: "error" });
  const warn = (field: string, message: string) => out.push({ field, message, severity: "warning" });

  if (!p.title.trim()) err("title", "A problem needs a title.");

  const slug = p.slug.trim() || slugify(p.title);
  if (!slug) err("slug", "A slug is made from the title — give it a title with letters or digits.");
  else if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug)) err("slug", "Lowercase letters, digits and single hyphens only.");
  else {
    const owner = takenSlugs.get(slug);
    if (owner !== undefined && owner !== p.id) err("slug", `“${slug}” is already used by another problem.`);
  }

  if (!p.description.trim()) warn("description", "No statement yet — the solver sees an empty page.");

  p.examples.forEach((e, i) => {
    if (!e.input.trim() && !e.output.trim()) err(`examples.${i}`, "An example needs an input or an output — or remove it.");
  });

  const judged = p.test_cases.filter((c) => c.kind !== "user");
  if (judged.length === 0) warn("test_cases", "No example or hidden cases, so Run and Submit have nothing to check.");
  else if (!p.test_cases.some((c) => c.kind === "hidden")) warn("test_cases", "No hidden cases: Submit will only re-check the examples.");

  const names = new Map<string, number>();
  p.test_cases.forEach((c, i) => {
    if (!c.name.trim()) err(`test_cases.${i}.name`, "Give the case a name so a failure can say which one.");
    else if (names.has(c.name.trim())) err(`test_cases.${i}.name`, `Same name as case ${names.get(c.name.trim())! + 1}.`);
    else names.set(c.name.trim(), i);
    if (c.kind !== "user" && !c.expected_output.trim())
      warn(`test_cases.${i}.expected_output`, "Empty expected output — only a program that prints nothing passes.");
  });

  p.hints.forEach((h, i) => {
    if (!h.trim()) err(`hints.${i}`, "An empty hint — write it or remove it.");
  });

  const keys = new Set<string>();
  p.prerequisites.forEach((pr, i) => {
    if (!pr.name.trim()) err(`prerequisites.${i}.name`, "A prerequisite needs a name.");
    const k = pr.key.trim() || slugify(pr.name);
    if (k && keys.has(k)) err(`prerequisites.${i}.key`, `The key “${k}” is used twice.`);
    keys.add(k);
  });

  return out;
}

export const errorsOf = (issues: Issue[]) => issues.filter((i) => i.severity === "error");

/** The first message for a field, for display beside it. */
export function messageFor(issues: Issue[], field: string): Issue | undefined {
  return issues.find((i) => i.field === field && i.severity === "error") ?? issues.find((i) => i.field === field);
}

/** Move an item within a list — the test-case editor's up/down buttons. */
export function moveItem<T>(list: readonly T[], from: number, to: number): T[] {
  if (to < 0 || to >= list.length || from === to) return [...list];
  const next = [...list];
  const [item] = next.splice(from, 1);
  next.splice(to, 0, item!);
  return next;
}
