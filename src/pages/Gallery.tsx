/**
 * The component gallery — every piece of the design system, in every state.
 *
 * Dev-only (`/ui`, mounted when `VITE_MOCK=1`). It exists so that a change to a
 * token or a component can be checked against all of its states at once,
 * instead of being discovered later on whichever page happened to use the
 * broken one. It is also the page the visual-regression shots are taken from.
 *
 * Every state that matters gets an entry, including the ugly ones: loading,
 * empty, error, disabled, and the longest label anyone will plausibly write.
 */

import { useState } from "react";
import { DiffBadge, Empty, Stat, ClickableRow, Tag, Confidence } from "../components/common";
import { Modal, ConfirmDialog } from "../components/ui/Modal";
import { Tabs, TabPanel } from "../components/ui/Tabs";
import { useToast } from "../components/Toast";
import { Markdown } from "../components/Markdown";
import { TrackSkeleton } from "../components/Skeleton";
import { VerdictBar } from "../components/solve/VerdictBar";
import { useStore } from "../store";
import type { Difficulty, JudgeReport } from "../types";

function Row({ title, note, children }: { title: string; note?: string; children: React.ReactNode }) {
  return (
    <section className="gallery-row">
      <div className="gallery-row-head">
        <h3>{title}</h3>
        {note && <p className="faint">{note}</p>}
      </div>
      <div className="gallery-demo">{children}</div>
    </section>
  );
}

const SAMPLE_REPORT: JudgeReport = {
  status: "wrong",
  passed: 3,
  total: 5,
  runtime_ms: 42,
  memory_kb: 14200,
  compile_error: "",
  not_installed_hint: "",
  results: [
    {
      name: "Case 1",
      kind: "example",
      input: "12 18",
      expected: "6",
      actual: "6",
      stderr: "",
      passed: true,
      timed_out: false,
      runtime_ms: 8,
      memory_kb: 14200,
      truncated: false,
      verdict: "pass",
    },
  ],
};

const MD = `## A lesson heading

Prose with \`inline code\`, a [link](#), and **bold**.

\`\`\`java
public class Main {
    // A comment, so the comment colour is visible too.
    public static void main(String[] args) {
        int total = 0;
        for (int i = 0; i < 10; i++) total += i;
        System.out.println("sum = " + total);
    }
}
\`\`\`

| Column | Another |
|---|---|
| a | b |
`;

