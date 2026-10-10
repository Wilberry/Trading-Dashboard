# Development roadmap and acceptance criteria — v0.1

## Phase 0 — Confirm product and data feasibility

- Approve core vocabulary: Short-term, Mid-term, Long-term; explicit per-signal expected duration; levels and invalidation.
- Confirm initial instrument list and trading-day/calendar-day semantics for forex vs crypto.
- Evaluate compliant/licensed access to X, Truth Social, news, ING Economics, government releases and historical OHLC/forex/crypto markets.
- Define affordable data-retention and vendor-operating budgets.
- Prototype TradeMeter interaction and a reproducible historical research example before claiming model accuracy.
- Specify UX loading/stale/insufficient-data states.

**Deliverable:** reviewable product specification, feed feasibility matrix and interactive UX design.

## Phase 1 — First useful intelligence MVP

- Watchlist with liquid FX, XAUUSD, BTC and ETH instruments, quotes and source freshness.
- Dashboard using **Glance → Expand → Deep Dive**.
- TradeMeter with five categories and three *actual* horizon-specific model outputs, initially marked as a baseline/research model.
- Per-horizon bias, explicit expected duration, levels, invalidation, important catalysts and supporting evidence.
- First authorized social feed plus official announcements, licensed reporting and economic calendar.
- Persistent permitted raw observations, canonical event matching, history of signals, model metadata and outcomes.
- Economic releases with forecast/actual/previous and surprise interpretation.
- Basic alerts for significant events, bias shifts, invalidations and stale feeds.
- Authentication, access control, ingestion monitoring and recovery.

### MVP acceptance tests

1. **Horizon switch:** model output, signal category, duration and watch levels are horizon-specific; a frontend tab cannot just relabel the same result.
2. **Glanceability:** users can identify instrument, bias, expected duration and key levels within seconds without opening full articles.
3. **Traceability:** each signal includes model version, timestamp, input cutoff, evidence links, sample count and data status.
4. **Reproducibility:** a historical signal remains queryable unchanged after future model updates.
5. **Event deduplication:** repeated X/news reports of one announcement create one canonical event with many source citations.
6. **No invented accuracy:** sparse history, missing vendors or stale market data yield cautious/insufficient evidence states.
7. **Event explainability:** a relevant official or social report shows impacted assets, credibility/confirmation state and plausible market channels.
8. **Time correctness:** all outcomes use only historically observable data and preserve original data vintages and publication times.

## Phase 2 — Statistical depth

- Historical event-study explorer, forward-return distributions and time-to-invalidation statistics.
- Regime-based analysis, pressure-shift timelines and comparable condition cohorts.
- Out-of-sample model evaluation by asset and horizon; confidence intervals and drift monitoring.
- Higher quality duration estimation, level methodology and volatility-adjusted alerts.
- Research search for stored historical social/economic/market events.

## Phase 3 — Professional terminal

- Correlation, currency exposure, session and liquidity analytics.
- Crypto-specific derivatives, ETF flows and on-chain support where licensed.
- Trading journal, versioned trade ideas, personalized performance metrics.
- Custom layouts, more sophisticated alert rules and optional authenticated API access.
- Consider optional broker integration only with an explicit separate risk/security specification.

## Workstreams

1. UX and frontend.
2. Source licensing, connectors and event classification.
3. Persistence, data pipelines and observability.
4. Statistical research and validation.
5. Signal API, audit trail and permissions.
6. QA, security and operational readiness.

## Suggested first GitHub issues

- Define horizon policies, Forex vs crypto time units and duration copy.
- Vet vendors and licensing for X, Truth Social, institutional research and live market data.
- Define canonical event, evidence and raw observation schemas.
- Specify TradeMeter score/model contract and baseline validation.
- Design responsive glance/expand/deep-dive prototypes.
- Design append-only signal and trade-idea histories with outcome labeling.

This is a **proposed roadmap**; dates, owners and vendor commitments are undecided.
