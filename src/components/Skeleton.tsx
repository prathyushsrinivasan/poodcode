/**
 * Loading skeletons for the Library pages.
 *
 * Both pages used to render `Loading…` centred at 20vh while a 480 KB seed
 * parsed, which is a blank screen for long enough to read as a broken app. A
 * skeleton of the shape that is about to arrive answers the only question the
 * user actually has — *is anything happening?* — and costs a few divs.
 *
 * Deliberately not a generic skeleton library: the point is that the placeholder
 * has the same silhouette as the real content, so it has to know what that is.
 */

function Bar({ w, h = 12, mb = 8 }: { w: number | string; h?: number; mb?: number }) {
  return (
    <div
      className="skel"
      style={{ width: typeof w === "number" ? `${w}%` : w, height: h, marginBottom: mb }}
      aria-hidden
    />
  );
}

/** The curriculum front page: heading, the continue panel, search, then the
 * stage rail beside one stage's path of units. */
export function LibrarySkeleton() {
  return (
    <div className="page cur-page" role="status" aria-label="Loading the curriculum">
      <Bar w={30} h={26} mb={6} />
      <Bar w={45} h={12} mb={22} />

      <div className="cur-hero">
        <div className="cur-hero-main">
          <Bar w={15} h={10} />
          <Bar w={45} h={20} />
          <Bar w={65} h={12} mb={18} />
          <Bar w={35} h={30} mb={0} />
        </div>
        <div className="cur-hero-side">
          <Bar w={25} h={24} mb={0} />
          <Bar w="100%" h={6} mb={0} />
          <Bar w={60} h={12} mb={0} />
        </div>
      </div>

      <Bar w="100%" h={40} mb={24} />

      <div className="cur-layout">
        <div className="cur-stages">
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <Bar key={i} w="100%" h={48} mb={6} />
          ))}
        </div>
        <div>
          <Bar w={25} h={10} />
          <Bar w={40} h={24} />
          <Bar w={55} h={14} mb={22} />
          {[0, 1, 2].map((i) => (
            <div key={i} className="cur-unit">
              <Bar w={35} h={16} />
              <Bar w={60} h={12} />
              <Bar w={40} h={8} mb={0} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/** A unit page: breadcrumb, the unit header, the tab bar, then prose. */
export function UnitSkeleton() {
  return (
    <div className="page cur-page" role="status" aria-label="Loading the unit">
      <Bar w={30} h={12} mb={0} />
      <div className="cu-hero">
        <div className="cu-hero-icon" />
        <div>
          <Bar w={40} h={24} />
          <Bar w={60} h={14} />
          <Bar w={35} h={6} mb={0} />
        </div>
        <Bar w="180px" h={32} mb={0} />
      </div>

      <div className="cu-tabs" style={{ position: "static", paddingBottom: 10 }}>
        {[0, 1, 2, 3].map((i) => (
          <Bar key={i} w="150px" h={34} mb={0} />
        ))}
      </div>

      <div className="cu-main">
        <Bar w={30} h={20} mb={14} />
        {[0, 1, 2, 3, 4].map((i) => (
          <Bar key={i} w={92 - (i % 3) * 9} h={12} />
        ))}
      </div>
    </div>
  );
}

/** A track overview: hero, progress panel, then a grid of unit cards.
 *
 * Shared by the TypeScript and Java courses, the Backend Lab, Projects and
 * Mastery — five pages that each showed a bare "Loading…" while a 2-5 MB seed
 * parsed, which on a cold start is several seconds of blank page reading as a
 * broken app (UI_ROADMAP E3). */
export function TrackSkeleton({ cards = 6 }: { cards?: number }) {
  return (
    <div className="page" role="status" aria-label="Loading">
      <Bar w={35} h={26} mb={6} />
      <Bar w={55} h={12} mb={22} />

      <div className="card skel-hero">
        <Bar w={20} h={12} />
        <Bar w={45} h={20} />
        <Bar w="100%" h={8} mb={10} />
        <Bar w={30} h={30} mb={0} />
      </div>

      <Bar w={25} h={16} mb={12} />
      <div className="grid cols-2">
        {Array.from({ length: cards }).map((_, i) => (
          <div key={i} className="card">
            <Bar w={60} h={16} />
            <Bar w={85} h={12} />
            <Bar w={40} h={10} mb={0} />
          </div>
        ))}
      </div>
    </div>
  );
}

/** A long reading page: title, then paragraphs. */
export function ReadingSkeleton() {
  return (
    <div className="page" role="status" aria-label="Loading">
      <Bar w={40} h={26} mb={6} />
      <Bar w={60} h={12} mb={24} />
      {[92, 86, 95, 78, 90, 83, 70].map((w, i) => (
        <Bar key={i} w={w} h={12} />
      ))}
    </div>
  );
}
