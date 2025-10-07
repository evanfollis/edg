# Observability

## Metrics (Prometheus)
- holonomy_curvature_fro{loop_id}
- holonomy_torsion_fro{loop_id}
- holonomy_closure_norm{loop_id}
- edge_kappa{edge_id}, edge_roundtrip{edge_id}, edge_rho{edge_id}
- gold_loop_breach_total{loop_id}
- lensflow_step_loss
- residual_norm{pair}

## Traces (OpenTelemetry)
- TraceID flows: PM proposal → required loops → holonomy calc → risk gate
- Span attributes: edge_id, dsu_ids, dataset_hashes, code_digest

## Logs
- Structured JSON. Always include: artifact_ref, dsu_signatures, κ/τ/ρ, units, env versions.
