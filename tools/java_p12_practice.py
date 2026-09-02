# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 12 practice - encapsulation.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[12]`.
#
# Module 12 scope: access modifiers, `private` fields, getters and setters,
# verbs over setters, class invariants established in the constructor and
# preserved by every mutator, clamping vs rejecting, immutable objects,
# defensive copying in and out.
#
# NOT AVAILABLE: `throw` and exceptions are Part 5 (module 15), so the third
# option for a bad argument - throwing - is discussed in prose but every
# exercise here either CLAMPS or REJECTS (returns a boolean). `extends`,
# `@Override` and `toString()` are module 13, so objects still describe
# themselves through a `describe()` method.
# ---------------------------------------------------------------------------


def _wrap1440(v):
    """Java's ((v % 1440) + 1440) % 1440 - non-negative even for negative v."""
    return ((v % 1440) + 1440) % 1440


def _p12ex(eid, title, difficulty, prompt, types, body, tests, hints):
    types = types.strip("\n")
    return _jch(eid, title, difficulty, prompt, _joop(types, body), types,
                tests, hints)


# --- Family A - private, and the accessors that replace it -------------------

_P12_A = _jfam(
    "p12-private", "`private`, and what replaces it",
    "Close the field; open a method.",
    """
Module 11's fields had no modifier, so anything in the package could reach in
and change them. `private` closes that door:

```java
class Person {
    private String name;
    private int age;

    Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    String getName() { return name; }      // accessor: read-only view
    int getAge()     { return age; }
}
```

**The four access levels**, widest to narrowest:

| Modifier | Visible to |
|---|---|
| `public` | everyone |
| `protected` | this class, subclasses, and the package |
| *(none)* | this class and the package — "package-private" |
| `private` | **this class only** |

**Default to `private` for fields and `public` for the methods that matter.**
The rule of thumb is that a field is an implementation decision and a method is
a promise. Making a field public freezes the decision forever, because anyone
may be depending on it.

**A getter is not just a field with extra typing.** It lets you change your mind
later — compute the value instead of storing it, validate, log, or return a copy
— without any caller changing. That option is the entire point, and it costs one
line.

**Access is per CLASS, not per object.** A method of `Person` may read
`other.name` on a *different* `Person`, which is what made module 11's copy
constructor and `sameAs` possible. Private means "inside this class", not
"inside this object".
""",
    [
        _p12ex("j12-pr-getters", "Close the fields, open two getters", "Intro",
               "Write a `Person` class with `private String name` and `private int age`, "
               "a constructor taking both, and `getName()` and `getAge()`. `main` reads "
               "a one-word name and an age and prints each on its own line.",
               """
class Person {
    private String name;
    private int age;

    Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    String getName() {
        return name;
    }

    int getAge() {
        return age;
    }
}
""",
               """        String pn = sc.next();
        int pa = sc.nextInt();
        Person p = new Person(pn, pa);
        System.out.println(p.getName());
        System.out.println(p.getAge());""",
               [_case(f"{n} {a}", _nl(n, a))
                for (n, a) in (("Ada", 36), ("x", 0), ("Bo", 100), ("Cy", 1),
                               ("Di", 42))],
               ["Both fields get `private`.",
                "The constructor still assigns them with `this.` — code inside the "
                "class may always touch its own private fields.",
                "Each getter returns one field and takes no parameters.",
                "`main` cannot say `p.name` any more; it has to go through the "
                "method."]),

        _p12ex("j12-pr-computed", "A getter that computes", "Easy",
               "Write a `Rect` class with `private int w` and `private int h`, a "
               "constructor, `int getArea()` returning `w * h`, and "
               "`int getPerimeter()` returning `2 * (w + h)`. Neither area nor perimeter "
               "is stored as a field.",
               """
class Rect {
    private int w;
    private int h;

    Rect(int w, int h) {
        this.w = w;
        this.h = h;
    }

    int getArea() {
        return w * h;
    }

    int getPerimeter() {
        return 2 * (w + h);
    }
}
""",
               """        int rw = sc.nextInt();
        int rh = sc.nextInt();
        Rect r = new Rect(rw, rh);
        System.out.println(r.getArea());
        System.out.println(r.getPerimeter());""",
               [_case(f"{w} {h}", _nl(w * h, 2 * (w + h)))
                for (w, h) in ((3, 4), (1, 1), (0, 5), (12, 2), (7, 7))],
               ["A getter does not have to return a stored field.",
                "Storing the area as well would mean keeping it in step forever; "
                "computing it cannot go stale.",
                "That freedom is exactly what `private` bought you — callers cannot "
                "tell the difference.",
                "Mind the perimeter formula: `2 * (w + h)`, with the brackets."]),

        _p12ex("j12-pr-readonly", "Read-only from outside", "Easy",
               "Write a `Ticket` class with `private final int number` assigned in the "
               "constructor, a getter, and **no setter at all**. Add "
               "`boolean isBefore(Ticket other)` returning whether this number is "
               "smaller. `main` builds two tickets and prints the first number and the "
               "comparison.",
               """
class Ticket {
    private final int number;

    Ticket(int number) {
        this.number = number;
    }

    int getNumber() {
        return number;
    }

    boolean isBefore(Ticket other) {
        return this.number < other.number;
    }
}
""",
               """        int t1 = sc.nextInt();
        int t2 = sc.nextInt();
        Ticket a = new Ticket(t1);
        Ticket b = new Ticket(t2);
        System.out.println(a.getNumber());
        System.out.println(a.isBefore(b));""",
               [_case(f"{x} {y}", _nl(x, _jbool(x < y)))
                for (x, y) in ((1, 2), (5, 5), (9, 3), (0, 1), (-2, -1))],
               ["`private final` means assigned once, in the constructor, and never "
                "again.",
                "There is no setter, and there could not be one — `final` forbids "
                "it.",
                "`isBefore` reaches into `other.number` even though it is private, "
                "because access is per CLASS: both objects are `Ticket`s.",
                "Equal numbers are not 'before', so a strict `<`."]),

        _p12ex("j12-pr-package-vs-private", "Two levels side by side", "Medium",
               "Write a `Meter` class with `private int secret = 42;` and a "
               "package-private (no modifier) `int visible = 7;`. Give it "
               "`int reveal()` returning `secret`. `main` prints `m.visible` directly, "
               "then `m.reveal()`.",
               """
class Meter {
    private int secret = 42;
    int visible = 7;

    int reveal() {
        return secret;
    }
}
""",
               """        int ignored = sc.nextInt();
        Meter m = new Meter();
        System.out.println(m.visible);
        System.out.println(m.reveal());""",
               [_case(str(v), _nl(7, 42)) for v in (1, 0, -3, 100, 5)],
               ["`visible` has no modifier, so `main` — in the same file and "
                "package — may read it directly.",
                "`secret` is `private`, so `m.secret` from `main` would NOT compile; "
                "it has to go through `reveal()`.",
                "Fields may be initialised at their declaration, and that runs "
                "before the constructor body.",
                "No constructor is written at all here, so Java supplies the free "
                "no-argument one.",
                "The output is the same for every input — the input is only there so "
                "the program reads something."]),

        _p12ex("j12-pr-two-objects", "Reaching into another instance", "Medium",
               "Write a `Wallet` class with `private int cents`, a constructor, "
               "`int getCents()`, and `int totalWith(Wallet other)` returning the sum of "
               "both wallets' cents by reading `other.cents` **directly**. `main` builds "
               "two and prints the total.",
               """
class Wallet {
    private int cents;

    Wallet(int cents) {
        this.cents = cents;
    }

    int getCents() {
        return cents;
    }

    int totalWith(Wallet other) {
        return this.cents + other.cents;
    }
}
""",
               """        int w1 = sc.nextInt();
        int w2 = sc.nextInt();
        Wallet a = new Wallet(w1);
        Wallet b = new Wallet(w2);
        System.out.println(a.totalWith(b));""",
               [_case(f"{x} {y}", x + y)
                for (x, y) in ((100, 250), (0, 0), (-5, 5), (1, 1), (999, 1))],
               ["`private` restricts access to the CLASS, not to the object.",
                "So a `Wallet` method may read another `Wallet`'s private field "
                "directly.",
                "`this.cents + other.cents` — no getter needed, though using one "
                "would also work.",
                "This is what made module 11's copy constructor possible, and it "
                "surprises people who read `private` as 'per object'."]),
    ])


