# UI overhaul roadmap

**Scope:** how the app looks, reads, navigates and feels — the shell, pages,
components, visual system, accessibility and feedback. Content (what the courses
teach) is out of scope; see `DSA_ROADMAP.md` for that.

**Method:** a code audit of `src/` on 2026-09-18 — 27 pages, 21 components and
`global.css` (1,698 lines). Every item says what is wrong, with the evidence,
and what to change.

**What already works, and should be the template for the rest:** the DSA
curriculum pages (`Library.tsx`, `CurriculumUnit.tsx`, `CurriculumDrill.tsx`).
They have:
- a stage rail, a tabbed unit page and a "continue" hero;
- loading skeletons and remembered UI state;
- real ARIA, and CSS classes instead of inline styles.

Most of the rest of the app predates that work.

**Sizing:** S = hours, M = a day or two, L = several days.

---

## The numbers behind this list

| Measure | Value |
|---|---|
| Inline `style={{…}}` objects in pages and components | **~1,500** (Projects 171, Learn 99, Solve 98, Mastery 96, Backend 85) |
| Most repeated inline values | `fontSize: 12` ×187, `marginTop: 10` ×61, `marginTop: 0` ×52 |
| Files with any `aria-` attribute | **10 of 48** |
| Tab bars with `role="tab"` | 1 (Solve's tabs are plain `div`s) |
| Pages with a loading skeleton | 3 of 27 (all curriculum) |
| Silent `.catch(() => {})` / `catch {}` | **42** |
| `window.confirm` for destructive actions | 4 |
| CSS breakpoints | 2 (1150px, 980px), curriculum pages only |
| Built pages with **no route** | **9** |
| Contrast, faint text on background (AA needs 4.5:1) | 3.75–4.10 dark · **2.89–3.08 light** |
| Contrast, white on the primary button | **3.20** |
| Contrast, "Medium" orange on white (light theme) | **2.19** |

---

## A. Navigation and information architecture

**A1 · Nine finished pages are unreachable (M, decision first).** Statistics,
Learning Timeline, Random Practice, Company Prep, Interview Mode, Contest Mode,
Pattern Drill, Flashcards and the Visual Debugger all still exist in
`src/pages/`, but commit `7ee15cc` removed their routes and nav entries. Nothing
imports them. Solve still carries the modes they launched (`?mode=interview`,
`?contest=`, `?drill=1`) with no way in, and the README still lists them as
"Fully built".

Decide per page:
- **Restore** under two new nav groups — *Practice modes* (Random, Pattern
  Drill, Interview, Contest, Flashcards) and *Insights* (Statistics, Timeline,
  Company Prep) — restyled with the component set from §C.
- **Or delete** the page and its Solve branch, and correct the README.

**A2 · The sidebar is a flat list of ten destinations with no intent grouping (S).**
One "Practice" heading covers the Dashboard, the DSA curriculum, a concept
library, three courses, a project track, a mastery programme, a Japanese bridge
and learning paths. Group by what the learner is doing:
- **Today:** Dashboard.
- **Learn:** Learn, DSA Curriculum, Learning Paths.
- **Courses:** TypeScript, Java, Backend Lab, Projects, 6-Month Mastery.
- **Languages:** 日本語 → Java.
- **Practice / Insights:** see A1.
- **App:** Settings.

**A3 · Learning Paths and the DSA Curriculum overlap (M).** Both are "problems in
a taught order". Paths predates the curriculum and has its own progress bars and
page. Either fold the paths into the curriculum as saved filters or "tracks
through the units", or retitle them clearly as short topic playlists and link
each to its units.

**A4 · There is no back or forward (M).** Tauri has no browser chrome. Only four
pages draw their own back button (Solve, ProblemForm, CurriculumUnit, Backend),
so reaching a problem from the curriculum, the Dashboard or the palette strands
you. Add a slim **top bar** containing:
- back/forward buttons, bound to Alt+←/→ and mouse buttons 4/5;
- a **breadcrumb** (DSA Curriculum › Stage 3 › Sorting › Count Inversions);
- the palette trigger, moved from the sidebar.

**A5 · The sidebar cannot collapse (S).** It always takes 220px, including on
Solve and the Projects workbench, where width matters most. Add a collapsed
icon-only rail (Ctrl+B) and collapse it automatically on editor pages, with a
remembered preference.

**A6 · Nav badges are styled but never shown (S).** `.nav-badge` exists in the
CSS. The only badge was the removed review count. Show what is actually due:
- curriculum review-lane items;
- 日本語 vocabulary cards due;
- an "in progress" dot on courses with a started unit.

**A7 · The Dashboard ends with four buttons duplicating the sidebar (S).**
"DSA Curriculum · TypeScript Course · Java Course · Backend Lab" — replace them
with the per-track continue cards from B1.

**A8 · The command palette has no recents and no actions beyond navigation (M).**
Add:
- **Recent** (last opened problems, units and weeks);
- **Actions** (new problem, back up database, switch editor language, collapse
  sidebar);
- a `?` entry that opens a keyboard-shortcut sheet (D8).

**A9 · The welcome tour is stale and incomplete (S).**
- **Stale:** it says the Java course is "ten modules past the basics" (it has 31).
- **Incomplete:** it omits Learn, Projects and 日本語.
- **No Escape to close.**
- **Hard to reopen:** only from Settings, which reloads the whole app.

Rebuild it as a short checklist ("pick a track · solve one problem · set daily
goals"), reopenable from a help menu without a reload.

**A10 · The 404 page is a bare 🤔 (S).** Give it the palette search and the last
page visited.

---

## B. Dashboard and "today"

**B1 · The Dashboard knows about one part of the app (L).** It shows problem
counts, daily difficulty goals, a weakest topic, one suggested problem and topic
recommendations — plus the Mastery card. It says nothing about:
- the curriculum's *up next* and its review lane;
- the TypeScript and Java courses' resume points;
- Backend Lab or Projects progress;
- 日本語 cards due.

Rebuild it as **Today**:
- one **continue card per active track** (last position plus the next action);
- a **due now** list merging every review system;
- the streak;
- a compact activity heatmap (the `.heatmap` CSS and the Timeline page already
  exist).

**B2 · A daily goal tracks something the app no longer lets you do (S).**
"Review problems" is still a goal row and a Settings field, but the review
queue's UI was removed. Replace it with "curriculum reviews" (the review lane),
or drop it.

**B3 · Loading never ends on an error (S).** The Dashboard waits on
`api.dashboard()`, logs failures to the console, and stays on "Loading…"
forever — the same bug the curriculum fixed in its B1. Add a skeleton, an error
state with Retry, and partial rendering when only the recommendations fail.

**B4 · Suggestions are not actionable (S).** The "Weakest topic" tile cannot be
clicked, and the recommended-focus chips are `span`s with `onClick`, unreachable
by keyboard. Link the topic to a filtered Browse and its unit, and make chips
real buttons or links.

**B5 · The stat tiles are three numbers with no trend (S).** Add a
seven-day sparkline and a comparison with last week to each ("solved today",
"study time", "streak").

---

## C. Visual design system

**C1 · Design tokens cover colour and one radius only (M).** `:root` defines
palette variables, `--radius` and `--sidebar-w`. There is no spacing scale,
type scale, shadow scale, z-index scale or motion token, which is why ~1,500
inline style objects each choose their own `12`, `10`, `14` or `16`. Define:
- `--space-1…8` on a 4px grid;
- `--text-xs…2xl`;
- `--shadow-1…3`, `--z-*`, and `--ease-*` / `--dur-*`.

Then map every existing inline value onto a token.

**C2 · Two design languages (L).** The curriculum pages use named `cur-*` classes,
a rail, tabs, heroes and skeletons. The TypeScript and Java courses, Backend
Lab, Projects, Mastery, Learn and Settings use `card` grids with inline styles.
Pick the curriculum language as the house style and move every track page onto
it (see §G).

**C3 · No component library (L).** Buttons are CSS classes, and every page
rebuilds the same pieces by hand. Build a small set in `src/components/ui/`:

| Component | Replaces |
|---|---|
| `Button` (primary / secondary / ghost / danger, sizes, icon slot, loading) | raw `<button className=…>` everywhere |
| `Card`, `CardHeader` | `div.card` + inline `h3 style={{marginTop:0}}` (dozens) |
| `ProgressBar` (value, tone, label) | 12+ hand-built `.progress > span style={{width}}` |
| `Tabs` (roving focus, ARIA) | Solve's `div.tab` tabs and the curriculum's own tabs |
| `Modal` / `ConfirmDialog` | the welcome overlay, the palette shell, 4 × `window.confirm` |
| `PageHeader` (title, subtitle, actions, breadcrumb) | `h1.page-title` + `p.page-sub` repeated per page |
| `Badge`, `Chip`, `Pill` | `.badge`, `.pill`, clickable spans |
| `StatTile`, `EmptyState`, `ErrorState`, `Skeleton` | `Stat`, `Empty`, ad-hoc "Loading…" |
| `Field`, `FormRow`, `NumberInput`, `Toggle` | Settings' local `Field`, raw checkboxes |
| `Tooltip`, `Kbd` | `title=` attributes, `.kbd` |

**C4 · Exercise cards are implemented several times (M).**
- `ExerciseCard` exists twice: in `Learn.tsx` (SQL-aware) and in
  `components/LearnExercise.tsx` (courses).
- Mastery has `QuizQuestionCard`.
- The 日本語 bridge has `BridgeCard`.
- Projects renders exercises its own way.

Unify them into one `Exercise` component with slots for statement, editor,
verdict and reference, so verdict colours, spacing and actions match everywhere.

**C5 · The fonts are named but not shipped (S).** The stack starts with "Inter"
and "JetBrains Mono". No font files are bundled, and the CSP (`font-src 'self'`)
blocks CDNs, so Windows silently renders Segoe UI and Cascadia. Either bundle
both (WOFF2, subset, `font-display: swap`) or make the stack honest.

**C6 · Emoji are the icon set (M).** Every nav item, most buttons, tab labels and
headings use emoji (🏠 📚 📘 ⚙️ ▶ ⏎ 🎯 …). They render differently per OS, cannot
follow the theme colour, and make dense toolbars noisy. Adopt one SVG icon set,
bundled locally (offline app). Keep emoji for content — flags, celebratory
moments, 日本語 flashcards.

**C7 · The type scale is too small and too flat (S).**
- Body is 14px, page titles 22px, and 201 inline `fontSize: 11/12`.
- Section headings are default `h3`s with `marginTop: 0` overrides.

Set a 12 / 13 / 14 / 16 / 20 / 28 scale with clear heading levels. Raise
secondary text to 13px where it carries information rather than decoration.

**C8 · Themes: dark, light, nothing else (M).**
- No "follow system" option.
- No high-contrast mode.
- No accent choice.

Also, the editor theme only changes through the app theme toggle. Add
**System**, a **high-contrast** variant, and an independent editor theme picker.

**C9 · Difficulty colours ignore the theme (S).** `--intro/--easy/--medium/--hard`
are defined once in `:root`. On the light theme "Medium" text on white is
2.19:1 and "Easy" 2.61:1. Give each theme its own darker/lighter values, and pair
colour with the letter so colour is never the only signal.

**C10 · Motion is ad hoc (S).** Only `fadein` and the skeleton shimmer are
defined. Add consistent short transitions for:
- panels and collapsibles opening;
- tab changes;
- toast entry;
- the verdict appearing after Submit.

All of it gated behind `prefers-reduced-motion`, which the skeleton already
respects.

**C11 · There is no density or app-scale setting (S).** Only the editor font size
can change. Add an **interface size** (90–125%, scaling the root size) and
**compact/comfortable** density for lists and tables.

**C12 · Brand polish (S).**
- **Logo:** a gradient "P" square with a hard-coded `#7b5cff` outside the palette.
- **Window chrome:** the default title bar.

Design a proper mark, derive the app icon from it, and consider a custom title
bar that holds the back/forward buttons from A4.

---

## D. Accessibility

**D1 · Text contrast fails AA in both themes (S).** `--text-faint` is 3.75:1 on
cards in dark and 2.89–3.08:1 in light, yet it is used for 11–12px explanatory
text (75 `.faint` elements plus inline uses). Darken the light-theme value and
lighten the dark-theme value to ≥ 4.5:1, and reserve "faint" for truly optional
text.

**D2 · Filled buttons have low-contrast labels (S).**
- **Primary:** white on `--accent` (#4c8dff) is 3.20:1.
- **Success:** white on `--good` is 2.61:1.

Darken the fills (or use dark text on them) until they pass 4.5:1.

**D3 · Clickable `div`s and `span`s (M).** Solve's seven tabs, the course week
cards, the Dashboard chips and Settings' "re-detect" all use `onClick` on
non-interactive elements, so they cannot be reached with Tab. `ClickableRow`
exists in `common.tsx` and is used in only a few places. Convert all of them to
buttons or links, or to `ClickableRow`.

**D4 · Tabs are not tabs (S).** Only one `role="tab"` exists in the codebase.
Give every tab bar `role="tablist"`, `aria-selected`, roving tabindex and
←/→/Home/End keys, through the `Tabs` component from C3.

**D5 · Focus is mostly invisible (S).** Only `.collapsible-head` has a
`:focus-visible` style. Add one global focus ring token, applied to buttons,
links, inputs, tabs and clickable rows.

**D6 · Dialogs do not behave like dialogs (S).** The welcome overlay has no
Escape handler, no focus trap and no `aria-modal`; the palette handles Escape
but does not trap focus or restore it on close. Both should come from `Modal`
(C3).

**D7 · Toasts are not announced (S).** The toast is a plain `div`. Put the
container in `aria-live="polite"`, and use `assertive` for errors.

**D8 · Keyboard shortcuts are invisible (M).** The editor has Ctrl+Enter (run)
and Ctrl+Shift+Enter (submit), and the palette has Ctrl+K. Nothing documents
them, and the rest of the app has none. Add:
- a **shortcut sheet** (`?`);
- tooltips showing each shortcut beside its button;
- global keys — next/previous problem in a rung, toggle the description pane,
  reveal the next hint, focus the editor, collapse the sidebar.

**D9 · Structure is weak for screen readers (M).**
- Pages lack landmark regions beyond `aside`/`main`.
- Many sections use styled `div`s instead of headings.
- Icon-only buttons (✕, ↻) have no `aria-label`.

Audit each page for landmarks, a single `h1`, ordered headings and labelled
controls.

---

## E. Feedback, loading and errors

**E1 · The toast is a single, short-lived line (M).** `ToastProvider`:
- holds one message and replaces it on each call;
- clears it after 2.2s;
- has no severity, action or dismiss.

So "Submit error: …" or "Restore failed: …" disappears before it can be read.
Replace it with a stacked toast system:
- info / success / warning / error styles;
- longer, hover-pausing durations for errors;
- a "copy details" action for failures;
- **Undo** for reversible actions (resetting a unit, forgetting review answers).

**E2 · 42 silent failures (M).** Calls such as `recordContestResult`, settings
writes and progress marks end in `.catch(() => {})`. Some really are
best-effort, but none of them tell anyone. Decide per call: stay silent (with a
comment saying why), show a quiet toast, or show an inline error with Retry.

**E3 · 24 of 27 pages have no skeleton (M).** Skeletons exist
(`components/Skeleton.tsx`) but only the curriculum uses them. Give every page a
layout-shaped skeleton and an `ErrorState` with Retry.

**E4 · Saves give no feedback (S).**
- **Settings:** writes a goal or preference on every keystroke, silently.
- **Solve:** debounces draft saves invisibly.

Add a small "Saved · just now" indicator on editors and forms, and a failure
state when a write does not land.

**E5 · Destructive actions use `window.confirm` (S).** Four places: restore
database, start a project module over, replace the workbench code, and forget
review answers.
Replace them with `ConfirmDialog`, which should:
- name exactly what will be lost;
- offer "back up first" on Restore;
- make the destructive button visually distinct.

**E6 · Empty states say nothing to do (S).** `Empty` renders an icon and a
sentence. Add a primary action to every empty state — "no notes yet → write
one", "no attempts → run the examples".

---

## F. Solve — the workspace

**F1 · The split is fixed at 50/50 (M).** `.solve` is
`grid-template-columns: 1fr 1fr`. At the minimum window size (960px) with the
sidebar showing, each half is about 370px. Make the panes **resizable**, let the
description **collapse**, offer a **stacked layout** for narrow windows, and
remember the sizes.

**F2 · Solve needs a focus mode (S).** Hide the sidebar and top bar and widen the
editor (F11 or a toolbar toggle). With A5 this becomes the default for Solve.

**F3 · Seven tabs in half a screen (M).** The left pane tabs are Description,
Prerequisites, Notes, Solutions, Attempts, Reflect and Editorial; they overflow
and scroll horizontally. Group them:
- **Problem:** description, prerequisites, editorial.
- **My work:** notes, attempts, solutions, reflection.

Then show counts ("Attempts · 4") so empty tabs are not worth clicking.

**F4 · The minimap is on by default in a half-width editor (S).**
`DEFAULT_PREFS.minimap = true` spends ~80px of a 370–600px editor. Default it to
off.

**F5 · Verdicts need a status bar (M).** Pin a bottom bar under the editor with:
- the last verdict;
- passed/total;
- runtime and memory (already measured);
- run count;
- a one-click jump to the first failing case's diff.

The results pane then becomes the detail view instead of the only place a result
appears.

**F6 · Rung and curriculum context is thin on Solve (S).** Show the unit and rung
the problem belongs to in the breadcrumb (A4). Add
"previous / next in rung" buttons and keyboard shortcuts.

**F7 · The modes need their own look, if restored (M).** Interview, contest and
drill currently change behaviour (timer, locked hints, explain-first) but look
like ordinary Solve. Give each a distinct chrome: a countdown bar, a mode badge,
and panels that are visibly locked rather than just empty.

**F8 · Custom input and test cases are hard to find (S).** "Custom stdin (for
Run)" sits at the bottom of the results tabs. Put a "Run with my input" split
button next to Run, and surface the test-case manager as its own tab with a
count.

---

## G. Course and track pages

**G1 · One track template instead of five layouts (L).** The TypeScript course,
Java course, Backend Lab, Projects and the 6-Month Mastery programme each have
their own overview page, progress card, module list and module page. Give all of
them the curriculum's structure:
- a **hero** ("resume unit N →", progress, time left);
- a **module rail** grouped by month or phase;
- a **module page** with Learn / Practise / Review tabs;
- the same prev/next paging.

**G2 · Unauthored weeks crowd the course pages (S).** The TypeScript course shows
all 32 weeks, 17 of them "soon" cards at 55% opacity, as full cards in the grid.
Collapse them into one "Coming later: weeks 16–32" row.

**G3 · Module cards are mouse-only (S).** The course week cards are `div`s with
`onClick` (D3). Use `ClickableRow`, or make them links, so ⌘/Ctrl-click and
keyboard both work.

**G4 · Long lessons need wayfinding (M).**
- **Navigation:** lessons are long markdown, with no table of contents,
  scrollspy or estimated reading position.
- **Progress:** the scroll-to-bottom auto-complete is invisible until it fires.

Add a sticky **on this page** outline, a reading-progress indicator, and a
visible "✓ read" state as the bottom sentinel is reached.

**G5 · Code blocks in lessons are plain text (M).** `Markdown.tsx` renders
fenced code with no syntax highlighting and no copy button, across hundreds of
Java, TypeScript and SQL lessons. Add build-time or lightweight runtime
highlighting (bundled offline) and a copy button on every block. The Monaco
theme colours can be reused so lessons and the editor match.

**G6 · Learn is one 1,501-line page for four jobs (L).** It is a concept library,
a language switcher, a SQL track and the 日本語 vocabulary. Split it into
sub-routes, and give the list search, filtering by language/category/progress,
and grouped headings. Move 日本語 vocabulary under the 日本語 nav group (A2),
beside the bridge.

**G7 · Projects is the heaviest page (L).** `Projects.tsx` is 1,880 lines with
171 inline styles; the workbench, history and review views add more. Split it
into components while moving it onto the design system — it is where most of
the visual inconsistency lives.

**G8 · Exercise verdicts differ by track (S).** Pass/fail/warn colours, verdict
wording and "show reference" placement vary between Learn, the courses, Projects
and Mastery. Fixed by C4; worth listing so it is checked page by page.

---

## H. Library, Browse and problem management

**H1 · Browse is a wide table with pill filters and no persistence (M).**
Add:
- a sticky header;
- **saved filter presets** ("unsolved Mediums in my weakest topic");
- a column chooser;
- keyboard row navigation (↑/↓, Enter to open);
- a remembered scroll position when returning from a problem.

**H2 · Browse renders every row (S).** All 653 rows are always in the DOM. With
more user problems this will stutter; virtualise the table or page it.

**H3 · The problem form is a long single column (M).** `ProblemForm.tsx` has 42
inline styles. Add:
- sections (statement, examples, constraints, tests, solutions);
- a live **markdown preview**;
- a proper **test-case table editor**;
- validation messages beside fields instead of toasts.

**H4 · The curriculum pages need a few finishing touches (S).**
- The stage rail cannot collapse on narrow windows.
- The unit page has no in-page outline across its tabs.
- The optional stage (just added) could use a distinct visual treatment in the
  rail, beyond a "+" number.

---

## I. Insights (if restored in A1)

**I1 · Statistics only measures problems (M).** The page charts problem
difficulty and topics (`Charts.tsx` is a 37-line ECharts wrapper). Make it
cover every track: units cleared, course weeks, project modules, review
retention, and time per track per week.

**I2 · The timeline belongs on the Dashboard (S).** Surface a 12-week activity
heatmap on Today (B1). Keep the full Timeline page for drill-down.

---

## J. Layout, window and state

**J1 · There is no layout contract between 960 and 1400px (M).** The window
minimum is 960×640, and only two breakpoints exist, both in curriculum CSS.
Define the behaviour of each page template at 960, 1180 and 1440 wide: sidebar
collapsed or expanded, one or two columns, split or stacked Solve.

**J2 · Scroll position is lost (S).** The app scrolls inside `.main`, not the
window, so the router does not restore scroll. Going back from a problem to
Browse or a long course page starts at the top. Save and restore scroll per
route.

**J3 · UI state is remembered in only one place (S).** The curriculum remembers
its last tab per unit. Extend that to Solve's active tab and pane sizes, Learn's
language, Browse's filters, and each course page's open month.

**J4 · Multiple windows (L, optional).** Tauri can open a second window. Allow
"pop out" of a lesson or the editorial beside the editor on a large or second
monitor.

---

## K. Settings

**K1 · Settings is one flat page of five cards (S).** Split it into sections:
Appearance, Editor, Goals, Data, Toolchains, Shortcuts, About. Add a left-hand
section nav and search.

**K2 · "re-detect" is a fake link (S).** The toolchain "re-detect" is a
`span onClick` that only toasts "restart the app". Implement a real re-detection
command, or remove the link and say "restart to re-detect".

**K3 · Showing the welcome again reloads the app (S).** It sets `onboarded = 0`
and calls `location.reload()`. Open the tour in place (A9).

**K4 · There is no About section (S).** The app version, seed versions,
database location, backup reminder and a keyboard-shortcut reference have no
home.

**K5 · Goals only know problem difficulties (S).** Daily goals are
Intro/Easy/Medium/Hard/Reviews. Add track goals (course weeks per week, curriculum
units, 日本語 cards per day) to match the Today page (B1).

---

## L. Tooling to make the overhaul safe

**L1 · The UI cannot run in a browser (M).** Every page calls Tauri `invoke`, so
`vite` in a normal browser shows errors instead of pages. Add a fixture-backed
mock `api` (a dev flag) that serves the seed JSON plus fake progress. Design
work, screenshots and reviews can then happen without the desktop build.

**L2 · A component gallery (S).** A dev-only `/ui` route showing every component
in both themes and every state — loading, empty, error, disabled.

**L3 · Visual regression checks (M).** With L1, capture Playwright screenshots of
the key pages in dark and light, and fail CI on unexpected diffs.

**L4 · A guard against inline styles (S).** Add a lint rule that rejects new
`style={{…}}` except for genuinely dynamic values (widths, colours computed from
data), so the ~1,500 do not grow back.

**L5 · Split `global.css` (S).** Break its 1,698 lines into
`tokens.css`, `base.css`, `components/*.css` and per-feature files. Delete rules
that belonged to removed pages (`.nav-badge` users, `.heatmap` if Timeline is
dropped).

**L6 · Accessibility checks in CI (S).** Run axe on the L3 screenshots' pages, and
check contrast of the token pairs automatically.

---

## Order of work

1. **Decide and unblock:**
   - A1 — restore or delete the nine pages;
   - L1 — a mock API, so everything after this can be viewed in a browser.
2. **Cheap accessibility and trust fixes (all S):** D1, D2, D5, D4, D7, B2, B3,
   E5, F4, K2, A9.
3. **Foundations:** C1 tokens → C3 components → C5 fonts → C6 icons → E1 toasts
   → L4, L5.
4. **Shell:** A2 grouping, A4 top bar with back/forward and breadcrumbs, A5
   collapsible sidebar, A6 badges, A8 palette, D8 shortcuts.
5. **Home:** B1 Today, B4, B5, I2.
6. **Workspace:** F1–F8.
7. **Templates:** G1 track template (courses, Backend, Projects, Mastery), G4
   and G5 lesson reading, C4 unified exercise, G6 Learn split, G7 Projects.
8. **Everything else:** H, I, J, K, C8–C12, and L2/L3/L6 as guards.

The ~1,500 inline styles, emoji icons and the two design languages will shrink
naturally through steps 3 and 7. Track the counts from the table at the top as
the progress measure.
