# Phase 1: Preprocessing - Research

**Researched:** 2026-03-18
**Domain:** Jupyter notebook preprocessing pipeline refactor — Lambert-W removal, biological terminology, PAR_LIGHT ablation
**Confidence:** HIGH (all findings from direct codebase inspection)

## Summary

Phase 1 makes surgical edits to a single self-contained Jupyter notebook (`hqss_experiment.ipynb`, 42 cells). The work has three independent threads: (1) delete Lambert-W Gaussianization code and simplify the denormalization chain, (2) rename "log returns" to "specific growth rate" with one markdown justification cell, and (3) add PAR_LIGHT ablation — train no-PAR variants of both GANs, run both conditions through LSTM evaluation, and report the comparison table.

The preprocessing pipeline is defined in cell 4 (data loading through windowing). It feeds `gan_loader` (cell 11) and `vae_loader` (cell 11) which are consumed by all four model training cells. The denormalization functions in cell 7 (`denorm_qgan_output`, `denorm_vae_output`) currently chain Lambert-W inverse before z-score inversion — both must be rewritten. The generation functions in cell 14 pass `DELTA_LW`, `LW_MIN`, `LW_MAX` as arguments — all of these references must be removed.

The PAR_LIGHT ablation is the most structurally complex task. For GANs: the current qGAN circuit encodes PAR_LIGHT via RY rotations per qubit (cell 6) and the current cGAN concatenates PAR noise+par before the MLP (cell 9). The "without PAR" variants require genuinely different model architectures — the conditioning input must be removed from both circuit and MLP, not zeroed. VAEs (qVAE and cVAE) do not expose a PAR_LIGHT input to the generation function, so their existing generated curves serve directly as the "without PAR" condition without retraining.

**Primary recommendation:** Work in three focused passes — (1) Lambert-W deletion + denorm simplification, (2) terminology rename + markdown cell, (3) ablation model definitions + parallel LSTM evaluation loop. Each pass is independently testable by running the affected cells.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Normalization after Lambert-W removal:**
- Remove Lambert-W entirely — delete `lambert_w_gaussianize()`, `lambert_w_inverse()`, `_kurtosis_for_delta()`, and all related constants (DELTA_LW, LW_MIN, LW_MAX)
- Pipeline becomes: OD → dither → specific growth rate → z-score → scale[-1,1] (for GANs) or z-score only (for VAEs)
- Keep the existing split: GANs (qGAN, cGAN) receive [-1,1] scaled input; VAEs (qVAE, cVAE) receive z-scored (unbounded) input
- Dithering step (±0.005 noise) is kept as-is — standard numerical stability trick
- All Lambert-W code is deleted entirely (not commented out) — git history preserves it

