use serde::Serialize;
use std::time::Duration;

use crate::exec::{self, PrepareError, RunSpec};
use crate::harness;
use crate::models::{FunctionSpec, TestCase};

/// Per-problem judging configuration.
pub struct JudgeConfig {
    /// "exact" | "float" | "unordered" | "checker"
    pub mode: String,
    pub tolerance: f64,
    pub function_spec: Option<FunctionSpec>,
    /// Special-judge script (Python `def check(input, output) -> bool`). Used
    /// when `mode == "checker"` to accept any valid answer, not one exact string.
    pub checker: Option<String>,
    pub timeout: Duration,
}

impl JudgeConfig {
    pub fn exact(timeout: Duration) -> Self {
        JudgeConfig {
            mode: "exact".into(),
            tolerance: 0.0,
            function_spec: None,
            checker: None,
            timeout,
        }
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct CaseResult {
    pub name: String,
    pub kind: String,
    pub input: String,
    pub expected: String,
    pub actual: String,
    pub stderr: String,
    pub passed: bool,
    pub timed_out: bool,
    pub runtime_ms: i64,
    pub memory_kb: Option<i64>,
    /// True if the program's stdout was cut off at the capture cap.
    pub truncated: bool,
    /// "pass" | "wrong" | "tle" | "re" | "trunc"
    pub verdict: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct JudgeReport {
    /// "accepted" | "wrong" | "error" | "not_installed"
    pub status: String,
    pub passed: i64,
    pub total: i64,
    pub runtime_ms: i64,
    /// Peak resident memory across all cases (KiB), when measurable.
    pub memory_kb: Option<i64>,
    pub compile_error: String,
    pub not_installed_hint: String,
    pub results: Vec<CaseResult>,
}

impl JudgeReport {
    fn error(status: &str, msg: String) -> Self {
        JudgeReport {
            status: status.into(),
            passed: 0,
            total: 0,
            runtime_ms: 0,
            memory_kb: None,
            compile_error: if status == "error" { msg.clone() } else { String::new() },
            not_installed_hint: if status == "not_installed" { msg } else { String::new() },
            results: vec![],
        }
    }
}

/// Normalize program output for comparison: strip trailing spaces on each line
/// and drop trailing blank lines. This forgives cosmetic whitespace differences
/// that would otherwise fail an otherwise-correct solution.
fn normalize(s: &str) -> String {
    let cleaned = s.replace('\r', "");
    let mut lines: Vec<&str> = cleaned.split('\n').map(|l| l.trim_end()).collect();
    while lines.last().is_some_and(|l| l.is_empty()) {
        lines.pop();
    }
    lines.join("\n")
}

/// Compare program output to the expected output under the problem's mode.
fn outputs_match(actual: &str, expected: &str, mode: &str, tol: f64) -> bool {
    match mode {
        "float" => floats_match(actual, expected, tol),
        "unordered" => unordered_match(actual, expected),
        _ => normalize(actual) == normalize(expected),
    }
}

/// All whitespace-separated numbers match within an absolute-or-relative tolerance.
fn floats_match(actual: &str, expected: &str, tol: f64) -> bool {
    let a: Vec<&str> = actual.split_whitespace().collect();
    let b: Vec<&str> = expected.split_whitespace().collect();
    if a.len() != b.len() {
        return false;
    }
    let tol = if tol > 0.0 { tol } else { 1e-6 };
    for (x, y) in a.iter().zip(b.iter()) {
        match (x.parse::<f64>(), y.parse::<f64>()) {
            (Ok(fx), Ok(fy)) => {
                let diff = (fx - fy).abs();
                if diff > tol && diff > tol * fy.abs() {
                    return false;
                }
            }
            _ => {
                if x != y {
                    return false;
                }
            }
        }
    }
    true
}

/// Whitespace-separated tokens match as a multiset (order-insensitive).
fn unordered_match(actual: &str, expected: &str) -> bool {
    let mut a: Vec<&str> = actual.split_whitespace().collect();
    let mut b: Vec<&str> = expected.split_whitespace().collect();
    a.sort_unstable();
    b.sort_unstable();
    a == b
}

/// Run a special-judge checker: a Python snippet defining `check(input, output)`
/// that returns True when the program's output is a valid answer for the case.
/// Requires Python; returns Err if it can't run so the case is treated as failed.
fn run_checker(checker_src: &str, input: &str, output: &str, timeout: Duration) -> Result<bool, String> {
    use std::process::{Command, Stdio};

    let dir = std::env::temp_dir().join(format!("poodcode-chk-{}", uuid::Uuid::new_v4()));
    std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let _guard = DirGuard(dir.clone());
    std::fs::write(dir.join("in.txt"), input).map_err(|e| e.to_string())?;
    std::fs::write(dir.join("out.txt"), output).map_err(|e| e.to_string())?;
    let runner = format!(
        "import io\nwith io.open('in.txt', encoding='utf-8') as f: _inp = f.read()\nwith io.open('out.txt', encoding='utf-8') as f: _out = f.read()\n{checker}\nprint('1' if check(_inp, _out) else '0')\n",
        checker = checker_src
    );
    std::fs::write(dir.join("run.py"), &runner).map_err(|e| e.to_string())?;

    let _ = timeout; // checkers are our own trusted, fast scripts
    let out = Command::new("python")
        .arg("run.py")
        .current_dir(&dir)
        .stdin(Stdio::null())
        .output()
        .map_err(|e| e.to_string())?;
    if !out.status.success() {
        return Err(String::from_utf8_lossy(&out.stderr).to_string());
    }
    Ok(String::from_utf8_lossy(&out.stdout).trim() == "1")
}

/// Back-compat entry point: exact match, no harness, given a per-case timeout.
pub fn judge(language: &str, code: &str, cases: &[TestCase], timeout: Duration) -> JudgeReport {
    judge_with(language, code, cases, &JudgeConfig::exact(timeout))
}

/// Compile once, then run every case under the given `JudgeConfig` (harness
/// wrapping, comparison mode, per-case timeout).
pub fn judge_with(
    language: &str,
    code: &str,
    cases: &[TestCase],
    cfg: &JudgeConfig,
) -> JudgeReport {
    let timeout = cfg.timeout;

    // If this is a function-harness problem, wrap the user's function with
    // generated I/O glue before compiling.
    let effective_code: String = match &cfg.function_spec {
        Some(fs) => match harness::wrap(language, code, fs) {
            Ok(wrapped) => wrapped,
            Err(msg) => return JudgeReport::error("error", msg),
        },
        None => code.to_string(),
    };
    let code = effective_code.as_str();

    // Isolated working directory per run.
    let dir = std::env::temp_dir().join(format!("poodcode-{}", uuid::Uuid::new_v4()));
    if let Err(e) = std::fs::create_dir_all(&dir) {
        return JudgeReport::error("error", format!("could not create work dir: {e}"));
    }
    let _guard = DirGuard(dir.clone());

    let spec: RunSpec = match exec::prepare(language, code, &dir) {
        Ok(s) => s,
        Err(PrepareError::NotInstalled { hint }) => {
            return JudgeReport::error("not_installed", hint)
        }
        Err(PrepareError::Compile { message }) => {
            return JudgeReport::error("error", message)
        }
        Err(PrepareError::Unknown(id)) => {
            return JudgeReport::error("error", format!("unknown language: {id}"))
        }
        Err(PrepareError::Io(e)) => return JudgeReport::error("error", e),
    };

    if cases.is_empty() {
        return JudgeReport::error("error", "no test cases to run".into());
    }

    let mut results = Vec::with_capacity(cases.len());
    let mut passed = 0i64;
    let mut total_ms = 0i64;
    let mut peak_mem: Option<i64> = None;
    let mut had_runtime_error = false;

    for tc in cases {
        match exec::run_once(&spec, &tc.input, timeout) {
            Ok(out) => {
                total_ms += out.runtime_ms;
                peak_mem = max_opt(peak_mem, out.memory_kb);
                let actual = out.stdout.clone();
                let runnable = !out.timed_out && !out.truncated && out.exit_code == Some(0);
                let matched = if cfg.mode == "checker" {
                    match (&cfg.checker, runnable) {
                        (Some(src), true) => {
                            run_checker(src, &tc.input, &actual, cfg.timeout).unwrap_or(false)
                        }
                        _ => false,
                    }
                } else {
                    outputs_match(&actual, &tc.expected_output, &cfg.mode, cfg.tolerance)
                };
                // A truncated stdout can never be judged as correct.
                let ok = runnable && matched;
                if ok {
                    passed += 1;
                }
                if out.exit_code != Some(0) || out.timed_out {
                    had_runtime_error = true;
                }
                // Fine-grained per-case verdict.
                let verdict = if ok {
                    "pass"
                } else if out.timed_out {
                    "tle"
                } else if out.truncated {
                    "trunc"
                } else if out.exit_code != Some(0) {
                    "re"
                } else {
                    "wrong"
                };
                let mut stderr = out.stderr;
                if out.truncated {
                    if !stderr.is_empty() {
                        stderr.push('\n');
                    }
                    stderr.push_str("[output truncated — exceeded 1 MiB limit]");
                }
                results.push(CaseResult {
                    name: if tc.name.is_empty() {
                        format!("Case {}", results.len() + 1)
                    } else {
                        tc.name.clone()
                    },
                    kind: tc.kind.clone(),
                    input: tc.input.clone(),
                    expected: tc.expected_output.clone(),
                    actual,
                    stderr,
                    passed: ok,
                    timed_out: out.timed_out,
                    runtime_ms: out.runtime_ms,
                    memory_kb: out.memory_kb,
                    truncated: out.truncated,
                    verdict: verdict.to_string(),
                });
            }
            Err(e) => {
                had_runtime_error = true;
                results.push(CaseResult {
                    name: format!("Case {}", results.len() + 1),
                    kind: tc.kind.clone(),
                    input: tc.input.clone(),
                    expected: tc.expected_output.clone(),
                    actual: String::new(),
                    stderr: e,
                    passed: false,
                    timed_out: false,
                    runtime_ms: 0,
                    memory_kb: None,
                    truncated: false,
                    verdict: "re".to_string(),
                });
            }
        }
    }

    let total = cases.len() as i64;
    let any_tle = results.iter().any(|r| r.timed_out);
    let status = if passed == total {
        "accepted"
    } else if any_tle {
        "tle"
    } else if had_runtime_error {
        "error"
    } else {
        "wrong"
    };

    JudgeReport {
        status: status.into(),
        passed,
        total,
        runtime_ms: total_ms,
        memory_kb: peak_mem,
        compile_error: String::new(),
        not_installed_hint: String::new(),
        results,
    }
}

/// Larger of two optional measurements (ignoring `None`).
fn max_opt(a: Option<i64>, b: Option<i64>) -> Option<i64> {
    match (a, b) {
        (Some(x), Some(y)) => Some(x.max(y)),
        (Some(x), None) => Some(x),
        (None, b) => b,
    }
}

/// Deletes the temp working directory when dropped.
struct DirGuard(std::path::PathBuf);
impl Drop for DirGuard {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}
