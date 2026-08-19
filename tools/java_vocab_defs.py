# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Java vocabulary Learn track.
#
# This file is exec()'d inside gen_seed.py's namespace (see the hook after the
# java_core2 drills). It extends CONCEPTS / CATEGORY / LESSONS in place with a
# set of *reference* concepts: the ~280 words a Java engineer keeps meeting,
# each with TWO explanations —
#     * a crisp textbook definition, and
#     * a non-textbook, plain-English "what it actually means" line,
# plus a tiny code snippet where one helps.
#
# WHY IT'S A "LANGUAGE" IN THE LEARN TAB:
#   Every concept here is marked  "language": "java_vocab"  so the Learn tab's
#   language toggle shows them under their own 📖 Java Vocab view, next to Java,
#   TypeScript, 日本語 and 🧠 Algorithms. There is NO code judge — these are
#   reference concepts (no fill-in-the-blank drills). They teach through:
#     * a Markdown glossary table (the two explanations + example),
#     * structured flashcards (`cards`) that flow into the SRS study mode, and
#     * a multiple-choice self-check quiz (`quiz`, graded client-side).
#   Concepts are embedded JSON, so there is NO SEED_VERSION / SQLite impact —
#   rebuild with `python tools/gen_seed.py`.
#
# TABLE / MARKDOWN NOTE:
#   The renderer is react-markdown + remark-gfm WITHOUT rehype-raw, so raw HTML
#   never renders. A literal '|' would break a table cell, so pipes are escaped
#   as '\|' (GFM renders that as a literal pipe, even inside a code span). Code
#   snippets therefore may contain '|' / '||' safely. No cell may contain a
#   newline or a backtick.
# ---------------------------------------------------------------------------

JV_LANG = "java_vocab"


def _jv_esc(cell):
    """Escape a pipe for a GFM table cell (renders as a literal '|')."""
    return cell.replace("|", "\\|")


def _jv_table(rows, intro=""):
    """Build the glossary lesson: an intro paragraph + a 4-column table of
    (term, textbook definition, plain-English gloss, example snippet)."""
    out = [
        "| Term | Textbook definition | In plain English | Example |",
        "|---|---|---|---|",
    ]
    for (term, textbook, plain, code) in rows:
        for c in (term, textbook, plain, code):
            assert "\n" not in c, f"newline in cell: {c!r}"
        # term and code are wrapped in a backtick code span, so they must not
        # contain a backtick themselves (prose cells may — it renders as code).
        for c in (term, code):
            assert "`" not in c, f"backtick in wrapped cell (breaks the code span): {c!r}"
        ex = f"`{_jv_esc(code)}`" if code else "—"
        out.append(
            f"| `{_jv_esc(term)}` | {_jv_esc(textbook)} | {_jv_esc(plain)} | {ex} |"
        )
    table = "\n".join(out) + "\n"
    return (intro.strip() + "\n\n" + table) if intro else table


def _jv_cards(rows):
    """Structured flashcards from the same rows the glossary shows, so the Learn
    tab can offer SRS study over them. Field mapping for the java_vocab variant
    of CardStudy/CardBack:  meaning = textbook line, example_en = plain-English
    line, example_ja = code snippet, reading = unused."""
    return [
        {
            "front": term,
            "reading": "",
            "meaning": textbook,
            "example_ja": code,
            "example_en": plain,
        }
        for (term, textbook, plain, code) in rows
    ]


def _jvq(question, options, answer, explanation):
    """One multiple-choice self-check question (answer = 0-based index)."""
    assert len(options) >= 2, f"quiz needs >=2 options: {question!r}"
    assert 0 <= answer < len(options), f"quiz answer out of range: {question!r}"
    assert explanation, f"quiz needs an explanation: {question!r}"
    return {
        "question": question,
        "options": options,
        "answer": answer,
        "explanation": explanation,
    }


def _jv(key, name, category, what, deep, note, rows, quiz=None, intro=""):
    """Register one Java-vocabulary reference concept."""
    assert key not in CONCEPTS, f"java_vocab: duplicate concept key {key!r}"
    seen = set()
    for r in rows:
        assert len(r) == 4, f"{key}: row must be (term, textbook, plain, code): {r!r}"
        assert r[0] not in seen, f"{key}: duplicate term {r[0]!r}"
        seen.add(r[0])
    CONCEPTS[key] = {
        "name": name,
        "what": what,
        "deep": deep,
        "java": note,          # shown under the accent "How to use this set" card
        "language": JV_LANG,
        "cards": _jv_cards(rows),
        "quiz": quiz or [],
    }
    CATEGORY[key] = category
    LESSONS[key] = _jv_table(rows, intro)
    EXERCISES.setdefault(key, [])   # reference only — no fill-in-the-blank drills


_STUDY_NOTE = (
    "Every row gives you **two** explanations: the **textbook definition** (what "
    "you'd write on an exam) and a **plain-English** line (what it actually means "
    "when you're staring at code). Skim the glossary, then hit **🎴 Study cards** "
    "to drill them with spaced repetition, and **❓ Check yourself** at the bottom."
)

CAT_CORE = "JV: Language Core"
CAT_OOP = "JV: OOP"
CAT_MOD = "JV: Modifiers"
CAT_TYPES = "JV: Types"
CAT_COLL = "JV: Collections"
CAT_GEN = "JV: Generics"
CAT_EXC = "JV: Exceptions"
CAT_CONC = "JV: Concurrency"
CAT_FUNC = "JV: Functional"
CAT_JVM = "JV: JVM & Memory"
CAT_STR = "JV: Strings"
CAT_IO = "JV: I/O"
CAT_TOOL = "JV: Tooling"
CAT_MODERN = "JV: Modern Java"


# ===========================================================================
# 1) LANGUAGE CORE — keywords & syntax
# ===========================================================================
_jv(
    "jv_keywords",
    "Keywords & Syntax",
    CAT_CORE,
    "The reserved words and punctuation every Java program is built from.",
    "Java has ~50 reserved keywords you can't use as names. This set covers the "
    "everyday ones — declaring things, branching, looping, and the tiny syntax "
    "rules (semicolons, blocks, the entry point) that make a file compile.",
    _STUDY_NOTE,
    [
        ("class", "A blueprint that groups fields and methods into a type.", "The box you put your code in — nothing runs outside a class.", "class Dog { }"),
        ("void", "A return type meaning the method hands nothing back.", "This method does stuff but gives you nothing in return.", "void print() { }"),
        ("return", "Exits a method, optionally handing a value back.", "Stop here and give this value back to whoever called me.", "return x + 1;"),
        ("if / else", "Runs a block only when a boolean condition holds.", "A fork in the road: go this way, otherwise that way.", "if (x > 0) { } else { }"),
        ("for", "A loop with init, condition, and step in one line.", "Repeat this a known number of times.", "for (int i = 0; i < n; i++) { }"),
        ("while", "A loop that repeats while a condition stays true.", "Keep going until this stops being true.", "while (running) { }"),
        ("do", "A loop that runs the body once before checking.", "Do it at least once, then decide whether to repeat.", "do { } while (x < 5);"),
        ("switch", "Branches to a case matching a value.", "A cleaner tower of if/else for one variable.", "switch (day) { case 1: break; }"),
        ("break", "Immediately exits the nearest loop or switch.", "Bail out of this loop right now.", "if (found) break;"),
        ("continue", "Skips to the next iteration of a loop.", "Skip the rest of this round and start the next.", "if (x < 0) continue;"),
        ("new", "Allocates an object and calls its constructor.", "Make me a fresh one of these.", "Dog d = new Dog();"),
        ("this", "A reference to the current object.", "Me — the object whose method is running.", "this.name = name;"),
        ("super", "A reference to the parent class's members.", "The version of me that my parent defined.", "super.toString();"),
        ("instanceof", "Tests whether an object is of a given type.", "Is this thing actually one of those?", "if (o instanceof Dog) { }"),
        ("null", "A reference that points at no object.", "A box labeled 'nothing here'.", "String s = null;"),
        ("true / false", "The two boolean literals.", "Yes and no, the only two values a boolean holds.", "boolean ok = true;"),
        ("package", "A namespace that groups related classes.", "The folder your class lives in, spelled with dots.", "package com.app.util;"),
        ("import", "Brings a type into scope by short name.", "Tells Java where to find a class so you can drop the long name.", "import java.util.List;"),
        ("main", "The entry-point method the JVM calls first.", "Where the program starts running.", "public static void main(String[] a) { }"),
        ("System.out.println", "Prints a line to standard output.", "The classic 'print something to the console'.", "System.out.println(x);"),
        ("assert", "Checks an invariant; throws if it's false (when enabled).", "A sanity check that only fires when you turn asserts on.", "assert n > 0;"),
        ("var", "Infers a local variable's type from its initializer.", "Let the compiler figure out the type for me.", "var list = new ArrayList<String>();"),
        ("yield", "Returns a value from a switch expression arm.", "The switch-expression version of return.", "case 1 -> { yield 10; }"),
        ("enum", "A type whose values are a fixed named set.", "A type that can only be one of these few things.", "enum Color { RED, GREEN }"),
    ],
    [
        _jvq("Which keyword allocates a new object and runs its constructor?",
             ["new", "class", "this", "void"], 0,
             "`new` reserves heap space and invokes the constructor, handing back a reference."),
        _jvq("What does `void` as a return type mean?",
             ["The method returns nothing", "The method returns null", "The method returns 0", "The method never ends"], 0,
             "`void` means the method produces no return value at all — you can't assign its result."),
        _jvq("`continue` inside a loop will…",
             ["skip to the next iteration", "exit the loop entirely", "restart the whole loop", "throw an exception"], 0,
             "`continue` skips the rest of the current iteration; `break` is what exits the loop."),
        _jvq("Which is TRUE about `var`?",
             ["The type is inferred from the initializer", "It makes the variable dynamically typed", "It works for fields too", "It means the value can't change"], 0,
             "`var` is still statically typed — the compiler infers the type; it only works for local variables with an initializer."),
        _jvq("`instanceof` evaluates to…",
             ["a boolean", "the object's class name", "an int", "the object itself"], 0,
             "`o instanceof Dog` is a boolean test of whether `o`'s runtime type is Dog (or a subtype)."),
    ],
)


