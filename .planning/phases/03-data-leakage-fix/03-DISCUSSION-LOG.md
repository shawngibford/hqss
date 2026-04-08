# Phase 3: Data Leakage Fix - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-08
**Phase:** 03-data-leakage-fix
**Areas discussed:** Split placement, Retraining budget, Checkpoint strategy, Constants verification
**Outcome:** Phase invalidated and removed from roadmap

---

## Split Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Split raw OD first | Split raw OD at 80% before computing growth_rate, compute constants from train only | |
| Split after growth rate | Compute growth_rate from full OD, split array at 80%, compute constants from train portion | |
| Split at window level | Compute from full data, only build DataLoader windows from first 80% | |
| Other (user input) | No split needed — generators should learn full distribution | ✓ |

**User's choice:** No split at all. Generators learn the full historical dataset distribution. Synthetic data augments the LSTM training. Only the LSTM has a train/test split.
**Notes:** User clarified that this is a data augmentation experiment for soft sensor improvement, not a generative model benchmark. The "leakage" concern from sci_review.md does not apply.

---

## LSTM Split Confirmation

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, current LSTM split is fine | Generators see all data, LSTM 80/20 temporal split for soft sensor evaluation | ✓ |
| Different split needed | LSTM evaluation split should work differently | |
| No split at all | LSTM trains and evaluates on full series | |

**User's choice:** Current LSTM 80/20 temporal split is correct.

---

## Phase 3 Disposition

| Option | Description | Selected |
|--------|-------------|----------|
| Remove Phase 3 entirely | DINT-01 invalid, remove phase, add justification cell | ✓ |
| Repurpose Phase 3 | Keep slot, redefine scope | |
| Keep Phase 3 as-is | Retrain on train-split anyway | |

**User's choice:** Remove Phase 3 entirely.

---

## Justification Cell Timing

| Option | Description | Selected |
|--------|-------------|----------|
| Add to Phase 4 scope | Bundle with LSTM evaluation fixes | |
| Quick task now | Add markdown cell immediately | ✓ |

**User's choice:** Add justification cell now as a quick task.

---

## Remaining Areas (Moot)

- **Retraining budget** — Moot. No retraining needed.
- **Checkpoint strategy** — Moot. Current checkpoints are valid.
- **Constants verification** — Moot. Full-dataset constants are correct.

## Claude's Discretion

None — all decisions made by user.

## Deferred Ideas

None.
