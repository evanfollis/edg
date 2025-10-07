# Governance & DSU (v1.0)

- All artifacts (Uₑ, Πᵢ, loops, gold loops, constitution) are content-addressed (sha256) and signed via DSU.
- **Tier-1** (K-space/metric/gold loops): requires 3-of-4 quorum; shadow+canary; bridge φ with distortion bound; full rollback plan.
- **Tier-2** (Uₑ, budgets, projector modes): 3-of-4; canary; numeric tests must pass (κ,τ,ρ).
- **Tier-3** (Πᵢ, translators Tᵢⱼ): agent owner + Risk sign-off.

**Emergency Revert (Sev-1):** HeadOfRisk + ModelRiskOfficer can revert in ≤30m; auto incident creation.

**Decision Dossier** required for any change: hypothesis, expected loop/KPI effect, tests, OOS windows, DSU IDs, data hashes, code digests.
