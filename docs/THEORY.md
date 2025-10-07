# Epistemic Differential Geometry & The Alphabet of Agency

## An Integrated, Exhaustive Academic Treatment (vFinal)

**Author:** [Your Name]

**Keywords:** Epistemic differential geometry, principal bundles, Cartan connection, curvature, torsion, Wilson loops, information geometry, multi-agent systems, agency grammar, constitutions of learning, residual flow, gauge theory.

---

## Abstract

We present a unified, rigorous framework for knowledge representation and intelligent coordination that merges **Epistemic Differential Geometry (EDG)** with the **Alphabet of Agency (AoA)**. EDG models beliefs as points on a manifold (\mathcal K) equipped with a principal (H)-bundle of interpretive frames and a Cartan connection (A=\omega\oplus\theta) over a model space ((G/H)). Curvature ((\Omega)) encodes path-dependent reframing (content preserved, basis changed) and torsion ((T)) encodes order-sensitive content creation/translation. AoA decomposes intelligent behavior into a free-monoid grammar of primitives (Perceive, Reflect, Plan, Revise, Critique, Act) that operate as update/transport operators on (\mathcal K). We formalize **constitutions of learning**—calibration budgets, compression–complexity trade-offs, and holonomy bounds—then integrate EDG and AoA into a coherent theory of multi-agent coordination via residual signals. We provide a discrete/computable instantiation on graphs/simplicial complexes, including edge-level factorization (U_e\approx R_e S_e), a loop-based reconstruction objective for deconvolving terrain (A^\star) and instrument (\Pi), Wilson-loop diagnostics, and a **lens-flow** (calibration RG) that reduces spurious holonomy while preserving stable curvature modes. The result is a complete theoretical and practical foundation for structured pluralism: many agents, many lenses, coherently integrated without erasing difference.

---

## 1. Introduction

Modern knowledge ecosystems—scientific, social, machine—are densely populated by models and perspectives that frequently disagree. Rather than attributing disagreement to irrationality or error, we hypothesize:

> **Disagreement is geometry, not villainy.**

When perspectives differ, they often occupy distinct coordinates on a shared manifold of meaning. If we can model the manifold, the lenses that project the world into evidence, and the legal transformations between lenses, we can measure and utilize disagreement as **structure**. In parallel, intelligent behavior is not monolithic optimization but **composition**: agents build complex behaviors by sequencing reusable primitives. This motivates two pillars:

1. **Epistemic Differential Geometry (EDG):** A geometric theory of knowledge with principal bundles of frames, Cartan data ((\omega,\theta)), and gauge-invariant loop observables.

2. **Alphabet of Agency (AoA):** A compositional grammar of intelligent behavior (Perceive, Reflect, Plan, Revise, Critique, Act) with formal operator semantics.

Together with a constitutional layer that constrains admissible epistemic dynamics, EDG+AoA yields a theory of **coherent pluralism**: a landscape where many agents and many truths can interact productively.

**Contributions.** This paper consolidates and extends prior drafts with:

* A full principal-(H) bundle formalization and Cartan connection over ((G/H)),
* Terrain–instrument split (A=A^\star+\Pi) and the inverse holonomy problem,
* Wilson loops as reframing signatures, and torsion as productive content shift,
* Information/Finsler metrics with geodesic vs. autoparallel bias analysis,
* A discrete EDG pipeline (graph/simplicial) with (U_e\approx R_e S_e) factorization,
* A loop-based reconstruction objective and a lens-flow (calibration RG),
* Operational regime taxonomy, tests for (T) vs. (\Omega), evaluation protocols, and detailed examples.

---

## 2. Preliminaries and Notation

* **Groups & Lie algebras:** (G) group of representational symmetries; (H\subset G) stabilizer; (\mathfrak g,\mathfrak h,\mathfrak m) corresponding Lie algebras with (\mathfrak g=\mathfrak h\oplus \mathfrak m).
* **Model space:** homogeneous space ((G/H))—idealized “flat” inference/semantics template.
* **Knowledge manifold:** smooth manifold (\mathcal K) of epistemic states (beliefs, models, distributions). Tangent spaces (T_x\mathcal K) encode admissible micro-updates.
* **Principal bundle:** (\pi:P\to\mathcal K) principal (H)-bundle of **frames of understanding** (interpretive choices).
* **Lens:** a (local) section (s:U\subset\mathcal K\to P) choosing a frame over (U).
* **Cartan connection:** (A\in\Omega^1(P,\mathfrak g)), split as (A=\omega\oplus\theta) with (\omega\in\Omega^1(P,\mathfrak h)), (\theta\in\Omega^1(P,\mathfrak m)).
* **Structure equations:** (T=d\theta+\omega\wedge\theta), (\Omega=d\omega+\omega\wedge\omega).
* **Parallel transport & holonomy:** (\mathcal P\exp\int \cdot) along curves in (\mathcal K); gauge-invariant traces on loops (Wilson loops).
* **AoA alphabet:** (A={\mathbf P,\mathbf R,\mathbf L,\mathbf V,\mathbf C,\mathbf A}), free monoid (A^*); operators act on states in (\mathcal K).

