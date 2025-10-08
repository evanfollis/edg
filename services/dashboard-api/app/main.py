from __future__ import annotations

from typing import Any, Dict, List

import os
import requests
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


LR_BASE = os.getenv("LOOP_REGISTRY_BASE", f"http://localhost:{os.getenv('LOOP_REGISTRY_PORT','7003')}")


@app.get("/gold/breaches")
def gold_breaches() -> List[Dict[str, Any]]:
    try:
        r = requests.get(f"{LR_BASE}/gold/breaches", timeout=2.0)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


@app.get("/healthz")
def healthz() -> Response:
    return Response(status_code=204)


