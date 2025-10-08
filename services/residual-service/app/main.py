from __future__ import annotations

from typing import Any, Dict, List
import hashlib
import os
import requests
from fastapi import Response
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST
from edg_numerics import (
    factor_edge_polar,
    factor_edge_procrustes,
    factor_edge_tikhonov_procrustes,
    factor_edge_g_polar,
)

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
g_artifacts = Gauge("residual_artifacts_total", "Artifacts uploaded", registry=REGISTRY)


# Object store / DSU config
OBJ_ENDPOINT = os.getenv("OBJECT_STORE_ENDPOINT", "http://localhost:9000")
OBJ_BUCKET = os.getenv("OBJECT_STORE_BUCKET", "edg-artifacts")
OBJ_ACCESS = os.getenv("OBJECT_STORE_ACCESS_KEY", "minioadmin")
OBJ_SECRET = os.getenv("OBJECT_STORE_SECRET_KEY", "minioadmin")
DSU_BASE = os.getenv("DSU_SIGNER_BASE", f"http://localhost:{os.getenv('DSU_SIGNER_PORT','7006')}")


def put_artifact(content: bytes) -> str:
    """Content-address artifact and upload to object store (best-effort).

    Returns a content-addressed reference string 'sha256:<hex>'.
    """
    digest = hashlib.sha256(content).hexdigest()
    ref = f"sha256:{digest}"
    try:
        import boto3  # lazy import to keep startup fast

        s3 = boto3.client(
            "s3",
            endpoint_url=OBJ_ENDPOINT,
            aws_access_key_id=OBJ_ACCESS,
            aws_secret_access_key=OBJ_SECRET,
        )
        # Ensure bucket exists
        try:
            s3.head_bucket(Bucket=OBJ_BUCKET)
        except Exception:
            s3.create_bucket(Bucket=OBJ_BUCKET)
        s3.put_object(Bucket=OBJ_BUCKET, Key=digest, Body=content)
        g_artifacts.inc()
    except Exception:
        # Best-effort; proceed even if store is unavailable
        pass
    return ref


def dsu_sign(ref: str, tier: str = "T2") -> None:
    try:
        requests.post(f"{DSU_BASE}/sign", json={"artifact_ref": ref, "tier": tier}, timeout=1.5)
    except Exception:
        pass


@app.post("/residuals")
def residuals(req: ResidualsRequest) -> Dict[str, Any]:
    # Choose factorization method; placeholder artifacts remain deterministic
    method = (req.factorization_method or "polar").lower()
    if method not in {"polar", "procrustes", "tikhonov_procrustes", "g_polar"}:
        method = "polar"

    # Create deterministic placeholder artifacts and upload
    base = f"{req.agent_i}->{req.agent_j}:{method}".encode()
    translator_ref = put_artifact(b"T:" + base)
    Rij_ref = put_artifact(b"R:" + base)
    Sij_ref = put_artifact(b"S:" + base)
    dsu_sign(translator_ref)
    dsu_sign(Rij_ref)
    dsu_sign(Sij_ref)
    return {
        "agent_i": req.agent_i,
        "agent_j": req.agent_j,
        "r_norm": 0.01,
        "translator_ref": translator_ref,
        "Rij_ref": Rij_ref,
        "Sij_ref": Sij_ref,
        "diagnostics": {
            "method": method,
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


@app.get("/healthz")
def healthz() -> Response:
    return Response(status_code=204)


