# Roadmap: HQSS — Generation Pipeline & Experimental Rigor (v1.1)

## Overview

Three phases fix the critical generation bugs uncovered by deep code review, then rebuild the experiment on correct foundations. Phase 2 fixes all generation-time code bugs (noise mismatch, scaling, seed collisions, window contamination) so that generated curves are valid. Phase 3 eliminates data leakage by retraining all generators on the train split only and recomputing preprocessing constants. Phase 4 fixes the LSTM evaluation pipeline (training budget fairness, multi-seed baseline, MAPE replacement) so model comparisons are meaningful.

## Milestones

- Partial **v1.0 Preprocessing** - Phase 1 (completed 2026-03-19)
- In Progress **v1.1 Generation Pipeline & Experimental Rigor** - Phases 2-4

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

<details>
<summary>v1.0 Preprocessing (Phase 1) - COMPLETED 2026-03-19</summary>

- [x] **Phase 1: Preprocessing** - Remove Lambert-W, rename to specific growth rate, add PAR_LIGHT ablation

</details>

### v1.1 Generation Pipeline & Experimental Rigor (In Progress)

- [ ] **Phase 2: Generation Bug Fixes** - Fix qGAN noise/scaling, seed collisions, and window contamination so generated curves are valid
- [ ] **Phase 3: Data Leakage Fix** - Retrain all generators on train-split only with corrected preprocessing constants
- [ ] **Phase 4: LSTM Evaluation Fixes** - Equalize training budget, multi-seed baseline, and replace MAPE with appropriate metric

## Phase Details

<details>
<summary>v1.0 Preprocessing (Phase 1) - COMPLETED 2026-03-19</summary>

### Phase 1: Preprocessing
**Goal**: The data pipeline uses biologically justified normalization and terminology, with PAR_LIGHT conditioning contribution quantified
**Depends on**: Nothing (first phase)
**Requirements**: PREP-01, PREP-02, PREP-03
**Success Criteria** (what must be TRUE):
  1. Lambert-W transform is absent from the notebook; only z-score normalization is applied to specific growth rates
  2. Every occurrence of "log returns" is replaced with "specific growth rate" and a biological justification cell is present
  3. Notebook runs two full generation+LSTM evaluation paths with and without PAR_LIGHT conditioning and reports the performance difference
**Plans:** 2/2 plans complete

Plans:
- [x] 01-01: Remove Lambert-W, rename to specific growth rate, simplify denormalization, retrain models
- [x] 01-02: PAR_LIGHT ablation: no-PAR model variants, generation loop, LSTM comparison table

</details>

### Phase 2: Generation Bug Fixes
**Goal**: All four generative models produce valid synthetic curves from correctly implemented generation code
**Depends on**: Phase 1
**Requirements**: GENBUG-01, GENBUG-02, GENBUG-03, GENBUG-04
**Success Criteria** (what must be TRUE):
  1. qGAN generation uses `torch.randn` noise (matching training distribution), and the `* 0.1` scaling is removed -- generated growth-rate variance is within 2x of real data variance, not 10x suppressed
  2. Each of the 3 seed replicates at size=250 produces entirely unique curves with zero shared seeds across replicates
  3. Sliding windows are created per-curve independently before concatenation -- no window spans the boundary between two different synthetic curves or between synthetic and real data
  4. A smoke test cell confirms all 4 models generate growth-rate distributions with mean and std within a reasonable range of real data (no 10x compression, no all-positive artifacts)
**Plans:** 2 plans

Plans:
- [x] 02-01-PLAN.md — Fix qGAN noise/scaling, seed collisions, and add smoke test cell
- [ ] 02-02-PLAN.md — Fix cross-boundary window contamination in LSTM loops

### Phase 3: Data Leakage Fix
**Goal**: All generative models train exclusively on the training split, eliminating information leakage from the test period
**Depends on**: Phase 2
**Requirements**: DINT-01
**Success Criteria** (what must be TRUE):
  1. The train/test split happens before dataset construction -- `gan_loader` and `vae_loader` contain only windows from the first 80% of the OD series
  2. MU, SIGMA, GR_MIN, and GR_MAX are computed from training-period growth rates only, and a verification cell prints these values alongside the old full-dataset values
  3. All four generative model checkpoints are retrained on train-only loaders and saved as new checkpoints (old checkpoints preserved for comparison)
**Plans**: TBD

Plans:
(none yet -- defined by plan-phase)

### Phase 4: LSTM Evaluation Fixes
**Goal**: The LSTM evaluation pipeline produces fair, interpretable comparisons across all models
**Depends on**: Phase 3
**Requirements**: DINT-02, DINT-03, EVAL-01
**Success Criteria** (what must be TRUE):
  1. Augmented LSTM training uses validation-based early stopping or epoch-proportional training so the baseline and size=250 augmented models receive comparable effective training (not 320x gradient step disparity)
  2. The baseline LSTM runs with the same 3+ seeds as augmented models, reporting mean +/- std -- no single-seed point estimate
  3. MAPE is removed or replaced with symmetric MAPE or RMSSE -- no metric divides by near-zero growth rates producing 100%+ values
  4. The comparison table shows all models evaluated under identical conditions (same seeds, same early stopping, same metrics)
**Plans**: TBD

Plans:
(none yet -- defined by plan-phase)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 (complete) -> 2 -> 3 -> 4

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Preprocessing | v1.0 | 2/2 | Complete | 2026-03-19 |
| 2. Generation Bug Fixes | v1.1 | 0/2 | Planning | - |
| 3. Data Leakage Fix | v1.1 | 0/TBD | Not started | - |
| 4. LSTM Evaluation Fixes | v1.1 | 0/TBD | Not started | - |
