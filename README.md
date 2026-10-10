# Trading Intelligence Dashboard

> Status: Product discovery and specification v0.1 — 10 October 2026  
> Coverage: Forex pairs, XAUUSD, Bitcoin, Ethereum, and expandable crypto markets.

An evidence-driven market intelligence terminal for active and swing traders. It gathers news, X, Truth Social, institutional research, economic releases, prices, macro and crypto market data; stores legally permissible history; connects events with affected assets; performs horizon-specific statistical analysis; and displays the essential conclusion before the details.

**Purpose:** Research and decision support, not automated execution or guaranteed trade outcomes.

## The product promise

A trader should know at a glance:
- What changed in the market?
- Which assets are affected?
- What does the TradeMeter indicate for **Short-term**, **Mid-term**, or **Long-term**?
- What is the **expected relevance duration** of the current directional bias?
- Which support, resistance, invalidation, and catalyst levels should be watched?
- What evidence and historical observations support the view?

## Six product principles

1. **Glance → Expand → Deep Dive.** No raw feed flooding the home screen.
2. **Horizon-specific models.** Selecting a different horizon recalculates the TradeMeter, direction, duration, and levels.
3. **Evidence-led TradeMeter.** Five outputs: Strong Sell, Sell, Neutral, Buy, Strong Buy. It reflects aggregated statistical evidence, not technical-analysis-only recommendations or literal order-flow pressure.
4. **Market memory.** Retain permitted raw observations, normalized events, source provenance, features, trade ideas, model snapshots, revisions and measured outcomes.
5. **Signal over noise.** Deduplicate related reporting, rank relevance, label unverified claims, surface meaningful changes.
6. **No false precision.** An expected duration is a conditional research window, not a guaranteed forecast. Report staleness, missing inputs and statistical limitations.

## Specification index

- [01 — Product requirements](docs/01-product-requirements.md)
- [02 — Dashboard UX and TradeMeter](docs/02-dashboard-ux-trademeter.md)
- [03 — Data architecture, persistence and governance](docs/03-data-architecture.md)
- [04 — Statistical methodology](docs/04-statistical-methodology.md)
- [05 — News and social intelligence](docs/05-intelligence-ingestion.md)
- [06 — MVP roadmap and acceptance criteria](docs/06-roadmap.md)
- [07 — Decision log](docs/07-decisions.md)

## Working horizon conventions

| Horizon | Research window | What must appear on screen |
| --- | --- | --- |
| Short-term | 1–3 trading days | Individual estimate, e.g. 2–3 trading days, plus levels and invalidation |
| Mid-term | 2–6 weeks | Specific expected duration, levels and invalidation |
| Long-term | 1–6 months+ | Specific expected duration, levels and invalidation |

The broad windows are **working conventions**, not hard-coded forecasts. Crypto's 24/7 schedule requires explicit calendar-day convention. All shown market figures in specs are fictional examples unless otherwise documented.

## Status

Initial documentation only. Vendor contracts, ingestion connectors, price data, statistical model validation and production code have **not** yet been implemented. Open design decisions are tracked in [the decision log](docs/07-decisions.md).