---

## 3. Epistemic Differential Geometry (EDG)

### 3.1 Model Space ((G/H)) and Meaning-Preserving Symmetry

The idealized, undistorted semantics of a domain can be represented by a homogeneous model space ((G/H)). Elements of (G) act as reparameterizations (choice of primitives, encodings, notations) leaving meaning invariant; (H) stabilizes a canonical frame. Intuitively, ((G/H)) is the Platonic template of concept relations. EDG is a **Cartan geometry modeled on ((G/H))**, attached to the empirical knowledge manifold (\mathcal K).

### 3.2 Knowledge Manifold ((\mathcal K)) and Principal (H)-Bundle ((P\to\mathcal K))

The manifold (\mathcal K) is the terrain of practiced knowledge. Each point (x\in\mathcal K) is a conceptual state (belief set, model, distribution). The principal (H)-bundle (P\to\mathcal K) collects **frames of understanding** over each (x). A **lens** is (locally) a section (s) picking a frame; overlapping sections model distinct communities with compatible overlaps. The bundle geometry captures how representations transform across the manifold.

### 3.3 Cartan Data: Coframe, Connection, Torsion, Curvature

A Cartan connection (A=\omega\oplus\theta\in\Omega^1(P,\mathfrak g)) splits (\mathfrak g=\mathfrak h\oplus\mathfrak m). Cartan’s structure equations:
[
T := d\theta + \omega\wedge\theta\in\Omega^2(P,\mathfrak m),\qquad
\Omega := d\omega + \omega\wedge\omega\in\Omega^2(P,\mathfrak h).
]
**Epistemic readings.**

* **Coframe (\theta):** how micro-changes in content are encoded in the chosen frame.
* **Connection (\omega):** how the frame/lens itself updates as we move—auto-updates of priors, metaphors, notations.
* **Curvature (\Omega) (reframing inconsistency):** path-dependent change of basis with content conserved; loop transport returns the “same” claim in a different explanatory frame.
* **Torsion (T) (innovative translation):** non-commutation of micro-inferences yields net content creation/loss; productive distortion (analogy, instrument effect).

### 3.4 Gauge Transformations, Holonomy, and Wilson Loops

Changes of frame (g:P\to H) act by (A\mapsto g^{-1}Ag+g^{-1}dg). Information invariant under all admissible gauges reflects **truths** independent of lens choice. Gauge-invariant loop observables include Wilson loops
[
W_\gamma ,=, \mathrm{Tr},\mathcal{P}\exp!\oint_{\gamma} \omega,
]
which measure reframing burden ((\mathfrak h)-part). The full holonomy (\mathcal{P}\exp\oint_{\gamma} A) encodes both reframing and content shift; its (\mathfrak m)-component diagnoses torsion on loops. Families of Wilson loops over diagnostic cycles form **reframing signatures** of communities.

### 3.5 Metrics, Geodesics, and Autoparallels (Method Bias)

Endow (\mathcal K) with an information metric (g) (e.g., Fisher–Rao; or Finsler metric induced by a contrast function). **Geodesics** are shortest explanations (minimal distortion paths). The connection derived from (A) induces **autoparallels** (following methodological transport without ad-hoc corrections). Their deviation quantifies **method-induced bias**. A constitution can bound this gap to keep methodologies consistent with minimal-explanation principles.

### 3.6 Terrain–Instrument Split and the Inverse Problem

