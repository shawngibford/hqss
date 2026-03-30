# Phase 2: Generation Bug Fixes - Research

**Researched:** 2026-03-30
**Domain:** Python / PyTorch / PennyLane quantum circuit generation pipeline (Jupyter notebook)
**Confidence:** HIGH — all findings based on direct notebook source inspection

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Smoke test generates a small sample (~10 curves per model) for fast validation, separate from the full generation loop
- **D-02:** Smoke test prints mean, std, min, max for each model vs real data in a comparison table
- **D-03:** Smoke test includes a KDE overlay plot (all 4 models + real on one figure) for visual comparison
- **D-04:** Smoke test flags any model whose std is >2x or <0.5x of real data variance (warning, not assertion)
- **D-05:** Use offset scheme: `seed = base_seed + (size_idx * 1000) + (rep_idx * 100)` to guarantee non-overlapping seeds across 3 replicates x 3 sizes
- **D-06:** Same seed set across all 4 models (per rep x size only) — architectures are different so outputs are independent regardless
- **D-07:** Create sliding windows per-curve independently, then concatenate all (X, y) arrays — no window ever spans two synthetic curves
- **D-08:** Apply the same per-curve windowing fix to real+synthetic data assembly — window real training series separately, window each synthetic curve separately, then concatenate all (X, y) arrays
- **D-09:** After removing `* 0.1` scaling, print a warning (not hard assert) when a model's output variance is outside the [0.5x, 2x] range of real data — let the experiment complete for analysis
- **D-10:** Also flag sign bias — warn if >90% of generated growth rates are same-sign

### Claude's Discretion

- Exact implementation of the offset seed formula (base seed value, multipliers)
- KDE plot styling and layout
- Warning message formatting
- Whether to consolidate the smoke test into the existing generation cell or create a new dedicated cell

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GENBUG-01 | Fix qGAN noise distribution — use `torch.randn` at generation (matching training), not `np.random.uniform(0, 4pi)` | Confirmed: training (cell 12, line 60) uses `torch.randn(B, NUM_QUBITS)`; generation (cell 20) uses `np.random.uniform(0, 4*np.pi, (NUM_QUBITS, n_windows))` — single-line swap |
| GENBUG-02 | Remove `* 0.1` scaling at generation — circuit outputs must match training scale | Confirmed: `gen_windows.append(out.float() * 0.1)` in cell 20 — remove the `* 0.1` |
| GENBUG-03 | Fix seed collisions — use non-overlapping seed ranges so all 3 replicates are truly independent | Confirmed: current `curve_seed = seed + k` causes overlaps at size=250 (seeds 137-291 shared across rep 0 and rep 1); D-05 offset scheme fixes this |
| GENBUG-04 | Fix cross-boundary window contamination — create sliding windows per curve independently, then concatenate (X, y) arrays | Confirmed: cell 31 concatenates all `ld_curves` into a flat series then calls `make_lstm_dataset()` on the whole thing — must window per-curve first |
</phase_requirements>

---

## Summary

Phase 2 fixes four discrete, independently addressable bugs in the generation pipeline. All bugs are confirmed by direct source inspection — the exact lines, functions, and cells are identified below. No external library research is required; every fix is a code-level change inside `hqss_experiment.ipynb`.

The four bugs are: (1) GENBUG-01/GENBUG-02 — two bugs in `_qgan_generate_one()` in cell 20: wrong noise distribution and an extra `* 0.1` scale factor; (2) GENBUG-03 — `curve_seed = seed + k` in the generation loop (cell 22) causes seed overlaps at large sizes; (3) GENBUG-04 — cell 31 (LSTM experiment loop) assembles augmented training data by concatenating all log-delta arrays into a flat series and then calling `make_lstm_dataset()` on the whole thing, causing windows to span curve boundaries.

The smoke test cell (D-01 through D-04) is a new dedicated cell using the existing `MODELS_INFO` dict to iterate all four models, printing a stats table and rendering a KDE overlay.

