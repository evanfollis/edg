# 𝒦/v0 Metric & Compatibility Spec
version: 1.0
status: locked
owner: architecture@ironvest
last_updated: 2025-10-07

## Purpose
Define the canonical embedding space 𝒦/v0, its inner product (metric g), admissible
transport factorizations (R/S split), numerical trust regions, and reporting rules so
all agents and edges interoperate safely, reproducibly, and auditably.

---

## 1) Embedding Space (𝒦/v0)
- **Space:** ℝ^d
- **Dimensionality (d):** 768 (default; projects may override but must declare)
- **Coordinate System:** fixed ordering documented in `specs/K_v0_features.md`
- **Normalization:** features z-scored over a rolling 2y training window (configurable,
  persist window hash and seeds in artifacts)
- **K-space ID:** `"K/v0"` (must be declared by all edges/agents using this spec)

---

## 2) Metric g
- **Default (MVP):** Euclidean metric (identity)  
  \( g(x,y) = x^\top y \), matrix form \(G = I\).
- **Tier-1 Planned Option:** Fisher–Rao / dually-flat metric (non-Euclidean).  
  Any change of g is a **Tier-1 constitutional change** and must:
  - publish a **g-aware factorization** procedure (see §4.4),
  - provide a versioned **bridge** \( \phi: \mathcal K\_{v0}\to \mathcal K\_{v1} \) with
    a measured distortion bound (see §9),
  - publish the **Cartan split** alignment (see §4.5).

**Compatibility Claim:** An edge is 𝒦/v0-compatible iff:
- it declares `k_space_id: "K/v0"`, and
- its transport \(U\) approximately preserves the inner product:
  \( \|U^\top U - I\|\_F \le \tau \) on validation, with default \( \tau = 0.02 \).

---

## 3) Transport Maps \(U_e\)
- **Shape:** \(U \in \mathbb R^{m\times n}\) (square or rectangular)
- **Fitting:** least-squares / ridge on rolling window (declare window, regularization)
- **Numerical Caps:**
  - Condition number \( \kappa(U) \le 500 \) (else apply Tikhonov regularization)
  - Round-trip distortion (validation): \( \le \tau \) (default 0.02)
- **Edge Types:** `edge_type: linear | nonlinear` (see §7)

---

## 4) Admissible Factorizations (R/S split)
Goal: separate **Reframing** \(R\) from **Content Shift** \(S\) consistently.

### 4.1 Square, well-conditioned (κ ≤ 500) under Euclidean g
- **Method:** Matrix polar decomposition (Higham)  
  \( U = Q S \) with \( Q \) orthogonal (R), \( S \) symmetric PSD (S).

### 4.2 Rectangular (m ≠ n)
- **Method:** Orthogonal Procrustes on subspace + PSD content
  1. Thin SVD: \( U = \tilde U \Sigma V^\top \)
  2. \( R := \tilde U V^\top \) (isometry on appropriate subspace)
  3. \( S := V \Sigma V^\top \) (declare convention)
- **Residual bound:** Procrustes residual \( \le \rho \) (default 0.01).

### 4.3 Ill-conditioned
- **Method:** Tikhonov-regularized Procrustes  
  Minimize \( \|UA - B\|^2 + \alpha\|A\|^2 \) with α tuned to achieve κ ≤ 500.  
  Log α and achieved κ.

### 4.4 g-aware (metric-compatible) factorization (non-Euclidean g)
When \( G \neq I \), use **g-polar**:
- \( R \in O(G): R^\top G R = G \) (reframing)
- \( S \) is **g-symmetric** PSD: \( G^{-1} S^\top G = S, \; S \succ 0 \) (content)

**Construction by congruence:**
1) Choose \( C \) with \( C^\top C = G \) (e.g., Cholesky).  
2) \( \tilde U = C U C^{-1} \), take standard polar \( \tilde U = Q \tilde S \).  
3) Map back: \( R = C^{-1} Q C \), \( S = C^{-1}\tilde S C \).  
Publish \(G, C\) and diagnostics.

