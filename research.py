"""Point-in-time, descriptive event studies for the research terminal.

This module does not make price predictions. It measures what happened after
historical, source-linked events using recorded *subsequent* price bars.
"""
from bisect import bisect_right
from datetime import datetime, timezone
from statistics import mean, median


OBSERVATIONS = {"short": 3, "mid": 10, "long": 30}
MIN_SAMPLE = 8


def parse_utc(value):
    """Refuse naive timestamps; normalize RFC3339 offsets to UTC."""
    stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("Timestamp requires a timezone offset")
    return stamp.astimezone(timezone.utc)


def quantile(sorted_values, fraction):
    """Linear-interpolated sample quantile; input must be sorted."""
    n = len(sorted_values)
    if not n:
        return None
    position = (n - 1) * fraction
    left = int(position)
    alpha = position - left
    if left + 1 >= n:
        return sorted_values[-1]
    return sorted_values[left] * (1 - alpha) + sorted_values[left + 1] * alpha


def event_study(conn, symbol, horizon, *, demo=True, as_of=None, category=None):
    """Descriptive forward returns after distinct historical events.

    Price at entry = first *recorded bar strictly after* event publication time.
    Exit = N bars after entry; future-unavailable outcomes are excluded.
    No information after as_of is used, and repeated coverage of an
    event_key counts only once.
    """
    if horizon not in OBSERVATIONS:
        raise ValueError("Unknown horizon")
    cutoff = parse_utc(as_of or datetime.now(timezone.utc).isoformat())
    flag = int(demo)
    bars = conn.execute(
        "SELECT ts, close FROM bars WHERE symbol=? AND demo=? ORDER BY ts",
        (symbol, flag),
    ).fetchall()
    prices = []
    times = []
    for row in bars:
        time = parse_utc(row["ts"])
        if time > cutoff:
            continue
        price = float(row["close"])
        if price > 0:
            times.append(time)
            prices.append(price)
    events = conn.execute(
        "SELECT e.event_key, e.kind, e.ts "
        "FROM evidence v JOIN events e ON e.id=v.event_id "
        "WHERE v.symbol=? AND e.demo=? AND v.demo=? ORDER BY e.ts",
        (symbol, flag, flag),
    ).fetchall()
    seen = set()
    moves = []
    period = OBSERVATIONS[horizon]
    for event in events:
        if category and event["kind"] != category:
            continue
        key = event["event_key"]
        if key in seen:
            continue
        seen.add(key)
        event_time = parse_utc(event["ts"])
        if event_time > cutoff:
            continue
        entry = bisect_right(times, event_time)
        end = entry + period
        if end >= len(prices):
            continue
        returns = (prices[end] / prices[entry] - 1) * 100
        moves.append(returns)
    ordered = sorted(moves)
    n = len(moves)
    sufficient = n >= MIN_SAMPLE
    return {
        "symbol": symbol,
        "horizon": horizon,
        "event_category": category or "all",
        "method": "entry: first subsequent stored close; exit: N stored bars later",
        "observations_forward": period,
        "count": n,
        "min_sample": MIN_SAMPLE,
        "sufficient": sufficient,
        "mean_return_pct": round(mean(moves), 4) if n else None,
        "median_return_pct": round(median(moves), 4) if n else None,
        "positive_fraction": round(sum(v > 0 for v in moves) / n, 4) if n else None,
        "p25_return_pct": round(quantile(ordered, .25), 4) if n else None,
        "p75_return_pct": round(quantile(ordered, .75), 4) if n else None,
        "sample_returns_pct": [round(v, 4) for v in moves[-30:]],
        "demo": bool(demo),
        "status": ("SYNTHETIC EXAMPLE — NOT VALIDATED" if demo
                   else "HISTORICAL DESCRIPTION — NOT FORECAST") if sufficient
                  else "INSUFFICIENT HISTORICAL MATCHES",
        "as_of": cutoff.isoformat(),
    }
