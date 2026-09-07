//! TypeScript type-checking gate.
//!
//! Node runs `.ts` by *stripping* type annotations — it never checks them. So
//! without this module `let n: number = "seven"` runs happily, and every
//! annotation in the TypeScript course is decoration. This is the missing half
//! of `exec::prepare` for TypeScript: the equivalent of the `javac` step that
//! Java exercises already go through before they are allowed to run.
//!
//! **Delivery.** The compiler is `typescript/lib/tsc.js` — one Node script plus
//! the `lib.*.d.ts` files it reads. A shipped desktop build has no
//! `node_modules`, so those files are bundled as a Tauri resource (`tslib/`);
//! in a dev tree they are resolved out of `node_modules` instead. If neither
//! resolves the check is SKIPPED rather than failing every TypeScript run — a
//! packaged build always has the resource, so this only degrades in a broken
//! dev tree, and `tools/verify_ts_course.py` treats a missing compiler as a
//! hard error so content is never silently unverified.
//!
//! **No `@types/node`.** A survey of all 1,476 judged programs found exactly one
//! import (`fs`) and one member of it (`readFileSync`). `tslib/poodcode-env.d.ts`
//! declares that much by hand, which keeps 2.6 MB of `@types/node` — and its own
//! transitive type dependencies — out of the bundle. `types` and `typeRoots` are
//! pinned empty so a dev tree's `node_modules/@types` cannot drift the results.

use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::OnceLock;

/// How strict the check is. Presets rather than free-form flags so the content
/// generator and the judge cannot disagree about what a level means.
///
/// - `strict` — `--strict`. The baseline for every judged TypeScript program.
/// - `strict+indexed` — adds `noUncheckedIndexedAccess`, which types `a[i]` as
///   `T | undefined`. The TypeScript course turns this on from week 6, where
///   arrays are taught; weeks 1–5 stay on `strict` because they have not met
///   the guard, the `??` or the `!` needed to satisfy it.
pub const STRICT: &str = "strict";
pub const STRICT_INDEXED: &str = "strict+indexed";

/// Resolved location of the compiler and the ambient declarations.
struct TsTools {
    /// `node <tsc_js>` runs the compiler.
    tsc_js: Option<PathBuf>,
    /// `tsc` (or similar) already on PATH, used only if `tsc_js` is absent.
    tsc_bin: Option<String>,
    /// Our hand-written stand-in for `@types/node`.
    env_dts: PathBuf,
}

fn tools() -> Option<&'static TsTools> {
    static TOOLS: OnceLock<Option<TsTools>> = OnceLock::new();
    TOOLS.get_or_init(resolve_tools).as_ref()
}

/// Directories that may hold the bundled `tslib/`, most specific first.
fn candidate_roots() -> Vec<PathBuf> {
    let mut roots = Vec::new();
    if let Ok(dir) = std::env::var("POODCODE_TSLIB") {
        roots.push(PathBuf::from(dir));
    }
    if let Ok(exe) = std::env::current_exe() {
        if let Some(d) = exe.parent() {
            roots.push(d.join("tslib"));
            // macOS app bundle: Contents/MacOS/<exe> -> Contents/Resources/tslib
            roots.push(d.join("../Resources/tslib"));
        }
    }
    roots
}

/// Walk up from `start` looking for `rel`, at most `depth` levels.
fn find_upwards(start: &Path, rel: &str, depth: usize) -> Option<PathBuf> {
    let mut cur = start;
    for _ in 0..depth {
        let candidate = cur.join(rel);
        if candidate.exists() {
            return Some(candidate);
        }
        cur = cur.parent()?;
    }
    None
}

fn resolve_tools() -> Option<TsTools> {
    // The ambient declarations: bundled beside the compiler, else in the source
    // tree (dev). Without them `import * as fs from "fs"` cannot resolve, so a
    // missing env.d.ts means we cannot check at all.
    let mut env_dts = candidate_roots()
        .into_iter()
        .map(|r| r.join("poodcode-env.d.ts"))
        .find(|p| p.exists());
    if env_dts.is_none() {
        let here = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        env_dts = find_upwards(&here, "tslib/poodcode-env.d.ts", 4)
            .or_else(|| find_upwards(&here, "src-tauri/tslib/poodcode-env.d.ts", 4));
    }
    let env_dts = env_dts?;

    // The compiler: bundled tsc.js, else the dev tree's node_modules, else a
    // `tsc` already on PATH.
    let mut tsc_js = candidate_roots()
        .into_iter()
        .map(|r| r.join("tsc.js"))
        .find(|p| p.exists());
    if tsc_js.is_none() {
        let here = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        tsc_js = find_upwards(&here, "node_modules/typescript/lib/tsc.js", 4);
    }
    let tsc_bin = if tsc_js.is_none() && binary_runs("tsc") {
        Some("tsc".to_string())
    } else {
        None
    };
    if tsc_js.is_none() && tsc_bin.is_none() {
        return None;
    }
    Some(TsTools { tsc_js, tsc_bin, env_dts })
}

