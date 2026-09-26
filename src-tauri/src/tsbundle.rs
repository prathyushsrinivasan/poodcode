//! Multi-file TypeScript projects (TS_MASTERY_ROADMAP X-45).
//!
//! A project workspace can hold several files. They travel as ONE string, each
//! file introduced by a marker line:
//!
//! ```text
//! // @file money.ts
//! export function money(c: number): string { … }
//! // @file main.ts
//! import { money } from "./money";
//! …
//! ```
//!
//! The judge runs one file, so the files are *bundled* by concatenation in the
//! order they appear: imports of sibling files (`./…`, `../…`) are dropped,
//! `export` is stripped from declarations, and repeated imports of the same
//! package (`import * as fs from "fs"` in two files) are kept once. Every
//! dropped line becomes a blank line and each marker line a blank line too, so
//! bundled line N is original line N — which is what lets compiler messages be
//! mapped back to `parse.ts(12,5)` instead of an anonymous `main.ts(57,5)`.
//!
//! The rules are line-based and deliberately small; tools/mastery_ts_kit.py
//! mirrors them to compute expected outputs, and tests/verify_mastery.rs judges
//! every multi-file reference through this code, so the two cannot drift.

/// The prefix of a file marker line.
pub const MARKER: &str = "// @file ";

/// Whether `code` is a multi-file workspace.
pub fn is_multi_file(code: &str) -> bool {
    code.lines().any(|l| marker_name(l).is_some())
}

/// `// @file money.ts` → `money.ts`. Spacing around `//` is free; the name is
/// one word.
fn marker_name(line: &str) -> Option<&str> {
    let rest = line.trim().strip_prefix("//")?.trim_start().strip_prefix("@file")?;
    if !rest.starts_with(char::is_whitespace) {
        return None;
    }
    let name = rest.trim();
    (!name.is_empty() && !name.contains(char::is_whitespace)).then_some(name)
}

/// The bundled program, and for every line of it the file and 1-based line it
/// came from.
pub struct Bundle {
    pub source: String,
    pub origin: Vec<(String, usize)>,
}

/// The module specifier a complete import/export statement ends with — the
/// last quoted string (`from "./money"`, or a bare `import "./setup"`). `None`
/// while the statement is still open (its specifier is on a later line).
fn quoted_target(text: &str) -> Option<&str> {
    let t = text.trim_end().trim_end_matches(';').trim_end();
    let quote = t.chars().last()?;
    if quote != '"' && quote != '\'' {
        return None;
    }
    let body = &t[..t.len() - 1];
    let start = body.rfind(quote)?;
    Some(&body[start + 1..])
}

fn is_relative(spec: &str) -> bool {
    spec.starts_with("./") || spec.starts_with("../")
}

const DECL_KEYWORDS: [&str; 12] = [
    "declare", "async", "function", "const", "let", "var", "class", "interface", "type",
    "abstract", "enum", "namespace",
];

/// `export function f` → `function f`; `export default class` → `class`.
fn strip_export(line: &str) -> String {
    let indent_len = line.len() - line.trim_start().len();
    let (indent, body) = line.split_at(indent_len);
    let Some(rest) = body.strip_prefix("export") else { return line.to_string() };
    if !rest.starts_with(char::is_whitespace) {
        return line.to_string();
    }
    let mut rest = rest.trim_start();
    if let Some(r) = rest.strip_prefix("default") {
        if r.starts_with(char::is_whitespace) {
            rest = r.trim_start();
        }
    }
    let first_word: String = rest.chars().take_while(|c| c.is_ascii_alphabetic()).collect();
    if DECL_KEYWORDS.contains(&first_word.as_str()) {
        format!("{indent}{rest}")
    } else {
        line.to_string()
    }
}

/// Bundle a multi-file workspace. `None` when `code` has no file markers.
pub fn bundle(code: &str) -> Option<Bundle> {
    if !is_multi_file(code) {
        return None;
    }
    let lines: Vec<&str> = code.lines().collect();
    let mut out: Vec<String> = Vec::with_capacity(lines.len());
    let mut origin: Vec<(String, usize)> = Vec::with_capacity(lines.len());
    let mut file = String::from("(before the first file)");
    let mut line_in_file = 0usize;
    let mut seen_imports: std::collections::HashSet<String> = std::collections::HashSet::new();

    let mut i = 0;
    while i < lines.len() {
        let line = lines[i];
        if let Some(name) = marker_name(line) {
            file = name.to_string();
            line_in_file = 0;
            out.push(String::new());
            origin.push((file.clone(), 0));
            i += 1;
            continue;
        }
        let trimmed = line.trim_start();
        let is_import = trimmed.starts_with("import ") || trimmed.starts_with("import{");
        let is_export_list = trimmed.starts_with("export {")
            || trimmed.starts_with("export{")
            || trimmed.starts_with("export type {")
            || trimmed.starts_with("export *");
        if is_import || is_export_list {
            // Gather a statement that spans lines: `import {\n a,\n} from "./x";`
            let mut j = i;
            let mut text = line.to_string();
            let complete = |t: &str| quoted_target(t).is_some() || (is_export_list && t.contains('}') && !t.contains("from") && t.trim_end().ends_with([';', '}']));
            while !complete(&text) && j + 1 < lines.len() && marker_name(lines[j + 1]).is_none() {
                j += 1;
                text.push('\n');
                text.push_str(lines[j]);
            }
            let target = quoted_target(&text);
            let drop = if is_export_list {
                true
            } else {
                match target {
                    Some(spec) if is_relative(spec) => true,
                    _ => !seen_imports.insert(text.split_whitespace().collect::<Vec<_>>().join(" ")),
                }
            };
            for kept in &lines[i..=j] {
                line_in_file += 1;
                out.push(if drop { String::new() } else { kept.to_string() });
                origin.push((file.clone(), line_in_file));
            }
            i = j + 1;
            continue;
        }
        line_in_file += 1;
        out.push(strip_export(line));
        origin.push((file.clone(), line_in_file));
        i += 1;
    }
    Some(Bundle { source: out.join("\n") + "\n", origin })
}

