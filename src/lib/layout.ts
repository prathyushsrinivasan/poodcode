/**
 * The layout contract between the window's minimum (960px) and a wide
 * monitor (UI_ROADMAP J1).
 *
 * There were two breakpoints, both in the curriculum's CSS, and every other
 * page did whatever its grid happened to do. Three classes now, named here and
 * exposed on the app frame as `data-layout`, so a page's CSS and its code
 * agree on where the lines are:
 *
 *   width        class     sidebar            reading pages         Solve
 *   ---------    -------   ----------------   -------------------   ------------------
 *   < 1180       compact   folds to icons     one column; the       side by side,
 *                          (transiently —     outline rail moves    resizable; stacks
 *                          your choice is     above the content     under 900px of pane
 *                          kept for wider)
 *   1180–1439    regular   as you left it     body + 190px rail     side by side
 *   ≥ 1440       wide      as you left it     body + 210px rail     side by side
 *
 * Card grids use `auto-fill` / `auto-fit` minimums rather than fixed column
 * counts, so they re-flow within a class without a breakpoint of their own.
 * `node tools/layout-check.mjs` loads every page at 960, 1180 and 1440 and
 * fails on sideways scrolling, a wrong class, or Solve's Run/Submit off screen.
 */

export const COMPACT_BELOW = 1180;
export const WIDE_FROM = 1440;

export type LayoutClass = "compact" | "regular" | "wide";

export function layoutClass(width: number): LayoutClass {
  if (width < COMPACT_BELOW) return "compact";
  if (width < WIDE_FROM) return "regular";
  return "wide";
}

/** Whether the shell should fold the sidebar on its own: on editor pages, and in compact windows. */
export function shouldAutoCollapse(layout: LayoutClass, onEditorPage: boolean): boolean {
  return onEditorPage || layout === "compact";
}
