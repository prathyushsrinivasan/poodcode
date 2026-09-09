import { useEffect, useState } from "react";
import { NavLink, Route, Routes, useNavigate } from "react-router-dom";
import { useStore } from "./store";
import { api } from "./api";
import { ToastProvider } from "./components/Toast";
import { CommandPalette } from "./components/CommandPalette";
import { Welcome } from "./components/Welcome";

import Dashboard from "./pages/Dashboard";
import Library from "./pages/Library";
import Solve from "./pages/Solve";
import Settings from "./pages/Settings";
import ProblemForm from "./pages/ProblemForm";
import Learn from "./pages/Learn";
import Course, { JavaCourse } from "./pages/Course";
import Backend from "./pages/Backend";
import Projects from "./pages/Projects";
import Mastery from "./pages/Mastery";
import JapaneseBridge from "./pages/JapaneseBridge";
import Paths from "./pages/Paths";

const NAV = [
  { section: "Practice" },
  { to: "/", label: "Dashboard", icon: "🏠", end: true },
  { to: "/library", label: "Problem Library", icon: "📚" },
  { to: "/learn", label: "Learn", icon: "📘" },
  { to: "/course", label: "TypeScript Course", icon: "📗" },
  { to: "/java-course", label: "Java Course", icon: "☕" },
  { to: "/backend", label: "Backend Lab", icon: "🛠️" },
  { to: "/projects", label: "Projects", icon: "🧱" },
  { to: "/mastery", label: "6-Month Mastery", icon: "🎓" },
  { to: "/jp-bridge", label: "日本語 → Java", icon: "🈁" },
  { to: "/paths", label: "Learning Paths", icon: "🧭" },
  { section: "App" },
  { to: "/settings", label: "Settings", icon: "⚙️" },
];

function Sidebar() {
  const setPalette = useStore((s) => s.setPalette);
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="logo">P</span> Poodcode
      </div>
      <button className="ghost" style={{ justifyContent: "flex-start", marginBottom: 6 }} onClick={() => setPalette(true)}>
        🔎 Search… <span className="kbd" style={{ marginLeft: "auto" }}>Ctrl K</span>
      </button>
      {NAV.map((item, i) =>
        "section" in item ? (
          <div key={i} className="nav-section">
            {item.section}
          </div>
        ) : (
          <NavLink
            key={item.to}
            to={item.to!}
            end={(item as any).end}
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <span className="ico">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        )
      )}
      <div className="spacer" />
      <div className="faint" style={{ fontSize: 11, padding: "8px 10px" }}>
        Offline · local-first
      </div>
    </aside>
  );
}

export default function App() {
  const init = useStore((s) => s.init);
  const loaded = useStore((s) => s.loaded);
  const [showWelcome, setShowWelcome] = useState(false);

  useEffect(() => {
    init();
  }, [init]);

  // First-run onboarding: show the welcome unless it's been dismissed before.
  useEffect(() => {
    api
      .getSettings()
      .then((s) => {
        if (s.onboarded !== "1") setShowWelcome(true);
      })
      .catch(() => {});
  }, []);

  const dismissWelcome = () => {
    setShowWelcome(false);
    api.setSetting("onboarded", "1").catch(() => {});
  };

  if (!loaded) {
    return <div className="empty" style={{ paddingTop: "20vh" }}>Loading Poodcode…</div>;
  }

  return (
    <ToastProvider>
      <div className="app">
        <Sidebar />
        <main className="main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/library" element={<Library />} />
            <Route path="/learn" element={<Learn />} />
            <Route path="/learn/:key" element={<Learn />} />
            <Route path="/course" element={<Course />} />
            <Route path="/course/:week" element={<Course />} />
            <Route path="/java-course" element={<JavaCourse />} />
            <Route path="/java-course/:week" element={<JavaCourse />} />
            <Route path="/backend" element={<Backend />} />
            <Route path="/backend/:project" element={<Backend />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:project" element={<Projects />} />
            <Route path="/projects/:project/:module" element={<Projects />} />
            <Route path="/mastery" element={<Mastery />} />
            <Route path="/jp-bridge" element={<JapaneseBridge />} />
            <Route path="/problem/new" element={<ProblemForm />} />
            <Route path="/problem/:id/edit" element={<ProblemForm />} />
            <Route path="/solve/:id" element={<Solve />} />
            <Route path="/paths" element={<Paths />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
      </div>
      <CommandPalette />
      {showWelcome && <Welcome onClose={dismissWelcome} />}
    </ToastProvider>
  );
}

function NotFound() {
  const nav = useNavigate();
  return (
    <div className="empty" style={{ paddingTop: "20vh" }}>
      <div className="big">🤔</div>
      <div>Nothing here.</div>
      <button style={{ marginTop: 12 }} onClick={() => nav("/")}>
        Back to Dashboard
      </button>
    </div>
  );
}
