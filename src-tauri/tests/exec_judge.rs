//! End-to-end verification of the execution + judging pipeline against real
//! solutions. These require the relevant toolchain; if it isn't installed the
//! test degrades gracefully (the judge reports `not_installed`) and is skipped.

use poodcode_lib::judge::{judge, judge_with, JudgeConfig};
use poodcode_lib::models::{FunctionSpec, Param, TestCase};
use std::time::Duration;

fn tc(input: &str, expected: &str) -> TestCase {
    TestCase {
        id: 0,
        problem_id: 0,
        kind: "hidden".into(),
        name: "t".into(),
        input: input.into(),
        expected_output: expected.into(),
        ordering: 0,
    }
}

const T: Duration = Duration::from_secs(8);

#[test]
fn python_correct_solution_is_accepted() {
    let code = "import sys\nd=sys.stdin.read().split()\nn=int(d[0])\nprint(sum(map(int,d[1:1+n])))\n";
    let cases = vec![tc("3\n1 2 3\n", "6"), tc("4\n10 -4 3 -3\n", "6"), tc("1\n5\n", "5")];
    let rep = judge("python", code, &cases, T);
    if rep.status == "not_installed" {
        eprintln!("python not installed; skipping");
        return;
    }
    assert_eq!(rep.status, "accepted", "report: {rep:?}");
    assert_eq!(rep.passed, 3);
}

#[test]
fn python_wrong_solution_is_wrong() {
    // Always prints 0 — should fail.
    let code = "import sys\nsys.stdin.read()\nprint(0)\n";
    let cases = vec![tc("3\n1 2 3\n", "6")];
    let rep = judge("python", code, &cases, T);
    if rep.status == "not_installed" {
        return;
    }
    assert_eq!(rep.status, "wrong", "report: {rep:?}");
    assert_eq!(rep.passed, 0);
}

#[test]
fn python_runtime_error_is_reported() {
    let code = "raise SystemExit(1)\n";
    let cases = vec![tc("1\n", "1")];
    let rep = judge("python", code, &cases, T);
    if rep.status == "not_installed" {
        return;
    }
    // Non-zero exit -> classified as error.
    assert_eq!(rep.status, "error", "report: {rep:?}");
}

#[test]
fn output_whitespace_is_normalized() {
    // Trailing spaces/newlines should still be accepted.
    let code = "print('4 5 1 2 3   ')\n";
    let cases = vec![tc("", "4 5 1 2 3\n")];
    let rep = judge("python", code, &cases, T);
    if rep.status == "not_installed" {
        return;
    }
    assert_eq!(rep.status, "accepted", "report: {rep:?}");
}

#[test]
fn javascript_correct_solution_is_accepted() {
    let code = "const d=require('fs').readFileSync(0,'utf8').split(/\\s+/).filter(Boolean).map(Number);const n=d[0];console.log(d.slice(1,1+n).reduce((a,b)=>a+b,0));";
    let cases = vec![tc("3\n1 2 3\n", "6"), tc("2\n-5 5\n", "0")];
    let rep = judge("javascript", code, &cases, T);
    if rep.status == "not_installed" {
        return;
    }
    assert_eq!(rep.status, "accepted", "report: {rep:?}");
}

#[test]
fn java_compiles_and_runs() {
    let code = r#"import java.util.*;
public class Main {
    public static void main(String[] a) {
        Scanner s = new Scanner(System.in);
        int n = s.nextInt(); long sum = 0;
        for (int i = 0; i < n; i++) sum += s.nextLong();
        System.out.println(sum);
    }
}"#;
    let cases = vec![tc("3\n1 2 3\n", "6"), tc("2\n-5 5\n", "0")];
    let rep = judge("java", code, &cases, T);
    if rep.status == "not_installed" {
        return;
    }
    assert_eq!(rep.status, "accepted", "report: {rep:?}");
}

