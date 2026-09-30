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

import { isValidElement, useMemo, useState, type ReactNode } from "react";
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

import { useHeadingLevel } from "./ui/Heading";
import { useKeyboardScroll } from "./ui/ScrollX";
import { topHeadingLevel } from "../lib/markdownOutline";

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
  // A long line scrolls the block sideways; the keyboard needs to reach it.
  const [preRef, scrollAttrs] = useKeyboardScroll<HTMLPreElement>("Code");

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

  // A TypeScript block opens in the playground in one click (X-04): the same
  // code, with its inferred types, narrowing and emitted JavaScript beside it.
  const className =
    isValidElement(children) && typeof (children.props as { className?: unknown }).className === "string"
      ? ((children.props as { className: string }).className)
      : "";
  const isTs = /\blanguage-(ts|typescript)\b/.test(className);
  const openInPlayground = (e: React.MouseEvent<HTMLButtonElement>) => {
    const text = e.currentTarget.closest(".md-pre")?.querySelector("pre")?.textContent ?? "";
    try {
      localStorage.setItem("poodcode:ts-playground", JSON.stringify({ code: text, focus: "" }));
    } catch {
      /* private mode — the playground opens on its example instead */
    }
    window.location.hash = "#/playground/ts";
  };

  return (
    <div className="md-pre">
      <span className="md-actions">
        {isTs && (
          <button className="md-copy" onClick={openInPlayground} title="Open this code in the TypeScript playground">
            ▶ Playground
          </button>
        )}
        <button className="md-copy" onClick={copy} aria-label="Copy this code">
          {copied ? "Copied" : "Copy"}
        </button>
      </span>
      <pre ref={preRef} {...scrollAttrs}>
        {children}
      </pre>
    </div>
  );
}

type HeadingProps = { children?: ReactNode; node?: unknown; className?: string; id?: string };

/**
 * Heading components for one rendering, rebased onto the page's outline.
 *
 * Content is authored with `##` or `###` as its top level, whatever it ends up
 * inside, so a statement written with `### Input` sat straight under the
 * page's h1 and a screen reader's heading list skipped a level (axe found it on
 * Projects, Solve and every module page). The shallowest heading in the text
 * now renders at the level the surrounding page expects (D9's heading
 * context), the rest keep their distance from it, and the authored level stays
 * a class so each one looks exactly as it did. `md-top` marks the top level
 * for the lesson outline.
 */
function headings(offset: number, top: number) {
  const make = (authored: number) =>
    function MdHeading({ children, id }: HeadingProps) {
      const level = Math.max(1, Math.min(6, authored + offset));
      const Tag = `h${level}` as "h2";
      return (
        <Tag id={id} className={authored === top ? `md-h${authored} md-top` : `md-h${authored}`}>
          {children}
        </Tag>
      );
    };
  return { h1: make(1), h2: make(2), h3: make(3), h4: make(4), h5: make(5), h6: make(6) };
}

/** Renders markdown (GFM: tables, checklists, etc.) inside a styled container. */
export function Markdown({ children }: { children: string }) {
  const level = useHeadingLevel();
  const top = useMemo(() => topHeadingLevel(children || ""), [children]);
  const components = useMemo(
    () => ({
      pre: ({ children: c }: { children?: ReactNode }) => <CodeBlock>{c}</CodeBlock>,
      ...(top === null ? {} : headings(level - top, top)),
    }),
    [level, top]
  );
  return (
    <div className="md">
      <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={REHYPE} components={components}>
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
