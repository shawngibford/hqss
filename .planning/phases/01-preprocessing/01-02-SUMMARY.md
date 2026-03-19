---
phase: 01-preprocessing
plan: 02
subsystem: data-pipeline
tags: [pennylane, pytorch, jupyter, ablation, qgan, cgan, lstm, par-light]

# Dependency graph
requires:
  - "01-01 simplified preprocessing pipeline (growth_rate, denorm functions)"
provides:
  - "No-PAR qGAN circuit: _qgan_circuit_fn_no_par(noise_params, params_pqc) omits RY block"
  - "No-PAR cGAN class: ClassicalGeneratorNoPAR with forward(self, noise) - no PAR input"
  - "ABLATION_MODELS_INFO dict mapping all 4 models to appropriate generation functions"
  - "PAR_LIGHT ablation pipeline: generation loop + LSTM evaluation + comparison table"
  - "ablation_df DataFrame with With PAR/Without PAR MSE+MAPE and Delta MSE columns"
affects:
  - "Phase 2+ (ablation data in checkpoints/synthetic_ablation/)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "1-channel critic for no-PAR GAN training (vs 2-channel [window|par] for conditioned variants)"
    - "ABLATION_MODELS_INFO mirrors MODELS_INFO structure; VAE entries reuse existing lambdas"
    - "Ablation cells inserted between main results and Section B statistical analysis"

key-files:
  created: []
  modified:
    - hqss_experiment.ipynb

key-decisions:
  - "No-PAR critic uses 1-channel (not 2-channel) — PAR channel has no meaning without PAR conditioning; avoids contaminating the ablation signal"
  - "VAE entries in ABLATION_MODELS_INFO reuse existing generation lambdas — VAEs never used PAR_LIGHT as input so no retraining needed"
  - "10-epoch training for no-PAR GANs (PHASE1_REDUCED=True) — consistent with user override from Plan 01"
  - "FORCE_ABLATION=True — ensures ablation data regenerates on each notebook run during prototyping"
  - "Ablation uses single size (150) and seed (42) — sufficient for qualitative comparison; full sweep reserved for Phase 2"

requirements-completed: [PREP-03]

# Metrics
duration: 5min
completed: 2026-03-19
---

# Phase 01 Plan 02: PAR_LIGHT Ablation Summary

**No-PAR variants of qGAN and cGAN defined (1-channel critics, noise-only inputs), with ablation training, generation loop, LSTM evaluation pipeline, and with-PAR vs without-PAR comparison table (MSE, MAPE, Delta MSE for all 4 models)**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-03-19T06:29:18Z
- **Completed:** 2026-03-19T06:34:12Z
- **Tasks:** 2 (both implementation tasks)
- **Files modified:** 1 (hqss_experiment.ipynb)

## Accomplishments

- Added `_qgan_circuit_fn_no_par(noise_params, params_pqc)` — identical IQP+StronglyEntangling circuit with PAR_LIGHT RY block removed; wrapped as `_qgan_circuit_no_par` QNode reusing same device and diff_method
- Added `ClassicalGeneratorNoPAR` with `forward(self, noise)` — noise-only MLP, no PAR concatenation
- Added `train_qgan_no_par` — WGAN-GP training loop with 1-channel critic, `for real_batch, _ in gan_loader:` to ignore par_batch; saves to `checkpoints/models/qgan_no_par.pt`
- Added `train_cgan_no_par` — same 1-channel critic design, `cgan_gen_no_par(noise)` only; saves to `checkpoints/models/cgan_no_par.pt`
- Added `FORCE_TRAIN_QGAN_NO_PAR = True` and `FORCE_TRAIN_CGAN_NO_PAR = True` flags
- Both no-PAR training cells use `PHASE1_REDUCED` flag (10 epochs per user override)
- Added `_qgan_no_par_generate_one` and `_cgan_no_par_generate_one` generation functions
- Added `ABLATION_MODELS_INFO` dict with keys `qgan_no_par`, `cgan_no_par`, `qvae`, `cvae`; VAE entries use lambda wrappers reusing existing functions
- Added PAR_LIGHT ablation generation loop: `ABLATION_SYNTH_DIR = CKPT_DIR / 'synthetic_ablation'`, `FORCE_ABLATION=True`, generates 150 curves per model
- Added ablation LSTM evaluation loop: mirrors main experiment pattern (train_lstm + evaluate_lstm)
- Added collect_main_results cell loading with-PAR results for side-by-side comparison
- Added `ablation_df` comparison table with columns: Model, With PAR MSE, Without PAR MSE, Delta MSE, With PAR MAPE, Without PAR MAPE
- Added PAR_LIGHT Ablation Summary markdown commentary cell
- All 47 code cells parse without SyntaxError (53 total cells including markdown)

## Task Commits

1. **Task 1: No-PAR model variants and ablation training cells** - `2175930`
2. **Task 2: Ablation generation loop, LSTM evaluation, comparison table** - `eda12d8`

## Files Created/Modified

- `/Users/shawngibford/dev/phd/HQSS/hqss_experiment.ipynb` - 10 new cells added (5 code cells Task 1, 4 code cells + 1 markdown cell Task 2)

## Decisions Made

- **1-channel critic for no-PAR GANs**: The original 2-channel critic concatenates [window | par_light]; without PAR conditioning there is no second channel. Using a 1-channel critic keeps the ablation clean and avoids forcing random noise into the PAR channel
- **VAE entries reuse existing generation lambdas**: VAEs sample from learned latent distributions and never accepted PAR_LIGHT as a generation-time input. The "no-PAR" condition for VAEs is identical to their standard operation, which the comparison table explicitly annotates with N/A
- **10-epoch prototyping**: Consistent with Plan 01 user override; PHASE1_REDUCED=True applies to all training including no-PAR variants

## Deviations from Plan

None — plan executed exactly as written. The 10-epoch training is a continuation of the existing user override from Plan 01 (not a new deviation).

## Issues Encountered

None - all cells parsed correctly on first pass. All automated verification checks passed.

## Next Phase Readiness

- PAR_LIGHT ablation is structurally complete — all model definitions, training, generation, and evaluation cells are in place
- To execute the full ablation: run cells top-to-bottom (training cells will execute at 10 epochs in PHASE1_REDUCED mode)
- For full training: set PHASE1_REDUCED=False to use QGAN_EPOCHS/CGAN_EPOCHS full counts
- Phase 01 is complete — both preprocessing (Plan 01) and PAR_LIGHT ablation (Plan 02) are done

---
*Phase: 01-preprocessing*
*Completed: 2026-03-19*
