/**
 * The keyboard-shortcut sheet, opened with `?`.
 *
 * The editor has had Ctrl+Enter and Ctrl+Shift+Enter since the beginning and
 * the palette has had Ctrl+K, but nothing in the app said so — you had to be
 * told, or read the source. This is the one place that lists them, and the
 * single source the tooltips elsewhere quote.
 */

import { useEffect, useState } from "react";
import { Modal } from "../ui/Modal";

export interface Shortcut {
  keys: string[];
  what: string;
}

export const SHORTCUTS: { group: string; items: Shortcut[] }[] = [
  {
    group: "Getting around",
    items: [
      { keys: ["Ctrl", "K"], what: "Open the command palette" },
      { keys: ["Alt", "←"], what: "Back" },
      { keys: ["Alt", "→"], what: "Forward" },
      { keys: ["Ctrl", "B"], what: "Collapse or expand the sidebar" },
      { keys: ["?"], what: "Show this sheet" },
      { keys: ["Esc"], what: "Close a dialog, the palette, or this sheet" },
    ],
  },
  {
    group: "Solving",
    items: [
      { keys: ["Ctrl", "Enter"], what: "Run against the example cases" },
      { keys: ["Ctrl", "Shift", "Enter"], what: "Submit" },
      { keys: ["Ctrl", "E"], what: "Focus the editor" },
      { keys: ["Ctrl", "."], what: "Show or hide the description pane" },
      { keys: ["Alt", "N"], what: "Next problem in the rung" },
      { keys: ["Alt", "P"], what: "Previous problem in the rung" },
      { keys: ["Ctrl", "H"], what: "Reveal the next hint" },
    ],
  },
  {
    group: "Editor",
    items: [
      { keys: ["Ctrl", "F"], what: "Find" },
      { keys: ["Ctrl", "H"], what: "Replace (inside the editor)" },
      { keys: ["Alt", "Shift", "F"], what: "Format the document" },
    ],
  },
];

export function Kbd({ children }: { children: React.ReactNode }) {
  return <span className="kbd">{children}</span>;
}

/** Renders a shortcut's keys with "+" between them. Used here and in tooltips. */
export function Keys({ keys }: { keys: string[] }) {
  return (
    <span className="keys">
      {keys.map((k, i) => (
        <span key={k + i}>
          {i > 0 && <span className="keys-plus">+</span>}
          <Kbd>{k}</Kbd>
        </span>
      ))}
    </span>
  );
}

export function ShortcutSheet() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "?") return;
      // "?" is a perfectly ordinary character to type; only treat it as the
      // shortcut when the user is not writing something.
      const el = document.activeElement as HTMLElement | null;
      const typing =
        el &&
        (el.tagName === "INPUT" ||
          el.tagName === "TEXTAREA" ||
          el.isContentEditable ||
          el.closest(".monaco-editor") !== null);
      if (typing) return;
      e.preventDefault();
      setOpen((o) => !o);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    const show = () => setOpen(true);
    window.addEventListener("poodcode:show-shortcuts", show);
    return () => window.removeEventListener("poodcode:show-shortcuts", show);
  }, []);

  return (
    <Modal
      open={open}
      onClose={() => setOpen(false)}
      title="Keyboard shortcuts"
      description="Press ? at any time to bring this back."
      size="lg"
    >
      <div className="shortcut-groups">
        {SHORTCUTS.map((g) => (
          <div key={g.group}>
            <h3 className="shortcut-group-title">{g.group}</h3>
            <table className="shortcut-table">
              <tbody>
                {g.items.map((s) => (
                  <tr key={s.what + s.keys.join()}>
                    <td className="shortcut-keys">
                      <Keys keys={s.keys} />
                    </td>
                    <td>{s.what}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    </Modal>
  );
}
