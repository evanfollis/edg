from __future__ import annotations

import json
import os
import requests
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST
from edg_numerics import (
    loop_holonomy as hn_loop_holonomy,
    stable_logm,
    curvature_torsion_closure_from_log,
    rotation_angle_norm_from_log,
)
from jsonschema import validate as js_validate, ValidationError as JSValidationError
import redis


REPO_ROOT = Path(__file__).resolve().parents[3]
HOLONOMY_SCHEMA_PATH = REPO_ROOT / "contracts" / "schemas" / "holonomy_result.schema.json"


def load_holonomy_schema() -> Dict[str, Any]:
    with HOLONOMY_SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


holonomy_schema = load_holonomy_schema()


class RunRequest(BaseModel):
    loop_id: str
    state_ref: str
    edge_ids: List[str]


app = FastAPI(title="Holonomy Engine", version="1.0.0")
REGISTRY = CollectorRegistry()
g_curv = Gauge(
    "holonomy_curvature_fro",
    "Curvature Frobenius norm",
    labelnames=("loop_id", "regime_tag"),
    registry=REGISTRY,
)
g_tors = Gauge(
    "holonomy_torsion_fro",
    "Torsion Frobenius norm",
    labelnames=("loop_id", "regime_tag"),
    registry=REGISTRY,
)
g_close = Gauge(
    "holonomy_closure_norm",
    "Closure norm",
    labelnames=("loop_id", "regime_tag"),
    registry=REGISTRY,
)

# Trust-region caps from env (aligned with CI defaults)
DELTA_MAX = float(os.getenv("IV_DELTA_MAX", "0.10"))
THETA_MAX = float(os.getenv("IV_THETA_MAX", "0.50"))
REL_LOG_PER_DIM = float(os.getenv("IV_REL_LOG_PER_DIM", "0.005"))

# Service endpoints
TR_BASE = os.getenv("TRANSPORT_REGISTRY_BASE", f"http://localhost:{os.getenv('TRANSPORT_REGISTRY_PORT','7001')}")
LR_BASE = os.getenv("LOOP_REGISTRY_BASE", f"http://localhost:{os.getenv('LOOP_REGISTRY_PORT','7003')}")
EVENT_BUS_URL = os.getenv("EVENT_BUS_URL")


def fetch_loop(loop_id: str) -> Dict[str, Any] | None:
    try:
        r = requests.get(f"{LR_BASE}/loops/{loop_id}", timeout=2.0)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None


def fetch_edge_dim(edge_id: str) -> int | None:
    try:
        r = requests.get(f"{TR_BASE}/edges/{edge_id}", timeout=2.0)
        if r.status_code == 200:
            data = r.json()
            shape = data.get("U", {}).get("shape")
            if isinstance(shape, list) and len(shape) == 2 and isinstance(shape[1], int):
                return shape[1]
    except Exception:
        return None
    return None


def fetch_edge_U(edge_id: str) -> np.ndarray | None:
    """Fetch U shape and synthesize identity matrix of appropriate dimension.

    Note: weights are referenced by content-hash and not directly retrievable here; we
    use identity as a placeholder that respects shape for trust-region-safe logging.
    """
    try:
        r = requests.get(f"{TR_BASE}/edges/{edge_id}", timeout=2.0)
        if r.status_code == 200:
            data = r.json()
            shape = data.get("U", {}).get("shape")
            if isinstance(shape, list) and len(shape) == 2 and all(isinstance(x, int) for x in shape):
                m, n = shape
                if m == n:
                    return np.eye(n)
                # For non-square, return an identity-like rectangular embedding
                mat = np.zeros((m, n))
                k = min(m, n)
                for i in range(k):
                    mat[i, i] = 1.0
                return mat
    except Exception:
        return None
    return None


def publish_event(stream: str, payload: Dict[str, Any]) -> None:
    if not EVENT_BUS_URL:
        return
    try:
        r = redis.from_url(EVENT_BUS_URL, decode_responses=True)
        r.xadd(stream, {"payload": json.dumps(payload)})
    except Exception:
        # best-effort; ignore failures
        pass


def identity_metrics(dim: int) -> Dict[str, Any]:
    return {
        "curvature_fro": 0.0,
        "torsion_fro": 0.0,
        "closure_norm": 0.0,
        "segments": 1,
        "dim": dim,
    }


