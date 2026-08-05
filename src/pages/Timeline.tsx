import { useEffect, useState } from "react";
import { api } from "../api";
import type { Stats } from "../types";
import { Chart, PALETTE } from "../components/Charts";

// Learning recommendations keyed by topic — surfaced when a topic is weak.
const RECOMMENDATIONS: Record<string, string[]> = {
  Graphs: ["BFS", "DFS", "Topological Sort", "Union-Find", "Dijkstra"],
  "Dynamic Programming": ["Fibonacci", "Climbing Stairs", "House Robber", "Coin Change", "LIS"],
  Hashing: ["Frequency maps", "Complement lookup", "Grouping by canonical key"],
  "Sliding Window": ["Fixed vs variable windows", "Two-pointer contraction"],
  "Binary Search": ["Lower/upper bound", "Search on answer"],
  Strings: ["Two pointers", "Frequency counting", "Prefix hashing"],
  Arrays: ["Prefix sums", "Kadane", "In-place manipulation"],
  Stack: ["Monotonic stack", "Matching pairs"],
  Math: ["Number theory basics", "Modular arithmetic"],
  "Two Pointers": ["Opposite ends", "Fast/slow pointers"],
  Matrix: ["Flood fill", "Directional traversal"],
};

export default function Timeline() {
  const [s, setS] = useState<Stats | null>(null);
  useEffect(() => {
    api.statistics().then(setS);
  }, []);
  if (!s) return <div className="page">Loading…</div>;

  const masteredTopics = s.by_topic.filter((t) => t.total > 0 && t.solved === t.total && t.avg_confidence >= 4);

  return (
    <div className="page">
      <h1 className="page-title">Learning Timeline</h1>
      <p className="page-sub">Your trajectory and what to focus on next.</p>

      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ marginTop: 0 }}>Problems solved per month</h3>
        <Chart
          option={{
            tooltip: { trigger: "axis" },
            xAxis: { type: "category", data: s.monthly_activity.map((m) => m.label) },
            yAxis: { type: "value" },
            series: [{ type: "bar", data: s.monthly_activity.map((m) => m.value), itemStyle: { color: PALETTE[0] } }],
          }}
        />
      </div>

      <div className="grid cols-2">
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Topics mastered</h3>
          {masteredTopics.length === 0 ? (
            <div className="dim">Keep going — master a topic by solving all its problems with high confidence.</div>
          ) : (
            <div className="tag-row">
              {masteredTopics.map((t) => (
                <span key={t.topic} className="badge" style={{ borderColor: "var(--good)", color: "var(--good)" }}>
                  ✓ {t.topic}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <h3 style={{ marginTop: 0 }}>Overall</h3>
          <div className="row" style={{ padding: "4px 0" }}>
            <span>Problems solved</span>
            <span className="spacer" />
            <strong>{s.total_solved}</strong>
          </div>
          <div className="row" style={{ padding: "4px 0" }}>
            <span>Topics touched</span>
            <span className="spacer" />
            <strong>{s.by_topic.filter((t) => t.solved > 0).length}</strong>
          </div>
          <div className="row" style={{ padding: "4px 0" }}>
            <span>Longest streak</span>
            <span className="spacer" />
            <strong>{s.longest_streak} days</strong>
          </div>
        </div>
      </div>

      <h3 style={{ marginTop: 22 }}>Recommendations</h3>
      {s.weakest_topics.length === 0 ? (
        <div className="dim">Solve a few problems to unlock personalized recommendations.</div>
      ) : (
        s.weakest_topics.slice(0, 4).map((t) => (
          <div key={t.topic} className="card" style={{ marginBottom: 10 }}>
            <div className="row">
              <strong>You could strengthen: {t.topic}</strong>
              <span className="spacer" />
              <span className="dim">{t.solved}/{t.total} solved · confidence {t.avg_confidence.toFixed(1)}/5</span>
            </div>
            {RECOMMENDATIONS[t.topic] && (
              <div className="tag-row" style={{ marginTop: 8 }}>
                <span className="dim" style={{ fontSize: 12 }}>Practice:</span>
                {RECOMMENDATIONS[t.topic].map((r) => (
                  <span key={r} className="badge tag">{r}</span>
                ))}
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}
