---
phase: 2
slug: generation-bug-fixes
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-30
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual smoke test (notebook-native — no pytest/jest in project) |
| **Config file** | N/A — single Jupyter notebook |
| **Quick run command** | Run smoke test cell (new cell after generation functions) |
| **Full suite command** | Run cells 0–24 sequentially (loads checkpoints where available) |
| **Estimated runtime** | ~30 seconds (smoke test only); ~5 minutes (full suite with cached checkpoints) |

---

## Sampling Rate

- **After every task commit:** Run smoke test cell
- **After every plan wave:** Run cells 0–24 sequentially
- **Before `/gsd:verify-work`:** Full suite must show no WARNING flags
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | GENBUG-01 | smoke | Run smoke test cell; check qGAN std within 2x of real | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | GENBUG-02 | smoke | Run smoke test cell; check qGAN range is [-1,1] not [-0.1,0.1] | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 1 | GENBUG-03 | manual | Print base+k ranges per rep; verify no overlap | ❌ W0 | ⬜ pending |
| 02-01-04 | 01 | 1 | GENBUG-04 | smoke | Print len(X_aug) vs sum of per-curve windows | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] New smoke test cell — covers GENBUG-01, GENBUG-02, and partial GENBUG-04 (stats table + KDE overlay + variance/sign warnings)
- [ ] Inline seed-range verification print in generation loop — covers GENBUG-03

*No test framework install needed — validation is notebook-native.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Seed range non-overlap | GENBUG-03 | Arithmetic verification, not runtime assertion | Print `base + k` range for each (size_idx, rep_idx) combo; verify no overlap visually |
| KDE overlay visual check | D-03 | Visual comparison cannot be automated | Inspect KDE plot: all 4 model distributions should roughly overlap real data |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
