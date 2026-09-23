//! Function-signature harness.
//!
//! When a problem declares a `FunctionSpec`, the user writes only the function
//! (e.g. `int solve(int[] nums)`), and this module wraps it with generated I/O
//! glue so it still runs under the app's stdin/stdout judge. The test-case
//! `input` holds one argument per line (arrays are space-separated on their
//! line); the wrapper parses them, calls the function, and prints the return in
//! a canonical form the generator's expected outputs match.
//!
//! Supported languages: Python, Java, TypeScript and JavaScript. Other
//! languages return a clear error for harness problems.
//!
//! The TypeScript glue is appended AFTER the learner's code and imports `fs`
//! under a private alias, so compiler diagnostics keep the learner's own line
//! numbers and a program that already imports `fs` does not collide.

use crate::models::FunctionSpec;

/// Supported harness parameter/return types (one line per argument).
fn is_array(ty: &str) -> bool {
    ty.ends_with("[]")
}

/// Wrap the user's function source into a complete, runnable program.
pub fn wrap(language: &str, user_code: &str, spec: &FunctionSpec) -> Result<String, String> {
    match language {
        "python" => Ok(wrap_python(user_code, spec)),
        "java" => Ok(wrap_java(user_code, spec)),
        "typescript" => Ok(wrap_node(user_code, spec, true)),
        "javascript" => Ok(wrap_node(user_code, spec, false)),
        other => Err(format!(
            "This problem uses the function harness, which isn't available for {other} yet — switch to Python, Java, TypeScript or JavaScript."
        )),
    }
}

/// Whether a problem's harness can run in the given language.
pub fn supports(language: &str) -> bool {
    matches!(language, "python" | "java" | "typescript" | "javascript")
}

// --------------------------------------------------------------------------
// Python
// --------------------------------------------------------------------------

fn py_parse(ty: &str, line: &str) -> String {
    match ty {
        "int" | "long" => format!("int(({line}).strip() or '0')"),
        "double" => format!("float(({line}).strip() or '0')"),
        "bool" => format!("(({line}).strip().lower() in ('true','1'))"),
        "string" => format!("({line}).rstrip('\\r')"),
        "int[]" | "long[]" => format!("[int(x) for x in ({line}).split()]"),
        "double[]" => format!("[float(x) for x in ({line}).split()]"),
        "string[]" => format!("({line}).split()"),
        _ => format!("({line})"),
    }
}

fn py_print(ty: &str, val: &str) -> String {
    match ty {
        "bool" => format!("print('true' if {val} else 'false')"),
        "int[]" | "long[]" | "double[]" => {
            format!("print(' '.join(str(x) for x in {val}))")
        }
        "string[]" => format!("print(' '.join({val}))"),
        _ => format!("print({val})"),
    }
}

fn wrap_python(user: &str, spec: &FunctionSpec) -> String {
    let mut s = String::new();
    s.push_str("import sys\n");
    s.push_str(user);
    s.push_str("\n\n_lines = sys.stdin.read().split('\\n')\n");
    let mut args = Vec::new();
    for (i, p) in spec.params.iter().enumerate() {
        let line = format!("(_lines[{i}] if {i} < len(_lines) else '')");
        s.push_str(&format!("_a{i} = {}\n", py_parse(&p.ty, &line)));
        args.push(format!("_a{i}"));
    }
    s.push_str(&format!("_res = {}({})\n", spec.name, args.join(", ")));
    s.push_str(&py_print(&spec.returns, "_res"));
    s.push('\n');
    s
}

// --------------------------------------------------------------------------
// TypeScript / JavaScript
// --------------------------------------------------------------------------

