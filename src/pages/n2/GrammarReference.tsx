import { useState } from "react";
import { Link } from "react-router-dom";
import { GRAMMAR_POINTS } from "../../data/n2Study/grammar";
import { STUDY_LESSONS } from "../../data/n2Study";
import { STUDY_ROOT } from "./StudyShared";

export default function GrammarReference() {
  const [query, setQuery] = useState("");
  const [group, setGroup] = useState("");
  const normalized = query.normalize("NFKC").trim().toLocaleLowerCase();
  const matches = GRAMMAR_POINTS.filter((p) => (!group || p.group === group) &&
    [p.pattern, p.meaning, p.formation, p.register, p.contrast, ...p.examples.flatMap((e) => [e.japanese, e.english])].join(" ").normalize("NFKC").toLocaleLowerCase().includes(normalized));
  const legacy = STUDY_LESSONS.filter((l) => ["wake", "limit", "change"].includes(l.id) && !group &&
    [l.format, l.takeaway, l.trap, ...l.examples.flatMap((e) => [e.japanese, e.english])].join(" ").normalize("NFKC").toLocaleLowerCase().includes(normalized));
  return <details className="card"><summary>Grammar reference</summary>
    <label className="study-field">Find a grammar pattern<input type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="ものの, cause, refusal…" /></label>
    <label className="study-field">Reference meaning group<select aria-label="Reference meaning group" value={group} onChange={(e) => setGroup(e.target.value)}>
      <option value="">All groups</option>{[...new Set(GRAMMAR_POINTS.map((p) => p.group))].sort().map((g) => <option key={g}>{g}</option>)}
    </select></label>
    <p role="status">{matches.length + legacy.length} patterns or comparisons match</p>
    <div className="study-stack">{matches.map((p) => <details className="study-reference" key={p.id}>
      <summary><span lang="ja">{p.pattern}</span> · {p.group}</summary>
      <p>{p.meaning}</p><p><strong>Formation:</strong> {p.formation}</p><p><strong>Usage &amp; tone:</strong> {p.register}</p>
      <div className="study-example">{p.examples.map((e) => <div key={e.japanese}><p lang="ja">{e.japanese}</p><p>{e.english}</p></div>)}</div>
      <p className="study-callout">{p.contrast}</p>
      <Link className="btn" aria-label={`Practise ${p.pattern}`} to={`${STUDY_ROOT}/lesson/grammar-${p.id}`}>Practise this pattern →</Link>
    </details>)}{legacy.map((l) => <details className="study-reference" key={l.id}><summary lang="ja">{l.format}</summary>
      <p>{l.takeaway}</p>{l.examples.map((e) => <div key={e.japanese}><p lang="ja">{e.japanese}</p><p>{e.english}</p></div>)}
      <p className="study-callout">{l.trap}</p><Link className="btn" to={`${STUDY_ROOT}/lesson/${l.id}`}>Practise this comparison →</Link>
    </details>)}</div>
    {!matches.length && !legacy.length && <p>Try another pattern, meaning or group.</p>}
  </details>;
}
