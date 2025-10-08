from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, Response
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST


app = FastAPI(title="Dashboard API", version="0.1.0")

REGISTRY = CollectorRegistry()
g_health = Gauge("dashboard_health", "Health status (1 ok)", registry=REGISTRY)


@app.get("/metrics/health")
def metrics_health() -> Dict[str, Any]:
    g_health.set(1)
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