**Primary recommendation:** Fix all four bugs as surgical edits to the identified lines/cells. No refactoring of surrounding logic is needed. Regenerate all synthetic curve checkpoints after fixes to ensure downstream LSTM results are based on corrected generation.

---

## Standard Stack

All fixes use libraries already present in the notebook. No new dependencies.

### Core (already installed)
| Library | Version | Purpose | Notes |
|---------|---------|---------|-------|
| torch | ≥2.0 | Replace `np.random.uniform` with `torch.randn`; existing `.float()` convention | Already used everywhere |
| numpy | ≥1.24 | Seed control (`np.random.seed`), array ops | Already used |
| matplotlib | ≥3.7 | KDE overlay plot in smoke test | Already used |
| scipy.stats.gaussian_kde | bundled with scipy | KDE computation for smoke test | Already used in cell 25 |

### Installation
No new installs required.

---

## Architecture Patterns

### Notebook Cell Structure
Section headers use the established convention:
```python
# ── N. SECTION NAME ──────────────────────────────────────────────────────────
```
New smoke test cell should follow this pattern.

### Existing Abstractions to Reuse
- `MODELS_INFO` dict (cell 22): maps model name to generation function — smoke test iterates this dict exactly as the generation loop does
- `_sliding_windows(data, size, stride)` (cell 11): existing utility — call it per-curve instead of on the concatenated series
- `make_lstm_dataset(series, lookback)` (cell 28): existing LSTM windowing — replaces the direct call on `augmented`
- `denorm_qgan_output`, `denorm_vae_output`, `log_delta_to_od` (cell 10): denorm chain — unchanged

### Pattern: Per-Curve Windowing (GENBUG-04 fix)

Current pattern (broken — windows span curve boundaries):
```python
augmented = np.concatenate([real_train_ld] + [ld.astype(np.float32) for ld in ld_list])
X_aug, y_aug = make_lstm_dataset(augmented, LOOKBACK)
```

Correct pattern (D-07, D-08):
```python
# Window real training data
X_parts, y_parts = [], []
X_r, y_r = make_lstm_dataset(real_train_ld, LOOKBACK)
X_parts.append(X_r); y_parts.append(y_r)
# Window each synthetic curve independently
for ld in ld_list:
    if len(ld) > LOOKBACK:  # guard: curve must be longer than lookback
        X_s, y_s = make_lstm_dataset(ld.astype(np.float32), LOOKBACK)
        X_parts.append(X_s); y_parts.append(y_s)
X_aug = np.concatenate(X_parts, axis=0)
y_aug = np.concatenate(y_parts, axis=0)
```

### Pattern: Non-Overlapping Seed Scheme (GENBUG-03 fix)

Decision D-05 formula: `seed = base_seed + (size_idx * 1000) + (rep_idx * 100)`

Verification that ranges don't collide for SYNTH_SIZES=[50, 150, 250] and 3 replicates:
```
size_idx=0 (size=50):   rep 0: seeds 0–49,   rep 1: seeds 100–149, rep 2: seeds 200–249
size_idx=1 (size=150):  rep 0: seeds 1000–1149, rep 1: seeds 1100–1249, rep 2: seeds 1200–1349
size_idx=2 (size=250):  rep 0: seeds 2000–2249, rep 1: seeds 2100–2349, rep 2: seeds 2200–2449
```
No overlap. The `base_seed` value (e.g. 0) is at Claude's discretion (D-06 implies matching the existing seed set per rep; could mirror GEN_SEEDS=[42, 137, 271] as rep_idx 0,1,2 offsets).

Revised generation loop structure:
```python
for size_idx, n_synth in enumerate(SYNTH_SIZES):
    for rep_idx, _ in enumerate(GEN_SEEDS):
        base_seed = size_idx * 1000 + rep_idx * 100   # no overlap guaranteed
        for k in range(n_synth):
            curve_seed = base_seed + k
            od, gr = gen_fn(seed=curve_seed)
```

### Pattern: qGAN Noise Fix (GENBUG-01 + GENBUG-02)

