# Meridian — Trading Intelligence Dashboard

> **Runnable research MVP (synthetic data only)** · October 2026

Trading Dashboard is an evidence-driven research terminal for Forex pairs, XAUUSD, Bitcoin and Ethereum. The initial application implements a dark responsive interface, five-state statistical TradeMeter, separate Short-term/Mid-term/Long-term models, explicit expected relevance durations, key support/resistance and invalidation levels, filtered event research, stored pressure history, saved trade ideas and saved price-alert rules.

**Not a live trading service.** All bundled price and news inputs are synthetic, the statistical model is not historically calibrated, and displayed Buy / Sell states are **not** actionable investment recommendations or probabilities of profit.

## Quick start

Requires Python 3.11+ and a browser. No pip packages or external services are required.

```bash
git clone https://github.com/Wilberry/Trading-Dashboard.git
cd Trading-Dashboard
python app.py
```

Open **http://127.0.0.1:8765/**. The app creates a local SQLite database (`data/trading.sqlite3`) on first startup and seeds deterministic demo candles and simulated market events. Leave the server running while you browse. Avoid exposing it to the public internet; it has no user authentication.

## Features

| Area | Implemented |
| --- | --- |
| Dashboard | Glance-first responsive layout, instrument selector, simulated price chart |
| TradeMeter | Polished semicircular meter with green/red adaptive glow and Strong Sell / Sell / Neutral / Buy / Strong Buy |
| Horizons | Separate statistical pressure calculations for Short-term, Mid-term, Long-term; explicit expected duration |
| Levels | Horizon-specific support/resistance and thesis invalidation |
| Intelligence | Event/feed storage and broad instrument impact annotations; demo source narratives |
| Database | Persistent candles, events, permitted raw payloads, signal/evidence history, trade ideas and alert rules |
| Research | Factor breakdowns and historical pressure snapshots |
| Journaling | Save trade idea thesis, horizon, reference entry, invalidation and target |
| Alerts | Save thresholds (no background price monitoring or notifications yet) |
| Tests | Python smoke tests and GitHub Actions lint/test workflow |

## Project layout

- `app.py` — dependency-free Python server, SQLite models, event ingestion and horizon-specific research.
- `web/index.html`, `web/styles.css`, `web/app.js` — responsive terminal and interactions.
- `tests/test_app.py` — smoke tests.
- `docs/` — original product requirements, UX, ingestion, statistics and roadmap, plus current implementation status.

## Run the checks

```bash
python -m unittest discover -s tests -v
python -m py_compile app.py
node --check web/app.js
```

Node is only needed for the optional JavaScript syntax check, not to run the application.

## Ingestion API

`GET /api/dashboard?symbol=EURUSD&horizon=short` returns the selected instrument, all horizon outputs, history, demo event feed, trade ideas and alert rules.

`POST /api/ideas` and `POST /api/alerts` save local user research. `POST /api/ingest` accepts an authorized event with `source`, `external_id`, `title`, `rights` (one of `licensed`, `authorized`, `public-domain`, `metadata-only`), optional `body`, `timestamp`, `category`, `event_key`, and an `impacts` object mapping instrument symbols to a directional numeric annotation between -1 and +1.

For administrator ingestion, set `TRADING_INGEST_TOKEN` in the environment and send the same value as the `X-Ingest-Token` HTTP header. Do not place credentials in Git.

The ingestion endpoint is a **research adapter**, not an automatic X/Truth Social scraper, real market-price provider or reliable sentiment-extraction model. Provider-specific connectors, licensing, queues and anti-abuse controls are not implemented.

## Research-data foundation (development branch)

An extended implementation is available on `feature/research-data-foundation`. This includes:

- Separate databases and query filtering for **synthetic demo** vs **authorized data**. Live mode starts empty instead of inventing market results.
- Append-only pressure signal refresh after new observations or the horizon-specific TTL.
- Point-in-time, descriptive event-study statistics (sample count, median, return quartiles, positive fraction), deduplicated by canonical event.
- Authorized, token-protected news and closing-price ingestion, with timestamp validation, rights metadata and original-source provenance.
- A manually configured, rights-aware **RSS/Atom metadata importer** with an official Federal Reserve feed example. X, Truth Social, institutional news and market-price providers still require agreements and integration.
- Live-mode browser is read-only pending real account authentication; synthetic risk/calendar content is hidden.
- Additional offline regression and HTTP API tests.

**Research caveat:** The current TradeMeter is still an uncalibrated baseline, not a prediction model. The stated durations are working display conventions rather than statistically calibrated validity windows. Historical event studies describe aggregate event reactions, not similarity-ranked projections.

See [authorized-data operations](docs/09-local-operations.md).

## What remains before a production release

1. Licensed/live sources for X, Truth Social, institutional commentary, economic calendars, broker/market quotes and historical backfill.
2. Independently verified statistical feature engineering, out-of-sample calibration, duration estimation and level selection. The current weights and model outputs are placeholders.
3. Secure authentication, user isolation, scalable time-series storage, source workers, audit and operational monitoring.
4. Reliable live alerts/notifications, trade-idea outcomes and advanced market regime and crypto derivatives analytics.
5. Browser/device accessibility QA, deployment, alert reliability tests, vendor/legal review and observability.

See [implementation status](docs/08-implementation-status.md), [product specification](docs/01-product-requirements.md), [TradeMeter requirements](docs/02-dashboard-ux-trademeter.md), [statistical methodology](docs/04-statistical-methodology.md), and [roadmap](docs/06-roadmap.md).

This project is for market research and decision support. It does not guarantee or promise profits.
