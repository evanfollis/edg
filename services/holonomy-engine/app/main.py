from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST


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
    # Minimal placeholder: if edge pair looks like identity round-trip, emit tiny values
    dim = 64
    if len(req.edge_ids) >= 2 and req.edge_ids[0].startswith("quant->pm") and req.edge_ids[1].startswith("pm->quant"):
        metrics = identity_metrics(dim)
        result = {
            "loop_id": req.loop_id,
            "H_ref": "sha256:H_identity",
            **metrics,
            "edge_attribution": [[req.edge_ids[0], 0.5], [req.edge_ids[1], 0.5]],
            "timestamp": "2025-10-07T15:02:11Z",
        }
        g_curv.labels(loop_id=req.loop_id, regime_tag="identity").set(metrics["curvature_fro"])
        g_tors.labels(loop_id=req.loop_id, regime_tag="identity").set(metrics["torsion_fro"])
        g_close.labels(loop_id=req.loop_id, regime_tag="identity").set(metrics["closure_norm"])
        return result

    # Generic: produce small random-ish stable values
    rng = np.random.default_rng(42)
    curvature = float(abs(rng.normal(0.0, 1e-4)))
    torsion = float(abs(rng.normal(0.0, 5e-5)))
    closure = float(abs(rng.normal(0.0, 5e-5)))
    weights = [1.0 / max(len(req.edge_ids), 1)] * len(req.edge_ids)
    attribution = [[eid, w] for eid, w in zip(req.edge_ids, weights)]
    result = {
        "loop_id": req.loop_id,
        "H_ref": "sha256:H_mock",
        "curvature_fro": curvature,
        "torsion_fro": torsion,
        "closure_norm": closure,
        "edge_attribution": attribution,
        "segments": 1,
        "dim": 64,
        "timestamp": "2025-10-07T15:02:11Z",
    }
    g_curv.labels(loop_id=req.loop_id, regime_tag="default").set(curvature)
    g_tors.labels(loop_id=req.loop_id, regime_tag="default").set(torsion)
    g_close.labels(loop_id=req.loop_id, regime_tag="default").set(closure)
    return result


@app.get("/metrics")
def metrics() -> Response:
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


