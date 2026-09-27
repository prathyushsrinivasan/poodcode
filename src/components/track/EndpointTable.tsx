/**
 * An HTTP contract as a table: method, path, purpose, request, response,
 * status. The Backend Lab and Projects each had their own copy, with a
 * `cursor: default` inline on every cell to undo the list-table styling.
 */

import type { Project } from "../../types";

export type Endpoint = Project["endpoints"][number];

export function EndpointTable({ endpoints }: { endpoints: Endpoint[] }) {
  return (
    <div className="card table-card">
      <table className="data static">
        <thead>
          <tr>
            <th scope="col">Method</th>
            <th scope="col">Path</th>
            <th scope="col">Purpose</th>
            <th scope="col">Request</th>
            <th scope="col">Response</th>
            <th scope="col">Status</th>
          </tr>
        </thead>
        <tbody>
          {endpoints.map((e, i) => (
            <tr key={i}>
              <td className="mono nowrap endpoint-method">{e.method}</td>
              <td className="mono nowrap">{e.path}</td>
              <td>{e.purpose}</td>
              <td className="mono faint cell-small">{e.request || "—"}</td>
              <td className="mono faint cell-small">{e.response || "—"}</td>
              <td className="mono nowrap cell-small">{e.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
