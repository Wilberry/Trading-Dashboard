# TradeMeter statistical methodology — research specification

## Goal

Produce evidence-based, **horizon-specific** directional pressure for each instrument from the accumulated permitted datasets. Outputs must include category, directional bias, expected relevance duration, watch levels, invalidation, evidence, timestamp, sample size, input quality and uncertainty.

**A score of 72/100 is not a 72% probability of a winning trade.** Treat signal scores, directional-probability estimates and trade profitability as distinct measurements.

## Inputs

- Scheduled and unscheduled macroeconomic releases, surprises, revisions and interest rate expectations.
- Official statements and institutional research; X and Truth Social claims plus verification and novelty.
- Source reputation, corroboration, market attention and event transmission channels.
- Prices, volatility, liquidity, momentum and technical structure as features rather than the sole source of the TradeMeter output.
- Cross-asset rates, USD conditions, broader risk regime and correlations.
- Market positioning, funding, open interest, ETF/crypto flows and venue-specific measures when available.
- Historical event reactions, comparable market regimes and observed outcomes.

Avoid treating ten articles repeating one announcement as ten independent bullish signals.

## Three separate research horizons

| Horizon | Initial working research window | Typical considerations |
| --- | --- | --- |
| Short-term | 1–3 trading days | Breaking catalysts, recent economic surprises, reaction patterns, short-term volatility, session behavior |
| Mid-term | 2–6 weeks | Economic trends, persistent themes, changing policy expectations, positioning and trend structure |
| Long-term | 1–6 months+ | Policy cycles, growth/inflation regimes, structural flows and durable macro divergence |

Each horizon needs its own feature windows, fitting procedure, label definition and calibration. Every *actual signal* should show a concrete estimate, such as "Expected relevance 2–3 trading days." This duration represents current thesis relevance, not guaranteed continuous movement.

## Prototype modeling pipeline

1. Build an instrument/horizon feature vector using only information available by the signal time.
2. Validate source health; flag stale or missing inputs and prevent duplicated stories from inflating weight.
3. Identify current volatility/macro regime.
4. Query well-defined comparable historical observations with count, dates and selection criteria.
5. Estimate observed forward price distributions and path features, including maximum adverse and favorable excursions.
6. Combine trained/statistically evaluated evidence into a signed score and independently calibrated five-category output.
7. Generate duration and watch-level candidates from the historical distribution, volatility and market structure; produce explicit invalidation rules.
8. Record the entire versioned input/output/evidence bundle and compare subsequent outcomes later.

Initial numeric bands, coefficients and examples in the UX specification are **placeholders** until fitted and validated.

## Historical analysis and calibration standards

- Walk-forward temporal validation; purge/embargo overlapping labels where relevant.
- Evaluate separately by instrument, horizon, regime and period.
- Use historical release vintages and recorded first-availability timestamps; no look-ahead.
- Report sample size and selection bias; use confidence intervals where defensible.
- Compare to naive and simple model baselines, not just a persuasive explanatory narrative.
- Track observed directional hit rate, conditional return and volatility distributions, drawdowns, MAE/MFE, calibration errors if probabilistic outputs are shown.
- Where simulating trades, include spread, transaction costs and slippage. Directional agreement alone does not prove a profitable strategy.
- Recalibrate on a monitored schedule with drift, outlier and provider-failure checks.
- Under insufficient evidence, return **Insufficient data** or a clearly cautious neutral state, not invented certainty.

## Outcome recording

For every signal snapshot, keep price path and levels at signal creation, the fixed evaluation horizon, end-of-window outcome, possible early invalidation and changes in evidence. Record model revisions as new versions. Do not retroactively change original levels or duration in historical accuracy metrics.

## Explainability contract

For each displayed output expose, at least on expand:
- Which drivers moved the score and which disagree.
- The model/version and exact data cutoff.
- Missing sources and source reliability.
- Relevant supporting records and original links.
- Historical cohort count, outcome statistics, uncertainty and time periods.
- Why levels and expected relevance duration were selected.

A single ambiguous "Confidence 86%" must not stand in for calibration, source trust and research sufficiency.