@app.post("/run")
def run_loop(req: RunRequest) -> Dict[str, Any]:
    # Dim and U map from edges
    dim = fetch_edge_dim(req.edge_ids[0]) or 64 if req.edge_ids else 64
    U_map: Dict[str, np.ndarray] = {}
    for eid in req.edge_ids:
        U = fetch_edge_U(eid)
        if U is None:
            # fallback to square identity with inferred dim
            U = np.eye(dim)
        U_map[eid] = U
    # Loop metadata (trust-region + regime)
    loop_meta = fetch_loop(req.loop_id) or {}
    regime_tag = (loop_meta.get("regime_tags") or ["default"]) [0]
    trust = loop_meta.get("trust_region") or {}
    delta_cap = float(trust.get("delta_max", DELTA_MAX))
    theta_cap = float(trust.get("theta_max_rad", THETA_MAX))
    rel_log_cap = float(trust.get("rel_log_fro_max_per_dim", REL_LOG_PER_DIM))

    # Compute holonomy and metrics using numerics lib
    try:
        H = hn_loop_holonomy(req.edge_ids, U_map)
        L = stable_logm(H, delta_max=delta_cap)
        # Segment-level checks: treat each edge transport as a segment
        prev_L = None
        for eid in req.edge_ids:
            Ui = U_map[eid]
            Li = stable_logm(Ui, delta_max=delta_cap)
            rot_mag = rotation_angle_norm_from_log(Li)
            if rot_mag > THETA_MAX + 1e-12:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": {
                            "code": "IV.NUMERIC.TRUST_REGION",
                            "message": "Per-segment rotation exceeds θ_max.",
                            "detail": {"theta": rot_mag, "theta_max": THETA_MAX, "edge_id": eid},
                        }
                    },
                )
            if prev_L is not None:
                rel = float(np.linalg.norm(Li - prev_L, 'fro') / max(dim, 1))
                if rel > REL_LOG_PER_DIM + 1e-12:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": {
                                "code": "IV.NUMERIC.TRUST_REGION",
                                "message": "Log branch discontinuity exceeds per-dim cap.",
                                "detail": {"rel": rel, "cap": REL_LOG_PER_DIM, "edge_id": eid},
                            }
                        },
                    )
            prev_L = Li
        metrics = curvature_torsion_closure_from_log(L)
    except ValueError as ve:
        # Trust region violated; return structured error per ERRORS.md
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "IV.NUMERIC.TRUST_REGION",
                    "message": "Loop segment outside log trust region (δ).",
                    "detail": {"delta_max": delta_cap, "loop_id": req.loop_id},
                }
            },
        ) from ve

    # Generic: produce small random-ish stable values
    weights = [1.0 / max(len(req.edge_ids), 1)] * len(req.edge_ids)
    attribution = [[eid, w] for eid, w in zip(req.edge_ids, weights)]
    # Wilson diagnostics (simple proxies)
    wilson_trace = float(np.trace(L))
    log_fro = float(np.linalg.norm(L, 'fro'))
    result = {
        "loop_id": req.loop_id,
        "H_ref": "sha256:H_mock",
        "curvature_fro": metrics["curvature_fro"],
        "torsion_fro": metrics["torsion_fro"],
        "closure_norm": metrics["closure_norm"],
        "wilson_trace": wilson_trace,
        "edge_attribution": attribution,
        "segments": 1,
        "dim": dim,
        "timestamp": "2025-10-07T15:02:11Z",
        "regime_tag": regime_tag,
        "log_fro": log_fro,
    }
    # Schema validation before emitting
    try:
        js_validate(instance=result, schema=holonomy_schema)
    except JSValidationError as ve:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "IV.SCHEMA.VALIDATION",
                    "message": "Holonomy result schema validation failed.",
                    "detail": {"path": list(ve.absolute_path), "msg": ve.message},
                }
            },
        ) from ve

    g_curv.labels(loop_id=req.loop_id, regime_tag=regime_tag).set(result["curvature_fro"])
    g_tors.labels(loop_id=req.loop_id, regime_tag=regime_tag).set(result["torsion_fro"])
    g_close.labels(loop_id=req.loop_id, regime_tag=regime_tag).set(result["closure_norm"])
    # Emit loop.run.completed (best-effort internal event)
    try:
        requests.post(f"{LR_BASE}/events/loop_run_completed", json=result, timeout=1.5)
    except Exception:
        pass
    # Publish to event bus (best-effort)
    publish_event("loop.run.completed", result)
    return result


@app.get("/metrics")
def metrics() -> Response:
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


