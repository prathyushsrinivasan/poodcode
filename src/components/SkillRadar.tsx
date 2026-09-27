// The skill radar (TS_MASTERY_ROADMAP X-69): six kinds of work, each axis the
// share of that kind solved so far. See `skillProfile` in lib/mastery.ts.

import type { Skill } from "../lib/mastery";

export function SkillRadar({ skills, size = 220 }: { skills: Skill[]; size?: number }) {
  const c = size / 2;
  const r = size / 2 - 42;
  const n = skills.length;
  const at = (i: number, frac: number) => {
    const angle = -Math.PI / 2 + (2 * Math.PI * i) / n;
    return [c + Math.cos(angle) * r * frac, c + Math.sin(angle) * r * frac] as const;
  };
  const polygon = (frac: (i: number) => number) =>
    skills.map((_, i) => at(i, frac(i)).map((v) => v.toFixed(1)).join(",")).join(" ");
  const share = (s: Skill) => (s.total === 0 ? 0 : s.done / s.total);

  return (
    <figure className="skill-radar m-0">
      <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size} role="img" aria-label="Skill radar">
        {[0.25, 0.5, 0.75, 1].map((f) => (
          <polygon key={f} points={polygon(() => f)} fill="none" stroke="var(--border)" strokeWidth={1} />
        ))}
        {skills.map((_, i) => {
          const [x, y] = at(i, 1);
          return <line key={i} x1={c} y1={c} x2={x} y2={y} stroke="var(--border)" strokeWidth={1} />;
        })}
        <polygon
          points={polygon((i) => Math.max(0.02, share(skills[i]!)))}
          fill="color-mix(in srgb, var(--accent) 30%, transparent)"
          stroke="var(--accent)"
          strokeWidth={2}
        />
        {skills.map((s, i) => {
          const [x, y] = at(i, 1.22);
          return (
            <text key={s.label} x={x} y={y} textAnchor="middle" dominantBaseline="middle" className="skill-label">
              {s.label}
            </text>
          );
        })}
      </svg>
      <figcaption className="dim quiz-note">
        {skills.map((s) => `${s.label} ${s.done}/${s.total}`).join(" · ")}
      </figcaption>
    </figure>
  );
}