export default function Gallery() {
  const toast = useToast();
  const { prefs, setPref, toggleTheme } = useStore();
  const [modal, setModal] = useState(false);
  const [confirm, setConfirm] = useState(false);
  const [tab, setTab] = useState<"one" | "two" | "three">("one");
  const [conf, setConf] = useState(3);

  const difficulties: Difficulty[] = ["Intro", "Easy", "Medium", "Hard"];

  return (
    <div className="page gallery">
      <h1 className="page-title">Component gallery</h1>
      <p className="page-sub">
        Every component in the design system, in every state. Dev-only — this route exists when the
        app runs on fixtures.
      </p>

      <div className="card gallery-controls">
        <strong>View as:</strong>
        <button onClick={toggleTheme}>Toggle theme ({prefs.theme})</button>
        <button onClick={() => setPref("highContrast", !prefs.highContrast)}>
          High contrast: {prefs.highContrast ? "on" : "off"}
        </button>
        <button
          onClick={() =>
            setPref("density", prefs.density === "compact" ? "comfortable" : "compact")
          }
        >
          Density: {prefs.density}
        </button>
      </div>

      <Row title="Buttons" note="Every variant, plus disabled.">
        <button className="primary">Primary</button>
        <button>Secondary</button>
        <button className="ghost">Ghost</button>
        <button className="success">Success</button>
        <button className="danger">Danger</button>
        <button className="danger filled">Danger, filled</button>
        <button disabled>Disabled</button>
        <button className="primary" disabled>
          Primary disabled
        </button>
      </Row>

      <Row title="Badges and difficulty" note="Difficulty colours are per theme (C9).">
        {difficulties.map((d) => (
          <DiffBadge key={d} d={d} />
        ))}
        <span className="badge">plain</span>
        <Tag>tag</Tag>
        <span className="nav-badge">7</span>
      </Row>

      <Row title="Confidence" note="Interactive — click a dot.">
        <Confidence value={conf} onChange={setConf} />
        <span className="dim">value: {conf}</span>
      </Row>

      <Row title="Pills">
        <div className="pill-toggle">
          <span className="pill on">On</span>
          <span className="pill">Off</span>
          <span className="pill">Another</span>
        </div>
      </Row>

      <Row title="Progress">
        <div className="progress gallery-bar">
          <span className="gallery-bar-35" />
        </div>
        <div className="progress gallery-bar">
          <span className="gallery-bar-full" />
        </div>
      </Row>

      <Row title="Stat tiles">
        <Stat value={42} label="Solved" />
        <Stat value="1h 12m" label="Study time" />
      </Row>

      <Row title="Tabs" note="Roving focus, arrow keys, counts (D4).">
        <div className="gallery-wide">
          <Tabs
            idBase="gallery"
            active={tab}
            onChange={setTab}
            tabs={[
              { key: "one", label: "First" },
              { key: "two", label: "Second", count: 4 },
              { key: "three", label: "Empty", count: 0 },
            ]}
          />
          <TabPanel idBase="gallery" active={tab}>
            <p className="dim">Panel for “{tab}”.</p>
          </TabPanel>
        </div>
      </Row>

      <Row title="Toasts" note="Errors persist until dismissed and carry details (E1).">
        <button onClick={() => toast("Plain message")}>Info</button>
        <button onClick={() => toast.success("Saved")}>Success</button>
        <button onClick={() => toast.warning("That might not be what you meant")}>Warning</button>
        <button
          onClick={() =>
            toast.error("Submit failed", {
              detail: "Error: ENOENT: no such file or directory, open 'Main.java'",
            })
          }
        >
          Error with details
        </button>
        <button
          onClick={() =>
            toast("Unit reset.", { action: { label: "Undo", onClick: () => toast.success("Undone") } })
          }
        >
          With undo
        </button>
      </Row>

      <Row title="Dialogs" note="Focus trapped, Escape closes, focus restored (D6).">
        <button onClick={() => setModal(true)}>Open modal</button>
        <button className="danger" onClick={() => setConfirm(true)}>
          Destructive confirm
        </button>
      </Row>

      <Row title="Verdict bar" note="Pinned under the editor on Solve (F5).">
        <div className="gallery-wide">
          <VerdictBar report={null} running={false} runCount={0} onJumpToFailure={() => {}} />
          <VerdictBar report={null} running runCount={1} onJumpToFailure={() => {}} />
          <VerdictBar report={SAMPLE_REPORT} running={false} runCount={3} onJumpToFailure={() => {}} />
          <VerdictBar
            report={{ ...SAMPLE_REPORT, status: "accepted", passed: 5 }}
            running={false}
            runCount={4}
            onJumpToFailure={() => {}}
          />
        </div>
      </Row>

      <Row title="Empty and error states">
        <Empty icon="📭" text="Nothing here yet." />
        <div className="card error-state">
          <strong>Could not load your progress.</strong>
          <p className="dim error-state-detail">TypeError: failed to fetch</p>
          <button>Retry</button>
        </div>
      </Row>

      <Row title="Clickable row" note="Keyboard-reachable list row (D3).">
        <div className="gallery-wide">
          <ClickableRow className="card week-tile" onActivate={() => toast("Activated")}>
            <strong>A row you can Tab to and press Enter on</strong>
            <p className="dim gallery-tight">Try it with the keyboard.</p>
          </ClickableRow>
          <ClickableRow className="card week-tile" disabled onActivate={() => {}}>
            <strong>Disabled — not in the tab order</strong>
          </ClickableRow>
        </div>
      </Row>

      <Row title="Markdown and code" note="Highlighting matches the Monaco theme (G5).">
        <div className="gallery-wide">
          <Markdown>{MD}</Markdown>
        </div>
      </Row>

      <Row title="Skeleton" note="What a track page shows while its seed parses (E3).">
        <div className="gallery-wide">
          <TrackSkeleton cards={2} />
        </div>
      </Row>

      <Row title="Form controls">
        <input placeholder="Text input" />
        <input type="number" defaultValue={12} />
        <select defaultValue="a">
          <option value="a">Select</option>
          <option value="b">Another</option>
        </select>
        <input placeholder="Disabled" disabled />
        <textarea rows={2} placeholder="Textarea" />
      </Row>

      <Modal
        open={modal}
        onClose={() => setModal(false)}
        title="A dialog"
        description="Escape closes it, Tab cycles inside it, and focus goes back where it was."
        footer={
          <>
            <button onClick={() => setModal(false)}>Cancel</button>
            <span className="spacer" />
            <button className="primary" onClick={() => setModal(false)}>
              Confirm
            </button>
          </>
        }
      >
        <p>Body content.</p>
      </Modal>

      <ConfirmDialog
        open={confirm}
        onClose={() => setConfirm(false)}
        onConfirm={() => {
          setConfirm(false);
          toast.success("Done");
        }}
        title="Delete this thing?"
        consequence="This names exactly what is about to be lost, which window.confirm could not."
        confirmLabel="Delete it"
        extraAction={{ label: "Back up first", onClick: () => toast("Backing up…") }}
      />
    </div>
  );
}
