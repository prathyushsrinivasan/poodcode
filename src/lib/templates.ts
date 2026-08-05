// Generic per-language stdin-reading skeletons. Used when a problem has no
// language-specific starter code. They read all of stdin and leave parsing to
// the user — a correct, universally-applicable starting point.

export const GENERIC_TEMPLATES: Record<string, string> = {
  python: `import sys

def main():
    data = sys.stdin.read()
    # TODO: parse 'data' and print your answer
    print(data.strip())

main()
`,
  javascript: `const data = require('fs').readFileSync(0, 'utf8');

function main() {
  // TODO: parse 'data' and print your answer
  process.stdout.write(data.trim());
}

main();
`,
  typescript: `const data: string = require('fs').readFileSync(0, 'utf8');

function main(): void {
  // TODO: parse 'data' and print your answer
  process.stdout.write(data.trim());
}

main();
`,
  java: `import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) sb.append(line).append('\\n');
        // TODO: parse the input and print your answer
        System.out.print(sb.toString().trim());
    }
}
`,
  cpp: `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    // TODO: read from cin and print your answer to cout
    return 0;
}
`,
  rust: `use std::io::{self, Read, Write};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    // TODO: parse 'input' and print your answer
    print!("{}", input.trim());
    io::stdout().flush().unwrap();
}
`,
  go: `package main

import (
    "bufio"
    "fmt"
    "os"
)

func main() {
    reader := bufio.NewReader(os.Stdin)
    _ = reader
    // TODO: read input and print your answer
    fmt.Print("")
}
`,
  csharp: `using System;

class Main2 {
    static void Main() {
        string input = Console.In.ReadToEnd();
        // TODO: parse 'input' and print your answer
        Console.Write(input.Trim());
    }
}
`,
  kotlin: `fun main() {
    val input = generateSequence(::readLine).joinToString("\\n")
    // TODO: parse 'input' and print your answer
    print(input.trim())
}
`,
};

/** Best starter code for a language: problem-specific if present, else generic. */
export function starterFor(
  starter: Record<string, string>,
  langId: string
): string {
  return starter[langId] ?? GENERIC_TEMPLATES[langId] ?? "";
}
