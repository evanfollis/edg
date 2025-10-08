import json
import os

import requests

BASE = "http://localhost"
TR = f"{BASE}:{os.getenv('TRANSPORT_REGISTRY_PORT','7001')}"
HE = f"{BASE}:{os.getenv('HOLONOMY_ENGINE_PORT','7002')}"
LR = f"{BASE}:{os.getenv('LOOP_REGISTRY_PORT','7003')}"
RS = f"{BASE}:{os.getenv('RESIDUAL_SERVICE_PORT','7004')}"

def post(url, payload):
  r = requests.post(url, json=payload, timeout=30)
  r.raise_for_status()
  return r.json() if r.content else {}

def main():
  # Register a simple Quant->PM linear edge
  with open("fixtures/edges/quant_pm_linear.json") as f:
    edge = json.load(f)
  post(f"{TR}/edges", edge)

  # Register identity loop
  with open("fixtures/loops/gamma_Quant_PM_identity.json") as f:
    loop = json.load(f)
  post(f"{LR}/loops", loop)

  # Run loop
  res = post(f"{HE}/run", {
    "loop_id": loop["loop_id"],
    "state_ref": "sha256:x0",
    "edge_ids": loop["edges"]
  })
  print("Holonomy:", res)

  # Residual example
  res2 = post(f"{RS}/residuals", {
    "agent_i":"agent:quant","agent_j":"agent:pm",
    "evidence_refs":["sha256:e1","sha256:e2"],
    "k_space_id":"K/v0","factorization_method":"polar"
  })
  print("Residual:", res2)

if __name__ == "__main__":
  main()