/// Rewrite `main.ts(LINE,COL)` locations in a compiler message to the file and
/// line the learner wrote. Lines past the bundle (a hidden harness) are left as
/// they are.
pub fn relabel(message: &str, origin: &[(String, usize)]) -> String {
    const MARK: &str = "main.ts(";
    message
        .lines()
        .map(|raw| {
            let Some(i) = raw.find(MARK) else { return raw.to_string() };
            let rest = &raw[i + MARK.len()..];
            let Some((loc, tail)) = rest.split_once(')') else { return raw.to_string() };
            let Some((line, col)) = loc.split_once(',') else { return raw.to_string() };
            let Ok(n) = line.trim().parse::<usize>() else { return raw.to_string() };
            match origin.get(n.wrapping_sub(1)) {
                Some((file, l)) if n >= 1 => format!("{}{}({},{}){}", &raw[..i], file, l, col, tail),
                _ => raw.to_string(),
            }
        })
        .collect::<Vec<_>>()
        .join("\n")
}

#[cfg(test)]
mod tests {
    use super::*;

    const WS: &str = "// @file money.ts\n\
export type Cents = number;\n\
export function money(c: Cents): string {\n\
  return (c / 100).toFixed(2);\n\
}\n\
// @file main.ts\n\
import * as fs from \"fs\";\n\
import { money, type Cents } from \"./money\";\n\
import {\n\
  money as m2,\n\
} from \"./money\";\n\
const input = fs.readFileSync(0, \"utf8\").trim();\n\
console.log(money(Number(input) as Cents));\n\
export { money };\n";

    #[test]
    fn plain_code_is_not_bundled() {
        assert!(bundle("const x = 1;\nconsole.log(x);\n").is_none());
        assert!(!is_multi_file("// @files are great\n"));
    }

    #[test]
    fn bundles_keeping_line_numbers() {
        let b = bundle(WS).unwrap();
        let lines: Vec<&str> = b.source.lines().collect();
        assert_eq!(lines.len(), WS.lines().count());
        assert_eq!(lines[1], "type Cents = number;");
        assert_eq!(lines[2], "function money(c: Cents): string {");
        assert_eq!(lines[6], "import * as fs from \"fs\";");
        assert_eq!(lines[7], "", "a sibling import is dropped");
        assert_eq!(&lines[8..11], &["", "", ""], "a multi-line sibling import is dropped");
        assert_eq!(lines[13], "", "an export list is dropped");
        assert_eq!(b.origin[7], ("main.ts".to_string(), 2));
        assert_eq!(b.origin[2], ("money.ts".to_string(), 2));
    }

    #[test]
    fn repeated_package_imports_are_kept_once() {
        let ws = "// @file a.ts\nimport * as fs from \"fs\";\n// @file b.ts\nimport * as fs from \"fs\";\n";
        let b = bundle(ws).unwrap();
        assert_eq!(b.source, "\nimport * as fs from \"fs\";\n\n\n");
    }

    #[test]
    fn export_default_and_non_declarations() {
        assert_eq!(strip_export("export default function f() {}"), "function f() {}");
        assert_eq!(strip_export("  export const x = 1;"), "  const x = 1;");
        assert_eq!(strip_export("export declare const b: unique symbol;"), "declare const b: unique symbol;");
        assert_eq!(strip_export("exported = 1;"), "exported = 1;");
    }

    #[test]
    fn relabels_compiler_locations() {
        let b = bundle(WS).unwrap();
        let msg = "main.ts(3,10): error TS2322: nope\nmain.ts(13,1): error TS2345: no\nsummary";
        let out = relabel(msg, &b.origin);
        assert_eq!(out, "money.ts(2,10): error TS2322: nope\nmain.ts(7,1): error TS2345: no\nsummary");
    }
}
