// Ambient declarations for judged TypeScript programs.
//
// Every judged program in the app is a single file that reads stdin and prints
// to stdout. A survey of all 1,476 of them (course + Learn + Mastery, solutions
// and starters) found exactly one import — `fs` — and exactly one member of it,
// `readFileSync`; no `require`, no `process`, no `Buffer`, no `__dirname`. The
// only other host globals used are `console` and `setTimeout`.
//
// So instead of bundling `@types/node` (2.6 MB, plus its own transitive type
// dependencies) into the desktop app, the type-checker ships these declarations.
// They are deliberately NARROW: an exercise that reaches for a Node API the
// course never teaches gets a clear "Cannot find name" rather than silently
// type-checking against an API the judge would then have to support.
//
// `lib` in the generated tsconfig is ES2022 only — no DOM — which is why
// `console` and `setTimeout` have to be declared here at all.

declare module "fs" {
  /** The form every program uses: `readFileSync(0, "utf8")` — fd 0 is stdin. */
  export function readFileSync(
    target: number | string,
    encoding: "utf8" | "utf-8"
  ): string;
  export function readFileSync(
    target: number | string,
    options: { encoding: "utf8" | "utf-8"; flag?: string }
  ): string;
  export function writeFileSync(
    target: number | string,
    data: string,
    encoding?: "utf8" | "utf-8"
  ): void;
}

declare module "node:fs" {
  export * from "fs";
}

interface Console {
  log(...data: unknown[]): void;
  error(...data: unknown[]): void;
  warn(...data: unknown[]): void;
  info(...data: unknown[]): void;
  debug(...data: unknown[]): void;
}
declare var console: Console;

declare function setTimeout(handler: () => void, ms?: number): number;
declare function clearTimeout(handle: number): void;
declare function queueMicrotask(callback: () => void): void;
