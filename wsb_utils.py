"""
Helper functions for the WallStreetBets pump-and-dump warning project.

Pipeline:  posts -> stock symbols per post -> mentions per (trading day, ticker) -> hype spikes

In plain words:
    1. extract_tickers  finds which real stocks each Reddit post talks about
    2. to_trading_day   puts each post on the trading day someone could act on it
    3. daily_mentions   counts how many posts mentioned each stock each day
    4. first_full_day   finds where the dataset really starts (skips the near-empty beginning)
    5. find_spikes      flags days when a stock suddenly got far more attention than usual

The notebook (project.ipynb) imports this file as `wu` and calls these functions.
"""

import re
import pandas as pd


# STOPWORDS: a "do not count" list
# All-caps words that look like stock symbols but are almost always normal words or slang on Reddit.
# Several are real tickers (ALL = Allstate, ON = ON Semi, NOW = ServiceNow...), but on WSB they're
# nearly always just English. We grew this list by checking the most-mentioned symbols by hand
# and adding anything that clearly wasn't people talking about the company.
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
    # Found in our first spike list: words/fragments that matched real tickers
    "AIN", "AINT", "AWAY", "BEAT", "APP", "APPS", "WAY", "HOLD", "TOO", "DONT", "CANT", "WONT",
    "ITS", "IM", "LETS", "OUR", "GET", "GOT", "ALSO", "BACK", "WORK", "FAST", "NICE", "TRUE",
    # Found in the top-40 check: brokers, trading slang and English words
    "RH",    # Robinhood (the trading app), not Restoration Hardware
    "TD",    # TD Ameritrade (a broker)
    "HF",    # "hedge funds"
    "SI",    # "short interest"
    "RSI",   # Relative Strength Index (a chart indicator)
    "MA",    # usually "moving average"
    "PSA",   # "public service announcement"
    "LINE", "TIME", "HERE", "LOT", "KNOW",
    # The whole market, not a hype stock (still used as the market feature in model_utils)
    "SPY", "QQQ",
    # Found after loosening the spike rule / price download
    "AKA",   # "also known as"
    "PC",    # personal computer
    "PR",    # "press release"
    "ET",    # "Eastern Time"
    "OI",    # "open interest"
    "WANT", "OWN", "IP"   # IP = "intellectual property" ("no IP, no product")
}

# The US stock market runs on New York time, so every post time is converted to it.
US_EASTERN = "America/New_York"


# is_shouting: is this post written mostly in CAPITAL LETTERS?
def is_shouting(text, threshold=0.7):
    """True if most letters in the text are capitals (e.g. "THIS IS THE WAY 🚀")."""
    # Why we need this: in a post like "THIS IS THE WAY WE LIKE THE STOCK", every word
    # looks like a stock symbol. So for shouted posts, we only trust "$GME"-style symbols.

    # Keep only the letters (ignore spaces, numbers, punctuation and emoji).
    letters = [c for c in text if c.isalpha()]

    # Short posts are never treated as shouting, so "GME to the moon $AMC" still counts.
    if len(letters) < 20:
        return False

    # Share of letters that are capitals. More than 70% capitals = shouting.
    return sum(c.isupper() for c in letters) / len(letters) > threshold


# extract_tickers: which real stocks does one post mention?
def extract_tickers(text, valid_tickers):
    """
    Return the set of stock symbols mentioned in one post's text.
    e.g. "GME to the moon $AMC YOLO" -> {"GME", "AMC"}
    Each ticker counts once per post, so spamming a symbol doesn't inflate counts.

    Rules to cut false matches:
      - "$GME" style tickers are always trusted (if real and not a stopword).
      - Plain all-caps words must be 2+ letters (single letters like "C" or "S" need a "$").
      - If the whole post is written in capitals, only "$" tickers count,
        because every word in a shouted post looks like a ticker.
    """
    # Some posts have no text (empty body). Return "no stocks" instead of crashing.
    if not isinstance(text, str):
        return set()

    # Step 1: "$" tickers, like $GME or $tsla. A "$" in front makes it very likely to be a stock,
    # so any case is allowed, then everything is turned into capitals ($tsla -> TSLA).
    dollar = {m for m in re.findall(r"\$([A-Za-z]{1,5})\b", text)}
    dollar = {m.upper() for m in dollar}

    # Step 2: plain capital words, like GME (2 to 5 capital letters).
    # The pattern skips words glued to other letters or an apostrophe,
    # so "AIN'T" doesn't become AIN and "GMEs" doesn't become GME.
    # Skipped entirely for shouted posts (see is_shouting).
    plain = set()
    if not is_shouting(text):
        plain = {m for m in re.findall(r"(?<![$\w'])[A-Z]{2,5}(?![\w'])", text)}

    # Step 3: combine both. Using a set means each stock counts once per post,
    # so one person writing "GME GME GME" counts as one mention.
    tickers = dollar | plain

    # Step 4: keep only real stock symbols (from NASDAQ's list) that aren't on the "do not count" list.
    return {t for t in tickers if t in valid_tickers and t not in STOPWORDS}


