import { useMemo, useState } from "react";
import type { Lab } from "../types";
import { Markdown } from "./Markdown";
import {
  bitRows,
  bits32,
  cellImages,
  extendedEuclid,
  factorize,
  gcdBig,
  javaLongMul,
  neighbours,
  parseBig,
  phiFrom,
  powerSteps,
  ringOf,
  spiralOrder,
  toInt32,
} from "../lib/unitLab";

/**
 * A unit's interactive lab: a playground that computes live in the page, with
 * the author's presets as one-click starting points. Three kinds, each over the
 * arithmetic in `lib/unitLab.ts`:
 *
 *   bits     two ints and a shift, every operator side by side as 32 bits
 *   modular  gcd / lcm, the extended-Euclid table, square-and-multiply, φ
 *   grid     click a cell: neighbours, images under each rotation, keys, spiral
 */
export function UnitLab({ lab }: { lab: Lab }) {
  const [values, setValues] = useState<Record<string, string>>(
    () => ({ ...(lab.presets[0]?.values ?? {}) })
  );
  const [preset, setPreset] = useState(0);
  const set = (k: string, v: string) => setValues((p) => ({ ...p, [k]: v }));

  return (
    <div className="card" style={{ padding: 14 }}>
      <Markdown>{lab.intro}</Markdown>
      <div className="row" style={{ flexWrap: "wrap", gap: 6, margin: "8px 0 12px" }}>
        {lab.presets.map((p, i) => (
          <button
            key={p.label}
            className={i === preset ? "" : "ghost"}
            style={{ fontSize: 12, padding: "3px 10px" }}
            onClick={() => {
              setPreset(i);
              setValues({ ...p.values });
            }}
          >
            {p.label}
          </button>
        ))}
      </div>
      {lab.kind === "bits" && <BitsLab v={values} set={set} />}
      {lab.kind === "modular" && <ModularLab v={values} set={set} />}
      {lab.kind === "grid" && <GridLab v={values} set={set} />}
    </div>
  );
}

type LabProps = { v: Record<string, string>; set: (k: string, v: string) => void };

function Field({ label, name, v, set, width = 150 }: LabProps & { label: string; name: string; width?: number }) {
  const bad = parseBig(v[name] ?? "") === null;
  return (
    <label className="dim" style={{ fontSize: 13, display: "inline-flex", alignItems: "center", gap: 6 }}>
      {label}
      <input
        className="mono"
        aria-label={label}
        value={v[name] ?? ""}
        onChange={(e) => set(name, e.target.value)}
        style={{ width, borderColor: bad ? "var(--bad)" : undefined }}
      />
    </label>
  );
}

function Bits({ value, compare }: { value: bigint; compare?: bigint }) {
  const s = bits32(value);
  const c = compare === undefined ? null : bits32(compare);
  return (
    <span className="mono" style={{ fontSize: 12, whiteSpace: "nowrap" }}>
      {s.split("").map((ch, i) => (
        <span
          key={i}
          style={{
            marginLeft: i > 0 && i % 8 === 0 ? 6 : 0,
            color: c && c[i] !== ch ? "var(--accent)" : ch === "1" ? undefined : "var(--faint, #888)",
            fontWeight: c && c[i] !== ch ? 700 : undefined,
          }}
        >
          {ch}
        </span>
      ))}
    </span>
  );
}

