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
