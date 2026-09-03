# Java Roadmap — After the Basics

The plan for the Java track in Poodcode, for someone who already has the
basics down (variables, types, operators, `if`/`else`, loops, and enough
arrays to declare one and loop over it).

It is deliberately **not** a "learn Java from zero" course — the TypeScript
course already fills that shape. This one starts where most people stall:
knowing the syntax but not yet being able to *reach* for the right array
pattern, the right string method, or the right method signature without
looking it up.

**Status legend** — ✅ built and shipping in the app · 🚧 partially built ·
⬜ planned.

**Built so far:** Parts 1–8, complete (modules 1–28) — **28 modules, 132
lessons, 570 judged exercises, plus 700 practice problems** in 140 variation
families.

**The track is finished.** Part 8 was the last part worth authoring for
interview preparation, and it is done.

**Scope note.** Parts 9, 13 and 14 are deliberately **not planned** — file I/O,
JDBC/Maven/Spring and the backend stack are job skills rather than
interview-coding material, and the Backend Lab already covers the transport
half. Part 11 is folded into earlier modules rather than authored, and Part 12
is already served by the Problem Library and the Mastery track. The track ends
at Part 8 plus, possibly, a single senior-level module on the JVM and design
patterns.

---

## Where it lives in the app

| Piece | Path |
|---|---|
| Content generator | `tools/java_course.py` (+ one `java_mNN_*.py` per module, and one `java_pNN_practice.py` per module's Practice section) |
| Generated seed | `src-tauri/seeds/java_course.json` |
| Rust command | `java_course` (`src-tauri/src/commands.rs`) |
| UI | `src/pages/Course.tsx` (shared with the TypeScript course), route `/java-course` |
| Fast verifier | `python tools/verify_java_course.py --starters` |
| Judge-level verifier | `cd src-tauri && cargo test --test verify_java_course` |

Modules are graded and completed exactly like TypeScript course weeks: every
judged exercise runs through the same stdin/stdout judge (`javac` → `java Main`),
and a module marks itself ✓ Done once you've read it through and solved
everything in it.

Each module also carries a **Practice** section: five families of five
variations each, where a family drills one pattern and twists a single
dimension at a time. Practice is deliberately *not* required to complete a
module — it is a drilling ground to come back to, so adding 25 problems never
moves the finish line.

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

## Part 4 — Object-oriented programming ✅

The heaviest section in Java, and the one interviews probe hardest. Complete.

**11. Classes and objects** ✅
Classes and objects · fields / instance variables · methods inside classes ·
`this` · constructors and constructor chaining (`this(...)`) · the default
constructor · `static` fields and methods · `final` · arrays of objects

**12. Encapsulation** ✅
Access modifiers · `private` fields · getters and setters · verbs over
setters · class invariants established in the constructor and preserved by
every mutator · clamping vs rejecting vs throwing · immutable objects ·
defensive copying in and out

**13. Inheritance and polymorphism** ✅
`extends` and the is-a test · `protected` · `super(...)` and `super.method()` ·
method overriding (vs overloading) · `@Override` · polymorphism and dynamic
dispatch · upcasting and downcasting · `instanceof` · `Object` as the root ·
the `toString` / `equals` / `hashCode` contracts

**14. Abstraction, interfaces and composition** ✅
Abstract classes and abstract methods · the template method · interfaces ·
`implements` · why implementing methods must be `public` · programming to an
interface · multiple interfaces · `default` and `static` interface methods ·
abstract class vs interface · pairing the two (interface + skeleton) ·
`final` methods and `final` classes · composition over inheritance · has-a ·
delegation · aggregation and association · the fragile base class

*(The scope linter reserves `abstract `, `interface ` and `implements ` for this
module, so no earlier one can reach for them.)*

## Part 5 — Exception handling ✅

Modules 15–16.

**15. What an exception is, and catching it** ✅
What an exception is · stack unwinding · reading a stack trace · `try` ·
`catch` · scope and definite assignment · `finally` and its four orderings ·
the hierarchy · several catch blocks · multi-catch · catching narrowly

**16. Throwing, checked exceptions, and resources** ✅
`throw` · `IllegalArgumentException` vs `IllegalStateException` · checked vs
unchecked · `throws` · custom exception types · exceptions that carry data ·
`AutoCloseable` · try-with-resources · closing order

## Part 6 — Collections framework ✅

Modules 17–20.

**17. Lists** ✅
`List` · `ArrayList` · `LinkedList` · generics and the diamond · autoboxing ·
`remove(int)` vs `remove(Object)` · `==` on wrappers · type erasure ·
the enhanced `for`, index loops and `Iterator` ·
`ConcurrentModificationException` and the three safe removals · cost comparison

**18. Sets and Maps** ✅
`Set` · `HashSet` / `LinkedHashSet` / `TreeSet` · the hashCode/equals contract ·
`Map` · `HashMap` / `LinkedHashMap` / `TreeMap` · `getOrDefault` and the
frequency-count idiom · `keySet` / `values` / `entrySet` · why iteration order
has to be chosen · grouping and inverting

**19. Queues, deques, stacks and heaps** ✅
`Queue` · the offer/poll/peek and add/remove/element families · `Deque` ·
`ArrayDeque` · stacks and why not `java.util.Stack` · bracket matching ·
`PriorityQueue` · heap order vs sorted order · the k-largest idiom

**20. Ordering, sorting, and choosing** ✅
`Comparable` and `compareTo` · why `Integer.compare` and never subtraction ·
`Comparator` as a named class · reversing · multi-key tie-breaking ·
`Collections.sort` and `list.sort` · stability and the two-pass sort ·
comparators in sorted collections · choosing a collection by cost

## Part 7 — Generics ✅

Modules 21–24. Modules 17–20 *used* `List<String>` on every page without ever
saying what the angle brackets were; this part is the answer, and it is
sequenced so that each idea is the thing the previous one could not do — ending
on what the compiler does with all of it.

**21. Type parameters and generic classes** ✅
Why generics exist (an `Object` field, a cast, and a `ClassCastException`) ·
raw types and what they switch off · `class Box<T>` · type parameter vs type
argument · the diamond · reference-type arguments only (`Box<int>` is illegal) ·
`T` as a field, parameter and return type · several parameters (`Pair<A, B>`) ·
nested type arguments · a container of your own wrapping a `List<T>` ·
the three things a type parameter cannot do (`static T`, `new T()`, `new T[]`)

**22. Generic methods and bounded type parameters** ✅
`static <T>` and where the brackets go · type inference at the call site ·
the type witness · one `T` tying two parameters together · why an unbounded `T`
can only be moved around · `<T extends Comparable<T>>` · `<T extends Number>` ·
`extends` meaning implements too · multiple bounds with `&` · bounds on a class
(`class Range<T extends Comparable<T>>`) · generic interfaces, passing `T`
through or fixing it · generic class vs generic method · a bound vs a
`Comparator`

**23. Wildcards** ✅
Invariance: `List<Integer>` is not a `List<Number>` · array covariance and
`ArrayStoreException` as the contrast · `List<?>` and why only `null` may be
added · `<?>` vs a raw type · `? extends T` (producers) · `? super T`
(consumers) · **PECS** · `copy(List<? super T>, List<? extends T>)` ·
reading the JDK's own signatures (`sort(Comparator<? super E>)`,
`addAll(Collection<? extends E>)`) · wildcard vs named type parameter ·
never a wildcard in a return type

