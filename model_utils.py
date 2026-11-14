"""
Model-side helpers: prices -> crash labels + features for each hype spike.
"""

import numpy as np
import pandas as pd

CRASH_DROP = -0.20   # a crash = price falls 20%+ below the entry price...
HORIZON = 5          # ...at any point in the next 5 trading days
LOOKBACK = 20        # trading days of history needed for the price features


def get_prices(tickers, start, end):
    """
    Download daily prices from yfinance. Returns {ticker: DataFrame[Open, High, Low, Close, Volume]}.
    Tickers yfinance can't find (often delisted) are left out. Report how many in your write-up.
    """
    import yfinance as yf

    raw = yf.download(sorted(set(tickers)), start=start, end=end,
                      auto_adjust=True, group_by="ticker", progress=False, threads=True)
    prices = {}
    for tk in set(tickers):
        if tk in raw.columns.get_level_values(0):
            p = raw[tk].dropna(how="all")
            if len(p) > LOOKBACK + HORIZON:
                prices[tk] = p
    return prices


def build_dataset(spikes, prices, market="SPY"):
    """
    One row per spike that has enough price history before and after it.

    Entry price = Close on the spike's trading day (posts after the close were already
    moved to the next day, so everything counted happened before this price).
    If the spike date is a market holiday, the next trading day is used.

    Label `crashed` = 1 if the lowest Low over the next HORIZON trading days
    is CRASH_DROP or more below the entry price.

    Price features only use data up to and including the spike day.
    """
    mkt = prices.get(market)
    rows = []

    for r in spikes.itertuples(index=False):
        p = prices.get(r.ticker)
        if p is None:
            continue

        i = p.index.searchsorted(pd.Timestamp(r.date))   # first trading day >= spike date
        if i < LOOKBACK or i + HORIZON >= len(p):
            continue                                       # not enough history or future

        close, low, vol = p["Close"].to_numpy(), p["Low"].to_numpy(), p["Volume"].to_numpy()
        entry = close[i]
        future_low = low[i + 1: i + 1 + HORIZON].min()
        daily_ret = np.diff(close[i - LOOKBACK: i + 1]) / close[i - LOOKBACK: i]

        row = {
            "date": p.index[i],
            "ticker": r.ticker,
            # hype features
            "mentions": r.mentions,
            "log_mentions": np.log1p(r.mentions),
            "spike_ratio": r.mentions / max(r.avg_before, 0.1),
            # price features (all known at the spike day's close)
            "ret_5d": entry / close[i - 5] - 1,
            "ret_20d": entry / close[i - LOOKBACK] - 1,
            "volume_ratio": vol[i] / max(vol[i - LOOKBACK: i].mean(), 1),
            "volatility_20d": daily_ret.std(),
            "log_price": np.log(entry),
            # outcome (NOT a feature)
            "min_future_ret": future_low / entry - 1,
        }

        if mkt is not None:
            j = mkt.index.searchsorted(p.index[i])
            if 5 <= j < len(mkt):
                mc = mkt["Close"].to_numpy()
                row["market_ret_5d"] = mc[j] / mc[j - 5] - 1

        rows.append(row)

    data = pd.DataFrame(rows)
    if not data.empty:
        data["crashed"] = (data["min_future_ret"] <= CRASH_DROP).astype(int)
    return data


FEATURES = ["log_mentions", "spike_ratio", "ret_5d", "ret_20d",
            "volume_ratio", "volatility_20d", "log_price", "market_ret_5d"]