# --- Family B - verbs over setters -------------------------------------------

_P12_B = _jfam(
    "p12-verbs", "Verbs over setters",
    "Name the operation, not the field.",
    """
A setter exposes a field under a thin disguise:

```java
account.setBalance(account.getBalance() - 50);      // caller does the arithmetic
```

Everything that could go wrong is now the caller's problem, and every caller has
to get it right. A **verb** moves the rule inside the object, where it can be
enforced once:

```java
account.withdraw(50);                                // the object does the work
```

**The test is whether the operation has a name in the problem domain.** Bank
accounts do not "set balance" — they deposit and withdraw. Playlists do not "set
songs" — they add and remove. When you can name the verb, the setter is almost
always the wrong shape.

**A verb can also refuse.** Because the object is in charge, it can decline an
operation that would break its rules and say so:

```java
boolean withdraw(int amount) {
    if (amount <= 0 || amount > balance) return false;   // refused
    balance -= amount;
    return true;
}
```

Returning a `boolean` is the simplest of the three responses to a bad argument.
The other two are **clamping** (silently adjust to the nearest legal value) and
**throwing** — which is Part 5, and deliberately not used anywhere in this
module.

**Not every field needs a setter, and most do not need one at all.** Start with
none, and add a mutator only when a real operation demands it.
""",
    [
        _p12ex("j12-pr-deposit", "Deposit and withdraw", "Medium",
               "Write an `Account` class with `private int balance`, a constructor, "
               "`int getBalance()`, `void deposit(int amount)` which ignores non-positive "
               "amounts, and `boolean withdraw(int amount)` which returns `false` and "
               "changes nothing unless the amount is positive and no more than the "
               "balance. `main` reads a start, a deposit and a withdrawal.",
               """
class Account {
    private int balance;

    Account(int balance) {
        this.balance = balance;
    }

    int getBalance() {
        return balance;
    }

    void deposit(int amount) {
        if (amount > 0) {
            balance = balance + amount;
        }
    }

    boolean withdraw(int amount) {
        if (amount <= 0 || amount > balance) {
            return false;
        }
        balance = balance - amount;
        return true;
    }
}
""",
               """        int start = sc.nextInt();
        int dep = sc.nextInt();
        int wit = sc.nextInt();
        Account acc = new Account(start);
        acc.deposit(dep);
        System.out.println(acc.withdraw(wit));
        System.out.println(acc.getBalance());""",
               [_case(f"{s} {d} {w}",
                      (lambda bal: _nl(_jbool(0 < w <= bal),
                                       bal - w if 0 < w <= bal else bal))(
                          s + (d if d > 0 else 0)))
                for (s, d, w) in ((100, 50, 30), (100, 0, 200), (0, 10, 10),
                                  (50, -5, 20), (10, 10, 0))],
               ["There is no `setBalance` — the two verbs are the whole interface.",
                "`deposit` silently ignores a non-positive amount, so the balance "
                "never falls through the wrong door.",
                "`withdraw` must check BOTH that the amount is positive and that it "
                "fits, and must not change the balance when it refuses.",
                "Return `false` before touching `balance`, not after.",
                "Case two withdraws more than there is and must leave the balance "
                "alone; case five withdraws `0`, which is not positive, so also "
                "`false`."]),

        _p12ex("j12-pr-counter-verbs", "Increment, reset, read", "Easy",
               "Write a `Counter` class with `private int count`, a no-argument "
               "constructor starting at `0`, `void increment()`, `void reset()` and "
               "`int get()`. There is no setter. `main` reads `k`, increments that many "
               "times, prints, resets, and prints again.",
               """
class Counter {
    private int count;

    Counter() {
        this.count = 0;
    }

    void increment() {
        count = count + 1;
    }

    void reset() {
        count = 0;
    }

    int get() {
        return count;
    }
}
""",
               """        int k = sc.nextInt();
        Counter c = new Counter();
        for (int i = 0; i < k; i++) {
            c.increment();
        }
        System.out.println(c.get());
        c.reset();
        System.out.println(c.get());""",
               [_case(str(k), _nl(k, 0)) for k in (5, 0, 1, 100, 3)],
               ["Three verbs and one reader.",
                "None of them takes the new value as a parameter — that is what "
                "makes them verbs rather than setters.",
                "A caller cannot set the count to 700 directly, which is exactly the "
                "guarantee.",
                "The second printed line is always `0`."]),

        _p12ex("j12-pr-playlist-add", "Add, do not set", "Medium",
               "Write a `Playlist` class holding `private int[] lengths` and "
               "`private int size`, built with a capacity in the constructor. Give it "
               "`boolean add(int seconds)` which refuses non-positive values and refuses "
               "once full, `int getSize()` and `int totalSeconds()`. `main` reads a "
               "capacity, then a count, then that many lengths.",
               """
class Playlist {
    private int[] lengths;
    private int size;

    Playlist(int capacity) {
        this.lengths = new int[capacity];
        this.size = 0;
    }

    boolean add(int seconds) {
        if (seconds <= 0 || size == lengths.length) {
            return false;
        }
        lengths[size] = seconds;
        size = size + 1;
        return true;
    }

    int getSize() {
        return size;
    }

    int totalSeconds() {
        int total = 0;
        for (int i = 0; i < size; i++) {
            total += lengths[i];
        }
        return total;
    }
}
""",
               """        int cap = sc.nextInt();
        int n = sc.nextInt();
        Playlist p = new Playlist(cap);
        for (int i = 0; i < n; i++) {
            p.add(sc.nextInt());
        }
        System.out.println(p.getSize());
        System.out.println(p.totalSeconds());""",
               [_case("\n".join([str(cap), str(len(vals)), " ".join(str(v) for v in vals)]),
                      (lambda kept: _nl(len(kept), sum(kept)))(
                          [v for v in vals if v > 0][:cap]))
                for (cap, vals) in ((5, [100, 200, 300]),
                                    (2, [10, 20, 30]),
                                    (3, [-5, 60, 0, 90]),
                                    (1, [42]),
                                    (4, [1, 2, 3, 4]))],
               ["The array is an implementation detail and stays `private` — callers "
                "only see `add`.",
                "`size` counts what has actually been added, which is not the "
                "array's length.",
                "`add` refuses two different ways: a non-positive length, and a full "
                "playlist. Both return `false` without changing anything.",
                "`totalSeconds` must loop to `size`, not to `lengths.length`, or it "
                "sums the empty tail.",
                "Case three has a negative and a zero, which are both refused, and "
                "case two overflows the capacity."]),

        _p12ex("j12-pr-toggle", "A verb with no argument at all", "Easy",
               "Write a `Light` class with `private boolean on`, a constructor taking "
               "the initial state, `void toggle()` which flips it, and "
               "`String state()` returning `on` or `off`. `main` reads `k` and toggles "
               "that many times.",
               """
class Light {
    private boolean on;

    Light(boolean on) {
        this.on = on;
    }

    void toggle() {
        on = !on;
    }

    String state() {
        if (on) {
            return "on";
        }
        return "off";
    }
}
""",
               """        boolean start = sc.nextInt() == 1;
        int k = sc.nextInt();
        Light l = new Light(start);
        for (int i = 0; i < k; i++) {
            l.toggle();
        }
        System.out.println(l.state());""",
               [_case(f"{s} {k}",
                      ("on" if ((s == 1) != (k % 2 == 1)) else "off"))
                for (s, k) in ((1, 0), (1, 1), (0, 3), (0, 4), (1, 7))],
               ["`toggle()` takes no parameter — the new value is entirely "
                "determined by the old one.",
                "`on = !on;` is the whole body.",
                "A `setOn(boolean)` would let a caller pass the same value twice and "
                "would not express 'flip' at all.",
                "`state()` converts the boolean to the two words the brief asks "
                "for."]),

        _p12ex("j12-pr-rename", "A setter that is really a verb", "Medium",
               "Write a `File` class with `private String name`, a constructor, "
               "`String getName()`, and `boolean rename(String newName)` which refuses "
               "an empty or blank name and otherwise renames, returning whether it "
               "worked. `main` reads a starting name and a proposed new one.",
               """
class File {
    private String name;

    File(String name) {
        this.name = name;
    }

    String getName() {
        return name;
    }

    boolean rename(String newName) {
        if (newName.isBlank()) {
            return false;
        }
        name = newName;
        return true;
    }
}
""",
               """        String first = sc.nextLine();
        String second = sc.nextLine();
        File f = new File(first);
        System.out.println(f.rename(second));
        System.out.println(f.getName());""",
               [_l2case(a, b, _nl(_jbool(b.strip() != ""),
                                  b if b.strip() != "" else a))
                for (a, b) in (("notes.txt", "todo.txt"), ("a", " "),
                               ("x.txt", "y.txt"), ("keep", ""),
                               ("one", "two"))],
               ["`rename` is a better name than `setName` because it says what the "
                "operation MEANS.",
                "It refuses a blank name — `isBlank()` from module 7 covers both "
                "empty and whitespace-only.",
                "Refuse before assigning, so a rejected rename leaves the old name "
                "intact.",
                "Cases two and four propose blank names and must keep the "
                "original."]),
    ])


