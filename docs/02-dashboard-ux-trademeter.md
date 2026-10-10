# Dashboard UX and TradeMeter — design specification

## Information hierarchy

1. **Glance (default):** selected instrument, current quote, TradeMeter signal, selected horizon, directional bias, explicit expected duration, key levels, next important catalyst, freshness.
2. **Expand (dropdown):** factor contributions, supporting and conflicting evidence, event links, levels and reasons, score changes, historical sample count and data status.
3. **Deep Dive (full page):** event/source timeline, research cohorts and statistics, versioned signal snapshots, method and calibration details, citations, trade ideas and outcomes.

## TradeMeter brief

A refined semi-circular speedometer set inside a recessed, softly illuminated cove. Arc from left to right: **Strong Sell | Sell | Neutral | Buy | Strong Buy**. Red gradients intensify proportionally toward Strong Sell; restrained gray/amber at Neutral; green gradients toward Strong Buy. Animation is smooth, legible and accessible: never convey meaning through color alone.

The TradeMeter represents the **statistically aggregated interpretation of ALL available, relevant, properly weighted evidence**. It is **not** a generic technical-analysis buy/sell widget. Technical indicators can contribute, but macro, economic releases, X/Truth Social and news, sentiment, market structure, volatility, positioning, historical reactions and other inputs can contribute as well.

### Illustrative bands (NOT calibrated)

| Score | Category |
| --- | --- |
| 0–19 | Strong Sell |
| 20–39 | Sell |
| 40–60 | Neutral |
| 61–80 | Buy |
| 81–100 | Strong Buy |

These thresholds are UI placeholders pending historical testing. A score of 72 **does not** mean a 72% chance of making money.

## Horizon selection

The three tabs are **Short-term**, **Mid-term**, and **Long-term**. Changing tabs replaces the complete horizon-specific output, including model, signal classification, estimated duration, level objects, sample size, and confidence/quality information; it must not simply relabel one score.

Working research buckets:
- Short-term: 1–3 trading days; show individual estimated duration such as **2–3 trading days**.
- Mid-term: 2–6 weeks; show an explicitly estimated subwindow when possible.
- Long-term: 1–6 months+; show an explicitly estimated subwindow when possible.
- Forex and crypto trading calendars differ; label exact units appropriately.

**Copy rule:** Present 'Short-term — Bearish — Expected duration 2–3 trading days' rather than an unexplained 'Short-term bearish'. The bias can change before the window ends if new evidence contradicts it.

## Glance example (fictional, not market data)

~~~text
EURUSD                                  1.1738
[ Short-term ]  [ Mid-term ]  [ Long-term ]

           TRADEMETER  72/100
                BUY (green)

SHORT-TERM DIRECTIONAL BIAS: BULLISH
Expected relevance: 2–3 trading days

Levels: support 1.1700 · resistance 1.1760
Invalidation: below 1.1685
Next catalyst: important USD release
As of 14:32 UTC · Data status: Adequate

[⌄ Why this view?]           [Full analysis →]
~~~

For each horizon, levels must be separately derived and explainable. Support/resistance, potential objectives and invalidation are distinct concepts. Neutral results should not invent directional targets.

## Key UX states

Loading; stale feed; inadequate history; missing provider; model recalculating; imminent major event; rumor not verified; bias invalidated; watchlist relevance; insufficient evidence. A stale or failed model must not masquerade as a fresh confident signal.

## Accessibility and polish

Display text categories beside color-coded glow; keyboard and touch operability; semantic disclosure controls; subtle rather than distracting animations; adaptive compact layout; explicit local time and UTC where useful.
