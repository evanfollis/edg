# Fixtures

- `edges/quant_pm_linear.json` — linear Uₑ with polar factorization (green κ/τ).
- `edges/nonlinear_example.json` — declares nonlinear penalties (or waiver stub).
- `loops/gamma_Quant_PM_identity.json` — identity loop def.
- `gold/pcp_synth.csv` — synthetic options chain to exercise PCP (1bp bound).
- `gold/cip_synth.csv` — synthetic FX & rates to exercise CIP (2bp bound).

Use `make seed` to load fixtures, register edges, and run loops once. Results land in `ledger/`.
