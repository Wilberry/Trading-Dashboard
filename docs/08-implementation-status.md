# Implementation status — research MVP

## Implemented

- Responsive instrument dashboard, markets, event feed, research lab, idea notebook, and alert rule page.
- TradeMeter with five pressure states and red/green color response, horizon selector and clear duration language.
- Distinct short/mid/long research calculations; individual directional views, levels and invalidation.
- Persistent SQLite historical market bars, events, raw/provenance, evidence, signal snapshots and manually saved trade ideas.
- Authorized admin API for ingesting licensed/authorized events; duplicated source IDs ignored.
- Research-history chart, data freshness and conspicuous unvalidated-demo labeling.
- Source code in `app.py` and `web/`; unit tests under `tests/`.

## Not production-ready

- **Live feeds not connected:** X, Truth Social, ING Economics, broker quotations, licensed news and economic calendars require provider approval/terms, credentials and ongoing workers.
- **TradeMeter not calibrated:** demo evidence weights and 0–100 thresholds are illustrative. It is not a prediction probability or validated strategy.
- **Expected duration** labels are working conventions rather than outcomes of historical duration model.
- **Price alerts** are stored but not monitored continuously; no notifications.
- **Security and scale:** local-use server; no authentication, tenancy, full access control, distributed processing, production database or deployment.
- **Trade outcomes** are not yet automatically labeled; journaling only stores initial thesis.
- No licensed historic backfill or out-of-sample statistical evaluation.

The goal is not to misleadingly represent synthetic evidence as actual market signals. See development roadmap and decision log.

## Research foundation extension (October 2026)

Implemented in `feature/research-data-foundation`:

- A distinct `TRADING_DATA_MODE=live` runtime and `data/trading_live.sqlite3` database; demo feed/bars do not contaminate authorized research.
- Clear **Unavailable / Not estimated** states when historical evidence or closing-bar coverage is insufficient.
- Append-only signal snapshots refreshed on new source inputs or horizon-specific freshness expiry.
- A descriptive point-in-time event study with historical sample-size gates and event-key deduplication; **not similarity ranking or a validated projected return**.
- Token-guarded authorized market-bar and source-event APIs with UTC timestamp checks, rights declarations, raw market payloads and source links.
- Metadata-only RSS/Atom adapter and official-source sample config (requires operator review of source terms, startup in authorized mode, no automatic sentiment inference).
- Research Lab event summaries, demo/live visual distinction, and no fictional upcoming-event panel in live mode.
- Additional offline/HTTP integration tests. Their CI execution remains unverified while GitHub-hosted jobs terminate without an assigned runner.

Still missing: approved X and Truth Social connectors, institutional research rights, automatically supplied live asset impact scoring, real-time forex/gold/crypto prices, economic calendar feeds, derived duration calibration, validated forward projection, source health monitors, authenticated user tenancy and deployed infrastructure. No real-money use should rely on current scoring.

For local operations see [09-local-operations](09-local-operations.md).