### 4.5 Cartan split alignment
For Tier-1 metric changes, publish the **Cartan split** \( \mathfrak g = \mathfrak h \oplus \mathfrak m \)
used to interpret \(R\) as \( \mathfrak h \) (reframing) and \(S\) as \( \mathfrak m \) (content).
Document (or reference) reductivity and compatibility with \(G\).

> **Declaration:** Every edge must report: factorization method, achieved residuals,
> condition number, round-trip score, and signatures (see §10).

---

## 5) Holonomy, Logs & Trust Regions
- **Loop holonomy:** \( H_\gamma = \prod\_{e\in\gamma} U_e \) (ordered product).
- **Matrix log allowed iff trust-region holds:**  
  \( \|H_\gamma - I\|\_2 \le \delta \) (default \( \delta = 0.1 \)); otherwise segment γ.
- **Segmentation:** split γ into subloops satisfying the trust-region, log per segment.
- **Branch continuity:** choose log branch minimizing incremental change vs previous period (see CI checks).

---

## 6) Units & Unit Maps
- Every edge publishes a **unit_map** for inputs/outputs (e.g., z-scores, bps).
- **Gold loops** (gauge-fixers) are evaluated in **native units**; normalization only after audit.

---

## 7) Linear vs Nonlinear Edge Governance
- `edge_type: linear` → penalize **spurious curvature** \( \omega^\Pi \) (R-side) in Lens-Flow objective.
- `edge_type: nonlinear` → enforce **content parsimony** on S (cannot hide complexity in black boxes):
  \[
  J\_{\text{nonlin}} = \alpha\_S \,\|S\_e\|\_F \;+\; \alpha\_{\text{cond}} \,\max(0, \operatorname{cond}(S\_e) - \kappa\_S)
  \]
  with defaults \( \alpha\_S=1.0,\; \alpha\_{\text{cond}}=0.1,\; \kappa\_S=100 \).

**Stable, predictive torsion waiver (nonlinear edges only):**  
Parsimony penalties may be waived for segments where all hold:
- **Stability:** torsion magnitude ranks in top \(q\%\) across ≥ \(K\) rolling windows,
- **Predictiveness:** forward OOS improves target KPIs (e.g., IR, hit-rate) by ≥ \(\Delta\_{\min}\),
- **Safety:** no degradation on gold loops.  
Defaults: \( q=20, K=6, \Delta\_{\min}\ge 0 \). Proof artifact must be attached.

---

## 8) Reductive Split Declaration
This spec assumes a reductive split \( \mathfrak g = \mathfrak h \oplus \mathfrak m \) aligned with R/S.
Edges must confirm compatibility or provide a bridge routine.

---

## 9) K-space Bridges (Tier-1 changes)
Any change to \(G\) or 𝒦 version requires a **bridge** \( \phi \) with:
- empirical distortion histogram and bound \( d(\phi) \le \tau \),
- shadow/canary deployment for at least one full rebalance cycle,
- frozen legacy inference endpoints for reproducibility (retention window declared).

---

## 10) Reporting & Signatures (DSU)
Every \(U_e\) fit must log:
- dataset hashes, time windows, seeds,
- \( \kappa(U) \), round-trip score (τ), factorization residuals (ρ),
- factorization method and edge_type,
- nonlinear penalty config or waiver proof (if applicable),
- code digests, dependency locks,
- DSU signatures of owners (see governance handbook).

---

## 11) Defaults (mirroring Constitution)
- \( \kappa \le 500 \), \( \tau \le 0.02 \), \( \rho \le 0.01 \), \( \delta \le 0.1 \)
- Nonlinear parsimony: \( \alpha\_S=1.0,\; \alpha\_{\text{cond}}=0.1,\; \kappa\_S=100 \)
