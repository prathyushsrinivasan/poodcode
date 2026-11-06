"""Execute examples and cases; audit the no-surprise-syntax prerequisite contract."""
import contextlib
import copy
import io
import json
import subprocess
import sys

from python_course import ROOT, authored_course, syntax_features


def main():
    modules = authored_course()
    actual = json.loads((ROOT / "src/data/python/course.json").read_text(encoding="utf-8"))
    assert actual == modules, "Generated course is stale: run python tools/python_course.py"
    known = set()
    ids = set()
    cases = 0
    preserved = {"squares", "islands", "kth-largest", "last-stone", "merge"}
    for module in modules:
        known |= syntax_features(module["example"])
        result = subprocess.run([sys.executable, "-c", module["example"]], capture_output=True, text=True, timeout=5)
        assert result.returncode == 0, (module["id"], result.stderr)
        for exercise in module["exercises"]:
            assert exercise["id"] not in ids
            ids.add(exercise["id"])
            assert syntax_features(exercise["solution"]) <= known
            assert syntax_features(exercise["starter"]) <= known
            starter_failed = False
            for test in exercise["tests"]:
                for source, starter in [(exercise["solution"], False), (exercise["starter"], True)]:
                    env = {}
                    try:
                        with contextlib.redirect_stdout(io.StringIO()):
                            exec(source, env)
                            exec(test["setup"], env)
                            # Evaluate the published call's args once, so we can
                            # verify the input objects themselves were preserved.
                            args_text = test["call"][len("solve("):-1]
                            args = eval("(" + args_text + ",)", env)
                            before = copy.deepcopy(args)
                            answer = env["solve"](*args)
                        matches = repr(answer) == test["expected"]
                        if not starter:
                            assert matches, (exercise["id"], test["name"], answer, test["expected"])
                            if exercise["id"].split(":")[1] in preserved:
                                assert args == before, (exercise["id"], "mutated input")
                        else:
                            starter_failed |= not matches
                    except Exception:
                        if starter:
                            starter_failed = True
                        else:
                            raise
                cases += 1
            assert starter_failed, (exercise["id"], "starter incorrectly passes every case")
    print(f"Verified {len(modules)} runnable examples, {len(ids)} solutions, {cases} cases, all starters fail, syntax prerequisites and input preservation.")


if __name__ == "__main__":
    main()
