# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 36 - Annotations and reflection.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# THE ANGLE: reflection is how every framework you will use - JUnit, Spring,
# Jackson, Hibernate, Mockito - does what it does. So the module builds small
# versions of those frameworks (a test runner, a validator, an options parser,
# a logging proxy) rather than listing the java.lang.reflect API.
#
#   36.1 the Class object            - a type as a value
#   36.2 fields, methods, invoking   - and InvocationTargetException
#   36.3 annotations                 - declaring them, retention, reading them
#   36.4 a framework in miniature    - test runner, validator, options parser
#   36.5 proxies, and the costs      - dynamic proxies; strong encapsulation
#
# DETERMINISM - THE ONE RULE THIS MODULE LIVES BY
#   `getDeclaredFields()` and `getDeclaredMethods()` return their results "in
#   no particular order" (their Javadoc says exactly that). HotSpot's order is
#   stable-looking but NOT declaration order, and may change between releases.
#   Every program here therefore SORTS members by name before printing them,
#   and lesson 36.2 teaches that as a rule, not a workaround. (getInterfaces()
#   and getRecordComponents() ARE specified to follow declaration order.)
#
#   Superclass chains of JDK collection classes (ArrayList -> AbstractList ->
#   AbstractCollection -> Object) have been stable for decades; JDK INTERFACE
#   lists are not (Java 21 added the Sequenced* interfaces), so no program
#   prints a JDK class's interfaces.
#
#   `setAccessible(true)` on a private field of java.lang.String throws
#   InaccessibleObjectException on JDK 16+ (strong encapsulation of java.base).
#   Lesson 36.5 relies on that; every other module compiles on JDK 17.
# ---------------------------------------------------------------------------

_M36 = []

_IMPORTS36 = ("import java.util.*;\n"
              "import java.util.function.*;\n"
              "import java.lang.annotation.*;\n"
              "import java.lang.reflect.*;\n")

# Almost every reflective call throws a checked exception.
_SIG36 = "    public static void main(String[] args) throws Exception {"


def _j36t(types, body, helpers=""):
    """Helper types above Main, optional static helpers, then a Scanner main that
    may throw."""
    return _jp(
        _IMPORTS36 + "\n"
        + (types.strip("\n") + "\n\n" if types.strip() else "")
        + "public class Main {\n"
        + (helpers.rstrip("\n") + "\n\n" if helpers.strip() else "")
        + _SIG36 + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }\n}"
    )


def _rows36(rows, out):
    stdin = "\n".join([str(len(rows))] + [" ".join(str(t) for t in r) for r in rows])
    return _case(stdin, out)


def _toks36(ts, out):
    return _case("\n".join([str(len(ts)), " ".join(ts)]), out)


def _after36(src, marker):
    return src[src.index(marker):].strip("\n")


# ===========================================================================
# 36.1 The Class object
# ===========================================================================

# Superclass chains, stable across every JDK this course supports.
_CHAINS36 = {
    "ArrayList": ["ArrayList", "AbstractList", "AbstractCollection", "Object"],
    "LinkedList": ["LinkedList", "AbstractSequentialList", "AbstractList",
                   "AbstractCollection", "Object"],
    "HashMap": ["HashMap", "AbstractMap", "Object"],
    "TreeMap": ["TreeMap", "AbstractMap", "Object"],
    "ArrayDeque": ["ArrayDeque", "AbstractCollection", "Object"],
    "PriorityQueue": ["PriorityQueue", "AbstractQueue", "AbstractCollection", "Object"],
    "HashSet": ["HashSet", "AbstractSet", "AbstractCollection", "Object"],
    "TreeSet": ["TreeSet", "AbstractSet", "AbstractCollection", "Object"],
}
_CHAINCASES36 = (["ArrayList"], ["HashMap", "TreeSet"], ["LinkedList"], ["PriorityQueue", "ArrayDeque"],
                 ["HashSet", "TreeMap", "ArrayList"])

_KINDS36 = {"List": "interface", "ArrayList": "class", "Map": "interface", "HashMap": "class",
            "Deque": "interface", "ArrayDeque": "class", "Iterator": "interface",
            "TreeSet": "class", "Collection": "interface"}
_KINDCASES36 = (["List", "ArrayList"], ["Map"], ["Deque", "ArrayDeque", "Iterator"], ["TreeSet"],
                ["Collection", "HashMap"])

_SHAPES36 = """
interface Shape {
}

interface Named {
}

class Circle implements Shape, Named {
}

class Label implements Named {
}

class Square implements Named, Shape {
}

class Blob {
}
"""
_IFACES36 = {"Circle": ["Shape", "Named"], "Label": ["Named"], "Square": ["Named", "Shape"],
             "Blob": []}
_OBJCASES36 = (["Circle", "Blob"], ["Square"], ["Label", "Circle", "Square"], ["Blob"],
               ["Square", "Label"])


def _obj_line36(name):
    ifs = _IFACES36[name]
    return f"{name} shape={_jbool('Shape' in ifs)} interfaces={_jarr(ifs)}"


_DESCTYPES36 = """
record Point(int x, int y) {
}

enum Suit {
    CLUBS, HEARTS
}
"""
_DESCRIBE36 = (
    "    static String describe(Class<?> c) {\n"
    "        String kind;\n"
    "        if (c.isPrimitive()) {\n"
    "            kind = \"primitive\";\n"
    "        } else if (c.isArray()) {\n"
    "            kind = \"array of \" + c.getComponentType().getSimpleName();\n"
    "        } else if (c.isInterface()) {\n"
    "            kind = \"interface\";\n"
    "        } else if (c.isEnum()) {\n"
    "            kind = \"enum\";\n"
    "        } else if (c.isRecord()) {\n"
    "            kind = \"record\";\n"
    "        } else {\n"
    "            kind = \"class extends \" + c.getSuperclass().getSimpleName();\n"
    "        }\n"
    "        return c.getSimpleName() + \": \" + kind;\n"
    "    }"
)
_DESCMAP36 = (
    "        Map<String, Class<?>> types = new HashMap<>();\n"
    "        types.put(\"int\", int.class);\n"
    "        types.put(\"String\", String.class);\n"
    "        types.put(\"String[]\", String[].class);\n"
    "        types.put(\"int[][]\", int[][].class);\n"
    "        types.put(\"List\", List.class);\n"
    "        types.put(\"ArrayList\", ArrayList.class);\n"
    "        types.put(\"Point\", Point.class);\n"
    "        types.put(\"Suit\", Suit.class);\n"
    "        types.put(\"Integer\", Integer.class);\n"
)
_DESCOUT36 = {"int": "int: primitive", "String": "String: class extends Object",
              "String[]": "String[]: array of String", "int[][]": "int[][]: array of int[]",
              "List": "List: interface", "ArrayList": "ArrayList: class extends AbstractList",
              "Point": "Point: record", "Suit": "Suit: enum",
              "Integer": "Integer: class extends Number"}
_DESCCASES36 = (["int", "String"], ["String[]", "int[][]"], ["List", "ArrayList", "Point"], ["Suit"],
                ["Integer", "int", "Point"])


