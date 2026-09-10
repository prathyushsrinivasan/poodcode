import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useStore } from "../store";
import { api } from "../api";
import type { BackendTrack, Problem, ProjectTrack, WeeklyCourse } from "../types";

interface Cmd {
  id: string;
  label: string;
  hint?: string;
  run: () => void;
}

/** The units of the four content tracks, so search can reach a course week or a
 * project module and not just the page it lives on. Loaded on the palette's
 * first open and kept — the seeds are embedded in the binary and never change
 * while the app is running. */
type Tracks = {
  ts: WeeklyCourse | null;
  java: WeeklyCourse | null;
  backend: BackendTrack | null;
  projects: ProjectTrack | null;
};

const NO_TRACKS: Tracks = { ts: null, java: null, backend: null, projects: null };

/** One command per authored unit of a weekly course. Units are addressed by
 * number, which is what `/course/:week` expects. */
function courseCmds(
  course: WeeklyCourse | null,
  route: string,
  navigate: (to: string) => void
): Cmd[] {
  if (!course) return [];
  const unit = course.unit_label || "Week";
  return course.weeks
    .filter((w) => w.authored)
    .map((w) => ({
      id: `${route}-${w.number}`,
      label: `${unit} ${w.number}. ${w.theme}`,
      hint: course.title,
      run: () => navigate(`${route}/${w.number}`),
    }));
}

export function CommandPalette() {
  const open = useStore((s) => s.paletteOpen);
  const setOpen = useStore((s) => s.setPalette);
  const toggleTheme = useStore((s) => s.toggleTheme);
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [sel, setSel] = useState(0);
  const [problems, setProblems] = useState<Problem[]>([]);
  const [tracks, setTracks] = useState<Tracks>(NO_TRACKS);
  const tracksRequested = useRef(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) return;
    setQ("");
    setSel(0);
    api.listProblems().then(setProblems).catch(() => {});
    setTimeout(() => inputRef.current?.focus(), 10);

    // Track content is fetched once per session, and each failure is swallowed
    // on its own: a track that will not load costs you its entries, not the
    // palette.
    if (tracksRequested.current) return;
    tracksRequested.current = true;
    const put = <K extends keyof Tracks>(k: K) => (v: Tracks[K]) =>
      setTracks((t) => ({ ...t, [k]: v }));
    api.tsCourse().then(put("ts")).catch(() => {});
    api.javaCourse().then(put("java")).catch(() => {});
    api.backendTrack().then(put("backend")).catch(() => {});
    api.projectsTrack().then(put("projects")).catch(() => {});
  }, [open]);

  const navCmds = useMemo<Cmd[]>(
    () => [
      { id: "dash", label: "Go to Dashboard", run: () => navigate("/") },
      { id: "lib", label: "Go to Problem Library", run: () => navigate("/library") },
      { id: "learn", label: "Go to Learn", run: () => navigate("/learn") },
      { id: "course", label: "Open the TypeScript Course", run: () => navigate("/course") },
      { id: "java-course", label: "Open the Java Course", run: () => navigate("/java-course") },
      { id: "backend", label: "Open the Backend Lab", run: () => navigate("/backend") },
      { id: "projects", label: "Open Projects", run: () => navigate("/projects") },
      { id: "mastery", label: "Go to 6-Month Mastery", run: () => navigate("/mastery") },
      { id: "settings", label: "Open Settings", run: () => navigate("/settings") },
      { id: "theme", label: "Toggle Light / Dark Theme", run: () => toggleTheme() },
    ],
    [navigate, toggleTheme]
  );

  const probCmds = useMemo<Cmd[]>(
    () =>
      problems.map((p) => ({
        id: `p${p.id}`,
        label: p.title,
        hint: `${p.difficulty} · ${p.topics.join(", ")}`,
        run: () => navigate(`/solve/${p.id}`),
      })),
    [problems, navigate]
  );

  const trackCmds = useMemo<Cmd[]>(
    () => [
      ...courseCmds(tracks.ts, "/course", navigate),
      ...courseCmds(tracks.java, "/java-course", navigate),
      ...(tracks.backend?.projects ?? [])
        .filter((p) => p.authored)
        .map((p) => ({
          id: `backend-${p.key}`,
          label: `${p.number}. ${p.title}`,
          hint: `Backend Lab · ${p.tagline}`,
          run: () => navigate(`/backend/${p.key}`),
        })),
      ...(tracks.projects?.projects ?? []).flatMap((pr) =>
        (pr.modules ?? [])
          .filter((m) => m.authored)
          .map((m) => ({
            id: `module-${pr.key}-${m.key}`,
            label: `Module ${m.number}. ${m.title}`,
            hint: `${pr.title} · ${m.what}`,
            run: () => navigate(`/projects/${pr.key}/${m.key}`),
          }))
      ),
    ],
    [tracks, navigate]
  );

  const filtered = useMemo(() => {
    const s = q.trim().toLowerCase();
    // With nothing typed the palette is a shortcut list, so it stays what it
    // always was: the pages, then the problems. Track units are hundreds of
    // entries and would push everything else past the 40-row cut — they are
    // what you search *for*, not what you browse.
    if (!s) return [...navCmds, ...probCmds].slice(0, 40);
    return [...navCmds, ...trackCmds, ...probCmds]
      .filter((c) => (c.label + " " + (c.hint ?? "")).toLowerCase().includes(s))
      .slice(0, 40);
  }, [q, navCmds, probCmds, trackCmds]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen(!useStore.getState().paletteOpen);
      } else if (e.key === "Escape") {
        setOpen(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [setOpen]);

  if (!open) return null;

  const choose = (c?: Cmd) => {
    if (!c) return;
    setOpen(false);
    c.run();
  };

  return (
    <div className="palette-overlay" onClick={() => setOpen(false)}>
      <div className="palette" onClick={(e) => e.stopPropagation()}>
        <input
          ref={inputRef}
          placeholder="Search problems, lessons, modules and commands…"
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setSel(0);
          }}
          onKeyDown={(e) => {
            if (e.key === "ArrowDown") {
              e.preventDefault();
              setSel((s) => Math.min(s + 1, filtered.length - 1));
            } else if (e.key === "ArrowUp") {
              e.preventDefault();
              setSel((s) => Math.max(s - 1, 0));
            } else if (e.key === "Enter") {
              choose(filtered[sel]);
            }
          }}
        />
        <div className="palette-list">
          {filtered.map((c, i) => (
            <div
              key={c.id}
              className={`palette-item ${i === sel ? "sel" : ""}`}
              onMouseEnter={() => setSel(i)}
              onClick={() => choose(c)}
            >
              <span>{c.label}</span>
              {c.hint && <span className="dim" style={{ fontSize: 12 }}>&nbsp;— {c.hint}</span>}
            </div>
          ))}
          {filtered.length === 0 && <div className="palette-item dim">No matches</div>}
        </div>
      </div>
    </div>
  );
}