#[test]
fn rust_compiles_and_runs() {
    let code = r#"use std::io::{self, Read};
fn main() {
    let mut s = String::new();
    io::stdin().read_to_string(&mut s).unwrap();
    let mut it = s.split_whitespace().map(|x| x.parse::<i64>().unwrap());
    let n = it.next().unwrap();
    let sum: i64 = (0..n).map(|_| it.next().unwrap()).sum();
    println!("{}", sum);
}"#;
    let cases = vec![tc("3\n1 2 3\n", "6")];
    let rep = judge("rust", code, &cases, T);
    if rep.status == "not_installed" {
        return;
    }
    assert_eq!(rep.status, "accepted", "report: {rep:?}");
}

#[test]
fn java_compile_error_is_reported() {
    let code = "public class Main { this is not valid java }";
    let cases = vec![tc("", "")];
    let rep = judge("java", code, &cases, T);
    if rep.status == "not_installed" {
        return;
    }
    assert_eq!(rep.status, "error", "report: {rep:?}");
    assert!(!rep.compile_error.is_empty());
}

#[test]
fn python_function_harness_accepts_correct_solution() {
    // User writes only the function; the harness supplies args and reads the return.
    let code = "def solve(nums, target):\n    pos = {}\n    for i, x in enumerate(nums):\n        if target - x in pos:\n            return [pos[target - x] + 1, i + 1]\n        pos[x] = i\n    return [-1]\n";
    let spec = FunctionSpec {
        name: "solve".into(),
        params: vec![
            Param { name: "nums".into(), ty: "int[]".into() },
            Param { name: "target".into(), ty: "int".into() },
        ],
        returns: "int[]".into(),
    };
    let cfg = JudgeConfig {
        mode: "exact".into(),
        tolerance: 0.0,
        function_spec: Some(spec),
        checker: None,
        timeout: T,
    };
    let cases = vec![tc("2 7 11 15\n9\n", "1 2"), tc("3 2 4\n6\n", "2 3")];
    let rep = judge_with("python", code, &cases, &cfg);
    if rep.status == "not_installed" {
        return;
    }
    assert_eq!(rep.status, "accepted", "report: {rep:?}");
}

#[test]
fn java_function_harness_accepts_correct_solution() {
    let code = "class Solution {\n    int solve(int[] nums) {\n        int best = nums[0], cur = nums[0];\n        for (int i = 1; i < nums.length; i++) { cur = Math.max(nums[i], cur + nums[i]); best = Math.max(best, cur); }\n        return best;\n    }\n}";
    let spec = FunctionSpec {
        name: "solve".into(),
        params: vec![Param { name: "nums".into(), ty: "int[]".into() }],
        returns: "int".into(),
    };
    let cfg = JudgeConfig { mode: "exact".into(), tolerance: 0.0, function_spec: Some(spec), checker: None, timeout: T };
    let cases = vec![tc("-2 1 -3 4 -1 2 1 -5 4\n", "6"), tc("1\n", "1")];
    let rep = judge_with("java", code, &cases, &cfg);
    if rep.status == "not_installed" {
        return;
    }
    assert_eq!(rep.status, "accepted", "report: {rep:?}");
}

#[test]
fn java_harness_handles_array_return() {
    // "running sum" returns int[] — exercises the Java harness array serializer.
    let code = "class Solution {\n    int[] solve(int[] nums) {\n        int[] out = new int[nums.length];\n        int s = 0;\n        for (int i = 0; i < nums.length; i++) { s += nums[i]; out[i] = s; }\n        return out;\n    }\n}";
    let spec = FunctionSpec {
        name: "solve".into(),
        params: vec![Param { name: "nums".into(), ty: "int[]".into() }],
        returns: "int[]".into(),
    };
    let cfg = JudgeConfig { mode: "exact".into(), tolerance: 0.0, function_spec: Some(spec), checker: None, timeout: T };
    let cases = vec![tc("1 2 3 4\n", "1 3 6 10"), tc("5\n", "5")];
    let rep = judge_with("java", code, &cases, &cfg);
    if rep.status == "not_installed" {
        return;
    }
    assert_eq!(rep.status, "accepted", "report: {rep:?}");
}

