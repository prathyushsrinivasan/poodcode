# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 12 — Encapsulation.
#
# exec()'d by tools/java_course.py; appends one module to `_MODULES`.
#
# The argument this module makes: `private` is not bureaucracy, it is the only
# way to guarantee anything about your own object. Every lesson is a
# demonstration that a public field lets a caller break a rule the class is
# supposed to enforce.
#
# Lesson 12.4 (defensive copying) is where module 1's aliasing lesson finally
# pays off in full: a private final array field is still shared with whoever
# handed it to you, and with whoever you hand it back to.
#
# `toString`/`equals`/`hashCode` deliberately live in module 13, not here —
# they are OVERRIDES, and overriding is not taught until 13.3.
# ---------------------------------------------------------------------------

_M12 = []


# --- 12.1 Access modifiers --------------------------------------------------

_M12.append(_jlesson(
    "m12-private", "`private`, and why fields are not public",
    "The only way to guarantee anything about your own object.",
    """
A field you leave public is a field anyone can set to anything:

```java
class Account {
    int balance;                      // public to the whole package
}

Account a = new Account();
a.balance = -5000;                    // and nothing can stop this
```

The class was supposed to guarantee that a balance is never negative. It cannot,
because the rule lives in the class and the assignment does not. **`private`
moves the door inside:**

```java
class Account {
    private int balance;              // only Account's own code can touch it

    void deposit(int amount) {
        if (amount > 0) balance += amount;     // the rule lives WITH the data
    }

    int getBalance() {
        return balance;
    }
}
```

Now every path that changes `balance` runs through code you wrote, so the rule
is enforceable. That is **encapsulation**: the data and the rules about it are
sealed together, and the outside world gets a deliberately chosen door.

**The four levels**, narrowest first:

| Modifier | Visible to |
|---|---|
| `private` | this class only |
| *(none)* — "package-private" | any class in the same package |
| `protected` | same package, plus subclasses anywhere (module 13) |
| `public` | everything |

**The default rule: fields `private`, methods as public as they need to be.**
Start everything private and widen only when something outside genuinely needs
it. Widening later is easy; narrowing later breaks every caller.

**`private` is per-class, not per-object.** A method of `Account` can read the
private fields of *another* `Account` — which is exactly what a comparison or a
copy constructor needs:

```java
boolean richerThan(Account other) {
    return this.balance > other.balance;      // legal: same class
}
```

**Private methods** are for steps that are your business alone:

```java
private boolean isValid(int amount) { return amount > 0; }
```

Making a helper private means you can rename or delete it tomorrow without
breaking anyone. Every method you make public is a promise.

**A quiet consequence:** in this course everything lives in one file and
therefore one package, so a field with no modifier is still reachable from
`Main`. That is exactly why the drills use `private` explicitly — leaving it off
would look like it worked.
""",
    warmup=[
        _jq("A class wants to guarantee `balance >= 0`. Why is a public field fatal to that?",
            ["Any caller can assign directly, bypassing every check the class makes",
             "Public fields cannot hold integers",
             "It isn't — the class can still validate",
             "Because public fields are static"],
            0,
            "A rule can only be enforced if every write goes through code that checks it. A "
            "public field is a write path with no code in it."),
        _jq("Can an `Account` method read `other.balance` when `balance` is private?",
            ["Yes — `private` is per-class, not per-object",
             "No, never",
             "Only if `other` is `this`",
             "Only with a getter"],
            0,
            "Access control is checked against the class you are writing in. That is what "
            "makes comparison and copy-constructor code possible."),
    ],
    exercises=[
        _je("j12-pv-field", "Seal the field",
            "`Account` should not let anyone assign `balance` directly. Replace "
            "`____` with the field declaration that closes it off — `main` goes "
            "through `deposit` and `getBalance` instead.",
            _joop("class Account {\n"
                  "    private int balance;\n"
                  "\n"
                  "    void deposit(int amount) {\n"
                  "        if (amount > 0) balance += amount;\n"
                  "    }\n"
                  "\n"
                  "    int getBalance() {\n"
                  "        return balance;\n"
                  "    }\n"
                  "}",
                  "        Account a = new Account();\n"
                  "        a.deposit(sc.nextInt());\n"
                  "        a.deposit(sc.nextInt());\n"
                  "        System.out.println(a.getBalance());"),
            "    private int balance;",
            [_case(f"{x}\n{y}", max(0, x) + max(0, y))
             for (x, y) in ((100, 50), (100, -50), (-10, -20), (0, 7))],
            hints=["One keyword restricts a member to its own class.",
                   "The field is still an `int`.",
                   "`private int balance;` — note the negative deposits are rejected, which "
                   "is only possible because nobody can assign the field directly."],
            difficulty="Intro"),

        _je("j12-pv-method", "A helper nobody else needs",
            "`isValid` is an internal detail of `Account` and should not be part of "
            "its public surface. Replace `____` with its declaration.",
            _joop("class Account {\n"
                  "    private int balance;\n"
                  "\n"
                  "    private boolean isValid(int amount) {\n"
                  "        return amount > 0;\n"
                  "    }\n"
                  "\n"
                  "    void deposit(int amount) {\n"
                  "        if (isValid(amount)) balance += amount;\n"
                  "    }\n"
                  "\n"
                  "    int getBalance() {\n"
                  "        return balance;\n"
                  "    }\n"
                  "}",
                  "        Account a = new Account();\n"
                  "        a.deposit(sc.nextInt());\n"
                  "        a.deposit(sc.nextInt());\n"
                  "        System.out.println(a.getBalance());"),
            "    private boolean isValid(int amount) {",
            [_case(f"{x}\n{y}", max(0, x) + max(0, y))
             for (x, y) in ((100, 50), (30, -5), (-1, -2))],
            hints=["Same modifier as a private field, on a method.",
                   "It returns a `boolean` and takes the amount.",
                   "`private boolean isValid(int amount) {`"],
            difficulty="Intro"),

        _jfix("j12-pv-direct", "Reaching past the door",
              "`main` assigns the balance directly, which is exactly what `private` "
              "forbids — so this does not compile. Rewrite `main` to go through the "
              "class's own methods instead. (Deposit the amount; the class rejects "
              "anything that is not positive.)",
              _joop("class Account {\n"
                    "    private int balance;\n"
                    "\n"
                    "    void deposit(int amount) {\n"
                    "        if (amount > 0) balance += amount;\n"
                    "    }\n"
                    "\n"
                    "    int getBalance() {\n"
                    "        return balance;\n"
                    "    }\n"
                    "}",
                    "        Account a = new Account();\n"
                    "        a.balance = sc.nextInt();\n"
                    "        System.out.println(a.balance);"),
              _joop("class Account {\n"
                    "    private int balance;\n"
                    "\n"
                    "    void deposit(int amount) {\n"
                    "        if (amount > 0) balance += amount;\n"
                    "    }\n"
                    "\n"
                    "    int getBalance() {\n"
                    "        return balance;\n"
                    "    }\n"
                    "}",
                    "        Account a = new Account();\n"
                    "        a.deposit(sc.nextInt());\n"
                    "        System.out.println(a.getBalance());"),
              [_case(v, max(0, v)) for v in (100, 0, -25, 7)],
              hints=["`private` means only `Account`'s own code may touch the field.",
                     "The class already offers the two doors you need.",
                     "`a.deposit(...)` to write, `a.getBalance()` to read — and note a "
                     "negative input now yields 0 rather than a negative balance."]),

        _jch("j12-pv-counter", "Encapsulate a counter", "Medium",
             "Write `Tally`: a `private int` count that starts at 0, a `bump()` "
             "method that adds one, an `add(int n)` that adds `n` but **ignores "
             "anything negative**, and a `get()` that returns the total. Nothing "
             "outside the class may touch the field. Write the whole class where you "
             "see `____`.",
             _joop("class Tally {\n"
                   "    private int count;\n"
                   "\n"
                   "    void bump() {\n"
                   "        count++;\n"
                   "    }\n"
                   "\n"
                   "    void add(int n) {\n"
                   "        if (n > 0) count += n;\n"
                   "    }\n"
                   "\n"
                   "    int get() {\n"
                   "        return count;\n"
                   "    }\n"
                   "}",
                   "        Tally t = new Tally();\n"
                   "        t.bump();\n"
                   "        t.add(sc.nextInt());\n"
                   "        t.add(sc.nextInt());\n"
                   "        t.bump();\n"
                   "        System.out.println(t.get());"),
             "class Tally {\n"
             "    private int count;\n"
             "\n"
             "    void bump() {\n"
             "        count++;\n"
             "    }\n"
             "\n"
             "    void add(int n) {\n"
             "        if (n > 0) count += n;\n"
             "    }\n"
             "\n"
             "    int get() {\n"
             "        return count;\n"
             "    }\n"
             "}",
             [_case(f"{x}\n{y}", 2 + max(0, x) + max(0, y))
              for (x, y) in ((5, 3), (5, -3), (-1, -2), (0, 0))],
             hints=["`private int count;` starts at 0 on its own — fields get defaults.",
                    "`bump()` and `add(int)` return nothing, so they are `void`.",
                    "`add` guards with `if (n > 0)`; a negative must leave the count alone, "
                    "not subtract.",
                    "`main` calls `bump()` twice, so every expected answer starts from 2."]),
    ],
    quiz=[
        _jq("What is the sensible default for a new class's members?",
            ["Fields private; methods only as public as callers actually need",
             "Everything public, then narrow later",
             "Everything private, including methods",
             "Everything package-private"],
            0,
            "Widening access later is painless. Narrowing it breaks every caller, so start "
            "closed."),
        _jq("Why do this course's exercises write `private` explicitly rather than relying on the default?",
            ["Everything is in one file and one package, so the default is still reachable from Main",
             "Because Java requires a modifier",
             "For performance",
             "Because package-private does not exist"],
            0,
            "Package-private would look like it worked here and then fail to protect anything "
            "in a real multi-package project."),
    ],
))

