# Numbers, Bits & Grids — expansion roadmap

Stage 4 of the DSA Curriculum (`tools/dsa_s4_numbers.py`): **Math & Number
Theory → Bit Manipulation → Simulation & Matrices**. 3 units, 50 problems as of
SEED_VERSION 14.

## Audit: where the stage stands

Stage 3 went through two expansion rounds (see `ORDER_SEARCH_ROADMAP.md`).
Stage 4 had none, so it is missing every layer those rounds added.

| Depth layer | Stage 3 (Order & Search) | Stage 4 (Numbers, Bits & Grids) |
| --- | --- | --- |
| Stage router (`_route`) | 16 rows | **none** |
| Stage cheat sheet | yes | **none** |
| Loop invariant (`_inv`) | 5 / 5 | **0 / 3** |
| Variant family (`_var`) | 5 / 5 | **0 / 3** |
| Slow → fast rewrites (`_rw`) | 5 / 5 | **0 / 3** |
| Internals | 3 / 5 | **0 / 3** |
| Build it from scratch | 5 / 5 | **0 / 3** |
| Worked traces | 4–5 each | 1–2 each |
| Big-O drills | 8 each | 5 each |
| Spot-the-bug quizzes | 6 each | **0** |
| Stuck triage | 6 each | **0** |
| Edge cases | 8 each | **0** |
| Worked solution | 1 each | **0** |

Other gaps found while reading the units:

- **11 ladder problems have no rung note**: `is-multiple`, `gcd`, `power-of-two`,
  `single-number`, `rock-paper-scissors`, `traffic-light`, `color-bomb-explosion`,
  `territory-capture`, `rotate-array-right`, `rotate-matrix-90`, `spiral-order`.
- **Number theory** stops at the sieve and Fermat. Nothing covers prime
  factorisation as a skill, the smallest-prime-factor sieve, Euler's totient,
  the extended Euclidean algorithm (inverses modulo a *composite*), the Chinese
  remainder theorem, a segmented sieve, or the √n divisor-block trick for sums
  of ⌊n/i⌋.
- **Bit manipulation** has no problem on subset enumeration by mask, Gosper's
  hack, XOR over a range, counting set bits over 1…n, per-bit contribution
  counting, or greedy bit-by-bit maximisation. It has no on-ramp below Easy, and
  its weight (1) under-sells the representation every bitmask DP uses.
- **Simulation** has no on-ramp simpler than `robot-grid-walk`, nothing on
  diagonals, no ring (layer) rotation, no "tilt/gravity" simulation, no
  multi-structure simulation (a snake needs a deque and a set), and no problem
  that forces **cycle detection** — although the unit's own signal table says
  "simulate 10⁹ steps → look for a cycle".

## Two new features (generic fields, authored for this stage first)

1. **Interactive lab** (`lab` on `_unit`, rendered by `UnitLab.tsx` on the
   Learn tab). A playground that computes live in the browser, no judge:
   - `bits` — type integers, see their 32-bit two's-complement layout, and
     every operator's result side by side (`&`, `|`, `^`, `~`, `<<`, `>>`,
     `>>>`, `x & (x − 1)`, `x & −x`, `Integer.bitCount`), with the bits that
     changed highlighted.
   - `modular` — type `a`, `b`, `m`: gcd, lcm, extended-Euclid coefficients,
     `a⁻¹ mod m` (or why none exists), `aᵇ mod m` with the square-and-multiply
     steps shown, the prime factorisation and φ.
   - `grid` — pick a size, click a cell: its 4- and 8-neighbours (clipped at
     the border), where it goes under a 90° rotation / transpose / flip, its
     diagonal and anti-diagonal ids (`i − j`, `i + j`), its ring index, and
     where it falls in spiral order.
   Presets are authored data (`_lab(kind, intro, presets)`), so a unit decides
   what to load first.
2. **Work it out by hand** (`drills` on `_unit`, `_calc(prompt, answer, why,
   accept)`). Typed-answer cards — *"what is `13 ^ 11`?"*, *"φ(36)?"*, *"where
   does cell (1, 3) of a 4×5 grid go after a clockwise rotation?"* — graded by
   exact match after normalisation, scheduled like the other cards as
   `dsa-calc:<unit>:<i>`, and counted in the Review tab's deck. Multiple choice
   lets you recognise; typing the number proves you can compute it.

Both go through all four layers (generator helper → lint → `models.rs` →
`types.ts` → UI), with Rust mirrors of the lints.

## The list

