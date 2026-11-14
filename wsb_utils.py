"""
Helper functions for the WallStreetBets pump-and-dump warning project.

Pipeline:  posts -> stock symbols per post -> mentions per (trading day, ticker) -> hype spikes
"""

import re
import pandas as pd

# All-caps words that look like stock symbols but are almost always normal words or slang on Reddit.
# Several are real tickers (ALL = Allstate, ON = ON Semi, NOW = ServiceNow...), but on WSB they're
# nearly always just English. Extend this after checking the top-50 most-mentioned tickers.
STOPWORDS = {
    # Reddit / finance slang
    "DD", "YOLO", "WSB", "OP", "EDIT", "TLDR", "IMO", "IMHO", "LOL", "LMAO", "WTF", "FYI",
    "ATH", "ATL", "EOD", "EOW", "ETF", "IPO", "SEC", "CEO", "CFO", "CTO", "USA", "USD", "EU", "UK",
    "MOON", "HODL", "BUY", "SELL", "HOLD", "CALL", "CALLS", "PUT", "PUTS", "PUMP", "DUMP", "APE",
    "APES", "REKT", "LONG", "SHORT", "FUD", "FOMO", "GAIN", "GAINS", "LOSS", "RIP", "OTM", "ITM",
    "IV", "PT", "EPS", "PE", "AH", "PM", "AM", "EV", "TV", "AI", "IRA", "ROTH", "GG", "OK",
    # Common English words that are also tickers
    "I", "A", "AN", "AND", "ARE", "AS", "AT", "BE", "BIG", "BY", "CAN", "DO", "FOR", "FROM", "FUN",
    "GO", "GOOD", "HAS", "HE", "HOME", "IN", "INTO", "IS", "IT", "JUST", "LOVE", "ME", "MY", "NEW",
    "NEXT", "NO", "NOW", "OF", "ON", "ONE", "ONTO", "OPEN", "OR", "OUT", "PLAY", "REAL", "SAVE",
    "SEE", "SO", "TELL", "THAT", "THE", "THIS", "TO", "TWO", "UP", "US", "VERY", "WE", "WITH",
    "ALL", "ANY", "ELSE", "EVER", "LIFE", "LOW", "HIGH", "MAN", "RUN", "WELL", "YOU",
}

US_EASTERN = "America/New_York"


def extract_tickers(text, valid_tickers):
    """
    Return the set of stock symbols mentioned in one post's text.
    e.g. "GME to the moon $AMC YOLO" -> {"GME", "AMC"}
    Each ticker counts once per post, so spamming a symbol doesn't inflate counts.
    """
    if not isinstance(text, str):
        return set()

    # 1-5 letter uppercase words, with or without a leading '$'
    raw_matches = re.findall(r"\$?\b[A-Z]{1,5}\b", text)
    tickers = {m.lstrip("$") for m in raw_matches}

    return {t for t in tickers if t in valid_tickers and t not in STOPWORDS}


def to_trading_day(times):
    """
    Map post times to the US trading day on which someone could first act on them.

    - Times are treated as UTC (numbers are read as Unix seconds).
    - Posts at or after 4:00 PM US Eastern (market close) move to the next day.
    - Saturday/Sunday move to Monday.
    Market holidays are NOT handled here; the price merge should roll those forward.
    """
    times = pd.Series(times)
    if pd.api.types.is_numeric_dtype(times):
        ts = pd.to_datetime(times, unit="s", utc=True)
    else:
        ts = pd.to_datetime(times, utc=True)

    et = ts.dt.tz_convert(US_EASTERN)
    day = et.dt.tz_localize(None).dt.normalize()

    after_close = et.dt.hour >= 16
    day = day + pd.to_timedelta(after_close.astype(int), unit="D")

    # Roll Saturday (+2) and Sunday (+1) forward to Monday
    weekday = day.dt.dayofweek
    shift = (weekday == 5) * 2 + (weekday == 6) * 1
    day = day + pd.to_timedelta(shift, unit="D")

    return day


def daily_mentions(df, valid_tickers, date_col="timestamp", text_cols=("title", "body")):
    """
    Count how many posts mention each ticker on each trading day.

    df          : posts table
    date_col    : column with the post time ("timestamp" or "created" in the Kaggle WSB data)
    text_cols   : columns searched for tickers (title + body)

    Returns a DataFrame with columns: date, ticker, mentions
    """
    dates = to_trading_day(df[date_col]).reset_index(drop=True)

    text = df[list(text_cols)].fillna("").astype(str).agg(" ".join, axis=1).reset_index(drop=True)

    rows = [
        (d, t)
        for d, txt in zip(dates, text)
        for t in extract_tickers(txt, valid_tickers)
    ]

    if not rows:
        return pd.DataFrame(columns=["date", "ticker", "mentions"])

    mentions = pd.DataFrame(rows, columns=["date", "ticker"])
    return (
        mentions.groupby(["date", "ticker"])
        .size()
        .reset_index(name="mentions")
    )


def find_spikes(mentions, ratio=5, min_mentions=10, window=14):
    """
    Flag hype days for each ticker.

    A day is a spike if:
      - mentions >= min_mentions, AND
      - mentions >= ratio x the average over the previous `window` calendar days
        (days with no mentions count as 0; today is excluded from its own average)

    The first `window` days of the dataset are only used as history, so every ticker
    doesn't look "new" at the start.

    Returns a DataFrame with columns: date, ticker, mentions, avg_before
    """
    # Grid: one row per calendar day, one column per ticker, 0 where there were no mentions
    grid = mentions.pivot_table(
        index="date", columns="ticker", values="mentions", aggfunc="sum", fill_value=0
    )
    grid.index = pd.to_datetime(grid.index)
    grid = grid.asfreq("D", fill_value=0)

    avg_before = grid.shift(1).rolling(window, min_periods=window).mean()

    is_spike = (grid >= min_mentions) & (grid >= ratio * avg_before)

    out = pd.DataFrame({
        "mentions": grid.stack(),
        "avg_before": avg_before.stack(),
        "spike": is_spike.stack(),
    })
    out = out[out["spike"]].drop(columns="spike").reset_index()
    out.columns = ["date", "ticker", "mentions", "avg_before"]
    return out.sort_values(["date", "ticker"]).reset_index(drop=True)