/**
 * Empty, error and stat states (UI_ROADMAP C3, E3, E6).
 *
 * `Empty` rendered an emoji and a sentence — "No notes yet." — and stopped
 * there, so an empty state was a dead end rather than the obvious place to
 * start. `EmptyState` takes the action that fills it. `ErrorState` is the other
 * half of a page's loading contract: a page that fails to load says what
 * failed and offers Retry, instead of sitting on "Loading…" forever (B3).
 */

import { useState, type ReactNode } from "react";
import { Icon, type IconName } from "./Icon";
import { Button } from "./Button";

export interface StateAction {
  label: string;
  onClick: () => void;
  icon?: IconName;
}

export function EmptyState({
  icon = "inbox",
  title,
  children,
  action,
  secondary,
  compact = false,
}: {
  icon?: IconName;
  title: ReactNode;
  /** A sentence of explanation under the title. */
  children?: ReactNode;
  /** The thing that fills this empty state. Nearly every empty state has one. */
  action?: StateAction;
  secondary?: StateAction;
  /** A smaller version for inside a panel or tab. */
  compact?: boolean;
}) {
  return (
    <div className={`empty-state ${compact ? "compact" : ""}`} role="status">
      <span className="empty-state-icon">
        <Icon name={icon} size={compact ? 20 : 28} strokeWidth={1.6} />
      </span>
      <p className="empty-state-title">{title}</p>
      {children && <p className="empty-state-body">{children}</p>}
      {(action || secondary) && (
        <div className="empty-state-actions">
          {action && (
            <Button variant="primary" icon={action.icon} onClick={action.onClick} size={compact ? "sm" : "md"}>
              {action.label}
            </Button>
          )}
          {secondary && (
            <Button variant="ghost" icon={secondary.icon} onClick={secondary.onClick} size={compact ? "sm" : "md"}>
              {secondary.label}
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Something failed to load. Says what, shows the error text (collapsed, and
 * copyable, because it is what a bug report needs), and offers Retry.
 */
export function ErrorState({
  title = "Something went wrong.",
  error,
  onRetry,
  compact = false,
}: {
  title?: ReactNode;
  error?: unknown;
  onRetry?: () => void;
  compact?: boolean;
}) {
  const [copied, setCopied] = useState(false);
  const detail = error === undefined || error === null ? "" : error instanceof Error ? error.message : String(error);
  return (
    <div className={`error-state card ${compact ? "compact" : ""}`} role="alert">
      <div className="error-state-head">
        <Icon name="warning" size={18} className="error-state-icon" />
        <strong>{title}</strong>
      </div>
      {detail && <p className="error-state-detail mono">{detail}</p>}
      <div className="error-state-actions">
        {onRetry && (
          <Button variant="primary" icon="refresh" size="sm" onClick={onRetry}>
            Retry
          </Button>
        )}
        {detail && (
          <Button
            variant="ghost"
            size="sm"
            icon={copied ? "copied" : "copy"}
            onClick={() => {
              navigator.clipboard?.writeText(detail).then(
                () => setCopied(true),
                () => {
                  /* clipboard refused (no focus, no permission); the text is on screen anyway */
                }
              );
            }}
          >
            {copied ? "Copied" : "Copy details"}
          </Button>
        )}
      </div>
    </div>
  );
}

/** A headline number. `hint` is a line under the label (a trend, a comparison). */
export function StatTile({
  value,
  label,
  hint,
  icon,
  aside,
}: {
  value: ReactNode;
  label: string;
  hint?: ReactNode;
  icon?: IconName;
  /** Rendered at the right of the value — a sparkline, a ring. */
  aside?: ReactNode;
}) {
  return (
    <div className="card stat-tile">
      <div className="stat-tile-top">
        <div>
          <div className="stat-value">{value}</div>
          <div className="stat-label">
            {icon && <Icon name={icon} size={12} />}
            {label}
          </div>
        </div>
        {aside}
      </div>
      {hint && <div className="stat-hint">{hint}</div>}
    </div>
  );
}
