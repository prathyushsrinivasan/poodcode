import { useEffect, useState } from "react";
import { Link, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { useStore } from "./store";
import { api } from "./api";
import { ToastProvider } from "./components/Toast";
import { CommandPalette } from "./components/CommandPalette";
import { Welcome } from "./components/Welcome";
import { Sidebar } from "./components/shell/Sidebar";
import { TopBar } from "./components/shell/TopBar";
import { ShortcutSheet } from "./components/shell/ShortcutSheet";
import { ScrollRestore } from "./components/shell/ScrollRestore";

import Today from "./pages/Dashboard";
import Library from "./pages/Library";
import LibraryBrowse from "./pages/LibraryBrowse";
import CurriculumUnit from "./pages/CurriculumUnit";
import CurriculumDrill from "./pages/CurriculumDrill";
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
import Gallery from "./pages/Gallery";
// Dev-only: the component gallery is not part of the shipped app, and the
// literal check lets the bundler drop it from a production build.
const DEV_UI = import.meta.env.VITE_MOCK === "1";

/** Pages where the editor wants the width more than the nav does. The sidebar
 * collapses itself on arrival and restores whatever it was on the way out, so
 * the preference is borrowed rather than overwritten. */
const EDITOR_ROUTES = [/^\/solve\//, /^\/projects\/[^/]+\/workbench/];

function useAutoCollapse() {
  const { pathname } = useLocation();
  const setSidebarAuto = useStore((s) => s.setSidebarAuto);

  useEffect(() => {
    const isEditor = EDITOR_ROUTES.some((r) => r.test(pathname));
    // `null` hands control back to the saved preference rather than forcing the
    // sidebar open — leaving an editor page should restore what you chose, not
    // override it in the other direction.
    setSidebarAuto(isEditor ? true : null);
  }, [pathname, setSidebarAuto]);
}

function Shell() {
  useAutoCollapse();
  const collapsed = useStore((s) => s.sidebarAuto ?? s.prefs.sidebarCollapsed);

  return (
    <div className={`app ${collapsed ? "sidebar-collapsed" : ""}`}>
      <Sidebar />
      <TopBar />
      <ScrollRestore />
      <main className="main" id="main">
        <Routes>
          <Route path="/" element={<Today />} />
          <Route path="/library" element={<Library />} />
          {/* Static segments, so neither can ever be shadowed by a unit key. */}
          <Route path="/library/browse" element={<LibraryBrowse />} />
          <Route path="/library/unit/:key" element={<CurriculumUnit />} />
          <Route path="/library/placement" element={<CurriculumDrill view="placement" />} />
          <Route path="/library/mixed/:stage" element={<CurriculumDrill view="mixed" />} />
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
          {/* Static segment, so it out-ranks the `:module` route below it and
              cannot be shadowed by a module that one day gets this key. */}
          <Route path="/projects/:project/reference" element={<Projects view="reference" />} />
          <Route path="/projects/:project/history" element={<Projects view="history" />} />
          <Route path="/projects/:project/workbench" element={<Projects view="workbench" />} />
          <Route path="/projects/:project/review" element={<Projects view="review" />} />
          <Route path="/projects/:project/:module" element={<Projects />} />
          <Route path="/mastery" element={<Mastery />} />
          <Route path="/jp-bridge" element={<JapaneseBridge />} />
          <Route path="/problem/new" element={<ProblemForm />} />
          <Route path="/problem/:id/edit" element={<ProblemForm />} />
          <Route path="/solve/:id" element={<Solve />} />
          <Route path="/paths" element={<Paths />} />
          <Route path="/settings" element={<Settings />} />
          {DEV_UI && <Route path="/ui" element={<Gallery />} />}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </div>
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
      .catch(() => {
        /* a settings read that fails is not a reason to onboard again */
      });
  }, []);

  // Settings asks for the tour with an event rather than a reload: it used to
  // clear `onboarded` and call location.reload(), which threw away every
  // in-memory bit of state to show a dialog.
  useEffect(() => {
    const open = () => setShowWelcome(true);
    window.addEventListener("poodcode:show-welcome", open);
    return () => window.removeEventListener("poodcode:show-welcome", open);
  }, []);

  const dismissWelcome = () => {
    setShowWelcome(false);
    api.setSetting("onboarded", "1").catch(() => {
      /* the tour is dismissed either way; worst case it returns next launch */
    });
  };

  if (!loaded) {
    return (
      <div className="boot" role="status">
        Loading Poodcode…
      </div>
    );
  }

  return (
    <ToastProvider>
      <Shell />
      <CommandPalette />
      <ShortcutSheet />
      <Welcome open={showWelcome} onClose={dismissWelcome} />
    </ToastProvider>
  );
}

/** A 404 that helps. It used to be a 🤔 and a button home — no search, and no
 * mention of where you had just been. */
function NotFound() {
  const nav = useNavigate();
  const { pathname } = useLocation();
  const setPalette = useStore((s) => s.setPalette);

  return (
    <div className="page notfound">
      <div className="big" aria-hidden>
        🤔
      </div>
      <h1 className="page-title">Nothing at that address</h1>
      <p className="page-sub">
        <code className="mono">{pathname}</code> isn't a page in this app.
      </p>
      <div className="row notfound-actions">
        <button className="primary" onClick={() => setPalette(true)}>
          🔎 Search for it
        </button>
        <button onClick={() => nav(-1)}>← Go back</button>
        <Link className="ghost-link" to="/">
          Today
        </Link>
      </div>
    </div>
  );
}
