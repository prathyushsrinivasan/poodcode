/**
 * Route → breadcrumb trail.
 *
 * Tauri draws no browser chrome, so the app has no back button and no address
 * bar of its own. Only four pages ever drew their own "←", which meant reaching
 * a problem from the curriculum, from Today, or from the command palette left
 * you somewhere with no way back and nothing saying where "there" was.
 *
 * This is the "where am I" half. Static segments are named from the table
 * below; dynamic ones (a unit key, a problem id, a week number) cannot be named
 * without data, so they come back as `dynamic: true` with a placeholder and the
 * page that has the data fills them in via `useCrumb`.
 */

export interface Crumb {
  label: string;
  /** Absolute path, or null for the leaf (which is where you already are). */
  href: string | null;
  /** True when the label is a placeholder waiting on page data. */
  dynamic?: boolean;
}

interface RouteNode {
  label: string;
  /** Child segments. A key of `:` matches any single segment. */
  children?: Record<string, RouteNode>;
  /** Placeholder shown for a `:` node until the page supplies a real label. */
  dynamicLabel?: string;
}

/* The shape of the app, as the nav presents it. Kept here rather than derived
   from the <Routes> tree because the two differ on purpose: `/library/unit/:key`
   is three route segments but two crumbs, since "unit" is plumbing. */
const TREE: Record<string, RouteNode> = {
  "": { label: "Today" },
  library: {
    label: "DSA Curriculum",
    children: {
      browse: { label: "Browse problems" },
      placement: { label: "Placement test" },
      unit: {
        label: "",
        children: { ":": { label: "", dynamicLabel: "Unit" } },
      },
      mixed: {
        label: "",
        children: { ":": { label: "", dynamicLabel: "Mixed set" } },
      },
    },
  },
  learn: {
    label: "Learn",
    children: { ":": { label: "", dynamicLabel: "Lesson" } },
  },
  course: {
    label: "TypeScript Course",
    children: { ":": { label: "", dynamicLabel: "Week" } },
  },
  "java-course": {
    label: "Java Course",
    children: { ":": { label: "", dynamicLabel: "Module" } },
  },
  backend: {
    label: "Backend Lab",
    children: { ":": { label: "", dynamicLabel: "Project" } },
  },
  projects: {
    label: "Projects",
    children: {
      ":": {
        label: "",
        dynamicLabel: "Project",
        children: {
          reference: { label: "Handbook" },
          history: { label: "Build history" },
          workbench: { label: "Workbench" },
          review: { label: "Review" },
          ":": { label: "", dynamicLabel: "Module" },
        },
      },
    },
  },
  mastery: { label: "6-Month Mastery" },
  flashcards: { label: "Flashcards" },
  "ts-errors": { label: "TypeScript errors" },
  contest: {
    label: "Checkpoint",
    children: { ":": { label: "", dynamicLabel: "Checkpoint" } },
  },
  "jp-bridge": { label: "日本語 → Java" },
  paths: { label: "Learning Paths" },
  settings: { label: "Settings" },
  ui: { label: "Component gallery" },
  solve: {
    label: "",
    children: { ":": { label: "", dynamicLabel: "Problem" } },
  },
  problem: {
    label: "",
    children: {
      new: { label: "New problem" },
      ":": {
        label: "",
        dynamicLabel: "Problem",
        children: { edit: { label: "Edit" } },
      },
    },
  },
};

/** Split a path into its non-empty segments. */
export function segments(pathname: string): string[] {
  return pathname.split("/").filter(Boolean);
}

/**
 * Build the trail for a path.
 *
 * Always starts at Today, so there is a way home from anywhere. A node with an
 * empty label contributes no crumb of its own — that is how `/solve/12` becomes
 * "Today › Problem" rather than "Today › solve › 12".
 */
export function breadcrumb(pathname: string): Crumb[] {
  const parts = segments(pathname);
  const out: Crumb[] = [{ label: "Today", href: parts.length === 0 ? null : "/" }];
  if (parts.length === 0) return out;

  let level: Record<string, RouteNode> | undefined = TREE;
  let href = "";

  for (let i = 0; i < parts.length; i++) {
    const part = parts[i];
    if (!level) break;
    const node: RouteNode | undefined = level[part] ?? level[":"];
    if (!node) break;

    const isWildcard = !level[part] && !!level[":"];
    href += `/${part}`;
    const last = i === parts.length - 1;

    if (isWildcard) {
      out.push({
        label: node.dynamicLabel || part,
        href: last ? null : href,
        dynamic: true,
      });
    } else if (node.label) {
      out.push({ label: node.label, href: last ? null : href });
    }

    level = node.children;
  }

  // Whatever the trail ends on is where we are, so it is never a link.
  if (out.length > 0) out[out.length - 1].href = null;
  return out;
}

/** Replace the last dynamic crumb's placeholder with a real label.
 *
 * Pages know their own title long after the router does, so the trail renders
 * with "Problem" and sharpens to "Count Inversions" when the fetch lands. */
export function withLeafLabel(crumbs: Crumb[], label: string | null): Crumb[] {
  if (!label) return crumbs;
  const i = crumbs.map((c) => !!c.dynamic).lastIndexOf(true);
  if (i === -1) return crumbs;
  const copy = crumbs.slice();
  copy[i] = { ...copy[i], label, dynamic: false };
  return copy;
}
