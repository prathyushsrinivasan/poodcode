/**
 * Pages for a second window (UI_ROADMAP J4): a lesson, a problem's statement,
 * or its editorial, with none of the app's chrome — no sidebar, no top bar —
 * because the window exists to sit beside the editor and hold one thing.
 */

import { useEffect, useState } from "react";
import { Route, Routes, useParams } from "react-router-dom";
import { api } from "../api";
import type { Concept, Problem } from "../types";
import { Markdown } from "../components/Markdown";
import { LessonMarkdown } from "../components/LessonMarkdown";
import { DiffBadge } from "../components/common";
import { ErrorState, Icon } from "../components/ui";
import { loadConcepts } from "./learn/learnData";

export default function Popout() {
  return (
    <main className="popout" id="main">
      <Routes>
        <Route path="/popout/lesson/:key" element={<PopoutLesson />} />
        <Route path="/popout/problem/:id" element={<PopoutProblem view="statement" />} />
        <Route path="/popout/editorial/:id" element={<PopoutProblem view="editorial" />} />
        <Route path="*" element={<ErrorState title="Nothing to show in this window." />} />
      </Routes>
    </main>
  );
}

function useTitle(title: string | undefined) {
  useEffect(() => {
    if (title) document.title = `${title} — Poodcode`;
  }, [title]);
}

function PopoutLesson() {
  const { key } = useParams();
  const [concept, setConcept] = useState<Concept | null | undefined>(undefined);
  const [error, setError] = useState("");
  useEffect(() => {
    loadConcepts()
      .then((cs) => setConcept(cs.find((c) => c.key === key) ?? null))
      .catch((e) => setError(String(e)));
  }, [key]);
  useTitle(concept?.name);

  if (error) return <ErrorState title="The lesson could not be loaded." error={error} />;
  if (concept === undefined) return <p className="faint">Loading…</p>;
  if (concept === null) return <ErrorState title="No such lesson." />;
  return (
    <article className="popout-body">
      <div className="page-eyebrow">
        <Icon name="learn" size={12} /> Lesson · {concept.category}
      </div>
      <h1 className="page-title">{concept.name}</h1>
      <p className="page-sub">{concept.what}</p>
      <div className="lesson-body">
        <LessonMarkdown>{concept.lesson}</LessonMarkdown>
      </div>
    </article>
  );
}

function PopoutProblem({ view }: { view: "statement" | "editorial" }) {
  const { id } = useParams();
  const [problem, setProblem] = useState<Problem | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    api
      .getProblem(Number(id))
      .then(setProblem)
      .catch((e) => setError(String(e)));
  }, [id]);
  useTitle(problem ? `${problem.title}${view === "editorial" ? " · editorial" : ""}` : undefined);

  if (error) return <ErrorState title="The problem could not be loaded." error={error} />;
  if (!problem) return <p className="faint">Loading…</p>;
  return (
    <article className="popout-body">
      <div className="page-eyebrow">{view === "editorial" ? "Editorial" : "Problem"}</div>
      <h1 className="page-title popout-title">
        {problem.title} <DiffBadge d={problem.difficulty} />
      </h1>
      {view === "statement" ? (
        <>
          <Markdown>{problem.description}</Markdown>
          {problem.constraints && (
            <>
              <h2 className="solve-section-title">Constraints</h2>
              <Markdown>{problem.constraints.split("\n").map((l) => `- ${l}`).join("\n")}</Markdown>
            </>
          )}
          {problem.examples.length > 0 && (
            <>
              <h2 className="solve-section-title">Examples</h2>
              {problem.examples.map((ex, i) => (
                <div key={i} className="card unit-block">
                  <div className="io-label">Input</div>
                  <div className="io-block">{ex.input}</div>
                  <div className="io-label">Output</div>
                  <div className="io-block">{ex.output}</div>
                  {ex.explanation && <p className="section-lead">{ex.explanation}</p>}
                </div>
              ))}
            </>
          )}
        </>
      ) : (
        <>
          <p className="section-lead">
            Optimal: <span className="mono">{problem.optimal_time || "—"}</span> time,{" "}
            <span className="mono">{problem.optimal_space || "—"}</span> space.{" "}
            {problem.optimal_explanation}
          </p>
          {problem.editorials.map((e, i) => (
            <section key={i} className="card unit-block">
              <h2 className="card-title">{e.title}</h2>
              <p className="exercise-note">
                {e.time && <>Time {e.time}</>} {e.space && <>· space {e.space}</>}
              </p>
              {e.body && <Markdown>{e.body}</Markdown>}
            </section>
          ))}
          <Markdown>{problem.editorial || "_No editorial provided._"}</Markdown>
        </>
      )}
    </article>
  );
}
