# Roadmap: HQSS — Scientific Rigor (v1.0)

## Overview

Four phases take the HQSS notebook from a working proof-of-concept to a publication-ready experiment. Phase 1 fixes the data pipeline so everything downstream uses biologically justified preprocessing. Phase 2 implements the full quality evaluation suite against existing checkpoints. Phase 3 fixes model-level fairness issues and the qGAN window boundary artifact. Phase 4 fixes data leakage — retraining all generators on the train split only — and closes the milestone.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Preprocessing** - Remove Lambert-W, rename to specific growth rate, add PAR_LIGHT ablation (completed 2026-03-19)
- [ ] **Phase 2: Quality Metrics and Experiment Design** - Implement all quality metrics and complete the experiment design (baselines, seeds, timing)
- [ ] **Phase 3: Model Fairness** - Add parameter-matched baseline, equalize HPO/epochs, add noisy simulator, fix qGAN window boundaries
- [ ] **Phase 4: Data Integrity** - Retrain all generators on train-split only and re-run LSTM experiment on leak-free data

## Phase Details

### Phase 1: Preprocessing
**Goal**: The data pipeline uses biologically justified normalization and terminology, with PAR_LIGHT conditioning contribution quantified
**Depends on**: Nothing (first phase)
**Requirements**: PREP-01, PREP-02, PREP-03
**Success Criteria** (what must be TRUE):
  1. Lambert-W transform is absent from the notebook; only z-score normalization is applied to specific growth rates
  2. Every occurrence of "log returns" is replaced with "specific growth rate" and a biological justification cell (µ = d(ln OD)/dt) is present
  3. Notebook runs two full generation+LSTM evaluation paths — one with PAR_LIGHT conditioning, one without — and reports the performance difference
**Plans:** 2/2 plans complete

Plans:
- [x] 01-01-PLAN.md — Remove Lambert-W, rename to specific growth rate, simplify denormalization, retrain models
- [ ] 01-02-PLAN.md — PAR_LIGHT ablation: no-PAR model variants, generation loop, LSTM comparison table

### Phase 2: Quality Metrics and Experiment Design
**Goal**: The notebook produces a complete, statistically sound quality evaluation of all four generative models using existing checkpoints
**Depends on**: Phase 1
**Requirements**: QUAL-01, QUAL-02, QUAL-03, QUAL-04, QUAL-05, QUAL-06, QUAL-07, EXPR-01, EXPR-02, EXPR-03
**Success Criteria** (what must be TRUE):
  1. Section A cells compute and display MMD (RBF kernel) and EMD (Wasserstein-1) for each model vs real data
  2. Temporal metrics (ACF RMSE, DTW, Fréchet distance) are computed and displayed alongside MMD/EMD
  3. ACF(lag 1–50) comparison plots exist for each model with RMSE reported
  4. Section B statistical tests (Diebold-Mariano, Kruskal-Wallis, Cliff's delta) execute and display results with multiple-comparisons correction
  5. Gaussian noise and bootstrap resampling baselines run through the same LSTM evaluation pipeline as the generative models, and N≥10 seeds with 95% CIs are reported with wall-clock training times for all models
**Plans**: TBD

Plans:
(none yet — defined by plan-phase)

### Phase 3: Model Fairness
**Goal**: All generative models compete under equal conditions and the qGAN window boundary artifact is eliminated
**Depends on**: Phase 2
**Requirements**: FAIR-01, FAIR-02, FAIR-03, FAIR-04, EXPR-04
**Success Criteria** (what must be TRUE):
  1. A ~75-parameter classical generator baseline is present and runs through the same LSTM evaluation as qGAN
  2. All models use the same HPO budget or documented principled defaults; qVAE and cVAE train for equal epochs (or the difference is justified in a comment)
  3. qGAN and qVAE generation runs under a noisy simulator (depolarizing + readout noise via default.mixed) and results are displayed alongside clean simulator results
  4. qGAN-generated sequences show no visible discontinuities at 10-point window junctions, validated by a smoothness metric cell
**Plans**: TBD

Plans:
(none yet — defined by plan-phase)

### Phase 4: Data Integrity
**Goal**: All generators are trained exclusively on the train split, eliminating data leakage, and the final LSTM results reflect leak-free evaluation
**Depends on**: Phase 3
**Requirements**: DATA-01, DATA-02
**Success Criteria** (what must be TRUE):
  1. All four generative models are retrained using only windows from the first 80% of the OD series, with no access to the held-out test period
  2. The LSTM augmentation experiment re-runs on leak-free synthetic data and the notebook displays a before/after performance comparison table
**Plans**: TBD

Plans:
(none yet — defined by plan-phase)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Preprocessing | 2/2 | Complete   | 2026-03-19 |
| 2. Quality Metrics and Experiment Design | 0/TBD | Not started | - |
| 3. Model Fairness | 0/TBD | Not started | - |
| 4. Data Integrity | 0/TBD | Not started | - |
