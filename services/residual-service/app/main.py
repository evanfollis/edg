from __future__ import annotations

from typing import Any, Dict, List, Optional
import hashlib
import os
import json
import requests
import redis
from fastapi import Response, HTTPException, status
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST
from jsonschema import validate as js_validate, ValidationError as JSValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
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
EVENT_BUS_URL = os.getenv("EVENT_BUS_URL")


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
    result = {
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
    # Optional translator artifact preview validation (non-blocking)
    try:
        schema_path = Path(__file__).resolve().parents[3] / "contracts" / "schemas" / "translator_Tij.schemas.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        preview = {
            "translator_id": translator_ref,
            "agent_i": req.agent_i,
            "agent_j": req.agent_j,
            "k_space_id": req.k_space_id,
            "T_ref": translator_ref,
            "R_ref": Rij_ref,
            "S_ref": Sij_ref,
            "factorization": {"method": method},
            "diagnostics": {
                "kappa": 50.0,
                "rho": 0.005,
                "roundtrip": 0.012,
                "unit_map": {},
                "regime_tag": req.regime_tag or "default",
            },
            "signatures": ["dsu:dev"],
        }
        js_validate(instance=preview, schema=schema)
    except Exception:
        pass
    publish_event("residual.completed", result)
    return result


# ---- Persistence (Postgres) for translators ----
PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT", "5432")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")
PGDATABASE = os.getenv("PGDATABASE")


def get_engine() -> Optional[Engine]:
    if not (PGHOST and PGUSER and PGPASSWORD and PGDATABASE):
        return None
    url = f"postgresql+psycopg://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text(
                """
                CREATE TABLE IF NOT EXISTS translators (
                    translator_id TEXT PRIMARY KEY,
                    payload JSONB NOT NULL
                )
                """
            ))
        return engine
    except Exception:
        return None


DB_ENGINE = get_engine()


def publish_event(stream: str, payload: Dict[str, Any]) -> None:
    if not EVENT_BUS_URL:
        return
    try:
        r = redis.from_url(EVENT_BUS_URL, decode_responses=True)
        r.xadd(stream, {"payload": json.dumps(payload)})
    except Exception:
        pass


@app.post("/translators", status_code=status.HTTP_201_CREATED)
def create_translator(body: Dict[str, Any]) -> Dict[str, Any]:
    """Persist a translator artifact per translator_Tij schema and publish event."""
    try:
        schema_path = Path(__file__).resolve().parents[3] / "contracts" / "schemas" / "translator_Tij.schemas.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        js_validate(instance=body, schema=schema)
    except JSValidationError as ve:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "IV.SCHEMA.VALIDATION",
                    "message": "translator_Tij schema validation failed",
                    "detail": {"path": list(ve.absolute_path), "msg": ve.message},
                }
            },
        ) from ve

    translator_id = body.get("translator_id")
    if not isinstance(translator_id, str) or not translator_id:
        raise HTTPException(status_code=400, detail="translator_id required")

    # Best-effort DSU verify refs
    for key in ("T_ref", "R_ref", "S_ref"):
        ref = body.get(key)
        if isinstance(ref, str):
            try:
                requests.post(f"{DSU_BASE}/verify", json={"artifact_ref": ref}, timeout=1.5)
            except Exception:
                pass

    # Persist
    if DB_ENGINE is not None:
        with DB_ENGINE.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO translators(translator_id, payload)
                    VALUES (:tid, :payload::jsonb)
                    ON CONFLICT (translator_id) DO UPDATE SET payload = EXCLUDED.payload
                    """
                ),
                {"tid": translator_id, "payload": json.dumps(body)},
            )

    publish_event("translator.created", body)
    return {"status": "created", "translator_id": translator_id}


@app.get("/translators")
def list_translators() -> List[Dict[str, Any]]:
    if DB_ENGINE is None:
        return []
    with DB_ENGINE.connect() as conn:
        rows = conn.execute(text("SELECT payload FROM translators ORDER BY translator_id"))
        return [r[0] for r in rows]


@app.get("/metrics")
def metrics() -> Response:
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.get("/healthz")
def healthz() -> Response:
    return Response(status_code=204)


