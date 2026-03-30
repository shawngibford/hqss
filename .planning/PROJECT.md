# HQSS — Hybrid Quantum Synthetic Sampling

## What This Is

A single-notebook experimental pipeline comparing quantum circuit ansätze (qGAN, qVAE) against classical neural networks (cGAN, cVAE) for generating synthetic bioprocess optical density (OD) time series. Generated data augments LSTM forecasting on a small biological dataset. The project is a proof-of-concept for quantum generative models in scientific data augmentation — not a quantum advantage claim.

## Core Value

Demonstrate that quantum circuit ansätze can generate statistically faithful synthetic bioprocess data that improves downstream forecasting, with rigorous experimental methodology that withstands scientific peer review.

## Current Milestone: v1.1 Generation Pipeline & Experimental Rigor

**Goal:** Fix all critical generation bugs uncovered by deep code review, then rebuild the evaluation pipeline on correct foundations — addressing all 8 critical, 17 major, and 15 minor issues.

**Target features:**
- Fix qGAN generation bugs (noise mismatch, `*0.1` scaling) — quantum circuits define their own distributions
- Fix seed collisions, cross-boundary window contamination, training budget asymmetry
- Fix data leakage (generators + preprocessing constants on train-split only)
- Equalize model comparison fairness (HPO, training infrastructure, parameter-matched baselines)
- Implement complete quality evaluation with temporal metrics, proper statistics, N>=10 seeds
- Fix qVAE Softplus logvar, address cVAE mode collapse
- Clean up IBM section, minor issues, missing plots

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] PREP-01: Remove Lambert-W Gaussianization
- [ ] PREP-02: Rename "log returns" to "specific growth rate" with biological justification
- [ ] PREP-03: PAR_LIGHT ablation (with vs without conditioning)
- [ ] QUAL-01: Implement Section A — MMD + EMD computation
- [ ] QUAL-02: Temporal metrics — ACF RMSE, DTW, Fréchet distance
- [ ] QUAL-03: ACF validation — ACF(1–50) synthetic vs real per model
- [ ] QUAL-04: Execute Section B statistical tests (Diebold-Mariano, Kruskal-Wallis, Cliff's delta)
- [ ] QUAL-05: Biological plausibility — monotonicity, range, growth phases
- [ ] QUAL-06: Mode collapse detection — diversity/coverage metrics
- [ ] QUAL-07: Overfitting detection — train/val loss, memorization check
- [ ] EXPR-01: Classical augmentation baselines (Gaussian noise + bootstrap)
- [ ] EXPR-02: N≥10 seeds with proper 95% CIs and multiple-comparisons correction
- [ ] EXPR-03: Report training wall-clock time for all models
- [ ] EXPR-04: Window boundary fix — continuity at qGAN junctions
- [ ] FAIR-01: Parameter-matched classical baseline (~75-param cGAN)
- [ ] FAIR-02: Equalize HPO across all models
- [ ] FAIR-03: Noisy quantum simulator (depolarizing + readout noise)
- [ ] FAIR-04: Equalize training epochs (qVAE/cVAE)
- [ ] DATA-01: Retrain generators on train-split only (fix leakage)
- [ ] DATA-02: Re-run LSTM experiment on leak-free data

### Out of Scope

- IBM quantum hardware execution — deferred until simulator benchmarks are complete
- Real-time or streaming data — single batch experiment
- Multi-organism generalization — single OD trajectory, acknowledged in limitations
- TSTR evaluation — focus is on historical+synthetic augmentation, not synthetic-only training

## Context

- Single self-contained Jupyter notebook (`hqss_experiment.ipynb`, 27 cells)
- Data: `data.csv` — 778 OD + PAR_LIGHT measurements from bioprocess experiment
- External dependencies: qzeta package (qVAE), qGAN checkpoint, PennyLane, PyTorch
- Scientific peer review identified 5 critical, 10 major, and 7 minor issues
- Section A quality metrics cells are currently stubs (pass statements)
- Section B statistical tests are defined but never executed
- All current results use `lightning.qubit` classical simulator

## Constraints

- **Single notebook**: All changes must remain within `hqss_experiment.ipynb`
- **Existing architecture**: qGAN (5 qubits, 4 layers), qVAE (FullQuantumVAE from qzeta) — don't change quantum circuit structure
- **Compute**: Quantum circuit evaluation is slow; N≥10 seeds × 4 models × 3 sizes = significant runtime
- **Dependencies**: qzeta and qGAN repos are external, not modified here

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Remove Lambert-W | No biological justification; borrowed from finance | — Pending |
| Keep log returns (rename to growth rate) | Specific growth rate µ = d(ln(OD))/dt is biologically standard | — Pending |
| Reframe as quantum ansatz PoC | Simulator results can't claim quantum advantage | — Pending |
| Fix leakage last | Iterate on metrics/baselines with existing checkpoints first | ⚠️ Revisit — leakage fix moved earlier in v1.1 |
| Add noisy simulator | More thorough than clean simulator only; bridges to IBM hardware | — Pending |
| Quantum distributions | Quantum circuits define their own distributions — don't layer classical noise on top | — v1.1 principle |
| Fix generation bugs first | qGAN noise mismatch + *0.1 scaling invalidate all qGAN results — must fix before measuring anything | — v1.1 critical |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-30 after Phase 02 (generation-bug-fixes) completion*
