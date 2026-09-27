/**
 * Buttons (UI_ROADMAP C3).
 *
 * The app's buttons were a raw `<button className=…>` everywhere, each page
 * choosing its own spacing between an emoji and a word, and "loading" meant
 * swapping the label for "Running…" by hand. This is one button with the
 * variants the stylesheet already had, an icon slot, a size, and a loading
 * state that keeps the button's width so a toolbar does not jump.
 *
 * `IconButton` is the icon-only case, and it *requires* a label: an unlabelled
 * ✕ or ↻ is announced as "button" and nothing else (D9). The label doubles as
 * the tooltip, with the keyboard shortcut beside it when there is one (D8).
 */

import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from "react";
import { Icon, type IconName } from "./Icon";

export type ButtonVariant = "secondary" | "primary" | "ghost" | "success" | "danger" | "danger-filled";
export type ButtonSize = "sm" | "md";

interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "children"> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: IconName;
  iconRight?: IconName;
  /** Disables the button and shows a spinner in the icon slot. */
  loading?: boolean;
  /** A shortcut shown in the tooltip, e.g. "Ctrl+Enter". */
  shortcut?: string;
  children?: ReactNode;
}

function variantClass(v: ButtonVariant): string {
  switch (v) {
    case "secondary":
      return "";
    case "danger-filled":
      return "danger filled";
    default:
      return v;
  }
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    variant = "secondary",
    size = "md",
    icon,
    iconRight,
    loading = false,
    shortcut,
    className = "",
    title,
    disabled,
    type = "button",
    children,
    ...rest
  },
  ref
) {
  const tip = title ?? undefined;
  return (
    <button
      ref={ref}
      type={type}
      className={`btn ${variantClass(variant)} ${size === "sm" ? "btn-sm" : ""} ${className}`.trim()}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      aria-keyshortcuts={shortcut ? toAriaShortcut(shortcut) : undefined}
      title={shortcut ? `${tip ?? textOf(children)} (${shortcut})`.trim() : tip}
      {...rest}
    >
      {loading ? (
        <span className="btn-spinner" aria-hidden />
      ) : (
        icon && <Icon name={icon} size={size === "sm" ? 14 : 16} />
      )}
      {children !== undefined && children !== null && children !== false && (
        <span className="btn-label">{children}</span>
      )}
      {iconRight && <Icon name={iconRight} size={size === "sm" ? 14 : 16} />}
    </button>
  );
});

/** An icon-only button. `label` is required: it is the accessible name and the tooltip. */
export const IconButton = forwardRef<
  HTMLButtonElement,
  Omit<ButtonProps, "children" | "icon" | "iconRight"> & { icon: IconName; label: string }
>(function IconButton({ icon, label, shortcut, variant = "ghost", size = "md", className = "", type = "button", ...rest }, ref) {
  return (
    <button
      ref={ref}
      type={type}
      className={`btn icon-btn ${variantClass(variant)} ${size === "sm" ? "btn-sm" : ""} ${className}`.trim()}
      aria-label={label}
      aria-keyshortcuts={shortcut ? toAriaShortcut(shortcut) : undefined}
      title={shortcut ? `${label} (${shortcut})` : label}
      {...rest}
    >
      <Icon name={icon} size={size === "sm" ? 14 : 16} />
    </button>
  );
});

/** "Ctrl+Shift+Enter" → "Control+Shift+Enter", the form aria-keyshortcuts wants. */
function toAriaShortcut(s: string): string {
  return s
    .split("+")
    .map((k) => (k === "Ctrl" ? "Control" : k === "⌘" || k === "Cmd" ? "Meta" : k))
    .join("+");
}

function textOf(node: ReactNode): string {
  if (typeof node === "string" || typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(textOf).join("");
  return "";
}
