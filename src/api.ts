// Thin typed wrappers around Tauri commands. Command *argument* names use
// camelCase (Tauri auto-converts to the Rust snake_case params); returned data
// keeps snake_case field names (serde serialization).
import { invoke } from "@tauri-apps/api/core";
import type {
  Attempt,
  Concept,
  Dashboard,
  JudgeReport,
  LangInfo,
  Note,
  Problem,
  ProcOut,
  ReviewItem,
  Solution,
  Stats,
  TestCase,
  CountPair,
  TopicRecommendation,
  Mistake,
  Path,
  Contest,
  Flashcard,
} from "./types";

export const api = {
  // Problems
  listProblems: () => invoke<Problem[]>("list_problems"),
  getProblem: (id: number) => invoke<Problem>("get_problem", { id }),
  saveProblem: (problem: Problem) => invoke<number>("save_problem", { problem }),
  deleteProblem: (id: number) => invoke<void>("delete_problem", { id }),
  setFavorite: (id: number, favorite: boolean) =>
    invoke<void>("set_favorite", { id, favorite }),
  setConfidence: (id: number, confidence: number) =>
    invoke<void>("set_confidence", { id, confidence }),
  distinctTags: (kind: "topic" | "subtopic" | "company") =>
    invoke<string[]>("distinct_tags", { kind }),

  // Import / export
  importProblems: (json: string) => invoke<number>("import_problems", { json }),
  exportProblems: () => invoke<string>("export_problems"),
  readFile: (path: string) => invoke<string>("read_file", { path }),
  writeFile: (path: string, contents: string) =>
    invoke<void>("write_file", { path, contents }),

  // Test cases
  listTestCases: (problemId: number) =>
    invoke<TestCase[]>("list_test_cases", { problemId }),
  saveTestCase: (testCase: TestCase) =>
    invoke<number>("save_test_case", { testCase }),
  deleteTestCase: (id: number) => invoke<void>("delete_test_case", { id }),

  // Prerequisites checklist (per problem)
  knownPrereqs: (problemId: number) =>
    invoke<string[]>("known_prereqs", { problemId }),
  setPrereqStatus: (problemId: number, key: string, known: boolean) =>
    invoke<void>("set_prereq_status", { problemId, key, known }),

  // Notes
  getNote: (problemId: number) => invoke<Note>("get_note", { problemId }),
  saveNote: (problemId: number, content: string) =>
    invoke<void>("save_note", { problemId, content }),

  // Solutions
  listSolutions: (problemId: number) =>
    invoke<Solution[]>("list_solutions", { problemId }),
  saveSolution: (solution: Solution) =>
    invoke<number>("save_solution", { solution }),
  deleteSolution: (id: number) => invoke<void>("delete_solution", { id }),

  // Learn / concepts
  concepts: () => invoke<Concept[]>("concepts"),

  // Execution
  languages: () => invoke<LangInfo[]>("languages"),
  runTests: (problemId: number | null, language: string, code: string, cases: TestCase[]) =>
    invoke<JudgeReport>("run_tests", { problemId, language, code, cases }),
  runScratch: (problemId: number | null, language: string, code: string, stdin: string) =>
    invoke<ProcOut>("run_scratch", { problemId, language, code, stdin }),
  submit: (
    problemId: number,
    language: string,
    code: string,
    durationSeconds: number
  ) =>
    invoke<JudgeReport>("submit", {
      problemId,
      language,
      code,
      durationSeconds,
    }),
  listAttempts: (problemId: number) =>
    invoke<Attempt[]>("list_attempts", { problemId }),

  // Revision
  dueReviews: () => invoke<ReviewItem[]>("due_reviews"),
  markReviewed: (problemId: number, remembered: boolean) =>
    invoke<void>("mark_reviewed", { problemId, remembered }),
  gradeReview: (problemId: number, quality: number) =>
    invoke<void>("grade_review", { problemId, quality }),
  rescheduleReview: (problemId: number, dueDate: string) =>
    invoke<void>("reschedule_review", { problemId, dueDate }),

  // Mistakes (reflection)
  listMistakes: (problemId: number) => invoke<Mistake[]>("list_mistakes", { problemId }),
  addMistake: (mistake: Mistake) => invoke<number>("add_mistake", { mistake }),
  deleteMistake: (id: number) => invoke<void>("delete_mistake", { id }),

  // Learning paths
  listPaths: () => invoke<Path[]>("list_paths"),

  // Contests
  createContest: (title: string, problemIds: number[], durationSeconds: number) =>
    invoke<number>("create_contest", { title, problemIds, durationSeconds }),
  contest: (id: number) => invoke<Contest>("contest", { id }),
  listContests: () => invoke<Contest[]>("list_contests"),
  finishContest: (id: number) => invoke<void>("finish_contest", { id }),
  recordContestResult: (contestId: number, problemId: number, solved: boolean) =>
    invoke<void>("record_contest_result", { contestId, problemId, solved }),

  // Flashcards
  listFlashcards: () => invoke<Flashcard[]>("list_flashcards"),
  dueFlashcards: () => invoke<Flashcard[]>("due_flashcards"),
  addFlashcard: (front: string, back: string, source: string) =>
    invoke<number>("add_flashcard", { front, back, source }),
  gradeFlashcard: (id: number, quality: number) =>
    invoke<void>("grade_flashcard", { id, quality }),
  deleteFlashcard: (id: number) => invoke<void>("delete_flashcard", { id }),

  // Stats / dashboard
  statistics: () => invoke<Stats>("statistics"),
  dashboard: () => invoke<Dashboard>("dashboard"),
  timeline: () => invoke<CountPair[]>("timeline"),

  // Settings
  getSettings: () => invoke<Record<string, string>>("get_settings"),
  setSetting: (key: string, value: string) =>
    invoke<void>("set_setting", { key, value }),

  // Drafts + per-problem UI state (persisted in SQLite)
  getDraft: (problemId: number, language: string) =>
    invoke<string | null>("get_draft", { problemId, language }),
  saveDraft: (problemId: number, language: string, code: string) =>
    invoke<void>("save_draft", { problemId, language, code }),
  getHintsRevealed: (problemId: number) =>
    invoke<number>("get_hints_revealed", { problemId }),
  setHintsRevealed: (problemId: number, count: number) =>
    invoke<void>("set_hints_revealed", { problemId, count }),

  // Backup / restore (full database)
  backupDatabase: (path: string) => invoke<void>("backup_database", { path }),
  restoreDatabase: (path: string) => invoke<void>("restore_database", { path }),

  // Learning recommendations
  learningRecommendations: () =>
    invoke<TopicRecommendation[]>("learning_recommendations"),

  // Random practice
  randomProblem: (
    difficulty?: string,
    topic?: string,
    predicate?: string
  ) =>
    invoke<Problem | null>("random_problem", {
      difficulty: difficulty ?? null,
      topic: topic ?? null,
      predicate: predicate ?? null,
    }),
  logStudyTime: (seconds: number) =>
    invoke<void>("log_study_time", { seconds }),
};
