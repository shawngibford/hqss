# Phase 1: Preprocessing - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Remove Lambert-W Gaussianization from the preprocessing pipeline, rename "log returns" to "specific growth rate" with biological justification, and quantify PAR_LIGHT conditioning contribution via ablation. All four generative models are retrained on the new pipeline. This phase changes the data foundation everything downstream depends on.

</domain>

<decisions>
## Implementation Decisions

### Normalization after Lambert-W removal
- Remove Lambert-W entirely — delete `lambert_w_gaussianize()`, `lambert_w_inverse()`, `_kurtosis_for_delta()`, and all related constants (DELTA_LW, LW_MIN, LW_MAX)
- Pipeline becomes: OD → dither → specific growth rate → z-score → scale[-1,1] (for GANs) or z-score only (for VAEs)
- Keep the existing split: GANs (qGAN, cGAN) receive [-1,1] scaled input; VAEs (qVAE, cVAE) receive z-scored (unbounded) input
- Dithering step (±0.005 noise) is kept as-is — standard numerical stability trick
- All Lambert-W code is deleted entirely (not commented out) — git history preserves it

### PAR_LIGHT ablation design
- Full pipeline comparison: train/generate with PAR_LIGHT vs without for all 4 models, run both through LSTM evaluation
- For GANs: retrain separate qGAN/cGAN WITHOUT PAR_LIGHT conditioning input (not zero-fill — genuine architectural ablation)
- For VAEs: current behavior IS the "without" condition (they don't take PAR_LIGHT as a separate input) — no retraining needed
- Results presented as a comparison table (with-PAR vs without-PAR LSTM metrics: MSE, MAPE per model) plus a 1-2 sentence markdown commentary cell
- Ablation checkpoints stored in same directory with different naming (e.g., `qgan_no_par.pt`)

### Biological framing
- Rename all variable names throughout: `log_delta` → `growth_rate` (or similar biological name)
- One markdown cell placed immediately before the growth rate computation cell
- Cell contains: equation µ = d(ln OD)/dt, brief explanation that this is the standard microbiological specific growth rate
- No literature references — the equation is self-evident to the target audience
- All user-facing text (markdown cells, print statements, comments) updated to use "specific growth rate" instead of "log returns"

### Checkpoint strategy
- Retrain ALL 4 models on the new (no-Lambert-W) pipeline in Phase 1
- Use reduced epochs for quantum models (qGAN, qVAE) to manage compute cost — full training deferred to Phase 4 (data integrity fix)
- Classical models (cGAN, cVAE) train at full hyperparameters (fast enough)
- Old Lambert-W checkpoints are replaced entirely — not kept in a legacy directory
- Phase 4 will do the definitive retraining (train-split only + full epochs)

### Claude's Discretion
- Exact reduced epoch counts for quantum models in Phase 1
- Variable naming choice (growth_rate vs mu_growth vs specific_growth_rate)
- Denormalization function refactoring details after Lambert-W removal
- Print statement formatting and validation output style

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Preprocessing pipeline
- `.planning/codebase/ARCHITECTURE.md` — Full data flow diagram, preprocessing layer description (cells 3-5), denormalization chain per model family
- `.planning/codebase/CONVENTIONS.md` — Variable naming patterns, function naming conventions, code style

### Scientific review
- `sci_review.md` — Peer review feedback that motivated Lambert-W removal and biological framing

### Project constraints
- `.planning/PROJECT.md` — Single notebook constraint, existing architecture constraint (don't change quantum circuit structure)
- `.planning/REQUIREMENTS.md` — PREP-01, PREP-02, PREP-03 acceptance criteria

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `MODELS_INFO` dict (cell 15): Pluggable model → generation function mapping. Ablation models can be added here.
- Denormalization functions (`denorm_qgan_output`, `denorm_vae_output`, `log_delta_to_od`): Will be simplified after Lambert-W removal but structure is reusable.
- Checkpoint loading pattern: Conditional on file existence + force-retrain flags. Same pattern for ablation checkpoints.

### Established Patterns
- Two normalization paths: GAN ([-1,1] bounded) vs VAE (z-scored unbounded) — this split is preserved
- Force-retrain flags control whether to load checkpoint or retrain — reuse for ablation models
- Section headers with decorative separators (`# ── N. SECTION NAME ──────`) — maintain this style

### Integration Points
- Preprocessing output feeds ALL downstream cells — this is the most impactful change in the project
- `gan_loader` and `vae_loader` DataLoaders consume preprocessed windows
- Generation functions in cell 15 call denormalization functions — these must be updated to remove Lambert-W steps
- LSTM evaluation pipeline (cells 22-27) consumes generated OD curves — must work with both PAR_LIGHT conditions

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches for the implementation.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-preprocessing*
*Context gathered: 2026-03-18*