# ===========================================================================
# 2) OOP CONCEPTS
# ===========================================================================
_jv(
    "jv_oop",
    "OOP Concepts",
    CAT_OOP,
    "The object-oriented ideas Java is built around: classes, inheritance, polymorphism.",
    "Java is object-oriented to the core. These are the terms interviewers love: "
    "the four pillars (encapsulation, inheritance, polymorphism, abstraction) plus "
    "the machinery — constructors, overriding, interfaces — that makes them work.",
    _STUDY_NOTE,
    [
        ("object", "A concrete instance of a class held in memory.", "An actual thing built from the blueprint.", "Dog d = new Dog();"),
        ("instance", "One specific object created from a class.", "A single copy made from the mold.", "new Dog()"),
        ("field", "A variable that belongs to an object or class.", "A thing an object remembers.", "int age;"),
        ("method", "A named block of behavior on a class.", "A thing an object can do.", "void bark() { }"),
        ("constructor", "A special method that initializes a new object.", "The setup routine that runs when you say `new`.", "Dog(String n) { name = n; }"),
        ("encapsulation", "Bundling data with the methods that guard it.", "Hide the wires; expose safe buttons.", "private int bal;"),
        ("inheritance", "A class acquiring another class's members.", "Get a parent's stuff for free, then add your own.", "class Dog extends Animal { }"),
        ("polymorphism", "One reference behaving as many runtime types.", "Same call, different behavior depending on the real object.", "Animal a = new Dog();"),
        ("abstraction", "Exposing behavior while hiding implementation.", "You use the 'what' without caring about the 'how'.", "interface Shape { }"),
        ("override", "Replacing an inherited method's behavior.", "Redo a parent's method your own way.", "@Override String toString() { }"),
        ("overload", "Same method name, different parameter lists.", "One name, several versions for different inputs.", "add(int a); add(double a);"),
        ("interface", "A contract of methods a class promises to provide.", "A to-do list a class agrees to complete.", "interface Runnable { void run(); }"),
        ("abstract class", "A partial class that can't be instantiated.", "A half-built blueprint others must finish.", "abstract class Shape { }"),
        ("subclass", "A class that extends another.", "The child that inherits.", "class Cat extends Animal { }"),
        ("superclass", "The class being extended.", "The parent being inherited from.", "class Animal { }"),
        ("is-a relationship", "A subtype genuinely being its supertype.", "A Dog IS-A Animal — inheritance is right.", "Dog extends Animal"),
        ("has-a relationship", "One object holding another (composition).", "A Car HAS-A Engine — a field, not inheritance.", "class Car { Engine e; }"),
        ("composition", "Building behavior by holding other objects.", "Assemble from parts instead of inheriting.", "class Car { Engine e; }"),
        ("getter / setter", "Accessor methods for a private field.", "The safe read/write buttons around hidden data.", "int getAge() { return age; }"),
        ("this()", "A constructor calling another constructor.", "Reuse another constructor instead of repeating setup.", "Dog() { this(\"Rex\"); }"),
        ("static member", "A field or method owned by the class, not instances.", "Shared by everyone; belongs to the class itself.", "static int count;"),
        ("upcasting", "Treating an object as its supertype.", "See a Dog as just an Animal — always safe.", "Animal a = new Dog();"),
        ("downcasting", "Treating a supertype reference as a subtype.", "Insist this Animal is really a Dog — can fail.", "Dog d = (Dog) a;"),
        ("object identity", "Whether two references are the same object.", "Same object vs. merely equal — `==` vs `equals`.", "a == b"),
    ],
    [
        _jvq("Which pillar is about hiding internal data behind methods?",
             ["Encapsulation", "Inheritance", "Polymorphism", "Abstraction"], 0,
             "Encapsulation bundles data with the methods that control access, typically via private fields + getters/setters."),
        _jvq("`Animal a = new Dog();` then `a.speak()` runs Dog's version. This is…",
             ["Polymorphism", "Overloading", "Encapsulation", "Composition"], 0,
             "The call is resolved at runtime to the actual object's type — runtime polymorphism via overriding."),
        _jvq("Overloading differs from overriding because overloading…",
             ["changes the parameter list, same name", "replaces a parent method", "requires inheritance", "only works on constructors"], 0,
             "Overloading = same name, different parameters, resolved at compile time. Overriding replaces an inherited method."),
        _jvq("Which describes a HAS-A relationship?",
             ["A Car holds an Engine field", "A Cat extends Animal", "A Dog implements Runnable", "A Shape is abstract"], 0,
             "HAS-A is composition (holding another object as a field). IS-A is inheritance."),
        _jvq("Why can't you write `new Shape()` if `Shape` is an abstract class?",
             ["Abstract classes can't be instantiated", "It has no fields", "It's final", "It's private"], 0,
             "An abstract class may have unfinished (abstract) methods, so Java forbids instantiating it directly."),
    ],
)


