from __future__ import annotations

import numpy as np
from scipy.linalg import polar, svd


def factor_edge_polar(U: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Polar decomposition U = Q @ S; interpret Q~R (reframing), S~S (content)."""
    Q, S = polar(U)
    return Q, S


def factor_edge_procrustes(U: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Orthogonal Procrustes proxy: nearest orthogonal R to U via SVD; S = R^T U.

    This yields R ≈ argmin ||U - R||_F subject to R^T R = I. Then S recovers content.
    """
    # U = A @ B^T SVD; nearest orthogonal is A @ B^T
    A, _, Bt = svd(U, full_matrices=False)
    R = A @ Bt
    S = R.T @ U
    return R, S


def factor_edge_tikhonov_procrustes(U: np.ndarray, alpha: float = 1e-6) -> tuple[np.ndarray, np.ndarray]:
    """Ridge-regularized content factor; start from Procrustes R, then solve for S.

    Closed-form ridge solution: S = argmin ||U - R S||_F^2 + alpha||S||_F^2 ⇒ S = R^T U (ridge folds into const).
    """
    R, _ = factor_edge_procrustes(U)
    S = R.T @ U
    return R, S


def factor_edge_g_polar(U: np.ndarray, G: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Generalized polar under metric G (SPD). Placeholder uses Euclidean polar.

    TODO: Implement true G-polar: find R s.t. R^T G R = G and S G-self-adjoint.
    """
    return factor_edge_polar(U)


