# Sprints (6 × 1-week) — v1.1

## Sprint 1 — Bootstrap & Gold Loops Plumbed
- Registry stubs (transport, holonomy, loop).
- K/v0 spec, schemas, CI numerics (κ, τ, ρ, δ, θ, rel_log).
- Load `gold_loops.yaml`; run daily battery on fixtures.
- **Exit:** dashboard shows gold loop metrics; Sev-1 revert wired (sim).

## Sprint 2 — Transports & Edge Governance
- /edges implemented; factorization (polar/procrustes/tikhonov).
- Diagnostics enforced in CI.
- Events: `u-edge.updated`.
- **Exit:** Quant↔PM identity loop green; attribution visible.

## Sprint 3 — Holonomy & Residuals End-to-End
- holonomy-engine: trust-region segmentation; log(Hγ); **emit regime_tag**.
- residual-service: returns r_norm + **T_ij with (R_ij,S_ij)** and diagnostics.
- **Exit:** 2–3 non-gold loops live; risk gate can block PM proposal.

## Sprint 4 — Lens-Flow & Π Governance
- lens-flow: Πᵢ optimization with **omegaPi penalty & reporting**.
- Regime-scoped train/validate; DSU integration.
- **Exit:** ↓ loop loss **within regime** OOS; ω^Π down; no gold regressions.

## Sprint 5 — Canary & KPI Controls
- Shadow/canary runners; EG vs AG KPIs with regime filters.
- Bridge contract stub for future K migration.
- **Exit:** Promote only when loop loss ↓ and KPIs ⩾ baseline **per regime**.

## Sprint 6 — Ops Hardening
- RUNBOOK drills (Sev-1/2), incident templates.
- Observability: traces + metrics; alert thresholds tuned.
- **Exit:** Go/No-Go checklist met; Ops handoff.
