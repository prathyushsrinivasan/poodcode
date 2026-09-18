/**
 * Markdown rendering for every lesson, note and problem statement in the app.
 *
 * Fenced code used to render as plain text. That is hundreds of Java,
 * TypeScript and SQL lessons whose entire point is the code in them, shown
 * without a single colour — and with no way to copy a block except selecting it
 * by hand.
 *
 * Highlighting is `rehype-highlight`, which was already a dependency and unused,
 * restricted to the languages the content actually contains: the default is to
 * register all ~190 grammars, which is most of a megabyte for nothing. The
 * palette in `global.css` is keyed to the same colours Monaco uses, so a snippet
 * in a lesson and the same code in the editor look the same.
 */

import { useState, type ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";

import java from "highlight.js/lib/languages/java";
import typescript from "highlight.js/lib/languages/typescript";
import javascript from "highlight.js/lib/languages/javascript";
import sql from "highlight.js/lib/languages/sql";
import python from "highlight.js/lib/languages/python";
import bash from "highlight.js/lib/languages/bash";
import json from "highlight.js/lib/languages/json";
import xml from "highlight.js/lib/languages/xml";
import css from "highlight.js/lib/languages/css";
import plaintext from "highlight.js/lib/languages/plaintext";

/** Exactly the grammars the content uses. `text` is aliased so a fence tagged
 * ```text is highlighted as nothing rather than guessed at. */
const LANGUAGES = {
  java,
  typescript,
  javascript,
  sql,
  python,
  bash,
  json,
  xml,
  css,
  plaintext,
};

const REHYPE = [[rehypeHighlight, { languages: LANGUAGES, detect: true, ignoreMissing: true }]] as never;

/** A fenced block with a copy button. */
function CodeBlock({ children }: { children: ReactNode }) {
  const [copied, setCopied] = useState(false);

  const copy = async (e: React.MouseEvent<HTMLButtonElement>) => {
    // The text is whatever the <pre> ended up containing, which is the
    // highlighted markup's text — exactly what the reader sees.
    const pre = e.currentTarget.closest(".md-pre")?.querySelector("pre");
    const text = pre?.textContent ?? "";
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    } catch {
      /* clipboard denied — the block is still selectable */
    }
  };

  return (
    <div className="md-pre">
      <button className="md-copy" onClick={copy} aria-label="Copy this code">
        {copied ? "Copied" : "Copy"}
      </button>
      <pre>{children}</pre>
    </div>
  );
}

const COMPONENTS = {
  pre: ({ children }: { children?: ReactNode }) => <CodeBlock>{children}</CodeBlock>,
};

/** Renders markdown (GFM: tables, checklists, etc.) inside a styled container. */
export function Markdown({ children }: { children: string }) {
  return (
    <div className="md">
      <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={REHYPE} components={COMPONENTS}>
        {children || ""}
      </ReactMarkdown>
    </div>
  );
}

/** One line of markdown with no block wrapper around it.
 *
 * The content tracks write single-line prose with inline code in it — a
 * pitfall, an acceptance check, an objective — and rendering those as plain
 * text leaves the backticks on screen. This drops the `<p>` react-markdown
 * would otherwise emit, so a line can sit inside a flex row or a list item
 * without a block element fighting the layout. */
export function InlineMarkdown({ children }: { children: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{ p: ({ children: c }) => <>{c}</> }}
    >
      {children || ""}
    </ReactMarkdown>
  );
}