# --- 12.2 Getters and setters ----------------------------------------------

_M12.append(_jlesson(
    "m12-accessors", "Getters and setters",
    "The deliberate door — and why it is not just a public field with extra steps.",
    """
With the field private, you choose what the outside world may do:

```java
class Person {
    private String name;
    private int age;

    String getName() { return name; }              // read-only: no setter
    int getAge()     { return age; }

    void setAge(int age) {                          // writable, but on your terms
        if (age >= 0) this.age = age;
    }
}
```

**Naming is a convention with teeth.** `getX()` / `setX(...)`, and `isX()` for a
`boolean`. It is not enforced by the compiler, but frameworks — Jackson for
JSON, JPA for databases, Spring for wiring — find your fields by looking for
exactly these names. Follow it and things work for free; deviate and you will
spend an afternoon finding out why.

**`this.age = age;` again.** The parameter is named after the field, so it
shadows it. Module 11's rule, in the place it appears most.

**"Isn't a getter and setter pair just a public field?"** It is the question
worth asking, and the answer is what makes the pattern worth its noise:

- **You can validate.** `setAge(-5)` can refuse; `age = -5` cannot.
- **You can omit one.** No setter means read-only from outside, which a public
  field cannot express.
- **You can change the representation** without changing callers. Store a
  birth year and compute the age; `getAge()` still works.
- **You can add behaviour later** — logging, laziness, notification — in one
  place.

A getter/setter pair with no validation on a field with no rules genuinely *is*
ceremony, and modern Java has `record` for exactly that case. But the moment
there is a rule, the door is what enforces it.

**Setters do not have to be setters.** Often the honest API is a verb, not a
property:

```java
void deposit(int amount)          // better than setBalance(getBalance() + n)
void celebrateBirthday()          // better than setAge(getAge() + 1)
```

`setBalance` invites a caller to compute the new balance themselves, which puts
the rule back outside the class. Name the operation, not the field.

**Getters that return objects leak.** `getItems()` returning your private array
hands the caller a reference straight into your object — lesson 12.4.
""",
    warmup=[
        _jq("```java\nvoid setAge(int age) { this.age = this.age; }\n```\nAfter `p.setAge(30)`:",
            ["age is unchanged — the field was assigned to itself",
             "age is 30", "age is 0", "It does not compile"],
            0,
            "Both sides name the field, so nothing moves. The parameter is never used. "
            "`this.age = age;` is the correct line."),
        _jq("Which is the better API for adding money to an account?",
            ["deposit(int amount) — the rule stays inside the class",
             "setBalance(int newBalance)",
             "A public balance field",
             "getBalance() returning a mutable reference"],
            0,
            "`setBalance` makes the caller compute the new value, which moves the arithmetic "
            "— and the rule — outside the class."),
    ],
    exercises=[
        _je("j12-ac-getter", "Write the getter",
            "`name` is private and read-only from outside. Replace `____` with the "
            "getter.",
            _joop("class Person {\n"
                  "    private String name;\n"
                  "\n"
                  "    Person(String name) {\n"
                  "        this.name = name;\n"
                  "    }\n"
                  "\n"
                  "    String getName() {\n"
                  "        return name;\n"
                  "    }\n"
                  "}",
                  "        Person p = new Person(sc.nextLine());\n"
                  "        System.out.println(p.getName());"),
            "    String getName() {\n"
            "        return name;\n"
            "    }",
            [_scase(s, s) for s in ("Ada", "Grace Hopper", "x")],
            hints=["The convention is `get` plus the capitalised field name.",
                   "Its return type is the field's type.",
                   "`String getName() { return name; }`"],
            difficulty="Intro"),

        _je("j12-ac-setter", "Write the setter",
            "`setAge` should store the new age, but only when it is not negative. "
            "Replace `____` with the body — mind the shadowing.",
            _joop("class Person {\n"
                  "    private int age;\n"
                  "\n"
                  "    void setAge(int age) {\n"
                  "        if (age >= 0) this.age = age;\n"
                  "    }\n"
                  "\n"
                  "    int getAge() {\n"
                  "        return age;\n"
                  "    }\n"
                  "}",
                  "        Person p = new Person();\n"
                  "        p.setAge(sc.nextInt());\n"
                  "        p.setAge(sc.nextInt());\n"
                  "        System.out.println(p.getAge());"),
            "        if (age >= 0) this.age = age;",
            [_case(f"{a}\n{b}", (b if b >= 0 else (a if a >= 0 else 0)))
             for (a, b) in ((30, 31), (30, -1), (-5, -6), (0, 40))],
            hints=["Guard first, then assign.",
                   "The parameter shadows the field, so the left side needs `this.`.",
                   "`if (age >= 0) this.age = age;` — a rejected value leaves the previous "
                   "one in place."]),

        _jfix("j12-ac-selfassign", "The setter that stores nothing",
              "`setScore` never changes anything — `getScore()` always returns 0. "
              "Both sides of the assignment name the same thing.",
              _joop("class Player {\n"
                    "    private int score;\n"
                    "\n"
                    "    void setScore(int score) {\n"
                    "        this.score = this.score;\n"
                    "    }\n"
                    "\n"
                    "    int getScore() {\n"
                    "        return score;\n"
                    "    }\n"
                    "}",
                    "        Player p = new Player();\n"
                    "        p.setScore(sc.nextInt());\n"
                    "        System.out.println(p.getScore());"),
              _joop("class Player {\n"
                    "    private int score;\n"
                    "\n"
                    "    void setScore(int score) {\n"
                    "        this.score = score;\n"
                    "    }\n"
                    "\n"
                    "    int getScore() {\n"
                    "        return score;\n"
                    "    }\n"
                    "}",
                    "        Player p = new Player();\n"
                    "        p.setScore(sc.nextInt());\n"
                    "        System.out.println(p.getScore());"),
              [_case(v, v) for v in (42, 0, -3, 100)],
              hints=["What does `this.score` mean on the right-hand side?",
                     "The parameter is never read.",
                     "`this.score = score;` — field on the left, parameter on the right."],
              difficulty="Intro"),

        _jch("j12-ac-verb", "Name the operation, not the field", "Medium",
             "Write `Account` with a private `balance`, a `getBalance()`, and two "
             "**verbs** rather than a setter: `deposit(int amount)` adds a positive "
             "amount, and `withdraw(int amount)` subtracts one **only if the balance "
             "can cover it** — otherwise it does nothing. Both ignore amounts that "
             "are not positive. Write the whole class where you see `____`.",
             _joop("class Account {\n"
                   "    private int balance;\n"
                   "\n"
                   "    void deposit(int amount) {\n"
                   "        if (amount > 0) balance += amount;\n"
                   "    }\n"
                   "\n"
                   "    void withdraw(int amount) {\n"
                   "        if (amount > 0 && amount <= balance) balance -= amount;\n"
                   "    }\n"
                   "\n"
                   "    int getBalance() {\n"
                   "        return balance;\n"
                   "    }\n"
                   "}",
                   "        Account a = new Account();\n"
                   "        a.deposit(sc.nextInt());\n"
                   "        a.withdraw(sc.nextInt());\n"
                   "        a.deposit(sc.nextInt());\n"
                   "        System.out.println(a.getBalance());"),
             "class Account {\n"
             "    private int balance;\n"
             "\n"
             "    void deposit(int amount) {\n"
             "        if (amount > 0) balance += amount;\n"
             "    }\n"
             "\n"
             "    void withdraw(int amount) {\n"
             "        if (amount > 0 && amount <= balance) balance -= amount;\n"
             "    }\n"
             "\n"
             "    int getBalance() {\n"
             "        return balance;\n"
             "    }\n"
             "}",
             [_case(f"{d1}\n{w}\n{d2}",
                    (lambda b: b + (d2 if d2 > 0 else 0))(
                        (lambda b: b - (w if (w > 0 and w <= b) else 0))(
                            d1 if d1 > 0 else 0)))
              for (d1, w, d2) in ((100, 30, 5), (100, 500, 0), (100, -5, 20),
                                  (-10, 10, 50), (50, 50, 50))],
             hints=["`private int balance;` and one getter — no setter at all.",
                    "`deposit` guards on `amount > 0`.",
                    "`withdraw` needs BOTH guards: positive, and not more than the balance. "
                    "An overdraft attempt must leave the balance untouched.",
                    "Neither verb returns anything, so both are `void`."]),
    ],
    quiz=[
        _jq("Why follow the `getX`/`setX`/`isX` naming convention exactly?",
            ["Frameworks like Jackson, JPA and Spring locate properties by those names",
             "The compiler enforces it",
             "It makes the code faster",
             "It is required for private fields"],
            0,
            "It is a convention, not a rule — but a huge amount of the ecosystem is built on "
            "it, so deviating costs you working defaults."),
        _jq("A field with no rules at all, with a trivial getter and setter, is…",
            ["ceremony — which is what `record` exists to remove",
             "always correct design",
             "a compile error",
             "faster than a public field"],
            0,
            "The pattern earns its noise when there is a rule to enforce or a representation "
            "to hide. Java's `record` covers the plain-data case."),
    ],
))

