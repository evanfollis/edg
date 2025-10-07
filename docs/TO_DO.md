# Ironvest v1.1 — Engineering TODO (PR-1..PR-6)
Purpose: smallest decisive PRs to make the platform end-to-end executable with audit-safe numerics.  
Each PR includes scope, owner(s), acceptance tests, and links to specs.

---

## PR-1 — Lock JSON Schemas (BLOCKER)
**Scope**
- Finalize / validate:
  - `contracts/schemas/transport_edge.schema.json`
  - `contracts/schemas/loop.schema.json`
  - `contracts/schemas/holonomy_result.schema.json`
  - `contracts/schemas/nonlinear_waiver.schema.json`

**Owners**: @architecture (schema), @model-risk (review)

**Acceptance**
- All service request/response bodies validate against schemas.
- CI runs schema validation on fixtures with zero monkeypatching.
- Any incompatible change fails CI with `IV.SCHEMA.VALIDATION`.

**References**: `specs/K_v0_metric_spec.md` §4, `services/*/openapi.yaml`, `ci/tests/test_edges_and_loops.py`.

---

## PR-2 — Shared numerics lib (`edg-numerics`)
**Scope**
- Implement reference functions:
  - `trust_region(H, delta_max)` (‖H−I‖₂ check)
  - `segment_loop(edge_list, delta_max)` (greedy segmentation)
  - `stable_logm(H)` with branch continuity helper
  - Factorizations: `polar(U)`, `procrustes(U)`, `tikhonov_procrustes(U, alpha)`, `g_polar(U, G)`
  - `roundtrip(U, U_inv)`; `rotation_proxy(logH)`
- Package as pip-installable module; used by holonomy-engine & residual-service.

**Owners**: @quant-lead, @risk-lead (numerics), @architecture (API)

**Acceptance**
- CI passes numerics tests at default tolerances (κ≤500, τ≤0.02, ρ≤0.01, δ≤0.10).
- Deterministic results with fixed seeds; logs include dataset hashes.

**References**: `ci/tests/test_edges_and_loops.py`, `specs/K_v0_metric_spec.md` §4–5.

---

## PR-3 — Holonomy Engine v0
**Scope**
- Compose \(H_\gamma = \prod U_e\) using registry artifacts; segment by δ.
- Compute and return:
  - `curvature_fro`, `torsion_fro`, `closure_norm`
  - simple `edge_attribution` (sensitivity heuristic)
- Emit `loop.run.completed` **with `regime_tag`**.

**Owners**: @risk-lead, @pm-lead (review)

**Acceptance**
- `scripts/seed_repo.py` prints non-trivial holonomy JSON.
- `gamma_Quant_PM_identity` loop passes bounds on fixtures.
- Gold-loop battery runs green on canned data.

**References**: `services/holonomy-engine/openapi.yaml`, `loop-registry/gold_loops.yaml`.

---

## PR-4 — Residual Service v0 (T_ij with R/S)
**Scope**
- Fit best translator \(T_{ij}\) and factorize → `(Rij, Sij)`.
- Persist `translator_Tij` artifacts; record κ/ρ/roundtrip; DSU-sign.
- Return `r_norm`, `translator_ref`, `Rij_ref`, `Sij_ref`, diagnostics.

**Owners**: @quant-lead, @fundamental-lead (review)

**Acceptance**
- `/residuals` returns valid artifacts on fixtures; diagnostics meet CI bounds.
- Unit maps honored; regime_tag threaded through responses/logs.

**References**: `services/residual-service/openapi.yaml`, `contracts/schemas/translator_Tij.schema.json`.

---

## PR-5 — Wilson diagnostics & G-checks (hooks)
**Scope**
- Add fields to holonomy result: `wilson_trace`, (optional) `wilson_spectrum`.
- When non-Euclidean G is declared, verify `Rᵀ G R = G`; emit `g_invariance_error` metric.
- Feature-flag heavy computations (off by default).

**Owners**: @risk-lead, @architecture

**Acceptance**
- New fields appear in responses/metrics; flags controllable via env.
- CI includes a basic g-compatibility check when G≠I is configured.

**References**: `specs/K_v0_metric_spec.md` §4.4–4.5, `docs/OBSERVABILITY.md`.

---

## PR-6 — Lens-Flow stub optimizer (ω^Π accounting, regime scope)
**Scope**
- Single projected-gradient step that:
  - reduces loop loss on a diagnostic set,
  - respects step caps,
  - penalizes \(\|\omega^Π\|\) (report **pre/post**),
  - trains/validates on provided `regime_scope`.

**Owners**: @quant-lead, @risk-lead (governance), @pm-lead (review)

**Acceptance**
- `/step` returns `accepted` with `loop_loss_delta < 0`
- `omegaPi_norm_post ≤ omegaPi_norm_pre`
- Emits `lensflow.step.completed` with regime_scope

**References**: `services/lens-flow/openapi.yaml`, `constitution/CONSTITUTION.yaml` (`pi_governance`).

---

## Guardrails (unchanged)
- Gold loops = Sev-1 gates (auto-revert, freeze Tier-1/2, thaw after 5 greens).
- DSU signatures required per tier in `GOVERNANCE.md`.
- Observability tags: include `loop_id`, `regime_tag`, `edge_id`, `dsu_ids` across logs/metrics/traces.