# ===========================================================================
# 3) MODIFIERS & ACCESS
# ===========================================================================
_jv(
    "jv_modifiers",
    "Modifiers & Access",
    CAT_MOD,
    "The keywords that control visibility, mutability, and where members live.",
    "Modifiers are the little words in front of a declaration that change its "
    "rules: who can see it (access), whether it can change (final), whether it "
    "belongs to the class or the instance (static), and more.",
    _STUDY_NOTE,
    [
        ("public", "Visible to all other classes.", "Anyone, anywhere can use this.", "public int x;"),
        ("private", "Visible only inside the declaring class.", "Nobody outside this class gets to touch it.", "private int x;"),
        ("protected", "Visible to the package and to subclasses.", "Family and neighbors only.", "protected int x;"),
        ("package-private", "Default access: visible within the same package.", "No keyword = only classes in the same folder.", "int x;"),
        ("static", "Belongs to the class, shared across instances.", "One copy for everyone, not per-object.", "static int count;"),
        ("final (variable)", "A value that can be assigned only once.", "Set it once, then it's locked.", "final int MAX = 10;"),
        ("final (method)", "A method that can't be overridden.", "Subclasses can't change this behavior.", "final void run() { }"),
        ("final (class)", "A class that can't be extended.", "Nobody can inherit from this.", "final class Math { }"),
        ("abstract", "Declared without an implementation.", "A promise to be filled in by a subclass.", "abstract void draw();"),
        ("synchronized", "Allows only one thread in at a time.", "A one-at-a-time door for threads.", "synchronized void inc() { }"),
        ("volatile", "Forces reads/writes to go to main memory.", "Always see the freshest value across threads.", "volatile boolean flag;"),
        ("transient", "Excludes a field from serialization.", "Don't save this one to disk.", "transient String cache;"),
        ("native", "Implemented in non-Java (C/C++) code.", "The body lives outside Java, in native code.", "native void hardware();"),
        ("strictfp", "Forces portable IEEE floating-point math.", "Make float math identical on every machine.", "strictfp class Calc { }"),
        ("default (method)", "An interface method with a body.", "A free implementation an interface hands you.", "default void hi() { }"),
        ("static import", "Imports static members for unqualified use.", "Use `sqrt` instead of `Math.sqrt`.", "import static java.lang.Math.*;"),
        ("sealed", "Restricts which classes may extend it.", "Only these specific classes may inherit.", "sealed interface Shape permits Circle { }"),
        ("non-sealed", "Reopens a sealed hierarchy for extension.", "Undo the 'permits' lock for this branch.", "non-sealed class Circle { }"),
        ("record component", "An immutable field declared in a record header.", "A field a record generates for you automatically.", "record Point(int x, int y) { }"),
        ("access modifier order", "Convention: modifiers before type.", "The habitual `public static final` word order.", "public static final int N = 1;"),
    ],
    [
        _jvq("Which access level is the DEFAULT when you write no modifier?",
             ["Package-private", "public", "private", "protected"], 0,
             "No keyword means package-private: visible only to classes in the same package."),
        _jvq("`volatile` on a field mainly guarantees…",
             ["visibility of the latest value across threads", "that only one thread runs the method", "the field can't change", "the field isn't serialized"], 0,
             "`volatile` ensures reads/writes hit main memory so threads see the newest value; it does NOT make compound actions atomic."),
        _jvq("What does `final` on a method do?",
             ["Prevents subclasses from overriding it", "Prevents it from returning", "Makes it static", "Makes it thread-safe"], 0,
             "A final method is locked — no subclass may override it. (final class = can't be extended; final variable = can't be reassigned.)"),
        _jvq("`transient` affects a field during…",
             ["serialization", "garbage collection", "compilation", "method dispatch"], 0,
             "A transient field is skipped when the object is serialized, so it isn't written to the stream."),
        _jvq("A `static` field is best described as…",
             ["one shared copy owned by the class", "a copy per object", "always final", "thread-safe by default"], 0,
             "Static members belong to the class itself, so all instances share the single copy."),
    ],
)


# ===========================================================================
# 4) TYPES & PRIMITIVES
# ===========================================================================
_jv(
    "jv_types",
    "Types & Primitives",
    CAT_TYPES,
    "The built-in value types, their wrappers, and how conversion works.",
    "Java has eight primitive types (raw values) and matching wrapper classes "
    "(objects). Knowing the sizes, the boxing rules, and how casting/promotion "
    "work saves you from overflow and precision bugs.",
    _STUDY_NOTE,
    [
        ("int", "A 32-bit signed integer.", "The default whole number, ±2 billion.", "int n = 42;"),
        ("long", "A 64-bit signed integer.", "A whole number when int isn't big enough.", "long big = 9_000_000_000L;"),
        ("short", "A 16-bit signed integer.", "A small whole number, rarely used.", "short s = 100;"),
        ("byte", "An 8-bit signed integer (-128..127).", "The tiniest integer, used for raw bytes.", "byte b = 7;"),
        ("double", "A 64-bit floating-point number.", "The default decimal number.", "double pi = 3.14;"),
        ("float", "A 32-bit floating-point number.", "A smaller, less precise decimal.", "float f = 1.5f;"),
        ("char", "A 16-bit Unicode code unit.", "A single character, stored as a number.", "char c = 'A';"),
        ("boolean", "A true/false value.", "A yes/no switch.", "boolean ok = true;"),
        ("wrapper class", "An object form of a primitive (Integer, Double…).", "A primitive wearing an object costume.", "Integer i = 42;"),
        ("autoboxing", "Automatic primitive-to-wrapper conversion.", "Java quietly puts the int into an Integer.", "Integer i = 5;"),
        ("unboxing", "Automatic wrapper-to-primitive conversion.", "Java quietly takes the int back out.", "int x = i;"),
        ("widening", "Implicit conversion to a bigger type.", "int fits in a long, so no cast needed.", "long l = 5;"),
        ("narrowing", "Explicit conversion to a smaller type.", "Force a long into an int — may lose bits.", "int x = (int) 5L;"),
        ("cast", "Explicitly converting between types.", "Telling the compiler 'trust me, treat it as this'.", "double d = (double) n;"),
        ("overflow", "A value wrapping past its type's max.", "Add 1 to the biggest int and it flips negative.", "Integer.MAX_VALUE + 1"),
        ("literal", "A fixed value written directly in code.", "A hard-coded value like 42 or \"hi\".", "int n = 0xFF;"),
        ("type promotion", "Small types promoted to int in arithmetic.", "byte + byte is actually computed as int.", "int r = b1 + b2;"),
        ("BigInteger / BigDecimal", "Arbitrary-precision number classes.", "For numbers too big or money too exact for double.", "new BigDecimal(\"0.1\")"),
    ],
    [
        _jvq("Which primitive is the DEFAULT type of an integer literal like `42`?",
             ["int", "long", "short", "byte"], 0,
             "An un-suffixed integer literal is an `int`; append `L` for a `long`."),
        _jvq("Converting `Integer` to `int` automatically is called…",
             ["unboxing", "autoboxing", "widening", "casting"], 0,
             "Wrapper → primitive is unboxing; primitive → wrapper is autoboxing."),
        _jvq("Which conversion REQUIRES an explicit cast?",
             ["long to int (narrowing)", "int to long (widening)", "int to double", "byte to int"], 0,
             "Narrowing (bigger → smaller) can lose data, so Java forces an explicit cast."),
        _jvq("`Integer.MAX_VALUE + 1` produces…",
             ["a large negative number (overflow)", "a compile error", "an exception", "0"], 0,
             "Integer arithmetic wraps around silently; exceeding MAX_VALUE flips to the most negative int."),
        _jvq("For exact monetary math you should use…",
             ["BigDecimal", "double", "float", "long only"], 0,
             "`double`/`float` are binary approximations; `BigDecimal` stores exact decimal values."),
    ],
)


