from __future__ import annotations

import json
import os
import json as pyjson
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from jsonschema import validate, ValidationError
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST
import boto3
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import requests


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
    # Best-effort object store existence check and DSU sign
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=os.getenv("OBJECT_STORE_ENDPOINT", "http://localhost:9000"),
            aws_access_key_id=os.getenv("OBJECT_STORE_ACCESS_KEY", "minioadmin"),
            aws_secret_access_key=os.getenv("OBJECT_STORE_SECRET_KEY", "minioadmin"),
        )
        bucket = os.getenv("OBJECT_STORE_BUCKET", "edg-artifacts")
        try:
            s3.head_bucket(Bucket=bucket)
        except Exception:
            s3.create_bucket(Bucket=bucket)
        refs = []
        U = payload.get("U", {})
        if "weights_ref" in U:
            refs.append(U["weights_ref"])
        if "inverse_ref" in U:
            refs.append(U["inverse_ref"])
        fac = payload.get("factorization", {})
        if "R_ref" in fac:
            refs.append(fac["R_ref"])
        if "S_ref" in fac:
            refs.append(fac["S_ref"])
        verifications: Dict[str, Any] = {}
        for ref in refs:
            if isinstance(ref, str) and ref.startswith("sha256:"):
                key = ref.split(":", 1)[1]
                try:
                    s3.head_object(Bucket=bucket, Key=key)
                    exists = True
                except Exception:
                    exists = False
                verifications[ref] = {"exists": exists}
        if verifications:
            payload.setdefault("object_store", {}).update({"bucket": bucket, "refs": verifications})
    except Exception:
        pass
    try:
        dsu_base = os.getenv("DSU_SIGNER_BASE", f"http://localhost:{os.getenv('DSU_SIGNER_PORT','7006')}")
        for ref, info in payload.get("object_store", {}).get("refs", {}).items():
            try:
                requests.post(f"{dsu_base}/sign", json={"artifact_ref": ref, "tier": "T2"}, timeout=1.5)
                info["dsu_signed"] = True
            except Exception:
                info["dsu_signed"] = False
    except Exception:
        pass

    # Persist to DB if configured
    db_upsert_edge(edge_id, payload)
    return {"status": "created", "edge_id": edge_id}


@app.get("/edges")
def list_edges() -> List[Dict[str, Any]]:
    # Prefer DB if available
    rows = db_list_edges()
    if rows is not None:
        return rows
    return list(EDGE_STORE.values())


@app.get("/edges/{edge_id}")
def get_edge(edge_id: str) -> Dict[str, Any]:
    row = db_get_edge(edge_id)
    if row is not None:
        # Attach DSU verification best-effort
        attach_dsu_verification(row)
        return row
    if edge_id not in EDGE_STORE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="edge not found")
    obj = EDGE_STORE[edge_id]
    attach_dsu_verification(obj)
    return obj


@app.get("/healthz")
def healthz() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/metrics")
def metrics() -> Response:
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


# ---- Persistence (Postgres) ----
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
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS transport_edges (
                    edge_id TEXT PRIMARY KEY,
                    payload JSONB NOT NULL
                )
            """))
        return engine
    except Exception:
        return None


DB_ENGINE = get_engine()


def db_upsert_edge(edge_id: str, payload: Dict[str, Any]) -> None:
    if DB_ENGINE is None:
        return
    with DB_ENGINE.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO transport_edges(edge_id, payload)
                VALUES (:edge_id, :payload::jsonb)
                ON CONFLICT (edge_id) DO UPDATE SET payload = EXCLUDED.payload
                """
            ),
            {"edge_id": edge_id, "payload": pyjson.dumps(payload)},
        )


def db_list_edges() -> Optional[List[Dict[str, Any]]]:
    if DB_ENGINE is None:
        return None
    with DB_ENGINE.connect() as conn:
        rows = conn.execute(text("SELECT payload FROM transport_edges ORDER BY edge_id"))
        return [r[0] for r in rows]


def db_get_edge(edge_id: str) -> Optional[Dict[str, Any]]:
    if DB_ENGINE is None:
        return None
    with DB_ENGINE.connect() as conn:
        row = conn.execute(text("SELECT payload FROM transport_edges WHERE edge_id=:eid"), {"eid": edge_id}).fetchone()
        return row[0] if row else None


def attach_dsu_verification(obj: Dict[str, Any]) -> None:
    dsu_base = os.getenv("DSU_SIGNER_BASE", f"http://localhost:{os.getenv('DSU_SIGNER_PORT','7006')}")
    # Verify available artifact refs (weights/inverse/factors) if present
    refs = []
    U = obj.get("U", {})
    if "weights_ref" in U:
        refs.append(U["weights_ref"])
    if "inverse_ref" in U:
        refs.append(U["inverse_ref"])
    fac = obj.get("factorization", {})
    if "R_ref" in fac:
        refs.append(fac["R_ref"])
    if "S_ref" in fac:
        refs.append(fac["S_ref"])
    verifications: Dict[str, Any] = {}
    for ref in refs:
        try:
            r = requests.post(f"{dsu_base}/verify", json={"artifact_ref": ref}, timeout=1.5)
            if r.status_code == 200:
                verifications[ref] = r.json()
        except Exception:
            verifications[ref] = {"quorum_met": False}
    if verifications:
        obj.setdefault("dsu_verification", verifications)


