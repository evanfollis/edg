from __future__ import annotations

from typing import Any, Dict, List
from fastapi import Response
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST

from fastapi import FastAPI
from pydantic import BaseModel


class ResidualsRequest(BaseModel):
    agent_i: str
    agent_j: str
    evidence_refs: List[str]
    k_space_id: str
    factorization_method: str | None = "polar"
    regime_tag: str | None = None


app = FastAPI(title="Residual Service", version="1.1.0")

REGISTRY = CollectorRegistry()
g_resid = Gauge(
    "residual_norm",
    "Residual norm between agents",
    labelnames=("agent_i", "agent_j", "regime_tag"),
    registry=REGISTRY,
)


@app.post("/residuals")
def residuals(req: ResidualsRequest) -> Dict[str, Any]:
    # Mock computation with deterministic values
    return {
        "agent_i": req.agent_i,
        "agent_j": req.agent_j,
        "r_norm": 0.01,
        "translator_ref": "sha256:Tij",
        "Rij_ref": "sha256:Rij",
        "Sij_ref": "sha256:Sij",
        "diagnostics": {
            "method": req.factorization_method or "polar",
            "kappa": 50.0,
            "rho": 0.005,
            "roundtrip": 0.012,
            "regime_tag": req.regime_tag or "default",
        },
    }


@app.get("/metrics")
def metrics() -> Response:
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