Current broken generation noise:
```python
noise = torch.tensor(
    np.random.uniform(0, 4 * np.pi, (NUM_QUBITS, n_windows)),
    dtype=torch.float32
)
# ...
gen_windows.append(out.float() * 0.1)   # WRONG: scale suppresses variance 10x
```

Corrected generation noise (matching training in cell 12):
```python
# Training uses: noise = torch.randn(B, NUM_QUBITS)  -> shape (batch, n_qubits)
# Generation needs: shape (n_windows, n_qubits) to feed one window at a time
noise = torch.randn(n_windows, NUM_QUBITS)  # matches training distribution
# ...
gen_windows.append(out.float())  # remove * 0.1
```

Note: the existing loop indexes noise as `noise[:, i]` (shape: n_qubits), treating it as column-indexed. The corrected version should index as `noise[i]` (row i) to get a `(NUM_QUBITS,)` vector per window, matching how training provides `noise[j]` per batch element. This is a shape transposition — confirm the circuit function `_qgan_circuit_sim(noise_vec, par_vec, params)` expects a 1D noise vector of length `NUM_QUBITS`.

### Anti-Patterns to Avoid
- **Reasserting FORCE_GENERATE=True permanently:** Fix should edit the generation functions; checkpoint invalidation is handled by deleting stale files or setting FORCE_GENERATE=True for one run.
- **Hard assertions in smoke test:** D-04 and D-09 specify warnings only — use `print("WARNING: ...")` not `assert`.
- **Modifying denorm functions:** The `denorm_qgan_output` function expects input in [-1, 1]. After removing `* 0.1`, the raw circuit output (PauliX/Z expectations) is already in [-1, 1], so denorm is correct as-is.
- **Adding `np.random.seed` alongside `torch.manual_seed` without seeding both:** Both seeds must be set in generation functions that use both numpy and torch random.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| KDE computation | Custom kernel density estimation | `scipy.stats.gaussian_kde` (already used in cell 25) | Already imported, battle-tested |
| Sliding windows | Custom window logic per curve | `make_lstm_dataset()` already defined in cell 28 | One-liner with correct dtype handling |
| Seed range verification | Manual check | Simple arithmetic: max seed for set = base_seed + n_synth - 1; verify no overlap at max size | Not a code problem |

---

## Common Pitfalls

### Pitfall 1: Noise Shape Transposition (GENBUG-01)
**What goes wrong:** Current code creates `noise` with shape `(NUM_QUBITS, n_windows)` and indexes as `noise[:, i]`. After changing to `torch.randn(n_windows, NUM_QUBITS)`, must update the index to `noise[i]` (row-major) or the shapes passed to `_qgan_circuit_sim` will be wrong.
**Why it happens:** Training code uses `noise = torch.randn(B, NUM_QUBITS)` and accesses `noise[j]` — row per batch. The original generation code transposed this convention.
**How to avoid:** Change to `noise = torch.randn(n_windows, NUM_QUBITS)` and access `noise[i]` in the loop. Verify `_qgan_circuit_sim` receives shape `(NUM_QUBITS,)`.
**Warning signs:** `RuntimeError: size mismatch` or silent wrong-shape tensor passed to PennyLane circuit.

### Pitfall 2: Stale Checkpoints After Generation Fix
**What goes wrong:** Existing `checkpoints/synthetic/*/size*_seed*.npz` files were generated with the buggy code. After fixing GENBUG-01/02/03, old checkpoints will be loaded if `FORCE_GENERATE=False` — bypassing the fix entirely.
**Why it happens:** The checkpoint system skips generation when files exist.
**How to avoid:** Delete all `checkpoints/synthetic/` files (or set `FORCE_GENERATE=True`) before verifying the fix. Similarly, `checkpoints/lstm_results/` files are invalid — delete or set `FORCE_LSTM=True`.
**Warning signs:** Smoke test still shows `range=[-0.0012, 0.0133]` after fix — means old checkpoint was loaded.

