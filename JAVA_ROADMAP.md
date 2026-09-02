# Java Roadmap — After the Basics

The plan for the Java track in Poodcode, for someone who already has the
basics down (variables, types, operators, `if`/`else`, loops, and enough
arrays to declare one and loop over it).

It is deliberately **not** a "learn Java from zero" course — the TypeScript
course already fills that shape. This one starts where most people stall:
knowing the syntax but not yet being able to *reach* for the right array
pattern, the right string method, or the right method signature without
looking it up.

**Status legend** — ✅ built and shipping in the app · 🚧 in progress ·
⬜ planned.

---

## Where it lives in the app

| Piece | Path |
|---|---|
| Content generator | `tools/java_course.py` (+ `java_arrays.py`, `java_strings.py`, `java_methods.py`) |
| Generated seed | `src-tauri/seeds/java_course.json` |
| Rust command | `java_course` (`src-tauri/src/commands.rs`) |
| UI | `src/pages/Course.tsx` (shared with the TypeScript course), route `/java-course` |
| Fast verifier | `python tools/verify_java_course.py --starters` |
| Judge-level verifier | `cd src-tauri && cargo test --test verify_java_course` |

Modules are graded and completed exactly like TypeScript course weeks: every
judged exercise runs through the same stdin/stdout judge (`javac` → `java Main`),
and a module marks itself ✓ Done once you've read it through and solved
everything in it.

---

## Part 1 — Arrays, deeply ✅

Modules 1–5. The point is not "what is an array" but *fluency*: the five or six
motions that show up in nearly every array question.

**1. Arrays in memory** ✅
1D arrays · declaration and defaults · `.length` · traversal (index loop vs
enhanced `for`) · finding max/min and the *index* of max/min · linear search ·
the `Arrays` utility class (`toString`, `fill`, `copyOf`, `copyOfRange`,
`equals`) · aliasing vs copying

**2. 2D and multidimensional arrays** ✅
Rectangular `int[r][c]` · row-major layout · row-wise and column-wise
traversal · `deepToString` · row/column aggregates · diagonals · transpose ·
jagged arrays · 3D arrays

**3. Searching and sorting by hand** ✅
Binary search (the sorted precondition, the safe midpoint, the loop
invariant) · bubble sort with early exit · selection sort · insertion sort ·
stability and pass counts · `Arrays.sort` and `Arrays.binarySearch`

**4. Rearranging and counting** ✅
Array reversal (two-pointer swap) · rotation (extra array, and the
three-reversal trick) · frequency/counting arrays · duplicate elements ·
missing and repeating numbers

**5. Prefix sums, two pointers, sliding window** ✅
1D prefix sums and range-sum queries · 2D prefix sums · the two-pointer
technique on sorted arrays · fixed-size sliding window · variable-size
sliding window

## Part 2 — Strings ✅

Modules 6–8.

**6. The object behind the text** ✅
Creating strings · the string pool · literals vs `new String` ·
immutability · `length()`, `charAt()`, `substring()` · `equals()` vs `==` ·
`compareTo` · concatenation and what `s = s + x` really costs

**7. The String API and the classic problems** ✅
`indexOf` / `lastIndexOf` / `contains` / `startsWith` / `endsWith` ·
`isEmpty` / `isBlank` · `toUpperCase` / `strip` / `replace` / `repeat` ·
`split` and `String.join` · character classification (`Character.isDigit`,
`isLetter`, …) · traversal · reversal · palindrome · anagram · character
frequency

**8. StringBuilder and StringBuffer** ✅
Why `+=` in a loop is O(n²) · `append` / `insert` / `delete` /
`deleteCharAt` / `replace` / `reverse` / `setCharAt` · capacity ·
`StringBuffer`, synchronization, and how to choose

## Part 3 — Methods ✅

Modules 9–10.

**9. Methods** ✅
Defining and calling · the anatomy of a signature · parameters vs
arguments · return values and `void` · **pass-by-value** for primitives,
arrays and Strings · overloading and how Java picks an overload ·
scope and shadowing · `static` · varargs

**10. Recursion basics** ✅
Base case and recursive case · the call stack · factorial and Fibonacci ·
recursion over arrays (sum, max, search, reverse) · recursion over strings ·
recursive binary search · recursion vs iteration · `StackOverflowError`

---

## Part 4 — Object-oriented programming ⬜

The heaviest section in Java, and the one interviews probe hardest.

Classes and objects · fields / instance variables · methods inside classes ·
constructors (and constructor chaining) · `this` · `static` fields and
methods · encapsulation · getters and setters · inheritance · `super` ·
method overriding (vs overloading) · polymorphism · abstraction ·
abstract classes · interfaces · composition · association · `final` ·
`equals`/`hashCode`/`toString` contracts

