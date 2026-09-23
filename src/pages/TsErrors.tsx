import { useEffect, useMemo, useRef, useState, type RefObject } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Markdown } from "../components/Markdown";
import { Empty, inlineCode } from "../components/common";
import { TS_ERRORS, errorEntry, searchErrors, type TsErrorEntry } from "../lib/tsErrors";

/**
 * The TypeScript error glossary. Every entry is proven by
 * tools/gen_ts_errors.py: its "before" program really produces the code under
 * the judge's settings, and its "after" program type-checks clean and runs.
 *
 * `?code=2322` opens and scrolls to one entry — that is where the links under
 * a compile error land.
 */
export default function TsErrors() {
  const [params] = useSearchParams();
  const linked = Number(params.get("code")) || null;
  const [query, setQuery] = useState("");
  const hits = useMemo(() => searchErrors(query), [query]);
  const target = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (linked && errorEntry(linked)) target.current?.scrollIntoView({ block: "start" });
  }, [linked]);

  return (
    <div className="page">
      <h1 className="page-title">TypeScript errors, explained</h1>
      <p className="page-sub">
        {TS_ERRORS.length} errors you will meet while learning, each with what it means, what usually
        causes it, and a small program before and after the fix. Every example is checked with the
        same compiler settings the judge uses.
      </p>

      <input
        className="ts-error-search"
        type="search"
        placeholder="Search by code (2322) or words (possibly undefined)…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        aria-label="Search TypeScript errors"
      />

      {hits.length === 0 ? (
        <Empty icon="🔎" text="No error matches that. Try the code number from the message." />
      ) : (
        hits.map((e) => (
          <ErrorEntry
            key={e.code}
            entry={e}
            open={e.code === linked || query.trim() !== ""}
            highlight={e.code === linked}
            anchor={e.code === linked ? target : undefined}
          />
        ))
      )}
    </div>
  );
}

function ErrorEntry({
  entry,
  open,
  highlight,
  anchor,
}: {
  entry: TsErrorEntry;
  open: boolean;
  highlight: boolean;
  anchor?: RefObject<HTMLDivElement>;
}) {
  return (
    <div ref={anchor} className={`card ts-error-entry${highlight ? " highlight" : ""}`}>
      <details open={open}>
        <summary>
          <span className="ts-error-code">TS{entry.code}</span> {entry.title}
          <div className="dim ts-error-meaning">{inlineCode(entry.meaning)}</div>
        </summary>
        <Markdown>{entry.cause}</Markdown>
        <div className="ts-error-pair">
          <div>
            <div className="io-label">Produces TS{entry.code}</div>
            <Markdown>{"```ts\n" + entry.bad + "```"}</Markdown>
          </div>
          <div>
            <div className="io-label">Fixed</div>
            <Markdown>{"```ts\n" + entry.good + "```"}</Markdown>
          </div>
        </div>
        <p className="dim ts-error-foot">
          {entry.preset === "strict+indexed" && "Checked with noUncheckedIndexedAccess on. "}
          Taught in <Link to="/mastery">TypeScript Mastery, week {entry.week}</Link>.
        </p>
      </details>
    </div>
  );
}
