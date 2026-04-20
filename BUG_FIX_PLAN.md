# HQSS Bug Fix Plan

*Step-by-step remediation for the 5 issues in [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md). Scientifically rigorous, no regressions.*

---

## Status at a glance

| # | Issue | Code fix applied? | Re-run required? | Scientifically resolved? |
|---|---|---|---|---|
| 1 | qGAN noise bug | YES (Phase 2) | YES — checkpoints stale | After Step 2 |
| 2 | qGAN scaling bug | YES (Phase 2) | YES — checkpoints stale | After Step 2 |
| 3 | Data leakage | NO | YES | After Step 4 |
| 4 | Unfair training time | NO | YES | After Step 6 |
| 5 | Weak baseline (single seed) | NO | YES | After Step 7 |

The code fixes for #1 and #2 are in the notebook, but **the synthetic samples under `checkpoints/synthetic/` are dated 2026-03-19 — pre-fix**. They were generated with the buggy noise/scaling and must be discarded.

---

## Guiding principles

1. **No regression.** After every step we re-run a smoke test; after every tier we re-run the full experiment and compare metrics to the prior checkpoint. If an unrelated metric moves more than 10%, we investigate before proceeding.
2. **Atomic commits.** One git commit per step. Any step can be reverted with `git revert` if it introduces new problems.
3. **Deterministic runs.** Every numerical result must come from a seeded run whose seeds are logged in the notebook output.
4. **Compare before and after.** We keep a JSON snapshot of pre-fix metrics (`results/metrics_pre_fix.json`) and a post-fix snapshot. Fixes must be defensible by diff, not by narrative.
5. **When in doubt, look it up.** When the right way to do something is ambiguous (e.g. VAE logvar parameterization, TSTR convention, multiple-comparison correction), cite a reference in the code comment and link it in the commit message.

---

## Tier 0 — Safety rails (before any fix)

### Step 0.1 — Tag the current state

```bash
git tag pre-fix-baseline
git push --tags   # only if Shawn wants remote
```

This is the rollback point. If anything goes wrong, `git reset --hard pre-fix-baseline` restores everything.

### Step 0.2 — Snapshot current metrics

Add a new cell immediately after the final comparison table that serializes every metric in the notebook to `results/metrics_pre_fix.json` (baseline MSE, per-model MSE mean/std per size, DM p-values, MMD/EMD, etc.). Commit the JSON.

**Why:** without a captured before-state, "the fix didn't break anything" is an unverifiable claim.

### Step 0.3 — Discard stale synthetic samples

```bash
rm -rf checkpoints/synthetic/* checkpoints/synthetic_ablation/*
```

Set `FORCE_GENERATE = True` in Cell 0. We re-generate from scratch with the (already-fixed) noise and scaling code.

### Step 0.4 — Verify the pre-fix metrics are reproducible

Re-run the notebook end-to-end from the tag. Confirm that the freshly-written `metrics_pre_fix.json` matches within floating-point tolerance if we re-run a second time. If the notebook is not deterministic even at fixed seeds, that is itself a bug to log before making further changes.

---

## Tier 1 — Verify the already-applied fixes (Issues #1, #2)

### Step 1.1 — Regenerate synthetic samples with FORCE_GENERATE=True

Run Cells 20–22 (generation functions + generation loop). This produces fresh samples under `checkpoints/synthetic/` using:
- `torch.randn(n_windows, NUM_QUBITS)` at generation (matches training)
- No `* 0.1` scaling (raw circuit outputs flow to denormalization)

### Step 1.2 — Confirm the smoke test passes post-regen

Re-run Cell 23 (smoke test). Acceptance:

- qGAN generated growth-rate std within factor of 2 of real std (real std ≈ 0.0218). Pre-fix value was ~0.0025 (10× compression). Post-fix must land in roughly [0.011, 0.044].
- KDE overlay of qGAN vs real growth rate shows the two distributions substantially overlapping, not the narrow spike seen pre-fix.
- No model produces strictly-positive growth rates when real data spans both signs. (cVAE was suspect here — flagged for Step 8 below.)

### Step 1.3 — Diff vs. metrics_pre_fix.json

Expected direction: qGAN augmentation effect should *decrease* in magnitude (the previous ~2–4% improvement was partially an artifact of 10× flat curves acting as regularization). If qGAN now helps *more*, investigate — something else changed.

**Commit:** `fix(gen): regenerate synthetic samples with fixed noise and scaling (closes #1, #2)`

---

## Tier 2 — Fix data leakage (Issue #3)