Separate “truth terrain” and “lens response”:
[
A = A^\star + \Pi, \qquad A^\star=(\omega^\star\oplus\theta^\star),; \Pi=(\omega^\Pi\oplus\theta^\Pi).
]
Observed tensors conflate both:
[
\begin{aligned}
T_{\text{obs}} &= d(\theta^\star+\theta^\Pi) + (\omega^\star+\omega^\Pi)\wedge(\theta^\star+\theta^\Pi),\
\Omega_{\text{obs}} &= d(\omega^\star+\omega^\Pi) + (\omega^\star+\omega^\Pi)\wedge(\omega^\star+\omega^\Pi).
\end{aligned}
]
**Inverse holonomy problem.** Given loop holonomies and overlaps of lenses (multiple sections on overlaps), recover (A^\star) while learning (\Pi). Regularize (\Pi) (smoothness, sparsity, locality) under constitutional budgets to avoid over-explaining away true curvature/torsion.

---

## 4. The Alphabet of Agency (AoA)

### 4.1 Grammar of Primitives and Free-Monoid Structure

Let (\mathcal A={\mathbf P,\mathbf R,\mathbf L,\mathbf V,\mathbf C,\mathbf A}) be the set of agency primitives: **Perceive, Reflect, Plan, Revise, Critique, Act**. The set of strategies is the free monoid (\mathcal A^*) (finite sequences/“words” over (\mathcal A)); organizations of agents compose “sentences”.

### 4.2 Operator Semantics on (\mathcal K)

Each primitive acts as an operator on epistemic states and evidence:

* **(\mathbf P):** World (\to) Evidence; apply lens (\ell) to collect observations.
* **(\mathbf R):** (State, Evidence) (\to) coherence metric (consistency checks, residuals).
* **(\mathbf L):** State (\to) planned trajectory (\tau) on (\mathcal K).
* **(\mathbf V):** (State, Evidence) (\to) updated State (micro-update along (T_x\mathcal K)).
* **(\mathbf C):** (State, Residual) (\to) diagnosis (attribution across lenses/steps).
* **(\mathbf A):** State (\to) intervention in world (affecting subsequent evidence).

**Residuals drive control.** Inter-agent residuals (r_{ij}) act as coordination signals: small (\Rightarrow) consensus; large (\Rightarrow) trigger (\mathbf C/\mathbf V) to revise plans or lenses.

### 4.3 Category-Theoretic View (optional)

Objects = epistemic states; morphisms = AoA words annotated with transports on (\mathcal K). Functors correspond to lens changes; natural transformations capture critique/revision morphisms. This gives compositional semantics and principled refactoring of workflows.

---

## 5. Constitutions of Learning

A **constitution** is a tuple of budgets and guards that constrain admissible epistemic dynamics, not specific conclusions.

**Definition 5.1 (Calibration Budget).** Residual norms between admissible lenses satisfy (\lVert r_{ij}\rVert \le \epsilon) for a domain-specific (\epsilon>0).

**Definition 5.2 (Compression–Complexity Trade-off).** Models minimize
[
\mathcal J(M) = L(M) + \lambda, D(M),
]
where (L) is description length/complexity, (D) is calibration error, and (\lambda) sets the trade-off.

**Definition 5.3 (Holonomy Bound).** For a reasoning loop (\gamma:[0,1]\to\mathcal K), the loop deviation satisfies (d(\gamma(0),\gamma(1)) \le \eta) unless evidence forces violation; (\eta>0) is domain-set.

**Proposition 5.4 (Consistency under Budgets).** Under bounded curvature and torsion consistent with ((\epsilon,\eta)), there exists a gauge in which autoparallels deviate from geodesics by a controlled amount proportional to (\epsilon) and (\eta). *Sketch:* bound loop errors by holonomy and residual budgets; invoke Grönwall-type estimates on transport.

---

## 6. Integration: Geometry × Agency

**Single agent:** a trajectory (\gamma) on (\mathcal K) induced by a word (w\in\mathcal A^*), with local transports governed by (A).

**Multi-agent society:** a network of trajectories ({\gamma_i}) coupled by residual exchanges (r_{ij}). Coordination is achieved by residual-triggered (\mathbf C/\mathbf V) steps and constitution checks.

**Residual backpropagation:** Assign responsibility for a loop residual to steps in (w) via sensitivity of holonomy to local transports; use this to prioritize critiques and revisions where they most reduce global inconsistency.

**Governance:** Constitutions operate as priors/constraints on (\Pi) (instrument) and on allowable AoA words (e.g., require (\mathbf C) after (\mathbf A) if residual exceeds threshold).

---

## 7. Discrete/Computational EDG

### 7.1 Graph/Simplicial Construction

