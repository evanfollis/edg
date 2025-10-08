from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel


class SignRequest(BaseModel):
    artifact_ref: str
    tier: str


class VerifyRequest(BaseModel):
    artifact_ref: str


app = FastAPI(title="DSU Signer", version="1.0.0")


@app.post("/sign")
def sign(req: SignRequest) -> Dict[str, Any]:
    return {"artifact_ref": req.artifact_ref, "signatures": ["dsu:dev:signature"], "tier": req.tier}


@app.post("/verify")
def verify(req: VerifyRequest) -> Dict[str, Any]:
    return {"artifact_ref": req.artifact_ref, "quorum_met": True}