# --- Family C - invariants ---------------------------------------------------

_P12_C = _jfam(
    "p12-invariant", "Invariants",
    "A rule that is true the moment the object exists, and stays true.",
    """
An **invariant** is a statement about an object that is always true from the
outside: *a balance is never negative*, *a percentage is between 0 and 100*, *a
date's month is 1 to 12*.

Keeping one takes exactly two things:

1. **The constructor establishes it.** Nobody can ever hold a reference to an
   object that has not been through the constructor, which is what makes this
   airtight.
2. **Every mutator preserves it.** A single method that can push the field out
   of range destroys the guarantee for the whole class.

`private` is what makes it possible. A public field can be assigned by anyone,
so no invariant can survive one.

**Three responses to a bad argument:**

| Response | Behaviour | Good when |
|---|---|---|
| **Clamp** | silently move to the nearest legal value | out-of-range is expected and harmless (volume, brightness) |
| **Reject** | change nothing, return `false` | the caller can reasonably handle refusal |
| **Throw** | raise an exception | the call is a programming error — **Part 5** |

The wrong answer is the fourth one: accept it and let the field go bad. That
turns a small mistake at the call site into a corrupted object that fails
somewhere else entirely, long afterwards.

**Clamping in the constructor and in every setter must agree.** Writing the
check twice is how they drift apart — which is why module 11's `this(...)`
delegation and a shared private helper are worth the trouble.
""",
    [
        _p12ex("j12-pr-percent", "A value that stays in range", "Medium",
               "Write a `Volume` class with `private int level` held between `0` and "
               "`100`. Both the constructor and `void set(int v)` must **clamp** out of "
               "range values. Add `int get()`. `main` reads a starting value and then a "
               "new one.",
               """
class Volume {
    private int level;

    Volume(int level) {
        this.level = clamp(level);
    }

    void set(int v) {
        level = clamp(v);
    }

    int get() {
        return level;
    }

    private int clamp(int v) {
        if (v < 0) {
            return 0;
        }
        if (v > 100) {
            return 100;
        }
        return v;
    }
}
""",
               """        int a1 = sc.nextInt();
        int b1 = sc.nextInt();
        Volume v = new Volume(a1);
        System.out.println(v.get());
        v.set(b1);
        System.out.println(v.get());""",
               [_case(f"{x} {y}", _nl(min(max(x, 0), 100), min(max(y, 0), 100)))
                for (x, y) in ((50, 150), (-10, 20), (0, 100), (200, -1),
                               (7, 7))],
               ["The rule is needed in two places, so write it ONCE in a private "
                "helper and call it from both.",
                "A `private` method is invisible outside the class, which is exactly "
                "right for an internal rule.",
                "Duplicating the clamp in the constructor and the setter is how the "
                "two drift apart later.",
                "Clamping means adjusting silently — `150` becomes `100`, not a "
                "refusal.",
                "The helper can be `private` and still be called from the "
                "constructor."]),

        _p12ex("j12-pr-reject", "Refuse instead of clamping", "Medium",
               "Write an `Age` class with `private int years`, whose constructor clamps "
               "to `0` if negative, and whose `boolean set(int v)` **rejects** anything "
               "outside `0..150` — returning `false` and changing nothing. Add "
               "`int get()`.",
               """
class Age {
    private int years;

    Age(int years) {
        if (years < 0) {
            this.years = 0;
        } else {
            this.years = years;
        }
    }

    boolean set(int v) {
        if (v < 0 || v > 150) {
            return false;
        }
        years = v;
        return true;
    }

    int get() {
        return years;
    }
}
""",
               """        int a1 = sc.nextInt();
        int b1 = sc.nextInt();
        Age age = new Age(a1);
        System.out.println(age.set(b1));
        System.out.println(age.get());""",
               [_case(f"{x} {y}",
                      (lambda start: _nl(_jbool(0 <= y <= 150),
                                         y if 0 <= y <= 150 else start))(max(x, 0)))
                for (x, y) in ((30, 40), (30, 200), (-5, 10), (0, -1), (99, 150))],
               ["This class deliberately uses two different strategies, which is "
                "worth noticing: the constructor clamps, the setter rejects.",
                "Reject means return `false` and leave the field exactly as it was.",
                "Check the range before assigning, never after.",
                "Case two and four propose out-of-range values and must keep the "
                "old one.",
                "Case five proposes exactly `150`, which is inside the range and "
                "must be accepted."]),

        _p12ex("j12-pr-range-pair", "Two fields, one rule between them", "Hard",
               "Write a `Range` class with `private int lo` and `private int hi` and the "
               "invariant `lo <= hi`. The constructor swaps them if they arrive the "
               "wrong way round. `boolean setLo(int v)` rejects a value greater than "
               "`hi`; `boolean setHi(int v)` rejects a value less than `lo`. Add "
               "`String describe()` returning `lo..hi`.",
               """
class Range {
    private int lo;
    private int hi;

    Range(int lo, int hi) {
        if (lo <= hi) {
            this.lo = lo;
            this.hi = hi;
        } else {
            this.lo = hi;
            this.hi = lo;
        }
    }

    boolean setLo(int v) {
        if (v > hi) {
            return false;
        }
        lo = v;
        return true;
    }

    boolean setHi(int v) {
        if (v < lo) {
            return false;
        }
        hi = v;
        return true;
    }

    String describe() {
        return lo + ".." + hi;
    }
}
""",
               """        int p = sc.nextInt();
        int q = sc.nextInt();
        int nl = sc.nextInt();
        Range r = new Range(p, q);
        System.out.println(r.describe());
        System.out.println(r.setLo(nl));
        System.out.println(r.describe());""",
               [_case(f"{p} {q} {nl}",
                      (lambda lo, hi: _nl(f"{lo}..{hi}", _jbool(nl <= hi),
                                          f"{nl if nl <= hi else lo}..{hi}"))(
                          min(p, q), max(p, q)))
                for (p, q, nl) in ((1, 5, 3), (5, 1, 0), (2, 2, 9),
                                   (0, 10, 10), (-3, 3, -5))],
               ["The invariant now relates TWO fields, so neither setter can be "
                "written without looking at the other.",
                "The constructor establishes it by swapping rather than refusing — "
                "case two passes them the wrong way round.",
                "`setLo` must reject anything above `hi`; `setHi` anything below "
                "`lo`.",
                "Equal is allowed, since the rule is `lo <= hi` — case four sets `lo` "
                "to exactly `hi` and must succeed.",
                "This is why fields go private: a public `lo` could be set to 99 "
                "with no way to stop it."]),

        _p12ex("j12-pr-nonneg-total", "The total can never go negative", "Medium",
               "Write a `Stock` class with `private int units` (never negative). The "
               "constructor clamps. `void add(int n)` ignores non-positive `n`. "
               "`boolean remove(int n)` refuses unless `n` is positive and no more than "
               "`units`. Add `int get()`.",
               """
class Stock {
    private int units;

    Stock(int units) {
        if (units < 0) {
            this.units = 0;
        } else {
            this.units = units;
        }
    }

    void add(int n) {
        if (n > 0) {
            units = units + n;
        }
    }

    boolean remove(int n) {
        if (n <= 0 || n > units) {
            return false;
        }
        units = units - n;
        return true;
    }

    int get() {
        return units;
    }
}
""",
               """        int start = sc.nextInt();
        int in = sc.nextInt();
        int out = sc.nextInt();
        Stock s = new Stock(start);
        s.add(in);
        System.out.println(s.remove(out));
        System.out.println(s.get());""",
               [_case(f"{a} {b} {c}",
                      (lambda held: _nl(_jbool(0 < c <= held),
                                        held - c if 0 < c <= held else held))(
                          max(a, 0) + (b if b > 0 else 0)))
                for (a, b, c) in ((10, 5, 3), (0, 0, 1), (-4, 10, 10),
                                  (5, -2, 6), (7, 0, 7))],
               ["Three places enforce one rule: the constructor, `add` and "
                "`remove`.",
                "Missing any one of them breaks the guarantee for the whole class.",
                "`remove` must check the amount is positive AND available before "
                "subtracting.",
                "Case three starts negative (clamped to 0), adds 10, then removes "
                "exactly 10 — which is allowed.",
                "Case four asks to remove more than is held and must refuse."]),

        _p12ex("j12-pr-normalise", "Normalise on the way in", "Medium",
               "Write a `Clock` class with `private int minutes` held in `0..1439`. The "
               "constructor and `void advance(int n)` both wrap the value using "
               "`((v % 1440) + 1440) % 1440`, which is correct for negatives too. Add "
               "`int get()`.",
               """
class Clock {
    private int minutes;

    Clock(int minutes) {
        this.minutes = wrap(minutes);
    }

    void advance(int n) {
        minutes = wrap(minutes + n);
    }

    int get() {
        return minutes;
    }

    private int wrap(int v) {
        return ((v % 1440) + 1440) % 1440;
    }
}
""",
               """        int start = sc.nextInt();
        int step = sc.nextInt();
        Clock c = new Clock(start);
        c.advance(step);
        System.out.println(c.get());""",
               [_case(f"{a} {b}", _wrap1440(_wrap1440(a) + b))
                for (a, b) in ((100, 50), (1439, 1), (0, -1), (3000, 0),
                               (-30, 0))],
               ["Normalising is a third strategy, alongside clamping and rejecting: "
                "every input is legal, it just gets mapped into range.",
                "Java's `%` can return a negative, so `v % 1440` alone is not "
                "enough.",
                "`((v % 1440) + 1440) % 1440` forces the result non-negative — the "
                "same trick module 4's rotation needed.",
                "Write it once in a private helper and use it in both places.",
                "Case three wraps backwards past midnight to `1439`; case five "
                "starts negative."]),
    ])


