import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { JLPT_BACKUP_KEYS, reviewInventory } from "../lib/jlptWorkspace";
import { withJlptJournals } from "../lib/jlptPersistence";
import { useN2Study } from "../lib/useN2Study";

export default function JlptReviewEntry() {
  const state = useN2Study();
  const [settings, setSettings] = useState<Record<string, string> | null>(null);
  const [error, setError] = useState("");
  const [now, setNow] = useState(Date.now);
  useEffect(() => { let live = true; api.getSettings().then((s) => { if (live) setSettings(s); }).catch((e) => { if (live) setError(String(e)); }); const timer = window.setInterval(() => setNow(Date.now()), 30_000); return () => { live = false; window.clearInterval(timer); }; }, []);
  const due = state.data && settings ? reviewInventory(state.data, withJlptJournals(settings, JLPT_BACKUP_KEYS), now).filter((i) => i.due).length : null;
  return <div className="jlpt-review-entry"><Link className="btn primary" to="/japanese/n2/review">JLPT review{due !== null ? ` · ${due} due` : ""} →</Link>
    <Link className="btn" to="/japanese/n2/review?tab=practice">Daily practice &amp; mocks</Link>
    <Link className="ghost-link" to="/japanese/n2/review?tab=search">Search all JLPT content</Link>
    {error && <p role="alert">Due count unavailable: {error}</p>}
  </div>;
}
