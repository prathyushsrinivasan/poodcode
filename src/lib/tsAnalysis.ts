// Pure helpers behind the TypeScript playground (pages/TsPlayground.tsx). The
// page asks Monaco's TypeScript worker the questions; these decide which
// positions to ask about, so they can be tested without a worker.

/** Mask string, template and comment contents with spaces (same length), so a
 * search for an identifier only finds code. Template `${…}` holes stay code. */
export function maskNonCode(src: string): string {
  const out = src.split("");
  let i = 0;
  const blank = (from: number, to: number) => {
    for (let k = from; k < to && k < out.length; k++) if (out[k] !== "\n") out[k] = " ";
  };
  // A stack of open template literals, each with the brace depth of its holes.
  const templates: number[] = [];
  let braceDepth = 0;
  while (i < src.length) {
    const c = src[i]!;
    const next = src[i + 1];
    const inTemplateText = templates.length > 0 && templates[templates.length - 1] === braceDepth && c !== "`";
    if (templates.length > 0 && templates[templates.length - 1] === braceDepth) {
      // Inside template text.
      if (c === "\\") {
        blank(i, i + 2);
        i += 2;
        continue;
      }
      if (c === "`") {
        templates.pop();
        i++;
        continue;
      }
      if (c === "$" && next === "{") {
        braceDepth++;
        i += 2;
        continue;
      }
      if (inTemplateText) blank(i, i + 1);
      i++;
      continue;
    }
    if (c === "/" && next === "/") {
      const end = src.indexOf("\n", i);
      const stop = end < 0 ? src.length : end;
      blank(i, stop);
      i = stop;
      continue;
    }
    if (c === "/" && next === "*") {
      const end = src.indexOf("*/", i + 2);
      const stop = end < 0 ? src.length : end + 2;
      blank(i, stop);
      i = stop;
      continue;
    }
    if (c === '"' || c === "'") {
      let j = i + 1;
      while (j < src.length && src[j] !== c && src[j] !== "\n") j += src[j] === "\\" ? 2 : 1;
      blank(i + 1, j);
      i = j + 1;
      continue;
    }
    if (c === "`") {
      templates.push(braceDepth);
      i++;
      continue;
    }
    if (c === "{") braceDepth++;
    if (c === "}") braceDepth = Math.max(0, braceDepth - 1);
    i++;
  }
  return out.join("");
}

/** Offsets of every code occurrence of the identifier `name`. */
export function occurrences(src: string, name: string): number[] {
  if (!/^[A-Za-z_$][\w$]*$/.test(name)) return [];
  const code = maskNonCode(src);
  const re = new RegExp(`(?<![\\w$.])${name.replace(/\$/g, "\\$")}(?![\\w$])`, "g");
  const hits: number[] = [];
  for (let m = re.exec(code); m; m = re.exec(code)) hits.push(m.index);
  return hits;
}

/** 1-based line number of an offset. */
export function lineOf(src: string, offset: number): number {
  let line = 1;
  for (let i = 0; i < offset && i < src.length; i++) if (src[i] === "\n") line++;
  return line;
}

/** Top-level type aliases and interfaces declared without type parameters —
 * the ones that can be shown fully expanded. */
export function expandableTypes(src: string): string[] {
  const code = maskNonCode(src);
  const names: string[] = [];
  const re = /^(?:export\s+)?(?:type|interface)\s+([A-Za-z_$][\w$]*)\s*(<)?/gm;
  for (let m = re.exec(code); m; m = re.exec(code)) {
    if (!m[2] && m[1] && !names.includes(m[1])) names.push(m[1]);
  }
  return names;
}

export const EXPAND_HELPER =
  "type __PgExpand<T> = T extends (...args: never[]) => unknown ? T : T extends object ? { [K in keyof T]: T[K] } : T;";

/** The source with one probe per type appended: `declare const __pg_0:
 * __PgExpand<Name>;`. Hovering a probe shows the type resolved and expanded.
 * Returns the text and the offset of each probe's name. */
export function probeSource(src: string, names: string[]): { text: string; offsets: number[] } {
  let text = src.replace(/\s*$/, "") + "\n\n" + EXPAND_HELPER + "\n";
  const offsets: number[] = [];
  names.forEach((n, i) => {
    const decl = `declare const __pg_${i}: __PgExpand<${n}>;\n`;
    offsets.push(text.length + "declare const ".length);
    text += decl;
  });
  return { text, offsets };
}

/** `const __pg_0: { a: number; }` → `{ a: number; }` — the part after the
 * probe's name in a quick-info string. */
export function probeType(display: string): string {
  const idx = display.indexOf(":");
  return idx < 0 ? display : display.slice(idx + 1).trim();
}
