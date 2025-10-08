from __future__ import annotations

import json
from pathlib import Path
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec

from starlette.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]


def load_app(file_path: Path):
    loader = SourceFileLoader("_app_module", str(file_path))
    spec = spec_from_loader(loader.name, loader)
    assert spec is not None
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module.app


def test_transport_registry_register_edge():
    app = load_app(ROOT / "services" / "transport-registry" / "app" / "main.py")
    client = TestClient(app)
    edge = json.loads((ROOT / "fixtures" / "edges" / "quant_pm_linear.json").read_text())
    r = client.post("/edges", json=edge)
    assert r.status_code == 201
    r2 = client.get(f"/edges/{edge['edge_id']}")
    assert r2.status_code == 200


def test_loop_registry_register_loop_and_breach_state():
    app = load_app(ROOT / "services" / "loop-registry" / "app" / "main.py")
    client = TestClient(app)
    loop = json.loads((ROOT / "fixtures" / "loops" / "gamma_Quant_PM_identity.json").read_text())
    r = client.post("/loops", json=loop)
    assert r.status_code == 201
    # Simulate event ingestion with small value
    evt = {
        "loop_id": loop["loop_id"],
        "curvature_fro": 0.0,
        "timestamp": "2025-10-07T15:02:11Z",
    }
    r2 = client.post("/events/loop_run_completed", json=evt)
    assert r2.status_code == 200
    # Freeze state endpoint should exist
    r3 = client.get("/governance/freeze_state")
    assert r3.status_code == 200


def test_holonomy_engine_run_identity():
    app = load_app(ROOT / "services" / "holonomy-engine" / "app" / "main.py")
    client = TestClient(app)
    payload = {
        "loop_id": "gamma_Quant_PM_identity",
        "state_ref": "sha256:x0",
        "edge_ids": ["quant->pm@1.0.0", "pm->quant@1.0.0"],
    }
    r = client.post("/run", json=payload)
    assert r.status_code == 200
    data = r.json()
    for key in ("loop_id", "curvature_fro", "torsion_fro", "closure_norm", "segments", "dim", "timestamp"):
        assert key in data


def test_residual_service_residuals():
    app = load_app(ROOT / "services" / "residual-service" / "app" / "main.py")
    client = TestClient(app)
    payload = {
        "agent_i": "agent:quant",
        "agent_j": "agent:pm",
        "evidence_refs": ["sha256:e1", "sha256:e2"],
        "k_space_id": "K/v0",
        "factorization_method": "polar",
    }
    r = client.post("/residuals", json=payload)
    assert r.status_code == 200
    data = r.json()
    for key in ("translator_ref", "Rij_ref", "Sij_ref", "diagnostics"):
        assert key in data


