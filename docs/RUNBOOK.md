# Runbook (Ops)

## Sev-1 (Gold loop breach)
1) Alert triggers (MTTD ≤ 5m). Incident page: HeadOfRisk, ModelRiskOfficer.
2) Auto-revert to last signed state via DSU; freeze K-space and transports.
3) Root-cause checklist:
   - Data vendor anomalies? Unit maps changed?
   - Edge κ/τ/ρ regressions?
   - New code digests deployed without signatures?
4) Thaw after 5 consecutive greens; record Decision Dossier.

## Sev-2 (Budget/infra amendments)
- Open change request with Decision Dossier.
- Canary ≤10% flows, 2-day window. Must pass:
  - OOS loop loss decrease,
  - No gold-loop degradation,
  - Non-degrading business KPIs (IR, hit-rate, TE).

## Common Tasks
- Register Uₑ: POST /edges (transport-registry), then DSU /sign (tier from constitution).
- Run loop: POST /run (holonomy-engine), then publish to ledger and dashboards.
- Lens-Flow step: POST /step with constraints; sign Πᵢ after improvement.