# to_trading_day: which trading day does each post belong to?
def to_trading_day(times):
    """
    Map post times to the US trading day on which someone could first act on them.

    - Times are treated as UTC (numbers are read as Unix seconds).
    - Posts at or after 4:00 PM US Eastern (market close) move to the next day.
    - Saturday/Sunday move to Monday.
    Market holidays are NOT handled here; the price merge should roll those forward.
    """
    # Why we need this: the market closes at 4 PM Eastern. A post at 6 PM on Monday couldn't
    # affect Monday's price, so it belongs to Tuesday. Without this, the model would "see"
    # hype that happened after the price it predicts from (data leakage).

    # Step 1: read the times. The "created" column is a number (seconds since 1970, in UTC).
    times = pd.Series(times)
    if pd.api.types.is_numeric_dtype(times):
        ts = pd.to_datetime(times, unit="s", utc=True)
    else:
        ts = pd.to_datetime(times, utc=True)

    # Step 2: convert to New York time, then keep just the date (drop the hour).
    et = ts.dt.tz_convert(US_EASTERN)
    day = et.dt.tz_localize(None).dt.normalize()

    # Step 3: posts at 4 PM or later count toward the next day.
    after_close = et.dt.hour >= 16
    day = day + pd.to_timedelta(after_close.astype(int), unit="D")

    # Step 4: the market is closed on weekends, so roll Saturday (+2 days) and Sunday (+1 day)
    # forward to Monday. (dayofweek: Monday = 0 ... Saturday = 5, Sunday = 6)
    weekday = day.dt.dayofweek
    shift = (weekday == 5) * 2 + (weekday == 6) * 1
    day = day + pd.to_timedelta(shift, unit="D")

    return day


# daily_mentions: how many posts mentioned each stock each day?
def daily_mentions(df, valid_tickers, date_col="timestamp", text_cols=("title", "body")):
    """
    Count how many posts mention each ticker on each trading day.

    df          : posts table
    date_col    : column with the post time ("timestamp" or "created" in the Kaggle WSB data)
    text_cols   : columns searched for tickers (title + body)

    Returns a DataFrame with columns: date, ticker, mentions
    e.g.   2021-03-03 | RKT | 185   (185 posts mentioned RKT that day)
    """
    # Step 1: give every post its trading day.
    dates = to_trading_day(df[date_col]).reset_index(drop=True)

    # Step 2: join each post's title and body into one string, since a ticker can be in either.
    text = df[list(text_cols)].fillna("").astype(str).agg(" ".join, axis=1).reset_index(drop=True)

    # Step 3: go through every post, find its stocks, and write down one (date, ticker) pair
    # per stock. A post on Jan 27 mentioning GME and AMC adds two pairs.
    rows = [
        (d, t)
        for d, txt in zip(dates, text)
        for t in extract_tickers(txt, valid_tickers)
    ]

    # If no post mentioned any stock, return an empty table with the right columns.
    if not rows:
        return pd.DataFrame(columns=["date", "ticker", "mentions"])

    # Step 4: count how many times each (date, ticker) pair appears.
    # That count = the number of posts that mentioned that stock that day.
    mentions = pd.DataFrame(rows, columns=["date", "ticker"])
    return (
        mentions.groupby(["date", "ticker"])
        .size()
        .reset_index(name="mentions")
    )


# first_full_day: where does the dataset really start?
def first_full_day(df, date_col="created", min_posts=100):
    """
    First trading day with at least `min_posts` posts.
    The dataset has a few scattered old posts and then starts properly; anything
    before this day is too sparse to measure "normal" mention levels.
    """
    # Why we need this: our data has one stray post from Sept 2020, then starts properly on
    # Jan 28, 2021. Without this cut, every popular stock looked like it jumped from 0 mentions
    # to hundreds overnight, which created fake spikes (GME, AMC, BB, NOK on Jan 28).

    # Step 1: count posts per trading day, in date order.
    days = to_trading_day(df[date_col])
    counts = days.value_counts().sort_index()

    # Step 2: keep only the "busy" days (at least 100 posts).
    full = counts[counts >= min_posts]

    # Step 3: the earliest busy day is where the data really starts.
    # (If no day has 100 posts, just use the first day.)
    return full.index.min() if len(full) else counts.index.min()


# find_spikes: when did a stock suddenly get far more attention than usual?
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

    We call it with ratio=5, min_mentions=5 in the notebook: at least 5 posts AND at least
    5x the stock's usual attention. Each stock is compared with ITS OWN normal level, because
    popular stocks (GME) are always talked about and small ones (CLOV) rarely are.
    """
    # build a grid with one row per calendar day and one column per stock.
    # Days when a stock had no mentions get a 0 (otherwise they'd be missing, and the
    # average below would skip quiet days and come out too high).
    grid = mentions.pivot_table(
        index="date", columns="ticker", values="mentions", aggfunc="sum", fill_value=0
    )
    grid.index = pd.to_datetime(grid.index)
    grid = grid.asfreq("D", fill_value=0)          # add any missing calendar days as all zeros

    # each stock's "normal" level = its average over the previous 14 days.
    # shift(1) moves everything down one day, so today is left out of its own average.
    # min_periods=window means a stock needs 14 full days of history before it can spike.
    avg_before = grid.shift(1).rolling(window, min_periods=window).mean()

    #  a spike = enough posts AND far above normal.
    # e.g. RKT on Mar 3: 185 posts vs. a normal of about 6.4 a day = about 29x -> spike.
    is_spike = (grid >= min_mentions) & (grid >= ratio * avg_before)

    #turn the grid back into a list of rows and keep only the spike days.
    out = pd.DataFrame({
        "mentions": grid.stack(),
        "avg_before": avg_before.stack(),
        "spike": is_spike.stack(),
    })
    out = out[out["spike"]].drop(columns="spike").reset_index()
    out.columns = ["date", "ticker", "mentions", "avg_before"]
    return out.sort_values(["date", "ticker"]).reset_index(drop=True)