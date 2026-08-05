import type { Difficulty } from "../types";

export function formatDuration(seconds: number): string {
  if (!seconds || seconds < 0) return "0m";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

export function formatClock(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

export function relativeDate(iso: string | null): string {
  if (!iso) return "never";
  const d = new Date(iso.replace(" ", "T"));
  if (Number.isNaN(d.getTime())) return iso;
  const diff = (Date.now() - d.getTime()) / 86_400_000;
  if (diff < 1) return "today";
  if (diff < 2) return "yesterday";
  if (diff < 30) return `${Math.floor(diff)}d ago`;
  if (diff < 365) return `${Math.floor(diff / 30)}mo ago`;
  return `${Math.floor(diff / 365)}y ago`;
}

export const difficultyColor: Record<Difficulty, string> = {
  Intro: "var(--intro)",
  Easy: "var(--easy)",
  Medium: "var(--medium)",
  Hard: "var(--hard)",
};

export function percent(x: number): string {
  return `${Math.round(x * 100)}%`;
}

/** Format a memory reading in KiB as a compact human string, or "—" if unknown. */
export function formatMemory(kb: number | null | undefined): string {
  if (kb == null || kb <= 0) return "—";
  if (kb < 1024) return `${kb} KB`;
  return `${(kb / 1024).toFixed(1)} MB`;
}
