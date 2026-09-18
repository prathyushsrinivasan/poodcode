/**
 * The window's own chrome: history, a breadcrumb, and the palette.
 *
 * Tauri draws no browser UI, so the app had no back button and no sense of
 * place. Four pages drew their own "←" and the rest simply stranded you —
 * opening a problem from Today, from the curriculum or from the palette left
 * nowhere to go but the sidebar.
 *
 * Back and forward are bound to Alt+←/→ and to mouse buttons 4/5 (the physical
 * back/forward buttons on most mice), because those are what people already
 * press.
 */

import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useStore } from "../../store";
import { breadcrumb, withLeafLabel } from "../../lib/breadcrumb";

export function TopBar() {
  const nav = useNavigate();
  const { pathname } = useLocation();
  const setPalette = useStore((s) => s.setPalette);
  const toggleSidebar = useStore((s) => s.toggleSidebar);
  const collapsed = useStore((s) => s.sidebarAuto ?? s.prefs.sidebarCollapsed);
  const crumbLabel = useStore((s) => s.crumbLabel);

  // "Can I go forward?" is not answerable from the History API — it exposes
  // `length` but not the position within it. React Router stamps each entry
  // with `history.state.idx`, so the current position is readable; remembering
  // the deepest index reached tells us whether anything is ahead of us.
  const [{ index, deepest }, setPos] = useState({ index: 0, deepest: 0 });

  useEffect(() => {
    const idx = Number((window.history.state as { idx?: number } | null)?.idx ?? 0);
    setPos((p) => ({ index: idx, deepest: Math.max(p.deepest, idx) }));
  }, [pathname]);

  const canBack = index > 0;
  const canForward = index < deepest;

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!e.altKey) return;
      if (e.key === "ArrowLeft") {
        e.preventDefault();
        nav(-1);
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        nav(1);
      }
    };
    // Mouse buttons 3 and 4 are the side "back"/"forward" buttons.
    const onMouse = (e: MouseEvent) => {
      if (e.button === 3) {
        e.preventDefault();
        nav(-1);
      } else if (e.button === 4) {
        e.preventDefault();
        nav(1);
      }
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("mouseup", onMouse);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("mouseup", onMouse);
    };
  }, [nav]);

  const crumbs = withLeafLabel(breadcrumb(pathname), crumbLabel);

  return (
    <header className="topbar">
      <button
        className="ghost topbar-icon"
        onClick={toggleSidebar}
        aria-label={collapsed ? "Expand the sidebar" : "Collapse the sidebar"}
        title={`${collapsed ? "Expand" : "Collapse"} sidebar (Ctrl+B)`}
      >
        ☰
      </button>
      <button
        className="ghost topbar-icon"
        onClick={() => nav(-1)}
        disabled={!canBack}
        aria-label="Back"
        title="Back (Alt+←)"
      >
        ←
      </button>
      <button
        className="ghost topbar-icon"
        onClick={() => nav(1)}
        disabled={!canForward}
        aria-label="Forward"
        title="Forward (Alt+→)"
      >
        →
      </button>

      <nav className="crumbs" aria-label="Breadcrumb">
        <ol>
          {crumbs.map((c, i) => (
            <li key={`${c.label}-${i}`}>
              {c.href ? (
                <Link to={c.href}>{c.label}</Link>
              ) : (
                <span aria-current="page" className={c.dynamic ? "crumb-pending" : undefined}>
                  {c.label}
                </span>
              )}
              {i < crumbs.length - 1 && (
                <span className="crumb-sep" aria-hidden>
                  ›
                </span>
              )}
            </li>
          ))}
        </ol>
      </nav>

      <span className="spacer" />

      <button className="ghost topbar-search" onClick={() => setPalette(true)}>
        <span aria-hidden>🔎</span> Search…
        <span className="kbd">Ctrl</span>
        <span className="kbd">K</span>
      </button>
    </header>
  );
}
