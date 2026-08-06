//! Pluggable code-execution engine.
//!
//! Model: the user's program communicates over **stdin/stdout**. A test case is
//! an `input` (fed to stdin) and an `expected_output` (compared against stdout,
//! trimmed line-by-line). This keeps judging fully language-agnostic and makes
//! adding a new language a matter of describing how to compile/run it.
//!
//! Languages whose toolchain is not installed are still listed (so the UI can
//! show them) but `installed = false` with an install hint; execution returns a
//! structured `NotInstalled` preparation error.

use serde::Serialize;
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::OnceLock;
use std::thread;
use std::time::{Duration, Instant};
use wait_timeout::ChildExt;

#[derive(Debug, Clone, Serialize)]
pub struct LangInfo {
    pub id: String,
    pub label: String,
    pub monaco: String,
    pub installed: bool,
    pub install_hint: String,
}

/// Every language the app understands. `installed` is resolved at runtime.
pub fn languages() -> Vec<LangInfo> {
    LANGS
        .iter()
        .map(|l| LangInfo {
            id: l.id.into(),
            label: l.label.into(),
            monaco: l.monaco.into(),
            installed: l.installed(),
            install_hint: l.install_hint.into(),
        })
        .collect()
}

struct LangSpec {
    id: &'static str,
    label: &'static str,
    monaco: &'static str,
    /// Programs that must all be present for the language to be runnable.
    tools: &'static [&'static str],
    install_hint: &'static str,
}

impl LangSpec {
    fn installed(&self) -> bool {
        self.tools.iter().all(|t| tool_available(t))
    }
}

// Java is listed first — Poodcode is Java-centered by default.
const LANGS: &[LangSpec] = &[
    LangSpec { id: "java", label: "Java", monaco: "java", tools: &["javac", "java"], install_hint: "Install a JDK (`javac` and `java` on PATH)." },
    LangSpec { id: "python", label: "Python", monaco: "python", tools: &["python"], install_hint: "Install Python 3 and ensure `python` is on PATH." },
    LangSpec { id: "cpp", label: "C++", monaco: "cpp", tools: &["g++"], install_hint: "Install a C++ compiler (`g++` on PATH), e.g. MSYS2/MinGW or WSL." },
    LangSpec { id: "javascript", label: "JavaScript", monaco: "javascript", tools: &["node"], install_hint: "Install Node.js (`node` on PATH)." },
    LangSpec { id: "typescript", label: "TypeScript", monaco: "typescript", tools: &["node"], install_hint: "Install Node.js 22+ (runs .ts via type-stripping)." },
    LangSpec { id: "go", label: "Go", monaco: "go", tools: &["go"], install_hint: "Install Go (`go` on PATH)." },
    LangSpec { id: "rust", label: "Rust", monaco: "rust", tools: &["rustc"], install_hint: "Install Rust (`rustc` on PATH)." },
    LangSpec { id: "csharp", label: "C#", monaco: "csharp", tools: &["dotnet"], install_hint: "Install the .NET SDK (`dotnet` on PATH)." },
    LangSpec { id: "kotlin", label: "Kotlin", monaco: "kotlin", tools: &["kotlinc"], install_hint: "Install Kotlin (`kotlinc` on PATH)." },
];

fn lang(id: &str) -> Option<&'static LangSpec> {
    LANGS.iter().find(|l| l.id == id)
}

/// Cache of tool-availability probes so we don't spawn a process every call.
fn availability_cache() -> &'static std::sync::Mutex<std::collections::HashMap<String, bool>> {
    static CACHE: OnceLock<std::sync::Mutex<std::collections::HashMap<String, bool>>> =
        OnceLock::new();
    CACHE.get_or_init(|| std::sync::Mutex::new(std::collections::HashMap::new()))
}

fn tool_available(program: &str) -> bool {
    if let Ok(cache) = availability_cache().lock() {
        if let Some(v) = cache.get(program) {
            return *v;
        }
    }
    let arg = if program == "java" { "-version" } else { "--version" };
    let ok = Command::new(program)
        .arg(arg)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .map(|s| s.success())
        .unwrap_or(false);
    if let Ok(mut cache) = availability_cache().lock() {
        cache.insert(program.to_string(), ok);
    }
    ok
}

#[derive(Debug)]
pub enum PrepareError {
    NotInstalled { hint: String },
    Unknown(String),
    Compile { message: String },
    Io(String),
}

