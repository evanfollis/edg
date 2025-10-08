from __future__ import annotations

import numpy as np
from scipy.linalg import polar


def factor_edge_polar(U: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Polar decomposition U = Q @ S; interpret Q~R (reframing), S~S (content)."""
    Q, S = polar(U)
    return Q, S


