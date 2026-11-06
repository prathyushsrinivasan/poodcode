import { readingCorrection } from "../lib/readingCorrection";

export default function ReadingCorrection({ answer, accepted }: { answer: string; accepted: readonly string[] }) {
  const difference = readingCorrection(answer, accepted);
  if (!difference.distance) return null;
  return <div className="study-callout">
    <p>Your reading: <span lang="ja">{difference.given.map((part, i) => part.changed ? <del key={i}>{part.text}</del> : <span key={i}>{part.text}</span>)}</span></p>
    <p>Expected reading: <span lang="ja">{difference.correct.map((part, i) => part.changed ? <mark key={i}>{part.text}</mark> : <span key={i}>{part.text}</span>)}</span></p>
    <p className="n2-meta">Marked kana show what to add or change; crossed-out kana need changing or removing. Check small kana, long vowels and voiced sounds.</p>
  </div>;
}
