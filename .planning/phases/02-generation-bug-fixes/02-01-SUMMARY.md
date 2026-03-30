---
phase: 02-generation-bug-fixes
plan: 01
subsystem: generation
tags: [pytorch, pennylane, qgan, numpy, scipy, jupyter]

# Dependency graph
requires:
  - phase: 01-preprocessing-fixes
    provides: growth_rate preprocessing pipeline, denorm functions, MU/SIGMA/GR_MIN/GR_MAX constants
provides:
  - "Fixed _qgan_generate_one: torch.randn noise, row-major indexing, no 0.1 scaling"
  - "Fixed _qgan_no_par_generate_one: same noise and scaling fixes (ablation variant)"
  - "Fixed _qgan_generate_one_ibm: same noise and scaling fixes (IBM variant)"
  - "Fixed generation loop: non-overlapping seed scheme across sizes and replicates (GENBUG-03)"
  - "Smoke test cell: stats table, KDE overlay, variance and sign bias warnings"
affects:
  - 02-generation-bug-fixes/02-02 (GENBUG-04 cross-boundary window fix)
  - any phase that reads synthetic checkpoints or generation functions

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "torch.randn(n_windows, NUM_QUBITS) for qGAN noise -- matches training convention noise = torch.randn(B, NUM_QUBITS)"
    - "noise[i] row-major indexing in generation loop (not noise[:,i] column-major)"
    - "size_idx * 1000 + rep_idx * 100 + k seed offset scheme for non-overlapping curve seeds"
    - "Smoke test generates SMOKE_N=10 curves per model using MODELS_INFO dict iteration"

key-files:
  created: []
  modified:
    - hqss_experiment.ipynb

key-decisions:
  - "Applied GENBUG-01/02 fixes to all 3 qGAN generation variants (main, no_par, IBM) for consistency"
  - "Smoke test inserted as dedicated cell (cell 23) after generation loop -- depends on MODELS_INFO, avoids re-running full loop"
  - "Seed scheme uses rep_idx (not GEN_SEEDS value) for arithmetic; GEN_SEEDS values retained in checkpoint filenames for downstream compatibility"

patterns-established:
  - "Smoke test pattern: iterate MODELS_INFO, generate SMOKE_N curves, print stats table, KDE overlay, flag variance/sign issues"
  - "qGAN noise shape convention: (n_windows, NUM_QUBITS), indexed as noise[i] per window"

requirements-completed: [GENBUG-01, GENBUG-02, GENBUG-03]

# Metrics
duration: 2min
completed: 2026-03-30
---

# Phase 02 Plan 01: Generation Bug Fixes Summary

**Fixed qGAN Gaussian noise mismatch, removed 10x variance-suppressing 0.1 scaling, and added non-overlapping seed scheme across 3 functions + generation loop; new smoke test cell prints per-model stats table and KDE overlay**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-03-30T17:43:20Z
- **Completed:** 2026-03-30T17:45:15Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Fixed GENBUG-01 (noise mismatch) and GENBUG-02 (0.1 scaling) in all 3 qGAN generation functions: `_qgan_generate_one`, `_qgan_no_par_generate_one`, `_qgan_generate_one_ibm`
- Fixed GENBUG-03 (seed collision) in generation loop: `curve_seed = size_idx * 1000 + rep_idx * 100 + k` guarantees non-overlapping ranges across all 3 sizes and 3 replicates
- Added smoke test cell (cell 23) with SMOKE_N=10, stats comparison table, KDE overlay plot, and variance/sign bias warnings (decisions D-01 through D-04, D-09, D-10)

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix qGAN noise distribution, remove 0.1 scaling, fix seed scheme** - `da8467e` (fix)
2. **Task 2: Add smoke test cell with stats table, KDE overlay, and variance/sign warnings** - `25c504d` (feat)

**Plan metadata:** (docs commit to follow)

## Files Created/Modified

- `hqss_experiment.ipynb` - Fixed cells 20, 21, 22, 51; inserted new smoke test cell at position 23

## Decisions Made

- Extended GENBUG-01/02 fixes to `_qgan_generate_one_ibm` (IBM section, cell 51) even though plan mentioned it as secondary ("check IBM section") — same root cause, applied consistently
- Smoke test uses `rep_idx` in arithmetic but retains `seed` (from GEN_SEEDS) in checkpoint filenames to preserve downstream compatibility
- Smoke test imports `gaussian_kde` inline for cell independence (already imported upstream, but explicit import allows running cell in isolation)

## Deviations from Plan

None - plan executed exactly as written. IBM fix was explicitly mentioned in the plan action ("Check the IBM section... apply the same noise fix").

## Issues Encountered

None - all bug locations were exactly where the research doc indicated. String replacements applied cleanly on first attempt.

## User Setup Required

None - no external service configuration required.

**Important note for next run:** Existing synthetic checkpoints in `checkpoints/synthetic/` were generated with the buggy code. Set `FORCE_GENERATE=True` or delete those files before running the full generation loop to ensure corrected code is used. Similarly, `checkpoints/lstm_results/` are invalid and should be regenerated.

## Next Phase Readiness

- Plan 01 complete: GENBUG-01, GENBUG-02, GENBUG-03 fixed
- Plan 02 (GENBUG-04: cross-boundary window contamination in LSTM loop) is independent and can proceed immediately
- Smoke test cell (cell 23) is ready to validate generation functions after any future changes

---
*Phase: 02-generation-bug-fixes*
*Completed: 2026-03-30*
