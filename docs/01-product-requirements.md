# Product requirements — v0.1

## Goal

Enable traders to answer in seconds: What happened? What markets could it affect? What do our horizon-specific evidence and historical statistics indicate? What levels and catalysts matter, and what would invalidate the view?

## Users and markets

Initial coverage: liquid Forex pairs such as EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD and NZDUSD; gold (XAUUSD); Bitcoin and Ethereum; expand to broader crypto markets in stages. Support active and swing traders. Forex market hours and crypto 24/7 availability must be handled differently.

## Functional requirements

### Market intelligence
- Watchlist: quote, change, freshness, relevant alerts and clear pressure/bias summary.
- News sources: official economic and central-bank releases, licensed market news, institutional commentary including ING Economics where permitted.
- Social sources: X and Truth Social are first-class, independent feed inputs. Detect impactful official accounts and statements; distinguish claims and opinions from confirmed facts.
- Normalize, link, deduplicate and verify multiple reports of the same real-world event; preserve source links and timestamps.
- Economic calendar: scheduled releases, prior/forecast/actual, surprise and revisions; localized times and affected instruments.
- Explain likely transmission channels, uncertainty, conflicting interpretations, and observable market reaction.

### Directional research
- TradeMeter: polished semicircular meter with red sell-side glow, neutral lighting, green buy-side glow, and five states (Strong Sell / Sell / Neutral / Buy / Strong Buy).
- Select Short-term / Mid-term / Long-term; compute separately for each horizon using historical, fundamental, social, macro, price, positioning and other available evidence.
- Show **explicit expected duration** for each directional bias, not just a timeframe label.
- Show support, resistance, levels to watch, invalidation, relevant upcoming catalysts, timestamp, sample size and data freshness.
- Maintain versioned pressure/bias change history and compare subsequent outcomes.
- Historical event studies, comparable market regimes, conditional distributions and research explorer (advanced stage).
- Alert users to market-moving events, material changes in pressure/bias, levels breached and upcoming catalysts.

### Additional trading context
Market regime, currency strength, yields/rates, sessions, volatility, correlation and portfolio USD exposure; crypto derivatives, funding, liquidations, ETF flows and permitted on-chain data as coverage expands. Trade idea recording, change log, expiry and outcome evaluation; optional journal and portfolio analytics later.

## Interface requirements

Default screen is high signal-to-noise. Each card uses **Glance → Expand → Deep Dive**; raw news and detailed evidence remain behind disclosure, with easy access to source material and historical research. Desktop-first but responsive; text labels must supplement color.

## Nonfunctional requirements

Point-in-time correctness and reproducibility; provider licensing and retention rules; asynchronous queues and backfill; source health, outage handling and freshness; audit logs, tenant isolation, encryption, least-privilege access, watchlist privacy, reasonable latency and accessible interaction.

## Not initially in scope

Live broker order execution; promised profitability; sophisticated institutional order-flow estimates without actual data; unsupported blanket claims of forecast accuracy; every blockchain or market-data venue.

## Terminology

- **TradeMeter pressure:** aggregated statistical evidence score, not literal volume of buys vs sells.
- **Directional bias:** current evidence-leaning orientation for a named horizon.
- **Expected duration:** estimated time window for the bias to remain relevant under current conditions, **not** a prediction of uninterrupted price motion.
- **Invalidation:** explicit price or event condition that negates or weakens the original thesis.
- **Confidence:** never ambiguous; distinguish source reliability, evidence agreement, sample size and calibrated model probability.