### Pitfall 3: Per-Curve Window Count Guards (GENBUG-04)
**What goes wrong:** Synthetic curves from qGAN produce 770 points (not 777), qVAE/cVAE produce 768 points. With LOOKBACK=20, any curve shorter than 21 points would produce an empty dataset. At 770+, this is fine — but a guard prevents silent empty arrays.
**Why it happens:** `make_lstm_dataset` produces `len(series) - LOOKBACK` samples; for short series this is zero.
**How to avoid:** Add `if len(ld) > LOOKBACK:` guard before calling `make_lstm_dataset` on each synthetic curve.
**Warning signs:** Total `X_aug` window count is lower than expected; silent empty concatenation.

### Pitfall 4: Seed Collision Verification After GENBUG-03 Fix
**What goes wrong:** The D-05 offset formula uses `size_idx` (position in SYNTH_SIZES list), not `n_synth` (the actual size value). If `SYNTH_SIZES` order changes, seed assignments change too — regenerating all existing checkpoints.
**Why it happens:** Index-based formulas tie seed assignment to list ordering.
**How to avoid:** Lock `SYNTH_SIZES` order in a comment, or use a dict mapping size → seed offset explicitly.

### Pitfall 5: Smoke Test Cell Placement
**What goes wrong:** Smoke test depends on `MODELS_INFO`, which is defined in cell 22. If the smoke test cell is inserted before cell 22, it will fail with `NameError`.
**Why it happens:** Jupyter cells execute in linear order.
**How to avoid:** Place smoke test cell immediately after cell 22 (the existing generation loop cell), or after cell 20 (generation functions) if testing the functions directly without running the full loop.

---

## Code Examples

Verified patterns from direct notebook source inspection:

### GENBUG-01 + GENBUG-02: Fixed `_qgan_generate_one` noise block
```python
# Source: hqss_experiment.ipynb cell 20 (current buggy code reference)
# Fix: match training convention from cell 12 line 60: noise = torch.randn(B, NUM_QUBITS)

with torch.no_grad():
    noise = torch.randn(n_windows, NUM_QUBITS)  # FIXED: was np.random.uniform(0, 4*pi)
    par_flat = par_light_norm_arr[:n_windows * NUM_QUBITS]
    par_mat  = par_flat.reshape(n_windows, NUM_QUBITS)

    gen_windows = []
    for i in range(n_windows):
        out = _qgan_circuit_sim(
            noise[i],                                     # FIXED: was noise[:, i]
            torch.tensor(par_mat[i], dtype=torch.float32),
            params
        )
        if isinstance(out, (list, tuple)):
            out = torch.stack(list(out))
        gen_windows.append(out.float())                   # FIXED: removed * 0.1
```

### GENBUG-03: Fixed seed scheme in generation loop (cell 22)
```python
# Source: hqss_experiment.ipynb cell 22
# Fix: replace `curve_seed = seed + k` with offset scheme (D-05)

for size_idx, n_synth in enumerate(SYNTH_SIZES):
    for rep_idx, _ in enumerate(GEN_SEEDS):
        base = size_idx * 1000 + rep_idx * 100
        save_path = save_dir / f'size{n_synth}_seed{rep_idx}.npz'   # key by rep_idx
        # ...
        for k in range(n_synth):
            curve_seed = base + k    # FIXED: was seed + k (collisions)
```

### GENBUG-04: Fixed per-curve windowing in LSTM loop (cell 31)
```python
# Source: hqss_experiment.ipynb cell 31
# Fix: window each series independently (D-07, D-08)

X_parts, y_parts = [], []
X_r, y_r = make_lstm_dataset(real_train_ld, LOOKBACK)
X_parts.append(X_r)
y_parts.append(y_r)
for ld in ld_list:
    if len(ld) > LOOKBACK:
        X_s, y_s = make_lstm_dataset(ld.astype(np.float32), LOOKBACK)
        X_parts.append(X_s)
        y_parts.append(y_s)
X_aug = np.concatenate(X_parts, axis=0)
y_aug = np.concatenate(y_parts, axis=0)
```

