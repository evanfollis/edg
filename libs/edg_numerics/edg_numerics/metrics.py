from __future__ import annotations

from typing import Optional

import numpy as np
from numpy.linalg import norm
from scipy.linalg import logm


def is_near_identity(H: np.ndarray, delta_max: float) -> bool:
    """Spectral norm trust-region check for log(H): ||H - I||_2 <= delta_max."""
    return norm(H - np.eye(H.shape[0]), 2) <= delta_max


def stable_logm(H: np.ndarray, delta_max: float) -> np.ndarray:
    """Branch-continuous log with trust-region guard; raise if outside region.

    The caller should segment loops before calling log if this guard fails.
    """
    if is_near_identity(H, delta_max=delta_max):
        return logm(H)
    raise ValueError("Trust region violated; segment loop before log.")


def trust_region(H: np.ndarray, delta_max: float) -> bool:
    """Alias for is_near_identity; explicit API per PR-2."""
    return is_near_identity(H, delta_max)


def segment_loop(edge_mats: list[np.ndarray], delta_max: float) -> list[list[np.ndarray]]:
    """Greedy segmentation: split sequence so each segment product stays in trust region.

    Returns list of segments (each a list of matrices). Minimal placeholder strategy.
    """
    segments: list[list[np.ndarray]] = []
    current: list[np.ndarray] = []
    acc: Optional[np.ndarray] = None
    for U in edge_mats:
        if acc is None:
            acc = U.copy()
            current = [U]
        else:
            candidate = U @ acc
            if is_near_identity(candidate, delta_max):
                acc = candidate
                current.append(U)
            else:
                segments.append(current)
                acc = U.copy()
                current = [U]
    if current:
        segments.append(current)
    return segments


def roundtrip_distortion(U: np.ndarray, U_inv_approx: np.ndarray) -> float:
    """Validation round-trip distortion: ||U_inv U − I||_F / sqrt(N)."""
    I = np.eye(U.shape[1])
    return float(norm(U_inv_approx @ U - I, 'fro') / np.sqrt(I.size))


def procrustes_residual(X: np.ndarray, Y: np.ndarray, R: np.ndarray) -> float:
    """Residual of orthogonal Procrustes fit: ||X R − Y||_F / ||Y||_F."""
    denom = max(norm(Y, 'fro'), 1e-12)
    return float(norm(X @ R - Y, 'fro') / denom)


def skew_part(M: np.ndarray) -> np.ndarray:
    """Skew-symmetric component: (M - Mᵀ)/2."""
    return 0.5 * (M - M.T)


def rotation_angle_norm_from_log(logH: np.ndarray) -> float:
    """Proxy for rotation magnitude: spectral norm of the skew part of log(H)."""
    K = skew_part(logH)
    return float(norm(K, 2))