/// How to run a prepared program.
pub struct RunSpec {
    program: String,
    args: Vec<String>,
    cwd: PathBuf,
}

/// Maximum bytes captured from a program's stdout / stderr. A runaway program
/// that prints forever will fill a pipe and block once we stop reading, then be
/// killed by the wall-clock timeout — this cap keeps our own memory bounded.
pub const MAX_STDOUT_BYTES: usize = 1 << 20; // 1 MiB
pub const MAX_STDERR_BYTES: usize = 256 * 1024; // 256 KiB

/// Output of running a program once against a single input.
#[derive(Debug, Clone, Serialize)]
pub struct ProcOut {
    pub stdout: String,
    pub stderr: String,
    pub exit_code: Option<i32>,
    pub timed_out: bool,
    pub runtime_ms: i64,
    /// Peak resident memory in KiB, when the platform can measure it.
    pub memory_kb: Option<i64>,
    /// True if stdout was cut off at `MAX_STDOUT_BYTES`.
    pub truncated: bool,
}

/// Prepare a program in `dir`: write the source, compile if necessary, and
/// return the command needed to run it. Compilation happens once so a submit
/// can reuse the artifact across many test cases.
pub fn prepare(lang_id: &str, code: &str, dir: &Path) -> Result<RunSpec, PrepareError> {
    let spec = lang(lang_id).ok_or_else(|| PrepareError::Unknown(lang_id.to_string()))?;
    if !spec.installed() {
        return Err(PrepareError::NotInstalled {
            hint: spec.install_hint.to_string(),
        });
    }
    let cwd = dir.to_path_buf();
    let write = |name: &str, contents: &str| -> Result<PathBuf, PrepareError> {
        let p = dir.join(name);
        std::fs::write(&p, contents).map_err(|e| PrepareError::Io(e.to_string()))?;
        Ok(p)
    };

    match lang_id {
        "python" => {
            write("main.py", code)?;
            Ok(RunSpec { program: "python".into(), args: vec!["-u".into(), "main.py".into()], cwd })
        }
        "javascript" => {
            write("main.js", code)?;
            Ok(RunSpec { program: "node".into(), args: vec!["main.js".into()], cwd })
        }
        "typescript" => {
            write("main.ts", code)?;
            // Node 22+ strips type annotations natively.
            Ok(RunSpec {
                program: "node".into(),
                args: vec!["--experimental-strip-types".into(), "--no-warnings".into(), "main.ts".into()],
                cwd,
            })
        }
        "java" => {
            write("Main.java", code)?;
            compile_step("javac", &["Main.java"], dir)?;
            Ok(RunSpec { program: "java".into(), args: vec!["-cp".into(), ".".into(), "Main".into()], cwd })
        }
        "rust" => {
            write("main.rs", code)?;
            let bin = if cfg!(windows) { "main.exe" } else { "main" };
            compile_step("rustc", &["-O", "main.rs", "-o", bin], dir)?;
            Ok(RunSpec { program: dir.join(bin).to_string_lossy().into_owned(), args: vec![], cwd })
        }
        "cpp" => {
            write("main.cpp", code)?;
            let bin = if cfg!(windows) { "main.exe" } else { "main" };
            compile_step("g++", &["-O2", "-std=c++17", "main.cpp", "-o", bin], dir)?;
            Ok(RunSpec { program: dir.join(bin).to_string_lossy().into_owned(), args: vec![], cwd })
        }
        "go" => {
            write("main.go", code)?;
            let bin = if cfg!(windows) { "main.exe" } else { "main" };
            compile_step("go", &["build", "-o", bin, "main.go"], dir)?;
            Ok(RunSpec { program: dir.join(bin).to_string_lossy().into_owned(), args: vec![], cwd })
        }
        other => Err(PrepareError::Unknown(other.to_string())),
    }
}

fn compile_step(program: &str, args: &[&str], dir: &Path) -> Result<(), PrepareError> {
    let out = Command::new(program)
        .args(args)
        .current_dir(dir)
        .stdin(Stdio::null())
        .output()
        .map_err(|e| PrepareError::Io(e.to_string()))?;
    if !out.status.success() {
        let mut msg = String::from_utf8_lossy(&out.stderr).to_string();
        if msg.trim().is_empty() {
            msg = String::from_utf8_lossy(&out.stdout).to_string();
        }
        return Err(PrepareError::Compile { message: msg });
    }
    Ok(())
}

