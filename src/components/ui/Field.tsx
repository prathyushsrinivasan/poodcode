/**
 * Form controls (UI_ROADMAP C3).
 *
 * Settings had its own local `Field` and `Toggle`; the problem form, Projects
 * and the course pages used bare checkboxes and inputs with a `<div>` of text
 * near them and no `<label>` tying the two together. These are the shared
 * versions: a labelled row with a hint and an inline error (H3 wants
 * validation beside the field, not in a toast), a switch, a segmented choice
 * and a number input that clamps.
 */

import { useId, type ReactNode } from "react";

/**
 * A labelled control. The label is a real `<label htmlFor>` for the control
 * rendered through `children(id)`; for a control that labels itself (a switch,
 * a segmented group) pass a node instead and the text is associated by
 * `aria-labelledby`.
 */
export function Field({
  label,
  hint,
  error,
  children,
  layout = "row",
}: {
  label: ReactNode;
  hint?: ReactNode;
  error?: ReactNode;
  children: ReactNode | ((id: string, describedBy: string | undefined) => ReactNode);
  /** `row` puts the control at the right (settings); `stack` puts it under the label (forms). */
  layout?: "row" | "stack";
}) {
  const id = useId();
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  const describedBy = [hintId, errorId].filter(Boolean).join(" ") || undefined;
  const control = typeof children === "function" ? children(id, describedBy) : children;
  return (
    <div className={`field field-${layout} ${error ? "has-error" : ""}`}>
      <div className="field-label">
        {typeof children === "function" ? (
          <label htmlFor={id}>{label}</label>
        ) : (
          <span id={`${id}-label`}>{label}</span>
        )}
        {hint && (
          <span className="field-hint" id={hintId}>
            {hint}
          </span>
        )}
      </div>
      <div className="field-control">
        {control}
        {error && (
          <span className="field-error" id={errorId} role="alert">
            {error}
          </span>
        )}
      </div>
    </div>
  );
}

/** An on/off switch, for booleans that were bare checkboxes. */
export function Toggle({
  checked,
  onChange,
  label,
  disabled,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  /** The accessible name — the switch has no visible text of its own. */
  label: string;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      disabled={disabled}
      className={`toggle ${checked ? "on" : ""}`}
      onClick={() => onChange(!checked)}
    >
      <span className="toggle-knob" aria-hidden />
    </button>
  );
}

/** A segmented choice — clearer than a select for two to four options. */
export function Segmented<T extends string>({
  value,
  options,
  onChange,
  label,
}: {
  value: T;
  options: { value: T; label: ReactNode }[];
  onChange: (v: T) => void;
  label: string;
}) {
  return (
    <div className="pill-toggle" role="group" aria-label={label}>
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          className={`pill ${value === o.value ? "on" : ""}`}
          aria-pressed={value === o.value}
          onClick={() => onChange(o.value)}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

/** A number input that clamps to [min, max] and never emits NaN. */
export function NumberInput({
  value,
  onChange,
  min,
  max,
  step = 1,
  id,
  label,
  describedBy,
}: {
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
  step?: number;
  id?: string;
  /** Needed when there is no `<label htmlFor>` pointing at it. */
  label?: string;
  describedBy?: string;
}) {
  return (
    <input
      id={id}
      type="number"
      className="number-input"
      value={Number.isFinite(value) ? value : ""}
      min={min}
      max={max}
      step={step}
      aria-label={label}
      aria-describedby={describedBy}
      onChange={(e) => {
        const n = e.target.valueAsNumber;
        if (!Number.isFinite(n)) return;
        let v = n;
        if (min !== undefined) v = Math.max(min, v);
        if (max !== undefined) v = Math.min(max, v);
        onChange(v);
      }}
    />
  );
}
