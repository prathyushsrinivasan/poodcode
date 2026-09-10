import { useState } from "react";
import { Markdown } from "./Markdown";

/** A worked solution, hidden behind a button.
 *
 * Shared by all three track pages, which each want their own wording — the
 * Backend Lab reveals "a reference implementation", a Projects module reveals
 * "the solution for this module" — but the same behaviour underneath: it stays
 * shut until asked for, and it comes with a caveat about what to do with it.
 *
 * `note` is that caveat. It defaults to the honest one: comparing your own
 * attempt against this is the part that teaches; replacing yours with it is
 * not. Pass a different one to say more; pass "" to say nothing. */
export function ReferenceReveal({
  reference,
  language = "ts",
  revealLabel = "Reveal a reference solution",
  hideLabel = "Hide the reference solution",
  note = "One way to write it — not the only way. Compare it with yours rather than replacing yours with it.",
}: {
  reference: string;
  language?: string;
  revealLabel?: string;
  hideLabel?: string;
  note?: string;
}) {
  const [show, setShow] = useState(false);
  return (
    <div style={{ marginTop: 14 }}>
      <button className="ghost" onClick={() => setShow((s) => !s)}>
        {show ? hideLabel : revealLabel}
      </button>
      {show && (
        <div style={{ marginTop: 10 }}>
          {note && (
            <p className="faint" style={{ fontSize: 12 }}>
              {note}
            </p>
          )}
          <Markdown>{"```" + language + "\n" + reference + "\n```"}</Markdown>
        </div>
      )}
    </div>
  );
}