## Part 5 — Exception handling ⬜

What an exception is · `try` · `catch` · `finally` · `throw` vs `throws` ·
checked vs unchecked · custom exceptions · multiple catch blocks and
multi-catch · the exception hierarchy · try-with-resources

## Part 6 — Collections framework ⬜

In order: `ArrayList` · `LinkedList` · `HashSet` · `LinkedHashSet` ·
`TreeSet` · `HashMap` · `LinkedHashMap` · `TreeMap` · `Queue` · `Deque` ·
`PriorityQueue` · `Stack` (and why `ArrayDeque` is the modern answer) ·
`Iterator`. Plus: generics in collections · `Comparable` · `Comparator` ·
sorting collections · choosing the right collection.

## Part 7 — Generics ⬜

Generic classes · generic methods · type parameters · wildcards (`<?>`,
`<? extends T>`, `<? super T>`) · why generics exist (and what erasure costs)

## Part 8 — Java 8+ ⬜

Lambda expressions · functional interfaces (`Predicate`, `Consumer`,
`Function`, `Supplier`) · method references · the Stream API (`filter`,
`map`, `sorted`, `distinct`, `reduce`, `collect`, `forEach`) · `Optional` ·
default and static interface methods

## Part 9 — File handling and I/O ⬜

`File` · reading and writing files · `FileReader` / `FileWriter` ·
buffered I/O · `InputStream` / `OutputStream` · serialization basics ·
`Path` and `Files`

## Part 10 — Multithreading ⬜

Processes vs threads · creating threads (`Thread`, `Runnable`) · the thread
lifecycle · `sleep()` · `join()` · synchronization · race conditions ·
locks · `ExecutorService` · `Callable` and `Future` · concurrent collections

## Part 11 — The APIs worth knowing cold ⬜

`Math` · `Arrays` · `Collections` · `String` · `StringBuilder` · `Objects` ·
`Random` · `LocalDate` · `LocalTime` · `LocalDateTime` · `DateTimeFormatter`

## Part 12 — Data structures and algorithms in Java ⬜

Time and space complexity · Big-O · recursion · linked lists · stacks ·
queues · hashing · trees · binary search trees · heaps · graphs · BFS · DFS ·
sorting algorithms · searching algorithms · two pointers · sliding window ·
prefix sums · backtracking · dynamic programming basics · greedy

*(Note: the existing Problem Library and 6-Month Mastery track already cover
a lot of this ground with judged problems — this part is about sequencing it
rather than authoring it from nothing.)*

## Part 13 — Advanced Java ⬜

JDBC · SQL basics · database connectivity · Maven / Gradle · JUnit ·
logging · annotations · reflection · design patterns · JVM basics ·
garbage collection · memory management · concurrency in depth

*(SQL basics already ship as their own Learn track.)*

## Part 14 — Java backend development ⬜

HTTP/HTTPS · REST APIs · JSON · servlets · Spring · **Spring Boot** ·
Spring MVC · Spring Data JPA · Hibernate · Spring Security ·
authentication/authorization · microservices · Docker · Git/GitHub ·
basic cloud deployment

*(The Backend Lab already teaches the transport-layer half of this — routing,
CRUD, validation, persistence, querying, auth — in Node, deliberately without
a framework. Part 14 is the Java/Spring restatement of the same ideas, which
lands much better once you have already built the thing by hand.)*

---

## Design rules for this track

These are the same rules the TypeScript course follows, restated for Java.

1. **Nothing before its module.** A module may only require ideas introduced
   in it or earlier. `_lint_scope` in `tools/java_course.py` scans every
   program and fails generation on a violation — so, for example, no exercise
   before Module 8 may use `StringBuilder`, and nothing before Module 10 may
   define a recursive helper.
2. **You already know the basics.** Variables, `if`/`else`, `for`, `while`,
   and printing are assumed from line one. Module 1 opens on memory layout,
   not on `int x = 5;`.
3. **Every exercise is judged.** Programs read stdin and print to stdout, and
   are graded by the same judge as every other track — no self-marking.
4. **Expected outputs are computed, not typed.** Each test case's expected
   output is produced by a Python mirror of the intended algorithm inside the
   generator, the same trust model `tools/gen_seed.py` uses for the problem
   bank. A hand-typed expected output is a bug waiting to happen.
5. **Interview framing throughout.** Where a real codebase would just call
   `Arrays.sort`, the lesson says so — and then hand-writes it anyway, because
   that is what gets asked.
