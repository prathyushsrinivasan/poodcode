import { Link } from "react-router-dom";
import { Badge, PageHeader } from "../components/ui";
import { N2_QUESTIONS } from "../data/jlptN2";
import { N2_ASSEMBLY_QUESTIONS } from "../data/jlptN2SentenceOrder";
import { READING_PASSAGES, READING_QUESTIONS } from "../data/dokkai";
import { KANJI_GROUPS, KANJI_WORDS } from "../data/kanjiWords";

export default function JlptN2Courses() {
  return <div className="page n2-page">
    <PageHeader eyebrow="日本語 · JLPT N2" title="JLPT N2 courses"
      subtitle="Choose the question format you want to practice. Each course has its own lessons, explanations and saved progress." />
    <div className="n2-grid">
      <Link className="card n2-lesson" to="/japanese/n2/kanji">
        <Badge>Kanji · Readings &amp; meanings</Badge>
        <h2>Kanji Word Builder</h2>
        <p>Explore words built from each kanji. Type the hiragana, then choose every matching English meaning. Includes single-answer and multiple-answer quizzes.</p>
        <span className="n2-meta">{KANJI_GROUPS.length} kanji · {KANJI_WORDS.length} vocabulary entries · N3–N1 study estimates</span>
        <strong>Explore kanji &amp; words →</strong>
      </Link>
      <Link className="card n2-lesson" to="/japanese/n2/reading">
        <Badge>Reading · 読解</Badge>
        <h2>読解（どっかい）</h2>
        <p>短文・中文・AB問題文・長文・情報検索. Read with vocabulary on hover, practice under a time limit, and review the evidence behind every answer.</p>
        <span className="n2-meta">{READING_PASSAGES.length} passages · {READING_QUESTIONS.length} questions · 100 short passages</span>
        <strong>Open reading sections →</strong>
      </Link>
      <Link className="card n2-lesson" to="/japanese/n2/patterns">
        <Badge>Kanji · Vocabulary</Badge>
        <h2>Kanji &amp; Vocabulary Blanks</h2>
        <p>Learn the pattern. Fill the blank. The original course: one-kanji word building and contextual vocabulary, with readings and translations.</p>
        <span className="n2-meta">{N2_QUESTIONS.length} questions · 24 pattern families</span>
        <strong>Open course →</strong>
      </Link>
      <Link className="card n2-lesson" to="/japanese/n2/sentence-order">
        <Badge>Grammar · 文の組み立て</Badge>
        <h2>Sentence Assembly ★</h2>
        <p>Put four fragments in order and choose the one that belongs at ★. Learn grammar connections, practice your five examples and try fresh five-question sets.</p>
        <span className="n2-meta">{N2_ASSEMBLY_QUESTIONS.length} questions · solving tips · mistake review</span>
        <strong>Open course →</strong>
      </Link>
    </div>
  </div>;
}