# --- 12.3 Invariants --------------------------------------------------------

_M12.append(_jlesson(
    "m12-invariant", "Class invariants",
    "The sentence that is always true — and the two places you have to enforce it.",
    """
A **class invariant** is a statement that is true of every instance, at every
moment a caller can observe it. For an `Account`: *the balance is never
negative*. For a `Range`: *low is never greater than high*.

Writing the invariant down as one sentence is most of the work. Enforcing it
takes exactly two things:

**1. The constructor must establish it.** An object should never exist in an
invalid state, not even briefly.

**2. Every mutator must preserve it.** A method that can break the rule has to
check before it commits.

Miss either and the guarantee is worthless. Validating in the setter but not the
constructor means an object can be *born* broken:

```java
class Account {
    private int balance;

    Account(int balance) {
        this.balance = balance;             // no check — new Account(-500) is legal
    }

    void withdraw(int amount) {
        if (amount <= balance) balance -= amount;      // carefully guarded...
    }
}
```

Every withdrawal is checked and the object is still wrong, because it started
wrong. This is the most common encapsulation bug there is: the rule was applied
to the *operations* and not to *construction*.

**Three ways to handle bad input,** and choosing on purpose matters:

```java
// clamp — force it into range
if (v < MIN) this.v = MIN; else if (v > MAX) this.v = MAX; else this.v = v;

// reject silently — leave the old value alone
if (v >= MIN && v <= MAX) this.v = v;

// refuse loudly — the honest choice for a constructor
if (v < MIN) throw new IllegalArgumentException("too small");
```

Throwing is what production code does, and it gets its own module in Part 5 of
the roadmap. Until then these exercises clamp or reject, and say which.

**Do not duplicate the rule.** If the constructor and the setter enforce the
same thing, the constructor should call the setter:

```java
Account(int balance) {
    setBalance(balance);            // one copy of the rule
}
```

Two copies drift. Someone loosens one and forgets the other, and the invariant
quietly stops holding. (There is a wrinkle once inheritance arrives — calling an
overridable method from a constructor is risky — which is why `final` on such
methods, or a private helper, is the safer habit.)
""",
    warmup=[
        _jq("A class validates in every setter but not in its constructor. What is possible?",
            ["An object that is invalid from the moment it is created",
             "Nothing — the setters cover it",
             "A compile error",
             "The constructor throws automatically"],
            0,
            "The invariant has to be established by the constructor and then preserved by "
            "each mutator. Only half is no guarantee at all."),
        _jq("Why should a constructor call the setter rather than repeating its check?",
            ["So the rule exists in exactly one place and cannot drift",
             "Because constructors cannot contain `if`",
             "For performance",
             "It shouldn't — duplication is safer"],
            0,
            "Two copies of a rule is one copy plus a future bug. (Once inheritance is in "
            "play, prefer a `private` or `final` helper so a subclass cannot change what the "
            "constructor runs.)"),
    ],
    exercises=[
        _je("j12-in-clamp", "Clamp it into range",
            "`Volume` must always sit between 0 and 100. Replace `____` with the "
            "body of `set`, which clamps anything outside that range.",
            _joop("class Volume {\n"
                  "    private int level;\n"
                  "\n"
                  "    void set(int level) {\n"
                  "        if (level < 0) this.level = 0;\n"
                  "        else if (level > 100) this.level = 100;\n"
                  "        else this.level = level;\n"
                  "    }\n"
                  "\n"
                  "    int get() {\n"
                  "        return level;\n"
                  "    }\n"
                  "}",
                  "        Volume v = new Volume();\n"
                  "        v.set(sc.nextInt());\n"
                  "        System.out.println(v.get());"),
            "        if (level < 0) this.level = 0;\n"
            "        else if (level > 100) this.level = 100;\n"
            "        else this.level = level;",
            [_case(x, min(100, max(0, x))) for x in (50, -20, 200, 0, 100)],
            hints=["Three cases: too low, too high, and fine.",
                   "Every branch assigns the field, so use if / else-if / else.",
                   "The parameter shadows the field, so every assignment needs `this.level`."]),

        _je("j12-in-ctor", "Establish it at birth",
            "The constructor must not let an invalid object exist. Replace `____` "
            "with its body — reuse the setter rather than repeating its rule.",
            _joop("class Volume {\n"
                  "    private int level;\n"
                  "\n"
                  "    Volume(int level) {\n"
                  "        set(level);\n"
                  "    }\n"
                  "\n"
                  "    void set(int level) {\n"
                  "        if (level < 0) this.level = 0;\n"
                  "        else if (level > 100) this.level = 100;\n"
                  "        else this.level = level;\n"
                  "    }\n"
                  "\n"
                  "    int get() {\n"
                  "        return level;\n"
                  "    }\n"
                  "}",
                  "        Volume v = new Volume(sc.nextInt());\n"
                  "        System.out.println(v.get());"),
            "        set(level);",
            [_case(x, min(100, max(0, x))) for x in (50, -20, 200, 100)],
            hints=["The rule already exists, one method below.",
                   "Call it instead of copying the three branches.",
                   "`set(level);`"],
            difficulty="Medium"),

        _jfix("j12-in-born", "Born broken",
              "`Account` guards every withdrawal carefully — and still allows a "
              "negative balance, because the constructor does not check its argument. "
              "Fix the constructor so a negative opening balance becomes 0.",
              _joop("class Account {\n"
                    "    private int balance;\n"
                    "\n"
                    "    Account(int balance) {\n"
                    "        this.balance = balance;\n"
                    "    }\n"
                    "\n"
                    "    void withdraw(int amount) {\n"
                    "        if (amount > 0 && amount <= balance) balance -= amount;\n"
                    "    }\n"
                    "\n"
                    "    int getBalance() {\n"
                    "        return balance;\n"
                    "    }\n"
                    "}",
                    "        Account a = new Account(sc.nextInt());\n"
                    "        a.withdraw(sc.nextInt());\n"
                    "        System.out.println(a.getBalance());"),
              _joop("class Account {\n"
                    "    private int balance;\n"
                    "\n"
                    "    Account(int balance) {\n"
                    "        if (balance < 0) this.balance = 0;\n"
                    "        else this.balance = balance;\n"
                    "    }\n"
                    "\n"
                    "    void withdraw(int amount) {\n"
                    "        if (amount > 0 && amount <= balance) balance -= amount;\n"
                    "    }\n"
                    "\n"
                    "    int getBalance() {\n"
                    "        return balance;\n"
                    "    }\n"
                    "}",
                    "        Account a = new Account(sc.nextInt());\n"
                    "        a.withdraw(sc.nextInt());\n"
                    "        System.out.println(a.getBalance());"),
              [_case(f"{o}\n{w}",
                     (lambda b: b - (w if (w > 0 and w <= b) else 0))(max(0, o)))
               for (o, w) in ((100, 30), (-500, 10), (-1, 0), (50, 80))],
              hints=["Where can the balance become negative, given every withdrawal is "
                     "guarded?",
                     "The object is invalid before any method is called.",
                     "Guard the constructor: a negative opening balance becomes 0."],
              difficulty="Medium"),

        _jch("j12-in-range", "A range that cannot be backwards", "Hard",
             "Write `Range` with private `low` and `high` and the invariant **low is "
             "never greater than high**. Its constructor takes two numbers in either "
             "order and stores them the right way round. Add `length()` returning "
             "`high - low`, and `contains(int v)` returning whether `v` lies within "
             "the range inclusive. Write the whole class where you see `____`.",
             _joop("class Range {\n"
                   "    private int low;\n"
                   "    private int high;\n"
                   "\n"
                   "    Range(int a, int b) {\n"
                   "        if (a <= b) {\n"
                   "            low = a;\n"
                   "            high = b;\n"
                   "        } else {\n"
                   "            low = b;\n"
                   "            high = a;\n"
                   "        }\n"
                   "    }\n"
                   "\n"
                   "    int length() {\n"
                   "        return high - low;\n"
                   "    }\n"
                   "\n"
                   "    boolean contains(int v) {\n"
                   "        return v >= low && v <= high;\n"
                   "    }\n"
                   "}",
                   "        Range r = new Range(sc.nextInt(), sc.nextInt());\n"
                   "        System.out.println(r.length());\n"
                   "        System.out.println(r.contains(sc.nextInt()));"),
             "class Range {\n"
             "    private int low;\n"
             "    private int high;\n"
             "\n"
             "    Range(int a, int b) {\n"
             "        if (a <= b) {\n"
             "            low = a;\n"
             "            high = b;\n"
             "        } else {\n"
             "            low = b;\n"
             "            high = a;\n"
             "        }\n"
             "    }\n"
             "\n"
             "    int length() {\n"
             "        return high - low;\n"
             "    }\n"
             "\n"
             "    boolean contains(int v) {\n"
             "        return v >= low && v <= high;\n"
             "    }\n"
             "}",
             [_case(f"{a}\n{b}\n{v}", _nl(abs(b - a),
                                          _jbool(min(a, b) <= v <= max(a, b))))
              for (a, b, v) in ((1, 5, 3), (5, 1, 3), (5, 1, 9),
                                (2, 2, 2), (-3, 4, -3), (4, -3, 5))],
             hints=["The constructor establishes the invariant by ordering its two arguments.",
                    "Name the parameters `a` and `b` rather than `low`/`high` — nothing is "
                    "shadowed, so no `this.` is needed.",
                    "`length()` can just be `high - low`, because the constructor guaranteed "
                    "the order. That guarantee is the whole point of an invariant.",
                    "`contains` is inclusive at both ends: `v >= low && v <= high`."]),
    ],
    quiz=[
        _jq("What are the two obligations that make an invariant real?",
            ["The constructor establishes it, and every mutator preserves it",
             "Every field is final, and every method is private",
             "The class is immutable, and it has no setters",
             "It is documented, and it is tested"],
            0,
            "Half of it is no guarantee. The most common failure is guarding the operations "
            "and forgetting construction."),
        _jq("`length()` returns `high - low` with no `Math.abs`. Why is that safe?",
            ["The constructor guarantees low <= high, so the difference cannot be negative",
             "Because subtraction is always positive",
             "It isn't safe",
             "Because both fields are private"],
            0,
            "That is exactly what an invariant buys: every other method can rely on it and "
            "stop re-checking. Guarantees established once simplify everything downstream."),
    ],
))