### A. Stage level
1. **Stage router**: ~16 `_route` rows, each with its `not_when` near miss
   (√n vs sieve vs SPF sieve; "mod 10⁹+7" vs "mod m, m not prime"; XOR pairs vs
   triples; "all subsets, n ≤ 20" vs n = 40; simulate vs find the cycle; rotate
   vs transpose).
2. **Stage goal rewrite**: a "what each unit looks inside" table and a
   paragraph on the confusable pairs.
3. **Stage cheat sheet**: every template on one page, the bugs that fail hidden
   tests, and the costs to quote.
4. **Lint coverage**: add all three units to `_NEEDS_INVARIANT`,
   `_NEEDS_VARIANTS`, `_NEEDS_REWRITES`, `_NEEDS_BUILD_IT`, `_NEEDS_INTERNALS`
   and `_NEEDS_HELP`, plus a new `_NEEDS_LAB` / `_NEEDS_DRILLS`. Mirror them in
   `verify_dsa_curriculum.rs`.

### B. Math & Number Theory
5. **Invariant**: Euclid — `gcd(a, b)` is unchanged by `(a, b) → (b, a mod b)`,
   plus extended Euclid's `a·x + b·y = r` row invariant.
6. **Variants** (≥ 9): trial division, factorisation, sieve, SPF sieve,
   segmented sieve, gcd/lcm, extended Euclid, fast power mod p, Fermat inverse,
   factorial tables, CRT, totient, divisor blocks.
7. **Rewrites**: primality to n → to √n; n trial divisions → one sieve;
   `(a * b) / gcd` → `a / gcd * b`; per-query factorials → tables; Σ⌊n/i⌋
   one by one → by blocks.
8. **Internals**: why `long` is the working type (2⁶³ vs (10⁹+7)²), the
   prime-number theorem as a size estimate, why Euclid is O(log) (Lamé /
   Fibonacci worst case), `BigInteger` and `Math.floorMod`.
9. **Build it**: a number-theory toolkit class, tested against brute force.
10. **Traces**: extended Euclid table, the SPF sieve filling in, √n divisor
    blocks for n = 20.
11. New problems: `prime-factorization` (E), `divisor-count-queries` (M, SPF
    sieve), `coprime-count` (M, totient), `inverse-mod-any` (M, extended
    Euclid), `two-clocks-align` (H, CRT with non-coprime moduli),
    `primes-in-window` (H, segmented sieve), `floor-quotient-sum` (H, divisor
    blocks).
12. New rungs **Factorisation**, **Inverses and congruences**, **Beyond √n**.
13. Notes, checks, pitfalls, signals, Big-O, quizzes, stuck, edge cases,
    walkthrough (`two-clocks-align`), drills, lab (`modular`).

### C. Bit Manipulation
14. **Invariant**: Kernighan — `count + popcount(x)` equals the original
    popcount, and each iteration removes exactly one set bit.
15. **Variants** (≥ 9): test/set/clear/toggle, XOR fold, lowbit / clear
    lowbit, popcount DP, subset enumeration, submask enumeration, Gosper's
    hack, per-bit contribution, greedy high-bit-first, XOR prefix.
16. **Rewrites**: 32 shifts → Kernighan; hash map for the loner → XOR; O(n²)
    pair XOR sum → per-bit counting; recompute each subset's sum → build from
    `mask & (mask − 1)`; XOR loop over [l, r] → period-4 formula.
17. **Internals**: two's complement, `>>` vs `>>>`, shift counts mod 32/64,
    `Integer.bitCount` / `numberOfTrailingZeros` as intrinsics, `BitSet`,
    `long` masks up to 64.
18. **Build it**: a `Bits` utility class plus a brute-force tester, then a
    64-element `long` set.
19. **Traces**: Gosper's hack step by step, submask enumeration, missing /
    duplicate XOR split.
20. **Weight 1 → 2**: it is the representation bitmask DP is built on, and the
    unit now carries enough to justify it.
21. New problems: `light-panel` (I, on-ramp), `range-xor` (M, period 4),
    `set-bits-up-to-n` (M), `next-same-popcount` (M, Gosper), `budget-subsets`
    (M, subset sums by lowbit), `missing-and-duplicate` (M, XOR split),
    `pair-xor-total` (M, per-bit contribution), `max-and-pair` (M, greedy by
    bit).
22. New rungs **Masks as sets**, **Bit by bit**.
23. Notes, checks, pitfalls, signals, Big-O, quizzes, stuck, edge cases,
    walkthrough (`pair-xor-total`), drills, lab (`bits`).