/// Run a prepared program once, feeding `input` on stdin, with a wall-clock
/// timeout. Reader threads drain stdout/stderr to avoid pipe deadlocks.
pub fn run_once(spec: &RunSpec, input: &str, timeout: Duration) -> Result<ProcOut, String> {
    let mut child = Command::new(&spec.program)
        .args(&spec.args)
        .current_dir(&spec.cwd)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| e.to_string())?;

    let start = Instant::now();

    if let Some(mut si) = child.stdin.take() {
        let data = input.as_bytes().to_vec();
        thread::spawn(move || {
            let _ = si.write_all(&data);
            let _ = si.flush();
        });
    }

    // Drain stdout/stderr on reader threads, each bounded so a runaway program
    // cannot exhaust our memory. Reading one extra byte past the cap lets us
    // report truncation accurately.
    let out_pipe = child.stdout.take().unwrap();
    let err_pipe = child.stderr.take().unwrap();
    let h_out = thread::spawn(move || read_capped(out_pipe, MAX_STDOUT_BYTES));
    let h_err = thread::spawn(move || read_capped(err_pipe, MAX_STDERR_BYTES));

    let (status_opt, timed_out) = match child.wait_timeout(timeout).map_err(|e| e.to_string())? {
        Some(s) => (Some(s), false),
        None => {
            let _ = child.kill();
            let _ = child.wait();
            (None, true)
        }
    };
    let runtime_ms = start.elapsed().as_millis() as i64;
    let memory_kb = peak_memory_kb(&child);

    let (out_bytes, out_trunc) = h_out.join().unwrap_or_default();
    let (err_bytes, _) = h_err.join().unwrap_or_default();
    let stdout = String::from_utf8_lossy(&out_bytes).to_string();
    let stderr = String::from_utf8_lossy(&err_bytes).to_string();
    let exit_code = status_opt.and_then(|s| s.code());

    Ok(ProcOut {
        stdout,
        stderr,
        exit_code,
        timed_out,
        runtime_ms,
        memory_kb,
        truncated: out_trunc,
    })
}

/// Read up to `cap` bytes from `r`, returning the bytes and whether more data
/// was available (i.e. the output was truncated).
fn read_capped(mut r: impl Read, cap: usize) -> (Vec<u8>, bool) {
    let mut buf = Vec::new();
    // Read one byte beyond the cap so we can detect truncation, then trim.
    let _ = (&mut r).take(cap as u64 + 1).read_to_end(&mut buf);
    let truncated = buf.len() > cap;
    if truncated {
        buf.truncate(cap);
    }
    (buf, truncated)
}

/// Peak resident-set size of a finished (or killed) child, in KiB. Implemented
/// on Windows via `K32GetProcessMemoryInfo`; other platforms return `None`
/// rather than fabricate a number. The child's handle is still open here (the
/// `Child` has not been dropped), so the counters remain queryable.
#[cfg(windows)]
fn peak_memory_kb(child: &std::process::Child) -> Option<i64> {
    use std::os::windows::io::AsRawHandle;

    #[repr(C)]
    #[allow(non_snake_case)]
    struct ProcessMemoryCounters {
        cb: u32,
        PageFaultCount: u32,
        PeakWorkingSetSize: usize,
        WorkingSetSize: usize,
        QuotaPeakPagedPoolUsage: usize,
        QuotaPagedPoolUsage: usize,
        QuotaPeakNonPagedPoolUsage: usize,
        QuotaNonPagedPoolUsage: usize,
        PagefileUsage: usize,
        PeakPagefileUsage: usize,
    }
    extern "system" {
        fn K32GetProcessMemoryInfo(
            process: *mut std::ffi::c_void,
            counters: *mut ProcessMemoryCounters,
            cb: u32,
        ) -> i32;
    }

    let handle = child.as_raw_handle();
    if handle.is_null() {
        return None;
    }
    unsafe {
        let mut c: ProcessMemoryCounters = std::mem::zeroed();
        c.cb = std::mem::size_of::<ProcessMemoryCounters>() as u32;
        if K32GetProcessMemoryInfo(handle, &mut c, c.cb) != 0 {
            Some((c.PeakWorkingSetSize / 1024) as i64)
        } else {
            None
        }
    }
}

#[cfg(not(windows))]
fn peak_memory_kb(_child: &std::process::Child) -> Option<i64> {
    None
}
