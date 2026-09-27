# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 36 practice - annotations and reflection.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[36]`.
#
# The module's determinism rule holds here too: any member list that reaches
# the output is SORTED first. Classes whose members are counted are plain
# classes with no lambdas, no inner classes, and no enum or record machinery,
# so the compiler adds no synthetic members to the counts.
# ---------------------------------------------------------------------------


def _p36(eid, title, difficulty, prompt, types, body, region, tests, hints, helpers=""):
    return _jch(eid, title, difficulty, prompt, _j36t(types, body, helpers=helpers),
                region.strip("\n"), tests, hints)


# --- Family A - Class objects ------------------------------------------------------

_JNAMES36 = (["ArrayList"], ["HashMap", "Deque"], ["Iterator", "TreeSet", "Optional"], ["Scanner"],
             ["Random", "List"])

_ANIMALS36 = """
class Animal {
}

class Mammal extends Animal {
}

class Dog extends Mammal {
}

class Puppy extends Dog {
}

class Bird extends Animal {
}

class Cat extends Mammal {
}
"""
_PARENT36 = {"Animal": "Object", "Mammal": "Animal", "Dog": "Mammal", "Puppy": "Dog",
             "Bird": "Animal", "Cat": "Mammal", "Object": None}
_ANIMALMAP36 = (
    "        Map<String, Class<?>> types = new HashMap<>();\n"
    "        for (Class<?> c : List.of(Animal.class, Mammal.class, Dog.class, Puppy.class, Bird.class, Cat.class)) {\n"
    "            types.put(c.getSimpleName(), c);\n"
    "        }\n"
)


def _chain36(name):
    out = []
    while name is not None:
        out.append(name)
        name = _PARENT36[name]
    return out


_DEPTHS36 = (["Animal", "Puppy"], ["Dog"], ["Cat", "Bird", "Mammal"], ["Puppy", "Puppy"], ["Bird"])
_PAIRS36 = ([("Dog", "Cat")], [("Puppy", "Bird")], [("Dog", "Puppy"), ("Cat", "Cat")], [("Animal", "Bird")],
            [("Puppy", "Cat"), ("Bird", "Mammal")])


def _common36(a, b):
    ca = _chain36(a)
    for x in _chain36(b):
        if x in ca:
            return x
    return "Object"


_IFACEH36 = """
interface Movable {
}

interface Vehicle extends Movable {
}

interface Electric {
}

class Car implements Vehicle {
}

class Tesla extends Car implements Electric {
}

class Rock {
}

class Scooter implements Movable, Electric {
}
"""
_IFMAP36 = (
    "        Map<String, Class<?>> types = new HashMap<>();\n"
    "        for (Class<?> c : List.of(Movable.class, Vehicle.class, Electric.class, Car.class, Tesla.class,\n"
    "                Rock.class, Scooter.class)) {\n"
    "            types.put(c.getSimpleName(), c);\n"
    "        }\n"
)
_DIRECT36 = {"Car": {"Vehicle"}, "Tesla": {"Electric"}, "Rock": set(), "Scooter": {"Movable", "Electric"}}
_ASSIGN36 = {"Car": {"Vehicle", "Movable"}, "Tesla": {"Electric", "Vehicle", "Movable"}, "Rock": set(),
             "Scooter": {"Movable", "Electric"}}
_IFQ36 = ([("Car", "Movable")], [("Tesla", "Vehicle"), ("Tesla", "Electric")], [("Rock", "Movable")],
          [("Scooter", "Movable"), ("Car", "Electric")], [("Tesla", "Movable")])

_ARRS36 = (["int[][]"], ["String"], ["String[]", "double[][][]"], ["int"], ["long[][]", "int[]"])
_ARRMAP36 = (
    "        Map<String, Class<?>> types = new HashMap<>();\n"
    "        types.put(\"int\", int.class);\n"
    "        types.put(\"int[]\", int[].class);\n"
    "        types.put(\"int[][]\", int[][].class);\n"
    "        types.put(\"long[][]\", long[][].class);\n"
    "        types.put(\"String\", String.class);\n"
    "        types.put(\"String[]\", String[].class);\n"
    "        types.put(\"double[][][]\", double[][][].class);\n"
)


def _arr36(t):
    return f"{t}: {t.count('[]')} dimensions of {t.replace('[]', '')}"