# --- 12.4 Immutability and defensive copying -------------------------------

_M12.append(_jlesson(
    "m12-immutable", "Immutable objects and defensive copying",
    "The aliasing lesson, one last time — and the two copies that close the leaks.",
    """
An **immutable** object cannot change after construction. `String` is the one
you already know; module 11 made `Point` immutable with `final` fields. The
recipe:

1. Every field `private final`.
2. No setters, and no method that assigns a field.
3. Anything that "changes" the object returns a **new** one.
4. **Defensively copy any mutable object in and out.**

Step 4 is the one people miss, and it is module 1's aliasing lesson arriving for
the last time.

**The leak going in.** A constructor that stores the array it was handed is
storing an array the caller still holds:

```java
class Bag {
    private final int[] items;

    Bag(int[] items) {
        this.items = items;              // LEAK — the caller kept a reference
    }
}

int[] source = {1, 2, 3};
Bag b = new Bag(source);
source[0] = 999;                          // ...and just reached inside b
```

`final` did not help: it freezes the *reference*, never the array. The fix is to
copy on the way in:

```java
this.items = Arrays.copyOf(items, items.length);
```

**The leak coming out.** A getter that returns the field hands out a reference
into your private state:

```java
int[] getItems() { return items; }        // LEAK — caller can write to it

int[] copy = b.getItems();
copy[0] = 999;                             // ...and just reached inside b again
```

Same fix, other direction:

```java
int[] getItems() { return Arrays.copyOf(items, items.length); }
```

**A private field is not a protected field.** `private` controls who can name
the field; it says nothing about who has a reference to the object it points
at. Any mutable object crossing your boundary — in or out — has to be copied,
or you are sharing state you promised to own.

**When to skip the copy.** If the field type is itself immutable — `String`,
`Integer`, another immutable class of yours — there is nothing to defend
against, and copying would be waste. That is the real argument for immutability:
immutable things compose without ceremony.

**What it buys.** Free to share with no fear of a surprise change, safe as a
`HashMap` key (its hash cannot shift underneath the map), and automatically safe
across threads — nobody can write to it, so there is nothing to race. That is
why `String` is immutable, and it is the same reasoning from module 6.

**The cost** is allocation: every "change" builds a new object, and copying a
big array on every call is real. Immutability by default, mutability where a
measurement says so.
""",
    warmup=[
        _jq("```java\nint[] src = {1,2,3};\nBag b = new Bag(src);   // constructor does: this.items = items;\nsrc[0] = 999;\n```\nWhat is inside b?",
            ["{999, 2, 3} — the caller still holds the same array",
             "{1, 2, 3} — final protected it",
             "A compile error",
             "{0, 0, 0}"],
            0,
            "There is one array with two holders. `final` froze the field, not the array — "
            "module 1's distinction, exactly."),
        _jq("A getter returns the private array field directly. What can a caller do?",
            ["Write into it, changing the object's private state",
             "Nothing — the field is private",
             "Only read it",
             "Only if the field is not final"],
            0,
            "`private` controls who can name the field. Once a reference escapes, the access "
            "modifier is irrelevant."),
    ],
    exercises=[
        _je("j12-im-copyin", "Copy on the way in",
            "`Bag` must not be affected when the caller later modifies the array it "
            "passed in. Replace `____` with the constructor's assignment.",
            _joop("class Bag {\n"
                  "    private final int[] items;\n"
                  "\n"
                  "    Bag(int[] items) {\n"
                  "        this.items = Arrays.copyOf(items, items.length);\n"
                  "    }\n"
                  "\n"
                  "    int total() {\n"
                  "        int s = 0;\n"
                  "        for (int x : items) s += x;\n"
                  "        return s;\n"
                  "    }\n"
                  "}",
                  _RD_ARR
                  + "        Bag b = new Bag(a);\n"
                    "        a[0] = 1000;\n"
                    "        System.out.println(b.total());"),
            "        this.items = Arrays.copyOf(items, items.length);",
            [_acase(a, sum(a)) for a in ([1, 2, 3], [5], [-4, 4, 7], [10, 20])],
            hints=["Storing the parameter directly would share the caller's array.",
                   "Module 1's `Arrays.copyOf` makes an independent copy.",
                   "`this.items = Arrays.copyOf(items, items.length);`"],
            difficulty="Medium"),

        _je("j12-im-copyout", "Copy on the way out",
            "`getItems` must not hand callers a reference into the object's private "
            "state. Replace `____` with its body.",
            _joop("class Bag {\n"
                  "    private final int[] items;\n"
                  "\n"
                  "    Bag(int[] items) {\n"
                  "        this.items = Arrays.copyOf(items, items.length);\n"
                  "    }\n"
                  "\n"
                  "    int[] getItems() {\n"
                  "        return Arrays.copyOf(items, items.length);\n"
                  "    }\n"
                  "\n"
                  "    int total() {\n"
                  "        int s = 0;\n"
                  "        for (int x : items) s += x;\n"
                  "        return s;\n"
                  "    }\n"
                  "}",
                  _RD_ARR
                  + "        Bag b = new Bag(a);\n"
                    "        int[] out = b.getItems();\n"
                    "        out[0] = 1000;\n"
                    "        System.out.println(b.total());"),
            "        return Arrays.copyOf(items, items.length);",
            [_acase(a, sum(a)) for a in ([1, 2, 3], [5], [-4, 4, 7], [10, 20])],
            hints=["Returning `items` would let the caller write into the object.",
                   "Hand back a copy instead.",
                   "`return Arrays.copyOf(items, items.length);`"],
            difficulty="Medium"),

        _jfix("j12-im-leak", "The final field that leaked anyway",
              "`Bag` stores a `private final int[]` and still changes when the caller "
              "modifies the array it was constructed from. `final` is not the "
              "problem — fix the constructor.",
              _joop("class Bag {\n"
                    "    private final int[] items;\n"
                    "\n"
                    "    Bag(int[] items) {\n"
                    "        this.items = items;\n"
                    "    }\n"
                    "\n"
                    "    int total() {\n"
                    "        int s = 0;\n"
                    "        for (int x : items) s += x;\n"
                    "        return s;\n"
                    "    }\n"
                    "}",
                    _RD_ARR
                    + "        Bag b = new Bag(a);\n"
                      "        a[0] = 1000;\n"
                      "        System.out.println(b.total());"),
              _joop("class Bag {\n"
                    "    private final int[] items;\n"
                    "\n"
                    "    Bag(int[] items) {\n"
                    "        this.items = Arrays.copyOf(items, items.length);\n"
                    "    }\n"
                    "\n"
                    "    int total() {\n"
                    "        int s = 0;\n"
                    "        for (int x : items) s += x;\n"
                    "        return s;\n"
                    "    }\n"
                    "}",
                    _RD_ARR
                    + "        Bag b = new Bag(a);\n"
                      "        a[0] = 1000;\n"
                      "        System.out.println(b.total());"),
              [_acase(a, sum(a)) for a in ([1, 2, 3], [7], [2, 2, 2, 2])],
              hints=["`final` freezes which array the field points at, not the array itself.",
                     "The caller still holds a reference to the very same array.",
                     "Copy it on the way in: `Arrays.copyOf(items, items.length)`."],
              difficulty="Medium"),

        _jch("j12-im-full", "A genuinely immutable bag", "Hard",
             "Write `Bag` so that neither the array it was given nor the array it "
             "hands back can reach inside it. It needs a `private final int[] items` "
             "copied in the constructor, a `getItems()` that copies on the way out, "
             "a `total()`, and a `withExtra(int v)` that returns a **new** `Bag` with "
             "one more element — leaving this one alone. Write the whole class where "
             "you see `____`.",
             _joop("class Bag {\n"
                   "    private final int[] items;\n"
                   "\n"
                   "    Bag(int[] items) {\n"
                   "        this.items = Arrays.copyOf(items, items.length);\n"
                   "    }\n"
                   "\n"
                   "    int[] getItems() {\n"
                   "        return Arrays.copyOf(items, items.length);\n"
                   "    }\n"
                   "\n"
                   "    int total() {\n"
                   "        int s = 0;\n"
                   "        for (int x : items) s += x;\n"
                   "        return s;\n"
                   "    }\n"
                   "\n"
                   "    Bag withExtra(int v) {\n"
                   "        int[] bigger = Arrays.copyOf(items, items.length + 1);\n"
                   "        bigger[items.length] = v;\n"
                   "        return new Bag(bigger);\n"
                   "    }\n"
                   "}",
                   _RD_ARR
                   + "        int v = sc.nextInt();\n"
                     "        Bag b = new Bag(a);\n"
                     "        a[0] = 1000;\n"
                     "        int[] out = b.getItems();\n"
                     "        out[0] = 2000;\n"
                     "        Bag bigger = b.withExtra(v);\n"
                     "        System.out.println(b.total());\n"
                     "        System.out.println(bigger.total());"),
             "class Bag {\n"
             "    private final int[] items;\n"
             "\n"
             "    Bag(int[] items) {\n"
             "        this.items = Arrays.copyOf(items, items.length);\n"
             "    }\n"
             "\n"
             "    int[] getItems() {\n"
             "        return Arrays.copyOf(items, items.length);\n"
             "    }\n"
             "\n"
             "    int total() {\n"
             "        int s = 0;\n"
             "        for (int x : items) s += x;\n"
             "        return s;\n"
             "    }\n"
             "\n"
             "    Bag withExtra(int v) {\n"
             "        int[] bigger = Arrays.copyOf(items, items.length + 1);\n"
             "        bigger[items.length] = v;\n"
             "        return new Bag(bigger);\n"
             "    }\n"
             "}",
             [_akcase(a, v, _nl(sum(a), sum(a) + v))
              for (a, v) in (([1, 2, 3], 10), ([5], -5), ([2, 2], 0), ([7, 8, 9], 6))],
             hints=["Two copies: one in the constructor, one in the getter. Both are "
                    "`Arrays.copyOf(items, items.length)`.",
                    "`main` deliberately writes to both the source array and the returned "
                    "array — if either copy is missing, `total()` changes and the case fails.",
                    "`withExtra` grows a copy by one (module 1's `copyOf` trick), fills the "
                    "last slot, and returns `new Bag(bigger)`.",
                    "Nothing outside the constructor may assign `items` — `final` will enforce "
                    "that for you."]),
    ],
    quiz=[
        _jq("Which is NOT part of making a class immutable?",
            ["Marking the class `static`",
             "Making every field `private final`",
             "Copying mutable arguments in the constructor",
             "Returning copies from getters"],
            0,
            "`static` on a class means something else entirely (nested classes). The other "
            "three are the recipe, plus 'no setters'."),
        _jq("Your immutable class has a `private final String name` field. Copy it defensively?",
            ["No — String is already immutable, so there is nothing to defend against",
             "Yes, always copy every field",
             "Yes, with new String(name)",
             "Only if it might be null"],
            0,
            "Immutable fields need no defence. That composability is the strongest practical "
            "argument for making your own types immutable."),
    ],
))


