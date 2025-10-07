# Ironvest — Core Architecture (v1.0)

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
                         [Residual Service]
                               │
                           [Dashboards]

## Services (microservices or modules)

1) **transport-registry**
   - Owns Uₑ artifacts: fit params, inverses, factorization (R/S), diagnostics.
   - Validates numeric caps (κ, τ, ρ) and unit maps.
   - REST + event emission on changes.

2) **holonomy-engine**
   - Composes Uₑ along loops; checks trust regions; computes log(Hγ), curvature/torsion/closure.
   - Returns edge attribution (sensitivity/Shapley approximation).

3) **loop-registry**
   - Stores loop definitions (including Gold Loops) and sampling policies.
   - Enforces Sev-1 gates for Gold loops.

4) **residual-service**
   - Fits best translations Tᵢⱼ for agent evidence residuals rᵢⱼ.
   - Provides residuals to Risk/PM and to holonomy-engine for attribution.

5) **lens-flow**
   - Optimizes Πᵢ (and optionally Uₑ) to reduce loop loss under budgets and parsimony rules.
   - Nonlinear content parsimony penalties & stable/predictive torsion waivers.

6) **dsu-signer**
   - Content-addressed signing/verification for all artifacts and constitution changes.
   - M-of-N quorum enforcement and key management.

7) **dashboard-api**
   - Aggregates metrics: loop health, curvature/torsion heatmaps, budget flags, EG/AG KPIs.

## Storage

- **vector/**: 𝒦/v0 embeddings (pgvector/FAISS).
- **sql/**: Postgres/DuckDB for metadata, runs, KPIs, incidents.
- **ledger/**: content-addressed blobs (e.g., object store) + DSU signatures.

## Event Bus
- Simple topics (NATS/Redis/Kafka):
  - `u-edge.updated`, `loop.run.requested`, `loop.run.completed`,
  - `lensflow.step.completed`, `goldloop.breach`, `constitution.amendment.proposed|approved|reverted`.

## Security & Governance
- DSU with HSM-backed keys and 3-of-4 quorum for Tier-1/2 changes.
- Emergency Break-Glass: 2-of-2 (HeadOfRisk, ModelRisk) revert.

## Observability
- OpenTelemetry tracing on all inter-service requests (trace Uₑ IDs through loops).
- Metrics: Prometheus counters/gauges (see `OBSERVABILITY.md`).
- Structured logs including DSU artifact IDs, dataset hashes, κ/τ/ρ.

