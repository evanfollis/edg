# 𝒦/v0 Feature Ordering (v1.0)
Dimensionality: 768

> This ordering MUST be stable. Any change is Tier-1 (requires bridge ϕ).

1–64: factor_exposures.core_v3   (value, momentum, quality, size, low_vol, carry…)
65–96: sector_onehots.gics_v2
97–128: risk_model.params        (beta, idio_var, corr_pcs_1..n)
129–192: macro_drivers           (rates_1d/5d/20d, inflation_surprise, fx_basket…)
193–384: news_embeddings         (sentence-transformer vX hash: abc123)
385–512: accounting_ratios       (roa, roe, margins, accruals… normalized)
513–640: pm_constraints_shadow   (leverage, turnover, cons caps…)
641–704: execution_costs         (slippage_est, spread, adv_pct bands…)
705–768: reserved                (expansion headroom)

Normalization: z-score per feature over rolling 2y; persist window hash.
