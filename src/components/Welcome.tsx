/**
 * First-run orientation, as a short checklist.
 *
 * The old tour was a wall of six track descriptions, and it was wrong: it said
 * the Java course was "ten modules past the basics" when it has 31, and it
 * omitted Learn, Projects and 日本語 entirely. It also had no Escape handler, no
 * focus trap, and the only way back to it was a Settings button that cleared a
 * flag and reloaded the whole app.
 *
 * Now it is three things to do, the counts come from the seeds rather than from
 * prose that goes stale, and it is a real dialog (see ui/Modal) that Settings
 * reopens in place with an event.
 */

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { Modal } from "./ui/Modal";

interface Counts {
  problems: number | null;
  units: number | null;
  javaModules: number | null;
  tsWeeks: number | null;
}

export function Welcome({ open, onClose }: { open: boolean; onClose: () => void }) {
  const nav = useNavigate();
  const [counts, setCounts] = useState<Counts>({
    problems: null,
    units: null,
    javaModules: null,
    tsWeeks: null,
  });

  // Read the real numbers out of the seeds. Anything that fails to load is
  // simply left out of the sentence rather than guessed at.
  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    (async () => {
      const [problems, java, ts] = await Promise.all([
        api.listProblems().catch(() => null),
        api.javaCourse().catch(() => null),
        api.tsCourse().catch(() => null),
      ]);
      if (cancelled) return;
      setCounts({
        problems: problems?.length ?? null,
        units: null,
        javaModules: java ? java.weeks.filter((w) => w.authored).length : null,
        tsWeeks: ts ? ts.weeks.filter((w) => w.authored).length : null,
      });
    })();
    return () => {
      cancelled = true;
    };
  }, [open]);

  const go = (to: string) => {
    onClose();
    nav(to);
  };

  const steps = [
    {
      n: 1,
      title: "Pick a track",
      body: (
        <>
          The <strong>DSA Curriculum</strong> teaches
          {counts.problems ? ` all ${counts.problems} problems` : " every problem"} in the order
          that builds them, starting below Easy — printing a line. The{" "}
          <strong>Java</strong>
          {counts.javaModules ? ` (${counts.javaModules} judged modules)` : ""} and{" "}
          <strong>TypeScript</strong>
          {counts.tsWeeks ? ` (${counts.tsWeeks} weeks)` : ""} courses teach the languages
          themselves. <strong>Learn</strong> is the concept library behind both, and{" "}
          <strong>Projects</strong> and the <strong>Backend Lab</strong> are build-it-yourself
          tracks.
        </>
      ),
      action: { label: "Open the DSA Curriculum", to: "/library" },
    },
    {
      n: 2,
      title: "Solve one problem",
      body: (
        <>
          You write a solution and it is judged against real test cases, offline. Press{" "}
          <span className="kbd">Ctrl</span>
          <span className="kbd">Enter</span> to run and{" "}
          <span className="kbd">Ctrl</span>
          <span className="kbd">Shift</span>
          <span className="kbd">Enter</span> to submit. Press{" "}
          <span className="kbd">?</span> for every other shortcut.
        </>
      ),
      action: { label: "Browse all problems", to: "/library/browse" },
    },
    {
      n: 3,
      title: "Set your daily goals",
      body: (
        <>
          Today's page tracks a streak, what is due for review across every track, and how far
          each one has got. The targets it measures against are yours to set.
        </>
      ),
      action: { label: "Open Settings", to: "/settings" },
    },
  ];

  return (
    <Modal
      open={open}
      onClose={onClose}
      size="md"
      title={
        <span className="welcome-title">
          <span className="logo" aria-hidden>
            P
          </span>
          Welcome to Poodcode
        </span>
      }
      description="Your offline coding-interview trainer. Three things to get going."
      footer={
        <>
          <button className="ghost" onClick={onClose}>
            Skip for now
          </button>
          <span className="spacer" />
          <button className="primary" onClick={() => go("/library")}>
            Start the DSA Curriculum →
          </button>
        </>
      }
    >
      <ol className="welcome-steps">
        {steps.map((s) => (
          <li key={s.n}>
            <div className="welcome-step-n" aria-hidden>
              {s.n}
            </div>
            <div className="welcome-step-body">
              <strong>{s.title}</strong>
              <p className="dim">{s.body}</p>
              <button className="ghost welcome-step-go" onClick={() => go(s.action.to)}>
                {s.action.label} →
              </button>
            </div>
          </li>
        ))}
      </ol>
    </Modal>
  );
}
