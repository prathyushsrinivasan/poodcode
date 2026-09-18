/**
 * A draggable split, with the description collapsible and a stacked fallback.
 *
 * `.solve` was `grid-template-columns: 1fr 1fr`, fixed. At the window's minimum
 * size (960px) with the sidebar showing, that left each half about 370px — too
 * narrow to read a problem statement in, and too narrow to write code in, at
 * the same time. Neither half could be given up for the other.
 *
 * The divider is a real `separator` with arrow-key support, because dragging a
 * 6px target is not something everyone can do.
 */

import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";

const MIN_PERCENT = 20;
const MAX_PERCENT = 80;
const STEP = 4;

/** Below this the panes stop being side by side and stack instead. */
const STACK_BELOW = 900;

export function SplitPane({
  left,
  right,
  /** 0-100, the left pane's share. Persisted by the caller. */
  percent,
  onPercent,
  collapsed,
  onExpand,
  leftLabel = "Description",
}: {
  left: ReactNode;
  right: ReactNode;
  percent: number;
  onPercent: (p: number) => void;
  collapsed: boolean;
  onExpand: () => void;
  leftLabel?: string;
}) {
  const host = useRef<HTMLDivElement>(null);
  const [dragging, setDragging] = useState(false);
  const [stacked, setStacked] = useState(
    () => typeof window !== "undefined" && window.innerWidth < STACK_BELOW
  );

  useEffect(() => {
    const onResize = () => setStacked(window.innerWidth < STACK_BELOW);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const applyFromX = useCallback(
    (clientX: number) => {
      const box = host.current?.getBoundingClientRect();
      if (!box || box.width === 0) return;
      const pct = ((clientX - box.left) / box.width) * 100;
      onPercent(Math.min(MAX_PERCENT, Math.max(MIN_PERCENT, pct)));
    },
    [onPercent]
  );

  useEffect(() => {
    if (!dragging) return;
    const move = (e: PointerEvent) => {
      e.preventDefault();
      applyFromX(e.clientX);
    };
    const up = () => setDragging(false);
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    // While dragging, the cursor belongs to the divider wherever it is, and no
    // text should select underneath it.
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
    return () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
  }, [dragging, applyFromX]);

  // Collapsed: the description becomes a thin rail you can click to bring back.
  if (collapsed && !stacked) {
    return (
      <div className="solve solve-collapsed" ref={host}>
        <button
          className="solve-rail"
          onClick={onExpand}
          title={`Show ${leftLabel.toLowerCase()} (Ctrl+.)`}
          aria-label={`Show ${leftLabel.toLowerCase()}`}
        >
          <span className="solve-rail-text">{leftLabel}</span>
          <span aria-hidden>›</span>
        </button>
        {right}
      </div>
    );
  }

  if (stacked) {
    return (
      <div className="solve solve-stacked" ref={host}>
        {left}
        {right}
      </div>
    );
  }

  return (
    <div
      className={`solve ${dragging ? "dragging" : ""}`}
      ref={host}
      // `minmax(0, 1fr)`, not `1fr`: a grid track's implicit minimum is
      // min-content, so the editor column refused to shrink below its
      // toolbar's natural width and pushed Submit off the window.
      style={{ gridTemplateColumns: `${percent}% 6px minmax(0, 1fr)` }}
    >
      {left}
      <div
        className="solve-divider"
        role="separator"
        aria-orientation="vertical"
        aria-label="Resize the panes"
        aria-valuenow={Math.round(percent)}
        aria-valuemin={MIN_PERCENT}
        aria-valuemax={MAX_PERCENT}
        tabIndex={0}
        onPointerDown={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDoubleClick={() => onPercent(50)}
        onKeyDown={(e) => {
          if (e.key === "ArrowLeft") {
            e.preventDefault();
            onPercent(Math.max(MIN_PERCENT, percent - STEP));
          } else if (e.key === "ArrowRight") {
            e.preventDefault();
            onPercent(Math.min(MAX_PERCENT, percent + STEP));
          } else if (e.key === "Home") {
            e.preventDefault();
            onPercent(50);
          }
        }}
      >
        <span className="solve-divider-grip" aria-hidden />
      </div>
      {right}
    </div>
  );
}
