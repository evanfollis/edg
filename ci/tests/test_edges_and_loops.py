"""
CI Template: Edge invariants, nonlinear parsimony, and loop trust/continuity
- Thresholds are driven by env vars (with sane defaults).
- Fails build on hard breaches; warns or logs for drifts as configured.
"""

import os
import numpy as np
from numpy.linalg import norm, cond
from scipy.linalg import logm

# -------- Config (env or defaults) --------
KAPPA_MAX = float(os.getenv("IV_KAPPA_MAX", "500"))      # condition number cap
TAU_MAX   = float(os.getenv("IV_TAU_MAX",   "0.02"))     # round-trip distortion
RHO_MAX   = float(os.getenv("IV_RHO_MAX",   "0.01"))     # Procrustes residual
DELTA_MAX = float(os.getenv("IV_DELTA_MAX", "0.10"))     # log trust region
THETA_MAX = float(os.getenv("IV_THETA_MAX", "0.50"))     # per-segment rotation proxy (rad)
REL_LOG_PER_DIM = float(os.getenv("IV_REL_LOG_PER_DIM", "0.005"))  # continuity / dim
KAPPA_S_MAX = float(os.getenv("IV_KAPPA_S_MAX", "100"))  # cond cap for S (nonlinear)
ALPHA_S = float(os.getenv("IV_ALPHA_S", "1.0"))          # S Fro penalty weight (nonlinear)
ALPHA_COND = float(os.getenv("IV_ALPHA_COND", "0.1"))    # cond(S) penalty weight

# -------- Utilities --------

def is_near_identity(H, delta_max=DELTA_MAX):
    """Spectral norm trust-region check for log(H)."""
    return norm(H - np.eye(H.shape[0]), 2) <= delta_max

def roundtrip_distortion(U, U_inv_approx):
    """Compute validation round-trip distortion ‖U_inv U − I‖_F / sqrt(N)."""
    I = np.eye(U.shape[1])
    return norm(U_inv_approx @ U - I, 'fro') / np.sqrt(I.size)

def procrustes_residual(X, Y, R):
    """Residual of orthogonal Procrustes fit: ‖XR − Y‖_F / ‖Y‖_F."""
    denom = max(norm(Y, 'fro'), 1e-12)
    return norm(X @ R - Y, 'fro') / denom

def stable_logm(H):
    """Branch-continuous log with trust-region check; segment if needed."""
    if is_near_identity(H):
        return logm(H)
    raise ValueError("Trust region violated; segment loop before log.")

def skew_part(M):
    """Skew-symmetric component: (M - Mᵀ)/2."""
    return 0.5 * (M - M.T)

def rotation_angle_norm_from_log(logH):
    """
    Proxy for rotation magnitude: spectral norm of the skew part of log(H).
    Suitable for per-segment cap θ_max.
    """
    K = skew_part(logH)
    return norm(K, 2)

# -------- Edge-level tests --------

def test_edge_condition_number(edge_artifact):
    """
    Edge must declare U and report κ(U). Fail if κ > KAPPA_MAX.
    """
    U = edge_artifact.U  # np.ndarray
    kappa = cond(U)
    assert kappa <= KAPPA_MAX, f"κ={kappa:.1f} exceeds cap {KAPPA_MAX}"

def test_edge_roundtrip_distortion(edge_artifact):
    """
    Edge must supply an approximate inverse or left-inverse for round-trip check.
    """
    U = edge_artifact.U
    U_inv = edge_artifact.U_inv_approx
    rt = roundtrip_distortion(U, U_inv)
    assert rt <= TAU_MAX, f"round-trip distortion {rt:.4f} > τ {TAU_MAX}"

def test_edge_factorization_residual(edge_artifact):
    """
    For non-square edges using Procrustes, residual must be ≤ ρ.
    """
    if getattr(edge_artifact, "factorization", "") == "procrustes":
        X, Y, R = edge_artifact.procrustes_inputs  # np arrays
        res = procrustes_residual(X, Y, R)
        assert res <= RHO_MAX, f"Procrustes residual {res:.4f} > ρ {RHO_MAX}"

