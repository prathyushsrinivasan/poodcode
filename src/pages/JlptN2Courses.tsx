import { Link } from "react-router-dom";
import { Card, Icon, PageHeader } from "../components/ui";
import { JLPT_SECTIONS } from "../data/jlptSections";
import { useN2Study } from "../lib/useN2Study";
import { StudyStatus, STUDY_ROOT } from "./n2/StudyShared";
import JlptReviewEntry from "../components/JlptReviewEntry";
import { COURSE_LINKS } from "../lib/jlptWorkspace";
import JlptRecovery from "../components/JlptRecovery";

export default function JlptN2Courses() {
  const state = useN2Study();
  const session = state.data?.session;
  return <div className="page n2-page study-page jlpt-home">
    <PageHeader eyebrow="日本語" title="JLPT" subtitle="Choose what you want to practice." />
    <JlptReviewEntry />
    <JlptRecovery showCourses />
    {session && session.phase !== "summary" && <Card className="study-resume">
      <div><strong>Pick up where you left off</strong><p>{session.title} · Question {session.position + 1} of {session.questionIds.length}</p></div>
      <Link className="btn primary" to={`${STUDY_ROOT}/study`}>Continue round →</Link>
    </Card>}
    <div className="jlpt-sections">
      {JLPT_SECTIONS.map((section) => <section className="jlpt-section" key={section.id} aria-labelledby={`jlpt-${section.id}`}>
        <h2 id={`jlpt-${section.id}`}><span lang="ja">{section.japanese}</span><span>{section.title}</span></h2>
        <ul className="jlpt-practice-list">
          {section.items.map((item) => <li key={item.label}>
            {item.to ? <Link to={item.to} className="jlpt-practice-link"><span>{item.label}</span><Icon name="chevronRight" size={16} /></Link>
              : <span className="jlpt-practice-unavailable"><span>{item.label}</span><small>Coming soon</small></span>}
          </li>)}
        </ul>
      </section>)}
    </div>
    <details className="card jlpt-tips"><summary>Courses &amp; personal tools</summary><div className="n2-actions">{COURSE_LINKS.map((l) => <Link key={l.href} to={l.href}>{l.label} →</Link>)}<Link to={`${STUDY_ROOT}/review?tab=vocabulary`}>Personal vocabulary lists →</Link><Link to={`${STUDY_ROOT}/review?tab=backup`}>Progress export / import →</Link></div></details>
    <StudyStatus state={state} />
  </div>;
}
