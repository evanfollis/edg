## Register a transport edge (Quant→PM)
POST /edges
```json
{
  "edge_id": "quant->pm@1.0.0",
  "src": "agent:quant",
  "dst": "agent:pm",
  "k_space_id": "K/v0",
  "edge_type": "linear",
  "U": {"shape":[768,64],"weights_ref":"sha256:...W","inverse_ref":"sha256:...Winv"},
  "factorization": {"method":"polar","R_ref":"sha256:...R","S_ref":"sha256:...S","residual":0.004},
  "unit_map": {"in":"zscore","out":"weights"},
  "diagnostics": {"kappa":212.0,"roundtrip":0.011,"rho":0.0},
  "signatures": ["dsu:HeadOfRisk:...","dsu:PolicyLead:..."]
}
```
---
## Register a transport edge with inline artifacts (base64)
POST /edges
```json
{
  "edge_id": "quant->pm@1.1.0",
  "src": "agent:quant",
  "dst": "agent:pm",
  "k_space_id": "K/v0",
  "edge_type": "linear",
  "U": {
    "shape": [64,64],
    "weights_content": "<base64-bytes>",
    "inverse_content": "<base64-bytes>"
  },
  "factorization": {
    "method": "polar",
    "R_content": "<base64-bytes>",
    "S_content": "<base64-bytes>",
    "residual": 0.004
  },
  "unit_map": {"in":"zscore","out":"weights"},
  "diagnostics": {"kappa":120.0,"roundtrip":0.011,"rho":0.0},
  "signatures": ["dsu:HeadOfRisk:dev","dsu:PolicyLead:dev"]
}
```
The registry will store the blobs in object storage, replace `*_content` with `*_ref` (sha256), DSU‑sign refs, and persist metadata.
---
## Run a loop
POST /run
```json
{
  "loop_id": "gamma_Quant_PM_identity",
  "state_ref": "sha256:x0",
  "edge_ids": ["quant->pm@1.0.0","pm->quant@1.0.0"]
}
```
---
## Typical holonomy result
```json
{
  "loop_id":"gamma_Quant_PM_identity",
  "H_ref":"sha256:...H",
  "curvature_fro":0.00007,
  "torsion_fro":0.00003,
  "closure_norm":0.00002,
  "edge_attribution":[["quant->pm@1.0.0",0.62],["pm->quant@1.0.0",0.38]],
  "segments":1,
  "dim":64,
  "timestamp":"2025-10-07T15:02:11Z"
}
```
---
## Presign artifact for download
POST /artifacts/presign
```json
{"artifact_ref": "sha256:..."}
```
Response:
```json
{"url": "https://minio/...", "expires_s": 900}
```
---