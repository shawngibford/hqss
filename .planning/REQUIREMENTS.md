# Requirements: HQSS

**Defined:** 2026-03-30
**Core Value:** Demonstrate quantum circuit ansatze can generate faithful synthetic bioprocess data with rigorous methodology

## v1.1 Requirements

Requirements for critical bug fixes. Each maps to roadmap phases.

### Generation Bugs

- [ ] **GENBUG-01**: Fix qGAN noise distribution — use `torch.randn` at generation (matching training), not `np.random.uniform(0, 4pi)`
- [ ] **GENBUG-02**: Remove `* 0.1` scaling at generation — circuit outputs must match training scale
- [ ] **GENBUG-03**: Fix seed collisions — use non-overlapping seed ranges so all 3 replicates are truly independent (no shared curves)
- [ ] **GENBUG-04**: Fix cross-boundary window contamination — create sliding windows per curve independently, then concatenate (X, y) arrays

### Data Integrity

- [ ] **DINT-01**: Fix data leakage — build `gan_loader`/`vae_loader` from train-split only windows; compute MU, SIGMA, GR_MIN, GR_MAX on training data only
- [ ] **DINT-02**: Fix training budget asymmetry — add validation-based early stopping or epoch-proportional training so augmented LSTMs don't get 320x more gradient steps than baseline
- [ ] **DINT-03**: Run baseline LSTM with same 3+ seeds — report baseline mean +/- std for fair comparison instead of single-seed point estimate

### Evaluation

- [ ] **EVAL-01**: Drop MAPE or replace with symmetric MAPE / RMSSE — current MAPE divides by near-zero growth rates producing meaningless 144-530% values

## v1.0 Requirements (Validated)

### Preprocessing (Phase 1 — Complete)

- [x] **PREP-01**: Remove Lambert-W Gaussianization — use z-score normalization only on specific growth rates
- [x] **PREP-02**: Rename "log returns" to "specific growth rate" throughout notebook with biological justification text
- [x] **PREP-03**: PAR_LIGHT ablation — train and generate with vs without light conditioning, quantify contribution

## v1.2 Requirements (Deferred)

### Quality Metrics

- **QUAL-01**: Implement Section A — MMD + EMD computation for each model vs real data
- **QUAL-02**: Temporal metrics — ACF RMSE, DTW, Frechet distance
- **QUAL-03**: ACF validation — ACF(1-50) synthetic vs real per model with overlay plots
- **QUAL-04**: Execute Section B statistical tests with multiple-comparisons correction
- **QUAL-05**: Biological plausibility — monotonicity, range, growth phases
- **QUAL-06**: Mode collapse detection — diversity/coverage metrics
- **QUAL-07**: Overfitting detection — train/val loss, memorization check

### Experiment Design

- **EXPR-01**: Classical augmentation baselines (Gaussian noise + bootstrap)
- **EXPR-02**: N>=10 seeds with proper 95% CIs and multiple-comparisons correction
- **EXPR-03**: Report training wall-clock time for all models
- **EXPR-04**: Window boundary fix — continuity at qGAN junctions

### Model Fairness

- **FAIR-01**: Parameter-matched classical baseline (~75-param cGAN)
- **FAIR-02**: Equalize HPO across all models
- **FAIR-03**: Noisy quantum simulator (depolarizing + readout noise)
- **FAIR-04**: Equalize training epochs (qVAE/cVAE)
- **FAIR-05**: Fix qVAE Softplus logvar (posterior can't shrink below prior)
- **FAIR-06**: Address cVAE mode collapse (narrow all-positive output)

### IBM & Polish

- **IBM-01**: Fix IBM PAR_LIGHT scale mismatch (par_norm_trim vs par_scaled_trim)
- **IBM-02**: Fix IBM qVAE device patching (ineffective — QNodes still use simulator)
- **POLISH-01**: Add ACF overlay plots, training loss curves, ablation bar charts
- **POLISH-02**: Fix MMD/EMD shared y-axis, compute metrics across all seeds
- **POLISH-03**: Fix DM p-value aggregation (Fisher's method, not averaging)

## Out of Scope

| Feature | Reason |
|---------|--------|
| IBM quantum hardware execution | Deferred until simulator results are correct |
| TSTR evaluation | Focus is augmentation, not synthetic-only training |
| Multi-organism generalization | Single OD trajectory; acknowledge in limitations |
| Real-time/streaming data | Single batch experiment |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PREP-01 | Phase 1 | Complete |
| PREP-02 | Phase 1 | Complete |
| PREP-03 | Phase 1 | Complete |
| GENBUG-01 | Phase 2 | Pending |
| GENBUG-02 | Phase 2 | Pending |
| GENBUG-03 | Phase 2 | Pending |
| GENBUG-04 | Phase 2 | Pending |
| DINT-01 | Phase 3 | Pending |
| DINT-02 | Phase 4 | Pending |
| DINT-03 | Phase 4 | Pending |
| EVAL-01 | Phase 4 | Pending |

**Coverage:**
- v1.1 requirements: 8 total
- Mapped to phases: 8/8
- Unmapped: 0

---
*Requirements defined: 2026-03-30*
*Last updated: 2026-03-30 after v1.1 roadmap creation*
