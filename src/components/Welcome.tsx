import { useNavigate } from "react-router-dom";

/** First-run welcome that orients a new user across the app's sections and points
 * them at a concrete starting point. Dismissal is persisted by the caller. */
export function Welcome({ onClose }: { onClose: () => void }) {
  const nav = useNavigate();

  const go = (to: string) => {
    onClose();
    nav(to);
  };

  const items: { icon: string; title: string; body: string }[] = [
    { icon: "📚", title: "Problem Library", body: "132 problems ordered easiest → hardest. Start at the top and work down." },
    { icon: "🧭", title: "Learning Paths", body: "Curated tracks (Foundations, Arrays, DP…) that build skills in order." },
    { icon: "🔁", title: "Revision", body: "Solved problems return on a spaced-repetition schedule so they stick." },
    { icon: "🧩", title: "Drill & 🔬 Debugger", body: "Name the pattern before coding; step through algorithms visually." },
    { icon: "⏱️", title: "Interview & 🏁 Contest", body: "Timed practice when you're ready to simulate the real thing." },
  ];

  return (
    <div className="welcome-overlay" onClick={onClose}>
      <div className="welcome-card" onClick={(e) => e.stopPropagation()}>
        <div className="row">
          <span className="logo" style={{ marginRight: 8 }}>P</span>
          <h2 style={{ margin: 0 }}>Welcome to Poodcode</h2>
          <span className="spacer" />
          <button className="ghost" onClick={onClose}>✕</button>
        </div>
        <p className="dim" style={{ marginTop: 8 }}>
          Your offline coding-interview trainer. You write a solution, it's judged against real test
          cases, and what you solve comes back for review so it sticks. Here's the lay of the land:
        </p>

        <div style={{ margin: "10px 0" }}>
          {items.map((it) => (
            <div key={it.title} className="row" style={{ alignItems: "flex-start", padding: "7px 0", gap: 10 }}>
              <span style={{ fontSize: 20, width: 26 }}>{it.icon}</span>
              <span>
                <strong>{it.title}</strong>
                <div className="dim" style={{ fontSize: 13 }}>{it.body}</div>
              </span>
            </div>
          ))}
        </div>

        <div className="card" style={{ borderColor: "var(--accent)", marginBottom: 12 }}>
          <strong>New to this?</strong>{" "}
          <span className="dim">Begin with the Foundations path or the easiest problems — they only need basic Java.</span>
        </div>

        <div className="row wrap">
          <button className="primary" onClick={() => go("/paths")}>🧭 Start with Learning Paths</button>
          <button onClick={() => go("/library")}>📚 Browse the Library</button>
          <span className="spacer" />
          <button className="ghost" onClick={onClose}>Skip for now</button>
        </div>
      </div>
    </div>
  );
}
