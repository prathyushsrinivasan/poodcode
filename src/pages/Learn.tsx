/**
 * Learn: the concept library and its chapters (UI_ROADMAP G6).
 *
 * This file was 1,542 lines doing four jobs. It is now the router between
 * them; the jobs live in `pages/learn/`:
 *
 *   LearnIndex     /learn            the library — tracks, search, filters
 *   ConceptPage    /learn/:key       one chapter, on the reader layout
 *   JapanesePage   /japanese         the 日本語 vocabulary and review deck
 *
 * The exercise card and quiz it used to carry its own copies of are in
 * `components/exercise`, shared with every other track.
 */

import { Navigate, useLocation, useParams } from "react-router-dom";
import LearnIndex from "./learn/LearnIndex";
import ConceptPage from "./learn/ConceptPage";

export { default as JapanesePage } from "./learn/JapanesePage";

export default function Learn() {
  const { key } = useParams();
  const { search } = useLocation();
  // `/learn?word=…` was the 日本語 flashcard's address before it had a page.
  if (!key && new URLSearchParams(search).has("word")) {
    return <Navigate to={`/japanese${search}`} replace />;
  }
  return key ? <ConceptPage /> : <LearnIndex />;
}
