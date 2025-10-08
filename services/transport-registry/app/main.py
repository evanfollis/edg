from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from jsonschema import validate, ValidationError
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST


REPO_ROOT = Path(__file__).resolve().parents[3]
TRANSPORT_SCHEMA_PATH = REPO_ROOT / "contracts" / "schemas" / "transport_edge.schema.json"


def load_transport_schema() -> Dict[str, Any]:
    with TRANSPORT_SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


transport_schema = load_transport_schema()


class TransportEdgeBody(BaseModel):
    # Accept arbitrary payload; validation is performed via jsonschema
    __root__: Dict[str, Any]

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:  # type: ignore[override]
        return self.__root__


app = FastAPI(title="Transport Registry", version="1.0.0")


# In-memory store keyed by edge_id
EDGE_STORE: Dict[str, Dict[str, Any]] = {}


# ---- Configuration (env with defaults aligned to CI) ----
KAPPA_MAX = float(os.getenv("IV_KAPPA_MAX", "500"))
TAU_MAX = float(os.getenv("IV_TAU_MAX", "0.02"))
RHO_MAX = float(os.getenv("IV_RHO_MAX", "0.01"))


# ---- Metrics ----
REGISTRY = CollectorRegistry()
g_edge_kappa = Gauge(
    "edge_kappa",
    "Condition number of transport U_e",
    labelnames=("edge_id",),
    registry=REGISTRY,
)
g_edge_roundtrip = Gauge(
    "edge_roundtrip",
    "Round-trip distortion of U_e",
    labelnames=("edge_id",),
    registry=REGISTRY,
)
g_edge_rho = Gauge(
    "edge_rho",
    "Procrustes residual (if applicable)",
    labelnames=("edge_id",),
    registry=REGISTRY,
)


@app.post("/edges", status_code=status.HTTP_201_CREATED)
def register_edge(body: TransportEdgeBody) -> Dict[str, Any]:
    payload = body.dict()
    try:
        validate(instance=payload, schema=transport_schema)
    except ValidationError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "IV.SCHEMA.VALIDATION",
                    "message": "Transport edge schema validation failed.",
                    "detail": {"path": list(ve.absolute_path), "msg": ve.message},
                }
            },
        ) from ve

    edge_id = payload.get("edge_id")
    if not isinstance(edge_id, str) or len(edge_id) == 0:
        raise HTTPException(status_code=400, detail="edge_id is required")

    EDGE_STORE[edge_id] = payload

    # Numeric guardrails
    try:
        diag = payload.get("diagnostics", {})
        kappa = float(diag.get("kappa", 0.0))
        roundtrip = float(diag.get("roundtrip", 0.0))
        rho = float(diag.get("rho", 0.0))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail="invalid diagnostics values") from exc

    if kappa > KAPPA_MAX:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "IV.NUMERIC.KAPPA_EXCEEDED",
                    "message": f"κ={kappa:.1f} exceeds cap {KAPPA_MAX}",
                    "detail": {"edge_id": edge_id, "kappa": kappa, "cap": KAPPA_MAX},
                }
            },
        )
    if roundtrip > TAU_MAX:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "IV.NUMERIC.ROUNDTRIP_EXCEEDED",
                    "message": f"round-trip distortion {roundtrip:.4f} > τ {TAU_MAX}",
                    "detail": {"edge_id": edge_id, "roundtrip": roundtrip, "cap": TAU_MAX},
                }
            },
        )
    if rho > RHO_MAX:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "IV.NUMERIC.PROCRUSTES_RESIDUAL",
                    "message": f"Procrustes residual {rho:.4f} > ρ {RHO_MAX}",
                    "detail": {"edge_id": edge_id, "rho": rho, "cap": RHO_MAX},
                }
            },
        )

    # Nonlinear parsimony declaration (if edge_type == nonlinear)
    if payload.get("edge_type") == "nonlinear":
        has_penalty = payload.get("nonlinear_penalty") is not None
        has_proof = payload.get("oos_torsion_proof") is not None
        if not (has_penalty or has_proof):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "IV.SCHEMA.VALIDATION",
                        "message": "Nonlinear edge must declare content-parsimony penalty or attach OOS torsion proof.",
                        "detail": {"edge_id": edge_id},
                    }
                },
            )

    # Record metrics
    g_edge_kappa.labels(edge_id=edge_id).set(kappa)
    g_edge_roundtrip.labels(edge_id=edge_id).set(roundtrip)
    g_edge_rho.labels(edge_id=edge_id).set(rho)
    return {"status": "created", "edge_id": edge_id}


@app.get("/edges")
def list_edges() -> List[Dict[str, Any]]:
    return list(EDGE_STORE.values())


@app.get("/edges/{edge_id}")
def get_edge(edge_id: str) -> Dict[str, Any]:
    if edge_id not in EDGE_STORE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="edge not found")
    return EDGE_STORE[edge_id]


@app.get("/healthz")
def healthz() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/metrics")
def metrics() -> Response:
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