# ===========================================================================
# 5) COLLECTIONS & DATA STRUCTURES
# ===========================================================================
_jv(
    "jv_collections",
    "Collections & Data Structures",
    CAT_COLL,
    "The java.util toolkit: lists, maps, sets, queues, and their trade-offs.",
    "The Collections Framework is the daily bread of Java. Knowing which "
    "structure gives O(1) lookup, which keeps order, and which allows duplicates "
    "is exactly what interviews and real code demand.",
    _STUDY_NOTE,
    [
        ("Collection", "The root interface for groups of elements.", "The umbrella term for 'a bunch of things'.", "Collection<String> c;"),
        ("List", "An ordered collection allowing duplicates.", "A sequence you index into, like a row of boxes.", "List<Integer> l;"),
        ("ArrayList", "A List backed by a resizable array.", "The default list — fast random access.", "new ArrayList<>()"),
        ("LinkedList", "A List/Deque backed by a doubly-linked list.", "Fast add/remove at the ends, slow indexing.", "new LinkedList<>()"),
        ("Set", "A collection with no duplicate elements.", "A bag that ignores repeats.", "Set<String> s;"),
        ("HashSet", "A Set backed by a hash table.", "Unordered set with O(1) contains.", "new HashSet<>()"),
        ("LinkedHashSet", "A HashSet that remembers insertion order.", "A set that keeps things in the order you added them.", "new LinkedHashSet<>()"),
        ("TreeSet", "A Set kept in sorted order.", "A set that's always sorted for you.", "new TreeSet<>()"),
        ("Map", "A collection of key-to-value pairs.", "A dictionary: look up a value by its key.", "Map<String,Integer> m;"),
        ("HashMap", "A Map backed by a hash table.", "The default map — O(1) get/put, no order.", "new HashMap<>()"),
        ("LinkedHashMap", "A HashMap that preserves insertion order.", "A map that iterates in add order.", "new LinkedHashMap<>()"),
        ("TreeMap", "A Map sorted by key.", "A map that's always ordered by key.", "new TreeMap<>()"),
        ("Queue", "A collection processed front-to-back (FIFO).", "A line: first in, first out.", "Queue<Integer> q;"),
        ("Deque", "A double-ended queue.", "A line you can push/pop from both ends.", "Deque<Integer> d;"),
        ("ArrayDeque", "A fast resizable-array Deque.", "The go-to stack/queue — beats Stack and LinkedList.", "new ArrayDeque<>()"),
        ("Stack", "A LIFO structure (legacy class).", "Last in, first out — but prefer ArrayDeque.", "new ArrayDeque<>()"),
        ("PriorityQueue", "A queue ordered by priority (a heap).", "Always hands you the smallest (or largest) next.", "new PriorityQueue<>()"),
        ("Iterator", "An object to walk a collection one item at a time.", "A cursor that says 'next?' and 'got more?'.", "Iterator<T> it = c.iterator();"),
        ("Iterable", "Anything a for-each loop can traverse.", "The 'you can loop over me' contract.", "for (T x : list) { }"),
        ("Comparable", "A type's natural ordering via compareTo.", "'Here's how to sort me by default.'", "class N implements Comparable<N> { }"),
        ("Comparator", "An external ordering strategy.", "A custom 'sort by this instead' rule.", "Comparator.comparingInt(x -> x)"),
        ("Collections", "Static helpers for collections (sort, etc.).", "The utility belt for lists and sets.", "Collections.sort(list);"),
        ("Arrays", "Static helpers for arrays.", "The utility belt for raw arrays.", "Arrays.sort(arr);"),
        ("entrySet", "A Map's set of key-value pairs.", "The way to loop over both keys and values.", "for (var e : m.entrySet()) { }"),
        ("keySet / values", "A Map's keys / values as collections.", "Just the keys, or just the values.", "m.keySet()"),
        ("load factor", "HashMap's fill ratio before it resizes.", "How full the table gets before it grows (0.75).", "new HashMap<>(16, 0.75f)"),
        ("capacity", "The number of buckets a hash table has.", "How many slots the map allocated under the hood.", "new HashMap<>(64)"),
        ("fail-fast", "Iterators that throw on concurrent modification.", "Change a list mid-loop and it slaps your hand.", "ConcurrentModificationException"),
    ],
    [
        _jvq("Which structure gives average O(1) lookup by key with NO ordering?",
             ["HashMap", "TreeMap", "LinkedList", "ArrayList"], 0,
             "HashMap hashes keys to buckets for O(1) average get/put but makes no ordering promise."),
        _jvq("You need elements kept in sorted order automatically. Use…",
             ["TreeSet", "HashSet", "ArrayList", "ArrayDeque"], 0,
             "TreeSet (a red-black tree) keeps elements sorted; HashSet is unordered."),
        _jvq("The modern recommended class for a stack is…",
             ["ArrayDeque", "Stack", "LinkedList", "PriorityQueue"], 0,
             "`ArrayDeque` is faster and cleaner than the legacy synchronized `Stack` class."),
        _jvq("A PriorityQueue always removes…",
             ["the highest-priority (e.g. smallest) element", "the most recently added", "the oldest added", "a random element"], 0,
             "A PriorityQueue is a heap: `poll()` returns the head according to the comparator (smallest by default)."),
        _jvq("`ConcurrentModificationException` typically means…",
             ["a collection was structurally modified during iteration", "two threads deadlocked", "the map ran out of capacity", "a null key was used"], 0,
             "Fail-fast iterators throw it when the backing collection is modified while you're looping over it."),
        _jvq("To iterate keys AND values of a Map efficiently, loop over…",
             ["entrySet()", "keySet() then get()", "values()", "the map directly"], 0,
             "`entrySet()` gives both key and value per entry, avoiding a second lookup per key."),
    ],
)


# ===========================================================================
# 6) GENERICS & TYPE SYSTEM
# ===========================================================================
_jv(
    "jv_generics",
    "Generics & Type System",
    CAT_GEN,
    "Type parameters, wildcards, and the erasure that powers them.",
    "Generics let one class or method work over many types with compile-time "
    "safety. The catch is type erasure — generics vanish at runtime — which "
    "explains most of the weird rules and error messages.",
    _STUDY_NOTE,
    [
        ("generic type", "A class/interface parameterized by a type.", "A container that works for any type you plug in.", "class Box<T> { }"),
        ("type parameter", "The placeholder like <T> in a declaration.", "The blank you fill with a real type later.", "class Box<T> { T val; }"),
        ("type argument", "The concrete type you supply.", "The real type you put in the blank.", "Box<String> b;"),
        ("bounded type", "A parameter limited by extends.", "'Any type, as long as it's a Number.'", "class Box<T extends Number> { }"),
        ("wildcard", "An unknown type written as ?.", "'Some type, I don't care which.'", "List<?> anything;"),
        ("upper bound", "`? extends T` — T or a subtype.", "Reading side: producers of T.", "List<? extends Number> nums;"),
        ("lower bound", "`? super T` — T or a supertype.", "Writing side: consumers of T.", "List<? super Integer> sink;"),
        ("type erasure", "Generics removed at compile time.", "At runtime a List<String> is just a List.", "List<String> -> List"),
        ("raw type", "A generic used without a type argument.", "The old, unsafe pre-generics form.", "List l = new ArrayList();"),
        ("generic method", "A method with its own type parameter.", "A method that's generic on its own, apart from the class.", "<T> T first(List<T> xs) { }"),
        ("PECS", "Producer-Extends, Consumer-Super rule.", "Use extends to read, super to write.", "List<? extends T> src;"),
        ("diamond operator", "`<>` that infers type arguments.", "Skip repeating the type on the right side.", "List<String> l = new ArrayList<>();"),
        ("unchecked warning", "A compiler warning about lost generic safety.", "'I can't prove this cast is safe' from erasure.", "@SuppressWarnings(\"unchecked\")"),
        ("recursive bound", "A type bounded by itself (F-bound).", "The trick behind Comparable<T>.", "T extends Comparable<T>"),
    ],
    [
        _jvq("What happens to generic type info at runtime?",
             ["It's erased", "It's fully preserved via reflection", "It's stored in each object", "It's turned into Object always"], 0,
             "Type erasure removes generic parameters at compile time, so `List<String>` and `List<Integer>` share one runtime class."),
        _jvq("PECS says: use `? extends T` when you want to…",
             ["read (produce) values out", "write (consume) values in", "avoid casts", "compare values"], 0,
             "Producer-Extends: an `? extends T` source produces Ts you read; `? super T` consumes Ts you write."),
        _jvq("The diamond operator `<>` lets you…",
             ["omit repeating the type arguments on the right", "create raw types", "cast safely", "bound a parameter"], 0,
             "`new ArrayList<>()` infers the type from the variable declaration, avoiding repetition."),
        _jvq("A `raw type` like `List l = new ArrayList();` is discouraged because…",
             ["it loses compile-time type checking", "it won't compile", "it's slower at runtime", "it can't be iterated"], 0,
             "Raw types bypass generic checks, reintroducing the ClassCastExceptions generics were meant to prevent."),
        _jvq("`<T extends Number>` means T can be…",
             ["Number or any subclass of it", "any type", "only Number", "any superclass of Number"], 0,
             "An upper bound restricts T to Number and its subtypes (Integer, Double, …)."),
    ],
)


