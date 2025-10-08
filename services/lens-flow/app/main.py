from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel


class StepTargets(BaseModel):
    minimize_loop_loss: Optional[bool] = True
    preserve_modes: Optional[List[str]] = None
    report_omegaPi: Optional[bool] = True


class RegimeScope(BaseModel):
    train_tags: Optional[List[str]] = None
    validate_tags: Optional[List[str]] = None


class Constraints(BaseModel):
    step_caps: Optional[Dict[str, float]] = None
    nonlinear_parsimony: Optional[bool] = True
    omegaPi_penalty_weight: Optional[float] = 1.0


class StepRequest(BaseModel):
    targets: StepTargets
    constraints: Constraints
    regime_scope: Optional[RegimeScope] = None


app = FastAPI(title="Lens-Flow", version="1.1.0")


@app.post("/step")
def step(req: StepRequest) -> Dict[str, Any]:
    return {
        "status": "accepted",
        "loop_loss_delta": -0.001,
        "omegaPi_norm_pre": 1.0,
        "omegaPi_norm_post": 0.9,
        "notes": "mock step applied",
    }


