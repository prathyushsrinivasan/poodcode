/**
 * Remember where each page was scrolled to.
 *
 * The app scrolls inside `.main`, not the window, so the router's own scroll
 * handling never applied: going back from a problem to Browse, or to a long
 * course page, always landed at the top — losing the row you were reading and
 * making "back" feel like "start over".
 *
 * Positions are keyed by path and kept in memory for the session only. A new
 * navigation (PUSH) starts at the top, as a new page should; a back or forward
 * (POP) restores.
 */

import { useEffect, useLayoutEffect, useRef } from "react";
import { useLocation, useNavigationType } from "react-router-dom";

const positions = new Map<string, number>();

export function ScrollRestore({ containerId = "main" }: { containerId?: string }) {
  const { key, pathname } = useLocation();
  const navType = useNavigationType();
  const previous = useRef<{ key: string; el: HTMLElement | null } | null>(null);

  // Save on the way out. `useLayoutEffect`'s cleanup runs before the new page
  // paints, so the number recorded is the old page's, not zero.
  useLayoutEffect(() => {
    const el = document.getElementById(containerId);
    previous.current = { key, el };
    return () => {
      if (el) positions.set(key, el.scrollTop);
    };
  }, [key, containerId]);

  useLayoutEffect(() => {
    const el = document.getElementById(containerId);
    if (!el) return;
    const saved = positions.get(key);
    // POP is back/forward — the only case where a remembered position is what
    // the user expects. Following a link should start at the top.
    el.scrollTop = navType === "POP" && saved !== undefined ? saved : 0;
  }, [key, navType, containerId]);

  // Pages load their content after the route changes, so the scroll height the
  // restore needed often did not exist yet. Re-apply once as content settles.
  useEffect(() => {
    if (navType !== "POP") return;
    const saved = positions.get(key);
    if (saved === undefined || saved === 0) return;
    let frames = 0;
    let raf = 0;
    const retry = () => {
      const el = document.getElementById(containerId);
      if (el && el.scrollHeight > el.clientHeight + saved) {
        el.scrollTop = saved;
        return;
      }
      if (frames++ < 30) raf = requestAnimationFrame(retry);
    };
    raf = requestAnimationFrame(retry);
    return () => cancelAnimationFrame(raf);
  }, [key, pathname, navType, containerId]);

  return null;
}