# ===========================================================================
# 7) EXCEPTIONS & ERRORS
# ===========================================================================
_jv(
    "jv_exceptions",
    "Exceptions & Errors",
    CAT_EXC,
    "How Java signals, propagates, and handles things going wrong.",
    "Exceptions are Java's structured way to say 'something broke.' The key "
    "distinctions — checked vs unchecked, Exception vs Error, and the try/catch/"
    "finally flow — come up constantly in code review and interviews.",
    _STUDY_NOTE,
    [
        ("exception", "An object signaling an abnormal event.", "A thrown 'something went wrong' package.", "throw new IOException();"),
        ("Throwable", "The root of all errors and exceptions.", "The ancestor of everything you can throw.", "class Throwable { }"),
        ("Error", "A serious problem apps shouldn't catch.", "The JVM is in trouble — don't try to recover.", "OutOfMemoryError"),
        ("checked exception", "Must be declared or caught (compile-time).", "The compiler forces you to deal with it.", "throws IOException"),
        ("unchecked exception", "A RuntimeException; not enforced.", "Bugs you don't have to declare — usually programmer error.", "NullPointerException"),
        ("RuntimeException", "The base of unchecked exceptions.", "The 'your code has a bug' family.", "class RuntimeException { }"),
        ("try", "Wraps code that might throw.", "The 'attempt this' block.", "try { risky(); }"),
        ("catch", "Handles a thrown exception.", "The 'if it breaks, do this' block.", "catch (IOException e) { }"),
        ("finally", "Runs whether or not an exception occurred.", "Cleanup that always happens.", "finally { file.close(); }"),
        ("throw", "Raises an exception now.", "Fire the alarm right here.", "throw new IllegalArgumentException();"),
        ("throws", "Declares exceptions a method may raise.", "A warning label on the method signature.", "void read() throws IOException"),
        ("stack trace", "The call chain at the point of failure.", "The breadcrumb trail of who called what.", "e.printStackTrace();"),
        ("NullPointerException", "Dereferencing a null reference.", "You used something that was empty.", "s.length() // s == null"),
        ("try-with-resources", "Auto-closes resources on exit.", "Opens and guarantees closing for you.", "try (var f = open()) { }"),
        ("custom exception", "A user-defined Exception subclass.", "Your own named error type.", "class BankError extends Exception { }"),
        ("exception chaining", "Wrapping one exception in another.", "'This failed because of that' with the cause kept.", "new X(\"msg\", cause)"),
    ],
    [
        _jvq("A CHECKED exception is one that…",
             ["must be declared with `throws` or caught", "extends RuntimeException", "the JVM throws only", "can never be caught"], 0,
             "Checked exceptions are enforced by the compiler; unchecked (RuntimeException) ones are not."),
        _jvq("The `finally` block runs…",
             ["whether or not an exception was thrown", "only when an exception is thrown", "only when none is thrown", "only if you call it"], 0,
             "`finally` always executes (barring JVM exit), which is why it's used for cleanup."),
        _jvq("`NullPointerException` is a…",
             ["unchecked (runtime) exception", "checked exception", "an Error", "compile error"], 0,
             "NPE extends RuntimeException, so it's unchecked — the compiler doesn't force you to handle it."),
        _jvq("You should generally NOT catch an `Error` (e.g. OutOfMemoryError) because…",
             ["it signals a serious unrecoverable JVM problem", "it's a checked exception", "it can't be caught", "it's always a bug in the JDK"], 0,
             "Errors indicate conditions the application usually can't sensibly recover from."),
        _jvq("`try-with-resources` is preferred because it…",
             ["automatically closes resources", "catches all exceptions", "retries on failure", "runs faster"], 0,
             "Any resource implementing AutoCloseable is closed automatically when the try block exits, even on exception."),
    ],
)


# ===========================================================================
# 8) CONCURRENCY & THREADS
# ===========================================================================
_jv(
    "jv_concurrency",
    "Concurrency & Threads",
    CAT_CONC,
    "Running code in parallel safely: threads, locks, and the memory model.",
    "Concurrency is where Java gets subtle. These terms — race conditions, "
    "synchronization, the happens-before relationship, thread pools — are the "
    "vocabulary you need to reason about (and survive interviews on) multi-threaded code.",
    _STUDY_NOTE,
    [
        ("thread", "An independent path of execution.", "A worker running your code in parallel.", "new Thread(task).start();"),
        ("Runnable", "A task with a run() and no result.", "A job you hand a thread to do.", "Runnable r = () -> work();"),
        ("Callable", "A task that returns a value or throws.", "Like Runnable, but it hands something back.", "Callable<Integer> c = () -> 1;"),
        ("process vs thread", "Isolated program vs shared-memory worker.", "Separate apartments vs roommates sharing a room.", "Thread t = new Thread();"),
        ("race condition", "Result depends on unlucky thread timing.", "Two threads stomp on the same data.", "count++; // not atomic"),
        ("synchronized", "A lock allowing one thread at a time.", "A one-at-a-time turnstile.", "synchronized (lock) { }"),
        ("lock", "An explicit mutual-exclusion object.", "A manual key you acquire and release.", "lock.lock(); ... lock.unlock();"),
        ("deadlock", "Threads each waiting on the other's lock.", "Two people each holding the door the other needs.", "// A holds L1 waits L2..."),
        ("atomic", "An operation that completes indivisibly.", "All-or-nothing, no thread sees it half-done.", "new AtomicInteger();"),
        ("volatile", "Guarantees visibility of a field's writes.", "Every thread sees the latest value.", "volatile boolean stop;"),
        ("happens-before", "The ordering rule making writes visible.", "The guarantee that A's result is seen by B.", "// unlock -> lock"),
        ("thread pool", "A reusable set of worker threads.", "A team you hand tasks to instead of hiring per task.", "Executors.newFixedThreadPool(4);"),
        ("ExecutorService", "Manages and schedules async tasks.", "The manager that runs your tasks for you.", "es.submit(task);"),
        ("Future", "A handle to a not-yet-ready result.", "An IOU for a value coming later.", "Future<Integer> f = es.submit(c);"),
        ("wait / notify", "Low-level thread coordination on a monitor.", "'Sleep until someone taps me.'", "obj.wait(); obj.notify();"),
        ("ConcurrentHashMap", "A thread-safe, scalable HashMap.", "A map many threads can hit at once safely.", "new ConcurrentHashMap<>()"),
        ("thread-safe", "Correct when used by many threads.", "Won't corrupt if several threads share it.", "// synchronized/immutable"),
        ("immutable", "State that can't change after creation.", "Frozen data — inherently thread-safe.", "final int x;"),
        ("CompletableFuture", "A composable async result.", "A Future you can chain .then steps onto.", "CompletableFuture.supplyAsync(f)"),
        ("daemon thread", "A background thread that won't block exit.", "A helper the JVM won't wait for on shutdown.", "t.setDaemon(true);"),
    ],
    [
        _jvq("A race condition happens when…",
             ["the result depends on thread timing over shared data", "a thread runs too slowly", "two processes share a file", "a lock is never used"], 0,
             "Race conditions arise from unsynchronized access to shared mutable state, where interleaving changes the outcome."),
        _jvq("`volatile` guarantees ______ but NOT ______.",
             ["visibility; atomicity of compound actions", "atomicity; visibility", "ordering; speed", "locking; unlocking"], 0,
             "volatile makes the latest value visible, but `count++` (read-modify-write) is still not atomic."),
        _jvq("Deadlock requires (among other conditions)…",
             ["threads holding locks while waiting for others", "a single thread", "no locks at all", "a full thread pool"], 0,
             "Classic deadlock: each thread holds one lock and waits for a lock the other holds, forming a cycle."),
        _jvq("The safest way to share a counter across threads is…",
             ["AtomicInteger", "a plain int", "a volatile int with count++", "a local variable"], 0,
             "AtomicInteger's incrementAndGet is a single atomic operation; a volatile int++ still races."),
        _jvq("A `Future` represents…",
             ["a result that may not be ready yet", "a background thread", "a lock", "a completed task only"], 0,
             "A Future is a handle to an asynchronous computation's eventual result; `get()` blocks until it's ready."),
        _jvq("Why are immutable objects inherently thread-safe?",
             ["their state can't change after construction", "they use synchronized", "they're always static", "the GC protects them"], 0,
             "If nothing can mutate the object, concurrent readers can never see an inconsistent state."),
    ],
)


