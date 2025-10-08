import json
from pathlib import Path

from jsonschema import validate


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "contracts" / "schemas"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_transport_edge_fixture_validates():
    schema = load(SCHEMAS / "transport_edge.schema.json")
    fixture = load(ROOT / "fixtures" / "edges" / "quant_pm_linear.json")
    validate(instance=fixture, schema=schema)


def test_loop_fixture_validates():
    schema = load(SCHEMAS / "loop.schema.json")
    fixture = load(ROOT / "fixtures" / "loops" / "gamma_Quant_PM_identity.json")
    validate(instance=fixture, schema=schema)


def test_holonomy_result_example_validates():
    schema = load(SCHEMAS / "holonomy_result.schema.json")
    example = {
        "loop_id": "gamma_Quant_PM_identity",
        "H_ref": "sha256:H",
        "curvature_fro": 0.0,
        "torsion_fro": 0.0,
        "closure_norm": 0.0,
        "edge_attribution": [["quant->pm@1.0.0", 0.5], ["pm->quant@1.0.0", 0.5]],
        "segments": 1,
        "dim": 64,
        "timestamp": "2025-10-07T15:02:11Z",
    }
    validate(instance=example, schema=schema)


def test_translator_preview_validates():
    schema = load(SCHEMAS / "translator_Tij.schemas.json")
    preview = {
        "translator_id": "sha256:T",
        "agent_i": "agent:quant",
        "agent_j": "agent:pm",
        "k_space_id": "K/v0",
        "T_ref": "sha256:T",
        "R_ref": "sha256:R",
        "S_ref": "sha256:S",
        "factorization": {"method": "polar"},
        "diagnostics": {
            "kappa": 50.0,
            "rho": 0.005,
            "roundtrip": 0.012,
            "unit_map": {},
            "regime_tag": "default",
        },
        "signatures": ["dsu:dev"],
    }
    validate(instance=preview, schema=schema)


