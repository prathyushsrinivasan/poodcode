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
//
// The Projects track (tools/projects_track.py) added the second group below:
// `node:http`, `URL` and `fetch`, which are what a judged HTTP server and the
// request replayer that drives it need. Same rule applies — each member is
// declared because a shipped program uses it, not because Node has it.

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

// ---------------------------------------------------------------------------
// HTTP — used by the Projects track, whose programs boot a real server on port
// 0 and replay a request script through `fetch`.
// ---------------------------------------------------------------------------

declare module "http" {
  /** Header names arrive lower-cased. Every value the track reads is a string
   *  or absent, so the index signature is deliberately not widened to
   *  `string[]` (which only `set-cookie` would need). */
  export interface IncomingHttpHeaders {
    [name: string]: string | undefined;
  }

  export interface IncomingMessage {
    /** Absent only on a malformed request; the track always narrows it. */
    readonly method?: string;
    /** Path plus query string — NOT an absolute URL, which is why every
     *  handler builds a `new URL(req.url ?? "/", "http://localhost")`. */
    readonly url?: string;
    readonly headers: IncomingHttpHeaders;
    /** Chunks are `Buffer` until this is called. The track calls it before
     *  reading any body, which is what makes the `string` chunk below true. */
    setEncoding(encoding: "utf8" | "utf-8"): this;
    on(event: "data", listener: (chunk: string) => void): this;
    on(event: "end", listener: () => void): this;
    on(event: "error", listener: (err: Error) => void): this;
  }

  export interface ServerResponse {
    statusCode: number;
    /** True once a status line has gone out — the guard an error boundary
     *  needs before it tries to write a 500 over an already-sent response. */
    readonly headersSent: boolean;
    setHeader(name: string, value: string): this;
    writeHead(status: number, headers?: Record<string, string>): this;
    end(data?: string): this;
  }

  export interface AddressInfo {
    address: string;
    family: string;
    port: number;
  }

  export interface Server {
    listen(port: number, host: string, callback: () => void): this;
    /** `null` before `listen` resolves; an object once bound. Port 0 means
     *  "any free port", so reading `.port` back is how the driver finds it. */
    address(): AddressInfo | null;
    close(callback?: () => void): this;
  }

  export type RequestListener = (
    req: IncomingMessage,
    res: ServerResponse
  ) => void | Promise<void>;

  export function createServer(listener: RequestListener): Server;
}

// The track imports named, never default — `import { createServer, type
// IncomingMessage } from "node:http"`. A default import would make
// `http.IncomingMessage` a namespace reference, which this file cannot satisfy
// without declaring one; named type imports are the better lesson anyway.
declare module "node:http" {
  export * from "http";
}

/** WHATWG URL. Declared here rather than pulled from `lib.dom` because the
 *  generated tsconfig ships no DOM lib — see the header. */
declare class URL {
  constructor(input: string, base?: string);
  readonly pathname: string;
  readonly search: string;
  readonly searchParams: URLSearchParams;
  readonly href: string;
}

declare class URLSearchParams {
  constructor(init?: string);
  get(name: string): string | null;
  getAll(name: string): string[];
  has(name: string): boolean;
  set(name: string, value: string): void;
  forEach(callback: (value: string, key: string) => void): void;
  entries(): IterableIterator<[string, string]>;
  keys(): IterableIterator<string>;
  [Symbol.iterator](): IterableIterator<[string, string]>;
}

interface FetchResponse {
  readonly status: number;
  readonly ok: boolean;
  text(): Promise<string>;
  /** `unknown`, not `any` — a response body is untrusted data, and making the
   *  learner narrow it is the same lesson the course's `JSON.parse` week
   *  teaches. */
  json(): Promise<unknown>;
}

interface FetchInit {
  method?: string;
  headers?: Record<string, string>;
  body?: string;
}

declare function fetch(input: string, init?: FetchInit): Promise<FetchResponse>;
