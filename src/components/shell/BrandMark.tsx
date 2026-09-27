/**
 * The Poodcode mark (UI_ROADMAP C12).
 *
 * It was a "P" on a gradient square, the gradient running into a #7b5cff that
 * existed nowhere else in the palette. The mark is now drawn: a P whose bowl
 * is a prompt chevron, with a cursor underneath — a P and a `>_` at once,
 * which is what the app is. In the UI it takes the theme's accent, so it
 * follows light, dark and high contrast; `src-tauri/icons/source.svg` is the
 * same drawing in fixed colours, and every app icon is generated from it
 * (`npx tauri icon src-tauri/icons/source.svg`).
 */

export function BrandMark({ size = 26, title }: { size?: number; title?: string }) {
  return (
    <svg
      className="brand-mark"
      width={size}
      height={size}
      viewBox="0 0 64 64"
      role={title ? "img" : undefined}
      aria-label={title}
      aria-hidden={title ? undefined : true}
      focusable="false"
    >
      <rect width="64" height="64" rx="15" className="brand-mark-bg" />
      <g fill="none" strokeLinecap="round" strokeLinejoin="round" className="brand-mark-glyph">
        {/* The stem, and a bowl drawn as a chevron: P, and a prompt. */}
        <path d="M20 14 V50" strokeWidth="7" />
        <path d="M20 14 H29 L41 24 L29 34 H20" strokeWidth="7" />
        {/* The cursor. */}
        <path d="M35 48 H45" strokeWidth="5" />
      </g>
    </svg>
  );
}