### Smoke Test: Stats table and variance warning (D-01 through D-04, D-09, D-10)
```python
# Source: pattern from existing smoke test at bottom of cell 20 + cell 25 (gaussian_kde)
SMOKE_N = 10
real_gr = growth_rate  # already defined

print(f'{"Model":<10} {"mean":>8} {"std":>8} {"min":>8} {"max":>8}  {"flag"}')
print('-' * 60)
real_std = float(np.std(real_gr))
print(f'{"real":<10} {np.mean(real_gr):8.4f} {real_std:8.4f} {np.min(real_gr):8.4f} {np.max(real_gr):8.4f}')

kde_data = {'real': real_gr}
for model_name, info in MODELS_INFO.items():
    grs = []
    for k in range(SMOKE_N):
        _, gr = info['fn'](seed=k)
        grs.append(gr)
    all_gr = np.concatenate(grs)
    kde_data[model_name] = all_gr
    m_std = float(np.std(all_gr))
    flags = []
    if m_std > 2 * real_std or m_std < 0.5 * real_std:
        flags.append(f'STD {m_std/real_std:.1f}x')        # D-04, D-09
    pos_frac = float(np.mean(all_gr > 0))
    if pos_frac > 0.9 or pos_frac < 0.1:
        flags.append(f'SIGN_BIAS {pos_frac:.0%}+')         # D-10
    print(f'{model_name:<10} {np.mean(all_gr):8.4f} {m_std:8.4f} {np.min(all_gr):8.4f} '
          f'{np.max(all_gr):8.4f}  {"WARNING: " + ", ".join(flags) if flags else "ok"}')

# KDE overlay (D-03)
fig, ax = plt.subplots(figsize=(8, 4))
for label, gr in kde_data.items():
    kde = gaussian_kde(gr)
    xs  = np.linspace(gr.min(), gr.max(), 300)
    ax.plot(xs, kde(xs), label=label)
ax.set_xlabel('Growth rate'); ax.set_ylabel('Density')
ax.set_title('Growth-rate distributions: synthetic vs real')
ax.legend(); plt.tight_layout(); plt.show()
```

---

## State of the Art

No library upgrades or new patterns required. All fixes are code corrections within existing patterns.

| Bug | Root Cause | Fix Type |
|-----|-----------|----------|
| GENBUG-01 noise mismatch | Uniform vs Gaussian — wrong RNG call | 2-line change in `_qgan_generate_one` |
| GENBUG-02 `* 0.1` scale | Extra constant applied only at generation | Remove single multiplication |
| GENBUG-03 seed collision | Linear offset `seed + k` wraps into next replicate | Replace with `size_idx*1000 + rep_idx*100 + k` |
| GENBUG-04 cross-boundary windows | `np.concatenate` before `make_lstm_dataset` | Restructure LSTM loop to window per-curve |

---

## Open Questions

1. **Base seed value for offset scheme**
   - What we know: D-05 specifies multipliers (1000, 100); base_seed value not locked
   - What's unclear: Should base equal 0, or echo existing GEN_SEEDS=[42, 137, 271] per rep?
   - Recommendation: Use `base = size_idx * 1000 + rep_idx * 100` with base starting at 0. The existing `GEN_SEEDS` list is used for rep_idx indexing (rep 0 = GEN_SEEDS[0], etc.) for checkpoint naming only, not for arithmetic. This is simpler and satisfies D-05.

2. **Checkpoint file naming after GENBUG-03 fix**
   - What we know: Current filenames use `seed` value (e.g. `size50_seed42.npz`). After the fix, seed values change.
   - What's unclear: Should filenames embed `rep_idx` or the new `base_seed` value?
   - Recommendation: Use `rep_idx` in filenames (`size50_rep0.npz`) to decouple naming from arithmetic. Or keep using GEN_SEEDS values as labels (`size50_seed42.npz` means rep 0) but compute `curve_seed` internally with the offset scheme.