function BitsLab({ v, set }: LabProps) {
  const a = parseBig(v.a ?? "");
  const b = parseBig(v.b ?? "");
  const k = parseBig(v.k ?? "");
  const rows = a !== null && b !== null && k !== null ? bitRows(a, b, k) : null;
  return (
    <>
      <div className="row" style={{ gap: 14, flexWrap: "wrap", marginBottom: 10 }}>
        <Field label="a" name="a" v={v} set={set} />
        <Field label="b" name="b" v={v} set={set} />
        <Field label="shift k" name="k" v={v} set={set} width={70} />
      </div>
      {!rows ? (
        <div className="dim">Type integers (decimal, 0x… or 0b…).</div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table className="data">
            <thead>
              <tr>
                <th>Expression</th>
                <th>32 bits (changed vs a in colour)</th>
                <th>Value</th>
                <th>Meaning</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ cursor: "default" }}>
                <td className="mono">a</td>
                <td><Bits value={a!} /></td>
                <td className="mono">{String(toInt32(a!))}</td>
                <td className="dim">{toInt32(a!) !== a ? "wrapped to a Java int" : "as typed"}</td>
              </tr>
              <tr style={{ cursor: "default" }}>
                <td className="mono">b</td>
                <td><Bits value={b!} /></td>
                <td className="mono">{String(toInt32(b!))}</td>
                <td />
              </tr>
              {rows.map((r) => (
                <tr key={r.expr} style={{ cursor: "default" }}>
                  <td className="mono">{r.expr}</td>
                  <td>{r.expr.includes("(a)") ? "" : <Bits value={r.value} compare={a!} />}</td>
                  <td className="mono">{String(r.value)}</td>
                  <td className="dim">{r.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function ModularLab({ v, set }: LabProps) {
  const a = parseBig(v.a ?? "");
  const b = parseBig(v.b ?? "");
  const m = parseBig(v.m ?? "");
  const ok = a !== null && b !== null && m !== null && m >= 1n && a >= 0n && b >= 0n;
  const res = useMemo(() => {
    if (!ok) return null;
    const g = gcdBig(a!, m!);
    const ee = extendedEuclid(a!, m!);
    const pw = powerSteps(a!, b!, m!);
    const fac = factorize(m!);
    const fermat = m! > 2n ? powerSteps(a!, m! - 2n, m!).value : null;
    return { g, lcm: g === 0n ? 0n : (a! / g) * m!, ee, pw, fac, fermat };
  }, [ok, a, b, m]);

  return (
    <>
      <div className="row" style={{ gap: 14, flexWrap: "wrap", marginBottom: 10 }}>
        <Field label="a" name="a" v={v} set={set} width={190} />
        <Field label="exponent b" name="b" v={v} set={set} width={130} />
        <Field label="modulus m" name="m" v={v} set={set} width={130} />
      </div>
      {!res ? (
        <div className="dim">Type non-negative integers, with m ≥ 1.</div>
      ) : (
        <>
          <div className="grid cols-2" style={{ gap: 8, marginBottom: 12 }}>
            <Stat label="gcd(a, m)" value={String(res.g)} />
            <Stat label="lcm(a, m) = a / gcd · m" value={String(res.lcm)} />
            <Stat
              label="a⁻¹ mod m (extended Euclid)"
              value={res.ee.inverse === null ? `none — gcd is ${res.ee.gcd}` : String(res.ee.inverse)}
            />
            <Stat
              label="Fermat's a^(m−2) mod m"
              value={
                res.fermat === null
                  ? "—"
                  : res.ee.inverse !== null && res.fermat === res.ee.inverse
                  ? `${res.fermat} ✓ agrees`
                  : `${res.fermat} ✗ wrong here (m is not prime or a ≡ 0)`
              }
            />
            <Stat label={`a^b mod m`} value={String(res.pw.value)} />
            <Stat
              label="m factorised, and φ(m)"
              value={
                res.fac === null
                  ? "too large to factor here"
                  : res.fac.length === 0
                  ? "—"
                  : `${res.fac.map(([p, e]) => (e > 1 ? `${p}^${e}` : String(p))).join(" · ")}   φ = ${phiFrom(m!, res.fac)}`
              }
            />
            <Stat
              label="a · a in a Java long (no reduction)"
              value={
                javaLongMul(a!, a!) === a! * a! ? `${a! * a!} (fits)` : `${javaLongMul(a!, a!)} (overflowed!)`
              }
            />
          </div>
          <h4 style={{ margin: "8px 0 4px" }}>Extended Euclid — every row keeps r ≡ a·s (mod m)</h4>
          <div style={{ overflowX: "auto", marginBottom: 12 }}>
            <table className="data">
              <thead>
                <tr><th>q</th><th>r₀</th><th>s₀</th><th>r₁</th><th>s₁</th></tr>
              </thead>
              <tbody>
                {res.ee.steps.map((s, i) => (
                  <tr key={i} style={{ cursor: "default" }}>
                    <td className="mono">{s.q === null ? "start" : String(s.q)}</td>
                    <td className="mono">{String(s.r0)}</td>
                    <td className="mono">{String(s.s0)}</td>
                    <td className="mono">{String(s.r1)}</td>
                    <td className="mono">{String(s.s1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <h4 style={{ margin: "8px 0 4px" }}>Square and multiply — one row per bit of b</h4>
          <div style={{ overflowX: "auto" }}>
            <table className="data">
              <thead>
                <tr><th>remaining e</th><th>low bit</th><th>base (squared each row)</th><th>result</th></tr>
              </thead>
              <tbody>
                {res.pw.steps.map((s, i) => (
                  <tr key={i} style={{ cursor: "default" }}>
                    <td className="mono">{String(s.e)}</td>
                    <td className="mono">{String(s.bit)}</td>
                    <td className="mono">{String(s.base)}</td>
                    <td className="mono">{s.bit === 1n ? <strong>{String(s.result)}</strong> : String(s.result)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="card" style={{ padding: "8px 10px", margin: 0 }}>
      <div className="dim" style={{ fontSize: 12 }}>{label}</div>
      <div className="mono" style={{ wordBreak: "break-all" }}>{value}</div>
    </div>
  );
}

const GRID_MAX = 12;

function GridLab({ v, set }: LabProps) {
  const clamp = (x: bigint | null, lo: number, hi: number) =>
    x === null ? lo : Math.max(lo, Math.min(hi, Number(x)));
  const r = clamp(parseBig(v.rows ?? ""), 1, GRID_MAX);
  const c = clamp(parseBig(v.cols ?? ""), 1, GRID_MAX);
  const i = clamp(parseBig(v.i ?? ""), 0, r - 1);
  const j = clamp(parseBig(v.j ?? ""), 0, c - 1);
  const [eight, setEight] = useState(true);
  const [show, setShow] = useState("Rotate 90° clockwise");

  const nb = new Set(neighbours(r, c, i, j, eight).map(([a, b]) => `${a},${b}`));
  const spiral = spiralOrder(r, c);
  const spiralIndex = spiral.findIndex(([a, b]) => a === i && b === j);
  const images = cellImages(r, c, i, j);
  const img = images.find((x) => x.name === show) ?? images[0];

  return (
    <>
      <div className="row" style={{ gap: 14, flexWrap: "wrap", marginBottom: 10 }}>
        <Field label="rows" name="rows" v={v} set={set} width={50} />
        <Field label="cols" name="cols" v={v} set={set} width={50} />
        <label className="dim" style={{ fontSize: 13 }}>
          <input type="checkbox" checked={eight} onChange={(e) => setEight(e.target.checked)} /> 8 neighbours
        </label>
        <span className="faint" style={{ fontSize: 12 }}>Click a cell. Up to {GRID_MAX} × {GRID_MAX}.</span>
      </div>
      <div className="row" style={{ gap: 20, flexWrap: "wrap", alignItems: "flex-start" }}>
        <div
          role="grid"
          aria-label="grid"
          style={{ display: "grid", gridTemplateColumns: `repeat(${c}, 30px)`, gap: 2 }}
        >
          {Array.from({ length: r * c }, (_, id) => {
            const a = Math.floor(id / c), b = id % c;
            const sel = a === i && b === j;
            const isNb = nb.has(`${a},${b}`);
            return (
              <button
                key={id}
                title={`(${a}, ${b})  id ${id}`}
                onClick={() => {
                  set("i", String(a));
                  set("j", String(b));
                }}
                style={{
                  width: 30,
                  height: 30,
                  padding: 0,
                  fontSize: 10,
                  background: sel ? "var(--accent)" : isNb ? "color-mix(in srgb, var(--accent) 25%, transparent)" : undefined,
                  color: sel ? "var(--bg, #fff)" : undefined,
                }}
              >
                {spiral.findIndex(([x, y]) => x === a && y === b)}
              </button>
            );
          })}
        </div>
        <div style={{ minWidth: 240, flex: 1 }}>
          <table className="data">
            <tbody>
              <Kv k="Cell" v={`(${i}, ${j})`} />
              <Kv k="Flattened id  i · cols + j" v={`${i} · ${c} + ${j} = ${i * c + j}`} />
              <Kv k={`${eight ? 8 : 4}-neighbours inside the grid`} v={String(nb.size)} />
              <Kv k="↘ diagonal key  i − j" v={String(i - j)} />
              <Kv k="↙ diagonal key  i + j" v={String(i + j)} />
              <Kv k="Ring (layer)" v={String(ringOf(r, c, i, j))} />
              <Kv k="Position in spiral order" v={`${spiralIndex} of ${r * c} (numbers on the cells)`} />
            </tbody>
          </table>
          <div style={{ marginTop: 10 }}>
            <select value={show} onChange={(e) => setShow(e.target.value)} aria-label="transformation">
              {images.map((x) => (
                <option key={x.name}>{x.name}</option>
              ))}
            </select>
            <div className="mono" style={{ marginTop: 6 }}>
              ({i}, {j}) → ({img.to[0]}, {img.to[1]}) in a {img.shape} grid
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function Kv({ k, v }: { k: string; v: string }) {
  return (
    <tr style={{ cursor: "default" }}>
      <td className="dim">{k}</td>
      <td className="mono">{v}</td>
    </tr>
  );
}
