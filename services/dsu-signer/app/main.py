from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, Response
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel


class SignRequest(BaseModel):
    artifact_ref: str
    tier: str


class VerifyRequest(BaseModel):
    artifact_ref: str


app = FastAPI(title="DSU Signer", version="1.0.0")

REGISTRY = CollectorRegistry()
g_sign = Gauge("dsu_sign_total", "Count of sign operations", registry=REGISTRY)
g_verify = Gauge("dsu_verify_total", "Count of verify operations", registry=REGISTRY)


@app.post("/sign")
def sign(req: SignRequest) -> Dict[str, Any]:
    g_sign.inc()
    return {"artifact_ref": req.artifact_ref, "signatures": ["dsu:dev:signature"], "tier": req.tier}


@app.post("/verify")
def verify(req: VerifyRequest) -> Dict[str, Any]:
    g_verify.inc()
    return {"artifact_ref": req.artifact_ref, "quorum_met": True}


@app.get("/metrics")
def metrics() -> Response:
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.get("/healthz")
def healthz() -> Response:
    return Response(status_code=204)