/// Parse argument line `i` exactly as the Python glue does: numbers default to
/// 0 on an empty line, arrays split on any whitespace, strings keep their
/// spaces but lose a Windows carriage return.
fn node_parse(ty: &str, i: usize) -> String {
    let line = format!("__pcLine({i})");
    match ty {
        "int" | "long" | "double" => format!(r#"Number({line}.trim() || "0")"#),
        "bool" => format!(r#"["true", "1"].includes({line}.trim().toLowerCase())"#),
        "string" => line,
        "int[]" | "long[]" | "double[]" => format!(r"{line}.split(/\s+/).filter(Boolean).map(Number)"),
        "string[]" => format!(r"{line}.split(/\s+/).filter(Boolean)"),
        _ => line,
    }
}

/// Print the return value the way `_ser` in tools/gen_seed.py serialises it.
fn node_print(ty: &str) -> &'static str {
    match ty {
        "bool" => r#"console.log(__pcRes ? "true" : "false");"#,
        t if is_array(t) => r#"console.log(__pcRes.join(" "));"#,
        _ => "console.log(String(__pcRes));",
    }
}

/// `typed` selects TypeScript (an `import`, annotated glue) over JavaScript
/// (`require`, which is what a `.js` file run as CommonJS needs).
fn wrap_node(user: &str, spec: &FunctionSpec, typed: bool) -> String {
    let mut s = String::new();
    s.push_str(user);
    s.push_str("\n\n// ---- harness: reads the arguments, calls your function, prints the result ----\n");
    if typed {
        s.push_str("import * as __pcFs from \"fs\";\n");
        s.push_str(r#"const __pcLines: string[] = __pcFs.readFileSync(0, "utf8").split("\n");"#);
        s.push('\n');
        s.push_str(r#"const __pcLine = (i: number): string => (__pcLines[i] ?? "").replace(/\r$/, "");"#);
        s.push('\n');
    } else {
        s.push_str(r#"const __pcLines = require("fs").readFileSync(0, "utf8").split("\n");"#);
        s.push('\n');
        s.push_str(r#"const __pcLine = (i) => (__pcLines[i] ?? "").replace(/\r$/, "");"#);
        s.push('\n');
    }
    let mut args = Vec::new();
    for (i, p) in spec.params.iter().enumerate() {
        s.push_str(&format!("const __pcA{i} = {};\n", node_parse(&p.ty, i)));
        args.push(format!("__pcA{i}"));
    }
    s.push_str(&format!("const __pcRes = {}({});\n", spec.name, args.join(", ")));
    s.push_str(node_print(&spec.returns));
    s.push('\n');
    s
}

// --------------------------------------------------------------------------
// Java
// --------------------------------------------------------------------------

fn java_type(ty: &str) -> &str {
    match ty {
        "int" => "int",
        "long" => "long",
        "double" => "double",
        "bool" => "boolean",
        "string" => "String",
        "int[]" => "int[]",
        "long[]" => "long[]",
        "double[]" => "double[]",
        "string[]" => "String[]",
        _ => "Object",
    }
}

fn java_parse(ty: &str, idx: usize) -> String {
    let l = format!("L[{idx}]");
    match ty {
        "int" => format!("Integer.parseInt({l}.trim())"),
        "long" => format!("Long.parseLong({l}.trim())"),
        "double" => format!("Double.parseDouble({l}.trim())"),
        "bool" => format!("({l}.trim().equalsIgnoreCase(\"true\") || {l}.trim().equals(\"1\"))"),
        "string" => l,
        "int[]" => format!("pInts({l})"),
        "long[]" => format!("pLongs({l})"),
        "double[]" => format!("pDoubles({l})"),
        "string[]" => format!("pStrs({l})"),
        _ => l,
    }
}

fn java_print(ty: &str) -> String {
    if is_array(ty) {
        // Join array elements with a single space.
        "System.out.println(join(res));".to_string()
    } else {
        "System.out.println(res);".to_string()
    }
}

fn wrap_java(user: &str, spec: &FunctionSpec) -> String {
    let n = spec.params.len();
    let mut decls = String::new();
    let mut call_args = Vec::new();
    for (i, p) in spec.params.iter().enumerate() {
        decls.push_str(&format!(
            "        {} a{} = {};\n",
            java_type(&p.ty),
            i,
            java_parse(&p.ty, i)
        ));
        call_args.push(format!("a{i}"));
    }
    let ret = java_type(&spec.returns);
    let print = java_print(&spec.returns);

    format!(
        r#"import java.util.*;
import java.io.*;

{user}

public class Main {{
    static int[] pInts(String s) {{
        if (s == null || s.trim().isEmpty()) return new int[0];
        String[] t = s.trim().split("\\s+");
        int[] a = new int[t.length];
        for (int i = 0; i < t.length; i++) a[i] = Integer.parseInt(t[i]);
        return a;
    }}
    static long[] pLongs(String s) {{
        if (s == null || s.trim().isEmpty()) return new long[0];
        String[] t = s.trim().split("\\s+");
        long[] a = new long[t.length];
        for (int i = 0; i < t.length; i++) a[i] = Long.parseLong(t[i]);
        return a;
    }}
    static double[] pDoubles(String s) {{
        if (s == null || s.trim().isEmpty()) return new double[0];
        String[] t = s.trim().split("\\s+");
        double[] a = new double[t.length];
        for (int i = 0; i < t.length; i++) a[i] = Double.parseDouble(t[i]);
        return a;
    }}
    static String[] pStrs(String s) {{
        if (s == null || s.trim().isEmpty()) return new String[0];
        return s.trim().split("\\s+");
    }}
    static String join(int[] a) {{ StringBuilder b = new StringBuilder(); for (int i = 0; i < a.length; i++) {{ if (i > 0) b.append(' '); b.append(a[i]); }} return b.toString(); }}
    static String join(long[] a) {{ StringBuilder b = new StringBuilder(); for (int i = 0; i < a.length; i++) {{ if (i > 0) b.append(' '); b.append(a[i]); }} return b.toString(); }}
    static String join(double[] a) {{ StringBuilder b = new StringBuilder(); for (int i = 0; i < a.length; i++) {{ if (i > 0) b.append(' '); b.append(a[i]); }} return b.toString(); }}
    static String join(String[] a) {{ StringBuilder b = new StringBuilder(); for (int i = 0; i < a.length; i++) {{ if (i > 0) b.append(' '); b.append(a[i]); }} return b.toString(); }}

    public static void main(String[] argv) throws Exception {{
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] L = new String[{n}];
        for (int i = 0; i < {n}; i++) {{ String ln = br.readLine(); L[i] = (ln == null) ? "" : ln; }}
{decls}        Solution sol = new Solution();
        {ret} res = sol.{name}({args});
        {print}
    }}
}}
"#,
        user = user,
        n = n,
        decls = decls,
        ret = ret,
        name = spec.name,
        args = call_args.join(", "),
        print = print,
    )
}
