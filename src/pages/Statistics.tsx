import { useEffect, useState } from "react";
import { api } from "../api";
import type { Stats } from "../types";
import { Chart, PALETTE } from "../components/Charts";
import { Stat } from "../components/common";
import { formatDuration, percent } from "../lib/format";

function Heatmap({ cells }: { cells: { date: string; count: number }[] }) {
  const max = Math.max(1, ...cells.map((c) => c.count));
  const color = (c: number) => {
    if (c <= 0) return "var(--bg-elev-2)";
    const intensity = Math.min(1, c / max);
    return `color-mix(in srgb, var(--accent) ${20 + intensity * 80}%, transparent)`;
  };
  return (
    <div className="heatmap">
      {cells.map((c) => (
        <div
          key={c.date}
          className="heat-cell"
          title={`${c.date}: ${c.count} solved`}
          style={{ background: color(c.count) }}
        />
      ))}
    </div>
  );
}

export default function Statistics() {
  const [s, setS] = useState<Stats | null>(null);
  useEffect(() => {
    api.statistics().then(setS);
  }, []);
  if (!s) return <div className="page">Loading…</div>;

  const diffData = ["Intro", "Easy", "Medium", "Hard"].map((d) => ({
    name: d,
    solved: s.by_difficulty[d]?.solved ?? 0,
    total: s.by_difficulty[d]?.total ?? 0,
  }));

  return (
    <div className="page page-wide">
      <h1 className="page-title">Statistics</h1>
      <p className="page-sub">Your overall progress and patterns.</p>

      <div className="grid cols-4" style={{ marginBottom: 16 }}>
        <Stat value={`${s.total_solved}/${s.total_problems}`} label="Solved" />
        <Stat value={formatDuration(s.avg_solve_seconds)} label="Avg solve time" />
        <Stat value={percent(s.acceptance_rate)} label="Acceptance rate" />
        <Stat value={`${s.current_streak}🔥 / ${s.longest_streak}`} label="Streak (cur / best)" />
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ marginTop: 0 }}>Learning outcomes</h3>
        <p className="faint" style={{ fontSize: 12, marginTop: 0 }}>
          Behavioral signals — what actually happened, not self-report.
        </p>
        <div className="grid cols-4">
          <Stat value={percent(s.first_attempt_rate)} label="First-try solve rate" />
          <Stat value={s.avg_tries_to_solve.toFixed(1)} label="Avg tries to solve" />
          <Stat value={s.reviews_total > 0 ? percent(s.retention_rate) : "—"} label="Review retention" />
          <Stat value={s.reviews_total} label="Reviews graded" />
        </div>
      </div>

      {s.topic_behavior.length > 0 && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3 style={{ marginTop: 0 }}>Behavioral mastery by topic</h3>
          <p className="faint" style={{ fontSize: 12, marginTop: 0 }}>
            Derived from first-attempt accuracy and hint dependence — weakest first.
          </p>
          {s.topic_behavior.slice(0, 8).map((t) => (
            <div key={t.topic} className="row" style={{ padding: "5px 0", alignItems: "center" }}>
              <span style={{ width: 160 }}>{t.topic}</span>
              <div className="progress" style={{ flex: 1 }}>
                <span
                  style={{
                    width: `${Math.round(t.mastery * 100)}%`,
                    background: t.mastery >= 0.66 ? "var(--good)" : t.mastery >= 0.33 ? "var(--accent)" : "var(--bad)",
                  }}
                />
              </div>
              <span className="dim mono" style={{ width: 200, textAlign: "right" }}>
                {percent(t.first_try_rate)} first-try · {t.avg_hints_used.toFixed(1)} hints
              </span>
            </div>
          ))}
        </div>
      )}

      {s.mistake_tally.length > 0 && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3 style={{ marginTop: 0 }}>Your top mistake types</h3>
          <div className="tag-row">
            {s.mistake_tally.map((m) => (
              <span key={m.label} className="badge" style={{ color: "var(--bad)", borderColor: "var(--bad)" }}>
                {m.label} · {m.value}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ marginTop: 0 }}>Activity (last 26 weeks)</h3>
        <Heatmap cells={s.heatmap} />
      </div>

      <div className="grid cols-2">
        <div className="card">
          <h3 style={{ marginTop: 0 }}>By difficulty</h3>
          <Chart
            option={{
              tooltip: { trigger: "axis" },
              legend: { textStyle: { color: "inherit" }, top: 0 },
              xAxis: { type: "category", data: diffData.map((d) => d.name) },
              yAxis: { type: "value" },
              series: [
                { name: "Solved", type: "bar", stack: "x", data: diffData.map((d) => d.solved), itemStyle: { color: PALETTE[1] } },
                {
                  name: "Unsolved",
                  type: "bar",
                  stack: "x",
                  data: diffData.map((d) => d.total - d.solved),
                  itemStyle: { color: "var(--bg-elev-2)" },
                },
              ],
            }}
          />
        </div>

        <div className="card">
          <h3 style={{ marginTop: 0 }}>Language usage</h3>
          {s.language_usage.length === 0 ? (
            <div className="dim">No submissions yet.</div>
          ) : (
            <Chart
              option={{
                series: [
                  {
                    type: "pie",
                    radius: ["40%", "70%"],
                    data: s.language_usage.map((l) => ({ name: l.label, value: l.value })),
                    label: { color: "inherit" },
                  },
                ],
              }}
            />
          )}
        </div>

        <div className="card">
          <h3 style={{ marginTop: 0 }}>Solved per topic</h3>
          <Chart
            height={Math.max(220, s.by_topic.length * 26)}
            option={{
              tooltip: { trigger: "axis" },
              xAxis: { type: "value" },
              yAxis: { type: "category", data: s.by_topic.map((t) => t.topic) },
              series: [
                { name: "Solved", type: "bar", data: s.by_topic.map((t) => t.solved), itemStyle: { color: PALETTE[0] } },
              ],
            }}
          />
        </div>

        <div className="card">
          <h3 style={{ marginTop: 0 }}>Monthly activity</h3>
          <Chart
            option={{
              tooltip: { trigger: "axis" },
              xAxis: { type: "category", data: s.monthly_activity.map((m) => m.label) },
              yAxis: { type: "value" },
              series: [
                { type: "line", smooth: true, areaStyle: {}, data: s.monthly_activity.map((m) => m.value), itemStyle: { color: PALETTE[2] } },
              ],
            }}
          />
        </div>
      </div>

      <div className="grid cols-2" style={{ marginTop: 16 }}>
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Weakest topics</h3>
          {s.weakest_topics.map((t) => (
            <div key={t.topic} className="row" style={{ padding: "5px 0" }}>
              <span>{t.topic}</span>
              <span className="spacer" />
              <span className="dim">{t.solved}/{t.total} · conf {t.avg_confidence.toFixed(1)}</span>
            </div>
          ))}
          {s.weakest_topics.length === 0 && <div className="dim">Not enough data yet.</div>}
        </div>
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Strongest topics</h3>
          {s.strongest_topics.map((t) => (
            <div key={t.topic} className="row" style={{ padding: "5px 0" }}>
              <span>{t.topic}</span>
              <span className="spacer" />
              <span className="dim">{t.solved}/{t.total} · conf {t.avg_confidence.toFixed(1)}</span>
            </div>
          ))}
          {s.strongest_topics.length === 0 && <div className="dim">Not enough data yet.</div>}
        </div>
      </div>
    </div>
  );
}
