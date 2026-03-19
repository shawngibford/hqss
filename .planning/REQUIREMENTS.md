# Requirements: HQSS

**Defined:** 2026-03-18
**Core Value:** Demonstrate quantum circuit ansätze can generate faithful synthetic bioprocess data with rigorous methodology

## v1 Requirements

Requirements for scientific rigor milestone. Each maps to roadmap phases.

### Preprocessing

- [x] **PREP-01**: Remove Lambert-W Gaussianization — use z-score normalization only on specific growth rates
- [x] **PREP-02**: Rename "log returns" to "specific growth rate" throughout notebook with biological justification text
- [ ] **PREP-03**: PAR_LIGHT ablation — train and generate with vs without light conditioning, quantify contribution to downstream LSTM performance

### Quality Metrics

- [ ] **QUAL-01**: Implement Section A stub cells — compute MMD (RBF kernel) and EMD (Wasserstein-1) on synthetic vs real data
- [ ] **QUAL-02**: Implement temporal quality metrics alongside MMD/EMD — ACF RMSE, dynamic time warping distance, Fréchet distance on full curves
- [ ] **QUAL-03**: ACF validation — compute and compare ACF(lag 1–50) of synthetic samples vs real data for each model, report RMSE
- [ ] **QUAL-04**: Execute and display Section B statistical tests — Diebold-Mariano, Kruskal-Wallis, Cliff's delta with proper output
- [ ] **QUAL-05**: Biological plausibility metrics — monotonicity fraction, OD range validation, growth phase identification for synthetic curves
- [ ] **QUAL-06**: Mode collapse detection — compute diversity metrics (pairwise distance distribution, coverage, density) across generated samples per model
- [ ] **QUAL-07**: Overfitting detection — plot train vs validation loss curves, measure nearest-neighbor distance between synthetic and training windows to detect memorization

### Experiment Design

- [ ] **EXPR-01**: Add classical augmentation baselines — Gaussian noise injection and bootstrap resampling — run through same LSTM evaluation
- [ ] **EXPR-02**: Increase to N≥10 seeds with proper 95% confidence intervals and Bonferroni or BH multiple-comparisons correction
- [ ] **EXPR-03**: Report training wall-clock time for all generative models and LSTM training
- [ ] **EXPR-04**: Window boundary fix — add continuity constraint or smoothing at qGAN 10-point window junctions, validate smoothness

### Model Fairness

- [ ] **FAIR-01**: Add parameter-matched classical baseline (~75-param classical generator) to match qGAN parameter budget
- [ ] **FAIR-02**: Equalize hyperparameter optimization — apply equal HPO budget to all models or use common principled defaults
- [ ] **FAIR-03**: Add noisy quantum simulator results — depolarizing and readout noise models via PennyLane default.mixed
- [ ] **FAIR-04**: Equalize training epochs across model pairs (qVAE 50 → match cVAE 200, or justify difference)

### Data Integrity

- [ ] **DATA-01**: Retrain all four generative models on train-split only windows (first 80% of series) to fix data leakage
- [ ] **DATA-02**: Re-run full LSTM augmentation experiment on leak-free synthetic data and report before/after comparison

## v2 Requirements

### IBM Hardware

- **IBM-01**: Execute qGAN on IBM quantum hardware via Qiskit Runtime
- **IBM-02**: Execute qVAE on IBM quantum hardware
- **IBM-03**: Compare hardware results (with noise) to simulator results

### Publication

- **PUB-01**: Write Limitations section acknowledging single trajectory, observed conditions scope
- **PUB-02**: Archive data.csv publicly with SHA256 hash
- **PUB-03**: Add multi-step prediction evaluation (h=7 day forecast)

## Out of Scope

| Feature | Reason |
|---------|--------|
| TSTR evaluation | Focus is historical+synthetic augmentation, not synthetic-only training |
| Real-time/streaming data | Single batch experiment |
| Multi-organism generalization | Single OD trajectory; acknowledge in limitations |
| OAuth/web interface | Research notebook, not application |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PREP-01 | Phase 1 | Pending |
| PREP-02 | Phase 1 | Pending |
| PREP-03 | Phase 1 | Pending |
| QUAL-01 | Phase 2 | Pending |
| QUAL-02 | Phase 2 | Pending |
| QUAL-03 | Phase 2 | Pending |
| QUAL-04 | Phase 2 | Pending |
| QUAL-05 | Phase 2 | Pending |
| QUAL-06 | Phase 2 | Pending |
| QUAL-07 | Phase 2 | Pending |
| EXPR-01 | Phase 2 | Pending |
| EXPR-02 | Phase 2 | Pending |
| EXPR-03 | Phase 2 | Pending |
| EXPR-04 | Phase 3 | Pending |
| FAIR-01 | Phase 3 | Pending |
| FAIR-02 | Phase 3 | Pending |
| FAIR-03 | Phase 3 | Pending |
| FAIR-04 | Phase 3 | Pending |
| DATA-01 | Phase 4 | Pending |
| DATA-02 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0

---
*Requirements defined: 2026-03-18*
*Last updated: 2026-03-18 — traceability updated after roadmap creation*
