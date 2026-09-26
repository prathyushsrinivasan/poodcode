// A state machine drawn as a graph (M3-03): states on a circle, one arrow per
// transition. The start state (the union's first member) is ringed; terminal
// states are dashed; states the start cannot reach are marked in red.
import { analyseMachine, type Machine } from "../lib/stateMachine";

const W = 420;
const H = 300;
const R = 30;

export function StateDiagram({ machine }: { machine: Machine }) {
  const { terminal, unreachable } = analyseMachine(machine);
  const n = machine.states.length;
  const cx = W / 2;
  const cy = H / 2;
  const ring = Math.min(W, H) / 2 - R - 14;
  const pos = new Map(
    machine.states.map((s, i) => {
      const a = (i / n) * 2 * Math.PI - Math.PI / 2;
      return [s, { x: cx + ring * Math.cos(a), y: cy + ring * Math.sin(a) }] as const;
    })
  );
  const markerId = `sm-arrow-${machine.name}`;
  const twoWay = new Set(machine.edges.map(([a, b]) => `${a}\u0000${b}`));

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      width="100%"
      role="img"
      aria-label={`${machine.name}: ${machine.edges.map(([a, b]) => `${a} to ${b}`).join(", ")}`}
      style={{ maxWidth: W }}
    >
      <defs>
        <marker id={markerId} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="var(--text-faint)" />
        </marker>
      </defs>
      {machine.edges.map(([a, b], i) => {
        const p = pos.get(a)!;
        const q = pos.get(b)!;
        if (a === b) {
          return (
            <path
              key={i}
              d={`M${p.x - 10},${p.y - R + 2} C${p.x - 30},${p.y - R - 34} ${p.x + 30},${p.y - R - 34} ${p.x + 10},${p.y - R + 2}`}
              fill="none"
              stroke="var(--text-faint)"
              markerEnd={`url(#${markerId})`}
            />
          );
        }
        const dx = q.x - p.x;
        const dy = q.y - p.y;
        const len = Math.hypot(dx, dy) || 1;
        const ux = dx / len;
        const uy = dy / len;
        // A pair of opposite edges bends apart so both arrows stay visible.
        const bend = twoWay.has(`${b}\u0000${a}`) ? 18 : 0;
        const sx = p.x + ux * R;
        const sy = p.y + uy * R;
        const ex = q.x - ux * (R + 2);
        const ey = q.y - uy * (R + 2);
        const mx = (sx + ex) / 2 - uy * bend;
        const my = (sy + ey) / 2 + ux * bend;
        return (
          <path
            key={i}
            d={`M${sx},${sy} Q${mx},${my} ${ex},${ey}`}
            fill="none"
            stroke="var(--text-faint)"
            strokeWidth={1.5}
            markerEnd={`url(#${markerId})`}
          />
        );
      })}
      {machine.states.map((s, i) => {
        const p = pos.get(s)!;
        const bad = unreachable.includes(s);
        return (
          <g key={s}>
            {i === 0 && <circle cx={p.x} cy={p.y} r={R + 5} fill="none" stroke="var(--accent)" />}
            <circle
              cx={p.x}
              cy={p.y}
              r={R}
              fill="var(--bg-elev-2)"
              stroke={bad ? "var(--bad)" : "var(--accent)"}
              strokeDasharray={terminal.includes(s) ? "4 3" : undefined}
              strokeWidth={1.5}
            />
            <text
              x={p.x}
              y={p.y + 4}
              textAnchor="middle"
              fontSize={s.length > 8 ? 9 : 11}
              fill={bad ? "var(--bad)" : "var(--text)"}
              fontFamily="var(--font-mono)"
            >
              {s}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