* **Nodes** (x\in\mathcal K): embeddings/posteriors representing epistemic states.
* **Edges** (e=(x\to y)): admissible inferences/translations with transports (U_e) (affine/Jacobian/pushforward maps).
* **Faces/Loops** (\gamma): sequences of edges; holonomy (H_\gamma=\prod_{e\in\gamma}U_e).

### 7.2 Edge Factorization and Loop Diagnostics

Factor transports as
[
U_e \approx R_e, S_e, \quad R_e\in H \text{ (pure reframing)},; S_e\in\exp(\mathfrak m) \text{ (content shift)}.
]
On loops, (\prod R_e) diagnoses curvature; (\prod S_e) diagnoses torsion. Use polar/Cartan-like decompositions under a chosen metric.

### 7.3 Loop-Based Reconstruction Objective

Given a family of diagnostic loops (\mathcal L), fit ((A^\star,\Pi)) by
[
\mathcal S(A^\star,\Pi) = \sum_{\gamma\in\mathcal L}\left|\log H_\gamma - \oint_\gamma A^\star\right|^2 + \lambda,\mathcal R(\Pi),
]
with (\log) a Lie-log map near identity and regularizer (\mathcal R) (smoothness, sparsity, locality) encoding plausible instrument physics.

### 7.4 Lens-Flow (Calibration RG)

Evolve (\Pi) to reduce spurious holonomy while preserving stable curvature components:
[
\frac{d\Pi}{dt} = -\nabla_{\Pi},\mathbb E_{\gamma\sim\mu}\Big[\big|\log H_\gamma - !!\oint_\gamma A^\star\big|^2\Big],\quad \text{s.t. } \mathsf{Proj}_{\mathrm{stable}(\Omega)}(\Pi)=\text{const}.
]
Here (\mu) samples loop families; constraints prevent “fitting away” genuine reframing.

### 7.5 Complexity and Convergence Notes

For sparse (\mathcal L) over local neighborhoods, per-iteration cost scales with loop length and edge dimension. Use stochastic loop sampling and incremental (\log)-map updates; convergence can be certified by decrease of loop loss and budget satisfaction.

---

## 8. Diagnostics, Regimes, and Metrics

### 8.1 Regime Taxonomy

| Regime                 | Signal                                   | Expectation                                                   |
| ---------------------- | ---------------------------------------- | ------------------------------------------------------------- |
| High (\Omega), low (T) | Path-dependent reframing, content stable | Notation/discipline burdens; debate without deep disagreement |
| Low (\Omega), high (T) | Translation changes assertibles          | Interdisciplinary creases; genuine novelty & category risk    |
| Nearly gauge-flat      | (\Omega\approx 0), (T\approx 0)          | Beware false consensus (instrument dominance)                 |

### 8.2 Operational Tests

* **Torsion test:** apply two commuting micro-updates (\delta_1,\delta_2); if order matters in a way not gaugeable, (T\neq 0).
* **Curvature test:** loop transport preserves content yet changes basis; detect via non-trivial (W_\gamma) with (S)-part (\approx I).

### 8.3 Evaluation Metrics

* Loop loss (|\log H_\gamma - \oint_\gamma A^\star|) (mean/quantiles),
* Residual budgets (\epsilon) satisfaction rates,
* Holonomy deviation vs. (\eta) bounds,
* Geodesic–autoparallel gap (bias index),
* Stability of curvature modes across lenses/communities.

---

## 9. Applications and Case Studies

### 9.1 Science (Newton (\to) Relativity; Classical (\to) Quantum)

Residuals small in Newtonian low-velocity domains; large at relativistic regimes. Translation (T(\mathrm N\to\mathrm R)) well-conditioned locally, fails globally. Quantum requires change of model space (Hilbert bundle), seen as curvature that cannot be gauged away.

### 9.2 Multi-Agent AI

Ensembles with heterogeneous encoders define lenses; residual flow directs critique/revision. Constitutions curb overfitting by penalizing instrument complexity that erases stable (\Omega).

### 9.3 Social/Political Epistemics

Competing policy lenses project shared data differently; loop diagnostics across debates identify reframing burdens vs. genuinely divergent assertibles, guiding deliberation designs that reduce unproductive curvature while spotlighting torsional seams where new synthesis is needed.

---

## 10. Related Work (Selected Pointers)

* **Gauge/Cartan geometry:** Principal connections, curvature/torsion, Wilson loops.
* **Information geometry:** Fisher–Rao metric, contrast-induced geodesics, exponential families.
* **Category/compositionality:** Monoidal categories for processes; lenses/optics in functional programming.
* **Multi-agent RL & constitutional AI:** Strategy composition; rule-based oversight—here lifted to epistemic structure rather than outputs only.

