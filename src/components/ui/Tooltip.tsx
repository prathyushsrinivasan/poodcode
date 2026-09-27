/**
 * A tooltip that keyboard users get too (UI_ROADMAP C3, D8).
 *
 * `title=` only appears after a mouse has rested on something for a second,
 * never on focus, and cannot hold a shortcut hint in a readable form. This one
 * shows on hover *and* on focus of whatever it wraps, is tied to it by
 * `aria-describedby`, and hides on Escape.
 *
 * It wraps a single focusable child and positions above it with CSS; there is
 * no portal, so it is for short labels on toolbar controls, not for rich
 * popovers inside scrolling containers that clip.
 */

import { cloneElement, isValidElement, useEffect, useId, useState, type ReactElement, type ReactNode } from "react";
import { Kbd } from "./Card";

export function Tooltip({
  content,
  shortcut,
  placement = "top",
  children,
}: {
  content: ReactNode;
  shortcut?: string;
  placement?: "top" | "bottom";
  children: ReactElement;
}) {
  const id = useId();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  if (!isValidElement(children)) return children;

  const child = cloneElement(children as ReactElement<Record<string, unknown>>, {
    "aria-describedby": id,
  });

  return (
    <span
      className="tooltip-host"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
      onBlur={() => setOpen(false)}
    >
      {child}
      <span role="tooltip" id={id} className={`tooltip tooltip-${placement} ${open ? "open" : ""}`}>
        {content}
        {shortcut && (
          <span className="tooltip-keys">
            <Kbd keys={shortcut} />
          </span>
        )}
      </span>
    </span>
  );
}
