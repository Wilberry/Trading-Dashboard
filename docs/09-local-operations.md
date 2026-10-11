# Running the demo and authorized-data research mode

> Application status: local research prototype. This is not a public hosted financial signal service. Its scoring method and duration/level methodology are unvalidated.

## Default demo

Run `python app.py` and open http://127.0.0.1:8765. The default mode is **demo**, stored separately in `data/trading_demo.sqlite3`. All prices, events and TradeMeter signals are simulated. You can create research ideas and price alert rules locally, but alerts do not execute automatically.

## Authorized-data mode

Run in a trusted local shell:

```bash
export TRADING_DATA_MODE=live
export TRADING_INGEST_TOKEN="replace-with-a-long-random-secret"
python app.py
```

The server uses a distinct database `data/trading_live.sqlite3`. It **does not generate synthetic data**, and it **does not fetch market data or social posts automatically**.

Until enough authorized records are imported, TradeMeter shows **Unavailable / Insufficient data**, not a fabricated Buy/Sell.

**The prototype is not secure for internet exposure.** The browser is read-only in live mode because personal-account authentication is not implemented. Keep the default 127.0.0.1 binding.

## Authorized headline collection (RSS/Atom)

The project has a metadata-only feed connector, not a crawler of full copyrighted news articles.

- Review `config/feeds.example.json` and each source's use and retention terms.
- In a second terminal with the same `TRADING_INGEST_TOKEN`, preview entries using `python -m connectors.rss --config config/feeds.example.json --dry-run`.
- Import metadata using `python -m connectors.rss --config config/feeds.example.json`.
- Re-running the import is idempotent by `(source, external_id)`.
- Canonical event keys can combine reports from several approved providers without multiplying evidence.
- Imported headlines have **no automatically inferred directional impact**. Users see source metadata; statistical signals require separate, authorized and validated asset relevance inputs.

One example source is the Federal Reserve's published press-release RSS feed. The code uses HTTPS and retains source URLs and publication/observed timestamps where available.

## Authorized event API

```bash
curl -X POST http://127.0.0.1:8765/api/ingest \
  -H "Content-Type: application/json" \
  -H "X-Ingest-Token: $TRADING_INGEST_TOKEN" \
  -d '{
    "source":"licensed-feed",
    "external_id":"release-123",
    "title":"Authorized market development",
    "rights":"metadata-only",
    "url":"https://example.org/original",
    "category":"official",
    "timestamp":"2026-10-10T14:30:00+00:00",
    "event_key":"canonical-development-123",
    "impacts":{}
  }'
```

`impacts` is deliberately empty for unclassified events. Only supply explicit directional annotations when sourced and quality controlled; such annotations feed the *uncalibrated* baseline model, not a validated probability of profitable trading.

## Authorized closing-price API

```bash
curl -X POST http://127.0.0.1:8765/api/bars \
  -H "Content-Type: application/json" \
  -H "X-Ingest-Token: $TRADING_INGEST_TOKEN" \
  -d '{
    "symbol":"EURUSD",
    "timestamp":"2026-10-10T14:30:00+00:00",
    "close":1.1685,
    "source":"licensed-price-provider",
    "rights":"licensed"
  }'
```

The endpoint checks positive finite prices, authorized source, timestamp with timezone and source rights, and writes an auditable raw market payload with the close. A production-ready candle model with OHLCV, revisions and provider-contract enforcement is not yet implemented.

## Historical event studies

`GET /api/study?symbol=EURUSD&horizon=short` returns observed outcomes after historical events and sample sizes, using the first subsequent recorded close and a specified number of future stored bars. Duplicate canonical events count once. Outcomes not observable before the current as-of cutoff are excluded. This is *descriptive research*, **not** a calibrated forecast or controlled comparison to the current regime.

## Data correctness rules

- Demo and authorized records are filtered independently and use separate default database paths.
- Event and bar timezones must be explicit. Future-dated observations are rejected.
- Every signal version remains stored; fresh data leads to new append-only snapshots.
- Short-term requires at least 6 closing bars; mid-term at least 20; long-term at least 60, plus enough deduplicated relevant evidence.
- Insufficient historical evidence is shown as unavailable. Expected duration remains **Not estimated** in that state.
- The baseline uses rough factor decay and close-based range proxies; neither the weighting nor the stated durations have been validated.

## Run tests

```bash
python -m py_compile app.py research.py connectors/rss.py
python -m unittest discover -s tests -v
node --check web/app.js
```

If GitHub Actions jobs fail without any steps being scheduled (no runner assigned), inspect the repo's Actions and billing/runner settings. That failure mode is **not evidence of a failed unit test**.