# ===========================================================================
# 9) STREAMS, LAMBDAS & FUNCTIONAL
# ===========================================================================
_jv(
    "jv_streams",
    "Streams, Lambdas & Functional",
    CAT_FUNC,
    "Java's functional style: lambdas, method references, and the Stream pipeline.",
    "Since Java 8 you can process data declaratively. Lambdas, functional "
    "interfaces, and streams let you say WHAT you want (filter, map, collect) "
    "instead of writing the loop — cleaner code and a favorite interview topic.",
    _STUDY_NOTE,
    [
        ("lambda", "A concise anonymous function.", "A throwaway function with no name.", "x -> x * 2"),
        ("functional interface", "An interface with one abstract method.", "A one-method contract a lambda can fill.", "@FunctionalInterface"),
        ("method reference", "A shorthand pointing at an existing method.", "Reuse a method by name instead of a lambda.", "String::length"),
        ("Stream", "A pipeline over a sequence of elements.", "A conveyor belt you attach operations to.", "list.stream()"),
        ("filter", "Keeps elements matching a predicate.", "Throw away everything that fails the test.", ".filter(x -> x > 0)"),
        ("map", "Transforms each element.", "Turn every item into something else.", ".map(x -> x * x)"),
        ("reduce", "Combines elements into one value.", "Fold the whole stream into a single result.", ".reduce(0, Integer::sum)"),
        ("collect", "Gathers a stream into a collection.", "Pour the results into a list/set/map.", ".collect(Collectors.toList())"),
        ("forEach", "Runs an action per element.", "Do this for every item.", ".forEach(System.out::println)"),
        ("Optional", "A container that may or may not hold a value.", "A box that says 'maybe there's something here'.", "Optional<String> o;"),
        ("Predicate", "A function returning a boolean.", "A yes/no test.", "Predicate<Integer> p = x -> x > 0;"),
        ("Function", "A function from one type to another.", "An input-to-output transformer.", "Function<Integer,Integer> f;"),
        ("Consumer", "A function that takes input, returns nothing.", "Do-something-with-it, hand nothing back.", "Consumer<String> c = System.out::println;"),
        ("Supplier", "A function that produces a value.", "Give-me-one-on-demand.", "Supplier<Double> s = Math::random;"),
        ("lazy evaluation", "Intermediate ops run only on terminal.", "Nothing happens until you ask for the result.", ".filter(...).map(...).count()"),
        ("intermediate operation", "A stream op returning a new stream.", "A step that sets up more steps.", ".map(f)"),
        ("terminal operation", "A stream op producing a result/side effect.", "The step that actually runs the pipeline.", ".collect(...)"),
        ("Collectors", "Factory of reduction recipes for collect.", "Prebuilt ways to gather stream results.", "Collectors.groupingBy(f)"),
        ("parallelStream", "A stream that splits work across cores.", "The same pipeline, run on many threads.", "list.parallelStream()"),
        ("flatMap", "Maps then flattens nested streams.", "Turn a list of lists into one flat stream.", ".flatMap(List::stream)"),
    ],
    [
        _jvq("A lambda in Java can be assigned to…",
             ["a functional interface (one abstract method)", "any interface", "any class", "only Runnable"], 0,
             "Lambdas target functional interfaces — interfaces with exactly one abstract method (SAM)."),
        _jvq("Which is a TERMINAL stream operation?",
             ["collect", "filter", "map", "sorted"], 0,
             "`collect` produces a result and triggers the pipeline; filter/map/sorted are intermediate and lazy."),
        _jvq("Streams are LAZY, meaning…",
             ["intermediate ops don't run until a terminal op", "they run in the background", "they cache results", "they're slower"], 0,
             "Nothing is computed until a terminal operation pulls elements through the pipeline."),
        _jvq("`Optional` exists mainly to…",
             ["represent a possibly-absent value explicitly", "make code faster", "replace all nulls at runtime", "hold multiple values"], 0,
             "Optional forces callers to consider the empty case instead of silently hitting a NullPointerException."),
        _jvq("`String::length` is an example of a…",
             ["method reference", "lambda with parameters", "constructor", "field access"], 0,
             "It's a method reference — shorthand for `s -> s.length()`."),
        _jvq("`flatMap` differs from `map` because it…",
             ["flattens nested streams into one", "filters elements", "sorts elements", "runs in parallel"], 0,
             "map produces a stream of streams for nested data; flatMap merges them into a single stream."),
    ],
)


# ===========================================================================
# 10) JVM & MEMORY
# ===========================================================================
_jv(
    "jv_jvm",
    "The JVM & Memory",
    CAT_JVM,
    "How your code compiles, loads, runs, and gets garbage-collected.",
    "'Java' is a language AND a virtual machine. Understanding bytecode, the "
    "heap/stack split, class loading, and garbage collection explains performance, "
    "'why is it null', and the difference between the JDK, JRE, and JVM.",
    _STUDY_NOTE,
    [
        ("JVM", "The virtual machine that runs bytecode.", "The engine that actually runs Java.", "java Main"),
        ("JRE", "JVM plus core libraries to run apps.", "Everything needed to RUN Java (not build it).", "// runtime only"),
        ("JDK", "JRE plus compiler and dev tools.", "Everything to BUILD and run Java.", "javac Main.java"),
        ("bytecode", "The .class instructions the JVM executes.", "Half-compiled code the JVM understands.", "Main.class"),
        ("javac", "The Java source-to-bytecode compiler.", "Turns your .java into .class.", "javac Main.java"),
        ("JIT compiler", "Compiles hot bytecode to native code.", "Speeds up code that runs a lot.", "// HotSpot JIT"),
        ("class loader", "Loads .class files into the JVM.", "The part that finds and reads your classes.", "getClass().getClassLoader()"),
        ("heap", "Memory where objects live.", "The big shared pool for `new` objects.", "new Object()"),
        ("stack", "Per-thread memory for calls and locals.", "Each thread's scratchpad of method frames.", "int local = 1;"),
        ("stack frame", "One method call's slice of the stack.", "A method's private workspace while it runs.", "// pushed per call"),
        ("garbage collection", "Automatic reclaiming of unreachable objects.", "Java cleans up memory you stopped using.", "System.gc(); // hint"),
        ("reachability", "Whether an object is still referenced.", "Can anything still find this object?", "obj = null; // now unreachable"),
        ("memory leak", "Holding references you no longer need.", "Java can't free it because you still point at it.", "cache.put(k, v); // never removed"),
        ("StackOverflowError", "The call stack grew too deep.", "Runaway recursion filled the stack.", "void f() { f(); }"),
        ("OutOfMemoryError", "The heap couldn't fit more objects.", "You ran out of room for new objects.", "new int[Integer.MAX_VALUE];"),
        ("generational GC", "GC split into young and old regions.", "Most objects die young, so scan those first.", "// young/old gen"),
        ("metaspace", "Native memory holding class metadata.", "Where class definitions live (post-PermGen).", "-XX:MaxMetaspaceSize"),
        ("just-in-time (JIT)", "Runtime native compilation of bytecode.", "Compile-while-running for speed.", "// warm-up then fast"),
        ("classpath", "Where the JVM looks for classes.", "The list of folders/jars Java searches.", "java -cp lib.jar Main"),
        ("finalize (deprecated)", "An old pre-GC callback, now removed.", "A cleanup hook you should never rely on.", "// use try-with-resources"),
    ],
    [
        _jvq("Objects created with `new` live on the…",
             ["heap", "stack", "classpath", "metaspace"], 0,
             "Objects go on the shared heap; local variables and call frames live on each thread's stack."),
        _jvq("The difference between the JDK and the JRE is that the JDK also includes…",
             ["the compiler and dev tools", "the JVM", "the heap", "garbage collection"], 0,
             "JRE = run Java; JDK = JRE + `javac` and tools to build it."),
        _jvq("Deep infinite recursion typically causes…",
             ["StackOverflowError", "OutOfMemoryError", "NullPointerException", "a deadlock"], 0,
             "Each call adds a stack frame; too many exhausts the thread's stack → StackOverflowError."),
        _jvq("A memory leak in Java usually means…",
             ["you still hold references to objects you don't need", "the GC is disabled", "the heap is too small", "you forgot to call free()"], 0,
             "The GC only frees unreachable objects; lingering references (e.g. in a growing cache) keep them alive."),
        _jvq("Bytecode (`.class`) is…",
             ["portable instructions the JVM executes", "native machine code", "the Java source", "a compressed jar"], 0,
             "`javac` produces platform-independent bytecode; the JVM (optionally JIT-compiling) runs it."),
        _jvq("Generational GC is based on the observation that…",
             ["most objects die young", "old objects are largest", "the stack fills first", "threads share the heap"], 0,
             "The weak generational hypothesis: most objects become garbage quickly, so the young generation is collected often and cheaply."),
    ],
)


