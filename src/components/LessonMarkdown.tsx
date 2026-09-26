// A lesson, with its pitfalls as collapsible cards (TS_MASTERY_ROADMAP X-05).
// Lessons without a "### Pitfalls" section render exactly as plain Markdown.
import { useMemo } from "react";
import { splitPitfalls } from "../lib/lessonSections";
import { InlineMarkdown, Markdown } from "./Markdown";

export function LessonMarkdown({ children }: { children: string }) {
  const parts = useMemo(() => splitPitfalls(children), [children]);
  if (!parts) return <Markdown>{children}</Markdown>;
  return (
    <>
      <Markdown>{parts.before}</Markdown>
      <Markdown>{parts.heading}</Markdown>
      <p className="dim quiz-note" style={{ marginTop: -4 }}>
        Each looks right and isn't. Guess what goes wrong before you open it.
      </p>
      {parts.pitfalls.map((p, i) => (
        <details key={i} className="card pitfall-card">
          <summary>
            <span className="pitfall-mark" aria-hidden>
              ⚠
            </span>{" "}
            <InlineMarkdown>{p.title}</InlineMarkdown>
          </summary>
          <Markdown>{p.body}</Markdown>
        </details>
      ))}
      {parts.after && <Markdown>{parts.after}</Markdown>}
    </>
  );
}
