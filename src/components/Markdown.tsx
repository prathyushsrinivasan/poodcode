import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/** Renders markdown (GFM: tables, checklists, etc.) inside a styled container. */
export function Markdown({ children }: { children: string }) {
  return (
    <div className="md">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children || ""}</ReactMarkdown>
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
