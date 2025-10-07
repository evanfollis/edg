# Ironvest — Core Architecture (v1.1)

## Purpose
A production-grade, auditable implementation of EDG/AoA for multi-agent investing:
- Agents are **lenses (Π)** + AoA primitives.
- Interfaces are **transports (Uₑ)** with R/S factorization.
- Knowledge space **𝒦/v0** is the shared metric space.
- Governance is enforced by **Gold Loops** and the **Constitution**.

## High-Level Diagram

Agents (Quant, PM, Risk, Fundamental, Modeling, News/Policy)
  ↓↑ via transports Uₑ
[Transport Registry] ——> [Holonomy Engine] ——> [Loop Registry]
          │                      │                    │
          └──logs + DSU──> [Ledger/Audit] <──DSU──┘
                               │
                         [Lens-Flow Optimizer]
                               │
                         [Residual Service]  — returns Tᵢⱼ + (Rᵢⱼ,Sᵢⱼ)
                               │
                           [Dashboards]

## Services

1) **transport-registry**
   - Owns Uₑ artifacts: fit params, inverses, R/S factors, diagnostics.
   - Validates numeric caps (κ, τ, ρ) and unit maps.

2) **holonomy-engine**
   - Composes Uₑ along loops; trust-region segmentation; log(Hγ); curvature/torsion/closure.
   - Emits `loop.run.completed` **with regime_tag** for regime-aware scoring.

3) **loop-registry**
   - Stores loop definitions (including Gold Loops) and sampling policies.
   - Enforces Sev-1 gates for Gold loops.

4) **residual-service**  (**updated**)
   - Fits best translator Tᵢⱼ for agent evidence and **factorizes it into (Rᵢⱼ,Sᵢⱼ)**.
   - Returns residuals and diagnostics to Risk/PM and holonomy-engine for attribution.

5) **lens-flow**  (**updated**)
   - Optimizes Πᵢ (and optionally Uₑ) to reduce loop loss under budgets.
   - **Reports pre/post ‖ω^Π‖** (spurious curvature) and supports **regime_scope** (train/validate by regime).
   - Enforces nonlinear content parsimony or requires OOS torsion proof.

6) **dsu-signer**
   - Content-addressed signing/verification; quorum enforcement; key management.

7) **dashboard-api**
   - Aggregates metrics: loop health, curvature/torsion heatmaps, residuals, EG/AG KPIs, **regime filters**.

## Storage
- **vector/**: 𝒦/v0 embeddings (pgvector/FAISS).
- **sql/**: Postgres/DuckDB for metadata, runs, KPIs, incidents.
- **ledger/**: content-addressed blobs + DSU signatures.

## Event Bus
Topics (NATS/Redis/Kafka):
- `u-edge.updated`, `loop.run.requested`, **`loop.run.completed` (includes regime_tag)**,
- `lensflow.step.completed`, `goldloop.breach`,
- `constitution.amendment.proposed|approved|reverted`.

## Security & Governance
- DSU with HSM-backed keys and 3-of-4 quorum for Tier-1/2 changes.
- Emergency Break-Glass: 2-of-2 (HeadOfRisk, ModelRisk) revert.

## Observability
- OpenTelemetry tracing across services (propagate loop_id, regime_tag, edge_ids).
- Prometheus metrics (see OBSERVABILITY.md).
- Structured logs include DSU IDs, dataset hashes, κ/τ/ρ, regime_tag.