**Scientific justification for overriding the previous "this is augmentation, not benchmarking" stance:** The experiment's primary claim is *synthetic data improves held-out forecasting*. If generators see the held-out window during their own training, any synthetic sample can carry test-set statistics into the augmented training loader. The improvement then becomes a measurement of leakage, not of augmentation. Even in a strict data-augmentation framing, the integrity of the test set is non-negotiable.

### Step 2.1 — Split first, fit everything second

Move the 80/20 train/test split to Cell 6 (right after `growth_rate` is computed). Expose two arrays: `growth_rate_train` (first 622 points) and `growth_rate_test` (last 155 points).

**Fixed index split** (not random shuffle) is required because this is a time series — test must be the final contiguous segment.

### Step 2.2 — Recompute normalization constants from training split only

`MU`, `SIGMA`, `GR_MIN`, `GR_MAX` (Cell 3 → moves to Cell 6) must be computed from `growth_rate_train` only. Save them:

```python
norm_stats = {"MU": MU, "SIGMA": SIGMA, "GR_MIN": GR_MIN, "GR_MAX": GR_MAX, "split_index": 622}
json.dump(norm_stats, open("results/norm_stats.json", "w"))
```

These constants are used for both normalization (before training) and denormalization (after generation). They must never touch `growth_rate_test`.

### Step 2.3 — Train generators on training windows only

`gan_loader` (Cell 10) and `vae_loader` (Cell 12) must be built from sliding windows over `growth_rate_train_normalized` only. Explicit length check in a new assertion cell:

```python
expected_gan_windows = (len(growth_rate_train) - WINDOW_GAN) // STRIDE_GAN + 1
assert len(gan_loader.dataset) == expected_gan_windows, f"Leakage: loader has {len(gan_loader.dataset)} windows, expected {expected_gan_windows}"
```

Same for VAE loader.

### Step 2.4 — Retrain all four generators

Because training data has changed, **all four checkpoints are now invalid**. Retrain qGAN, qVAE, cGAN, cVAE from scratch with the new loaders. This is the most expensive single step in the plan.

- qGAN: 500 epochs (unchanged)
- qVAE: 50 epochs (flag this for Tier 3 — see M1 unfair-engineering issue, Step 10)
- cGAN: 500 epochs
- cVAE: 200 epochs

Save new checkpoints under `checkpoints/models/retrained_train_only/` so the pre-fix checkpoints are still available for comparison.

### Step 2.5 — Regenerate synthetic samples

With `FORCE_GENERATE=True`, rebuild `checkpoints/synthetic/` from the retrained generators.

### Step 2.6 — Regression check

Re-run the smoke test (Cell 23). Acceptance:
- All four models still produce growth rates with std within factor of 2 of real training std.
- MMD and EMD vs real *test* data are higher than vs real *training* data (expected — generators never saw test).
- If MMD/EMD to test are *lower* than to training, that is prima facie evidence of residual leakage; investigate.

**Commit:** `fix(data): split train/test before generator training to eliminate leakage (closes #3)`

**Research flag:** the question "should normalization constants for a time-series regression be frozen on training data?" is standard practice (Hyndman & Athanasopoulos, *Forecasting: Principles and Practice*, ch. 5.10). Cite this in the commit message.

---

## Tier 3 — Equalize training time (Issue #4)

**Scientific justification:** comparing a model that trained for 470 gradient steps against models that trained for 150,000 steps measures training duration, not augmentation quality. To isolate the augmentation effect, either the gradient-step count must be equalized or both models must be trained to convergence under the same stopping rule.

I prefer **validation-based early stopping with a held-out validation split**. It avoids the "equalize artificially at 470 steps" trap (which under-trains the augmented model) and the "equalize at 150,000 steps" trap (which over-trains the baseline into memorization).

### Step 3.1 — Carve a validation split from the training segment

The current 622-point training segment becomes:
- **Train:** first 497 points (80% of 622)
- **Val:** next 125 points (20% of 622)
- **Test:** last 155 points (unchanged from Tier 2)

Update `norm_stats.json` to record the new split indices.

**Caveat:** normalization constants should be re-fit on the 497-point train-only subset, *not* on train+val. This is strict but correct. Expect a small shift in MU/SIGMA (< 2%) that propagates downstream.

### Step 3.2 — Add early stopping to LSTM training

Modify the LSTM training routine (Cell 30 for baseline, Cell 32 for augmented) to:
1. Compute val MSE after each epoch on the real validation windows only (never on synthetic).
2. Stop when val MSE has not improved for `PATIENCE = 10` epochs.
3. Restore the weights from the best val epoch before evaluating on test.

