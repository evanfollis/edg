from __future__ import annotations

from typing import Dict, Iterable, List

import numpy as np
from numpy.linalg import norm


def loop_holonomy(edge_ids: List[str], edge_id_to_U: Dict[str, np.ndarray]) -> np.ndarray:
    """Compute loop holonomy H = prod U_e in traversal order (right-multiplying base)."""
    if not edge_ids:
        raise ValueError("edge_ids must be non-empty")
    first = edge_id_to_U[edge_ids[0]]
    H = np.eye(first.shape[0])
    for eid in edge_ids:
        H = edge_id_to_U[eid] @ H
    return H


def curvature_torsion_closure_from_log(logH: np.ndarray) -> Dict[str, float]:
    """Minimal placeholder metrics from logH; extend as needed."""
    fro = float(norm(logH, 'fro'))
    return {
        "curvature_fro": fro * 0.5,
        "torsion_fro": fro * 0.25,
        "closure_norm": fro * 0.2,
    }


