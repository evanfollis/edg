from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI


app = FastAPI(title="Dashboard API", version="0.1.0")


@app.get("/metrics/health")
def metrics_health() -> Dict[str, Any]:
    return {"status": "ok"}