Log the epoch at which early stopping fired — this number will vary by augmented size and becomes a reported quantity.

**Minimum epochs** should still be respected (say, 10) so we don't stop before the model has had a chance to learn.

### Step 3.3 — Verify the stopping rule is triggering

Add an assertion that `stopped_epoch < MAX_EPOCHS` for at least one baseline and one augmented run at each size. If every run hits MAX_EPOCHS, patience is too high or MAX_EPOCHS is too low.

### Step 3.4 — Regression check

Compare to `metrics_pre_fix.json`:
- Baseline MSE is expected to move (slightly better, because early stopping prevents mild overfit; possibly slightly worse, because validation split reduces train size).
- Augmented MSEs are expected to move substantially — the pre-fix 150,000-step advantage is gone. Expect some augmented models to now perform *worse* than baseline (this is the correct, unconfounded answer).

**Commit:** `fix(lstm): validation-based early stopping for fair baseline vs augmented comparison (closes #4)`

**Research flag:** the patience-based early stopping convention follows Prechelt (1998), *Early Stopping — But When?*. Modern alternative: `MaxMin` (monitor val loss minimum over a rolling window). Either is defensible — cite the chosen one.

---

## Tier 4 — Robust multi-seed evaluation (Issue #5)

**Scientific justification:** a single baseline point compared against a 3-sample mean of augmented runs is not a controlled comparison. With N=3 per augmented condition the 95% CI is ±2.5×std, which for current stds (~1e-6) is wider than many reported effects. The statistically defensible minimum is equal N for baseline and augmented, and a seed count that gives > 80% power for the smallest effect we care to detect.

### Step 4.1 — Decouple generation seeds from LSTM seeds

Current code uses the same seed variable to initialize the generator RNG and the LSTM weights. This injects systematic confounding. Split into two seed variables per run:

```python
for lstm_seed in LSTM_SEEDS:           # e.g. 10 values
    for gen_seed in GEN_SEEDS:         # e.g. 3 values
        # one LSTM run per (lstm_seed, gen_seed) pair
```

For the baseline (no synthetic data), only `lstm_seed` varies — generate one row per `lstm_seed`.

### Step 4.2 — Increase to N = 10 LSTM seeds

Replace `GEN_SEEDS = [42, 137, 271]` and the baseline's single `torch.manual_seed(0)` with `LSTM_SEEDS = [0, 1, 2, ..., 9]`. Keep `GEN_SEEDS = [42, 137, 271]` for generation variability if compute allows — total LSTM runs per condition become 10 × 3 = 30.

**Compute budget reality check:** 10 × 3 × 4 models × 3 sizes = 360 augmented LSTM runs. At ~30s each on MPS that's ~3 hours. Baseline adds 10 runs. If this is too expensive, drop to `GEN_SEEDS = [42]` for an initial pass and add the full matrix later. Document the choice.

### Step 4.3 — Report proper statistics

For each condition:
- Mean MSE across seeds
- **Sample** standard deviation (`np.std(..., ddof=1)`, not population std)
- 95% CI using `t.ppf(0.975, df=N-1) * std / sqrt(N)`
- For the augmented-vs-baseline comparison: paired test when baseline and augmented share `lstm_seed` (they do, by design of Step 4.1), not independent t-test.

Replace the current `sig_stars(np.mean([e['p'] for e in dm_ents]))` pattern — averaging p-values is statistically invalid — with Fisher's combined probability test (`scipy.stats.combine_pvalues(pvals, method='fisher')`).

### Step 4.4 — Correct for multiple comparisons

With 4 models × 3 sizes = 12 comparisons against baseline, apply Holm–Bonferroni correction to the family of p-values before declaring any significance. Add a `q_value` column to the summary table.

### Step 4.5 — Regression check

Re-run the full comparison table. Compare to Tier 3's snapshot:
- Baseline mean should be close to Tier 3's baseline single-seed value, but with a real std attached.
- Augmented effect sizes should shrink in significance (some previously-"significant" results will lose stars after Holm correction). This is the correct outcome, not a regression.

**Commit:** `fix(eval): N=10 LSTM seeds, paired test, Holm correction (closes #5)`

**Research flag:** Holm–Bonferroni vs Benjamini–Hochberg for 12 comparisons — Holm controls FWER and is more conservative; BH controls FDR and is standard in genomics. For a paper with few planned comparisons, Holm is appropriate. Cite Holm (1979).

---

## Tier 5 — While we have the lab open (rigor upgrades closely tied to Tier 1–4)

These extend the five core fixes into a genuinely publishable statistical design. Each is small on its own and closes a direct flank of the five.

