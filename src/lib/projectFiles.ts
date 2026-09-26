// Multi-file project workspaces (TS_MASTERY_ROADMAP X-45). A workspace is
// stored and judged as ONE string, each file introduced by a marker line
// `// @file name.ts`; the judge bundles it (src-tauri/src/tsbundle.rs). This
// module splits that string into editable files and joins them back — the UI
// never has to know about the markers.

export type WorkspaceFile = { name: string; content: string };

const MARKER = /^\s*\/\/\s*@file\s+(\S+)\s*$/;

/** Whether `code` holds several files. */
export function isMultiFile(code: string): boolean {
  return code.split("\n").some((l) => MARKER.test(l));
}

/** The files in `code`, in order; null for an ordinary single-file program.
 * Text before the first marker (normally none) becomes a file of its own. */
export function splitFiles(code: string): WorkspaceFile[] | null {
  if (!isMultiFile(code)) return null;
  const files: WorkspaceFile[] = [];
  let name: string | null = null;
  let buf: string[] = [];
  const flush = () => {
    const content = buf.join("\n").replace(/\s+$/, "");
    if (name !== null) files.push({ name, content });
    else if (content.trim() !== "") files.push({ name: "untitled.ts", content });
    buf = [];
  };
  for (const line of code.split("\n")) {
    const m = MARKER.exec(line);
    if (m) {
      flush();
      name = m[1] ?? "untitled.ts";
    } else {
      buf.push(line);
    }
  }
  flush();
  return files;
}

/** The inverse of `splitFiles`: `splitFiles(joinFiles(fs))` equals `fs` for
 * files without trailing whitespace. */
export function joinFiles(files: WorkspaceFile[]): string {
  return files.map((f) => `// @file ${f.name}\n${f.content.replace(/\s+$/, "")}`).join("\n\n") + "\n";
}

/** A file name the workspace accepts: one word ending in `.ts`, not taken. */
export function fileNameProblem(name: string, taken: string[]): string | null {
  if (!/^[A-Za-z0-9_.-]+\.ts$/.test(name)) return "Use one word ending in .ts, like utils.ts";
  if (taken.includes(name)) return `${name} already exists`;
  return null;
}

/** Turn a single-file program into a workspace whose only file is main.ts. */
export function toWorkspace(code: string): WorkspaceFile[] {
  return splitFiles(code) ?? [{ name: "main.ts", content: code.replace(/\s+$/, "") }];
}
