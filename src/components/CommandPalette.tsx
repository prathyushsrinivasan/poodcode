import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useStore } from "../store";
import { api } from "../api";
import type { Problem } from "../types";

interface Cmd {
  id: string;
  label: string;
  hint?: string;
  run: () => void;
}

export function CommandPalette() {
  const open = useStore((s) => s.paletteOpen);
  const setOpen = useStore((s) => s.setPalette);
  const toggleTheme = useStore((s) => s.toggleTheme);
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [sel, setSel] = useState(0);
  const [problems, setProblems] = useState<Problem[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setQ("");
      setSel(0);
      api.listProblems().then(setProblems).catch(() => {});
      setTimeout(() => inputRef.current?.focus(), 10);
    }
  }, [open]);

  const commands = useMemo<Cmd[]>(() => {
    const nav: Cmd[] = [
      { id: "dash", label: "Go to Dashboard", run: () => navigate("/") },
      { id: "lib", label: "Go to Problem Library", run: () => navigate("/library") },
      { id: "rev", label: "Go to Revision Queue", run: () => navigate("/revision") },
      { id: "stats", label: "Go to Statistics", run: () => navigate("/stats") },
      { id: "timeline", label: "Go to Learning Timeline", run: () => navigate("/timeline") },
      { id: "random", label: "Go to Random Practice", run: () => navigate("/random") },
      { id: "companies", label: "Go to Company Prep", run: () => navigate("/companies") },
      { id: "interview", label: "Start Interview Mode", run: () => navigate("/interview") },
      { id: "settings", label: "Open Settings", run: () => navigate("/settings") },
      { id: "theme", label: "Toggle Light / Dark Theme", run: () => toggleTheme() },
    ];
    const probCmds: Cmd[] = problems.map((p) => ({
      id: `p${p.id}`,
      label: p.title,
      hint: `${p.difficulty} · ${p.topics.join(", ")}`,
      run: () => navigate(`/solve/${p.id}`),
    }));
    return [...nav, ...probCmds];
  }, [problems, navigate, toggleTheme]);

  const filtered = useMemo(() => {
    const s = q.trim().toLowerCase();
    if (!s) return commands.slice(0, 40);
    return commands
      .filter((c) => (c.label + " " + (c.hint ?? "")).toLowerCase().includes(s))
      .slice(0, 40);
  }, [q, commands]);

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
          placeholder="Search problems and commands…"
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
