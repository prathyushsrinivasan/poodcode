/**
 * Pop a lesson or an editorial out into its own window (UI_ROADMAP J4).
 *
 * On one screen, Solve's description and editor share the width; on a large
 * or second monitor, the lesson or editorial you are working from can have a
 * window of its own beside the editor. Each popout is a second Tauri webview
 * showing a chrome-less route (`/popout/...`). Opening the same thing twice
 * focuses the window already showing it. In a plain browser (the mock), it is
 * a `window.open`.
 */

/** A window label Tauri accepts: letters, digits, `-`, `/`, `:`, `_`. */
export function popoutLabel(path: string): string {
  return `popout-${path.replace(/^\/+/, "").replace(/[^a-zA-Z0-9_-]+/g, "-")}`.slice(0, 80);
}

function inTauri(): boolean {
  return typeof window !== "undefined" && "__TAURI_INTERNALS__" in window;
}

export async function openPopout(path: string, title: string): Promise<void> {
  const url = `index.html#${path}`;
  const label = popoutLabel(path);
  if (!inTauri()) {
    window.open(`#${path}`, label, "width=760,height=900");
    return;
  }
  const { WebviewWindow } = await import("@tauri-apps/api/webviewWindow");
  const existing = await WebviewWindow.getByLabel(label);
  if (existing) {
    await existing.setFocus();
    return;
  }
  const win = new WebviewWindow(label, {
    url,
    title: `${title} — Poodcode`,
    width: 760,
    height: 900,
    minWidth: 420,
    minHeight: 400,
  });
  await new Promise<void>((resolve, reject) => {
    void win.once("tauri://created", () => resolve());
    void win.once("tauri://error", (e) => reject(new Error(String(e.payload))));
  });
}
