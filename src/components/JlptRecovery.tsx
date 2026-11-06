import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { recoveredCourses } from "../lib/jlptSessionRecovery";

export default function JlptRecovery({ showCourses = false }: { showCourses?: boolean }) {
  const [error, setError] = useState("");
  const [courses] = useState(() => { try { return showCourses ? recoveredCourses(localStorage) : []; } catch { return []; } });
  useEffect(() => { const failed = (event: Event) => setError((event as CustomEvent<string>).detail || "Draft recovery could not be saved. Keep this page open until your answers are submitted."); window.addEventListener("jlpt-recovery-error", failed); return () => window.removeEventListener("jlpt-recovery-error", failed); }, []);
  return <>{error && <p role="alert">{error}</p>}{courses.length > 0 && <details className="card"><summary>Continue saved course practice · {courses.length}</summary><div className="n2-actions">{courses.map((c) => <Link key={c.route} to={c.route}>Continue {c.label} →</Link>)}</div></details>}</>;
}
