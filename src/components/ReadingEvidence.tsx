import { useState } from "react";
import { evidenceSentences, compareEvidence } from "../lib/readingEvidence";

export default function ReadingEvidence({ texts, evidence, review }: { texts: { text: string }[]; evidence: string[]; review: boolean }) {
  const [selected, setSelected] = useState<string[]>([]);
  const sentences = evidenceSentences(texts);
  const feedback = review ? compareEvidence(texts, evidence, selected) : null;
  return <details className="reading-evidence-practice"><summary>Choose supporting sentences</summary>
    <p className="n2-meta">Select the sentences that support your answer. Compare them with the supplied evidence after checking.</p>
    <fieldset className="study-answer-options" disabled={review}><legend>Evidence from the passage</legend>
      {sentences.map((sentence) => <label key={sentence.id} className={`study-option ${selected.includes(sentence.id) ? "is-selected" : ""}`}>
        <input type="checkbox" checked={selected.includes(sentence.id)} onChange={(e) => setSelected((before) => e.target.checked ? [...before, sentence.id] : before.filter((id) => id !== sentence.id))} />
        <span lang="ja">{texts.length > 1 && <small>Text {sentence.textIndex + 1}: </small>}{sentence.text}</span>
      </label>)}
    </fieldset>
    {feedback && selected.length > 0 && <p role="status" className="study-callout">{feedback.coversAll && feedback.matching.length === feedback.selected.length
      ? "Your selected sentences overlap all of the supplied evidence."
      : `${feedback.matching.length} of ${feedback.selected.length} selected sentences overlap the supplied evidence. Compare your selection with the highlighted text.`}</p>}
  </details>;
}
