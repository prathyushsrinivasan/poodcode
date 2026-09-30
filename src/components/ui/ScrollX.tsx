/**
 * Something that scrolls sideways, reachable from the keyboard.
 *
 * A wide table or a long line of code in an `overflow: auto` box can only be
 * scrolled with a mouse unless the box itself takes focus — Tab never lands in
 * it when it holds nothing focusable, and the arrow keys have nothing to act on
 * (WCAG 2.1.1; axe's scrollable-region-focusable found it on unit pages and in
 * lesson code). The box becomes a named, focusable region only while its
 * content actually overflows, so a table that fits adds no tab stop.
 */

import { useEffect, useRef, useState, type ReactNode } from "react";

/** A ref for a scroll box, and the attributes it needs while it overflows. */
export function useKeyboardScroll<T extends HTMLElement>(label: string) {
  const ref = useRef<T>(null);
  const [overflows, setOverflows] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const check = () => setOverflows(el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1);
    check();
    // The box resizing (the window, a rail folding) and its content changing
    // (a table filling in) can each start or stop the overflow.
    const resize = new ResizeObserver(check);
    resize.observe(el);
    const content = new MutationObserver(check);
    content.observe(el, { childList: true, subtree: true, characterData: true });
    return () => {
      resize.disconnect();
      content.disconnect();
    };
  }, []);

  const attrs = overflows ? { tabIndex: 0, role: "region" as const, "aria-label": label } : {};
  return [ref, attrs] as const;
}

/** A sideways-scrolling box: `<ScrollX label="Costs" className="card p-0">`. */
export function ScrollX({ label, className, children }: { label: string; className?: string; children: ReactNode }) {
  const [ref, attrs] = useKeyboardScroll<HTMLDivElement>(label);
  return (
    <div ref={ref} className={className ? `overflow-x-auto ${className}` : "overflow-x-auto"} {...attrs}>
      {children}
    </div>
  );
}
