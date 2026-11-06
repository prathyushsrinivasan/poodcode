import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import type { ReadingWord } from "../data/dokkai/types";
import { readingTransferExamples } from "../lib/readingTransfer";

export default function ReadingTransfer({ word, source }: { word: ReadingWord; source: string }) {
  const [open, setOpen] = useState(false);
  const examples = useMemo(() => open ? readingTransferExamples(word, source) : [], [open, word, source]);
  return <details className="reading-transfer" onToggle={(e) => setOpen(e.currentTarget.open)}><summary>Use this word in another sentence</summary>
    {examples.map((example) => <div key={example.passageId} className="study-example">
      <p lang="ja">{example.sentence.slice(0, example.at)}<mark>{example.wordText}</mark>{example.sentence.slice(example.at + example.wordText.length)}</p>
      <Link to={`/japanese/n2/reading/${example.kind}/${example.passageId}`}>Read the passage: {example.title} →</Link>
    </div>)}
    {open && !examples.length && <p className="n2-meta">No second context for this exact reading and meaning is in the bank yet.</p>}
  </details>;
}