*(Detailed bibliographic citations can be inserted to taste.)*

---

## 11. Limitations, Risks, and Ethical Notes

* **Modeling choice risk:** Poorly chosen (G,H) or metrics can imprint spurious curvature/torsion.
* **Over-regularization:** Aggressive (\mathcal R(\Pi)) or lens-flow constraints may smooth away legitimate novelty.
* **Computational scaling:** Loop enumeration is expensive; stochastic approximations required.
* **Misuse risk:** Framing disagreement as “mere geometry” must not minimize moral stakes; constitutions should encode fairness and safety constraints explicitly.

---

## 12. Conclusion

We unified EDG and AoA into a single, exhaustive framework: a **geometry of knowledge** (principal bundles, Cartan data, loop invariants) and a **grammar of agency** (composable operators) governed by **constitutions of learning**. With discrete instantiations, reconstruction objectives, and lens-flow dynamics, the theory is both principled and computable. The result is a roadmap to coherent pluralism—many agents, many lenses—coordinated by geometry rather than suppressed into uniformity.

---

## Acknowledgments

[Optional]

---

## Appendices (Exhaustive)

### Appendix A — Mathematical Background

**Lie groups and homogeneous spaces.** (G/H) as model space; Adjoint action; decomposition (\mathfrak g=\mathfrak h\oplus\mathfrak m).

**Principal bundles.** (\pi:P\to\mathcal K) with fiber (H); right action; local trivialisations and transition functions.

**Cartan connections.** (A\in\Omega^1(P,\mathfrak g)) reproduces generators on verticals; equivariant; soldering via (\theta). Structure equations as in §3.3.

**Parallel transport and holonomy.** Path-ordered exponentials; Ambrose–Singer type relations; Wilson loops as traces.

**Information/Finsler geometry.** Fisher–Rao and dually-flat structures; contrast functions and geodesics; pullbacks to (\mathcal K).

---

### Appendix B — Formal Results and Sketches

**B.1 Budgeted Consistency (Prop. 5.4).** Under bounds on (\Omega, T) compatible with ((\epsilon,\eta)), there exists a gauge with bounded geodesic–autoparallel deviation. *Sketch:* (i) relate loop holonomy to curvature integrals; (ii) bound via (\eta); (iii) tie residual calibration to torsion via commutator estimates; (iv) construct gauge minimizing mixed terms.

**B.2 Identifiability in the Inverse Problem.** With sufficiently rich loop family (\mathcal L) spanning (\pi_1) generators over overlaps, and regularity assumptions on (\Pi), the decomposition (A=A^\star+\Pi) is locally identifiable up to gauge. *Sketch:* uniqueness from loop equations modulo (H)-conjugacy and instrument class constraints.

---

### Appendix C — Algorithms & Pseudocode

**C.1 Edge Factorization (polar-like).**

```python
import numpy as np
from scipy.linalg import polar

def factor_edge(U):
    # Polar decomposition as a proxy: U = Q @ S, Q orthogonal ~ R (reframing), S SPD ~ S (content shift)
    Q, S = polar(U)
    return Q, S
```

**C.2 Loop Holonomy and Loss.**

```python
def loop_holonomy(loop_edges, U):
    H = np.eye(U[loop_edges[0]].shape[0])
    for e in loop_edges:
        H = U[e] @ H
    return H

def loop_loss(loops, U, A_predict):
    loss = 0.0
    for gamma in loops:
        H = loop_holonomy(gamma, U)
        pred = A_predict.integrate_over(gamma)  # path integral of A^*
        resid = logm(H) - pred
        loss += np.linalg.norm(resid, 'fro')**2
    return loss
```

**C.3 Lens-Flow (stochastic).**

```python
def lens_flow_step(Pi_params, sample_loops, U, A_star, lr, projector):
    grad = 0.0
    for gamma in sample_loops:
        H = loop_holonomy(gamma, U)
        pred = integrate_A_star(gamma, A_star)
        resid = logm(H) - pred
        grad += grad_wrt_Pi(resid, gamma, Pi_params)
    grad = projector.filter(grad)  # preserve stable curvature modes
    Pi_params -= lr * grad
    return Pi_params
```

---

### Appendix D — Diagram Specifications (for vector rendering)