**PAR_LIGHT ablation design:**
- Full pipeline comparison: train/generate with PAR_LIGHT vs without for all 4 models, run both through LSTM evaluation
- For GANs: retrain separate qGAN/cGAN WITHOUT PAR_LIGHT conditioning input (not zero-fill — genuine architectural ablation)
- For VAEs: current behavior IS the "without" condition (they don't take PAR_LIGHT as a separate input) — no retraining needed
- Results presented as a comparison table (with-PAR vs without-PAR LSTM metrics: MSE, MAPE per model) plus a 1-2 sentence markdown commentary cell
- Ablation checkpoints stored in same directory with different naming (e.g., `qgan_no_par.pt`)

**Biological framing:**
- Rename all variable names throughout: `log_delta` → `growth_rate` (or similar biological name)
- One markdown cell placed immediately before the growth rate computation cell
- Cell contains: equation µ = d(ln OD)/dt, brief explanation that this is the standard microbiological specific growth rate
- No literature references — the equation is self-evident to the target audience
- All user-facing text (markdown cells, print statements, comments) updated to use "specific growth rate" instead of "log returns"

**Checkpoint strategy:**
- Retrain ALL 4 models on the new (no-Lambert-W) pipeline in Phase 1
- Use reduced epochs for quantum models (qGAN, qVAE) to manage compute cost — full training deferred to Phase 4 (data integrity fix)
- Classical models (cGAN, cVAE) train at full hyperparameters (fast enough)
- Old Lambert-W checkpoints are replaced entirely — not kept in a legacy directory

### Claude's Discretion
- Exact reduced epoch counts for quantum models in Phase 1
- Variable naming choice (growth_rate vs mu_growth vs specific_growth_rate)
- Denormalization function refactoring details after Lambert-W removal
- Print statement formatting and validation output style

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PREP-01 | Remove Lambert-W Gaussianization — use z-score normalization only on specific growth rates | Cell 4 inspection: 4 functions + 3 constants to delete; cell 7 denorm functions to rewrite; cell 11 windowing to reroute from `gaussianized` to `norm_growth_rate`; cell 14 generation functions to strip LW args |
| PREP-02 | Rename "log returns" to "specific growth rate" throughout notebook with biological justification text | Variable `log_delta` used in cells 4-5, 7, 11, 14, 15, 19, 22, 25+; markdown cells 0, 17, and diagnostic labels in cell 5 also need updating; one new markdown cell before growth rate computation |
| PREP-03 | PAR_LIGHT ablation — train and generate with vs without light conditioning, quantify contribution to downstream LSTM performance | qGAN circuit (cell 6) encodes PAR via RY; no-PAR variant drops those rotations; cGAN concatenates PAR before MLP (cell 9); no-PAR variant uses noise-only input; VAEs need no retraining; ablation loop and results table are new cells |
</phase_requirements>

---

## Standard Stack

### Core (already in notebook)
| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| numpy | (existing) | Array operations, diff, log, cumsum | Used throughout |
| scipy.special.lambertw | (existing) | BEING DELETED | Remove import after deletion |
| scipy.optimize.minimize_scalar | (existing) | BEING DELETED (kurtosis minimization) | Remove after deletion |
| scipy.stats.kurtosis | (existing) | BEING DELETED | Remove after deletion if unused elsewhere |
| torch / torch.utils.data | (existing) | DataLoaders, model training | Unchanged |
| pandas | (existing) | CSV loading | Unchanged |

**After Phase 1 removal, check whether `minimize_scalar`, `lambertw`, and `kurtosis` are still needed anywhere else in the notebook before removing the imports.**

### No new dependencies required

This phase is purely a refactor — no new packages are introduced. All needed tools are already imported.

---

## Architecture Patterns

### Current Preprocessing Pipeline (to be modified)

```
Cell 4:
  raw_od → dither (±DITHER) → log(OD) diff → log_delta (777 pts)
  log_delta → z-score (MU, SIGMA) → norm_log_delta
  norm_log_delta → lambert_w_gaussianize(DELTA_LW) → gaussianized   ← DELETE
  gaussianized → scale[-1,1] (LW_MIN, LW_MAX) → scaled_data         ← SIMPLIFY
  raw_light → normalize [0,1] → par_norm_trim
  raw_light → scale[-1,1] → par_scaled_trim

Cell 11:
  gan_loader: windows from scaled_data, WINDOW_GAN=10, stride=2
  vae_loader: windows from gaussianized, WINDOW_VAE=32, stride=1    ← CHANGE TO norm_growth_rate
```

### Target Preprocessing Pipeline (after Phase 1)

```
Cell 4:
  raw_od → dither (±DITHER) → log(OD) diff → growth_rate (777 pts)
  growth_rate → z-score (MU, SIGMA) → norm_growth_rate
  norm_growth_rate → scale[-1,1] (GR_MIN, GR_MAX) → scaled_data     ← GAN input
  raw_light → normalize [0,1] → par_norm_trim
  raw_light → scale[-1,1] → par_scaled_trim

Cell 11:
  gan_loader: windows from scaled_data, WINDOW_GAN=10, stride=2     (unchanged)
  vae_loader: windows from norm_growth_rate, WINDOW_VAE=32, stride=1 (was gaussianized)
```

### Current Denormalization Chain (to be modified)

```python
# Cell 7 — denorm_qgan_output (currently):
flat → unscale[-1,1] using (LW_MIN, LW_MAX) → lambert_w_inverse(DELTA_LW) → *SIGMA + MU → growth_rate

# Cell 7 — denorm_vae_output (currently):
flat → lambert_w_inverse(DELTA_LW) → *SIGMA + MU → growth_rate
```

### Target Denormalization Chain (after Phase 1)

```python
# denorm_qgan_output (simplified):
flat → unscale[-1,1] using (GR_MIN, GR_MAX) → *SIGMA + MU → growth_rate

# denorm_vae_output (simplified):
flat → *SIGMA + MU → growth_rate
```

### PAR_LIGHT Ablation Architecture

The ablation requires four new elements in the notebook:

**1. No-PAR qGAN circuit variant (new function alongside cell 6):**
Current circuit injects PAR via `qml.RY(par_light_params[q] * np.pi, wires=q)` for each qubit. The no-PAR variant simply omits those 5 RY gates. The rest of the circuit (Hadamard init, IQP RZ, noise RZ, StronglyEntangling layers, final RX/RY, PauliX/Z measurements) is identical. The parameter count does not change — `params_pqc` stays at 75 parameters because PAR was never a trained parameter, only a runtime input.

**2. No-PAR cGAN circuit variant:**
Current `ClassicalGenerator.forward(noise, par)` concatenates `[noise | par]` as input. The no-PAR variant's `forward(noise)` uses only `noise` (dimension `NUM_QUBITS=5`). This changes the first Linear layer from `noise_dim + par_dim = 10` to `noise_dim = 5`. The no-PAR cGAN is a distinct `ClassicalGenerator` subclass or instantiated with `par_dim=0`.

**3. Ablation generation loop:**
Mirrors the existing `MODELS_INFO` pattern. A second dict `ABLATION_MODELS_INFO` (or extended `MODELS_INFO` with `'qgan_no_par'`, `'cgan_no_par'`, `'qvae'`, `'cvae'` keys pointing to no-PAR functions). Existing VAE entries are reused directly.

**4. Ablation LSTM evaluation and comparison table:**
After generation, run the same LSTM augmentation loop (cells 22-27 pattern) for ablation curves. Produce a markdown table:

| Model | With PAR MSE | Without PAR MSE | Delta MSE | With PAR MAPE | Without PAR MAPE |
|-------|-------------|-----------------|-----------|---------------|------------------|
| qGAN  | ...         | ...             | ...       | ...           | ...              |
| cGAN  | ...         | ...             | ...       | ...           | ...              |
| qVAE  | N/A (no PAR)| same            | 0         | ...           | ...              |
| cVAE  | N/A (no PAR)| same            | 0         | ...           | ...              |

### Variable Naming Decision (Claude's Discretion)

Use `growth_rate` for the primary variable (replacing `log_delta`). This is terse, biologically meaningful, and consistent with the µ symbol used in the justification cell. Avoid `mu_growth` (conflicts with the z-score `MU` constant) and `specific_growth_rate` (too verbose for repeated use in array expressions).

Constants rename map:
- `MU` → keep (z-score mean of growth_rate — reusing MU is fine, it's the z-score mu)
- `SIGMA` → keep
- `LW_MIN`, `LW_MAX` → rename to `GR_MIN`, `GR_MAX` (min/max of z-scored growth_rate, for [-1,1] scaling)
- `DELTA_LW` → delete
- `log_delta` → `growth_rate`
- `norm_log_delta` → `norm_growth_rate`
- `gaussianized` → delete (replaced by `norm_growth_rate` for VAE windowing)
- `scaled_data` → keep (this name remains accurate: it's the [-1,1] scaled data for GANs)

### Reduced Epoch Counts (Claude's Discretion)

Recommended reduced epoch counts for quantum models in Phase 1:
- **qGAN**: 100 epochs (vs. full 500). The HPO-optimal checkpoint already exists; Phase 1 trains a new checkpoint on the simplified pipeline. 100 epochs provides enough convergence signal to verify the pipeline works without the 30-90 min full runtime.
- **qVAE**: 20 epochs (vs. full 50). qVAE already trains for only 50; 20 is enough to verify the new `vae_loader` (now sourced from `norm_growth_rate` instead of `gaussianized`) works without hitting diminishing returns.
- Classical models (cGAN: full CGAN_EPOCHS, cVAE: full CVAE_EPOCHS) — fast enough, no reduction needed.

Add a constant `PHASE1_REDUCED = True` and conditional epoch selection at the top of each quantum training cell to make this explicit and easy to change in Phase 4.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Min/max scaling to [-1,1] | Custom scaler class | `(x - x.min()) / (x.max() - x.min()) * 2 - 1` inline | Already the pattern; one line; no sklearn needed |
| Z-score normalization | Custom class | `(x - x.mean()) / x.std()` inline | Already the pattern |
| No-PAR cGAN input | New nn.Module subclass | Instantiate ClassicalGenerator with `par_dim=0`, change first layer input size | Simpler; consistent with existing factory pattern |

**Key insight:** The entire preprocessing layer is pure numpy/scipy one-liners. There is no external preprocessing library (sklearn, etc.) — don't introduce one. Keep the same inline style.

---

## Common Pitfalls

### Pitfall 1: Stale checkpoint loaded after pipeline change
**What goes wrong:** `FORCE_TRAIN_*` flags default to `False`. After changing preprocessing constants, the old Lambert-W-trained checkpoint loads silently and generates using old normalization. The denormalization then applies the new (simplified) chain to data that was trained on the old chain.
**Why it happens:** The checkpoint loading block checks only file existence, not pipeline version.
**How to avoid:** Set `FORCE_TRAIN_QGAN = FORCE_TRAIN_QVAE = FORCE_TRAIN_CGAN = FORCE_TRAIN_CVAE = True` at the top of the notebook when executing Phase 1 for the first time. Also delete old checkpoint files or rename them before running to avoid confusion.
**Warning signs:** Generated OD curves look physically implausible (wrong scale, extreme values) even though the notebook appears to run without errors.

### Pitfall 2: VAE windowing still uses `gaussianized`
**What goes wrong:** Cell 11 builds `vae_loader` from `gaussianized`. If only cell 4 is updated to remove the Lambert-W step but cell 11 is not updated to point to `norm_growth_rate`, the VAE trains on a variable that no longer exists — NameError at runtime, or worse, silently uses a stale global if cells are run out of order.
**Why it happens:** `gaussianized` is computed in cell 4 and consumed in cell 11; they're separate cells.
**How to avoid:** When deleting `gaussianized` from cell 4, immediately update cell 11 in the same edit pass.
**Warning signs:** `NameError: name 'gaussianized' is not defined` when running cell 11.

### Pitfall 3: Lambert-W constants still passed to denorm functions
**What goes wrong:** `denorm_qgan_output` and `denorm_vae_output` in cell 7 accept `delta_lw` as a parameter. Cell 14 generation functions call them with `DELTA_LW`. If cell 7 is rewritten to remove LW but cell 14 still passes `DELTA_LW` (which no longer exists), NameError occurs.
**Why it happens:** The parameter-passing chain spans cell 7 → cell 14.
**How to avoid:** When rewriting denorm functions in cell 7, also update all callers in cell 14 in the same pass. Also update the IBM generation function in cell 39 (`_qgan_generate_one_ibm`) which also calls `denorm_qgan_output` with `DELTA_LW, LW_MIN, LW_MAX`.
**Warning signs:** `NameError: name 'DELTA_LW' is not defined` — or `LW_MIN`, `LW_MAX`.

### Pitfall 4: IBM generation cell not updated
**What goes wrong:** Cell 39 (`_qgan_generate_one_ibm`) is a copy of `_qgan_generate_one` that also calls `denorm_qgan_output(gen_windows, MU, SIGMA, DELTA_LW, LW_MIN, LW_MAX)`. This is easy to miss because it's far from the main preprocessing cells.
**Why it happens:** The IBM cells (cells 36-42) are a near-duplicate of the simulation cells.
**How to avoid:** Search the notebook source for all occurrences of `DELTA_LW`, `LW_MIN`, `LW_MAX`, `lambert_w`, `gaussianized`, `log_delta`, `log return` before declaring the rename complete.
**Warning signs:** The IBM section fails while the simulation section works fine.

### Pitfall 5: No-PAR GAN DataLoader still passes PAR
**What goes wrong:** The no-PAR GAN variants train on `gan_loader` which yields `(window, par_batch)` tuples. The no-PAR training loop must ignore or not use the `par_batch`. If a copy-paste of the existing training loop forgets to drop PAR, the no-PAR model silently trains with PAR conditioning.
**Why it happens:** `gan_loader` always yields two-element tuples; the training loop signature expects both.
**How to avoid:** In the no-PAR training loop, unpack as `for real_batch, _ in gan_loader:` and don't pass any conditioning signal to the no-PAR circuit/MLP.
**Warning signs:** No-PAR model performance is suspiciously similar to the with-PAR model.

### Pitfall 6: `scipy.special.lambertw` import left behind
**What goes wrong:** Removing Lambert-W functions but leaving `from scipy.special import lambertw` in cell 2 does not cause an error but leaves dead imports, and `minimize_scalar` and `kurtosis` may also become unused.
**Why it happens:** Cell 2 imports are all at the top; it's easy to forget to clean them.
**How to avoid:** After deleting Lambert-W code, re-check cell 2 imports. Remove `from scipy.special import lambertw`, `from scipy.optimize import minimize_scalar`, and `from scipy.stats import kurtosis` if not used elsewhere. Verify by searching remaining cells for each name.

### Pitfall 7: Diagnostic plot labels not updated
**What goes wrong:** Cell 5's preprocessing diagnostic plot has axis labels `'Log Return'` and title `'Log Returns Time Series'`, `'Log Returns Distribution'`. These persist as "log return" in output figures even after all code is renamed.
**Why it happens:** String literals in `set_xlabel`, `set_title`, etc. are not renamed by variable renaming.
**How to avoid:** Update all string literals in cell 5 as part of the PREP-02 rename pass. Also update the Q-Q plot title.

---

## Code Examples

Verified from direct codebase inspection:

### Current Lambert-W block to delete (cell 4, lines 24-43)
```python
# DELETE THIS ENTIRE BLOCK:
def _kurtosis_for_delta(d, data):
    sign = np.sign(data)
    lw   = lambertw(d * data**2).real
    lw   = np.maximum(lw, 0)
    return abs(kurtosis(sign * np.sqrt(lw / d), fisher=True))

res = minimize_scalar(_kurtosis_for_delta, bounds=(0.01, 2.0),
                      args=(norm_log_delta.astype(np.float64),), method='bounded')
DELTA_LW = res.x
print(f'Optimal Lambert-W delta: {DELTA_LW:.4f}  (|kurtosis|: {res.fun:.6f})')

def lambert_w_gaussianize(x, delta): ...
def lambert_w_inverse(x, delta): ...

gaussianized = lambert_w_gaussianize(norm_log_delta, DELTA_LW)

# ── 3.5 Scale to [-1, 1]  (qGAN training space) ────────────────────────────
LW_MIN = float(gaussianized.min())
LW_MAX = float(gaussianized.max())
scaled_data = (-1.0 + 2.0 * (gaussianized - LW_MIN) / (LW_MAX - LW_MIN)).astype(np.float32)
```

### Replacement: direct scaling from z-score (cell 4)
```python
# After z-score normalization, scale directly to [-1,1] for GANs:
GR_MIN = float(norm_growth_rate.min())
GR_MAX = float(norm_growth_rate.max())
scaled_data = (-1.0 + 2.0 * (norm_growth_rate - GR_MIN) / (GR_MAX - GR_MIN)).astype(np.float32)

print(f'Scaled [-1,1]: mean={scaled_data.mean():.4f}, std={scaled_data.std():.4f}')
print(f'Z-score range: [{GR_MIN:.4f}, {GR_MAX:.4f}]')
```

### Current denorm_qgan_output to rewrite (cell 7)
```python
def denorm_qgan_output(gen_windows, mu, sigma, delta_lw, lw_min, lw_max):
    flat = gen_windows.reshape(-1).detach().float().numpy()
    unscaled = 0.5 * (flat + 1.0) * (lw_max - lw_min) + lw_min
    un_gauss = lambert_w_inverse(unscaled, delta_lw).astype(np.float64)
    return (un_gauss * sigma + mu).astype(np.float32)
```

### Replacement: simplified denorm without LW (cell 7)
```python
def denorm_qgan_output(gen_windows, mu, sigma, gr_min, gr_max):
    """Reverse qGAN preprocessing: [-1,1] → z-score → growth_rate."""
    flat = gen_windows.reshape(-1).detach().float().numpy()
    # Unscale [-1, 1] → z-score space
    unscaled = 0.5 * (flat + 1.0) * (gr_max - gr_min) + gr_min
    # Denormalize → growth_rate space
    return (unscaled * sigma + mu).astype(np.float32)

def denorm_vae_output(windows_np, mu, sigma):
    """Reverse VAE preprocessing: z-score → growth_rate."""
    flat = windows_np.reshape(-1).astype(np.float64)
    return (flat * sigma + mu).astype(np.float32)
```

### VAE DataLoader update (cell 11)
```python
# Change FROM:
vae_windows = _sliding_windows(gaussianized, WINDOW_VAE, stride=STRIDE_VAE)
# Change TO:
vae_windows = _sliding_windows(norm_growth_rate, WINDOW_VAE, stride=STRIDE_VAE)
```

### Biological justification markdown cell (new cell before growth_rate computation)
```markdown
## Biological Framing: Specific Growth Rate

The core quantity modelled throughout this notebook is the **specific growth rate**:

$$\mu = \frac{d(\ln \text{OD})}{dt}$$

This is the standard microbiological definition of specific growth rate — the instantaneous
fractional rate of increase in biomass (approximated here by optical density). Computing
the first difference of log(OD) yields a discrete approximation of µ at each measurement
interval.
```

### No-PAR qGAN circuit function (new, alongside cell 6)
```python
def _qgan_circuit_fn_no_par(noise_params, params_pqc):
    """qGAN circuit without PAR_LIGHT conditioning."""
    idx = 0
    for q in range(NUM_QUBITS):
        qml.Hadamard(wires=q)
    for q in range(NUM_QUBITS):
        qml.RZ(params_pqc[idx], wires=q); idx += 1
    for q in range(NUM_QUBITS):
        qml.RZ(noise_params[q], wires=q)
    # NO PAR_LIGHT RY block
    for layer in range(NUM_LAYERS):
        for q in range(NUM_QUBITS):
            qml.Rot(params_pqc[idx], params_pqc[idx+1], params_pqc[idx+2], wires=q); idx += 3
        r = (layer % (NUM_QUBITS - 1)) + 1
        for q in range(NUM_QUBITS):
            qml.CNOT(wires=[q, (q + r) % NUM_QUBITS])
    for q in range(NUM_QUBITS):
        qml.RX(params_pqc[idx], wires=q); idx += 1
        qml.RY(params_pqc[idx], wires=q); idx += 1
    return (tuple(qml.expval(qml.PauliX(q)) for q in range(NUM_QUBITS)) +
            tuple(qml.expval(qml.PauliZ(q)) for q in range(NUM_QUBITS)))
```

### No-PAR cGAN generation (instantiation approach)
```python
# The ClassicalGenerator already accepts noise_dim and par_dim.
# For no-PAR variant, set par_dim=0 and adjust first layer:
class ClassicalGeneratorNoPAR(nn.Module):
    """MLP generator: noise only -> window in [-1,1]. No PAR_LIGHT conditioning."""
    def __init__(self, noise_dim=NUM_QUBITS, output_dim=WINDOW_GAN, hidden=HIDDEN_CGAN):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(noise_dim, hidden),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden, hidden * 2),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden * 2, hidden),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden, output_dim),
            nn.Tanh(),
        )
    def forward(self, noise):
        return self.net(noise)
```

### Ablation comparison table output pattern
```python
# After running LSTM evaluation for both conditions, produce a table:
ablation_rows = []
for model_name in ['qgan', 'cgan', 'qvae', 'cvae']:
    for condition in ['with_par', 'no_par']:
        mse_vals = [...]   # collected from LSTM runs
        mape_vals = [...]
        ablation_rows.append({
            'Model': model_name.upper(),
            'Condition': condition,
            'MSE (mean)': np.mean(mse_vals),
            'MAPE (mean)': np.mean(mape_vals),
        })
ablation_df = pd.DataFrame(ablation_rows)
# Pivot to wide format for readable comparison:
print(ablation_df.pivot(index='Model', columns='Condition',
                        values=['MSE (mean)', 'MAPE (mean)']))
```

---

## State of the Art

| Old Approach | Current Approach | Change | Impact |
|--------------|------------------|--------|--------|
| Lambert-W Gaussianization (Goerg 2015, from finance) | Z-score normalization only | Phase 1 | Simpler denorm chain; removes unvalidated assumption about OD distribution shape |
| "log returns" terminology (finance) | "specific growth rate" µ = d(ln OD)/dt (microbiology) | Phase 1 | Correct biological framing for peer review |
| No PAR_LIGHT ablation | With-PAR vs without-PAR comparison table | Phase 1 | Quantifies conditioning contribution; addresses peer reviewer concern M6 |

**Deprecated by Phase 1:**
- `_kurtosis_for_delta()`: kurtosis minimization for delta fitting — biologically unjustified, delete
- `lambert_w_gaussianize()`: Goerg transform — delete
- `lambert_w_inverse()`: inverse — delete
- Constants `DELTA_LW`, `LW_MIN`, `LW_MAX`: delete; replace with `GR_MIN`, `GR_MAX`

---

## Open Questions

1. **`scipy.stats.kurtosis` used elsewhere?**
   - What we know: Imported in cell 2 for `_kurtosis_for_delta`. Quality metrics in cell 19 use `compute_stylized_facts` which may compute kurtosis internally.
   - What's unclear: Whether `kurtosis` from scipy.stats is called directly anywhere outside cell 4.
   - Recommendation: Search all cells for `kurtosis` before removing the import. If only used in the deleted block, remove it.

2. **Does the no-PAR qGAN training loop use `gan_loader` which yields `(window, par_batch)` tuples?**
   - What we know: Yes — cell 11 always produces paired windows.
   - What's unclear: Whether to build a separate no-PAR DataLoader (windows only) or just unpack and ignore PAR.
   - Recommendation: Reuse `gan_loader` and unpack as `for real_batch, _ in gan_loader:`. No separate loader needed; simpler to maintain.

3. **Ablation checkpoint naming for no-PAR VAE results?**
   - What we know: VAEs produce the "no PAR" condition naturally (no retraining needed).
   - What's unclear: Whether to copy existing VAE synthetic files into the ablation directory or reference them in-place.
   - Recommendation: Reference in-place by pointing `ABLATION_MODELS_INFO['qvae']` and `ABLATION_MODELS_INFO['cvae']` at the existing `synthetic/qvae` and `synthetic/cvae` subdirectories. No file duplication needed.

---

## Validation Architecture

No formal test framework exists (no pytest, no jest, no vitest config — single notebook project). All validation is cell-level execution + print statement inspection.

### Phase Requirements → Validation Map

| Req ID | Behavior | Validation Method | Automated? |
|--------|----------|-------------------|-----------|
| PREP-01 | Lambert-W absent; only z-score applied | Search notebook source for `lambert_w`, `DELTA_LW`, `LW_MIN`, `LW_MAX` — all must be absent; run cell 4 and check printed output shows no LW delta line | Manual grep + cell run |
| PREP-01 | VAE DataLoader uses `norm_growth_rate` not `gaussianized` | Run cell 11; no NameError; `vae_windows` shape unchanged (same as before) | Cell run |
| PREP-01 | Denormalization produces same-scale output | Run cell 14 generation for one model; verify `growth_rate` output has ~same mean/std as the old `log_delta` (print the stats) | Cell run + print check |
| PREP-02 | No "log return" text in notebook | Search notebook JSON source for `log return`, `log_delta`, `Log Return` (case variants) — all must be absent from non-git-history content | grep on .ipynb |
| PREP-02 | Biological justification cell present before growth_rate computation | Inspect cell order: markdown cell with µ = d(ln OD)/dt immediately precedes growth_rate diff computation | Manual inspection |
| PREP-03 | Two complete generation+LSTM paths run | Execute notebook through ablation loop; verify `ablation_df` table populated with non-NaN values for all 4 models | Cell run |
| PREP-03 | With-PAR vs without-PAR comparison table displayed | Final ablation markdown cell shows table with MSE/MAPE for both conditions | Cell run + visual check |

### Sampling Protocol

Since there is no automated test runner, define a minimal smoke-test sequence after each plan's edits:

- **Per editing session:** Run only the modified cell(s) + all cells that depend on them (cell 4 → cell 5 → cell 7 → cell 11 is the minimum dependency chain after preprocessing changes)
- **Phase gate (before closing Phase 1):** Run the full notebook top-to-bottom with `FORCE_TRAIN_CGAN = FORCE_TRAIN_CVAE = True` and reduced-epoch flags for quantum models; verify all cells complete without error; verify ablation table is produced

---

## Sources

### Primary (HIGH confidence)
- Direct inspection of `hqss_experiment.ipynb` (cells 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 39) — all code patterns, variable names, function signatures
- `.planning/codebase/ARCHITECTURE.md` — data flow diagram, layer descriptions, denorm chain
- `.planning/codebase/CONVENTIONS.md` — naming patterns, code style
- `.planning/phases/01-preprocessing/01-CONTEXT.md` — locked decisions, discretion areas
- `sci_review.md` — peer review critique motivating Lambert-W removal (items M7, 8) and biological framing

### Secondary (MEDIUM confidence)
- `.planning/REQUIREMENTS.md` — PREP-01, PREP-02, PREP-03 acceptance criteria (directly copied)
- `.planning/PROJECT.md` — single notebook constraint, quantum circuit preservation constraint

### Tertiary (LOW confidence — not researched, not needed)
- No external library research required for this phase (pure refactor, no new dependencies)

---

## Metadata

**Confidence breakdown:**
- Lambert-W deletion scope: HIGH — all code locations verified by direct cell inspection
- New pipeline math: HIGH — trivial algebra (z-score → scale [-1,1] without LW step)
- PAR_LIGHT ablation architecture: HIGH — qGAN circuit and cGAN MLP structure confirmed in cells 6 and 9
- Variable naming recommendation: HIGH — consistent with conventions and avoids known name collisions
- Reduced epoch counts: MEDIUM — 100 qGAN / 20 qVAE are informed estimates; actual convergence must be visually verified

**Research date:** 2026-03-18
**Valid until:** This research describes code that will be modified in Phase 1. After Phase 1 implementation, the research is superseded by the new notebook state.
