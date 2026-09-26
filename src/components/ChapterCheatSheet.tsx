// A TypeScript chapter's cheat sheet (X-08): built from the lesson, one screen,
// printable on its own — printing hides everything else on the page.
import { useMemo } from "react";
import { cheatSheet, cheatSheetMarkdown } from "../lib/cheatSheet";
import { TS_ERRORS } from "../lib/tsErrors";
import { Markdown } from "./Markdown";

const GLOSSARY = new Map(TS_ERRORS.map((e) => [e.code, e.title]));

export function ChapterCheatSheet({ name, what, lesson }: { name: string; what: string; lesson: string }) {
  const md = useMemo(() => cheatSheetMarkdown(name, what, cheatSheet(lesson, GLOSSARY)), [name, what, lesson]);

  function print() {
    document.body.classList.add("printing-sheet");
    const done = () => {
      document.body.classList.remove("printing-sheet");
      window.removeEventListener("afterprint", done);
    };
    window.addEventListener("afterprint", done);
    window.print();
  }

  return (
    <div>
      <div className="row" style={{ justifyContent: "flex-end", marginBottom: 6 }}>
        <button className="ghost" onClick={print}>
          🖨 Print
        </button>
      </div>
      <div className="cheat-sheet">
        <Markdown>{md}</Markdown>
      </div>
    </div>
  );
}