fn binary_runs(program: &str) -> bool {
    Command::new(program)
        .arg("--version")
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
}

/// The tsconfig written beside the learner's program.
///
/// `module: esnext` + `moduleResolution: bundler` is deliberate: a single `.ts`
/// file in a directory with no `package.json` is CommonJS under `nodenext`, and
/// tsc then rejects top-level `await` (TS1309) in programs that Node itself runs
/// perfectly well, because Node auto-detects ESM syntax and reparses. Measured
/// across all 761 reference solutions, `nodenext` reported 7 failures and this
/// setting reports the 2 that are genuine content bugs. Renaming the file to
/// `.mts` scores the same but would flip every program in the app from CommonJS
/// to ESM *at runtime*, which this does not.
fn tsconfig_json(preset: &str, env_dts: &Path, file: &str) -> String {
    let indexed = preset == STRICT_INDEXED;
    // JSON-escape the path: Windows separators would otherwise be escapes.
    let env = env_dts.to_string_lossy().replace('\\', "\\\\");
    format!(
        r#"{{
  "compilerOptions": {{
    "target": "es2022",
    "lib": ["es2022"],
    "module": "esnext",
    "moduleResolution": "bundler",
    "moduleDetection": "force",
    "strict": true,
    "noUncheckedIndexedAccess": {indexed},
    "noEmit": true,
    "skipLibCheck": true,
    "pretty": false,
    "types": [],
    "typeRoots": []
  }},
  "files": ["{env}", "{file}"]
}}"#
    )
}

/// Type-check `file` (already written in `dir`) at the given strictness preset.
///
/// `Ok(())` means it compiles — or that no compiler could be resolved, which is
/// reported by [`available`] rather than by failing the run. `Err` carries the
/// compiler's diagnostics, ready to show the learner.
pub fn check(dir: &Path, file: &str, preset: &str) -> Result<(), String> {
    let Some(t) = tools() else { return Ok(()) };

    let cfg_path = dir.join("tsconfig.json");
    let cfg = tsconfig_json(preset, &t.env_dts, file);
    if std::fs::write(&cfg_path, cfg).is_err() {
        return Ok(()); // cannot check; never block the run on our own plumbing
    }

    let out = match (&t.tsc_js, &t.tsc_bin) {
        (Some(js), _) => Command::new("node")
            .arg(js)
            .args(["-p", "tsconfig.json"])
            .current_dir(dir)
            .stdin(Stdio::null())
            .output(),
        (None, Some(bin)) => Command::new(bin)
            .args(["-p", "tsconfig.json"])
            .current_dir(dir)
            .stdin(Stdio::null())
            .output(),
        (None, None) => return Ok(()),
    };

    let out = match out {
        Ok(o) => o,
        Err(_) => return Ok(()),
    };
    if out.status.success() {
        return Ok(());
    }
    let mut msg = String::from_utf8_lossy(&out.stdout).to_string();
    if msg.trim().is_empty() {
        msg = String::from_utf8_lossy(&out.stderr).to_string();
    }
    if msg.trim().is_empty() {
        // Non-zero with no diagnostics is our problem, not the learner's.
        return Ok(());
    }
    Err(msg.trim().to_string())
}

/// Whether a type-checker resolved. Used by tests and the verifier to refuse to
/// "pass" a run that silently skipped the check.
pub fn available() -> bool {
    tools().is_some()
}

