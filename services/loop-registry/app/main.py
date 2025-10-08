from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel
from jsonschema import validate, ValidationError
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
    g_loops.set(len(LOOP_STORE))
    return {"status": "created", "loop_id": loop_id}


@app.get("/loops")
def list_loops() -> List[Dict[str, Any]]:
    return list(LOOP_STORE.values())


@app.get("/loops/{loop_id}")
def get_loop(loop_id: str) -> Dict[str, Any]:
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


