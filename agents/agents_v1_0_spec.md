# Agents v1.0 Spec

Purpose: define the initial lenses (Πᵢ), their AoA flows, inputs/outputs, and DSU artifacts.
All agents must emit DSU-signed artifacts for their lens configs.

## Common conventions
- k_space_id: "K/v0"
- Evidence units: declared in unit_map per edge; agents must consume/produce according to contracts.
- Regime awareness: agents must pass through current `regime_tag` on all compute calls.

---

## Quantitative Agent
- Lens Π_quant: Factor/NLP encoder over market + fundamentals.
- Inputs: pricing time series, fundamentals, macro, news embeddings.
- Output (to 𝒦/v0): 768-d vector (see `specs/K_v0_features.md`).
- Regularization: ridge α ∈ [1e-4, 1e-1] (DSU-logged).
- AoA word: **P → V → R**
  - P: ingest/encode features.
  - V: update Π params under lens-flow step caps.
  - R: report residuals vs translators Tᵢⱼ; publish ω^Π pre/post when updating Π.
- DSU artifact: `agents/lens_quant.yaml`

## PM Agent
- Lens Π_pm: Utility/loss spec for portfolio optimization.
- Objective: maximize ex-ante IR subject to TE ≤ TE_max, turnover ≤ τ_max, constraints set C.
- Outputs: proposed weights vector; unit_map out: "weights".
- Gate: **Gold loops must be green** for Act (A).
- AoA word: **L → A** (gated by Risk agent and gold loops).
- DSU artifact: `agents/lens_pm.yaml`

## Risk Agent
- Lens Π_risk: constraint parameters + budgets enforcement.
- Budgets: ε (calibration), η (holonomy), per `constitution/CONSTITUTION.yaml`.
- Duties: trigger C → R when residuals or loops breach; maintain Sev-1/2 runbook flows.
- AoA word: **C → R**
- DSU artifact: parameters live in the Constitution; no separate lens file in v1.0.

## Fundamental Agent (optional in v1.0)
- Lens Π_fund: DCF/LBO assumptions → embeddings.
- AoA word: **P → V**
- DSU artifact: `agents/lens_fund.yaml` (optional placeholder in v1.0)

## Policy/News Agent (optional in v1.0)
- Lens Π_news: sentiment/topic models feeding `news_embeddings` features.
- AoA word: **P**
- DSU artifact: `agents/lens_news.yaml` (optional placeholder)

---
## Contracts per agent
- Must attach DSU signatures and code digests.
- Must log regime_scope used for training/validation of any Π update.
- Must provide `omegaPi_norm_pre` and `omegaPi_norm_post` on Π updates (Tier-3).
