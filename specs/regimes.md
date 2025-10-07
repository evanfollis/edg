# Regime Tags (v1.0)

Allowed tags:
- low_vol: realized vol in bottom tertile by 60d lookback
- high_vol: realized vol in top tertile by 60d lookback
- liquidity_stress: ADV/Spread metrics exceed stress thresholds
- rates_move: 10y move > X bps in 5d
- fx_basis: CIP basis > Y bps
- earnings: within ±5d of earnings window for basket
- macro_event: CPI/Fed/ECB event window

Emit via holonomy-engine on `/run` completion. Lens-Flow must scope train/validate to chosen tags.