### Step 5.1 — Replace MAPE

Growth rates cross zero, so MAPE divides by near-zero values and produces 144–530% garbage. Replace with:
- **sMAPE** (Armstrong 1985) for a bounded percentage-style metric, or
- **RMSSE** (Hyndman & Koehler 2006) for a naive-forecast-relative scale-free metric.

I recommend RMSSE — it's the metric used in the M4/M5 forecasting competitions and is unambiguous around zero.

### Step 5.2 — Add an IID Gaussian-noise augmentation baseline

For each augmented size, also run an LSTM trained on the real data plus the same number of windows of real data with added N(0, 0.1·SIGMA) noise. If the generative models do not outperform this trivial baseline, the augmentation infrastructure is not adding information.

### Step 5.3 — TSTR sanity check (Train Synthetic, Test Real)

Train an LSTM purely on synthetic windows (no real data) and evaluate on the real test set. A non-catastrophic TSTR score is direct evidence that synthetic curves preserve the forecasting signal. A catastrophic TSTR score under augmentation success suggests the real data is doing the work and synthetic curves are acting as regularization.

**Research flag:** TSTR convention comes from Esteban et al. 2017 (*Real-valued Medical Time Series Generation with Recurrent Conditional GANs*). Report both TSTR and TRTR (train-real-test-real, i.e. the baseline) for interpretability.

### Step 5.4 — Pre-register the analysis plan

Before running Tier 4 for real, write `results/ANALYSIS_PLAN.md` that states:
- the exact statistical tests,
- the significance threshold,
- the multiple-comparison correction,
- the primary metric (MSE on real test),
- the secondary metrics (RMSSE, TSTR score, MMD, EMD),
- stopping rules.

Commit this *before* the final multi-seed run. This prevents post-hoc cherry-picking and is standard practice in well-run computational studies.

---

## Verification protocol (applies to every tier)

After each tier I do the following before moving on:

1. **Smoke test re-run** (Cell 23). All four models produce growth-rate distributions within 2× of real. Fail → investigate, don't advance.
2. **Full-notebook re-run from a clean kernel.** If kernel-restart-and-run-all breaks, the notebook has hidden state — fix before advancing.
3. **Metric diff vs previous tier's JSON snapshot.** Direction of change must match the scientific expectation written in the step. Unexpected direction → investigate.
4. **Commit + tag**: `git tag tier-N-complete`.

---

## Files and cells likely to change

| Tier | Cells | Files |
|---|---|---|
| 0 | new end-of-notebook cell | `results/metrics_pre_fix.json`, git tag |
| 1 | 20, 21, 22, 23, 52 (already modified) | `checkpoints/synthetic/**` (regen) |
| 2 | 3, 6, 10, 12, model training cells | `checkpoints/models/retrained_train_only/**`, `results/norm_stats.json` |
| 3 | 30, 32, 37, 53 | — |
| 4 | 30, 32, summary table cells | `results/metrics_tier4.json`, `results/ANALYSIS_PLAN.md` |
| 5 | new metric cells, new TSTR cell | — |

---

## What this plan explicitly does NOT do

- Does not fix the qVAE Softplus-on-logvar issue (M4 in sci_review.md) — that is a separate quantum-model correctness ticket that the user flagged in all-caps at the bottom of sci_review.md. It should be the next plan after this one.
- Does not fix model-engineering asymmetries (HPO, ACF penalty, cVAE infrastructure — M1 in sci_review.md). Those are a fairness-of-comparison ticket, not a correctness ticket.
- Does not touch the IBM hardware section (M16, M17). Simulator-first; hardware after the simulator story is clean.

---

## When to ask the internet

I'll fetch references for:

1. **Early-stopping conventions for time-series regression** — confirm patience=10 and val-subset size (Prechelt 1998 is the canonical ref; modern best practice may differ).
2. **Fisher's method vs Stouffer's Z for p-value aggregation across seeds** — both are valid; pick the one appropriate for independent vs correlated tests.
3. **TSTR protocol details** — Esteban et al. 2017 established the pattern but different domains use different variants; pick the time-series variant.
4. **Paired test for seed-matched comparisons with N=10** — Wilcoxon signed-rank is standard but only has 2^10 = 1024 permutations, so exact p-values are fine without Monte Carlo.
5. **RMSSE denominator choice** — naive forecast is the standard but "naive" means "y_t = y_{t-1}" vs "y_t = mean(train)". Pick one and cite.

When I fetch a reference, I'll cite it in the code comment at the line where the convention is applied, and in the commit message.
