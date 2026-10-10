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
