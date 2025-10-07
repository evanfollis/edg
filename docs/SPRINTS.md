# Sprints (6 × 1-week sprints; deliverables each Friday)

## Sprint 1 — Bootstrap & Gold Loops Plumbed
- Scaffold repo + services stubs (transport-registry, holonomy-engine, loop-registry).
- Implement K/v0 metric spec, schemas, CI numerics (κ, τ, ρ, δ, θ, rel_log).
- Load `gold_loops.yaml`; run daily gold loop battery on canned data.
- **Exit:** gold loop results show on dashboard-api; Sev-1 revert wired (simulated).

## Sprint 2 — Transports & Edge Governance
- Implement /edges: register Uₑ with factorization (polar/procrustes).
- Compute diagnostics; enforce κ≤500, τ≤0.02, ρ≤0.01 in CI.
- Event bus emits `u-edge.updated`; holonomy-engine consumes & caches.
- **Exit:** Quant↔PM identity loop green on sample; edge attribution visible.

## Sprint 3 — Holonomy & Residuals End-to-End
- holonomy-engine: trust-region segmentation, log(Hγ), curvature/torsion/closure.
- residual-service: Tᵢⱼ fit, rᵢⱼ API; feed to dashboards & Risk.
- **Exit:** 2–3 non-gold loops live; risk gate can block a PM “proposal” when red.

## Sprint 4 — Lens-Flow & Nonlinear Governance
- lens-flow: optimize Πᵢ under step caps; nonlinear parsimony penalty & waiver path.
- DSU signer integrated with tiers; content-addressed ledger for runs.
- **Exit:** Demonstrate ↓ loop loss OOS without gold loop regressions; DSU-signed changes.

## Sprint 5 — K-Space & Canary Deployment
- Implement shadow + canary runners; control charts for EG vs AG KPIs.
- Bridge contract stub for future K-space migration; distortion report.
- **Exit:** Canary path promotes only when loop loss ↓ and KPIs ⩾ baseline.

## Sprint 6 — Ops Hardening & Runbooks
- Full RUNBOOK drills: Sev-1 revert, Sev-2 amendment, incident templates.
- Observability: tracing & metrics; alerting thresholds tuned.
- **Exit:** Go/No-Go checklist met; engineering handoff to Ops.
