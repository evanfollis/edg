from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from jsonschema import validate, ValidationError


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


