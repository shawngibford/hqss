---
phase: 02-generation-bug-fixes
plan: "02"
subsystem: ml-pipeline
tags: [lstm, windowing, numpy, pytorch, jupyter-notebook]

# Dependency graph
requires:
  - phase: 02-generation-bug-fixes
    provides: "Plan 01 fixes — qGAN noise, scaling, seed scheme already applied"
provides:
  - "Per-curve windowing in all 3 LSTM augmentation loops (no cross-boundary window contamination)"
  - "GENBUG-04 fully resolved in main experiment loop, ablation loop, and IBM loop"
affects: [downstream LSTM experiment results, ablation results, IBM evaluation]

# Tech tracking
tech-stack:
  added: []
  patterns: [per-curve windowing accumulation — window each curve independently then concatenate (X,y) arrays]

key-files:
  created: []
  modified:
    - hqss_experiment.ipynb

key-decisions:
  - "D-07/D-08 applied: window real training data and each synthetic curve independently, never concatenate first"
  - "len(ld) > LOOKBACK guard added at each loop to prevent empty arrays from pathologically short curves"

patterns-established:
  - "Per-curve windowing pattern: X_parts/y_parts accumulation — each curve windowed separately, all (X,y) concatenated after"

requirements-completed: [GENBUG-04]

# Metrics
duration: 10min
completed: 2026-03-30
---

# Phase 02 Plan 02: Generation Bug Fixes (GENBUG-04) Summary

**Per-curve LSTM windowing replacing flat-concatenate-then-window in all 3 experiment loops, eliminating cross-boundary window contamination**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-03-30T18:00:00Z
- **Completed:** 2026-03-30T18:10:00Z
- **Tasks:** 1 of 1
- **Files modified:** 1

## Accomplishments

- Fixed GENBUG-04 cross-boundary window contamination in the main LSTM experiment loop (cell 32)
- Fixed the same bug in the PAR_LIGHT ablation LSTM loop (cell 37)
- Fixed the same bug in the IBM LSTM loop (cell 53)
- All 3 locations now window real training data and each synthetic curve independently before concatenating (X, y) arrays

## Task Commits

1. **Task 1: Per-curve windowing in all LSTM loops** - `91f220d` (fix)

**Plan metadata:** _(docs commit follows)_

## Files Created/Modified

- `hqss_experiment.ipynb` - Replaced `augmented = np.concatenate(...)` then `make_lstm_dataset(augmented, ...)` with per-curve windowing (X_parts/y_parts accumulation) in cells 32, 37, and 53

## Decisions Made

- Applied D-07 and D-08 exactly as specified: window real training series independently, window each synthetic curve independently, then `np.concatenate(X_parts, axis=0)` and `np.concatenate(y_parts, axis=0)` for final assembly.
- Added `if len(ld) > LOOKBACK` guard at all 3 locations — this protects against degenerate short curves without affecting normal operation (all curves are 770+ points, LOOKBACK=20).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

The notebook's size (53,737 tokens) exceeded the Read tool's per-call limit, making direct file inspection impossible. Applied changes via Python JSON manipulation (`json.load` / `json.dump`), targeting cell indices (32, 37, 53) and line indices verified by assertion before replacement. All 6 acceptance criteria passed after patching.

## Known Stubs

None introduced by this plan.

## Next Phase Readiness

- Phase 02 complete: all 4 generation bugs (GENBUG-01 through GENBUG-04) are fixed
- Downstream LSTM results (main experiment, ablation, IBM) will be correct once regenerated with `FORCE_GENERATE=True` and `FORCE_LSTM=True`
- Existing checkpoint files in `checkpoints/synthetic/` were generated with pre-fix code (GENBUG-01/02/03) — should be deleted or `FORCE_GENERATE=True` set before any evaluation run

---
*Phase: 02-generation-bug-fixes*
*Completed: 2026-03-30*