# --- Family D - immutable objects --------------------------------------------

_P12_D = _jfam(
    "p12-immutable", "Immutable objects",
    "Never changes after construction — so nothing can go wrong later.",
    """
An immutable object is one whose visible state is fixed the moment it is built.
`String` and `Integer` are the famous examples.

**The recipe, in four steps:**

1. Make every field `private final`.
2. Assign every field in the constructor.
3. Provide **no** mutators — no setters, no methods that change a field.
4. Where a field is itself mutable (an array, or another object), copy it on the
   way in and on the way out. That is family E.

**Operations return new objects instead of mutating:**

```java
class Money {
    private final int cents;

    Money(int cents) { this.cents = cents; }

    Money plus(Money other) {
        return new Money(this.cents + other.cents);   // a NEW Money
    }
}
```

`plus` reads like `+` on numbers, and for the same reason: `3 + 4` does not
change `3`.

**Why bother.** An immutable object is safe to share between threads with no
locking, safe to use as a `HashMap` key (its hash can never go stale), safe to
hand to code you do not trust, and impossible to leave in a half-updated state.
It cannot have an invariant violated after construction, because it cannot be
changed at all.

**The cost** is allocation: a long chain of `plus` calls creates a lot of short
lived objects. That is exactly the `String` versus `StringBuilder` trade-off
from module 8, and the answer is the same — it rarely matters, and when it does
you use a mutable builder.

> `final` on the *class* stops a subclass adding mutable state and breaking the
> promise. That is why `String` is final, and it is module 14's argument.
""",
    [
        _p12ex("j12-pr-money", "An immutable Money", "Medium",
               "Write a `Money` class with `private final int cents`, a constructor, "
               "`int getCents()`, and `Money plus(Money other)` returning a **new** "
               "`Money`. There must be no setter. `main` adds two amounts and prints the "
               "sum and then the first amount, which must be unchanged.",
               """
class Money {
    private final int cents;

    Money(int cents) {
        this.cents = cents;
    }

    int getCents() {
        return cents;
    }

    Money plus(Money other) {
        return new Money(this.cents + other.cents);
    }
}
""",
               """        int m1 = sc.nextInt();
        int m2 = sc.nextInt();
        Money a = new Money(m1);
        Money b = new Money(m2);
        Money sum = a.plus(b);
        System.out.println(sum.getCents());
        System.out.println(a.getCents());""",
               [_case(f"{x} {y}", _nl(x + y, x))
                for (x, y) in ((150, 275), (0, 0), (-100, 50), (999, 1), (5, 5))],
               ["`private final` and a constructor: after that, nothing can change "
                "the field.",
                "`plus` must NOT assign to `cents` — it returns a brand new "
                "`Money`.",
                "That is why the second printed line still shows the original "
                "amount.",
                "This is exactly how `String` concatenation behaves, and for the "
                "same reason."]),

        _p12ex("j12-pr-point-with", "Change by making a new one", "Medium",
               "Write an immutable `Point` class with `private final int x, y`, a "
               "constructor, `String describe()` returning `(x, y)`, and "
               "`Point withX(int newX)` returning a new point with the new `x` and the "
               "same `y`. `main` prints the derived point and then the original.",
               """
class Point {
    private final int x;
    private final int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    String describe() {
        return "(" + x + ", " + y + ")";
    }

    Point withX(int newX) {
        return new Point(newX, this.y);
    }
}
""",
               """        int px = sc.nextInt();
        int py = sc.nextInt();
        Point p = new Point(px, py);
        Point q = p.withX(99);
        System.out.println(q.describe());
        System.out.println(p.describe());""",
               [_case(f"{x} {y}", _nl(f"(99, {y})", f"({x}, {y})"))
                for (x, y) in ((3, 4), (0, 0), (-1, 2), (100, -100), (7, 7))],
               ["The `withX` naming convention is standard for immutable types: it "
                "means 'like this one, but with a different x'.",
                "It builds a new object rather than assigning — the fields are "
                "`final` and could not be assigned anyway.",
                "Pass `this.y` through unchanged.",
                "Compare with module 11's aliasing exercise: there, changing through "
                "a second reference changed the original. Here it cannot."]),

        _p12ex("j12-pr-immutable-chain", "Chaining without mutating", "Medium",
               "Write an immutable `Counter` with `private final int value`, a "
               "constructor, `int get()`, and `Counter next()` returning a new counter "
               "one higher. `main` reads `k`, chains `next()` that many times, and "
               "prints the final value and then the starting counter's value.",
               """
class Counter {
    private final int value;

    Counter(int value) {
        this.value = value;
    }

    int get() {
        return value;
    }

    Counter next() {
        return new Counter(value + 1);
    }
}
""",
               """        int k = sc.nextInt();
        Counter start = new Counter(0);
        Counter cur = start;
        for (int i = 0; i < k; i++) {
            cur = cur.next();
        }
        System.out.println(cur.get());
        System.out.println(start.get());""",
               [_case(str(k), _nl(k, 0)) for k in (5, 0, 1, 100, 3)],
               ["`next()` returns a new object; it cannot change this one.",
                "So `main` has to reassign `cur` each time — `cur.next();` alone "
                "would compute a value and discard it.",
                "That is the same trap as calling `s.substring(1)` without assigning "
                "it, in module 6.",
                "`start` never moves, which is the second printed line.",
                "Note the cost: `k` objects are created. Module 8's argument, again."]),

        _p12ex("j12-pr-immutable-equal", "Comparing immutable values", "Medium",
               "Write an immutable `Money` with `private final int cents`, a "
               "constructor, `int getCents()`, and "
               "`boolean sameValueAs(Money other)`. `main` builds two from the same "
               "number and prints `a == b` and then `a.sameValueAs(b)`.",
               """
class Money {
    private final int cents;

    Money(int cents) {
        this.cents = cents;
    }

    int getCents() {
        return cents;
    }

    boolean sameValueAs(Money other) {
        return this.cents == other.cents;
    }
}
""",
               """        int v = sc.nextInt();
        Money a = new Money(v);
        Money b = new Money(v);
        System.out.println(a == b);
        System.out.println(a.sameValueAs(b));""",
               [_case(str(v), _nl("false", "true"))
                for v in (150, 0, -100, 999, 5)],
               ["Immutability does not make `==` work — these are still two "
                "different objects.",
                "So the first line is always `false`.",
                "`sameValueAs` compares the fields, giving `true`.",
                "Immutable value types are exactly the case where overriding "
                "`equals` matters most, which is module 13.",
                "Until then, a named method is the honest version."]),

        _p12ex("j12-pr-immutable-derived", "Derived values on an immutable object",
               "Medium",
               "Write an immutable `Rect` with `private final int w, h`, a constructor, "
               "`int area()`, and `Rect scaled(int factor)` returning a new `Rect` with "
               "both sides multiplied. `main` prints the original area and the scaled "
               "area.",
               """
class Rect {
    private final int w;
    private final int h;

    Rect(int w, int h) {
        this.w = w;
        this.h = h;
    }

    int area() {
        return w * h;
    }

    Rect scaled(int factor) {
        return new Rect(w * factor, h * factor);
    }
}
""",
               """        int rw = sc.nextInt();
        int rh = sc.nextInt();
        int f = sc.nextInt();
        Rect r = new Rect(rw, rh);
        System.out.println(r.area());
        System.out.println(r.scaled(f).area());""",
               [_case(f"{w} {h} {f}", _nl(w * h, (w * f) * (h * f)))
                for (w, h, f) in ((3, 4, 2), (1, 1, 1), (0, 5, 3), (2, 2, 0),
                                  (5, 3, 10))],
               ["`scaled` builds a new `Rect`; it never assigns to `w` or `h`.",
                "`area()` is computed rather than stored, so it can never disagree "
                "with the sides.",
                "The result of `scaled` can have `area()` called on it directly, "
                "since it is a full `Rect`.",
                "Both sides are multiplied, so the area grows by the square of the "
                "factor — case five is 15 then 1500."]),
    ])