_P36_A = _jfam(
    "p36-class", "`Class` objects",
    "Names, chains, common ancestors, `isAssignableFrom`, and arrays of arrays.",
    """
```java
c.getName()                     // "java.util.ArrayList"
c.getSuperclass()               // walk up until null
Movable.class.isAssignableFrom(c)   // c is a Movable, directly OR transitively
c.getInterfaces()               // DIRECT interfaces only
c.getComponentType()            // one array level down
```

`getInterfaces()` answers "what did this class write after `implements`?" -
which misses interfaces inherited from a superclass, or extended by another
interface. `isAssignableFrom` answers the question you usually meant: could a
value of this class be assigned to that type?
""",
    [
        _p36("j36-pa-name", "Simple and full names", "Intro",
             "For each `java.util` type, print its simple name and its fully qualified "
             "name.",
             "",
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            Class<?> c = Class.forName(\"java.util.\" + sc.next());\n"
             "            System.out.println(c.getSimpleName() + \" = \" + c.getName());\n"
             "        }",
             "        for (int i = 0; i < n; i++) {\n"
             "            Class<?> c = Class.forName(\"java.util.\" + sc.next());\n"
             "            System.out.println(c.getSimpleName() + \" = \" + c.getName());\n"
             "        }",
             [_toks36(ts, _nl(*[f"{t} = java.util.{t}" for t in ts])) for ts in _JNAMES36],
             ["`Class.forName` needs the full name.",
              "`getSimpleName()` and `getName()` give the two forms.",
              "Interfaces (`Deque`, `List`) have Class objects too."]),

        _p36("j36-pa-depth", "How deep is it?", "Easy",
             "For each class in the hierarchy, print its chain up to `Object` and its depth "
             "(the number of superclasses above it).",
             _ANIMALS36,
             _ANIMALMAP36
             + "        int n = sc.nextInt();\n"
               "        for (int i = 0; i < n; i++) {\n"
               "            Class<?> c = types.get(sc.next());\n"
               "            List<String> chain = new ArrayList<>();\n"
               "            for (Class<?> k = c; k != null; k = k.getSuperclass()) {\n"
               "                chain.add(k.getSimpleName());\n"
               "            }\n"
               "            System.out.println(String.join(\" < \", chain) + \" (depth \" + (chain.size() - 1) + \")\");\n"
               "        }",
             "            List<String> chain = new ArrayList<>();\n"
             "            for (Class<?> k = c; k != null; k = k.getSuperclass()) {\n"
             "                chain.add(k.getSimpleName());\n"
             "            }\n"
             "            System.out.println(String.join(\" < \", chain) + \" (depth \" + (chain.size() - 1) + \")\");",
             [_toks36(ts, _nl(*[" < ".join(_chain36(t)) + f" (depth {len(_chain36(t)) - 1})" for t in ts]))
              for ts in _DEPTHS36],
             ["A `for` loop can walk the chain: start at `c`, step with `getSuperclass()`.",
              "The chain includes the class itself and `Object`.",
              "Depth is the chain's length minus one."]),

        _p36("j36-pa-common", "The nearest common ancestor", "Medium",
             "For each pair, print the most specific class that both extend (a class "
             "counts as its own ancestor).",
             _ANIMALS36,
             _ANIMALMAP36
             + "        int n = sc.nextInt();\n"
               "        for (int i = 0; i < n; i++) {\n"
               "            Class<?> a = types.get(sc.next());\n"
               "            Class<?> b = types.get(sc.next());\n"
               "            Class<?> k = b;\n"
               "            while (!k.isAssignableFrom(a)) {\n"
               "                k = k.getSuperclass();\n"
               "            }\n"
               "            System.out.println(a.getSimpleName() + \" & \" + b.getSimpleName() + \" -> \" + k.getSimpleName());\n"
               "        }",
             "            Class<?> k = b;\n"
             "            while (!k.isAssignableFrom(a)) {\n"
             "                k = k.getSuperclass();\n"
             "            }",
             [_rows36(rows, _nl(*[f"{a} & {b} -> {_common36(a, b)}" for (a, b) in rows])) for rows in _PAIRS36],
             ["Walk up from one class until you reach something the other also is.",
              "`k.isAssignableFrom(a)` - could an `a` be stored in a variable of type `k`?",
              "Every chain ends at `Object`, so the loop always stops.",
              "`Dog & Puppy` is `Dog`: a class is assignable from itself."]),

        _p36("j36-pa-assignable", "Direct or inherited?", "Medium",
             "For each `class interface` pair, print whether the class lists the interface "
             "DIRECTLY (`getInterfaces()`), and whether it is one at all "
             "(`isAssignableFrom`).",
             _IFACEH36,
             _IFMAP36
             + "        int n = sc.nextInt();\n"
               "        for (int i = 0; i < n; i++) {\n"
               "            Class<?> c = types.get(sc.next());\n"
               "            Class<?> ifc = types.get(sc.next());\n"
               "            boolean direct = Arrays.asList(c.getInterfaces()).contains(ifc);\n"
               "            boolean is = ifc.isAssignableFrom(c);\n"
               "            System.out.println(c.getSimpleName() + \" \" + ifc.getSimpleName() + \" direct=\" + direct + \" is=\" + is);\n"
               "        }",
             "            boolean direct = Arrays.asList(c.getInterfaces()).contains(ifc);\n"
             "            boolean is = ifc.isAssignableFrom(c);",
             [_rows36(rows, _nl(*[f"{c} {i} direct={_jbool(i in _DIRECT36[c])} is={_jbool(i in _ASSIGN36[c])}"
                                  for (c, i) in rows])) for rows in _IFQ36],
             ["`getInterfaces()` lists only what the class wrote after `implements`.",
              "`Car implements Vehicle`, and `Vehicle extends Movable` - so Car IS a "
              "Movable without listing it.",
              "`Tesla` inherits `Vehicle` through `Car`.",
              "`ifc.isAssignableFrom(c)` is the transitive answer."]),

        _p36("j36-pa-arrays", "Arrays of arrays", "Hard",
             "For each type print `name: D dimensions of BASE` - an array's number of "
             "dimensions and its innermost element type. A non-array has 0 dimensions.",
             "",
             _ARRMAP36
             + "        int n = sc.nextInt();\n"
               "        for (int i = 0; i < n; i++) {\n"
               "            Class<?> c = types.get(sc.next());\n"
               "            String name = c.getSimpleName();\n"
               "            int dims = 0;\n"
               "            while (c.isArray()) {\n"
               "                c = c.getComponentType();\n"
               "                dims++;\n"
               "            }\n"
               "            System.out.println(name + \": \" + dims + \" dimensions of \" + c.getSimpleName());\n"
               "        }",
             "            int dims = 0;\n"
             "            while (c.isArray()) {\n"
             "                c = c.getComponentType();\n"
             "                dims++;\n"
             "            }",
             [_toks36(ts, _nl(*[_arr36(t) for t in ts])) for ts in _ARRS36],
             ["An `int[][]` is an array whose components are `int[]`.",
              "Peel one level per `getComponentType()` until `isArray()` is false.",
              "Count the levels as you go.",
              "Remember the simple name BEFORE peeling."]),
    ],
)


# --- Family B - members --------------------------------------------------------------

_SHAPESB36 = """
class Circle {
    private double radius;

    double area() {
        return 0;
    }

    double perimeter() {
        return 0;
    }
}

class Invoice {
    private String id;
    private int total;
    private boolean paid;
    private static int issued;

    void pay() {
    }
}

class Empty {
}
"""
_MCOUNTS36 = {"Circle": (1, 2), "Invoice": (4, 1), "Empty": (0, 0)}
_MCASES36 = (["Circle"], ["Invoice", "Empty"], ["Empty"], ["Circle", "Invoice"], ["Invoice"])

_BEAN36 = """
class Person {
    private final String name;
    private final int age;
    private final boolean admin;

    Person(String name, int age, boolean admin) {
        this.name = name;
        this.age = age;
        this.admin = admin;
    }

    public String getName() {
        return name;
    }

    public int getAge() {
        return age;
    }

    public boolean isAdmin() {
        return admin;
    }
}
"""
_PROPS36 = (["name", "age"], ["admin"], ["age", "admin", "name"], ["name"], ["admin", "age"])


def _prop36(p, person):
    return f"{p} = {person[p]}"


_CONFIGB36 = """
class Config {
    private String host = "localhost";
    private int port = 80;
    private boolean secure;

    @Override
    public String toString() {
        return (secure ? "https" : "http") + "://" + host + ":" + port;
    }
}
"""
_SETTER36 = (
    "    static void apply(Object target, String name, String text) throws Exception {\n"
    "        Field f = target.getClass().getDeclaredField(name);\n"
    "        f.setAccessible(true);\n"
    "        if (f.getType() == int.class) {\n"
    "            f.setInt(target, Integer.parseInt(text));\n"
    "        } else if (f.getType() == boolean.class) {\n"
    "            f.setBoolean(target, Boolean.parseBoolean(text));\n"
    "        } else {\n"
    "            f.set(target, text);\n"
    "        }\n"
    "    }"
)
_ASSIGNS36 = ([("port", "8080")], [("secure", "true"), ("host", "example.org")], [],
              [("host", "a.b"), ("port", "443"), ("secure", "true")], [("port", "1"), ("port", "2")])


def _config_out36(pairs):
    cfg = {"host": "localhost", "port": "80", "secure": "false"}
    for (k, v) in pairs:
        cfg[k] = v
    return f"{'https' if cfg['secure'] == 'true' else 'http'}://{cfg['host']}:{cfg['port']}"


_POINTB36 = """
class Point {
    private int x;
    private int y;
    private String label;

    Point(int x, int y, String label) {
        this.x = x;
        this.y = y;
        this.label = label;
    }

    void move(int dx) {
        x += dx;
    }

    @Override
    public String toString() {
        return label + "(" + x + ", " + y + ")";
    }
}
"""
_COPY36 = (
    "    static <T> T copy(T source) throws Exception {\n"
    "        @SuppressWarnings(\"unchecked\")\n"
    "        Class<T> type = (Class<T>) source.getClass();\n"
    "        Constructor<T> ctor = type.getDeclaredConstructor(int.class, int.class, String.class);\n"
    "        T target = ctor.newInstance(0, 0, \"\");\n"
    "        for (Field f : type.getDeclaredFields()) {\n"
    "            f.setAccessible(true);\n"
    "            f.set(target, f.get(source));\n"
    "        }\n"
    "        return target;\n"
    "    }"
)
_COPIES36 = ((1, 2, "a", 5), (0, 0, "origin", -3), (7, 7, "p", 0), (-4, 9, "q", 10), (3, 1, "z", 1))

_DIFF36 = """
class Profile {
    private String name;
    private int age;
    private String city;
    private boolean active;

    Profile(String name, int age, String city, boolean active) {
        this.name = name;
        this.age = age;
        this.city = city;
        this.active = active;
    }
}
"""
_DIFFHELP36 = (
    "    static List<String> diff(Object a, Object b) throws IllegalAccessException {\n"
    "        Field[] fields = a.getClass().getDeclaredFields();\n"
    "        Arrays.sort(fields, Comparator.comparing(Field::getName));\n"
    "        List<String> changes = new ArrayList<>();\n"
    "        for (Field f : fields) {\n"
    "            f.setAccessible(true);\n"
    "            Object x = f.get(a);\n"
    "            Object y = f.get(b);\n"
    "            if (!Objects.equals(x, y)) {\n"
    "                changes.add(f.getName() + \": \" + x + \" -> \" + y);\n"
    "            }\n"
    "        }\n"
    "        return changes;\n"
    "    }"
)
_DIFFS36 = ((("ada", 36, "london", "true"), ("ada", 37, "london", "true")),
            (("bo", 7, "oslo", "false"), ("bo", 7, "oslo", "false")),
            (("cy", 20, "rome", "true"), ("cyrus", 21, "paris", "false")),
            (("di", 50, "lima", "false"), ("di", 50, "lima", "true")),
            (("ed", 1, "kyiv", "true"), ("ed", 2, "kyiv", "true")))


def _diff_out36(a, b):
    names = ["active", "age", "city", "name"]
    av = {"name": a[0], "age": a[1], "city": a[2], "active": a[3]}
    bv = {"name": b[0], "age": b[1], "city": b[2], "active": b[3]}
    ch = [f"{n}: {av[n]} -> {bv[n]}" for n in names if str(av[n]) != str(bv[n])]
    return _nl(*ch) if ch else "identical"


_P36_B = _jfam(
    "p36-members", "Fields and methods",
    "Counting, reading by getter name, writing by field type, copying, and diffing.",
    """
```java
Method g = type.getMethod("get" + capitalised);     // JavaBeans getter
f.setInt(obj, 3);  f.setBoolean(obj, true);  f.set(obj, "text");
Constructor<T> c = type.getDeclaredConstructor(int.class, int.class, String.class);
T fresh = c.newInstance(0, 0, "");
if (!Objects.equals(f.get(a), f.get(b))) ...       // a field-by-field diff
```

Every one of these is a building block of a real library: getters by name are
how a template engine reads `${person.name}`; typed setters are how a config
loader fills an object; field copying is how a mapping library clones one; a
field diff is how an audit log records "what changed".
""",
    [
        _p36("j36-pb-count", "Counting members", "Intro",
             "For each class, print how many fields and how many methods it declares. "
             "Counting does not depend on order, so no sort is needed here.",
             _SHAPESB36,
             "        Map<String, Class<?>> types = Map.of(\"Circle\", Circle.class, \"Invoice\", Invoice.class,\n"
             "                \"Empty\", Empty.class);\n"
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            Class<?> c = types.get(sc.next());\n"
             "            System.out.println(c.getSimpleName() + \": \" + c.getDeclaredFields().length\n"
             "                    + \" fields, \" + c.getDeclaredMethods().length + \" methods\");\n"
             "        }",
             "            System.out.println(c.getSimpleName() + \": \" + c.getDeclaredFields().length\n"
             "                    + \" fields, \" + c.getDeclaredMethods().length + \" methods\");",
             [_toks36(ts, _nl(*[f"{t}: {_MCOUNTS36[t][0]} fields, {_MCOUNTS36[t][1]} methods" for t in ts]))
              for ts in _MCASES36],
             ["`getDeclaredFields().length` and `getDeclaredMethods().length`.",
              "Static fields count - they are declared too.",
              "Constructors are not methods; `getDeclaredConstructors()` lists them."]),

        _p36("j36-pb-getter", "Getters by property name", "Easy",
             "Read a person, then print each requested property by calling its JavaBeans "
             "getter reflectively: `getName`, `getAge` - but `isAdmin` for a boolean.",
             _BEAN36,
             "        Person p = new Person(sc.next(), sc.nextInt(), sc.nextBoolean());\n"
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            String prop = sc.next();\n"
             "            String cap = Character.toUpperCase(prop.charAt(0)) + prop.substring(1);\n"
             "            Method getter;\n"
             "            try {\n"
             "                getter = Person.class.getMethod(\"get\" + cap);\n"
             "            } catch (NoSuchMethodException e) {\n"
             "                getter = Person.class.getMethod(\"is\" + cap);\n"
             "            }\n"
             "            System.out.println(prop + \" = \" + getter.invoke(p));\n"
             "        }",
             "            Method getter;\n"
             "            try {\n"
             "                getter = Person.class.getMethod(\"get\" + cap);\n"
             "            } catch (NoSuchMethodException e) {\n"
             "                getter = Person.class.getMethod(\"is\" + cap);\n"
             "            }\n"
             "            System.out.println(prop + \" = \" + getter.invoke(p));",
             [_case(f"ada 36 true\n{len(ps)}\n{' '.join(ps)}",
                    _nl(*[_prop36(q, {'name': 'ada', 'age': 36, 'admin': 'true'}) for q in ps]))
              for ps in _PROPS36],
             ["The getter for `age` is `getAge` - capitalise the first letter.",
              "Booleans conventionally use `is`: `isAdmin`.",
              "Try `get` first and fall back to `is` on `NoSuchMethodException`.",
              "`getter.invoke(p)` - no arguments."]),

        _p36("j36-pb-setters", "Filling an object from text", "Medium",
             "Write `apply(target, name, text)`: find the declared field, open it, and set it "
             "from the text with the right conversion for its type (int, boolean or "
             "String). `main` applies `name=value` settings and prints the config.",
             _CONFIGB36,
             "        Config c = new Config();\n"
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            String[] kv = sc.next().split(\"=\");\n"
             "            apply(c, kv[0], kv[1]);\n"
             "        }\n"
             "        System.out.println(c);",
             _SETTER36,
             [_case(f"{len(ps)}" + ("\n" + " ".join(f"{k}={v}" for (k, v) in ps) if ps else "\n"),
                    _config_out36(ps)) for ps in _ASSIGNS36],
             ["`getDeclaredField(name)` finds one field by name.",
              "The fields are private, so `setAccessible(true)` first.",
              "`f.getType() == int.class` picks the conversion.",
              "`setInt`, `setBoolean` or `set`.",
              "Unset fields keep their initialisers: localhost, 80, false."],
             helpers=_SETTER36),

        _p36("j36-pb-copy", "A reflective copy", "Medium",
             "Write the generic `copy(source)`: create a new instance through the "
             "three-argument constructor, then copy every declared field across. `main` "
             "moves the COPY and prints both, showing they are independent.",
             _POINTB36,
             "        Point original = new Point(sc.nextInt(), sc.nextInt(), sc.next());\n"
             "        Point clone = copy(original);\n"
             "        clone.move(sc.nextInt());\n"
             "        System.out.println(original);\n"
             "        System.out.println(clone);",
             _COPY36,
             [_case(f"{x} {y} {lb} {dx}", _nl(f"{lb}({x}, {y})", f"{lb}({x + dx}, {y})"))
              for (x, y, lb, dx) in _COPIES36],
             ["`getDeclaredConstructor(int.class, int.class, String.class)` finds the "
              "constructor by its parameter types.",
              "`newInstance(0, 0, \"\")` makes a throwaway object to fill in.",
              "Then, for every field: `setAccessible(true)` and `f.set(target, f.get(source))`.",
              "Only the copy moves - the original is untouched.",
              "The cast to `Class<T>` is unchecked, hence the annotation on that one "
              "declaration."],
             helpers=_COPY36),

        _p36("j36-pb-diff", "What changed?", "Hard",
             "Write `diff(a, b)`: for each declared field, sorted by name, report `field: "
             "old -> new` where the two objects differ. `main` prints the changes or "
             "`identical`.",
             _DIFF36,
             "        Profile a = new Profile(sc.next(), sc.nextInt(), sc.next(), sc.nextBoolean());\n"
             "        Profile b = new Profile(sc.next(), sc.nextInt(), sc.next(), sc.nextBoolean());\n"
             "        List<String> changes = diff(a, b);\n"
             "        System.out.println(changes.isEmpty() ? \"identical\" : String.join(\"\\n\", changes));",
             _DIFFHELP36,
             [_case(f"{' '.join(str(x) for x in a)}\n{' '.join(str(x) for x in b)}", _diff_out36(a, b))
              for (a, b) in _DIFFS36],
             ["Sort the fields by name so the report is stable.",
              "`Objects.equals(x, y)` compares boxed values safely.",
              "The report uses the field NAME, not a getter.",
              "This is the core of an audit log or a test library's 'expected vs actual'."],
             helpers=_DIFFHELP36),
    ],
)


# --- Family C - annotations ------------------------------------------------------------

_ENDPOINTS36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Public {
}

class Service {
    @Public
    public void status() {
    }

    public void shutdown() {
    }

    @Public
    public void health() {
    }

    public void reindex() {
    }

    @Public
    public void version() {
    }
}
"""
_PUBLIC36 = ["health", "status", "version"]
_ALLM36 = ["health", "reindex", "shutdown", "status", "version"]
_PQ36 = (["status", "shutdown"], ["reindex"], ["health", "version", "status"], ["shutdown", "reindex"], ["version"])

_ROUTES36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Route {
    String path();

    String method() default "GET";
}

class Handlers {
    @Route(path = "/users")
    public void listUsers() {
    }

    @Route(path = "/users", method = "POST")
    public void createUser() {
    }

    @Route(path = "/health")
    public void health() {
    }

    @Route(path = "/users/id", method = "DELETE")
    public void deleteUser() {
    }
}
"""
_ROUTETAB36 = [("/health", "GET", "health"), ("/users", "GET", "listUsers"),
               ("/users", "POST", "createUser"), ("/users/id", "DELETE", "deleteUser")]
_RQ36 = ([("GET", "/users")], [("POST", "/users"), ("GET", "/health")], [("PUT", "/users")],
         [("DELETE", "/users/id"), ("GET", "/nope")], [("GET", "/users"), ("POST", "/users")])


def _route36(m, p):
    for (path, meth, name) in _ROUTETAB36:
        if path == p and meth == m:
            return f"{m} {p} -> {name}"
    return f"{m} {p} -> 404"


_TABLES36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface Table {
    String value();
}

@Table("app_users")
class User {
}

class Order {
}

@Table("stock")
class Product {
}

class Invoice {
}
"""
_TABLENAMES36 = {"User": "app_users", "Order": "orders", "Product": "stock", "Invoice": "invoices"}
_TQ36 = (["User"], ["Order", "Product"], ["Invoice"], ["Product", "User", "Order"], ["Order"])
_TABLEHELP36 = (
    "    static String tableFor(Class<?> c) {\n"
    "        Table t = c.getAnnotation(Table.class);\n"
    "        return t != null ? t.value() : c.getSimpleName().toLowerCase(Locale.ROOT) + \"s\";\n"
    "    }"
)

_TAGS36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Tags {
    String[] value();
}

class Suite {
    @Tags({"fast", "db"})
    public void a() {
    }

    @Tags("slow")
    public void b() {
    }

    @Tags({"fast"})
    public void c() {
    }

    public void d() {
    }

    @Tags({"db", "slow", "fast"})
    public void e() {
    }
}
"""
_TAGMAP36 = {"a": ["fast", "db"], "b": ["slow"], "c": ["fast"], "d": [], "e": ["db", "slow", "fast"]}
_TAGQ36 = ("fast", "db", "slow", "none", "*")


def _tags_out36(tag):
    if tag == "*":
        counts = {}
        for ts in _TAGMAP36.values():
            for t in ts:
                counts[t] = counts.get(t, 0) + 1
        return "{" + ", ".join(f"{k}={counts[k]}" for k in sorted(counts)) + "}"
    names = sorted(n for (n, ts) in _TAGMAP36.items() if tag in ts)
    return f"{tag}: {_jarr(names)}"


_SEVERITY36 = """
enum Severity {
    LOW, MEDIUM, HIGH
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Check {
    Severity value() default Severity.MEDIUM;
}

class Audit {
    @Check(Severity.HIGH)
    public void passwords() {
    }

    @Check
    public void logs() {
    }

    @Check(Severity.LOW)
    public void spelling() {
    }

    @Check(Severity.HIGH)
    public void backups() {
    }

    @Check
    public void licences() {
    }

    public void helper() {
    }
}
"""
_SEVHELP36 = (
    "    static Map<Severity, List<String>> group(Class<?> type) {\n"
    "        Map<Severity, List<String>> groups = new EnumMap<>(Severity.class);\n"
    "        Method[] methods = type.getDeclaredMethods();\n"
    "        Arrays.sort(methods, Comparator.comparing(Method::getName));\n"
    "        for (Method m : methods) {\n"
    "            Check c = m.getAnnotation(Check.class);\n"
    "            if (c != null) {\n"
    "                groups.computeIfAbsent(c.value(), k -> new ArrayList<>()).add(m.getName());\n"
    "            }\n"
    "        }\n"
    "        return groups;\n"
    "    }"
)
_SEVQ36 = ("ALL", "HIGH", "LOW", "MEDIUM", "ALL")
_SEVMAP36 = {"LOW": ["spelling"], "MEDIUM": ["licences", "logs"], "HIGH": ["backups", "passwords"]}


def _sev_out36(q):
    if q == "ALL":
        return "{" + ", ".join(f"{k}={_jarr(_SEVMAP36[k])}" for k in ("LOW", "MEDIUM", "HIGH")) + "}"
    return f"{q}: {_jarr(_SEVMAP36[q])}"


_P36_C = _jfam(
    "p36-annotations", "Annotations",
    "Markers, several elements with defaults, class-level annotations, array "
    "elements and enum elements.",
    """
```java
@interface Route { String path(); String method() default "GET"; }
@Route(path = "/users", method = "POST")       // several elements: name them all
@interface Tags { String[] value(); }
@Tags({"fast", "db"})   @Tags("slow")          // one-element arrays need no braces
@interface Check { Severity value() default Severity.MEDIUM; }   // an enum element
c.getAnnotation(Table.class)                   // on a CLASS: @Target(ElementType.TYPE)
```

Every annotation here is `@Retention(RetentionPolicy.RUNTIME)` - lesson 36.3's
rule - and every member list is sorted before it is printed.
""",
    [
        _p36("j36-pc-marker", "Which endpoints are public?", "Intro",
             "Print whether each named method of `Service` carries the `@Public` marker.",
             _ENDPOINTS36,
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            String name = sc.next();\n"
             "            Method m = Service.class.getMethod(name);\n"
             "            System.out.println(name + (m.isAnnotationPresent(Public.class) ? \" public\" : \" internal\"));\n"
             "        }",
             "            Method m = Service.class.getMethod(name);\n"
             "            System.out.println(name + (m.isAnnotationPresent(Public.class) ? \" public\" : \" internal\"));",
             [_toks36(ts, _nl(*[f"{t} {'public' if t in _PUBLIC36 else 'internal'}" for t in ts]))
              for ts in _PQ36],
             ["`getMethod(name)` - these methods take no parameters.",
              "`isAnnotationPresent(Public.class)`",
              "A marker annotation carries no data; its presence is the information."]),

        _p36("j36-pc-routes", "A router", "Easy",
             "Build a routing table from the `@Route` annotations - key `METHOD path` - then "
             "dispatch each request to the handler's name, or `404`.",
             _ROUTES36,
             "        Map<String, String> table = new HashMap<>();\n"
             "        for (Method m : Handlers.class.getDeclaredMethods()) {\n"
             "            Route r = m.getAnnotation(Route.class);\n"
             "            if (r != null) {\n"
             "                table.put(r.method() + \" \" + r.path(), m.getName());\n"
             "            }\n"
             "        }\n"
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            String key = sc.next() + \" \" + sc.next();\n"
             "            System.out.println(key + \" -> \" + table.getOrDefault(key, \"404\"));\n"
             "        }",
             "        for (Method m : Handlers.class.getDeclaredMethods()) {\n"
             "            Route r = m.getAnnotation(Route.class);\n"
             "            if (r != null) {\n"
             "                table.put(r.method() + \" \" + r.path(), m.getName());\n"
             "            }\n"
             "        }",
             [_rows36(rows, _nl(*[_route36(m, p) for (m, p) in rows])) for rows in _RQ36],
             ["`r.path()` and `r.method()` read the two elements.",
              "`method` defaults to `GET` where the annotation omits it.",
              "A map lookup makes the order of `getDeclaredMethods` irrelevant.",
              "This is Spring MVC's `@GetMapping` / `@PostMapping`, in miniature."]),

        _p36("j36-pc-table", "Table names from a class annotation", "Medium",
             "Write `tableFor(c)`: the class's `@Table` value if it has one, and otherwise "
             "its simple name, lower-cased, plus `s`.",
             _TABLES36,
             "        Map<String, Class<?>> types = Map.of(\"User\", User.class, \"Order\", Order.class,\n"
             "                \"Product\", Product.class, \"Invoice\", Invoice.class);\n"
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            Class<?> c = types.get(sc.next());\n"
             "            System.out.println(c.getSimpleName() + \" -> \" + tableFor(c));\n"
             "        }",
             _TABLEHELP36,
             [_toks36(ts, _nl(*[f"{t} -> {_TABLENAMES36[t]}" for t in ts])) for ts in _TQ36],
             ["`@Target(ElementType.TYPE)` puts the annotation on a class.",
              "`c.getAnnotation(Table.class)` - null when absent.",
              "The fallback is a convention: `Order` maps to `orders`.",
              "`toLowerCase(Locale.ROOT)` - module 32."],
             helpers=_TABLEHELP36),

        _p36("j36-pc-tags", "Array elements", "Medium",
             "Each method may carry `@Tags` with several tags. Given a tag, print the "
             "methods carrying it, sorted; given `*`, print how many methods carry each tag.",
             _TAGS36,
             "        String tag = sc.next();\n"
             "        Map<String, Integer> counts = new TreeMap<>();\n"
             "        List<String> names = new ArrayList<>();\n"
             "        for (Method m : Suite.class.getDeclaredMethods()) {\n"
             "            Tags t = m.getAnnotation(Tags.class);\n"
             "            if (t == null) {\n"
             "                continue;\n"
             "            }\n"
             "            for (String s : t.value()) {\n"
             "                counts.merge(s, 1, Integer::sum);\n"
             "                if (s.equals(tag)) {\n"
             "                    names.add(m.getName());\n"
             "                }\n"
             "            }\n"
             "        }\n"
             "        Collections.sort(names);\n"
             "        System.out.println(tag.equals(\"*\") ? counts.toString() : tag + \": \" + names);",
             "            for (String s : t.value()) {\n"
             "                counts.merge(s, 1, Integer::sum);\n"
             "                if (s.equals(tag)) {\n"
             "                    names.add(m.getName());\n"
             "                }\n"
             "            }",
             [_case(t, _tags_out36(t)) for t in _TAGQ36],
             ["An array element comes back as an array: `String[] value()`.",
              "Loop over `t.value()`.",
              "`@Tags(\"slow\")` is shorthand for a one-element array.",
              "Sort the names - the method order is unspecified."]),

        _p36("j36-pc-enum", "Enum elements, grouped", "Hard",
             "Write `group(type)`: every `@Check` method, grouped by its `Severity` (default "
             "MEDIUM) in an `EnumMap`, with names in alphabetical order. `main` prints one "
             "group, or all of them.",
             _SEVERITY36,
             "        Map<Severity, List<String>> groups = group(Audit.class);\n"
             "        String q = sc.next();\n"
             "        System.out.println(q.equals(\"ALL\") ? groups.toString()\n"
             "                : q + \": \" + groups.getOrDefault(Severity.valueOf(q), List.of()));",
             _SEVHELP36,
             [_case(q, _sev_out36(q)) for q in _SEVQ36],
             ["Sort the methods by name FIRST, so each group's list comes out sorted.",
              "`c.value()` is a `Severity` constant.",
              "`computeIfAbsent(severity, k -> new ArrayList<>()).add(name)`.",
              "The `EnumMap` prints LOW, MEDIUM, HIGH - declaration order, module 33."],
             helpers=_SEVHELP36),
    ],
)


# --- Family D - frameworks --------------------------------------------------------------

_BEFORE36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Test {
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface BeforeEach {
}

class CartTests {
    static int price;
    private List<Integer> cart;

    @BeforeEach
    void setUp() {
        cart = new ArrayList<>();
        cart.add(price);
    }

    @Test
    void addsSecondItem() {
        cart.add(price);
        if (cart.size() != 2) {
            throw new AssertionError("size " + cart.size());
        }
    }

    @Test
    void startsWithOneItem() {
        if (cart.size() != 1) {
            throw new AssertionError("size " + cart.size());
        }
    }

    @Test
    void priceIsPositive() {
        if (cart.get(0) <= 0) {
            throw new AssertionError("price " + cart.get(0));
        }
    }
}
"""
_BEFORERUN36 = (
    "    static void run(Class<?> type) throws Exception {\n"
    "        Method[] methods = type.getDeclaredMethods();\n"
    "        Arrays.sort(methods, Comparator.comparing(Method::getName));\n"
    "        Method before = null;\n"
    "        for (Method m : methods) {\n"
    "            if (m.isAnnotationPresent(BeforeEach.class)) {\n"
    "                before = m;\n"
    "            }\n"
    "        }\n"
    "        for (Method m : methods) {\n"
    "            if (!m.isAnnotationPresent(Test.class)) {\n"
    "                continue;\n"
    "            }\n"
    "            Object instance = type.getDeclaredConstructor().newInstance();\n"
    "            try {\n"
    "                if (before != null) {\n"
    "                    before.invoke(instance);\n"
    "                }\n"
    "                m.invoke(instance);\n"
    "                System.out.println(\"PASS \" + m.getName());\n"
    "            } catch (InvocationTargetException e) {\n"
    "                System.out.println(\"FAIL \" + m.getName() + \": \" + e.getCause().getMessage());\n"
    "            }\n"
    "        }\n"
    "    }"
)
_PRICES36 = (5, 0, 12, -3, 1)


def _before_out36(p):
    return _nl("PASS addsSecondItem",
               "PASS priceIsPositive" if p > 0 else f"FAIL priceIsPositive: price {p}",
               "PASS startsWithOneItem")


_ORDERED36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Step {
    int value();
}

class Pipeline {
    static List<String> log = new ArrayList<>();

    @Step(3)
    public void publish() {
        log.add("publish");
    }

    @Step(1)
    public void compile() {
        log.add("compile");
    }

    @Step(2)
    public void test() {
        log.add("test");
    }

    @Step(2)
    public void lint() {
        log.add("lint");
    }

    public void clean() {
        log.add("clean");
    }
}
"""
_STEPS36 = [("compile", 1), ("lint", 2), ("test", 2), ("publish", 3)]
_UPTO36 = (3, 1, 2, 0, 9)


def _steps_out36(k):
    ran = [n for (n, s) in _STEPS36 if s <= k]
    return _nl(f"ran {len(ran)} steps", _jarr(ran))


_DI36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Inject {
}

interface Greeter {
    String greet(String name);
}

interface Audit {
    void record(String event);
}

class FriendlyGreeter implements Greeter {
    public String greet(String name) {
        return "hi " + name;
    }
}

class PrintAudit implements Audit {
    public void record(String event) {
        System.out.println("audit: " + event);
    }
}

class WelcomeService {
    @Inject
    private Greeter greeter;

    @Inject
    private Audit audit;

    private int served;

    void welcome(String name) {
        served++;
        audit.record("welcome #" + served);
        System.out.println(greeter.greet(name));
    }
}
"""
_INJECTHELP36 = (
    "    static <T> T create(Class<T> type, Map<Class<?>, Object> registry) throws Exception {\n"
    "        T obj = type.getDeclaredConstructor().newInstance();\n"
    "        for (Field f : type.getDeclaredFields()) {\n"
    "            if (f.isAnnotationPresent(Inject.class)) {\n"
    "                Object dependency = registry.get(f.getType());\n"
    "                if (dependency == null) {\n"
    "                    throw new IllegalStateException(\"no \" + f.getType().getSimpleName());\n"
    "                }\n"
    "                f.setAccessible(true);\n"
    "                f.set(obj, dependency);\n"
    "            }\n"
    "        }\n"
    "        return obj;\n"
    "    }"
)
_WELCOMES36 = (["ada"], ["bo", "cy"], ["solo"], ["x", "y", "z"], ["pear", "fig"])


def _welcome_out36(names):
    out = []
    for i, n in enumerate(names, start=1):
        out.append(f"audit: welcome #{i}")
        out.append(f"hi {n}")
    return _nl(*out)


_CSV36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface Column {
    int order();

    String name() default "";
}

class Sale {
    @Column(order = 2, name = "qty")
    private int quantity;

    @Column(order = 1)
    private String item;

    private String internalNote = "secret";

    @Column(order = 3, name = "unit_price")
    private int price;

    Sale(String item, int quantity, int price) {
        this.item = item;
        this.quantity = quantity;
        this.price = price;
    }
}
"""
_CSVHELP36 = (
    "    static List<Field> columns(Class<?> type) {\n"
    "        List<Field> cols = new ArrayList<>();\n"
    "        for (Field f : type.getDeclaredFields()) {\n"
    "            if (f.isAnnotationPresent(Column.class)) {\n"
    "                f.setAccessible(true);\n"
    "                cols.add(f);\n"
    "            }\n"
    "        }\n"
    "        cols.sort(Comparator.comparingInt(f -> f.getAnnotation(Column.class).order()));\n"
    "        return cols;\n"
    "    }\n"
    "\n"
    "    static String header(List<Field> cols) {\n"
    "        List<String> names = new ArrayList<>();\n"
    "        for (Field f : cols) {\n"
    "            String n = f.getAnnotation(Column.class).name();\n"
    "            names.add(n.isEmpty() ? f.getName() : n);\n"
    "        }\n"
    "        return String.join(\",\", names);\n"
    "    }\n"
    "\n"
    "    static String row(Object o, List<Field> cols) throws IllegalAccessException {\n"
    "        List<String> values = new ArrayList<>();\n"
    "        for (Field f : cols) {\n"
    "            values.add(String.valueOf(f.get(o)));\n"
    "        }\n"
    "        return String.join(\",\", values);\n"
    "    }"
)
_SALES36 = ([("tea", 2, 350)], [("pen", 10, 99), ("ink", 1, 500)], [("x", 0, 0)],
            [("a", 1, 1), ("b", 2, 2), ("c", 3, 3)], [("cake", 7, 425)])

_SUBS36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Subscribe {
}

class Mailer {
    @Subscribe
    public void onSignup(String user) {
        System.out.println("mail: welcome " + user);
    }

    public void notAHandler(String user) {
        System.out.println("never");
    }
}

class Stats {
    int count;

    @Subscribe
    public void count(String user) {
        count++;
        System.out.println("stats: " + count + " signups");
    }

    @Subscribe
    public void audit(String user) {
        System.out.println("stats: audit " + user);
    }
}
"""
_BUSHELP36 = (
    "    static List<Object[]> handlers = new ArrayList<>();\n"
    "\n"
    "    static void register(Object listener) {\n"
    "        Method[] methods = listener.getClass().getDeclaredMethods();\n"
    "        Arrays.sort(methods, Comparator.comparing(Method::getName));\n"
    "        for (Method m : methods) {\n"
    "            if (m.isAnnotationPresent(Subscribe.class) && m.getParameterCount() == 1\n"
    "                    && m.getParameterTypes()[0] == String.class) {\n"
    "                handlers.add(new Object[] {listener, m});\n"
    "            }\n"
    "        }\n"
    "    }\n"
    "\n"
    "    static void post(String event) throws Exception {\n"
    "        for (Object[] h : handlers) {\n"
    "            ((Method) h[1]).invoke(h[0], event);\n"
    "        }\n"
    "    }"
)
_POSTS36 = (["ada"], ["bo", "cy"], ["solo"], ["x", "y", "z"], ["pear"])


def _posts_out36(users):
    out = []
    for i, u in enumerate(users, start=1):
        out.append(f"mail: welcome {u}")
        out.append(f"stats: audit {u}")
        out.append(f"stats: {i} signups")
    return _nl(*out)


_P36_D = _jfam(
    "p36-frameworks", "Frameworks in miniature",
    "Setup methods, ordered steps, dependency injection, CSV mapping and an "
    "annotation-driven event bus.",
    """
Each drill is a real framework feature, reduced to its reflective core:

| drill | the real thing |
|---|---|
| `@BeforeEach` | JUnit 5 |
| `@Step(n)` ordering | JUnit's `@Order`, build-tool task graphs |
| `@Inject` fields | Spring, Guice, Jakarta CDI |
| `@Column` mapping | JPA, CSV and JSON mappers |
| `@Subscribe` methods | Guava's EventBus |

The shape never changes: scan the members, read the annotations, act - and sort
whenever order reaches the output.
""",
    [
        _p36("j36-pd-before", "`@BeforeEach`", "Medium",
             "Write `run(type)`: find the `@BeforeEach` method, then for each `@Test` (in "
             "name order) make a fresh instance, run the setup on it, then the test.",
             _BEFORE36,
             "        CartTests.price = sc.nextInt();\n"
             "        run(CartTests.class);",
             _BEFORERUN36,
             [_case(str(p), _before_out36(p)) for p in _PRICES36],
             ["Find the setup method once, before the loop.",
              "Setup and test must run on the SAME fresh instance.",
              "Both invocations sit inside the one `try`: a failing setup fails its test.",
              "Without the setup, `cart` would be null and every test would error."],
             helpers=_BEFORERUN36),

        _p36("j36-pd-steps", "Ordered steps", "Easy",
             "Run every `@Step` method whose number is at most `k`, in step order and then "
             "by name, and print what ran.",
             _ORDERED36,
             "        int k = sc.nextInt();\n"
             "        Pipeline p = new Pipeline();\n"
             "        List<Method> steps = new ArrayList<>();\n"
             "        for (Method m : Pipeline.class.getDeclaredMethods()) {\n"
             "            Step s = m.getAnnotation(Step.class);\n"
             "            if (s != null && s.value() <= k) {\n"
             "                steps.add(m);\n"
             "            }\n"
             "        }\n"
             "        steps.sort(Comparator.comparingInt((Method m) -> m.getAnnotation(Step.class).value())\n"
             "                .thenComparing(Method::getName));\n"
             "        for (Method m : steps) {\n"
             "            m.invoke(p);\n"
             "        }\n"
             "        System.out.println(\"ran \" + Pipeline.log.size() + \" steps\");\n"
             "        System.out.println(Pipeline.log);",
             "        steps.sort(Comparator.comparingInt((Method m) -> m.getAnnotation(Step.class).value())\n"
             "                .thenComparing(Method::getName));",
             [_case(str(k), _steps_out36(k)) for k in _UPTO36],
             ["Sort by the annotation's number, then by name for steps that share one.",
              "`Comparator.comparingInt(m -> m.getAnnotation(Step.class).value())`",
              "The lambda needs its parameter typed as `(Method m)` for `thenComparing` "
              "to infer.",
              "`lint` and `test` are both step 2: alphabetical order decides."]),

        _p36("j36-pd-inject", "Dependency injection", "Medium",
             "Write `create(type, registry)`: construct the object, then fill every "
             "`@Inject` field with the registry's object for that field's type (throwing "
             "`IllegalStateException` if there is none).",
             _DI36,
             "        Map<Class<?>, Object> registry = new HashMap<>();\n"
             "        registry.put(Greeter.class, new FriendlyGreeter());\n"
             "        registry.put(Audit.class, new PrintAudit());\n"
             "        WelcomeService service = create(WelcomeService.class, registry);\n"
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            service.welcome(sc.next());\n"
             "        }",
             _INJECTHELP36,
             [_toks36(ns, _welcome_out36(ns)) for ns in _WELCOMES36],
             ["`type.getDeclaredConstructor().newInstance()` builds the object.",
              "For each `@Inject` field, look up `registry.get(f.getType())`.",
              "The fields are private: `setAccessible(true)` then `f.set(obj, dep)`.",
              "`served` has no `@Inject`, so it is left alone.",
              "This is module 35's constructor injection, done by a container instead of "
              "by hand."],
             helpers=_INJECTHELP36),

        _p36("j36-pd-csv", "Objects to CSV", "Medium",
             "Write `columns`, `header` and `row`: the `@Column` fields in `order`, the "
             "header using each column's `name` (or the field name when it is empty), and "
             "one row of values.",
             _CSV36,
             "        List<Field> cols = columns(Sale.class);\n"
             "        System.out.println(header(cols));\n"
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            System.out.println(row(new Sale(sc.next(), sc.nextInt(), sc.nextInt()), cols));\n"
             "        }",
             _CSVHELP36,
             [_rows36(rows, _nl("item,qty,unit_price", *[f"{a},{b},{c}" for (a, b, c) in rows]))
              for rows in _SALES36],
             ["Only fields with `@Column` become columns - `internalNote` stays private.",
              "Sort the columns by the annotation's `order()`, not by field name.",
              "An empty `name()` means 'use the field name'.",
              "`String.valueOf(f.get(o))` for each value."],
             helpers=_CSVHELP36),

        _p36("j36-pd-bus", "An annotation-driven event bus", "Hard",
             "Write `register` and `post`: `register(listener)` records every `@Subscribe` "
             "method taking one `String` (in name order); `post(event)` invokes every "
             "recorded method, in registration order.",
             _SUBS36,
             "        register(new Mailer());\n"
             "        register(new Stats());\n"
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            post(sc.next());\n"
             "        }",
             _BUSHELP36,
             [_toks36(us, _posts_out36(us)) for us in _POSTS36],
             ["Store pairs of (listener object, Method) - an `Object[]` of two is enough.",
              "Check the annotation AND the signature: one parameter, of type String.",
              "`m.getParameterTypes()[0] == String.class`",
              "Sorting within each listener makes `audit` run before `count`.",
              "This is Guava's EventBus: no listener interface at all, just annotated "
              "methods."],
             helpers=_BUSHELP36),
    ],
)


# --- Family E - proxies ----------------------------------------------------------------

_LISTOPS36 = ([("add", "a"), ("add", "b"), ("size",)], [("size",)], [("add", "x"), ("get", "0")],
              [("add", "p"), ("add", "q"), ("get", "1"), ("size",)], [("add", "z")])


def _listops_out36(ops):
    items, out = [], []
    for op in ops:
        if op[0] == "add":
            out.append(f"-> add[{op[1]}]")
            items.append(op[1])
            out.append("true")
        elif op[0] == "size":
            out.append("-> size")
            out.append(str(len(items)))
        else:
            out.append(f"-> get[{op[1]}]")
            out.append(items[int(op[1])])
    out.append(f"-> toString")
    out.append(_jarr(items))
    return _nl(*out)


def _listops_case36(ops):
    return _case("\n".join([str(len(ops))] + [" ".join(op) for op in ops]), _listops_out36(ops))


_ACCOUNT36 = """
interface Account {
    int balance();

    void deposit(int amount);

    String owner();
}

class BasicAccount implements Account {
    private int balance;

    public int balance() {
        return balance;
    }

    public void deposit(int amount) {
        balance += amount;
    }

    public String owner() {
        return "ada";
    }
}
"""
_RO36 = (
    "    static Account readOnly(Account target) {\n"
    "        return (Account) Proxy.newProxyInstance(\n"
    "                Account.class.getClassLoader(),\n"
    "                new Class<?>[] {Account.class},\n"
    "                (proxy, method, margs) -> {\n"
    "                    if (method.getReturnType() == void.class) {\n"
    "                        throw new UnsupportedOperationException(method.getName());\n"
    "                    }\n"
    "                    return method.invoke(target, margs);\n"
    "                });\n"
    "    }"
)
_ROOPS36 = ([("deposit", 5), ("balance",)], [("owner",)], [("balance",), ("deposit", 1), ("deposit", 2)],
            [("deposit", 100), ("owner",), ("balance",)], [("balance",)])


def _ro_out36(ops):
    out = []
    for op in ops:
        if op[0] == "deposit":
            out.append("refused: deposit")
        elif op[0] == "balance":
            out.append("balance = 10")
        else:
            out.append("owner = ada")
    return _nl(*out)


_CFGI36 = """
interface ServerConfig {
    String host();

    int port();

    boolean secure();
}
"""
_CFGHELP36 = (
    "    static ServerConfig configFrom(Map<String, String> values) {\n"
    "        return (ServerConfig) Proxy.newProxyInstance(\n"
    "                ServerConfig.class.getClassLoader(),\n"
    "                new Class<?>[] {ServerConfig.class},\n"
    "                (proxy, method, margs) -> {\n"
    "                    String text = values.get(method.getName());\n"
    "                    if (text == null) {\n"
    "                        throw new IllegalStateException(\"missing \" + method.getName());\n"
    "                    }\n"
    "                    Class<?> t = method.getReturnType();\n"
    "                    if (t == int.class) {\n"
    "                        return Integer.parseInt(text);\n"
    "                    }\n"
    "                    if (t == boolean.class) {\n"
    "                        return Boolean.parseBoolean(text);\n"
    "                    }\n"
    "                    return text;\n"
    "                });\n"
    "    }"
)
_CFGS36 = ([("host", "a.io"), ("port", "8080"), ("secure", "true")],
           [("host", "localhost"), ("port", "80"), ("secure", "false")],
           [("port", "443"), ("host", "b.org"), ("secure", "true")],
           [("host", "x"), ("secure", "false")],
           [("secure", "true"), ("port", "1"), ("host", "h")])


def _cfg_out36(pairs):
    d = dict(pairs)
    for key in ("secure", "host", "port"):   # the order main calls them in
        if key not in d:
            return f"error: missing {key}"
    return f"{'https' if d['secure'] == 'true' else 'http'}://{d['host']}:{d['port']}"


_FLAKY36 = """
interface Fetcher {
    String fetch(String url);
}

class FlakyFetcher implements Fetcher {
    private int failuresLeft;
    int attempts;

    FlakyFetcher(int failures) {
        this.failuresLeft = failures;
    }

    public String fetch(String url) {
        attempts++;
        if (failuresLeft > 0) {
            failuresLeft--;
            throw new IllegalStateException("timeout");
        }
        return "<" + url + ">";
    }
}
"""
_RETRYHELP36 = (
    "    static Fetcher retrying(Fetcher target, int maxAttempts) {\n"
    "        return (Fetcher) Proxy.newProxyInstance(\n"
    "                Fetcher.class.getClassLoader(),\n"
    "                new Class<?>[] {Fetcher.class},\n"
    "                (proxy, method, margs) -> {\n"
    "                    for (int attempt = 1; ; attempt++) {\n"
    "                        try {\n"
    "                            return method.invoke(target, margs);\n"
    "                        } catch (InvocationTargetException e) {\n"
    "                            if (!(e.getCause() instanceof IllegalStateException) || attempt == maxAttempts) {\n"
    "                                throw e.getCause();\n"
    "                            }\n"
    "                        }\n"
    "                    }\n"
    "                });\n"
    "    }"
)
_RETRIES36 = ((0, 3), (2, 3), (3, 3), (5, 2), (1, 1))


def _retry_out36(fails, maxa):
    if fails < maxa:
        return _nl("<site>", f"attempts {fails + 1}")
    return _nl("gave up: timeout", f"attempts {maxa}")


_NONNULL36 = """
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.PARAMETER)
@interface NonNull {
}

interface Directory {
    String lookup(@NonNull String name, String fallback);
}

class MapDirectory implements Directory {
    private final Map<String, String> entries = Map.of("ada", "room 1", "bo", "room 2");

    public String lookup(String name, String fallback) {
        return entries.getOrDefault(name, fallback == null ? "unknown" : fallback);
    }
}
"""
_NNHELP36 = (
    "    static Directory checked(Directory target) {\n"
    "        return (Directory) Proxy.newProxyInstance(\n"
    "                Directory.class.getClassLoader(),\n"
    "                new Class<?>[] {Directory.class},\n"
    "                (proxy, method, margs) -> {\n"
    "                    Annotation[][] params = method.getParameterAnnotations();\n"
    "                    for (int i = 0; i < params.length; i++) {\n"
    "                        for (Annotation a : params[i]) {\n"
    "                            if (a instanceof NonNull && margs[i] == null) {\n"
    "                                throw new IllegalArgumentException(\n"
    "                                        \"argument \" + i + \" of \" + method.getName() + \" is null\");\n"
    "                            }\n"
    "                        }\n"
    "                    }\n"
    "                    return method.invoke(target, margs);\n"
    "                });\n"
    "    }"
)
_NNQ36 = ([("ada", "-")], [("-", "x")], [("zed", "desk"), ("bo", "-")], [("-", "-")],
          [("ada", "x"), ("nobody", "-"), ("-", "y")])


def _nn_out36(rows):
    rooms = {"ada": "room 1", "bo": "room 2"}
    out = []
    for (n, f) in rows:
        if n == "-":
            out.append("rejected: argument 0 of lookup is null")
        else:
            out.append(rooms.get(n, "unknown" if f == "-" else f))
    return _nl(*out)


_P36_E = _jfam(
    "p36-proxies", "Dynamic proxies",
    "Tracing, read-only views, interfaces with no implementation, retries, and "
    "argument checks - each in one InvocationHandler.",
    """
```java
(proxy, method, args) -> {
    // before: log, check, count, look up a cache...
    Object result = method.invoke(target, args);   // or never call it at all
    // after: record, convert, retry...
    return result;
}
```

Two things proxies do that a hand-written decorator cannot. They work for *any*
interface, including ones with dozens of methods. And they need no target at
all: a handler can answer every call itself - which is how a configuration
interface, a Spring Data repository or a Retrofit HTTP client can be "just an
interface".

The handler also sees `toString`, `equals` and `hashCode` calls made on the
proxy - the first family drill prints one.
""",
    [
        _p36("j36-pe-trace", "Tracing a List", "Intro",
             "Wrap an `ArrayList` in a `List` proxy that prints `-> method[args]` (or just "
             "`-> method` with no arguments) before every call. Printing the list itself "
             "goes through the proxy too.",
             "",
             "        List<String> real = new ArrayList<>();\n"
             "        @SuppressWarnings(\"unchecked\")\n"
             "        List<String> list = (List<String>) Proxy.newProxyInstance(\n"
             "                Main.class.getClassLoader(),\n"
             "                new Class<?>[] {List.class},\n"
             "                (proxy, method, margs) -> {\n"
             "                    System.out.println(\"-> \" + method.getName()\n"
             "                            + (margs == null ? \"\" : Arrays.toString(margs)));\n"
             "                    return method.invoke(real, margs);\n"
             "                });\n"
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            switch (sc.next()) {\n"
             "                case \"add\" -> System.out.println(list.add(sc.next()));\n"
             "                case \"get\" -> System.out.println(list.get(sc.nextInt()));\n"
             "                default -> System.out.println(list.size());\n"
             "            }\n"
             "        }\n"
             "        String shown = list.toString();\n"
             "        System.out.println(shown);",
             "                (proxy, method, margs) -> {\n"
             "                    System.out.println(\"-> \" + method.getName()\n"
             "                            + (margs == null ? \"\" : Arrays.toString(margs)));\n"
             "                    return method.invoke(real, margs);\n"
             "                });",
             [_listops_case36(ops) for ops in _LISTOPS36],
             ["For a method with no parameters, `margs` is null - not an empty array.",
              "`Arrays.toString(margs)` shows the arguments as `[a]`.",
              "`list.toString()` is a call on the proxy, so it is traced as well.",
              "Store the result of `toString()` first, so the trace line prints before "
              "the list."]),

        _p36("j36-pe-readonly", "A read-only view", "Easy",
             "Write `readOnly(target)`: a proxy that refuses every method returning `void` "
             "(the mutators, here) with `UnsupportedOperationException(methodName)`, and "
             "passes the rest through.",
             _ACCOUNT36,
             "        BasicAccount real = new BasicAccount();\n"
             "        real.deposit(10);\n"
             "        Account view = readOnly(real);\n"
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            String op = sc.next();\n"
             "            try {\n"
             "                switch (op) {\n"
             "                    case \"deposit\" -> view.deposit(sc.nextInt());\n"
             "                    case \"balance\" -> System.out.println(\"balance = \" + view.balance());\n"
             "                    default -> System.out.println(\"owner = \" + view.owner());\n"
             "                }\n"
             "            } catch (UnsupportedOperationException e) {\n"
             "                System.out.println(\"refused: \" + e.getMessage());\n"
             "            }\n"
             "        }",
             _RO36,
             [_rows36(ops, _ro_out36(ops)) for ops in _ROOPS36],
             ["`method.getReturnType() == void.class` identifies the mutators here.",
              "Throw before calling the target, so nothing changes.",
              "An unchecked exception thrown by the handler reaches the caller as itself.",
              "This is `Collections.unmodifiableList`'s idea, for any interface."],
             helpers=_RO36),

        _p36("j36-pe-config", "An interface with no implementation", "Medium",
             "Write `configFrom(values)`: a `ServerConfig` whose every method answers from "
             "the map, by method name, converted to the method's return type - and throws "
             "`IllegalStateException(\"missing name\")` for an absent key.",
             _CFGI36,
             "        Map<String, String> values = new HashMap<>();\n"
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            values.put(sc.next(), sc.next());\n"
             "        }\n"
             "        ServerConfig cfg = configFrom(values);\n"
             "        try {\n"
             "            String url = (cfg.secure() ? \"https\" : \"http\") + \"://\" + cfg.host() + \":\" + cfg.port();\n"
             "            System.out.println(url);\n"
             "        } catch (IllegalStateException e) {\n"
             "            System.out.println(\"error: \" + e.getMessage());\n"
             "        }",
             _CFGHELP36,
             [_rows36(p, _cfg_out36(p)) for p in _CFGS36],
             ["There is no target object - the handler answers every call itself.",
              "`method.getName()` is the key; `method.getReturnType()` decides the "
              "conversion.",
              "Return a boxed `Integer` for an `int` method - the proxy unboxes it.",
              "`secure()` is called first in `main`, then `host()`, then `port()`."],
             helpers=_CFGHELP36),

        _p36("j36-pe-retry", "Retrying", "Medium",
             "Write `retrying(target, maxAttempts)`: a proxy that re-invokes a call that "
             "failed with `IllegalStateException`, up to `maxAttempts` attempts in total, "
             "then rethrows the real exception.",
             _FLAKY36,
             "        FlakyFetcher real = new FlakyFetcher(sc.nextInt());\n"
             "        Fetcher f = retrying(real, sc.nextInt());\n"
             "        try {\n"
             "            System.out.println(f.fetch(\"site\"));\n"
             "        } catch (IllegalStateException e) {\n"
             "            System.out.println(\"gave up: \" + e.getMessage());\n"
             "        }\n"
             "        System.out.println(\"attempts \" + real.attempts);",
             _RETRYHELP36,
             [_case(f"{a} {b}", _retry_out36(a, b)) for (a, b) in _RETRIES36],
             ["Loop, invoking the target each time.",
              "A failure arrives as `InvocationTargetException`; look at `getCause()`.",
              "Rethrow `e.getCause()` itself - an InvocationHandler may throw any "
              "Throwable, and the caller then sees the original exception.",
              "Only retry the exception you expect; anything else should fail at once."],
             helpers=_RETRYHELP36),

        _p36("j36-pe-nonnull", "Checking annotated parameters", "Hard",
             "Write `checked(target)`: before passing a call on, reject any argument whose "
             "PARAMETER is annotated `@NonNull` but is null, with "
             "`IllegalArgumentException(\"argument i of method is null\")`.",
             _NONNULL36,
             "        Directory dir = checked(new MapDirectory());\n"
             "        int n = sc.nextInt();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            String name = sc.next();\n"
             "            String fallback = sc.next();\n"
             "            try {\n"
             "                System.out.println(dir.lookup(name.equals(\"-\") ? null : name,\n"
             "                        fallback.equals(\"-\") ? null : fallback));\n"
             "            } catch (IllegalArgumentException e) {\n"
             "                System.out.println(\"rejected: \" + e.getMessage());\n"
             "            }\n"
             "        }",
             _NNHELP36,
             [_rows36(rows, _nn_out36(rows)) for rows in _NNQ36],
             ["`method.getParameterAnnotations()` is an array per parameter, in parameter "
              "order.",
              "`a instanceof NonNull` recognises the annotation.",
              "Only parameter 0 is `@NonNull`; a null fallback is allowed.",
              "`@Target(ElementType.PARAMETER)` puts the annotation on a parameter.",
              "Bean Validation's method validation works exactly like this."],
             helpers=_NNHELP36),
    ],
)


_PRACTICE[36] = [_P36_A, _P36_B, _P36_C, _P36_D, _P36_E]