1. **Knowledge manifold with bundle:** base surface (\mathcal K); fibers labeled by (H); sections as lenses.
2. **Cartan data:** arrows for (\theta) (content coding) and (\omega) (frame motion); parallelogram non-closure for (T); loop with basis rotation for (\Omega).
3. **AoA grammar:** nodes (\mathbf P,\mathbf R,\mathbf L,\mathbf V,\mathbf C,\mathbf A); common words as paths; sentences as parallel compositions.
4. **Discrete EDG:** node–edge graph; (U_e\to R_e,S_e) factor; highlight loop holonomy and its split.
5. **Lens-flow:** loss landscape over (\Pi)-parameters; trajectory showing reduction of spurious holonomy.

---

### Appendix E — Symbol Table / Glossary

* (G,H): symmetry and stabilizer groups; (\mathfrak g,\mathfrak h,\mathfrak m) Lie algebras with (\mathfrak g=\mathfrak h\oplus\mathfrak m).
* ((G/H)): model space (idealized semantics).
* (\mathcal K): knowledge manifold.
* (P\to\mathcal K): principal (H)-bundle of frames.
* Lens (s): section picking a frame.
* (A=\omega\oplus\theta): Cartan 1-form; (\omega) connection ((\mathfrak h)-valued), (\theta) coframe ((\mathfrak m)-valued).
* (T,\Omega): torsion, curvature.
* (A^\star,\Pi): terrain vs instrument components.
* (U_e): edge transport; (R_e,S_e): reframing/content factors.
* (W_\gamma): Wilson loop.
* (\epsilon,\lambda,\eta): calibration, complexity trade-off, holonomy budgets.
* AoA primitives: (\mathbf P,\mathbf R,\mathbf L,\mathbf V,\mathbf C,\mathbf A).

---

### Appendix F — Evaluation Protocols

* **Loop family design:** select cycles generating local homotopy classes and cross-community overlaps.
* **Budgets:** set (\epsilon,\eta) empirically via validation loops; tune (\lambda) to balance model simplicity and calibration.
* **Stability checks:** measure invariance of curvature signatures across time/lenses.
* **Ablations:** remove (\Pi) regularizers; switch off projector in lens-flow; measure overfitting to holonomy.

---

### Appendix G — Extended Examples

**G.1 Newton (\leftrightarrow) Relativity.** Low-velocity loops show near-trivial (\Omega); high-velocity loops incur non-trivial reframing (W_\gamma). Content shift (T) small; mainly curvature.

**G.2 Classical (\leftrightarrow) Quantum.** Some loops force content change (non-commuting observables); torsion localized at measurement-related faces; curvature indicates basis change in Hilbert bundle.

**G.3 Toy Corpus (Sentence-Transformers).** States as embeddings; edges as summarization/translation; compute (U_e), factor (R_e,S_e), run (\mathcal S) fit and lens-flow; visualize torsion heatmaps and Wilson-loop spectra.

---

### Appendix H — Measurement Plan & Playbook

1. **Stop arguing; run loops.** Pre-specify loop families; compute holonomies.
2. **Factor and map.** Decompose edges; chart curvature vs torsion concentrations.
3. **Deconvolve.** Fit (A^\star,\Pi) with (\mathcal S); audit identifiability on overlaps.
4. **Renormalize.** Run lens-flow with projections that preserve stable (\Omega) modes.
5. **Govern.** Enforce constitutions and geodesic–autoparallel gap bounds; publish Wilson-loop dashboards.

---

## Appendix I — Completeness Checklist (EDG 1–10 Crosswalk)

* **(1) (G/H), (\mathcal K), lens as section, principal (H)-bundle:** §3.1–3.2, Notation.
* **(2) Cartan data, (T,\Omega) with epistemic readings:** §3.3–3.4.
* **(3) Terrain–instrument split, observed tensors, inverse problem:** §3.6.
* **(4) Gauge action and loop observables, Wilson loops:** §3.4.
* **(5) Metric, geodesic vs autoparallel bias:** §3.5.
* **(6) Discrete/computable pipeline; (U_e\approx R_e S_e); action (\mathcal S):** §7.1–7.3; App. C; App. D.
* **(7) Reading invariants/regime taxonomy:** §8.1.
* **(8) Lens-flow (calibration RG):** §7.4.
* **(9) Operational correspondences/tests for (T) vs (\Omega):** §8.2.
* **(10) Measurement plan, deconvolution discipline, maps, toy instantiation:** §7.3–7.5; App. G–H.

**Result:** All ten items (and AoA merger) are fully represented, with diagnostics, algorithms, and governance.
