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

/** The curriculum front page: heading, progress card, search box, stage rows. */
export function LibrarySkeleton() {
  return (
    <div className="page page-wide" role="status" aria-label="Loading the curriculum">
      <Bar w={40} h={26} mb={6} />
      <Bar w={60} h={12} mb={18} />

      <div className="card" style={{ marginBottom: 16 }}>
        <Bar w={30} h={14} />
        <Bar w="100%" h={6} mb={16} />
        <Bar w={45} h={12} mb={0} />
      </div>

      <Bar w="100%" h={30} mb={18} />

      {[0, 1, 2].map((i) => (
        <div key={i} className="card" style={{ marginBottom: 12 }}>
          <Bar w={35} h={16} mb={12} />
          <div className="grid cols-2">
            {[0, 1].map((j) => (
              <div key={j} className="card" style={{ marginBottom: 0 }}>
                <Bar w={55} h={14} />
                <Bar w={80} h={10} />
                <Bar w="100%" h={6} mb={0} />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

/** A unit page: title, progress card, then a stack of collapsed sections. */
export function UnitSkeleton() {
  return (
    <div className="page page-wide" role="status" aria-label="Loading the unit">
      <Bar w={20} h={20} mb={14} />
      <Bar w={45} h={26} mb={6} />
      <Bar w={55} h={12} mb={18} />

      <div className="card" style={{ marginBottom: 16 }}>
        <Bar w={30} h={12} />
        <Bar w="100%" h={6} mb={0} />
      </div>

      {[0, 1, 2, 3, 4, 5].map((i) => (
        <div key={i} style={{ marginBottom: 10 }}>
          <Bar w={`${28 + (i % 3) * 8}%`} h={18} mb={0} />
        </div>
      ))}
    </div>
  );
}