_M36.append(_jlesson(
    "m36-class", "The `Class` object: a type as a value",
    "Every type is described at run time by an object you can ask questions of.",
    """
Everything so far has named types in source code: `new ArrayList<>()`,
`instanceof Circle`, `String.class` as an `EnumMap` key. At run time, the JVM
keeps an **object describing each loaded type** - an instance of `Class<T>` -
and the reflection API lets a program ask it questions.

## Three ways to get one

```java
Class<?> a = "hello".getClass();                    // from an object
Class<String> b = String.class;                     // from a type name in source
Class<?> c = Class.forName("java.util.ArrayList");  // from a String, at run time
```

The third is what makes frameworks possible: a class name read from a config
file or an annotation becomes a class the program can use, without the program
ever having mentioned it. It needs the **fully qualified** name, and throws the
checked `ClassNotFoundException` if nothing by that name can be loaded.

## Asking questions

```java
c.getSimpleName()      // "ArrayList"
c.getName()            // "java.util.ArrayList"
c.getSuperclass()      // AbstractList.class - null for Object and interfaces
c.getInterfaces()      // the interfaces it DIRECTLY implements, in declared order
c.isInterface()  c.isArray()  c.isPrimitive()  c.isEnum()  c.isRecord()
c.getComponentType()   // String.class, for String[].class
Shape.class.isInstance(obj)   // instanceof, with the type as a value
```

Even primitives and arrays have `Class` objects: `int.class`, `int[][].class`.

Walking `getSuperclass()` until it returns `null` gives the whole inheritance
chain - `ArrayList → AbstractList → AbstractCollection → Object` - which is
module 13's hierarchy made visible.

## Why this matters

Almost nothing in ordinary code needs reflection, and it should be the last
tool you reach for. But it is how JUnit finds your tests, how Spring wires your
objects together, how Jackson turns JSON into objects and back - and knowing
how they work is what makes their error messages make sense. This module builds
small versions of each.
""",
    warmup=[
        _jq("`Class.forName(\"ArrayList\")` throws `ClassNotFoundException` because…",
            ["it needs the fully qualified name, java.util.ArrayList",
             "ArrayList is generic", "it is not public", "forName is deprecated"],
            0,
            "Only the fully qualified name identifies a class."),
        _jq("`Object.class.getSuperclass()` returns…",
            ["null", "Object.class", "Class.class", "throws"],
            0,
            "Object is the root; the chain ends there."),
    ],
    exercises=[
        _je("j36-cl-chain", "Up the hierarchy",
            "For each `java.util` class name, print its superclass chain up to `Object`, "
            "joined by ` -> `. Replace `____` with the step that moves one class up.",
            _j36t("",
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            Class<?> c = Class.forName(\"java.util.\" + sc.next());\n"
                  "            List<String> chain = new ArrayList<>();\n"
                  "            while (c != null) {\n"
                  "                chain.add(c.getSimpleName());\n"
                  "                c = c.getSuperclass();\n"
                  "            }\n"
                  "            System.out.println(String.join(\" -> \", chain));\n"
                  "        }"),
            "                c = c.getSuperclass();",
            [_toks36(ts, _nl(*[" -> ".join(_CHAINS36[t]) for t in ts])) for ts in _CHAINCASES36],
            hints=["`getSuperclass()` returns the parent class's `Class` object.",
                   "It returns `null` above `Object`, which ends the loop.",
                   "`c = c.getSuperclass();`",
                   "`Class.forName` needs the package, hence `\"java.util.\" + name`."],
            difficulty="Easy"),

        _jfix("j36-cl-forname", "The class that could not be found",
              "This looks classes up by their simple names and throws "
              "`ClassNotFoundException` on the first one. Every name here lives in "
              "`java.util`; make the lookup use the fully qualified name.",
              _j36t("",
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String name = sc.next();\n"
                    "            Class<?> c = Class.forName(name);\n"
                    "            System.out.println(name + \" \" + (c.isInterface() ? \"interface\" : \"class\"));\n"
                    "        }"),
              _j36t("",
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String name = sc.next();\n"
                    "            Class<?> c = Class.forName(\"java.util.\" + name);\n"
                    "            System.out.println(name + \" \" + (c.isInterface() ? \"interface\" : \"class\"));\n"
                    "        }"),
              [_toks36(ts, _nl(*[f"{t} {_KINDS36[t]}" for t in ts])) for ts in _KINDCASES36],
              hints=["`Class.forName` does not search packages - there could be a `List` in "
                     "any of them.",
                     "Imports are a compile-time convenience; they mean nothing at run time.",
                     "`Class.forName(\"java.util.\" + name)`",
                     "`getName()` on a class gives back exactly this fully qualified form."],
              difficulty="Easy"),

        _je("j36-cl-instance", "`instanceof`, with the type as a value",
            "For each object print its class, whether it is a `Shape`, and the interfaces "
            "it directly implements - which `getInterfaces()` returns in the order the "
            "class declared them. Replace `____` with the `Shape` test.",
            _j36t(_SHAPES36,
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            Object obj = switch (sc.next()) {\n"
                  "                case \"Circle\" -> new Circle();\n"
                  "                case \"Label\" -> new Label();\n"
                  "                case \"Square\" -> new Square();\n"
                  "                default -> new Blob();\n"
                  "            };\n"
                  "            List<String> names = new ArrayList<>();\n"
                  "            for (Class<?> ifc : obj.getClass().getInterfaces()) {\n"
                  "                names.add(ifc.getSimpleName());\n"
                  "            }\n"
                  "            System.out.println(obj.getClass().getSimpleName() + \" shape=\"\n"
                  "                    + Shape.class.isInstance(obj) + \" interfaces=\" + names);\n"
                  "        }"),
            "Shape.class.isInstance(obj)",
            [_toks36(ts, _nl(*[_obj_line36(t) for t in ts])) for ts in _OBJCASES36],
            hints=["`X.class.isInstance(obj)` is `obj instanceof X` with X as a value.",
                   "`Shape.class.isInstance(obj)`",
                   "That form is what a framework uses when the type arrives as data.",
                   "Square declares `Named, Shape`, so that is the order it reports."],
            difficulty="Easy"),

        _jch("j36-cl-describe", "Describing any type", "Medium",
             "Write `describe(Class<?> c)`: `name: primitive`, `name: array of X` (the "
             "component's simple name), `name: interface`, `name: enum`, `name: record`, or "
             "`name: class extends Y` - checked in that order.",
             _j36t(_DESCTYPES36,
                   _DESCMAP36
                   + "        int n = sc.nextInt();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            System.out.println(describe(types.get(sc.next())));\n"
                     "        }",
                   helpers=_DESCRIBE36),
             _DESCRIBE36,
             [_toks36(ts, _nl(*[_DESCOUT36[t] for t in ts])) for ts in _DESCCASES36],
             hints=["Test `isPrimitive()` and `isArray()` first - neither has a superclass "
                    "worth reporting.",
                    "`getComponentType()` of `int[][]` is `int[]`: one level at a time.",
                    "Enums and records extend `Enum` and `Record`, so check `isEnum()` and "
                    "`isRecord()` before falling back to the superclass.",
                    "`Integer` extends `Number`; `String` extends `Object`."]),
    ],
    quiz=[
        _jq("Which returns the interfaces in the order the class declared them?",
            ["getInterfaces()", "getDeclaredMethods()", "getDeclaredFields()", "none of them"],
            0,
            "Its Javadoc specifies declaration order; the member lists do not."),
        _jq("`int[].class.getComponentType()` is…",
            ["int.class", "Integer.class", "null", "Object.class"],
            0,
            "Primitives have Class objects too."),
    ],
))


# ===========================================================================
# 36.2 Fields and methods
# ===========================================================================

_MEMBERS36 = """
class Book {
    private static int created;
    private String title;
    private int pages;
    public boolean available = true;

    Book(String title, int pages) {
        this.title = title;
        this.pages = pages;
        created++;
    }
}

class Point {
    private final int y;
    private final int x;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
}

class Person {
    static final String SPECIES = "human";
    private String name;
    private int age;
    private List<String> tags = new ArrayList<>();
    private double height;
}
"""
_FIELDS36 = {"book": [("available", "boolean"), ("pages", "int"), ("title", "String")],
             "point": [("x", "int"), ("y", "int")],
             "person": [("age", "int"), ("height", "double"), ("name", "String"), ("tags", "List")]}
_FIELDCASES36 = (["book"], ["point", "person"], ["person"], ["book", "point"], ["point"])

_CALC36 = """
class Calc {
    public int add(int a, int b) {
        return a + b;
    }

    public int sub(int a, int b) {
        return a - b;
    }

    public int mul(int a, int b) {
        return a * b;
    }

    public int max(int a, int b) {
        return Math.max(a, b);
    }
}
"""
_CALCROWS36 = ([("add", 2, 3), ("mul", 4, 5)], [("pow", 2, 8)], [("sub", 1, 9), ("max", -3, -7)],
               [("max", 5, 5)], [("mul", -2, 6), ("div", 1, 1), ("add", 0, 0)])
_CALCF36 = {"add": lambda a, b: a + b, "sub": lambda a, b: a - b, "mul": lambda a, b: a * b,
            "max": max}


def _calc_out36(rows):
    return _nl(*[f"{o}({a}, {b}) = {_CALCF36[o](a, b)}" if o in _CALCF36 else f"no such method: {o}"
                 for (o, a, b) in rows])


_SAFEDIV36 = """
class SafeMath {
    public int div(int a, int b) {
        if (b == 0) {
            throw new IllegalArgumentException("division by zero");
        }
        return a / b;
    }

    public int root(int a, int b) {
        if (a < 0) {
            throw new IllegalArgumentException("negative input");
        }
        return (int) Math.sqrt(a) + b;
    }
}
"""
_DIVROWS36 = ([("div", 7, 2), ("div", 1, 0)], [("root", -4, 0)], [("root", 16, 1), ("div", -9, 3)],
              [("div", 0, 0)], [("root", 10, 0), ("div", 100, 7), ("root", -1, 5)])


def _div_out36(rows):
    out = []
    for (op, a, b) in rows:
        if op == "div":
            out.append("error: division by zero" if b == 0 else f"div = {_jdiv(a, b)}")
        else:
            out.append("error: negative input" if a < 0 else f"root = {int(a ** 0.5) + b}")
    return _nl(*out)


_DUMPTYPES36 = """
class Book {
    private static int created;
    private String title;
    private int pages;
    private boolean available = true;

    Book(String title, int pages) {
        this.title = title;
        this.pages = pages;
        created++;
    }
}

class Pixel {
    private final int y;
    private final int x;
    private final String colour;

    Pixel(int x, int y, String colour) {
        this.x = x;
        this.y = y;
        this.colour = colour;
    }
}
"""
_DUMP36 = (
    "    static String describe(Object o) throws IllegalAccessException {\n"
    "        Field[] fields = o.getClass().getDeclaredFields();\n"
    "        Arrays.sort(fields, Comparator.comparing(Field::getName));\n"
    "        List<String> parts = new ArrayList<>();\n"
    "        for (Field f : fields) {\n"
    "            if (Modifier.isStatic(f.getModifiers())) {\n"
    "                continue;\n"
    "            }\n"
    "            f.setAccessible(true);\n"
    "            parts.add(f.getName() + \"=\" + f.get(o));\n"
    "        }\n"
    "        return o.getClass().getSimpleName() + \"{\" + String.join(\", \", parts) + \"}\";\n"
    "    }"
)
_DUMPROWS36 = ([("book", "Dune", 412)], [("pixel", 3, 4, "red")], [("book", "Emma", 1), ("pixel", 0, 0, "black")],
               [("pixel", -1, 7, "blue")], [("book", "X", 99), ("book", "Y", 100)])


def _dump36(r):
    if r[0] == "book":
        return f"Book{{available=true, pages={r[2]}, title={r[1]}}}"
    return f"Pixel{{colour={r[3]}, x={r[1]}, y={r[2]}}}"


_M36.append(_jlesson(
    "m36-members", "Fields and methods, found and used by name",
    "Read any field, call any method - and sort them, because the order is not yours.",
    """
A `Class` object also describes its members:

```java
Field[] fs  = c.getDeclaredFields();      // every field declared HERE, any access
Method[] ms = c.getDeclaredMethods();     // every method declared here
Method m    = c.getMethod("add", int.class, int.class);   // a public one, by signature
```

`getDeclared...` sees everything the class itself declares, private included,
but nothing inherited. `getMethod`/`getMethods` see only **public** members, but
include inherited ones - `getMethods()` on any class starts with the nine public
methods of `Object`. A method is identified by its name *and parameter types*,
because of overloading.

## The order is not specified

The Javadoc of `getDeclaredFields` says the elements are **"not sorted and are
not in any particular order"**. On today's JVM they often *look* like
declaration order, which is exactly what makes code that depends on it
dangerous. Anything that prints, compares or serialises members must **sort
them** - by name is the usual choice:

```java
Arrays.sort(fs, Comparator.comparing(Field::getName));
```

## Using them

```java
f.setAccessible(true);            // needed for a private member, from outside
Object v = f.get(obj);            // read the field of THAT object
f.set(obj, 42);                   // write it
Modifier.isStatic(f.getModifiers())

Object r = m.invoke(obj, 2, 3);   // call it; ints are boxed, the result is Object
```

## `InvocationTargetException`

When a method called through `invoke` throws, the exception does **not** come
out as itself - it arrives wrapped in `InvocationTargetException`, with the real
exception as its **cause**. It is module 31's `ExecutionException` again, and
for the same reason: the call happened somewhere else, and the wrapper tells you
so. Catching the original type around `invoke` therefore never catches
anything:

```java
try {
    m.invoke(obj, a, b);
} catch (InvocationTargetException e) {
    Throwable real = e.getCause();          // the IllegalArgumentException
}
```

`NoSuchMethodException`, `IllegalAccessException` and the rest are **checked**,
so reflective code is thick with `throws Exception` - one of the costs lesson
36.5 weighs up.
""",
    warmup=[
        _jq("A method called by `invoke` throws `IllegalArgumentException`. The caller "
            "receives…",
            ["InvocationTargetException, with the IAE as its cause",
             "the IllegalArgumentException", "null", "nothing - it is swallowed"],
            0,
            "Unwrap with getCause()."),
        _jq("`getDeclaredFields()` returns fields in…",
            ["no specified order - sort them yourself", "declaration order",
             "alphabetical order", "access order"],
            0,
            "The Javadoc says so explicitly."),
    ],
    exercises=[
        _je("j36-me-fields", "Listing fields, in an order you chose",
            "For each class, print its instance fields (skip static ones) as `name type`, "
            "sorted by name. Replace `____` with the sort.",
            _j36t(_MEMBERS36,
                  "        Map<String, Class<?>> types = Map.of(\"book\", Book.class, \"point\", Point.class,\n"
                  "                \"person\", Person.class);\n"
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            Class<?> c = types.get(sc.next());\n"
                  "            System.out.println(c.getSimpleName() + \":\");\n"
                  "            Field[] fields = c.getDeclaredFields();\n"
                  "            Arrays.sort(fields, Comparator.comparing(Field::getName));\n"
                  "            for (Field f : fields) {\n"
                  "                if (!Modifier.isStatic(f.getModifiers())) {\n"
                  "                    System.out.println(\"  \" + f.getName() + \" \" + f.getType().getSimpleName());\n"
                  "                }\n"
                  "            }\n"
                  "        }"),
            "            Arrays.sort(fields, Comparator.comparing(Field::getName));",
            [_toks36(ts, _nl(*[x for t in ts for x in
                               ([{"book": "Book", "point": "Point", "person": "Person"}[t] + ":"]
                                + [f"  {nm} {ty}" for (nm, ty) in _FIELDS36[t]])]))
             for ts in _FIELDCASES36],
            hints=["Without a sort, the order is whatever this JVM happens to produce.",
                   "`Arrays.sort(fields, Comparator.comparing(Field::getName));`",
                   "`Point` declares `y` before `x` - sorted output puts `x` first anyway.",
                   "`f.getType()` is the declared type: `List`, not `ArrayList`."],
            difficulty="Easy"),

        _je("j36-me-invoke", "Calling a method by name",
            "Each line is `op a b`. Find the public method named `op` taking two ints and "
            "call it - or print `no such method: op`. Replace `____` with the lookup.",
            _j36t(_CALC36,
                  "        Calc calc = new Calc();\n"
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            String op = sc.next();\n"
                  "            int a = sc.nextInt();\n"
                  "            int b = sc.nextInt();\n"
                  "            try {\n"
                  "                Method m = Calc.class.getMethod(op, int.class, int.class);\n"
                  "                System.out.println(op + \"(\" + a + \", \" + b + \") = \" + m.invoke(calc, a, b));\n"
                  "            } catch (NoSuchMethodException e) {\n"
                  "                System.out.println(\"no such method: \" + op);\n"
                  "            }\n"
                  "        }"),
            "Calc.class.getMethod(op, int.class, int.class)",
            [_rows36(rows, _calc_out36(rows)) for rows in _CALCROWS36],
            hints=["A method is found by name AND parameter types.",
                   "`int.class` is the Class object for the primitive `int`.",
                   "`Calc.class.getMethod(op, int.class, int.class)`",
                   "`invoke` boxes the ints and returns the result as an `Object`."],
            difficulty="Medium"),

        _jfix("j36-me-target", "The exception that came out wrapped",
              "`SafeMath` throws `IllegalArgumentException` for bad input, and this code "
              "catches exactly that around `invoke` - so it never catches anything, and the "
              "program dies with `InvocationTargetException`. Catch the wrapper and report "
              "its cause's message.",
              _j36t(_SAFEDIV36,
                    "        SafeMath math = new SafeMath();\n"
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String op = sc.next();\n"
                    "            int a = sc.nextInt();\n"
                    "            int b = sc.nextInt();\n"
                    "            Method m = SafeMath.class.getMethod(op, int.class, int.class);\n"
                    "            try {\n"
                    "                System.out.println(op + \" = \" + m.invoke(math, a, b));\n"
                    "            } catch (IllegalArgumentException e) {\n"
                    "                System.out.println(\"error: \" + e.getMessage());\n"
                    "            }\n"
                    "        }"),
              _j36t(_SAFEDIV36,
                    "        SafeMath math = new SafeMath();\n"
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String op = sc.next();\n"
                    "            int a = sc.nextInt();\n"
                    "            int b = sc.nextInt();\n"
                    "            Method m = SafeMath.class.getMethod(op, int.class, int.class);\n"
                    "            try {\n"
                    "                System.out.println(op + \" = \" + m.invoke(math, a, b));\n"
                    "            } catch (InvocationTargetException e) {\n"
                    "                System.out.println(\"error: \" + e.getCause().getMessage());\n"
                    "            }\n"
                    "        }"),
              [_rows36(rows, _div_out36(rows)) for rows in _DIVROWS36],
              hints=["An exception thrown by the invoked method is wrapped before it reaches "
                     "you.",
                     "Catch `InvocationTargetException`.",
                     "The original is `e.getCause()` - and its message is the one `SafeMath` "
                     "wrote.",
                     "(`invoke` CAN throw a plain IllegalArgumentException - but only when "
                     "the arguments do not fit the method's parameters.)"],
              difficulty="Medium"),

        _jch("j36-me-tostring", "A `toString` for any object", "Hard",
             "Write `describe(o)`: `ClassName{field=value, ...}` over the object's "
             "non-static declared fields, sorted by name - private ones included.",
             _j36t(_DUMPTYPES36,
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            Object o = sc.next().equals(\"book\")\n"
                   "                    ? new Book(sc.next(), sc.nextInt())\n"
                   "                    : new Pixel(sc.nextInt(), sc.nextInt(), sc.next());\n"
                   "            System.out.println(describe(o));\n"
                   "        }",
                   helpers=_DUMP36),
             _DUMP36,
             [_rows36(rows, _nl(*[_dump36(r) for r in rows])) for rows in _DUMPROWS36],
             hints=["`o.getClass().getDeclaredFields()`, then sort by name.",
                    "Skip statics: `Modifier.isStatic(f.getModifiers())`.",
                    "`f.setAccessible(true)` before `f.get(o)` - the fields are private to "
                    "another class.",
                    "`f.get(o)` returns an Object; string concatenation prints it.",
                    "This is, in miniature, what every JSON library and every IDE debugger "
                    "does."]),
    ],
    quiz=[
        _jq("`getMethods()` differs from `getDeclaredMethods()` in that it…",
            ["returns only public methods, including inherited ones",
             "returns private methods too", "is sorted", "excludes Object's methods"],
            0,
            "getDeclared* is everything declared here, of any access, not inherited."),
        _jq("Why must `getMethod(\"add\", int.class, int.class)` name the parameter types?",
            ["methods can be overloaded, so a name alone is ambiguous",
             "for speed", "because ints must be boxed", "it need not"],
            0,
            "The signature is the identity."),
    ],
))


# ===========================================================================
# 36.3 Annotations
# ===========================================================================

_SHELL36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Command {
    String value();
}

class Shell {
    @Command("ls")
    public void list() {
    }

    @Command("cd")
    public void changeDir() {
    }

    public void helper() {
    }

    @Command("pwd")
    public void printDir() {
    }
}
"""
_SHELLBODY36 = (
    "        String prefix = sc.next();\n"
    "        List<String> names = new ArrayList<>();\n"
    "        for (Method m : Shell.class.getDeclaredMethods()) {\n"
    "            Command c = m.getAnnotation(Command.class);\n"
    "            if (c != null && c.value().startsWith(prefix.equals(\"*\") ? \"\" : prefix)) {\n"
    "                names.add(c.value() + \" -> \" + m.getName());\n"
    "            }\n"
    "        }\n"
    "        Collections.sort(names);\n"
    "        System.out.println(names.size() + \" commands\");\n"
    "        for (String s : names) {\n"
    "            System.out.println(s);\n"
    "        }"
)
_CMDS36 = {"ls": "list", "cd": "changeDir", "pwd": "printDir"}
_PREFIXES36 = ("*", "c", "p", "x", "l")


def _shell_out36(prefix):
    p = "" if prefix == "*" else prefix
    rows = sorted(f"{k} -> {v}" for (k, v) in _CMDS36.items() if k.startswith(p))
    return _nl(f"{len(rows)} commands", *rows)


_TASKS36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Priority {
    int value() default 3;
}

class Tasks {
    @Priority(1)
    public void deploy() {
    }

    @Priority
    public void review() {
    }

    @Priority(5)
    public void tidy() {
    }

    @Priority
    public void backup() {
    }

    public void notATask() {
    }
}
"""
_TASKPRI36 = {"deploy": 1, "review": 3, "tidy": 5, "backup": 3}
_THRESHOLDS36 = (3, 1, 5, 0, 2)


def _tasks_out36(limit):
    rows = sorted((p, n) for (n, p) in _TASKPRI36.items() if p <= limit)
    return _nl(*[f"{p} {n}" for (p, n) in rows]) if rows else "(none)"


_API36 = """
class Api {
    @Deprecated(since = "2.0")
    public void oldLogin() {
    }

    public void login() {
    }

    @Deprecated(since = "1.5")
    public void legacyExport() {
    }

    public void export() {
    }

    @Deprecated(since = "3.1")
    public void fetchAll() {
    }
}
"""
_DEPRECATED36 = {"oldLogin": "2.0", "legacyExport": "1.5", "fetchAll": "3.1"}
_APIVERS36 = ("2.0", "9.9", "1.0", "3.1", "1.5")


def _api_out36(v):
    rows = sorted((n, s) for (n, s) in _DEPRECATED36.items() if s <= v)
    lines = [f"{n} (since {s})" for (n, s) in rows]
    return _nl(f"deprecated as of {v}: {len(rows)}", *lines)


_FORM36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Label {
    String value();
}

class Signup {
    @Label("Full name")
    private String name;

    @Label("E-mail address")
    private String email;

    private String city;

    @Label("Age in years")
    private int age;

    Signup(String name, String email, String city, int age) {
        this.name = name;
        this.email = email;
        this.city = city;
        this.age = age;
    }
}
"""
_FORMHELP36 = (
    "    static List<String> form(Object o) throws IllegalAccessException {\n"
    "        Field[] fields = o.getClass().getDeclaredFields();\n"
    "        Arrays.sort(fields, Comparator.comparing(Field::getName));\n"
    "        List<String> lines = new ArrayList<>();\n"
    "        for (Field f : fields) {\n"
    "            Label label = f.getAnnotation(Label.class);\n"
    "            String caption = label == null ? f.getName() : label.value();\n"
    "            f.setAccessible(true);\n"
    "            lines.add(caption + \": \" + f.get(o));\n"
    "        }\n"
    "        return lines;\n"
    "    }"
)
_SIGNUPS36 = (("ada", "ada@x.io", "london", 36), ("bo", "bo@y.org", "oslo", 7),
              ("cy", "c@z", "rome", 101), ("di", "d@d", "lima", 0), ("ed", "e@e", "kyiv", 44))


def _form_out36(name, email, city, age):
    return _nl(f"Age in years: {age}", f"city: {city}", f"E-mail address: {email}",
               f"Full name: {name}")


_M36.append(_jlesson(
    "m36-annotations", "Annotations: declaring them, and reading them back",
    "Metadata in the source - and the retention policy that decides whether anything "
    "can see it.",
    """
An **annotation** is structured metadata attached to a declaration. It does
nothing by itself; something has to *read* it - the compiler, a build tool, or,
at run time, reflection. You have used four since module 13: `@Override`,
`@FunctionalInterface` (25), `@SuppressWarnings` and `@SafeVarargs` (24), plus
`@Deprecated`.

## Declaring one

```java
@Retention(RetentionPolicy.RUNTIME)       // keep it in the class file AND at run time
@Target(ElementType.METHOD)               // only allowed on methods
@interface Command {
    String value();                       // an element - looks like a method
}

@Command("ls") public void list() { }     // `value` may be written without its name
```

**Elements** can be primitives, `String`, `Class`, enums, other annotations, or
arrays of those - and can have **defaults**:

```java
@interface Priority { int value() default 3; }
@Priority      void review() { }          // 3
@Priority(1)   void deploy() { }          // 1
```

An annotation with no elements at all (`@Test`) is a *marker*.

## Retention: the setting everybody forgets

| policy | kept in | visible to reflection |
|---|---|---|
| `SOURCE` | the source only | no - `@Override` is this |
| `CLASS` | the class file | **no** |
| `RUNTIME` | the class file, loaded | yes |

The **default is `CLASS`** - so an annotation declared without
`@Retention(RetentionPolicy.RUNTIME)` compiles, sits in the class file, and is
**invisible at run time**. `getAnnotation` returns `null`, `isAnnotationPresent`
returns `false`, and a framework looking for it silently finds nothing. It is
the first thing to check when "the framework ignores my annotation".

## Reading them

```java
m.isAnnotationPresent(Command.class)      // true or false
Command c = m.getAnnotation(Command.class);   // the annotation, or null
c.value()                                 // its element, called like a method
```

The same methods exist on `Class`, `Field`, `Constructor` and `Parameter`.
""",
    warmup=[
        _jq("An annotation declared with no `@Retention` is read with `getAnnotation`. "
            "The result is…",
            ["null - the default retention is CLASS", "the annotation",
             "an exception", "a compile error"],
            0,
            "Only RUNTIME retention survives into the running program."),
        _jq("`@Command(\"ls\")` can omit the element name because…",
            ["the element is called value", "it has one element", "it is a marker",
             "strings are special"],
            0,
            "Only an element named `value` may be written positionally."),
    ],
    exercises=[
        _jfix("j36-an-retention", "The annotation nobody could see",
              "`Shell`'s methods are marked with `@Command`, but this lists zero commands - "
              "`getAnnotation` always returns `null`. The annotation is missing the one line "
              "that keeps it at run time. Add it.",
              _j36t(_SHELL36.replace("@Retention(RetentionPolicy.RUNTIME)\n", ""), _SHELLBODY36),
              _j36t(_SHELL36, _SHELLBODY36),
              [_case(p, _shell_out36(p)) for p in _PREFIXES36],
              hints=["Without `@Retention`, an annotation's retention is CLASS.",
                     "CLASS-retained annotations are in the class file but not visible to "
                     "reflection.",
                     "`@Retention(RetentionPolicy.RUNTIME)` above `@interface Command`.",
                     "The commands are sorted by name, because `getDeclaredMethods` promises "
                     "no order."],
              difficulty="Easy"),

        _je("j36-an-default", "An element with a default",
            "`@Priority` has one element whose default is 3, so a bare `@Priority` means 3. "
            "Print every task at or below the given priority, lowest first (ties by name). "
            "Replace `____` with the element declaration.",
            _j36t(_TASKS36,
                  "        int limit = sc.nextInt();\n"
                  "        List<String> rows = new ArrayList<>();\n"
                  "        for (Method m : Tasks.class.getDeclaredMethods()) {\n"
                  "            Priority p = m.getAnnotation(Priority.class);\n"
                  "            if (p != null && p.value() <= limit) {\n"
                  "                rows.add(p.value() + \" \" + m.getName());\n"
                  "            }\n"
                  "        }\n"
                  "        Collections.sort(rows);\n"
                  "        System.out.println(rows.isEmpty() ? \"(none)\" : String.join(\"\\n\", rows));"),
            "    int value() default 3;",
            [_case(str(t), _tasks_out36(t)) for t in _THRESHOLDS36],
            hints=["An element is declared like an interface method.",
                   "`default 3` supplies the value when the annotation omits it.",
                   "`int value() default 3;`",
                   "Sorting the `\"p name\"` strings orders by priority, then name - the "
                   "priorities are single digits."],
            difficulty="Easy"),

        _je("j36-an-builtin", "Reading `@Deprecated`",
            "`@Deprecated` is a JDK annotation with RUNTIME retention and a `since` element. "
            "List the methods deprecated at or before the given version, sorted by name. "
            "Replace `____` with the test for the annotation.",
            _j36t(_API36,
                  "        String version = sc.next();\n"
                  "        List<String> rows = new ArrayList<>();\n"
                  "        for (Method m : Api.class.getDeclaredMethods()) {\n"
                  "            if (m.isAnnotationPresent(Deprecated.class)) {\n"
                  "                String since = m.getAnnotation(Deprecated.class).since();\n"
                  "                if (since.compareTo(version) <= 0) {\n"
                  "                    rows.add(m.getName() + \" (since \" + since + \")\");\n"
                  "                }\n"
                  "            }\n"
                  "        }\n"
                  "        Collections.sort(rows);\n"
                  "        System.out.println(\"deprecated as of \" + version + \": \" + rows.size());\n"
                  "        for (String r : rows) {\n"
                  "            System.out.println(r);\n"
                  "        }"),
            "m.isAnnotationPresent(Deprecated.class)",
            [_case(v, _api_out36(v)) for v in _APIVERS36],
            hints=["`isAnnotationPresent(X.class)` asks without fetching.",
                   "`m.isAnnotationPresent(Deprecated.class)`",
                   "Then `getAnnotation(Deprecated.class).since()` reads the element.",
                   "The versions are compared as Strings - fine for these single-digit "
                   "versions, and a bug for `10.0` versus `9.0`."],
            difficulty="Easy"),

        _jch("j36-an-label", "Form labels from annotations", "Medium",
             "Write `form(o)`: one line per declared field, sorted by field NAME, reading "
             "`caption: value`, where the caption is the field's `@Label` if it has one and "
             "the field name otherwise.",
             _j36t(_FORM36,
                   "        Signup s = new Signup(sc.next(), sc.next(), sc.next(), sc.nextInt());\n"
                   "        for (String line : form(s)) {\n"
                   "            System.out.println(line);\n"
                   "        }",
                   helpers=_FORMHELP36),
             _FORMHELP36,
             [_case(" ".join(str(x) for x in s), _form_out36(*s)) for s in _SIGNUPS36],
             hints=["`f.getAnnotation(Label.class)` is `null` for an unlabelled field.",
                    "Sort by field name - `age`, `city`, `email`, `name` - even though the "
                    "captions then print in a different alphabetical order.",
                    "`setAccessible(true)` before reading the private value.",
                    "`@Target(ElementType.FIELD)` on `Label` means it cannot be put on a "
                    "method by mistake."]),
    ],
    quiz=[
        _jq("The default retention policy for an annotation is…",
            ["CLASS", "RUNTIME", "SOURCE", "none"],
            0,
            "Which is why framework annotations always declare RUNTIME."),
        _jq("`@Override` has retention…",
            ["SOURCE - only the compiler needs it", "RUNTIME", "CLASS", "none"],
            0,
            "It is a compile-time check and nothing more."),
    ],
))


# ===========================================================================
# 36.4 A framework in miniature
# ===========================================================================

_TESTS36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Test {
}

class ListTests {
    static int[] data;

    static void check(boolean ok, String message) {
        if (!ok) {
            throw new AssertionError(message);
        }
    }

    @Test
    void allPositive() {
        for (int x : data) {
            check(x > 0, "found " + x);
        }
    }

    @Test
    void sorted() {
        for (int i = 1; i < data.length; i++) {
            check(data[i - 1] <= data[i], "out of order at index " + i);
        }
    }

    @Test
    void notEmpty() {
        check(data.length > 0, "no data");
    }

    @Test
    void sumBelowHundred() {
        int sum = 0;
        for (int x : data) {
            sum += x;
        }
        check(sum < 100, "sum is " + sum);
    }

    void helper() {
    }
}
"""
_RUNBODY36 = (
    "        int n = sc.nextInt();\n"
    "        ListTests.data = new int[n];\n"
    "        for (int i = 0; i < n; i++) {\n"
    "            ListTests.data[i] = sc.nextInt();\n"
    "        }\n"
    "        Method[] methods = ListTests.class.getDeclaredMethods();\n"
    "        Arrays.sort(methods, Comparator.comparing(Method::getName));\n"
    "        int passed = 0;\n"
    "        int failed = 0;\n"
    "        for (Method m : methods) {\n"
    "            if (!m.isAnnotationPresent(Test.class)) {\n"
    "                continue;\n"
    "            }\n"
    "            Object instance = ListTests.class.getDeclaredConstructor().newInstance();\n"
    "            try {\n"
    "                m.invoke(instance);\n"
    "                System.out.println(\"PASS \" + m.getName());\n"
    "                passed++;\n"
    "            } catch (InvocationTargetException e) {\n"
    "                System.out.println(\"FAIL \" + m.getName() + \": \" + e.getCause().getMessage());\n"
    "                failed++;\n"
    "            }\n"
    "        }\n"
    "        System.out.println(passed + \" passed, \" + failed + \" failed\");"
)
_DATA36 = ([1, 2, 3], [5, -1, 7], [], [40, 50, 60], [9, 3])


def _run_out36(xs):
    res = []
    bad = next((x for x in xs if x <= 0), None)
    res.append(("allPositive", None if bad is None else f"found {bad}"))
    res.append(("notEmpty", None if xs else "no data"))
    oo = next((i for i in range(1, len(xs)) if xs[i - 1] > xs[i]), None)
    res.append(("sorted", None if oo is None else f"out of order at index {oo}"))
    s = sum(xs)
    res.append(("sumBelowHundred", None if s < 100 else f"sum is {s}"))
    lines, p, f = [], 0, 0
    for (name, err) in res:
        if err is None:
            lines.append(f"PASS {name}")
            p += 1
        else:
            lines.append(f"FAIL {name}: {err}")
            f += 1
    lines.append(f"{p} passed, {f} failed")
    return _nl(*lines)


def _data_case36(xs):
    return _case(f"{len(xs)}\n{_sp(xs)}" if xs else "0\n", _run_out36(xs))


_VALID36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface NotBlank {
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Range {
    int min();

    int max();
}

class Account {
    @NotBlank
    private final String user;

    @Range(min = 18, max = 120)
    private final int age;

    @NotBlank
    private final String country;

    @Range(min = 0, max = 10)
    private final int rating;

    Account(String user, int age, String country, int rating) {
        this.user = user;
        this.age = age;
        this.country = country;
        this.rating = rating;
    }
}
"""
_VALIDHELP36 = (
    "    static List<String> validate(Object o) throws IllegalAccessException {\n"
    "        Field[] fields = o.getClass().getDeclaredFields();\n"
    "        Arrays.sort(fields, Comparator.comparing(Field::getName));\n"
    "        List<String> problems = new ArrayList<>();\n"
    "        for (Field f : fields) {\n"
    "            f.setAccessible(true);\n"
    "            Object value = f.get(o);\n"
    "            if (f.isAnnotationPresent(NotBlank.class)\n"
    "                    && (value == null || value.toString().isBlank())) {\n"
    "                problems.add(f.getName() + \": must not be blank\");\n"
    "            }\n"
    "            Range r = f.getAnnotation(Range.class);\n"
    "            if (r != null) {\n"
    "                int v = (Integer) value;\n"
    "                if (v < r.min() || v > r.max()) {\n"
    "                    problems.add(f.getName() + \": must be between \" + r.min() + \" and \" + r.max());\n"
    "                }\n"
    "            }\n"
    "        }\n"
    "        return problems;\n"
    "    }"
)
_ACCTS36 = ([("ada", 36, "uk", 7)], [("-", 12, "fr", 11)], [("bo", 18, "-", 0), ("cy", 121, "no", 10)],
            [("-", 200, "-", -1)], [("di", 120, "pe", 5), ("ed", 17, "it", 3)])


def _valid_out36(u, age, c, rating):
    probs = []
    if not (18 <= age <= 120):
        probs.append("age: must be between 18 and 120")
    if c == "-":
        probs.append("country: must not be blank")
    if not (0 <= rating <= 10):
        probs.append("rating: must be between 0 and 10")
    if u == "-":
        probs.append("user: must not be blank")
    return "ok" if not probs else "; ".join(probs)


_OPTS36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Option {
    String value();
}

class Settings {
    @Option("--name")
    String name = "world";

    @Option("--times")
    int times = 1;

    @Option("--loud")
    boolean loud;
}
"""
_OPTSHELP36 = (
    "    static void parse(String[] args, Object target) throws IllegalAccessException {\n"
    "        Map<String, Field> byFlag = new HashMap<>();\n"
    "        for (Field f : target.getClass().getDeclaredFields()) {\n"
    "            Option o = f.getAnnotation(Option.class);\n"
    "            if (o != null) {\n"
    "                byFlag.put(o.value(), f);\n"
    "            }\n"
    "        }\n"
    "        for (int i = 0; i < args.length; i++) {\n"
    "            Field f = byFlag.get(args[i]);\n"
    "            if (f == null) {\n"
    "                throw new IllegalArgumentException(\"unknown option \" + args[i]);\n"
    "            }\n"
    "            if (f.getType() == boolean.class) {\n"
    "                f.setBoolean(target, true);\n"
    "            } else if (f.getType() == int.class) {\n"
    "                f.setInt(target, Integer.parseInt(args[++i]));\n"
    "            } else {\n"
    "                f.set(target, args[++i]);\n"
    "            }\n"
    "        }\n"
    "    }"
)
_ARGS36 = (["--name", "ada"], [], ["--loud", "--times", "2"], ["--times", "3", "--name", "bo", "--loud"],
           ["--colour", "red"])


def _opts_out36(args):
    name, times, loud = "world", 1, False
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--name":
            name = args[i + 1]
            i += 1
        elif a == "--times":
            times = int(args[i + 1])
            i += 1
        elif a == "--loud":
            loud = True
        else:
            return f"error: unknown option {a}"
        i += 1
    g = f"hello {name}"
    if loud:
        g = g.upper() + "!"
    return _nl(*[g] * times)


def _args_case36(args):
    return _case(f"{len(args)}" + (f"\n{' '.join(args)}" if args else "\n"), _opts_out36(args))


_M36.append(_jlesson(
    "m36-framework", "A framework in miniature",
    "A test runner, a validator and an options parser - each a loop over annotated "
    "members.",
    """
Every annotation-driven framework has the same skeleton:

1. **find** the members carrying a particular annotation;
2. **read** the annotation's elements for configuration;
3. **act** on the member - invoke the method, read or write the field.

Three small frameworks show the three shapes.

## A test runner (JUnit, in thirty lines)

```java
for (Method m : sortedByName(ListTests.class.getDeclaredMethods())) {
    if (!m.isAnnotationPresent(Test.class)) continue;
    Object instance = ListTests.class.getDeclaredConstructor().newInstance();
    try {
        m.invoke(instance);
        pass(m);
    } catch (InvocationTargetException e) {
        fail(m, e.getCause());            // the AssertionError the test threw
    }
}
```

Two JUnit habits hide in there. Each test gets a **fresh instance**, so tests
cannot leak state into one another. And an assertion is just a thrown
`AssertionError` - the runner tells "failed" from "passed" by whether the
invoked method threw.

(`getDeclaredConstructor().newInstance()` is the reflective `new`. The older
`Class.newInstance()` is deprecated because it could throw checked exceptions
without declaring them.)

## A validator (Bean Validation)

```java
@NotBlank private String user;
@Range(min = 18, max = 120) private int age;
```

The validator walks the fields, reads each one's value, and checks it against
whatever constraint annotations it carries - the annotation's elements (`min`,
`max`) are the rule's parameters. The class being validated contains no
validation code at all.

## An options parser (picocli, or Spring's `@Value`)

```java
@Option("--times") int times = 1;
```

The parser maps flags to fields, then **writes** each field with the right
conversion for its type: `setBoolean`, `setInt`, or `set` for a String. The
field initialisers supply the defaults.

## Private members

Invoking a private test method, or reading a private field, from *another*
class throws `IllegalAccessException` - reflection still honours access rules
until told otherwise. `m.setAccessible(true)` suppresses the check for that one
member; frameworks call it routinely, which is part of the bargain lesson 36.5
weighs up.
""",
    warmup=[
        _jq("A test runner decides a test failed when…",
            ["invoking it threw (usually an AssertionError)", "it returned false",
             "it printed FAIL", "it took too long"],
            0,
            "The invoked method's exception arrives wrapped in InvocationTargetException."),
        _jq("Why does each test method get a new instance?",
            ["so one test's state cannot leak into another", "for speed",
             "reflection requires it", "static methods cannot be tests"],
            0,
            "JUnit does exactly this."),
    ],
    exercises=[
        _je("j36-fw-runner", "Running the tests",
            "The runner finds every `@Test` method, sorted by name, and runs each on a "
            "fresh instance. Replace `____` with the call that runs the test.",
            _j36t(_TESTS36, _RUNBODY36),
            "                m.invoke(instance);",
            [_data_case36(xs) for xs in _DATA36],
            hints=["`invoke` needs the object to call the method on, then the arguments - "
                   "there are none.",
                   "`m.invoke(instance);`",
                   "If the test throws, the runner lands in the `InvocationTargetException` "
                   "catch.",
                   "`helper()` has no `@Test`, so it is never run."],
            difficulty="Easy"),

        _jfix("j36-fw-private", "Tests the runner was not allowed to call",
              "The test methods were made `private`, and now `invoke` throws "
              "`IllegalAccessException` before a single test runs. Leave them private, and "
              "let the runner in.",
              _j36t(_TESTS36.replace("    void allPositive()", "    private void allPositive()")
                    .replace("    void sorted()", "    private void sorted()")
                    .replace("    void notEmpty()", "    private void notEmpty()")
                    .replace("    void sumBelowHundred()", "    private void sumBelowHundred()"),
                    _RUNBODY36),
              _j36t(_TESTS36.replace("    void allPositive()", "    private void allPositive()")
                    .replace("    void sorted()", "    private void sorted()")
                    .replace("    void notEmpty()", "    private void notEmpty()")
                    .replace("    void sumBelowHundred()", "    private void sumBelowHundred()"),
                    _RUNBODY36.replace("                m.invoke(instance);",
                                       "                m.setAccessible(true);\n"
                                       "                m.invoke(instance);")),
              [_data_case36(xs) for xs in _DATA36],
              hints=["Reflection still enforces `private` - from another class, the call is "
                     "refused.",
                     "`m.setAccessible(true);` switches the check off for that one method.",
                     "Call it before `invoke`.",
                     "JUnit 5 does the same, which is why its test methods need not be "
                     "public."],
              difficulty="Easy"),

        _jch("j36-fw-validate", "A validator", "Hard",
             "Write `validate(o)`: for each declared field, sorted by name, report "
             "`field: must not be blank` for a `@NotBlank` field that is null or blank, and "
             "`field: must be between MIN and MAX` for a `@Range` int outside its bounds. "
             "`main` prints `ok` or the problems joined by `; `.",
             _j36t(_VALID36,
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            String user = sc.next();\n"
                   "            int age = sc.nextInt();\n"
                   "            String country = sc.next();\n"
                   "            int rating = sc.nextInt();\n"
                   "            Account a = new Account(user.equals(\"-\") ? \"\" : user, age,\n"
                   "                    country.equals(\"-\") ? null : country, rating);\n"
                   "            List<String> problems = validate(a);\n"
                   "            System.out.println(problems.isEmpty() ? \"ok\" : String.join(\"; \", problems));\n"
                   "        }",
                   helpers=_VALIDHELP36),
             _VALIDHELP36,
             [_rows36(rows, _nl(*[_valid_out36(*r) for r in rows])) for rows in _ACCTS36],
             hints=["Sort the fields by name so the problems come out in a fixed order.",
                    "`setAccessible(true)` and `f.get(o)` for each value.",
                    "Blank means null OR `toString().isBlank()` - the input uses both.",
                    "For `@Range`, read `r.min()` and `r.max()` and unbox the value: "
                    "`(Integer) value`.",
                    "`Account` itself contains no validation logic - the annotations are "
                    "the rules."]),

        _jch("j36-fw-options", "An options parser", "Hard",
             "Write `parse(args, target)`: map each `@Option` flag to its field, then walk "
             "the arguments - a boolean field is set to true by its flag alone; an int or "
             "String field takes the next argument. An unknown flag throws "
             "`IllegalArgumentException(\"unknown option X\")`.",
             _j36t(_OPTS36,
                   "        int n = sc.nextInt();\n"
                   "        String[] argv = new String[n];\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            argv[i] = sc.next();\n"
                   "        }\n"
                   "        Settings s = new Settings();\n"
                   "        try {\n"
                   "            parse(argv, s);\n"
                   "        } catch (IllegalArgumentException e) {\n"
                   "            System.out.println(\"error: \" + e.getMessage());\n"
                   "            return;\n"
                   "        }\n"
                   "        String greeting = \"hello \" + s.name;\n"
                   "        if (s.loud) {\n"
                   "            greeting = greeting.toUpperCase() + \"!\";\n"
                   "        }\n"
                   "        for (int i = 0; i < s.times; i++) {\n"
                   "            System.out.println(greeting);\n"
                   "        }",
                   helpers=_OPTSHELP36),
             _OPTSHELP36,
             [_args_case36(a) for a in _ARGS36],
             hints=["First build a `Map<String, Field>` from flag to field.",
                    "`f.getType() == boolean.class` - compare Class objects with `==`.",
                    "`f.setBoolean(target, true)`, `f.setInt(target, ...)`, `f.set(target, ...)`.",
                    "A flag that takes a value consumes the next argument: `args[++i]`.",
                    "The fields' initialisers are the defaults: `world`, 1, false."]),
    ],
    quiz=[
        _jq("`clazz.getDeclaredConstructor().newInstance()` is preferred over "
            "`clazz.newInstance()` because…",
            ["the old one could throw checked exceptions it did not declare",
             "it is faster", "it works for interfaces", "it skips constructors"],
            0,
            "Constructor.newInstance wraps them in InvocationTargetException instead."),
        _jq("A framework reads a private field from another class. It must first…",
            ["call setAccessible(true) on the Field", "make the field public",
             "use getMethods()", "nothing"],
            0,
            "Reflection respects access until told not to."),
    ],
))


# ===========================================================================
# 36.5 Proxies, and the costs
# ===========================================================================

_GREETER36 = """
interface Greeter {
    String greet(String name);

    String farewell(String name);
}

class PlainGreeter implements Greeter {
    public String greet(String name) {
        return "hello " + name;
    }

    public String farewell(String name) {
        return "bye " + name;
    }
}
"""
_LOGPROXY36 = (
    "        Greeter real = new PlainGreeter();\n"
    "        Greeter logged = (Greeter) Proxy.newProxyInstance(\n"
    "                Greeter.class.getClassLoader(),\n"
    "                new Class<?>[] {Greeter.class},\n"
    "                (proxy, method, margs) -> {\n"
    "                    System.out.println(\"call \" + method.getName() + \"(\" + margs[0] + \")\");\n"
    "                    return method.invoke(real, margs);\n"
    "                });\n"
)
_GCALLS36 = ([("greet", "ada")], [("farewell", "bo"), ("greet", "cy")], [("greet", "x"), ("greet", "y")],
             [("farewell", "solo")], [("greet", "p"), ("farewell", "q"), ("greet", "r")])


def _gcalls_out36(rows):
    out = []
    for (m, nm) in rows:
        out.append(f"call {m}({nm})")
        out.append(("hello " if m == "greet" else "bye ") + nm)
    return _nl(*out)


_COUNTING36 = (
    "    @SuppressWarnings(\"unchecked\")\n"
    "    static <T> T counting(Class<T> type, T target, Map<String, Integer> counts) {\n"
    "        return (T) Proxy.newProxyInstance(\n"
    "                type.getClassLoader(),\n"
    "                new Class<?>[] {type},\n"
    "                (proxy, method, margs) -> {\n"
    "                    counts.merge(method.getName(), 1, Integer::sum);\n"
    "                    return method.invoke(target, margs);\n"
    "                });\n"
    "    }"
)
_STACKI36 = """
interface Stack {
    void push(int x);

    int pop();

    boolean isEmpty();
}

class ArrayStack implements Stack {
    private final Deque<Integer> items = new ArrayDeque<>();

    public void push(int x) {
        items.push(x);
    }

    public int pop() {
        return items.pop();
    }

    public boolean isEmpty() {
        return items.isEmpty();
    }
}
"""
_PUSHES36 = ([1, 2, 3], [7], [4, 4], [9, 8, 7, 6], [5, 0])


def _counting_out36(xs):
    n = len(xs)
    return _nl(_sp(list(reversed(xs))), "{" + f"isEmpty={n + 1}, pop={n}, push={n}" + "}")


_SECRET36 = """
class Vault {
    private final String code;

    Vault(String code) {
        this.code = code;
    }
}
"""
_WORDS36 = ("sesame", "1234", "open", "x", "hunter2")

_PRICER36 = """
interface Pricer {
    int price(String item, int quantity);
}

class SlowPricer implements Pricer {
    int realCalls;

    public int price(String item, int quantity) {
        realCalls++;
        return item.length() * 100 * quantity;
    }
}
"""
_MEMO36 = (
    "    static Pricer memoize(Pricer target) {\n"
    "        Map<List<Object>, Object> cache = new HashMap<>();\n"
    "        return (Pricer) Proxy.newProxyInstance(\n"
    "                Pricer.class.getClassLoader(),\n"
    "                new Class<?>[] {Pricer.class},\n"
    "                (proxy, method, margs) -> {\n"
    "                    List<Object> key = new ArrayList<>();\n"
    "                    key.add(method.getName());\n"
    "                    key.addAll(Arrays.asList(margs));\n"
    "                    if (!cache.containsKey(key)) {\n"
    "                        cache.put(key, method.invoke(target, margs));\n"
    "                    }\n"
    "                    return cache.get(key);\n"
    "                });\n"
    "    }"
)
_QUOTES36 = ([("tea", 2), ("tea", 2), ("cake", 1)], [("x", 1)], [("pie", 3), ("pie", 4), ("pie", 3)],
             [("jam", 1), ("jam", 1), ("jam", 1)], [("a", 1), ("bb", 2), ("a", 1), ("bb", 2)])


def _quotes_out36(rows):
    seen, out = set(), []
    for (it, q) in rows:
        seen.add((it, q))
        out.append(f"{it} x{q} = {len(it) * 100 * q}")
    out.append(f"real calls {len(seen)}")
    return _nl(*out)


_M36.append(_jlesson(
    "m36-proxies", "Dynamic proxies - and what reflection costs",
    "An object that implements any interface at run time; and the wall the JDK "
    "built around itself.",
    """
## Dynamic proxies

Module 35's decorator needed a class per interface. A **dynamic proxy** is a
decorator the JVM writes for you, at run time, for *any* interface:

```java
Greeter logged = (Greeter) Proxy.newProxyInstance(
        Greeter.class.getClassLoader(),
        new Class<?>[] {Greeter.class},                 // the interfaces to implement
        (proxy, method, args) -> {                      // every call lands here
            System.out.println("call " + method.getName());
            return method.invoke(real, args);           // ...and is passed on
        });
```

The third argument is an `InvocationHandler` - one method, so a lambda - which
receives the `Method` being called and its arguments for **every** call on the
proxy. It can log, count, time, cache, check permissions, retry, or never call
the real object at all. This is how Spring adds transactions to your methods,
how Mockito makes mocks, and how Java's RMI made remote calls look local.

A proxy works only for **interfaces** (frameworks that proxy classes generate
bytecode with libraries such as ByteBuddy) - one more reason to program to
interfaces (module 14).

## What reflection costs

Reflection is the right tool for frameworks and the wrong one for almost
everything else:

* **No compile-time checking.** `getMethod("add")` compiles whether or not
  `add` exists, and a rename that the compiler would have caught becomes a
  run-time exception.
* **Checked exceptions everywhere**, and wrapped ones (`InvocationTargetException`).
* **Speed.** A reflective call is slower than a direct one, and harder for the
  JIT to optimise - usually fine for start-up wiring, not in a hot loop.
* **Encapsulation.** `setAccessible(true)` reads anything private, which is
  exactly why the JDK now refuses it for its own internals.

## The wall

Since Java 16 the JDK's own packages are **strongly encapsulated**: reflection
from your code into a private member of, say, `java.lang.String` fails.

```java
Field f = String.class.getDeclaredField("value");   // finding it is fine
f.setAccessible(true);   // InaccessibleObjectException - java.base does not open java.lang
```

The same call on a private field of *your own* class still works. Old libraries
that poked at JDK internals broke on this change - which was the point - and
command-line flags like `--add-opens` exist to let them through deliberately.
""",
    warmup=[
        _jq("`Proxy.newProxyInstance` can implement…",
            ["interfaces only", "any class", "final classes", "records"],
            0,
            "Proxying a class needs bytecode generation instead."),
        _jq("`setAccessible(true)` on a private field of `java.lang.String` (Java 17+)…",
            ["throws InaccessibleObjectException", "works", "returns false",
             "is a compile error"],
            0,
            "The JDK's own internals are strongly encapsulated."),
    ],
    exercises=[
        _je("j36-px-log", "A logging proxy",
            "Wrap a `Greeter` in a proxy that prints `call method(arg)` before passing each "
            "call on. Replace `____` with the line that passes the call to the real "
            "object.",
            _j36t(_GREETER36,
                  _LOGPROXY36
                  + "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String which = sc.next();\n"
                    "            String name = sc.next();\n"
                    "            System.out.println(which.equals(\"greet\") ? logged.greet(name) : logged.farewell(name));\n"
                    "        }"),
            "                    return method.invoke(real, margs);",
            [_rows36(rows, _gcalls_out36(rows)) for rows in _GCALLS36],
            hints=["The handler receives the `Method` that was called on the proxy.",
                   "Call that same method on the real object, with the same arguments.",
                   "`return method.invoke(real, margs);`",
                   "The handler must return what the real method returned - the proxy "
                   "hands it back to the caller."],
            difficulty="Easy"),

        _jch("j36-px-count", "A counting proxy for any interface", "Medium",
             "Write the generic `counting(type, target, counts)`: a proxy of interface "
             "`type` that records how many times each method name is called, then passes "
             "the call on. `main` uses it on a `Stack` and prints the counts.",
             _j36t(_STACKI36,
                   "        Map<String, Integer> counts = new TreeMap<>();\n"
                   "        Stack s = counting(Stack.class, new ArrayStack(), counts);\n"
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            s.push(sc.nextInt());\n"
                   "        }\n"
                   "        StringBuilder out = new StringBuilder();\n"
                   "        while (!s.isEmpty()) {\n"
                   "            if (out.length() > 0) out.append(' ');\n"
                   "            out.append(s.pop());\n"
                   "        }\n"
                   "        System.out.println(out);\n"
                   "        System.out.println(counts);",
                   helpers=_COUNTING36),
             _COUNTING36,
             [_acase(xs, _counting_out36(xs)) for xs in _PUSHES36],
             hints=["`static <T> T counting(Class<T> type, T target, Map<String, Integer> counts)`",
                    "`Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler)`",
                    "The handler: `counts.merge(method.getName(), 1, Integer::sum)`, then "
                    "`return method.invoke(target, margs);`",
                    "The cast to `T` is unchecked - module 24's promise - hence the "
                    "`@SuppressWarnings`.",
                    "`isEmpty` is called once more than `pop`: the loop's last check."]),

        _je("j36-px-wall", "The wall around the JDK",
            "Try to open the private `value` field of a `String`, and report what happens; "
            "then open the private `code` field of your OWN `Vault` class and read it. "
            "Replace `____` with the line that opens the Vault's field.",
            _j36t(_SECRET36,
                  "        String word = sc.next();\n"
                  "        Field jdk = String.class.getDeclaredField(\"value\");\n"
                  "        try {\n"
                  "            jdk.setAccessible(true);\n"
                  "            System.out.println(\"opened String.value\");\n"
                  "        } catch (RuntimeException e) {\n"
                  "            System.out.println(e.getClass().getSimpleName());\n"
                  "        }\n"
                  "        Vault v = new Vault(word);\n"
                  "        Field own = Vault.class.getDeclaredField(\"code\");\n"
                  "        own.setAccessible(true);\n"
                  "        System.out.println(\"vault code: \" + own.get(v));"),
            "        own.setAccessible(true);",
            [_case(w, _nl("InaccessibleObjectException", f"vault code: {w}")) for w in _WORDS36],
            hints=["Your own class, in your own (unnamed) module, can be opened freely.",
                   "`own.setAccessible(true);`",
                   "The JDK's `java.lang` package is not opened to your code, so the first "
                   "attempt throws.",
                   "Finding the field is allowed; only opening it is refused."],
            difficulty="Easy"),

        _jch("j36-px-memo", "A caching proxy", "Hard",
             "Write `memoize(target)`: a `Pricer` proxy that answers a repeated call (same "
             "method, same arguments) from a cache, and passes only new ones to the slow "
             "real pricer. `main` shows the real pricer is called once per distinct "
             "question.",
             _j36t(_PRICER36,
                   "        SlowPricer slow = new SlowPricer();\n"
                   "        Pricer fast = memoize(slow);\n"
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            String item = sc.next();\n"
                   "            int q = sc.nextInt();\n"
                   "            System.out.println(item + \" x\" + q + \" = \" + fast.price(item, q));\n"
                   "        }\n"
                   "        System.out.println(\"real calls \" + slow.realCalls);",
                   helpers=_MEMO36),
             _MEMO36,
             [_rows36(rows, _quotes_out36(rows)) for rows in _QUOTES36],
             hints=["The cache key must include the method name AND every argument.",
                    "A `List` makes a good key: `List`'s `equals` and `hashCode` compare "
                    "elements.",
                    "`Arrays.asList(margs)` turns the argument array into a list.",
                    "`containsKey` before `get` - a cached value could legitimately be null.",
                    "This is module 35's caching decorator, written once for any "
                    "interface."]),
    ],
    quiz=[
        _jq("Mockito's `mock(Service.class)` and Spring's `@Transactional` both rely on…",
            ["proxies that intercept every call", "annotations with SOURCE retention",
             "subclassing final classes", "setAccessible on the JDK"],
            0,
            "An InvocationHandler (or generated bytecode) sees each call first."),
        _jq("The biggest everyday cost of reflection is…",
            ["mistakes the compiler would have caught become run-time failures",
             "memory", "it cannot call methods", "it needs threads"],
            0,
            "A string naming a method is not checked until it runs."),
    ],
))


# ===========================================================================
# Capstone - a tiny test framework
# ===========================================================================

_CAPTYPES36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Test {
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Disabled {
    String value();
}

class Stats {
    static int[] values;

    static int total() {
        int t = 0;
        for (int v : values) {
            t += v;
        }
        return t;
    }

    static int mean() {
        return total() / values.length;
    }

    static int max() {
        if (values.length == 0) {
            throw new IllegalStateException("empty");
        }
        int m = values[0];
        for (int v : values) {
            m = Math.max(m, v);
        }
        return m;
    }
}

class StatsTests {
    static void check(boolean ok, String message) {
        if (!ok) {
            throw new AssertionError(message);
        }
    }

    @Test
    void totalIsNonNegative() {
        check(Stats.total() >= 0, "total is " + Stats.total());
    }

    @Test
    void meanBelowTen() {
        int m = Stats.mean();
        check(m < 10, "mean is " + m);
    }

    @Test
    void hasEvenCount() {
        check(Stats.values.length % 2 == 0, "odd count " + Stats.values.length);
    }

    @Test
    @Disabled("flaky on Fridays")
    void speed() {
        throw new AssertionError("never runs");
    }

    @Test
    void maxBelowHundred() {
        check(Stats.max() < 100, "max is " + Stats.max());
    }

    void notATest() {
        throw new AssertionError("never runs either");
    }
}
"""
_CAPRUN36 = (
    "    static void runTests(Class<?> type) throws Exception {\n"
    "        Method[] methods = type.getDeclaredMethods();\n"
    "        Arrays.sort(methods, Comparator.comparing(Method::getName));\n"
    "        int passed = 0, failed = 0, errors = 0, skipped = 0;\n"
    "        for (Method m : methods) {\n"
    "            if (!m.isAnnotationPresent(Test.class)) {\n"
    "                continue;\n"
    "            }\n"
    "            Disabled d = m.getAnnotation(Disabled.class);\n"
    "            if (d != null) {\n"
    "                System.out.println(\"SKIP \" + m.getName() + \": \" + d.value());\n"
    "                skipped++;\n"
    "                continue;\n"
    "            }\n"
    "            Object instance = type.getDeclaredConstructor().newInstance();\n"
    "            try {\n"
    "                m.invoke(instance);\n"
    "                System.out.println(\"PASS \" + m.getName());\n"
    "                passed++;\n"
    "            } catch (InvocationTargetException e) {\n"
    "                Throwable cause = e.getCause();\n"
    "                if (cause instanceof AssertionError) {\n"
    "                    System.out.println(\"FAIL \" + m.getName() + \": \" + cause.getMessage());\n"
    "                    failed++;\n"
    "                } else {\n"
    "                    System.out.println(\"ERROR \" + m.getName() + \": \" + cause.getClass().getSimpleName());\n"
    "                    errors++;\n"
    "                }\n"
    "            }\n"
    "        }\n"
    "        System.out.println(passed + \" passed, \" + failed + \" failed, \" + errors + \" errors, \"\n"
    "                + skipped + \" skipped\");\n"
    "    }"
)
_CAPDATA36 = ([2, 4, 6, 8], [150, -200, 7], [], [30, 50], [1, 2, 3])


def _cap_out36(xs):
    res = []
    total = sum(xs)
    res.append(("hasEvenCount", "pass" if len(xs) % 2 == 0 else ("fail", f"odd count {len(xs)}")))
    if not xs:
        res.append(("maxBelowHundred", ("error", "IllegalStateException")))
        res.append(("meanBelowTen", ("error", "ArithmeticException")))
    else:
        mx = max(xs)
        res.append(("maxBelowHundred", "pass" if mx < 100 else ("fail", f"max is {mx}")))
        mean = _jdiv(total, len(xs))
        res.append(("meanBelowTen", "pass" if mean < 10 else ("fail", f"mean is {mean}")))
    res.append(("speed", ("skip", "flaky on Fridays")))
    res.append(("totalIsNonNegative", "pass" if total >= 0 else ("fail", f"total is {total}")))
    lines = []
    c = {"pass": 0, "fail": 0, "error": 0, "skip": 0}
    for (name, r) in sorted(res):
        if r == "pass":
            lines.append(f"PASS {name}")
            c["pass"] += 1
        else:
            kind, msg = r
            lines.append(f"{kind.upper()} {name}: {msg}")
            c[kind] += 1
    lines.append(f"{c['pass']} passed, {c['fail']} failed, {c['error']} errors, {c['skip']} skipped")
    return _nl(*lines)


def _cap_case36(xs):
    return _case(f"{len(xs)}\n{_sp(xs)}" if xs else "0\n", _cap_out36(xs))


_M36_CAP = _jcap(
    "A tiny test framework",
    """
Write the runner at the heart of a test framework: `runTests(testClass)`.

* Consider only methods annotated `@Test`, **sorted by name** (reflection promises
  no order, and a test report must be repeatable).
* A test also annotated `@Disabled("reason")` is not run: print `SKIP name: reason`.
* Run every other test on a **fresh instance** of the test class.
* If it returns normally: `PASS name`. If it throws an `AssertionError`:
  `FAIL name: message`. If it throws anything else, the test itself is broken:
  `ERROR name: ExceptionSimpleName`.
* Finish with `P passed, F failed, E errors, S skipped`.

The tests exercise a small `Stats` class on the numbers read from stdin - so an
empty input makes two tests *error* (a division by zero, an empty maximum)
rather than fail, which is exactly the distinction the runner must draw.
""",
    _jch("j36-cap-runner", "A tiny test framework", "Hard",
         "Write `runTests` as the brief describes.",
         _j36t(_CAPTYPES36,
               "        int n = sc.nextInt();\n"
               "        Stats.values = new int[n];\n"
               "        for (int i = 0; i < n; i++) {\n"
               "            Stats.values[i] = sc.nextInt();\n"
               "        }\n"
               "        runTests(StatsTests.class);",
               helpers=_CAPRUN36),
         _CAPRUN36,
         [_cap_case36(xs) for xs in _CAPDATA36],
         hints=["`getDeclaredMethods()`, then `Arrays.sort(..., Comparator.comparing(Method::getName))`.",
                "Skip anything without `@Test` - `notATest` would otherwise run and fail.",
                "Check `@Disabled` BEFORE creating an instance or invoking.",
                "`type.getDeclaredConstructor().newInstance()` for each test.",
                "Everything the test throws arrives as an `InvocationTargetException`; "
                "decide on `getCause()`.",
                "`cause instanceof AssertionError` separates FAIL from ERROR.",
                "The ERROR line prints the exception's simple name, never its message - "
                "JDK messages change between versions."]),
    example_io="stdin:  3\n        1 2 3\n\n"
               "stdout: FAIL hasEvenCount: odd count 3\n        PASS maxBelowHundred\n"
               "        PASS meanBelowTen\n        SKIP speed: flaky on Fridays\n"
               "        PASS totalIsNonNegative\n"
               "        3 passed, 1 failed, 0 errors, 1 skipped",
    rubric=[
        "Only `@Test` methods run, in name order.",
        "`@Disabled` tests are reported with their reason and never invoked.",
        "Each test runs on a new instance of the test class.",
        "FAIL (an AssertionError) is distinguished from ERROR (any other exception).",
        "The cause is taken from the InvocationTargetException, not the wrapper itself.",
    ],
)


_MODULES.append(_jmod(
    36, 13, "Advanced Java",
    "Annotations and reflection",
    "How frameworks see your code: types as values, members found by name, "
    "annotations read at run time - built up into a test runner, a validator, an "
    "options parser and a proxy.",
    """
Reflection is how JUnit finds your tests, how Spring wires your objects, how
Jackson maps JSON and how Mockito fakes an interface. This module builds a small
version of each.

* **`Class` objects**: `getClass()`, `X.class`, `Class.forName` (fully qualified).
  Superclass chains, `getInterfaces()` (declared order), `isInstance`, and the
  `is...` questions - even `int.class` and `int[][].class` exist.
* **Members**: `getDeclaredFields`/`Methods` (everything declared here) versus
  `getMethods` (public, inherited). **Their order is unspecified - always sort.**
  `get`/`set`/`invoke`, `setAccessible`, and `InvocationTargetException`, whose
  `getCause()` is the real failure.
* **Annotations**: declaring with `@interface`, elements and defaults, `value`
  shorthand, `@Target`, and **`@Retention(RUNTIME)`** - without which reflection
  sees nothing.
* **Frameworks in miniature**: find annotated members, read their configuration,
  act on them - a test runner, a validator, an options parser.
* **Proxies and costs**: `Proxy.newProxyInstance` as a decorator for any
  interface; and reflection's price - no compile-time checks, checked exceptions,
  speed, broken encapsulation - with the JDK's own internals now walled off.
""",
    _M36,
    capstone=_M36_CAP,
    objectives=[
        "Obtain a `Class` object three ways, and use `Class.forName` with a fully qualified name.",
        "Walk a superclass chain, and list a class's interfaces in declared order.",
        "Distinguish `getDeclaredMethods` from `getMethods`.",
        "Explain why reflective member lists must be sorted before being printed or compared.",
        "Read and write fields and invoke methods reflectively, including private ones.",
        "Unwrap `InvocationTargetException` to find the real failure.",
        "Declare an annotation with elements, defaults, a target and a retention policy.",
        "Explain why an annotation without RUNTIME retention is invisible to reflection.",
        "Build a test runner, a validator and an options parser from annotated members.",
        "Write a dynamic proxy for logging, counting or caching.",
        "Weigh reflection's costs, and explain the JDK's strong encapsulation.",
    ],
    why="Reflection questions test whether you understand the frameworks you use: how "
        "does JUnit find tests, why does my annotation not work (retention), why did "
        "this exception arrive wrapped, how does Spring add a transaction to my method "
        "(a proxy), why did this library break on Java 17 (strong encapsulation). "
        "Writing a small test runner or validator is also a favourite senior-level "
        "exercise, because it touches annotations, reflection, exceptions and design at "
        "once.",
    est_minutes=330,
    glossary=[
        _jg("Reflection", "Inspecting and using types, fields and methods at run time "
                          "through objects that describe them."),
        _jg("Class<T>", "The run-time description of a type; obtained with getClass(), "
                        "X.class or Class.forName."),
        _jg("Class.forName", "Loads a class by its fully qualified name; throws "
                             "ClassNotFoundException."),
        _jg("getDeclaredMethods", "Every method the class itself declares, any access, "
                                  "not inherited - in no specified order."),
        _jg("getMethods", "Every public method, including inherited ones."),
        _jg("setAccessible", "Suppresses access checks for one reflected member; refused "
                             "for the JDK's own internals since Java 16."),
        _jg("InvocationTargetException", "Wraps an exception thrown by a method called "
                                         "through reflection; getCause() is the real one."),
        _jg("@interface", "Declares an annotation type."),
        _jg("Retention", "How long an annotation survives: SOURCE, CLASS (the default) "
                         "or RUNTIME."),
        _jg("Target", "Which kinds of declaration an annotation may be placed on."),
        _jg("Marker annotation", "An annotation with no elements, such as @Test."),
        _jg("Dynamic proxy", "An object created at run time that implements given "
                             "interfaces by forwarding every call to an InvocationHandler."),
        _jg("InvocationHandler", "Receives the proxy, the Method called and its "
                                 "arguments, for every call on a proxy."),
        _jg("Strong encapsulation", "Since Java 16, code cannot reflectively open "
                                    "private members of JDK packages unless explicitly "
                                    "allowed (--add-opens)."),
    ],
    cheatsheet="""
```java
// --- Class objects --------------------------------------------------------------
obj.getClass()   String.class   int.class   Class.forName("java.util.ArrayList")
c.getSimpleName()  c.getName()  c.getSuperclass()  c.getInterfaces()  // declared order
c.isInterface()  c.isArray()  c.isPrimitive()  c.isEnum()  c.isRecord()
c.getComponentType()   Shape.class.isInstance(obj)

// --- members: ALWAYS SORT -----------------------------------------------------
Field[] fs = c.getDeclaredFields();                 // any access, not inherited
Arrays.sort(fs, Comparator.comparing(Field::getName));
Modifier.isStatic(f.getModifiers())
f.setAccessible(true);  f.get(obj);  f.set(obj, v);  f.setInt(obj, 3);
Method m = c.getMethod("add", int.class, int.class);   // public, by signature
try { m.invoke(obj, 2, 3); }
catch (InvocationTargetException e) { Throwable real = e.getCause(); }
Object o = c.getDeclaredConstructor().newInstance();

// --- annotations ---------------------------------------------------------------
@Retention(RetentionPolicy.RUNTIME)     // default is CLASS: invisible at run time!
@Target(ElementType.METHOD)
@interface Priority { int value() default 3; }
@Priority(1) void deploy() { }          // `value` can be positional
m.isAnnotationPresent(Priority.class)   m.getAnnotation(Priority.class).value()

// --- proxies ---------------------------------------------------------------------
Greeter g = (Greeter) Proxy.newProxyInstance(
        Greeter.class.getClassLoader(), new Class<?>[] {Greeter.class},
        (proxy, method, args) -> { log(method); return method.invoke(real, args); });

// --- the wall ------------------------------------------------------------------------
String.class.getDeclaredField("value").setAccessible(true);   // InaccessibleObjectException
```
""",
    self_check=[
        "Can you get a `Class` object three ways, and say when `Class.forName` fails?",
        "Can you explain the difference between `getDeclaredMethods` and `getMethods`?",
        "Can you explain why a reflective program must sort the members it prints?",
        "Can you call a method by name, and handle the exception it throws?",
        "Can you read a private field of another class, and say what it takes?",
        "Can you declare an annotation with an element and a default?",
        "Can you explain why an annotation might be invisible to `getAnnotation`?",
        "Can you write a test runner that tells a failure from an error?",
        "Can you write a proxy that logs or counts every call to an interface?",
        "Can you list three costs of reflection, and say what changed in Java 16?",
    ],
    review=[
        _jq("A framework ignores your custom annotation entirely. The first thing to "
            "check is…",
            ["that it has @Retention(RetentionPolicy.RUNTIME)", "that it is public",
             "that it has elements", "that the class is final"],
            0,
            "CLASS retention is the default, and invisible to reflection."),
        _jq("```java\ntry { m.invoke(obj); }\ncatch (IllegalStateException e) { ... }\n```\nThe method throws IllegalStateException. The catch block…",
            ["never runs - the exception arrives as InvocationTargetException",
             "runs", "runs twice", "does not compile"],
            0,
            "Catch the wrapper and inspect getCause()."),
        _jq("A test prints fields from `getDeclaredFields()` without sorting. On a future "
            "JDK its expected output…",
            ["may stop matching - the order is unspecified", "is guaranteed stable",
             "becomes alphabetical", "throws"],
            0,
            "Sort by name whenever order is visible."),
        _jq("`Proxy.newProxyInstance` cannot proxy…",
            ["a class that implements no interface", "an interface", "several interfaces",
             "a generic interface"],
            0,
            "JDK proxies implement interfaces only."),
        _jq("`setAccessible(true)` on your own class's private field (Java 17)…",
            ["works", "throws InaccessibleObjectException", "is a compile error",
             "returns false"],
            0,
            "Only the JDK's own packages are walled off."),
    ],
    milestone="You can read a type's structure at run time, find and use members by name "
              "and annotation, and build the core of a test framework, a validator and a "
              "proxy - and you know why the frameworks you use behave as they do, and what "
              "reflection costs.",
))
