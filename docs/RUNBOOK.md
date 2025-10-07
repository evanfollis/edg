# Runbook (Ops) — v1.1

## Sev-1 (Gold loop breach)
1) Alert (MTTD ≤ 5m). Incident page: HeadOfRisk, ModelRiskOfficer.
2) Auto-revert to last signed state via DSU; freeze K-space and transports.
3) Root-cause checklist:
   - Data vendor anomalies? Unit maps changed?
   - Edge κ/τ/ρ regressions?
   - New code digests deployed without signatures?
   - **Regime shift?** Verify regime_tag on recent `loop.run.completed` events; compare within-regime.
4) Thaw after 5 consecutive **within-regime** greens; record Decision Dossier.

## Sev-2 (Budget/infra amendments)
- Change request with Decision Dossier (include regime_scope and OOS windows).
- Canary ≤10% flows, 2-day window. Must pass:
  - OOS loop loss decrease **within the same regime(s)**,
  - No gold-loop degradation,
  - Non-degrading business KPIs (IR, hit-rate, TE).

## Common Tasks
- Register Uₑ: POST /edges (transport-registry), then DSU /sign.
- Run loop: POST /run (holonomy-engine) — event includes `regime_tag`.
- Residuals: POST /residuals — capture T_ij + (R_ij,S_ij) and diagnostics.
- Lens-Flow step: POST /step with `regime_scope`; sign Πᵢ after improvement and report **ω^Π pre/post**.