**24. Erasure, and what it costs** ✅
What the compiler actually emits · one run-time class per generic type ·
type arguments erased to their bound · the casts the compiler inserts ·
why `new T()`, `new T[]` and `static T` are illegal · `instanceof List<?>` vs
`instanceof List<String>` · the `Object[]` workaround · unchecked casts as a
promise, and where the `ClassCastException` actually lands · heap pollution ·
`@SuppressWarnings("unchecked")` · generic varargs and `@SafeVarargs` · two
overloads that erase to the same signature · bridge methods · `Class<T>` type
tokens with `isInstance` and `cast` · interoperating with legacy raw-typed code

*(The scope linter reserves `<T>`, `<A,`, `<K,` and friends for module 21 and
`? extends` / `? super` / `<?>` for module 23, so no earlier module can reach
for either.)*

## Part 8 — Java 8+ ✅

Modules 25–28. The course withheld `->`, `.stream()` and `Optional` for
twenty-four modules on purpose: every `Comparator` in module 20 and every
interface implementation in module 14 is a **named class**, so module 25 opens
by collapsing code the learner has already written by hand.

*(`default` and `static` interface methods are not here — module 14 already
teaches them.)*

**25. Lambdas, functional interfaces and method references** ✅
Why a lambda exists (module 20's named `Comparator`, in one line) · the arrow ·
expression body vs block body · target typing · `Predicate` / `Function` /
`Consumer` / `Supplier` and their method names · `BiFunction` · declaring your
own functional interface · `@FunctionalInterface` and what it checks · why
`default`/`static` methods don't count · capture and **effectively final** ·
a lambda opens no new scope · `this` inside a lambda · closures and returning a
lambda · the four kinds of method reference · `Comparator.comparing` ·
`Iterable.forEach`

**26. Streams: the pipeline** ✅
Source, intermediate, terminal · a stream is not a collection · **laziness**,
and element-at-a-time execution · single-use and `IllegalStateException` ·
the source is never modified · `filter` and `map` · which vs what, and where the
element type changes · filter early · `sorted` / `sorted(Comparator)` /
`distinct` / `limit` / `skip` · stateful vs short-circuiting operations ·
`forEach` / `count` / `anyMatch` / `allMatch` / `noneMatch` · the empty-stream
answers · the pipeline with no terminal that silently does nothing

**27. Collecting and reducing** ✅
`collect` and `Collector` · `Collectors.toList` / `toSet` / `joining` (with
prefix and suffix) / `counting` · why a collected `Set` or a `HashMap` must
never be printed · `groupingBy` with a **map factory** and a **downstream
collector** · a frequency table in one line · `partitioningBy` and its
always-present `false`/`true` keys · `toMap`, duplicate keys, and the merge
function · `reduce(identity, op)` · why the identity must be neutral · folding
to a *choice* rather than a combination · primitive streams: `mapToInt`, `sum`,
`summaryStatistics` and its plain-value getters, `boxed`

*(The one-argument `reduce(op)`, and `average`/`max`/`min`, all return Optionals
and so are deferred to module 28 — which is the honest reason, not a dodge: an
empty stream has no answer.)*

**28. `Optional`** ✅
Why it exists — the signature that cannot lie, not the crash · `of` (an
assertion) / `ofNullable` / `empty` · `orElse` vs **`orElseGet`** and eager
argument evaluation · `orElseThrow(Supplier)` · `ifPresent` · `map` / `filter` /
`flatMap`, and why a chain removes the nested `if` · the terminals that return
one — `findFirst`, `max`, `min`, identity-free `reduce`, `average` — and the
single reason they all do · `OptionalInt` / `OptionalDouble` · **where not to
use it**: fields, parameters, collections · why every unguarded `get()` is the
`NullPointerException` you were avoiding, renamed

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
