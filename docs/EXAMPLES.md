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