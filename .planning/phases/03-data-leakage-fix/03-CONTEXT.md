# Phase 3: Data Leakage Fix - Context

**Gathered:** 2026-04-08
**Status:** INVALIDATED — Phase removed from roadmap

<domain>
## Phase Boundary

This phase was scoped to retrain all generators on the training split only and recompute preprocessing constants from training data only. **Discussion revealed the premise is incorrect for this experiment.**

</domain>

<decisions>
## Implementation Decisions

### Phase Invalidation
- **D-01:** Generators training on ALL data is correct for this experiment. The generative models learn the distribution of the full historical OD dataset. Synthetic curves are full-length augmentation data. The LSTM soft sensor trains on historical+synthetic data with an 80/20 temporal split for evaluation.
- **D-02:** DINT-01 requirement ("fix data leakage") is invalid — there is no leakage. Generators learning the full biological process distribution is the intended experimental design.
- **D-03:** MU, SIGMA, GR_MIN, GR_MAX computed from the full dataset are correct — no need to recompute from training split.
- **D-04:** Current checkpoints are valid (trained on full data as intended). No retraining needed.
- **D-05:** Phase 3 removed entirely from roadmap. Phase 4 (LSTM Evaluation Fixes) becomes the next phase.
- **D-06:** A justification markdown cell will be added to the notebook explaining why generators use all data (for reviewer clarity).

### Experimental Design Rationale
The experiment tests whether quantum-generated synthetic data can improve LSTM soft sensor accuracy:
1. Generators learn the full OD distribution (all 778 rows) — this is the "small dataset" being augmented
2. Synthetic curves are generated at various sizes (50, 150, 250)
3. LSTM trains on real_train (first 80%) + synthetic data, tests on held-out last 20%
4. Comparison: does augmentation improve prediction vs baseline (real data only)?

The generators seeing "test period" data is not leakage because they learn a distributional model of the biological process, not specific test-period values.

</decisions>

<canonical_refs>
## Canonical References

No external specs — the key finding is that DINT-01 was based on a misapplication of the data leakage concept to this experiment's augmentation design.

- `sci_review.md` — Original review that flagged "leakage" (§C1) — this concern is addressed by the justification cell
- `.planning/REQUIREMENTS.md` — DINT-01 to be marked as invalidated

</canonical_refs>

<code_context>
## Existing Code Insights

### Current State (Correct)
- `MU`, `SIGMA` computed from full `growth_rate` array — correct
- `GR_MIN`, `GR_MAX` computed from full `norm_growth_rate` — correct
- `gan_loader`, `vae_loader` built from all windows — correct
- `TRAIN_FRAC = 0.80` applied only at LSTM evaluation time — correct

### No Changes Needed
- Generator training code: correct as-is
- Preprocessing constants: correct as-is
- DataLoader construction: correct as-is

</code_context>

<specifics>
## Specific Ideas

Add a markdown cell near the preprocessing section explaining:
- This is a data augmentation experiment, not a generative modeling benchmark
- Generators learn the full biological process distribution by design
- Only the LSTM evaluation uses a temporal train/test split

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-data-leakage-fix*
*Context gathered: 2026-04-08*
*Outcome: Phase invalidated and removed from roadmap*
