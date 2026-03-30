# Phase 2: Generation Bug Fixes - Context

**Gathered:** 2026-03-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix all generation-time code bugs so the four generative models (qGAN, qVAE, cGAN, cVAE) produce valid synthetic curves. Covers: qGAN noise distribution mismatch (GENBUG-01), `* 0.1` scaling removal (GENBUG-02), seed collision elimination (GENBUG-03), and cross-boundary window contamination fix (GENBUG-04). Includes a smoke test cell to validate all fixes.

</domain>

<decisions>
## Implementation Decisions

### Smoke Test Design
- **D-01:** Smoke test generates a small sample (~10 curves per model) for fast validation, separate from the full generation loop
- **D-02:** Smoke test prints mean, std, min, max for each model vs real data in a comparison table
- **D-03:** Smoke test includes a KDE overlay plot (all 4 models + real on one figure) for visual comparison
- **D-04:** Smoke test flags any model whose std is >2x or <0.5x of real data variance (warning, not assertion)

### Seed Strategy
- **D-05:** Use offset scheme: `seed = base_seed + (size_idx * 1000) + (rep_idx * 100)` to guarantee non-overlapping seeds across 3 replicates x 3 sizes
- **D-06:** Same seed set across all 4 models (per rep x size only) — architectures are different so outputs are independent regardless

### Window Assembly
- **D-07:** Create sliding windows per-curve independently, then concatenate all (X, y) arrays — no window ever spans two synthetic curves
- **D-08:** Apply the same per-curve windowing fix to real+synthetic data assembly — window real training series separately, window each synthetic curve separately, then concatenate all (X, y) arrays. Eliminates real-to-synthetic boundary artifacts.

### Variance Validation
- **D-09:** After removing `* 0.1` scaling, print a warning (not hard assert) when a model's output variance is outside the [0.5x, 2x] range of real data — let the experiment complete for analysis
- **D-10:** Also flag sign bias — warn if >90% of generated growth rates are same-sign, since real growth rates are roughly symmetric around zero

### Claude's Discretion
- Exact implementation of the offset seed formula (base seed value, multipliers)
- KDE plot styling and layout
- Warning message formatting
- Whether to consolidate the smoke test into the existing generation cell or create a new dedicated cell

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Generation pipeline
- `.planning/codebase/ARCHITECTURE.md` — Full data flow diagram, generation layer (cells 14-15), denormalization chain per model family
- `.planning/codebase/CONCERNS.md` — C1 (data leakage, Phase 3), M6 (window boundary artifacts), F3 (quantum sim speed)

### Scientific review
- `sci_review.md` — Peer review that identified the generation bugs; see sections on qGAN noise mismatch and scaling

### Requirements
- `.planning/REQUIREMENTS.md` — GENBUG-01 through GENBUG-04 acceptance criteria
- `.planning/ROADMAP.md` — Phase 2 success criteria (4 specific conditions that must be TRUE)

### Prior phase context
- `.planning/phases/01-preprocessing/01-CONTEXT.md` — Preprocessing pipeline decisions (denorm chain, normalization paths)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `MODELS_INFO` dict (cell 15): Pluggable model-to-generation-function mapping — smoke test can iterate this dict
- Denormalization functions (`denorm_qgan_output`, `denorm_vae_output`, `log_delta_to_od`): Already simplified in Phase 1, will be used as-is
- `_sliding_windows()` function (cell 9): Existing windowing utility — will be called per-curve instead of on concatenated series

### Established Patterns
- Two normalization paths: GAN ([-1,1] bounded) vs VAE (z-scored unbounded) — preserved
- Force-retrain flags control checkpoint vs retrain — no change needed
- Section headers with decorative separators (`# ── N. SECTION NAME ──────`)
- `.float()` throughout for MPS compatibility

### Integration Points
- Generation functions in cell 15: `_qgan_generate_one` is the primary bug site (noise + scaling)
- LSTM augmentation loop (cell 24): Window assembly happens here — must be refactored for per-curve windowing
- `GEN_SEEDS` in config cell: Replace with offset scheme
- Checkpoint paths: Existing synthetic curve checkpoints will need regeneration after fixes

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

*Phase: 02-generation-bug-fixes*
*Context gathered: 2026-03-30*
