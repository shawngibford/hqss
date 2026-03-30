# Phase 2: Generation Bug Fixes - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-30
**Phase:** 02-generation-bug-fixes
**Areas discussed:** Smoke test design, Seed strategy, Window assembly, Variance validation

---

## Smoke Test Design

| Option | Description | Selected |
|--------|-------------|----------|
| Stats + visual | Print mean, std, min, max for each model vs real. KDE overlay plot. Flag if std outside 2x range. | ✓ |
| Stats only | Print comparison table, no plots. Flag anomalies with warnings. | |
| Stats + assertions | Same stats table but with hard assert statements that fail the cell. | |

**User's choice:** Stats + visual
**Notes:** None

| Option | Description | Selected |
|--------|-------------|----------|
| Small sample (~10 curves) | Fast enough to run routinely. Full generation happens in main loop. | ✓ |
| Full pipeline (250 curves) | More thorough but tied to slow generation loop. | |

**User's choice:** Small sample
**Notes:** None

---

## Seed Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Offset scheme | seed = base_seed + (size_idx * 1000) + (rep_idx * 100). Deterministic, no collisions. | ✓ |
| Explicit seed list | Flat list of 9 unique seeds in config cell. More readable but manual. | |
| Hash-based | seed = hash(f'{model}_{size}_{rep}') % 2^31. Scales but less readable. | |

**User's choice:** Offset scheme
**Notes:** None

| Option | Description | Selected |
|--------|-------------|----------|
| Per rep x size only | Same seed set across all 4 models. Architectures differ so outputs independent. | ✓ |
| Per model too | Add model offset (+10000 per model). Guarantees RNG state differs across models. | |

**User's choice:** Per rep x size only
**Notes:** None

---

## Window Assembly

| Option | Description | Selected |
|--------|-------------|----------|
| Window per curve, then concat | Extract sliding windows per synthetic curve independently. Concatenate (X, y) arrays. | ✓ |
| Pad boundaries | Concatenate curves with NaN sentinels. Skip windows containing NaN. | |
| You decide | Claude picks approach — just ensure no cross-boundary windows. | |

**User's choice:** Window per curve, then concat
**Notes:** None

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, fix both | Window real and synthetic separately, then concat all (X, y). Eliminates real→synthetic boundary artifacts. | ✓ |
| Synthetic only | Only fix synthetic boundaries. Real+synthetic join is less harmful. | |

**User's choice:** Yes, fix both
**Notes:** None

---

## Variance Validation

| Option | Description | Selected |
|--------|-------------|----------|
| Warning print | Print warning but don't halt execution. Let experiment complete. | ✓ |
| Hard assert | Assert variance within [0.5x, 2x]. Fail cell immediately if violated. | |
| Informational only | Print stats with no flagging. Researcher reads and judges. | |

**User's choice:** Warning print
**Notes:** None

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, check sign bias | Flag if >90% of growth rates are same-sign. Real data is roughly symmetric. | ✓ |
| No, just variance | Keep check focused on variance magnitude. Sign distribution for later phases. | |

**User's choice:** Yes, check sign bias
**Notes:** None

---

## Claude's Discretion

- Exact offset seed formula parameters (base seed, multipliers)
- KDE plot styling and layout
- Warning message formatting
- Whether smoke test is a new cell or integrated into existing generation cell

## Deferred Ideas

None — discussion stayed within phase scope.
