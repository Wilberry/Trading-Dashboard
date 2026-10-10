# Decision log — 10 October 2026

This file distinguishes **agreed product intent** from **working engineering proposals**. Do not silently promote example thresholds, historical statistics or generated levels into empirically validated product decisions.

## Agreed product decisions

1. One-stop decision-support dashboard for forex pairs, XAUUSD, BTC, ETH and an expanding crypto market.
2. X and Truth Social are important first-class sources along with official data, institutional commentary, finance news, and economic releases — never a single-source architecture.
3. Historical **permitted** data is retained, not only the items visible on screen: raw observations, event classifications, normalized inputs, analyses, trade ideas, revisions, forecasts and measured outcomes.
4. Display high-value information first, followed by a dropdown to expand, then optional complete analysis and source references.
5. **Short-term**, **Mid-term**, **Long-term** are the official horizon names.
6. Every directional view includes an **explicit expected duration** (for example 2–3 trading days), important levels, invalidation conditions, catalysts and supporting reasons. Duration is a conditional research estimate, not guaranteed future movement.
7. The visual **TradeMeter** is a polished speedometer with direction-sensitive red/neutral/green inner lighting.
8. TradeMeter states are **Strong Sell, Sell, Neutral, Buy, Strong Buy**.
9. TradeMeter represents horizon-specific, **statistically aggregated evidence across all relevant data**; it is **not just technical analysis**. Each horizon has its own modeling and calibration.
10. Store historical snapshots of scores/biases and outcomes to enable assessment of how well the product has performed and improve calibration responsibly.
11. The UI should be trader-centric and avoid irrelevant noise, including unnecessary repeated news stories.

## Working proposals, not final decisions

- Research windows: Short-term 1–3 trading days; Mid-term 2–6 weeks; Long-term 1–6 months+. Individual estimated duration should be more specific when supported by evidence.
- A numeric 0–100 TradeMeter score, placeholder five-category bands and weighting methodology subject to empirical calibration.
- Backend stack: PostgreSQL with partitioning/TimescaleDB, object storage, worker queue, Redis, separate source connectors and versioned modeling.
- Roadmap phase boundaries and MVP acceptance checks.
- Level derivation may combine observed structure, liquidity/volatility statistics and historical distribution; validation method TBD.

## Open questions requiring approval

1. Final product brand/display name.
2. Exact horizon semantics and calendar for FX versus 24/7 crypto.
3. Initial list of supported pairs and crypto instruments.
4. Vendor access, costs and licenses for X, Truth Social, ING Economics, economic feeds and market history.
5. TradeMeter model family, factor groups, weighting, calibration metrics and acceptable minimum sample sizes.
6. How to express uncertainty without misleading win-probability language.
7. How to calculate duration, support/resistance, invalidation and action-triggered alerts consistently.
8. Retention schedules, international compliance, security expectations and infrastructure costs.
9. Desktop/mobile layout, alert delivery preferences and product pricing.

## Change management

Every substantial decision should have a date, rationale and impact on the specification. The model version, training data cutoff and feature snapshot must be traceable to each historical signal. Retrospective modifications cannot erase the original record.
