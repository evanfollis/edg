# Observability — v1.1

## Metrics (Prometheus)
- holonomy_curvature_fro{loop_id,regime_tag}
- holonomy_torsion_fro{loop_id,regime_tag}
- holonomy_closure_norm{loop_id,regime_tag}
- edge_kappa{edge_id}, edge_roundtrip{edge_id}, edge_rho{edge_id}
- residual_norm{agent_i,agent_j,regime_tag}
- translator_kappa{agent_i,agent_j}
- lensflow_step_loss{regime_tag}
- omegaPi_norm{agent,phase="pre|post",regime_tag}
- gold_loop_breach_total{loop_id}

## Traces (OpenTelemetry)
- Propagate: loop_id, regime_tag, edge_ids, dsu_ids.

## Logs
- Include: artifact_ref, dsu_signatures, κ/τ/ρ, units, **regime_tag**, code_digest.
