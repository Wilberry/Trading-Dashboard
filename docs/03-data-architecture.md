# Data architecture, historical storage and governance — v0.1

## Central principle

**All available, permitted data should be retained for future research**, whether it appears on the dashboard today or not. Retain raw source observations when licensed, structured events, transformed features, model decisions, versions, trade ideas, and realized outcomes. "Store everything" is subject to copyright, provider API terms, deletion rules, privacy, storage cost and data minimization. When storing full text is prohibited, persist approved metadata, durable identifiers, hashes, excerpts or source references instead.

## End-to-end pipeline

~~~text
X / Truth Social / institutional research / official releases
             / market data / crypto / economic calendar
                                |
                     SOURCE CONNECTORS
                                |
                     DURABLE INGESTION QUEUE
                                |
              RAW-PERMITTED ARCHIVE + PROVENANCE
                                |
                VALIDATION / NORMALIZATION
                                |
            CANONICAL EVENTS / ENTITY RESOLUTION
                                |
         RELEVANCE + SOURCE QUALITY + DEDUPLICATION
                                |
              HISTORICAL FEATURE STORE / EVENT STUDY
                                |
            SHORT / MID / LONG STATISTICAL MODELS
                                |
     VERSIONED TRADEMETER + BIAS + DURATION + LEVELS
                                |
                   DASHBOARD / ALERTS / API
                                |
                 OUTCOME LABELS + MODEL AUDITS
~~~

## Required data categories

1. **Provenance:** provider/source, original IDs and URLs, author, trust classification, publication/first-observed/ingestion times, content hash, license/retention policy, raw pointer, corrections.
2. **Market data:** instrument/venue, tick or quote if licensed, OHLCV where available, spread, session, intervals, adjustment metadata, missing-bar/quality flags.
3. **Economic data:** calendar event, economic indicator, country, actual/consensus/prior, surprise, revisions, *point-in-time vintages*, rate decisions and speeches.
4. **Social and news:** authorized X posts, Truth Social posts, news reporting, ING Economics and other institutional commentary where permitted, topic/entity tags, user engagement when available, signal/stance classification, asset mappings.
5. **Macro and cross-market:** yields, FX rate differentials, DXY and other indexes, volatility and market regime, central-bank expectations, cross-asset relationships.
6. **Crypto:** funding, open interest, liquidations, exchange flows, ETF data, stablecoins and on-chain observations as licensing allows.
7. **Intelligence:** derived features, relevance/credibility values, horizon-specific aggregate pressure, bias, levels, explicit expected duration, driver weights, uncertainty, model and dataset versions, citation list.
8. **Trade ideas and outcomes:** creation-time thesis, instrument, levels, rationale, time horizon, revisions, triggers and timestamped realized price path, expiry and outcome.
9. **User data and operational state:** watchlists, alerts, preferences, account access, queue retries, feed health, ingestion failures and audit logs.

## Proposed technology boundaries (not yet approved)

- **PostgreSQL:** normalized assets, economic events, social/news metadata, sources, users, evidence joins, trade ideas, immutable signal metadata.
- **Partitioned PostgreSQL / TimescaleDB:** high-volume candles, feature snapshots, signal timelines and outcome series.
- **S3-compatible object storage:** permissible immutable original payloads and licensed historical backfill archives.
- **Queue/stream worker:** source processing, enrichment, deduplication and backfill.
- **Redis:** transient caching/rate limits only; never sole copy of research history.
- **Search index:** optional later for querying events and original text where rights permit.

## Candidate data relationships

- data_sources 1→many raw_observations
- raw_observations many↔many canonical_events
- canonical_events many↔many instruments
- instruments 1→many market_bars, feature_snapshots, signal_snapshots and trade_ideas
- signal_snapshots many↔many evidence_items
- signal_snapshots 1→many outcome_labels
- trade_ideas 1→many idea_revisions

## Required immutable signal fields

~~~text
signal_id
instrument_id
as_of_utc
horizon              # short | mid | long
pressure_score
pressure_category    # strong_sell | sell | neutral | buy | strong_buy
directional_bias
expected_valid_from
expected_valid_to
support_levels[]
resistance_levels[]
invalidation_conditions[]
catalysts[]
driver_contributions[]
historical_cohort_id
sample_size
quality_flags[]
model_version
feature_version
input_cutoff_utc
source_evidence_ids[]
created_at
supersedes_signal_id
~~~

A signal is appended, never silently overwritten. A recalibration publishes a new model version; retrospective restatements must remain distinguishable from historical real-time predictions.

## Data correctness and trust

- Store UTC for all normalized timestamps; display trader timezone.
- Distinguish posted/published, first observed, ingested, corrected and retracted timestamps.
- Archive original economic release vintages; using today's revised values in a past backtest creates look-ahead bias.
- Deduplicate ingestion through provider IDs, canonical event IDs and hashes without erasing separate evidence.
- Join only information known at the historical cutoff when producing or backtesting signals.
- Preserve exactly which model/inputs generated each score and which subsequent market outcome occurred.
- Handle expired licenses and deletion requests with lawful retention expiry and redaction pipelines.
- Isolate personal portfolios/watches by user; encrypt data and avoid secrets in repository.
