---
phase: 1
slug: preprocessing
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-18
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Jupyter notebook cell execution (papermill / manual kernel restart) |
| **Config file** | `hqss_experiment.ipynb` (self-contained) |
| **Quick run command** | `jupyter nbconvert --execute --to notebook --ExecutePreprocessor.timeout=300 hqss_experiment.ipynb` |
| **Full suite command** | `jupyter nbconvert --execute --to notebook --ExecutePreprocessor.timeout=1800 hqss_experiment.ipynb` |
| **Estimated runtime** | ~120 seconds (quick, reduced epochs) |

---

## Sampling Rate

- **After every task commit:** Run quick validation (cells 0-15 subset)
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | PREP-01 | grep | `grep -c "lambert_w" hqss_experiment.ipynb` returns 0 | ✅ | ⬜ pending |
| 1-01-02 | 01 | 1 | PREP-01 | grep | `grep -c "specific.growth.rate\|specific_growth_rate" hqss_experiment.ipynb` > 0 | ✅ | ⬜ pending |
| 1-01-03 | 01 | 1 | PREP-02 | grep | `grep -c "log.return\|log_return\|Log Return" hqss_experiment.ipynb` returns 0 | ✅ | ⬜ pending |
| 1-01-04 | 01 | 1 | PREP-02 | grep | `grep "d(ln OD)/dt" hqss_experiment.ipynb` matches | ✅ | ⬜ pending |
| 1-02-01 | 02 | 2 | PREP-03 | execution | Notebook produces two LSTM evaluation paths with/without PAR_LIGHT | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] No external test framework needed — validation is via notebook execution and grep checks
- [ ] Ensure `FORCE_TRAIN_*` flags are all set to `True` for retraining validation

*Existing notebook execution infrastructure covers all phase requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Biological justification cell is scientifically accurate | PREP-02 | Content review | Read the markdown cell; verify µ = d(ln OD)/dt derivation is correct |
| PAR_LIGHT ablation comparison is meaningful | PREP-03 | Requires judgment | Check that performance difference table shows plausible metrics |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