# ===========================================================================
# 11) STRINGS & TEXT
# ===========================================================================
_jv(
    "jv_strings",
    "Strings & Text",
    CAT_STR,
    "How Java represents text, and why strings are immutable.",
    "Strings feel simple but hide sharp edges: immutability, the string pool, "
    "`==` vs `equals`, and when to reach for StringBuilder. These come up in "
    "almost every interview and every performance review.",
    _STUDY_NOTE,
    [
        ("String", "An immutable sequence of characters.", "Text you can read but never change in place.", "String s = \"hi\";"),
        ("immutable", "Cannot be changed after creation.", "Every 'edit' actually makes a new string.", "s = s + \"!\";"),
        ("string pool", "A cache of interned string literals.", "Java reuses identical literals to save memory.", "\"a\" == \"a\" // true"),
        ("intern", "Puts a string into the shared pool.", "Force this string to be the shared copy.", "s.intern()"),
        ("StringBuilder", "A mutable, efficient string buffer.", "The right way to build strings in a loop.", "new StringBuilder()"),
        ("StringBuffer", "A thread-safe StringBuilder.", "Same, but synchronized (rarely needed).", "new StringBuffer()"),
        ("== vs equals", "Reference identity vs content equality.", "Same object vs same text.", "s.equals(t)"),
        ("charAt", "Returns the char at an index.", "Grab one character by position.", "s.charAt(0)"),
        ("substring", "Extracts part of a string.", "Snip out a slice of text.", "s.substring(1, 3)"),
        ("split", "Breaks a string on a regex.", "Chop text into pieces.", "s.split(\",\")"),
        ("format", "Builds a string from a template.", "printf-style string assembly.", "String.format(\"%d\", n)"),
        ("char", "A single 16-bit code unit.", "One character, stored as a number.", "'A'"),
        ("Unicode / UTF-16", "Java's internal character encoding.", "Each char is a 16-bit Unicode unit.", "\"\\u0041\""),
        ("text block", "A multi-line string literal (\"\"\").", "Paste multi-line text without \\n soup.", "String j = \"\"\"...\"\"\";"),
    ],
    [
        _jvq("Java strings are immutable, so `s = s + \"x\"`…",
             ["creates a new String object", "modifies s in place", "throws an exception", "does nothing"], 0,
             "Concatenation builds a brand-new String; the original is unchanged (which is why loops should use StringBuilder)."),
        _jvq("To compare the CONTENTS of two strings you should use…",
             ["equals()", "==", "compareTo() only", "hashCode()"], 0,
             "`==` compares references; `.equals()` compares character content."),
        _jvq("Building a string in a tight loop should use…",
             ["StringBuilder", "String + in the loop", "StringBuffer always", "char[] only"], 0,
             "Repeated `+` creates many throwaway Strings; StringBuilder mutates one buffer."),
        _jvq("The string pool means two identical string LITERALS…",
             ["may reference the same object", "are always different objects", "are mutable", "are garbage collected immediately"], 0,
             "Interned literals are cached, so `\"a\" == \"a\"` is often true — but never rely on `==` for content."),
        _jvq("`StringBuffer` differs from `StringBuilder` in that it is…",
             ["thread-safe (synchronized)", "immutable", "faster", "for chars only"], 0,
             "StringBuffer's methods are synchronized; StringBuilder isn't, making it faster for single-threaded use."),
    ],
)


# ===========================================================================
# 12) I/O, FILES & NETWORKING
# ===========================================================================
_jv(
    "jv_io",
    "I/O, Files & Networking",
    CAT_IO,
    "Reading and writing data: streams, readers, buffers, and files.",
    "Java's I/O splits into byte streams and character streams, with buffering "
    "for speed and the newer NIO/Files API for convenience. Knowing the layers "
    "keeps you from re-reading files byte by byte.",
    _STUDY_NOTE,
    [
        ("stream (I/O)", "A flow of bytes to or from a source.", "A pipe data travels through.", "InputStream in;"),
        ("InputStream", "A source of raw bytes.", "Something you read bytes out of.", "FileInputStream f;"),
        ("OutputStream", "A sink for raw bytes.", "Something you write bytes into.", "FileOutputStream f;"),
        ("Reader / Writer", "Character-oriented I/O.", "Streams that speak text, not raw bytes.", "FileReader r;"),
        ("BufferedReader", "A reader that buffers for efficiency.", "Reads in chunks so you're not hitting disk per char.", "new BufferedReader(r)"),
        ("Scanner", "Parses primitive tokens from input.", "The beginner-friendly input reader.", "new Scanner(System.in)"),
        ("System.in", "Standard input stream.", "Where typed/piped input comes from.", "new Scanner(System.in)"),
        ("File", "An abstract path to a file or dir.", "A handle to a location on disk.", "new File(\"a.txt\")"),
        ("Path / Files (NIO)", "Modern file API in java.nio.", "The cleaner, newer way to touch files.", "Files.readAllLines(path)"),
        ("serialization", "Turning an object into bytes.", "Freeze an object so you can save/send it.", "implements Serializable"),
        ("deserialization", "Rebuilding an object from bytes.", "Thaw the bytes back into an object.", "ois.readObject()"),
        ("buffer", "An in-memory staging area for data.", "A holding tank so I/O happens in bulk.", "byte[] buf = new byte[8192];"),
        ("flush", "Forces buffered data out.", "Push whatever's waiting out now.", "writer.flush();"),
        ("Socket", "An endpoint of a network connection.", "A phone line between two programs.", "new Socket(host, port)"),
    ],
    [
        _jvq("The difference between InputStream and Reader is that Reader handles…",
             ["characters (text)", "raw bytes", "only files", "network data"], 0,
             "Byte streams (InputStream/OutputStream) move raw bytes; Reader/Writer decode/encode characters."),
        _jvq("`BufferedReader` improves performance by…",
             ["reading data in larger chunks", "compressing the data", "using multiple threads", "caching the whole file"], 0,
             "Buffering reduces the number of underlying read calls by fetching bigger blocks at a time."),
        _jvq("A class must implement ______ to be serialized with ObjectOutputStream.",
             ["Serializable", "Cloneable", "Comparable", "Runnable"], 0,
             "`Serializable` is the marker interface that permits default Java serialization."),
        _jvq("`flush()` on a writer…",
             ["forces buffered output out immediately", "closes the file", "clears the file", "reads input"], 0,
             "flush pushes any buffered bytes to the destination without closing the stream."),
        _jvq("For modern file reading, the recommended API is…",
             ["java.nio.file.Files / Path", "java.io.File only", "RandomAccessFile", "Scanner only"], 0,
             "NIO's `Files`/`Path` offer concise, robust file operations over the older `java.io.File`."),
    ],
)


