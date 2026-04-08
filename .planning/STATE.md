---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Generation Pipeline & Experimental Rigor
status: Ready to plan
stopped_at: Phase 3 context gathered — phase invalidated and removed
last_updated: "2026-04-08T16:18:27.704Z"
progress:
  total_phases: 3
  completed_phases: 2
  total_plans: 4
  completed_plans: 4
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-30)

**Core value:** Demonstrate quantum circuit ansatze can generate faithful synthetic bioprocess data with rigorous methodology
**Current focus:** Phase 03 — LSTM Evaluation Fixes (old Phase 3 "Data Leakage Fix" removed)

## Current Position

Phase: 3
Plan: Not started

## Performance Metrics

**Velocity:**

- Total plans completed: 2
- Average duration: —
- Total execution time: —

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Preprocessing | 2 | — | — |

**Recent Trend:**

- Last 5 plans: —
- Trend: —

| Phase 02-generation-bug-fixes P01 | 2 | 2 tasks | 1 files |
| Phase 02-generation-bug-fixes P02 | 10 | 1 tasks | 1 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- v1.0 Phase 1 complete: Lambert-W removed, growth_rate naming, PAR ablation variants
- v1.1: Deep code review (sci_review.md) uncovered 8 critical + 17 major + 15 minor issues
- v1.1: Generation bugs (noise mismatch, *0.1 scaling) must be fixed before any metrics work
- v1.1: Quantum distribution principle — circuits define their own distributions, no classical overlays
- v1.1: Scrap unstarted v1.0 phases, redefine roadmap around code review findings
- v1.1: DINT-01 (leakage fix) kept in separate phase from code fixes — requires expensive retraining
- [Phase 02-generation-bug-fixes]: GENBUG-01/02/03 fixes applied to all 3 qGAN variants; torch.randn noise, row-major indexing, no 0.1 scaling, non-overlapping seed scheme
- [Phase 02-generation-bug-fixes]: Smoke test cell added after generation loop using MODELS_INFO dict; SMOKE_N=10 for fast validation; warns on variance and sign bias (not asserts)
- [Phase 02-generation-bug-fixes]: GENBUG-04: per-curve windowing applied to all 3 LSTM loops — no window ever spans two synthetic curves or the real/synthetic boundary

### Pending Todos

None yet.

### Blockers/Concerns

- Quantum circuit generation is slow — N>=10 seeds x 4 models x 3 sizes = significant compute
- Retraining all 4 models on train-split only (Phase 3) requires significant quantum circuit compute
- qGAN bugs (C1, C2) mean all existing qGAN checkpoints/results are invalid — must regenerate

## Session Continuity

Last session: 2026-04-08T16:18:27.700Z
Stopped at: Phase 3 context gathered — phase invalidated and removed
Resume file: .planning/phases/03-data-leakage-fix/03-CONTEXT.md
