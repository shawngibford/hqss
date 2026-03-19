---
phase: 01-preprocessing
plan: 01
subsystem: data-pipeline
tags: [numpy, preprocessing, jupyter, pytorch, pennylane, growth-rate, normalization]

# Dependency graph
requires: []
provides:
  - "Simplified preprocessing pipeline: OD -> dither -> growth_rate -> z-score -> scale[-1,1] (GANs) or z-score only (VAEs)"
  - "Biological justification markdown cell with specific growth rate equation mu = d(ln OD)/dt"
  - "Renamed variables: log_delta -> growth_rate, norm_log_delta -> norm_growth_rate, LW_MIN/LW_MAX -> GR_MIN/GR_MAX"
  - "Simplified denorm functions: denorm_qgan_output(gr_min, gr_max) and denorm_vae_output(mu, sigma) without Lambert-W"
  - "Phase 1 prototyping flags: PHASE1_REDUCED=True with all 4 models at 10 epochs"
  - "FORCE_TRAIN_* flags set True for pipeline re-verification"
affects:
  - 01-02-PLAN (PAR ablation - uses same preprocessing pipeline)
  - Phase 2+ (all downstream analysis uses growth_rate terminology)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Direct z-score -> scale[-1,1] for GANs without intermediate Gaussianization"
    - "PHASE1_REDUCED flag with conditional epoch selection for quantum models"
    - "Atomic per-cell denorm: qGAN needs gr_min/gr_max; VAEs need only mu/sigma"

key-files:
  created: []
  modified:
    - hqss_experiment.ipynb

key-decisions:
  - "Removed Lambert-W Gaussianization entirely (not commented out) - git history preserves it; biologically unjustified for OD data"
  - "Variable name: growth_rate (not specific_growth_rate or mu_growth) - terse, biologically meaningful, no name collision with MU constant"
  - "All 4 models use 10 epochs for Phase 1 prototyping (user override from plan's 100/20 suggestion) - verify pipeline first, full training in Phase 4"
  - "denorm_vae_output drops delta_lw parameter entirely; sample_gaussian(raw=True) now returns z-scored space which is directly denormalized"
  - "Kept log_delta_to_od function name but updated internal variable and docstring to reference growth_rate - avoids breaking downstream OD reconstruction calls"

patterns-established:
  - "PHASE1_REDUCED pattern: conditional _model_n_epochs = MODEL_EPOCHS_PHASE1 if PHASE1_REDUCED else MODEL_EPOCHS at each training cell"
  - "Return convention: generation functions return (od, gr) not (od, ld)"

requirements-completed: [PREP-01, PREP-02]

# Metrics
duration: 8min
completed: 2026-03-19
---

# Phase 01 Plan 01: Preprocessing Simplification Summary

**Removed Lambert-W Gaussianization from all cells, renamed log_delta -> growth_rate with biological justification cell (mu = d(ln OD)/dt), and configured 10-epoch prototyping flags for all 4 models**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-03-19T06:17:00Z
- **Completed:** 2026-03-19T06:25:10Z
- **Tasks:** 2 (1 implementation + 1 verification)
- **Files modified:** 1 (hqss_experiment.ipynb)

## Accomplishments

- Deleted entire Lambert-W block (_kurtosis_for_delta, minimize_scalar, lambert_w_gaussianize, lambert_w_inverse, DELTA_LW, LW_MIN, LW_MAX) from cell 4 and removed scipy.special.lambertw + scipy.optimize.minimize_scalar imports
- Added biological justification markdown cell with LaTeX equation `mu = d(ln OD)/dt` before preprocessing cell
- Renamed all variable references across 10+ cells: log_delta -> growth_rate, norm_log_delta -> norm_growth_rate, string labels "Log Return"/"Log Returns" -> "Specific Growth Rate"/"Growth Rate"
- Simplified denorm chain: denorm_qgan_output now takes gr_min, gr_max; denorm_vae_output takes only mu, sigma
- Updated VAE DataLoader source from gaussianized -> norm_growth_rate (cell 12)
- Set FORCE_TRAIN_QGAN/QVAE/CGAN/CVAE = True; added PHASE1_REDUCED=True with 10-epoch counts for all 4 models (user override: all 10, not plan's 100/20)
- Updated IBM generation cell (cell 40) to use new denorm signature
- All 43 notebook cells parse without SyntaxError

## Task Commits

1. **Task 1: Remove Lambert-W, rename variables, configure epochs** - `eac9926` (feat)
2. **Task 2: Verification** - no new commit (all checks passed, no code changes needed)

## Files Created/Modified

- `/Users/shawngibford/dev/phd/HQSS/hqss_experiment.ipynb` - Lambert-W removed, growth_rate terminology, simplified denorm, 10-epoch prototyping flags

## Decisions Made

- **All 4 models at 10 epochs** (user override): Plan suggested 100 for qGAN and 20 for qVAE; user override sets all to 10 for pipeline verification before full retrain in Phase 4
- **growth_rate vs specific_growth_rate**: Chose shorter name to avoid verbosity in array expressions; avoids collision with z-score constant MU
- **Kept log_delta_to_od function name**: Updating the function name would break downstream OD reconstruction calls across many cells; updated only its docstring and internal variable names

## Deviations from Plan

### User Override

**1. [User Override] 10 epochs for ALL models (not 100/20 as plan specified)**
- **Found during:** Task 1 (epoch configuration)
- **Issue:** Plan specified QGAN_EPOCHS_PHASE1=100 and QVAE_EPOCHS_PHASE1=20; user explicitly overrode to 10 for all 4 models
- **Fix:** Added CGAN_EPOCHS_PHASE1=10 and CVAE_EPOCHS_PHASE1=10 (not in original plan) and set all to 10
- **Files modified:** hqss_experiment.ipynb (cell 1)
- **Committed in:** eac9926 (Task 1 commit)

---

**Total deviations:** 1 (1 user override)
**Impact on plan:** User-directed change for faster prototyping. All 4 training cells now use 10-epoch prototyping counts when PHASE1_REDUCED=True. Set PHASE1_REDUCED=False or individual epoch counts to restore full training.

## Issues Encountered

None - all cells parsed correctly on first pass. The cell 16 update warning during scripting was a false alarm (the replacement succeeded via a different code path).

## Next Phase Readiness

- Preprocessing pipeline is simplified and consistent — ready for Plan 02 (PAR_LIGHT ablation)
- All FORCE_TRAIN flags are set True — notebook will retrain all 4 models when run top-to-bottom
- 10-epoch prototyping mode is active — run cells 8-14 sequentially to verify pipeline with fast training before full retrain
- Downstream cells (quality metrics, LSTM experiment, statistical analysis) reference growth_rate and ld_curves keys in npz files — compatible with new pipeline

---
*Phase: 01-preprocessing*
*Completed: 2026-03-19*