/// Rewrite diagnostics that point past the end of the learner's own code.
///
/// An exercise's hidden harness is appended to the learner's program and the two
/// compile as one file, so tsc numbers their lines continuously. Reporting
/// `main.ts(47,3)` for a twelve-line program sends the learner hunting for a
/// line that does not exist in what they can see.
///
/// Lines at or before `user_lines` are theirs and pass through untouched.
/// Anything after is re-anchored to `checks.ts` at a harness-relative line, and
/// `note` is prepended once to say what a failure there actually means.
pub fn relabel_harness_diagnostics(msg: &str, user_lines: usize, note: &str) -> String {
    const MARK: &str = "main.ts(";
    let mut touched = false;
    let mut out: Vec<String> = Vec::with_capacity(msg.lines().count());

    for raw in msg.lines() {
        // `pretty: false` gives one diagnostic per line, as
        // `main.ts(LINE,COL): error TSxxxx: message`. Anything that does not
        // parse that way (a summary line, a global error) is passed through.
        let parsed = raw.find(MARK).and_then(|i| {
            let (loc, tail) = raw[i + MARK.len()..].split_once(')')?;
            let (line, col) = loc.split_once(',')?;
            Some((line.trim().parse::<usize>().ok()?, col.to_string(), tail.to_string()))
        });
        match parsed {
            Some((line, col, tail)) if line > user_lines => {
                touched = true;
                out.push(format!("checks.ts({},{}){}", line - user_lines, col, tail));
            }
            _ => out.push(raw.to_string()),
        }
    }

    let body = out.join("\n");
    if touched && !note.is_empty() {
        format!("{note}\n\n{body}")
    } else {
        body
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn scratch() -> PathBuf {
        let d = std::env::temp_dir().join(format!("poodcode-tsck-{}", uuid::Uuid::new_v4()));
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    fn check_src(src: &str, preset: &str) -> Result<(), String> {
        let d = scratch();
        std::fs::write(d.join("main.ts"), src).unwrap();
        let r = check(&d, "main.ts", preset);
        let _ = std::fs::remove_dir_all(&d);
        r
    }

    #[test]
    fn accepts_a_correct_program() {
        if !available() {
            eprintln!("no TypeScript compiler resolved — skipping");
            return;
        }
        let src = "const n: number = 7;\nconsole.log(n * 2);\n";
        assert!(check_src(src, STRICT).is_ok());
    }

    #[test]
    fn rejects_a_type_error() {
        if !available() {
            eprintln!("no TypeScript compiler resolved — skipping");
            return;
        }
        // The exact program that passes today and must not after this change.
        let err = check_src("let n: number = \"seven\";\nconsole.log(n);\n", STRICT)
            .expect_err("a string assigned to a number must be rejected");
        assert!(err.contains("TS2322"), "expected TS2322, got: {err}");
    }

    #[test]
    fn resolves_the_fs_import_without_types_node() {
        if !available() {
            eprintln!("no TypeScript compiler resolved — skipping");
            return;
        }
        let src = "import * as fs from \"fs\";\n\
                   const line = fs.readFileSync(0, \"utf8\").trim();\n\
                   console.log(line.length);\n";
        assert!(check_src(src, STRICT).is_ok(), "the stdin idiom must type-check");
    }

    #[test]
    fn relabel_leaves_the_learners_own_diagnostics_alone() {
        let msg = "main.ts(3,7): error TS2322: Type 'string' is not assignable to type 'number'.";
        let out = relabel_harness_diagnostics(msg, 10, "note");
        assert_eq!(out, msg, "a line inside the learner's code must not be rewritten");
    }

    #[test]
    fn relabel_reanchors_diagnostics_from_the_harness() {
        // The learner's program is 4 lines; line 6 is the harness's line 2.
        let msg = "main.ts(6,15): error TS2554: Expected 2 arguments, but got 1.";
        let out = relabel_harness_diagnostics(msg, 4, "SIGNATURE");
        assert!(out.starts_with("SIGNATURE\n\n"), "the note explains what a failure here means: {out}");
        assert!(
            out.contains("checks.ts(2,15): error TS2554: Expected 2 arguments, but got 1."),
            "line must be re-anchored to the harness: {out}"
        );
        assert!(!out.contains("main.ts"), "the combined file is an implementation detail: {out}");
    }

    #[test]
    fn relabel_passes_through_lines_it_cannot_parse() {
        let msg = "error TS18003: No inputs were found in config file.";
        assert_eq!(relabel_harness_diagnostics(msg, 4, "note"), msg);
    }

    #[test]
    fn relabel_adds_no_note_when_nothing_moved() {
        let msg = "main.ts(2,1): error TS2304: Cannot find name 'foo'.";
        let out = relabel_harness_diagnostics(msg, 9, "SHOULD NOT APPEAR");
        assert!(!out.contains("SHOULD NOT APPEAR"), "{out}");
    }

    #[test]
    fn indexed_preset_is_stricter_than_strict() {
        if !available() {
            eprintln!("no TypeScript compiler resolved — skipping");
            return;
        }
        // `a[0]` is `number` under strict and `number | undefined` under
        // noUncheckedIndexedAccess. This is the proof the two presets differ.
        let src = "const a: number[] = [1, 2, 3];\n\
                   const first: number = a[0];\n\
                   console.log(first);\n";
        assert!(check_src(src, STRICT).is_ok(), "must pass on the plain strict preset");
        assert!(
            check_src(src, STRICT_INDEXED).is_err(),
            "must fail once noUncheckedIndexedAccess is on"
        );
    }
}