# --- Family E - defensive copying --------------------------------------------

_P12_E = _jfam(
    "p12-defensive", "Defensive copying",
    "`private` protects the field, not the object it points at.",
    """
This is where encapsulation is most often quietly broken.

```java
class Team {
    private final int[] scores;

    Team(int[] scores) {
        this.scores = scores;              // BUG: shares the caller's array
    }

    int[] getScores() {
        return scores;                     // BUG: hands the array out
    }
}
```

Both fields are `private` and `final`, and the class is still wide open:

```java
int[] mine = {1, 2, 3};
Team t = new Team(mine);
mine[0] = 999;                 // changed the Team's data from outside
t.getScores()[1] = 999;        // and again, through the getter
```

`final` stops the *reference* being repointed. It says nothing about the object
it points at. And `private` controls who can name the field, not who can reach
the array once you have handed it to them.

**The fix is to copy at both boundaries:**

```java
Team(int[] scores) {
    this.scores = Arrays.copyOf(scores, scores.length);   // copy IN
}

int[] getScores() {
    return Arrays.copyOf(scores, scores.length);          // copy OUT
}
```

**Both** are needed. Copying only on the way in still lets the getter leak the
real array; copying only on the way out still lets the constructor's caller keep
a handle on it.

**This is why immutable types are easier.** A field of type `String` or `int`
needs no defensive copy, because there is nothing a caller could do to it. The
copying only becomes necessary once a mutable object is involved — which is a
good argument for preferring immutable ones.
""",
    [
        _p12ex("j12-pr-leak-in", "Copy on the way in", "Hard",
               "Write a `Team` class with `private final int[] scores`, whose "
               "constructor takes an `int[]` and stores a **copy**. Add `int total()`. "
               "`main` builds a team, then modifies the array it passed in — and the "
               "team's total must not change.",
               """
class Team {
    private final int[] scores;

    Team(int[] scores) {
        this.scores = Arrays.copyOf(scores, scores.length);
    }

    int total() {
        int sum = 0;
        for (int i = 0; i < scores.length; i++) {
            sum += scores[i];
        }
        return sum;
    }
}
""",
               _RD_ARR + """        Team t = new Team(a);
        int before = t.total();
        a[0] = 999;
        System.out.println(before);
        System.out.println(t.total());""",
               [_acase(list(a), _nl(sum(a), sum(a)))
                for a in ([1, 2, 3], [7], [0, 0], [-1, 2, -3], [10, 20])],
               ["Storing the parameter directly would share one array with the "
                "caller.",
                "`Arrays.copyOf(scores, scores.length)` makes an independent one.",
                "`final` does not help here — it stops the field being repointed, "
                "not the array being written to.",
                "Both printed lines must match, whatever `main` does to its own "
                "array afterwards."]),

        _p12ex("j12-pr-leak-out", "Copy on the way out", "Hard",
               "Write a `Team` class with `private final int[] scores` copied in by the "
               "constructor, `int total()`, and `int[] getScores()` returning a "
               "**copy**. `main` gets the array, modifies what it got, and the total "
               "must be unaffected.",
               """
class Team {
    private final int[] scores;

    Team(int[] scores) {
        this.scores = Arrays.copyOf(scores, scores.length);
    }

    int total() {
        int sum = 0;
        for (int i = 0; i < scores.length; i++) {
            sum += scores[i];
        }
        return sum;
    }

    int[] getScores() {
        return Arrays.copyOf(scores, scores.length);
    }
}
""",
               _RD_ARR + """        Team t = new Team(a);
        int[] handed = t.getScores();
        handed[0] = 999;
        System.out.println(t.total());
        System.out.println(handed[0]);""",
               [_acase(list(a), _nl(sum(a), 999))
                for a in ([1, 2, 3], [7], [0, 0], [-1, 2, -3], [10, 20])],
               ["Returning the field directly hands the caller a live handle on the "
                "object's data.",
                "Return `Arrays.copyOf(...)` instead.",
                "The caller's change then affects only their copy, which is why the "
                "second line prints `999` while the total is unchanged.",
                "Copying in without copying out — or the reverse — leaves the hole "
                "open. Both are needed."]),

        _p12ex("j12-pr-defensive-both", "Both boundaries at once", "Hard",
               "Write a `Snapshot` class with `private final int[] data`, copying both "
               "in the constructor and in `int[] get()`. Add `int size()`. `main` "
               "attacks from both directions and every number must still be the "
               "original.",
               """
class Snapshot {
    private final int[] data;

    Snapshot(int[] data) {
        this.data = Arrays.copyOf(data, data.length);
    }

    int[] get() {
        return Arrays.copyOf(data, data.length);
    }

    int size() {
        return data.length;
    }
}
""",
               _RD_ARR + """        Snapshot s = new Snapshot(a);
        a[0] = 111;
        int[] out = s.get();
        out[0] = 222;
        System.out.println(s.get()[0]);
        System.out.println(s.size());""",
               [_acase(list(a), _nl(a[0], len(a)))
                for a in ([1, 2, 3], [7], [0, 0], [-1, 2, -3], [10, 20])],
               ["Two copies, one at each boundary.",
                "`main` modifies its own array AND the array it was handed; neither "
                "may reach the snapshot.",
                "So `s.get()[0]` still returns the value that was there when the "
                "snapshot was built.",
                "Note that `s.get()[0] = x` would also be harmless — it writes into "
                "a fresh copy that is immediately discarded.",
                "`size()` reads `data.length` directly, which is safe because a "
                "length cannot be modified."]),

        _p12ex("j12-pr-defensive-object", "Copying a mutable object field", "Hard",
               "Write a mutable `Point` class with `private int x, y`, a constructor, "
               "`void setX(int v)` and `int getX()`. Then write a `Marker` class with "
               "`private final Point where`, whose constructor stores a **copy** built "
               "with `new Point(p.getX(), p.getY())`, and `int getX()` returning "
               "`where.getX()`. `main` changes the point it passed in; the marker must "
               "not move.",
               """
class Point {
    private int x;
    private int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    void setX(int v) {
        x = v;
    }

    int getX() {
        return x;
    }

    int getY() {
        return y;
    }
}

class Marker {
    private final Point where;

    Marker(Point p) {
        this.where = new Point(p.getX(), p.getY());
    }

    int getX() {
        return where.getX();
    }
}
""",
               """        int px = sc.nextInt();
        int py = sc.nextInt();
        Point p = new Point(px, py);
        Marker m = new Marker(p);
        p.setX(999);
        System.out.println(m.getX());
        System.out.println(p.getX());""",
               [_case(f"{x} {y}", _nl(x, 999))
                for (x, y) in ((3, 4), (0, 0), (-1, 2), (100, -100), (7, 7))],
               ["The danger is not limited to arrays — any MUTABLE object field has "
                "it.",
                "`this.where = p;` would share one `Point` with the caller.",
                "Build a new one from the old one's values instead.",
                "`Marker` needs `Point` to expose `getY()` as well, so the copy can "
                "be built.",
                "The marker keeps the original x while the caller's point moves to "
                "999."]),

        _p12ex("j12-pr-no-copy-needed", "When no copy is needed", "Medium",
               "Write a `Label` class with `private final String text` and "
               "`private final int size`, a constructor, and `String describe()` "
               "returning `text/size`. Store both **directly** — no copying — and "
               "explain to yourself why that is safe. `main` reads a word and a number.",
               """
class Label {
    private final String text;
    private final int size;

    Label(String text, int size) {
        this.text = text;
        this.size = size;
    }

    String describe() {
        return text + "/" + size;
    }
}
""",
               """        String lt = sc.next();
        int ls = sc.nextInt();
        Label l = new Label(lt, ls);
        System.out.println(l.describe());""",
               [_case(f"{t} {n}", f"{t}/{n}")
                for (t, n) in (("big", 14), ("x", 0), ("bold", 72), ("a", 1),
                               ("title", 24))],
               ["No defensive copy is needed here, and adding one would be pure "
                "noise.",
                "`int` is a primitive — the field already holds its own copy of the "
                "value.",
                "`String` is immutable, so a shared reference cannot be used to "
                "change anything.",
                "Defensive copying is only required for MUTABLE object fields — "
                "arrays, collections, and classes with setters.",
                "That is a strong argument for preferring immutable types for "
                "fields: they make a whole category of bug impossible."]),
    ])


_PRACTICE[12] = [_P12_A, _P12_B, _P12_C, _P12_D, _P12_E]
