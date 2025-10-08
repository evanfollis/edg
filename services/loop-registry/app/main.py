from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, status, Response
import yaml
from collections import defaultdict, deque
import threading
import time
import json
import redis
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
g_breach = Gauge("gold_loop_breach_total", "Gold loop breaches", labelnames=("loop_id",), registry=REGISTRY)


# Load gold loops config
REPO_ROOT = Path(__file__).resolve().parents[3]
GOLD_PATH = REPO_ROOT / "loop-registry" / "gold_loops.yaml"
with GOLD_PATH.open("r", encoding="utf-8") as fh:
    GOLD_CFG = yaml.safe_load(fh)

# Rolling observations per loop_id for percentile windows
OBS: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=64))
EVENT_BUS_URL = os.getenv("EVENT_BUS_URL")
BREACHES: deque[Dict[str, Any]] = deque(maxlen=256)

# Governance freeze state
FREEZE_ACTIVE: bool = False
FREEZE_CATEGORIES: List[str] = []
CONSECUTIVE_GREENS: int = 0
THAW_REQUIRED: int = int(GOLD_CFG.get("defaults", {}).get("trust_region", {}).get("consecutive_greens", 5)) if isinstance(GOLD_CFG.get("defaults", {}), dict) else 5


def persist_observation(loop_id: str, value: float) -> None:
    if DB_ENGINE is None:
        return
    with DB_ENGINE.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS loop_observations(
                    loop_id TEXT NOT NULL,
                    ts TIMESTAMP DEFAULT NOW(),
                    value DOUBLE PRECISION NOT NULL
                )
                """
            )
        )
        conn.execute(
            text("INSERT INTO loop_observations(loop_id, value) VALUES (:lid, :val)"),
            {"lid": loop_id, "val": value},
        )


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


@app.post("/events/loop_run_completed")
def loop_run_completed(event: Dict[str, Any]) -> Dict[str, Any]:
    """Receive loop run results; update rolling obs and check gold loop bounds."""
    loop_id = event.get("loop_id")
    if not loop_id:
        return {"status": "ignored"}
    # Use log_fro if provided, else curvature_fro as scalar obs
    scalar = float(event.get("log_fro") or event.get("curvature_fro") or 0.0)
    OBS[loop_id].append(scalar)
    persist_observation(loop_id, scalar)

    # Check gold loop bounds
    for gl in GOLD_CFG.get("loops", []):
        if gl.get("id") != loop_id:
            continue
        bound = gl.get("bound", {})
        if bound.get("type") == "absolute":
            thr = float(bound.get("threshold", 0.0))
            if scalar > thr + 1e-15:
                g_breach.labels(loop_id=loop_id).inc()
                breach = {"loop_id": loop_id, "type": "absolute", "value": scalar, "threshold": thr}
                BREACHES.append(breach)
                persist_breach(breach)
                publish_event("goldloop.breach", breach)
                # Activate freeze per defaults
                activate_freeze()
                CONSECUTIVE_GREENS = 0
                return {"status": "breach", **breach}
        elif bound.get("type") == "percentile":
            window = int(bound.get("window_days", 5))
            pct = int(bound.get("percentile", 99))
            series = list(OBS[loop_id])[-window:]
            if len(series) > 0:
                import numpy as np
                val = float(np.percentile(series, pct))
                thr_bps = float(bound.get("threshold_bps", 0.0))
                if val > thr_bps + 1e-12:
                    g_breach.labels(loop_id=loop_id).inc()
                    breach = {"loop_id": loop_id, "type": "percentile", "value": val, "threshold_bps": thr_bps}
                    BREACHES.append(breach)
                    persist_breach(breach)
                    publish_event("goldloop.breach", breach)
                    activate_freeze()
                    CONSECUTIVE_GREENS = 0
                    return {"status": "breach", **breach}
        break
    # Green
    if FREEZE_ACTIVE:
        CONSECUTIVE_GREENS += 1
        if CONSECUTIVE_GREENS >= THAW_REQUIRED:
            deactivate_freeze()
    return {"status": "ok"}


def consume_loop_events_forever() -> None:
    if not EVENT_BUS_URL:
        return
    try:
        r = redis.from_url(EVENT_BUS_URL, decode_responses=True)
        group = "loop-registry"
        stream = "loop.run.completed"
        consumer = os.getenv("HOSTNAME", "lr-1")
        try:
            r.xgroup_create(stream, group, id="0-0", mkstream=True)
        except Exception:
            pass
        while True:
            resp = r.xreadgroup(group, consumer, streams={stream: ">"}, count=10, block=2000)
            for stream_name, messages in resp or []:
                for msg_id, data in messages:
                    try:
                        payload = json.loads(data.get("payload", "{}"))
                        loop_run_completed(payload)
                    finally:
                        r.xack(stream, group, msg_id)
    except Exception:
        # Background consumer should not crash the service; sleep and retry
        time.sleep(2.0)
        consume_loop_events_forever()


def start_consumer_thread() -> None:
    t = threading.Thread(target=consume_loop_events_forever, daemon=True)
    t.start()


start_consumer_thread()


def publish_event(stream: str, payload: Dict[str, Any]) -> None:
    if not EVENT_BUS_URL:
        return
    try:
        r = redis.from_url(EVENT_BUS_URL, decode_responses=True)
        r.xadd(stream, {"payload": json.dumps(payload)})
    except Exception:
        pass


def persist_breach(breach: Dict[str, Any]) -> None:
    if DB_ENGINE is None:
        return
    with DB_ENGINE.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS gold_breaches (
                    ts TIMESTAMP DEFAULT NOW(),
                    loop_id TEXT NOT NULL,
                    breach_type TEXT NOT NULL,
                    value DOUBLE PRECISION,
                    threshold DOUBLE PRECISION
                )
                """
            )
        )
        if breach.get("type") == "absolute":
            thr = float(breach.get("threshold", 0.0))
        else:
            thr = float(breach.get("threshold_bps", 0.0))
        conn.execute(
            text(
                "INSERT INTO gold_breaches(loop_id, breach_type, value, threshold) VALUES (:lid, :bt, :val, :thr)"
            ),
            {"lid": breach.get("loop_id"), "bt": breach.get("type"), "val": float(breach.get("value", 0.0)), "thr": thr},
        )


