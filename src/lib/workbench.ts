// Pure helpers for the Projects workbench (src/pages/ProjectWorkbench.tsx).

import type { Project } from "../types";

/** One request from a replayer script, and the reply the server gave it. */
export interface Exchange {
  request: string;
  status: number;
  body: string;
}

/**
 * Pair a replayer's stdout with the request script that produced it.
 *
 * The replayer prints exactly one `<status> <body>` line per non-blank request
 * line, in order. Returns null — and the caller falls back to raw output —
 * unless the output has exactly that shape: a handler that `console.log`s
 * interleaves lines of its own, and pairing those up would put replies next to
 * the wrong requests, which is worse than showing no table at all.
 */
export function pairExchanges(stdin: string, stdout: string): Exchange[] | null {
  const requests = stdin.split("\n").map((l) => l.trim()).filter(Boolean);
  const replies = stdout.replace(/\r/g, "").split("\n").filter((l) => l.trim() !== "");
  if (requests.length === 0 || requests.length !== replies.length) return null;
  const out: Exchange[] = [];
  for (let i = 0; i < replies.length; i++) {
    const m = /^(\d{3})(?: (.*))?$/.exec(replies[i]!);
    if (!m) return null;
    out.push({ request: requests[i]!, status: Number(m[1]), body: m[2] ?? "" });
  }
  return out;
}

/** One-click request lines built from the finished application's contract.
 * A path parameter like `:id` becomes 1, the first id the store hands out. */
export function sampleRequests(project: Pick<Project, "endpoints">): string[] {
  return project.endpoints.map((e) => {
    const path = e.path.replace(/:[A-Za-z]+/g, "1");
    return e.request ? `${e.method} ${path} ${e.request}` : `${e.method} ${path}`;
  });
}