### D. Simulation & Matrices
24. **Invariant**: the spiral — everything outside `[top..bot] × [left..right]`
    has been emitted exactly once — plus "every cell reads generation t".
25. **Variants** (≥ 9): direction array, copy-then-swap, in-place encoding,
    transpose/flip rotation, ring rotation, spiral boundaries, diagonal keys
    (`i − j`, `i + j`), gravity/compaction, cycle detection, deque snake.
26. **Rewrites**: rotate by index formula → transpose + reverse; k single-step
    ring rotations → one `k mod len` shift; simulate N days → find the cycle;
    per-step neighbour recount → deque + set; a `k`-buffer rotation → three
    reversals.
27. **Internals**: row-major layout and cache lines (why `i` outer, `j` inner),
    `int[][]` as an array of arrays (jagged, `clone()` is shallow), flattening
    `(i, j) ↔ i·cols + j`.
28. **Build it**: a `Grid` helper (neighbours, rotate, transpose, spiral,
    flatten), property-tested (rotate four times = identity, etc.).
29. **Traces**: spiral boundaries shrinking, tilt compaction of one row, cycle
    detection on a lamp row.
30. New problems: `transpose-matrix` (I, on-ramp), `diagonal-sums` (E),
    `striped-wallpaper` (E, Toeplitz), `rotate-rings` (M), `tilt-the-board`
    (M), `snake-on-grid` (M), `lamp-row-after-days` (H, cycle detection).
31. New rungs **Diagonals and rings**, **Bigger machines**, **Too many steps**.
32. Notes, checks, pitfalls, signals, Big-O, quizzes, stuck, edge cases,
    walkthrough (`lamp-row-after-days`), drills, lab (`grid`).

### E. Finishing
33. Rung notes for all 11 unnoted problems.
34. Place every new problem, keep rungs climbing and the weight bands sensible.
35. Bump `SEED_VERSION`, regenerate, run `verify_dsa_curriculum`, in-process
    Python-vs-Java agreement, and `VERIFY_SLUGS=… verify_seeds` on the batch.
36. Front end: `UnitLab.tsx` and the calc cards, vitest for the pure helpers,
    `tsc`, `vite build`.
37. Update `DSA_ROADMAP.md` and the curriculum memory.

## Status: implemented (SEED_VERSION 15)

All 37 items shipped. The stage went from 50 to 72 problems (731 in the bank).

| Unit | Required / total | Traces | Big-O | Quizzes | Stuck | Edge cases | Work-it-out cards | Lab | Worked solution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Math & number theory | 9 / 27 | 5 | 8 | 6 | 6 | 10 | 12 | `modular` | `two-clocks-align` |
| Bit manipulation | 9 / 23 | 6 | 8 | 6 | 6 | 10 | 12 | `bits` | `pair-xor-total` |
| Simulation & matrices | 9 / 26 | 4 | 8 | 6 | 6 | 11 | 11 | `grid` | `lamp-row-after-days` |

Each unit also gained an invariant, 10–12 variants, 5 rewrites, internals, a build-it
exercise, and new skeletons, signals, costs, pitfalls and checks. The stage has a
17-row router and a cheat sheet. All three units sit inside their weight bands.

**Changes to the plan**

- Bit manipulation moved to weight 2 as planned. To keep each unit inside its band,
  most new problems went to optional rungs. There are two new optional rungs:
  **Beyond √n** in number theory and **More bit tricks** in bits.
- `diagonal-sums` and `snake-on-grid` moved to the optional **More grids and
  machines** rung, and `set-matrix-zeroes` moved there from the required ladder.
  `spiral-order` took its place in the required ladder, because the unit's
  invariant is the spiral's.
- The lamp rule (Wolfram's rule 90) is invertible for even widths, so only odd
  widths have a pre-period. The pre-period trace, edge case and hidden test use
  `00001` for that reason.

**Verification**

- For all 22 new problems, the Python and Java references agree on every case, and
  the real judge accepts both (`VERIFY_SLUGS=… cargo test --test verify_seeds`).
  Brute-force oracles agree on 300 random inputs each.
- The generator lints (`_NEEDS_LAB`, `_NEEDS_DRILLS`, and all six older lists
  extended) pass, and so do their Rust mirrors: `verify_dsa_curriculum`, 7/7.
- Every quiz and card answer was checked by running a Python twin (55 checks), and
  every edge-case input was run through its problem's reference or matched against
  its stored example format.
- `tsc` passes, as do 329 vitest tests (14 new, for `lib/unitLab.ts`). The labs and
  cards were checked in the mock dev server, with no console errors.