# ===========================================================================
# 13) BUILD, TOOLING & ECOSYSTEM
# ===========================================================================
_jv(
    "jv_tooling",
    "Build, Tooling & Ecosystem",
    CAT_TOOL,
    "The tools around the code: build systems, packaging, testing, versions.",
    "Real Java projects live inside a toolchain. Maven/Gradle build them, JARs "
    "package them, JUnit tests them, and the ecosystem words (dependency, "
    "artifact, POM) are what you'll hear on any team.",
    _STUDY_NOTE,
    [
        ("Maven", "A build/dependency tool using pom.xml.", "The declarative build most Java teams use.", "mvn package"),
        ("Gradle", "A build tool using a Groovy/Kotlin script.", "The flexible, scriptable alternative to Maven.", "gradle build"),
        ("pom.xml", "Maven's project & dependency config.", "The file listing what your project needs.", "<dependency>...</dependency>"),
        ("dependency", "An external library your code needs.", "Someone else's code you rely on.", "<artifactId>guava</artifactId>"),
        ("artifact", "A built, versioned output (jar).", "The packaged thing a build produces.", "app-1.0.jar"),
        ("JAR", "A zip of classes and resources.", "Your whole app or library in one file.", "java -jar app.jar"),
        ("classpath", "Where the JVM finds classes/jars.", "The search path for your dependencies.", "-cp lib/*"),
        ("JUnit", "The standard unit-testing framework.", "How you write automated tests.", "@Test void works() { }"),
        ("assertion (test)", "A check that a value meets expectations.", "The 'is this right?' line in a test.", "assertEquals(4, add(2,2));"),
        ("mock", "A fake collaborator for a test.", "A stand-in object so you test one thing.", "mock(Repo.class)"),
        ("SLF4J / Logback", "Logging facade and backend.", "The standard way apps write logs.", "logger.info(\"started\");"),
        ("LTS version", "A long-term-support Java release.", "The versions companies actually pin to (8, 11, 17, 21).", "// Java 21 LTS"),
        ("javadoc", "Doc generated from /** */ comments.", "API docs built straight from your comments.", "/** Adds two ints. */"),
        ("annotation processor", "Code that reacts to annotations at build.", "A plugin that generates code from annotations.", "@AutoValue"),
        ("semantic versioning", "MAJOR.MINOR.PATCH version scheme.", "Version numbers that signal what changed.", "1.4.2"),
        ("IDE", "An integrated development environment.", "The editor that also builds/debugs (IntelliJ, Eclipse).", "// IntelliJ IDEA"),
    ],
    [
        _jvq("A Maven project's dependencies and build config live in…",
             ["pom.xml", "build.gradle", "MANIFEST.MF", "module-info.java"], 0,
             "Maven reads `pom.xml`; Gradle uses `build.gradle`."),
        _jvq("A JAR file is essentially…",
             ["a zip archive of classes and resources", "compiled native code", "a source bundle", "a database"], 0,
             "A JAR is a ZIP with a manifest, packaging compiled classes and resources for distribution."),
        _jvq("Which Java versions are LONG-TERM-SUPPORT (LTS)?",
             ["8, 11, 17, 21", "9, 10, 12", "all even versions", "only the latest"], 0,
             "LTS releases (8, 11, 17, 21…) get extended support and are what most teams standardize on."),
        _jvq("A `mock` in a unit test is…",
             ["a fake collaborator so you can test one unit in isolation", "a slow test", "a production dependency", "a build artifact"], 0,
             "Mocks stand in for real collaborators so a test exercises one class without its dependencies."),
        _jvq("Semantic version `2.5.1` — the `1` is the…",
             ["patch (bug-fix) number", "major version", "minor version", "build date"], 0,
             "MAJOR.MINOR.PATCH: a patch bump means backward-compatible bug fixes only."),
    ],
)


# ===========================================================================
# 14) MODERN JAVA & ANNOTATIONS
# ===========================================================================
_jv(
    "jv_modern",
    "Modern Java & Annotations",
    CAT_MODERN,
    "Records, sealed types, pattern matching, and the annotation/reflection tools.",
    "Java keeps evolving. Records kill boilerplate, sealed types tame hierarchies, "
    "switch got expressions and pattern matching, and annotations + reflection let "
    "frameworks work their magic. This is the vocabulary of Java 14+.",
    _STUDY_NOTE,
    [
        ("record", "An immutable data class with generated members.", "A tiny class that's just fields — Java writes the rest.", "record Point(int x, int y) { }"),
        ("sealed class", "A class limiting which types may extend it.", "A hierarchy with a fixed guest list.", "sealed interface Shape permits Circle { }"),
        ("permits", "Lists a sealed type's allowed subtypes.", "The guest list of a sealed type.", "sealed ... permits A, B"),
        ("pattern matching", "Testing and binding a type in one step.", "Check the type and grab it at once.", "if (o instanceof Dog d) { }"),
        ("switch expression", "A switch that returns a value.", "Switch that hands back a result, arrow-style.", "int n = switch (d) { case 1 -> 10; default -> 0; };"),
        ("text block", "A multi-line \"\"\" string literal.", "Multi-line text without escaping newlines.", "String s = \"\"\"hi\"\"\";"),
        ("var (local)", "Local variable type inference.", "Skip writing the obvious type.", "var list = new ArrayList<String>();"),
        ("annotation", "Metadata attached to code.", "A sticky note the compiler/tools read.", "@Override"),
        ("@Override", "Marks a method as overriding a parent.", "'I meant to replace the parent's version.'", "@Override void run() { }"),
        ("@Deprecated", "Flags an API as outdated.", "'Don't use this anymore.'", "@Deprecated void old() { }"),
        ("@FunctionalInterface", "Asserts a single-abstract-method interface.", "'This interface is lambda-ready.'", "@FunctionalInterface"),
        ("@SuppressWarnings", "Silences specific compiler warnings.", "'Yes I know, hush.'", "@SuppressWarnings(\"unchecked\")"),
        ("retention policy", "How long an annotation is kept.", "Whether the annotation survives to runtime.", "@Retention(RUNTIME)"),
        ("reflection", "Inspecting/altering code at runtime.", "Code that reads and pokes at other code live.", "obj.getClass().getMethods()"),
        ("Class object", "Runtime metadata for a type.", "The 'file card' describing a class at runtime.", "String.class"),
        ("module (JPMS)", "A named, encapsulated set of packages.", "A bigger box around packages, with declared exports.", "module app { requires x; }"),
        ("enhanced instanceof", "instanceof that binds a variable.", "Test-and-cast in one clean move.", "o instanceof String s"),
        ("Optional (modern)", "Explicit maybe-a-value container.", "A null-free way to say 'might be empty'.", "Optional.ofNullable(x)"),
    ],
    [
        _jvq("A `record` automatically generates…",
             ["constructor, accessors, equals/hashCode/toString", "getters and setters", "a builder", "thread-safe methods"], 0,
             "Records generate a canonical constructor, component accessors, and value-based equals/hashCode/toString — and are immutable."),
        _jvq("A `sealed` interface is useful because it…",
             ["restricts which classes can implement it", "makes methods final", "prevents instantiation", "adds thread safety"], 0,
             "Sealed types name their permitted subtypes, enabling exhaustive switches and safer hierarchies."),
        _jvq("Enhanced `instanceof` (`o instanceof String s`) lets you…",
             ["test the type and bind a variable at once", "cast without checking", "compare two objects", "avoid generics"], 0,
             "Pattern matching for instanceof both tests the type and, on success, binds `s` to the cast value."),
        _jvq("A switch EXPRESSION differs from a switch statement because it…",
             ["produces a value", "can't have a default", "only works on ints", "requires break"], 0,
             "Switch expressions (`->` arms, optional `yield`) return a value and don't fall through."),
        _jvq("Reflection lets you…",
             ["inspect and invoke code at runtime", "speed up the JVM", "avoid compilation", "manage memory"], 0,
             "Reflection reads class metadata and can access fields/methods dynamically — the basis of many frameworks."),
        _jvq("For an annotation to be readable at runtime (e.g. by a framework), it needs…",
             ["@Retention(RUNTIME)", "@Override", "@Deprecated", "no policy"], 0,
             "The default retention is CLASS (not visible at runtime); RUNTIME retention keeps it available to reflection."),
    ],
)