# --- Capstone ---------------------------------------------------------------

def _m12_account(opening, ops):
    """Python mirror: opening balance is clamped at 0, then each op applied."""
    bal = max(0, opening)
    applied = 0
    for (kind, amt) in ops:
        if kind == 1:                       # deposit
            if amt > 0:
                bal += amt
                applied += 1
        else:                                # withdraw
            if 0 < amt <= bal:
                bal -= amt
                applied += 1
    return _nl(f"balance={bal}", f"applied={applied}")


def _m12_case(opening, ops):
    lines = [str(opening), str(len(ops))] + [f"{k} {v}" for (k, v) in ops]
    return _case("\n".join(lines), _m12_account(opening, ops))


_M12_CAP = _jcap(
    "BankAccount",
    """
The classic encapsulation exercise, with the invariant stated up front.

**The invariant: the balance is never negative, and no operation may break it.**

Read an opening balance, then `n`, then `n` operation lines. Each line is a type
code and an amount:

| Line | Meaning |
|---|---|
| `1 amount` | deposit |
| `2 amount` | withdraw |

Print:

```
balance=<the final balance>
applied=<how many operations actually took effect>
```

`BankAccount` needs:

| Member | Kind |
|---|---|
| `balance` | `private int` — nothing outside may assign it |
| `applied` | `private int` — counts operations that took effect |
| `BankAccount(int opening)` | clamps a negative opening balance to 0 |
| `deposit(int amount)` | applies it only when `amount > 0` |
| `withdraw(int amount)` | applies it only when `amount > 0` **and** `amount <= balance` |
| `getBalance()`, `getApplied()` | read-only accessors |

The rules the hidden cases probe:

- **A negative opening balance becomes 0**, and does not count as an applied
  operation. Guarding the operations but not the constructor is the bug from
  lesson 12.3, and one test case is built to catch exactly it.
- **A rejected operation changes nothing** — not the balance, not the counter.
  An overdraft attempt is not a partial withdrawal.
- **There is no setter.** `deposit` and `withdraw` are verbs; a caller must
  never be able to compute a balance and hand it in.
""",
    _jch("j12-cap-account", "BankAccount", "Hard",
         "Write the whole `BankAccount` class where you see `____`. `main` is "
         "already written and drives it.",
         _joop("class BankAccount {\n"
               "    private int balance;\n"
               "    private int applied;\n"
               "\n"
               "    BankAccount(int opening) {\n"
               "        if (opening < 0) this.balance = 0;\n"
               "        else this.balance = opening;\n"
               "    }\n"
               "\n"
               "    void deposit(int amount) {\n"
               "        if (amount > 0) {\n"
               "            balance += amount;\n"
               "            applied++;\n"
               "        }\n"
               "    }\n"
               "\n"
               "    void withdraw(int amount) {\n"
               "        if (amount > 0 && amount <= balance) {\n"
               "            balance -= amount;\n"
               "            applied++;\n"
               "        }\n"
               "    }\n"
               "\n"
               "    int getBalance() {\n"
               "        return balance;\n"
               "    }\n"
               "\n"
               "    int getApplied() {\n"
               "        return applied;\n"
               "    }\n"
               "}",
               "        BankAccount acc = new BankAccount(sc.nextInt());\n"
               "        int n = sc.nextInt();\n"
               "        for (int i = 0; i < n; i++) {\n"
               "            int type = sc.nextInt();\n"
               "            int amount = sc.nextInt();\n"
               "            if (type == 1) acc.deposit(amount);\n"
               "            else acc.withdraw(amount);\n"
               "        }\n"
               '        System.out.println("balance=" + acc.getBalance());\n'
               '        System.out.println("applied=" + acc.getApplied());'),
         "class BankAccount {\n"
         "    private int balance;\n"
         "    private int applied;\n"
         "\n"
         "    BankAccount(int opening) {\n"
         "        if (opening < 0) this.balance = 0;\n"
         "        else this.balance = opening;\n"
         "    }\n"
         "\n"
         "    void deposit(int amount) {\n"
         "        if (amount > 0) {\n"
         "            balance += amount;\n"
         "            applied++;\n"
         "        }\n"
         "    }\n"
         "\n"
         "    void withdraw(int amount) {\n"
         "        if (amount > 0 && amount <= balance) {\n"
         "            balance -= amount;\n"
         "            applied++;\n"
         "        }\n"
         "    }\n"
         "\n"
         "    int getBalance() {\n"
         "        return balance;\n"
         "    }\n"
         "\n"
         "    int getApplied() {\n"
         "        return applied;\n"
         "    }\n"
         "}",
         [_m12_case(opening, ops)
          for (opening, ops) in (
              (100, [(1, 50), (2, 30), (2, 500), (1, -10)]),
              (-500, [(1, 10)]),
              (0, [(2, 1), (1, 0), (1, 25), (2, 25)]),
              (50, [(2, 50), (2, 1)]),
              (1000, [(1, 1), (1, 2), (1, 3), (2, 6)]))],
         hints=["Both fields are `private int` and start at 0 by default.",
                "The constructor clamps: a negative opening balance becomes 0. That is the "
                "case a class which only guards its operations gets wrong.",
                "`deposit` applies only when `amount > 0`; `withdraw` needs `amount > 0 && "
                "amount <= balance`.",
                "Bump `applied` INSIDE each guard, so a rejected operation changes nothing "
                "at all.",
                "No setter — `main` only ever calls the two verbs and the two getters."]),
    example_io="stdin:  100\n        4\n        1 50\n        2 30\n        2 500\n        1 -10\n\n"
               "stdout: balance=120\n        applied=2",
    rubric=[
        "`balance` and `applied` are private; `main` cannot assign either.",
        "A negative opening balance is clamped to 0 by the constructor.",
        "An overdraft attempt changes neither the balance nor the counter.",
        "A non-positive deposit is ignored entirely.",
        "`applied` counts only the operations that actually took effect.",
        "There is no `setBalance` — the only ways in are `deposit` and `withdraw`.",
    ],
)


