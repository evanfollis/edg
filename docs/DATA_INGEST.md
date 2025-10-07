# Data Ingest (𝒦/v0)

- Feature set & ordering: see `specs/K_v0_features.md`
- Normalization: rolling 2y z-score (persist window hash, seeds)
- Unit maps: declare for each edge and maintain in artifacts
- Drift monitor: PSI > 0.2 → pause lens-flow, open Data QA