def test_nonlinear_edge_parsimony(edge_artifact):
    """
    Nonlinear edges must either:
      (a) declare content-parsimony penalties for S (ALPHA_S, ALPHA_COND, KAPPA_S_MAX), or
      (b) attach an 'oos_torsion_proof' artifact that satisfies the waiver criteria.
    """
    if getattr(edge_artifact, "edge_type", "linear") == "nonlinear":
        has_proof = getattr(edge_artifact, "oos_torsion_proof", None) is not None
        has_penalty = getattr(edge_artifact, "nonlinear_penalty", None) is not None
        assert has_proof or has_penalty, (
            "Nonlinear edge must declare content-parsimony penalty or attach OOS torsion proof."
        )
        if has_penalty:
            S = edge_artifact.S_factor  # expected to be provided at fit-validation
            assert S is not None, "Nonlinear penalty declared but S_factor missing."
            condS = cond(S)
            # soft check: warn via log if needed; hard fail if wildly ill-conditioned
            assert condS <= max(10 * KAPPA_S_MAX, 1e3), f"cond(S)={condS:.1f} too large; check fit."

# -------- Loop-level tests --------

def test_loop_trust_region(loop_artifact):
    """
    Ensure each loop segment satisfies ‖H - I‖₂ ≤ δ prior to log.
    """
    for H in loop_artifact.segment_holonomies:  # list of np arrays
        assert is_near_identity(H), "Loop segment outside log trust region (δ)."

def test_loop_branch_continuity(loop_artifact):
    """
    Continuity checks per segment:
      (i) rotation magnitude proxy ≤ THETA_MAX,
      (ii) relative Frobenius delta per dimension ≤ REL_LOG_PER_DIM.
    """
    prev = None
    d = loop_artifact.dim
    for H in loop_artifact.segment_holonomies:
        L = stable_logm(H)
        rot_mag = rotation_angle_norm_from_log(L)
        assert rot_mag <= THETA_MAX + 1e-12, f"Rotation jump {rot_mag:.3f} > θ_max {THETA_MAX}"
        if prev is not None:
            rel = norm(L - prev, 'fro') / max(d, 1)
            assert rel <= REL_LOG_PER_DIM + 1e-12, (
                f"Log branch discontinuity: rel {rel:.4e} > {REL_LOG_PER_DIM:.4e}"
            )
        prev = L

# -------- Gold Loops Battery (Sev-1 gates) --------

def test_gold_loops_bounds(gold_registry, gold_observations):
    """
    Enforce gauge-fixing bounds (percentile-based or absolute).
    gold_observations[loop_id] must supply recent scalar series per loop.
    """
    for gl in gold_registry.loops:
        obs = gold_observations[gl.id]  # list/array of recent scalar metrics
        assert len(obs) > 0, f"No observations for gold loop {gl.id}"
        if gl.bound.type == "percentile":
            window = int(gl.bound.window_days)
            pct = np.percentile(obs[-window:], gl.bound.percentile)
            assert pct <= gl.bound.threshold_bps + 1e-12, (
                f"{gl.id} {gl.bound.percentile}p={pct:.3f} > {gl.bound.threshold_bps} bps"
            )
        elif gl.bound.type == "absolute":
            latest = obs[-1]
            assert latest <= gl.bound.threshold + 1e-15, (
                f"{gl.id} abs={latest:.6e} > {gl.bound.threshold:.6e}"
            )
        else:
            raise ValueError(f"Unknown bound type {gl.bound.type}")

# -------- CI env snippet (for reference) --------
# In your CI pipeline (e.g., GitHub Actions):
# env:
#   IV_KAPPA_MAX: "500"
#   IV_TAU_MAX: "0.02"
#   IV_RHO_MAX: "0.01"
#   IV_DELTA_MAX: "0.10"
#   IV_THETA_MAX: "0.50"
#   IV_REL_LOG_PER_DIM: "0.005"
#   IV_KAPPA_S_MAX: "100"
#   IV_ALPHA_S: "1.0"
#   IV_ALPHA_COND: "0.1"