@app.get("/gold/breaches")
def list_breaches() -> List[Dict[str, Any]]:
    # Prefer DB if available
    if DB_ENGINE is not None:
        with DB_ENGINE.connect() as conn:
            rows = conn.execute(
                text("SELECT ts, loop_id, breach_type, value, threshold FROM gold_breaches ORDER BY ts DESC LIMIT 256")
            )
            return [
                {
                    "ts": str(r[0]),
                    "loop_id": r[1],
                    "type": r[2],
                    "value": r[3],
                    "threshold": r[4],
                }
                for r in rows
            ]
    return list(BREACHES)[::-1]


def activate_freeze() -> None:
    global FREEZE_ACTIVE, FREEZE_CATEGORIES
    FREEZE_ACTIVE = True
    defaults = GOLD_CFG.get("defaults", {}) if isinstance(GOLD_CFG.get("defaults", {}), dict) else {}
    enforcement = defaults.get("enforcement", {}) if isinstance(defaults.get("enforcement", {}), dict) else {}
    cats = enforcement.get("freeze_categories", ["K_space_updates", "transport_updates"]) if isinstance(enforcement.get("freeze_categories", []), list) else ["K_space_updates", "transport_updates"]
    FREEZE_CATEGORIES = cats


def deactivate_freeze() -> None:
    global FREEZE_ACTIVE, FREEZE_CATEGORIES, CONSECUTIVE_GREENS
    FREEZE_ACTIVE = False
    FREEZE_CATEGORIES = []
    CONSECUTIVE_GREENS = 0


@app.get("/governance/freeze_state")
def freeze_state() -> Dict[str, Any]:
    return {
        "active": FREEZE_ACTIVE,
        "categories": FREEZE_CATEGORIES,
        "consecutive_greens": CONSECUTIVE_GREENS,
        "thaw_required": THAW_REQUIRED,
    }


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