_MODULES.append(_jmod(
    12, 4, "Object-oriented programming",
    "Encapsulation",
    "Seal the data with the rules that govern it: private fields, deliberate "
    "accessors, invariants that hold from construction onward, and the defensive "
    "copies that stop a private field leaking.",
    """
Module 11 gave you types. This one gives you *guarantees*.

The argument runs in a straight line. A public field is a write path with no
code in it, so no rule about it can be enforced — therefore fields are
`private`. A private field needs a deliberate door, and that door is where
validation lives. A rule is only real if the **constructor establishes it** and
**every mutator preserves it**; guarding the operations and forgetting
construction is the most common encapsulation bug there is.

The module ends where module 1 began. A `private final int[]` is still shared
with whoever handed it to you and whoever you return it to, because `final`
freezes the reference and never the object. Defensive copying — in and out — is
the last appearance of the aliasing lesson, and the reason immutable types are
worth the allocation.
""",
    _M12,
    capstone=_M12_CAP,
    objectives=[
        "Choose between `private`, package-private, `protected` and `public`, and default to private fields.",
        "Write getters and setters to convention, and say what they buy over a public field.",
        "Prefer a verb (`deposit`) to a setter when the operation carries a rule.",
        "State a class invariant in one sentence and enforce it in the constructor and every mutator.",
        "Choose deliberately between clamping, rejecting and refusing invalid input.",
        "Build an immutable class: private final fields, no setters, and a new object per change.",
        "Defensively copy mutable arguments in and mutable return values out.",
    ],
    why="Encapsulation is what makes a class trustworthy — it is the difference between "
        "a type that guarantees something and a struct that hopes. The defensive-copying "
        "leak in particular is a real production bug, not a textbook one.",
    est_minutes=270,
    glossary=[
        _jg("encapsulation", "Sealing data together with the rules that govern it, so every "
                             "change goes through code you control."),
        _jg("private", "Visible only inside the declaring class — including from another "
                       "instance of that same class."),
        _jg("package-private", "The default when you write no modifier: visible to the whole "
                               "package. In this one-file course that still includes `Main`."),
        _jg("accessor / getter", "A method returning a field's value, named `getX` or `isX` "
                                 "by convention that frameworks depend on."),
        _jg("mutator / setter", "A method that changes state. Often better expressed as a "
                                "verb (`deposit`) than as `setBalance`."),
        _jg("class invariant", "A statement true of every instance at every observable moment "
                               "— established by the constructor, preserved by each mutator."),
        _jg("clamping", "Forcing an out-of-range value to the nearest legal one, as opposed "
                        "to rejecting it or throwing."),
        _jg("immutable", "Unable to change after construction. Free to share, safe as a map "
                         "key, and thread-safe with no effort."),
        _jg("defensive copy", "Copying a mutable object as it crosses your boundary, in or "
                              "out, so no reference into your state escapes."),
    ],
    cheatsheet="""
```java
// --- the shape ----------------------------------------------------------
class Account {
    private int balance;                 // private: the ONLY way to guarantee
    private static final int MIN = 0;    //   anything about your own object

    Account(int opening) {
        setBalance(opening);             // constructor ESTABLISHES the invariant
    }

    private void setBalance(int v) {     // one copy of the rule
        if (v < MIN) balance = MIN; else balance = v;
    }

    void deposit(int amount) {           // a VERB, not setBalance
        if (amount > 0) balance += amount;
    }
    void withdraw(int amount) {          // each mutator PRESERVES the invariant
        if (amount > 0 && amount <= balance) balance -= amount;
    }
    int getBalance() { return balance; } // read-only from outside
}

// --- access levels, narrowest first ------------------------------------
private          // this class only
(none)           // package-private: the whole package
protected        // package + subclasses (module 13)
public           // everything

// --- handling bad input, pick on purpose -------------------------------
if (v < MIN) this.v = MIN; else if (v > MAX) this.v = MAX; else this.v = v;  // clamp
if (v >= MIN && v <= MAX) this.v = v;                                        // reject
if (v < MIN) throw new IllegalArgumentException("too small");                // refuse

// --- immutable class ----------------------------------------------------
class Bag {
    private final int[] items;                                  // 1. private final

    Bag(int[] items) {                                          // 4a. copy IN
        this.items = Arrays.copyOf(items, items.length);
    }
    int[] getItems() {                                          // 4b. copy OUT
        return Arrays.copyOf(items, items.length);
    }
    Bag withExtra(int v) {                                      // 3. new object
        int[] b = Arrays.copyOf(items, items.length + 1);
        b[items.length] = v;
        return new Bag(b);
    }
}                                                               // 2. no setters

// --- the trap -----------------------------------------------------------
private final int[] items;
this.items = items;      // final froze the REFERENCE; the caller still has one
return items;            // private froze the NAME; the caller now has a reference
// String / Integer / your immutable types need NO defensive copy
```
""",
    self_check=[
        "Can you explain in one sentence why a public field makes a rule unenforceable?",
        "Can you say four things a getter/setter pair buys over a public field?",
        "Would you write `deposit(amount)` or `setBalance(n)`, and can you say why?",
        "Can you state a class invariant for something you have written, and name where it is enforced?",
        "Can you explain why `private final int[]` still leaks, in both directions?",
        "Do you know which field types need no defensive copy, and why?",
        "Can you list the four steps of making a class immutable?",
    ],
    review=[
        _jq("A class validates in `setAge` but assigns directly in its constructor. What is the bug?",
            ["An object can be created invalid — the invariant is never established",
             "Nothing; the setter covers it",
             "The constructor will not compile",
             "`setAge` becomes unreachable"],
            0,
            "Both obligations are required. This is the single most common encapsulation "
            "mistake, and the capstone tests for it specifically."),
        _jq("```java\nprivate final int[] xs;\nint[] getXs() { return xs; }\n```\nWhat is wrong?",
            ["The caller gets a reference to the private array and can write into it",
             "Nothing — the field is private and final",
             "It does not compile",
             "The array is copied automatically on return"],
            0,
            "Neither `private` nor `final` protects the object a reference points at. Return "
            "`Arrays.copyOf(xs, xs.length)`."),
        _jq("Which field types need a defensive copy when stored or returned?",
            ["Mutable ones — arrays, and your own mutable classes",
             "All of them",
             "Only arrays",
             "None, if the field is final"],
            0,
            "`String`, boxed primitives and immutable classes of your own have nothing that "
            "can change, so copying them is pure waste."),
        _jq("Why is an immutable object automatically thread-safe?",
            ["Nothing can write to it, so there is no race to have",
             "Because the JVM locks it",
             "Because its fields are static",
             "It isn't — immutability is unrelated to threads"],
            0,
            "Data races need a writer. Remove every writer and the problem disappears — which "
            "is the same reason `String` can be shared through the pool."),
    ],
    milestone="Your classes now make promises they can actually keep: private state, "
              "deliberate doors, invariants that hold from the first instant, and no "
              "references leaking out the back.",
))
