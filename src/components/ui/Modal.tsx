/**
 * Dialogs that behave like dialogs.
 *
 * The app had two overlays — the welcome tour and the command palette — and
 * neither was a dialog in any sense a screen reader or a keyboard could detect:
 * no `aria-modal`, no focus trap, no restore of focus on close, and in the
 * welcome's case no Escape handler either. Four more decisions went through
 * `window.confirm`, which cannot say what is about to be lost.
 *
 * `Modal` is the one implementation of that behaviour; `ConfirmDialog` is the
 * destructive-action case built on it.
 */

import { useCallback, useEffect, useRef, type ReactNode } from "react";

/** Everything focusable, in DOM order, that is not disabled or hidden. */
const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

export function Modal({
  open,
  onClose,
  title,
  description,
  children,
  footer,
  size = "md",
  labelledBy,
}: {
  open: boolean;
  onClose: () => void;
  /** Rendered as the dialog's heading and used as its accessible name. */
  title?: ReactNode;
  description?: ReactNode;
  children?: ReactNode;
  footer?: ReactNode;
  size?: "sm" | "md" | "lg";
  /** Supply when the heading is drawn inside `children` instead of `title`. */
  labelledBy?: string;
}) {
  const card = useRef<HTMLDivElement>(null);
  const restoreTo = useRef<HTMLElement | null>(null);
  const titleId = useRef(`modal-title-${Math.random().toString(36).slice(2, 9)}`);

  // Remember what had focus, move focus inside, and put it back on close —
  // otherwise closing a dialog drops the keyboard user at the top of the page.
  useEffect(() => {
    if (!open) return;
    restoreTo.current = document.activeElement as HTMLElement | null;
    const first = card.current?.querySelector<HTMLElement>(FOCUSABLE);
    (first ?? card.current)?.focus();
    return () => restoreTo.current?.focus?.();
  }, [open]);

  const onKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        onClose();
        return;
      }
      if (e.key !== "Tab") return;
      // Trap: cycle within the dialog rather than escaping to the page behind.
      const items = [...(card.current?.querySelectorAll<HTMLElement>(FOCUSABLE) ?? [])];
      if (items.length === 0) return;
      const first = items[0];
      const last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    },
    [onClose]
  );

  if (!open) return null;

  return (
    <div
      className="modal-overlay"
      onMouseDown={(e) => {
        // Only a click that both starts and ends on the backdrop dismisses —
        // otherwise a text selection dragged out of the dialog closes it.
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className={`modal modal-${size}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby={labelledBy ?? (title ? titleId.current : undefined)}
        ref={card}
        tabIndex={-1}
        onKeyDown={onKeyDown}
      >
        {title && (
          <div className="modal-head">
            <h2 id={titleId.current} className="modal-title">
              {title}
            </h2>
            <button className="ghost modal-x" onClick={onClose} aria-label="Close dialog">
              ✕
            </button>
          </div>
        )}
        {description && <p className="modal-desc">{description}</p>}
        {children && <div className="modal-body">{children}</div>}
        {footer && <div className="modal-foot">{footer}</div>}
      </div>
    </div>
  );
}

/**
 * The confirm step for something that cannot be undone.
 *
 * `window.confirm` could only ask a yes/no question in the OS voice; this can
 * name what will be lost and offer a way out — `extraAction` is how Restore
 * offers "back up first" in the same breath as asking.
 */
export function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  /** Say exactly what disappears. "This deletes your 4 saved attempts." */
  consequence,
  confirmLabel = "Delete",
  cancelLabel = "Cancel",
  extraAction,
  busy = false,
}: {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: ReactNode;
  consequence: ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  extraAction?: { label: string; onClick: () => void };
  busy?: boolean;
}) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      size="sm"
      footer={
        <>
          <button onClick={onClose} disabled={busy}>
            {cancelLabel}
          </button>
          <span className="spacer" />
          {extraAction && (
            <button onClick={extraAction.onClick} disabled={busy}>
              {extraAction.label}
            </button>
          )}
          <button className="danger filled" onClick={onConfirm} disabled={busy}>
            {busy ? "Working…" : confirmLabel}
          </button>
        </>
      }
    >
      <p className="modal-consequence">{consequence}</p>
    </Modal>
  );
}
