from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel
from jsonschema import validate, ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST


REPO_ROOT = Path(__file__).resolve().parents[3]
LOOP_SCHEMA_PATH = REPO_ROOT / "contracts" / "schemas" / "loop.schema.json"


def load_loop_schema() -> Dict[str, Any]:
    with LOOP_SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


loop_schema = load_loop_schema()


class LoopBody(BaseModel):
    __root__: Dict[str, Any]

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:  # type: ignore[override]
        return self.__root__


app = FastAPI(title="Loop Registry", version="1.0.0")


LOOP_STORE: Dict[str, Dict[str, Any]] = {}


# Metrics / health
REGISTRY = CollectorRegistry()
g_loops = Gauge("loop_registry_total", "Count of loops registered", registry=REGISTRY)


@app.post("/loops", status_code=status.HTTP_201_CREATED)
def create_or_update_loop(body: LoopBody) -> Dict[str, Any]:
    payload = body.dict()
    try:
        validate(instance=payload, schema=loop_schema)
    except ValidationError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "IV.SCHEMA.VALIDATION",
                    "message": "Loop schema validation failed.",
                    "detail": {"path": list(ve.absolute_path), "msg": ve.message},
                }
            },
        ) from ve

    loop_id = payload.get("loop_id")
    if not isinstance(loop_id, str) or len(loop_id) == 0:
        raise HTTPException(status_code=400, detail="loop_id is required")
    LOOP_STORE[loop_id] = payload
    db_upsert_loop(loop_id, payload)
    g_loops.set(len(LOOP_STORE))
    return {"status": "created", "loop_id": loop_id}


@app.get("/loops")
def list_loops() -> List[Dict[str, Any]]:
    rows = db_list_loops()
    if rows is not None:
        return rows
    return list(LOOP_STORE.values())


@app.get("/loops/{loop_id}")
def get_loop(loop_id: str) -> Dict[str, Any]:
    row = db_get_loop(loop_id)
    if row is not None:
        return row
    if loop_id not in LOOP_STORE:
        raise HTTPException(status_code=404, detail="loop not found")
    return LOOP_STORE[loop_id]


@app.get("/metrics")
def metrics() -> Response:
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.get("/healthz")
def healthz() -> Response:
    return Response(status_code=204)


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
                CREATE TABLE IF NOT EXISTS loops (
                    loop_id TEXT PRIMARY KEY,
                    payload JSONB NOT NULL
                )
            """))
        return engine
    except Exception:
        return None


DB_ENGINE = get_engine()


def db_upsert_loop(loop_id: str, payload: Dict[str, Any]) -> None:
    if DB_ENGINE is None:
        return
    import json as pyjson
    with DB_ENGINE.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO loops(loop_id, payload)
                VALUES (:loop_id, :payload::jsonb)
                ON CONFLICT (loop_id) DO UPDATE SET payload = EXCLUDED.payload
                """
            ),
            {"loop_id": loop_id, "payload": pyjson.dumps(payload)},
        )


def db_list_loops() -> Optional[List[Dict[str, Any]]]:
    if DB_ENGINE is None:
        return None
    with DB_ENGINE.connect() as conn:
        rows = conn.execute(text("SELECT payload FROM loops ORDER BY loop_id"))
        return [r[0] for r in rows]


def db_get_loop(loop_id: str) -> Optional[Dict[str, Any]]:
    if DB_ENGINE is None:
        return None
    with DB_ENGINE.connect() as conn:
        row = conn.execute(text("SELECT payload FROM loops WHERE loop_id=:lid"), {"lid": loop_id}).fetchone()
        return row[0] if row else None