#[test]
fn float_compare_mode_tolerates_small_error() {
    let code = "print(3.14159)\n";
    let cfg = JudgeConfig { mode: "float".into(), tolerance: 1e-2, function_spec: None, checker: None, timeout: T };
    let cases = vec![tc("", "3.14")];
    let rep = judge_with("python", code, &cases, &cfg);
    if rep.status == "not_installed" {
        return;
    }
    assert_eq!(rep.status, "accepted", "report: {rep:?}");
}

#[test]
fn unordered_compare_mode_ignores_order() {
    let code = "print('3 1 2')\n";
    let cfg = JudgeConfig { mode: "unordered".into(), tolerance: 0.0, function_spec: None, checker: None, timeout: T };
    let cases = vec![tc("", "1 2 3")];
    let rep = judge_with("python", code, &cases, &cfg);
    if rep.status == "not_installed" {
        return;
    }
    assert_eq!(rep.status, "accepted", "report: {rep:?}");
}

#[test]
fn checker_mode_accepts_any_valid_answer() {
    // Two-sum "any pair": a checker validates the output instead of exact match.
    let checker = "def check(inp, out):\n    lines = inp.strip().split('\\n')\n    nums = list(map(int, lines[0].split()))\n    target = int(lines[1])\n    i, j = map(int, out.split())\n    n = len(nums)\n    return 1 <= i <= n and 1 <= j <= n and i != j and nums[i-1] + nums[j-1] == target\n";
    let spec = FunctionSpec {
        name: "solve".into(),
        params: vec![
            Param { name: "nums".into(), ty: "int[]".into() },
            Param { name: "target".into(), ty: "int".into() },
        ],
        returns: "int[]".into(),
    };
    // A solution returning indices in the OPPOSITE order still passes the checker.
    let code = "def solve(nums, target):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i]+nums[j]==target:\n                return [j+1, i+1]\n    return [-1,-1]\n";
    let cfg = JudgeConfig {
        mode: "checker".into(),
        tolerance: 0.0,
        function_spec: Some(spec.clone()),
        checker: Some(checker.to_string()),
        timeout: T,
    };
    let cases = vec![tc("2 7 11 15\n9\n", ""), tc("1 2 3 4 5\n6\n", "")];
    let rep = judge_with("python", code, &cases, &cfg);
    if rep.status == "not_installed" {
        return;
    }
    assert_eq!(rep.status, "accepted", "valid pair should pass checker: {rep:?}");

    // A wrong pair must be rejected.
    let bad = "def solve(nums, target):\n    return [1, 2]\n";
    let cfg2 = JudgeConfig { mode: "checker".into(), tolerance: 0.0, function_spec: Some(spec), checker: Some(checker.to_string()), timeout: T };
    let rep2 = judge_with("python", bad, &[tc("1 2 3 4 5\n100\n", "")], &cfg2);
    if rep2.status != "not_installed" {
        assert_ne!(rep2.status, "accepted", "invalid pair must fail checker");
    }
}

#[test]
fn oversized_output_is_truncated_and_never_accepted() {
    // Print far more than the 1 MiB capture cap.
    let code = "import sys\nsys.stdout.write('x' * 5_000_000)\n";
    let cases = vec![tc("", "x")];
    let rep = judge("python", code, &cases, T);
    if rep.status == "not_installed" {
        return;
    }
    assert!(rep.results[0].truncated, "expected truncation flag: {rep:?}");
    assert_ne!(rep.status, "accepted", "truncated output must not pass");
}

#[cfg(windows)]
#[test]
fn peak_memory_is_measured_on_windows() {
    let code = "print(42)\n";
    let cases = vec![tc("", "42")];
    let rep = judge("python", code, &cases, T);
    if rep.status == "not_installed" {
        return;
    }
    assert!(
        rep.memory_kb.unwrap_or(0) > 0,
        "expected a peak-memory reading, got {:?}",
        rep.memory_kb
    );
}

#[test]
fn typescript_type_stripping_runs() {
    let code = "const x: number = 41; console.log(x + 1);";
    let cases = vec![tc("", "42")];
    let rep = judge("typescript", code, &cases, T);
    if rep.status == "not_installed" {
        return;
    }
    assert_eq!(rep.status, "accepted", "report: {rep:?}");
}