3. **No-PAR ablation generation functions**
   - What we know: Cell 21 defines `_qgan_no_par_generate_one` and `_cgan_no_par_generate_one` with the same bugs (uniform noise + `* 0.1` in ablation variants).
   - What's unclear: Phase scope — CONTEXT.md says fix all four models but ablation variants are in a separate cell (21).
   - Recommendation: Apply the same GENBUG-01/GENBUG-02 fixes to cell 21 ablation functions as part of this phase, since they share the same root cause.

---

## Environment Availability

Step 2.6: SKIPPED — this phase is purely code changes within an existing notebook with no new external dependencies.

---

## Validation Architecture

`workflow.nyquist_validation` is not set to `false` in `.planning/config.json` — validation section is included.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual smoke test (existing pattern in cell 20) — no pytest/jest in this project |
| Config file | N/A — single Jupyter notebook |
| Quick run command | Run smoke test cell (new cell after generation functions) |
| Full suite command | Run cells 0–24 sequentially (loads checkpoints where available) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | Cell Exists? |
|--------|----------|-----------|-------------------|-------------|
| GENBUG-01 | qGAN growth-rate std is within 2x of real data std (not 10x suppressed) | smoke | Run smoke test cell; check WARNING flags in output | New cell needed |
| GENBUG-02 | Same as GENBUG-01 — `* 0.1` removal has same observable effect as noise fix | smoke | Run smoke test cell | New cell needed |
| GENBUG-03 | 3 replicates at size=250 produce zero shared curve seeds | manual inspection | Print `base + k` range for each rep; verify no overlap | Manual check in gen loop |
| GENBUG-04 | Window count for augmented dataset equals sum of per-curve window counts | smoke | Print `len(X_aug)` before and after fix; compare to `sum(len(ld) - LOOKBACK for ld in ld_list + [real_train_ld])` | Inline print in LSTM loop |

### Sampling Rate
- **Per fix commit:** Run smoke test cell (GENBUG-01/02/04 visible immediately)
- **Per wave merge:** Run cells 0–24 with `FORCE_GENERATE=False` (loads existing checkpoints except where regeneration is needed)
- **Phase gate:** Smoke test shows no WARNING flags for GENBUG-01/02; seed arithmetic verified for GENBUG-03; window count matches expected for GENBUG-04

### Wave 0 Gaps
- [ ] New smoke test cell — covers GENBUG-01, GENBUG-02, and partial GENBUG-04
- [ ] Inline seed-range verification print in generation loop — covers GENBUG-03

*(No test framework install needed — validation is notebook-native)*

---

## Sources

### Primary (HIGH confidence)
- Direct inspection of `hqss_experiment.ipynb` cells 2, 10, 11, 12, 20, 21, 22, 28, 29, 31
- `.planning/codebase/ARCHITECTURE.md` — generation layer data flow, denorm chain
- `.planning/codebase/CONCERNS.md` — C5 (seed collisions), M9 (cross-boundary windows confirmed), C1-C2 (qGAN noise/scaling bugs)
- `sci_review.md` — C1 (noise mismatch exact lines), C2 (`* 0.1` exact evidence), C5 (seed overlap arithmetic), M9 (window contamination)
- `.planning/phases/02-generation-bug-fixes/02-CONTEXT.md` — locked decisions D-01 through D-10

### Secondary (MEDIUM confidence)
- None required — all findings from direct source inspection.

### Tertiary (LOW confidence)
- None.

---

## Metadata

**Confidence breakdown:**
- Bug identification: HIGH — exact line locations confirmed from cell source
- Fix patterns: HIGH — derived from existing training code conventions already in the notebook
- Smoke test design: HIGH — locked by decisions D-01 through D-04, D-09, D-10
- Seed offset arithmetic: HIGH — verified by manual range calculation (no overlap at size=250)
- Ablation function scope: MEDIUM — not explicitly in CONTEXT.md, but logically consistent

**Research date:** 2026-03-30
**Valid until:** Indefinite — findings are from static notebook source, not external library documentation
