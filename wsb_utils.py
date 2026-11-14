import re
import pandas as pd

# Stopwords to filter out non-stock all-caps words commonly found on Reddit
STOPWORDS = {
    "I", "A", "DD", "YOLO", "CEO", "CFO", "IPO", "SEC", "WSB", "OP", "EDIT", 
    "ATH", "ATL", "ETF", "USA", "USD", "IT", "IS", "AN", "BE", "AS", "AT", 
    "BY", "FOR", "FROM", "IN", "INTO", "OF", "ON", "ONTO", "OR", "THAT", 
    "THE", "THIS", "TO", "WITH", "MOON", "HODL", "BUY", "SELL", "CALL", 
    "PUT", "PUMP", "DUMP", "APE", "REKT", "LONG", "SHORT", "FUD", "FOMO"
}

def extract_tickers(text, valid_tickers):
    """
    Finds unique, valid stock symbols in a single post's text.
    """
    if not isinstance(text, str):
        return set()
    
    # Find 1-5 letter uppercase words with optional '$' prefix
    raw_matches = re.findall(r"\$?\b[A-Z]{1,5}\b", text)
    
    # Clean '$' prefix and collect unique symbols
    tickers = {match.lstrip("$") for match in raw_matches}
    
    # Keep only symbols that are valid and not in stopwords
    valid_found = {t for t in tickers if t in valid_tickers and t not in STOPWORDS}
    
    return valid_found

def daily_mentions(df, valid_tickers):
    """
    Counts mentions per stock per day across all posts.
    Expected df columns: 'date', 'title', 'body'
    """
    # Ensure date is normalized to date objects
    if 'date' in df.columns:
        df = df.copy()
        df['date'] = pd.to_datetime(df['date']).dt.date
    
    rows = []
    
    # Combine title and body to search everywhere (handling NaN safely)
    titles = df['title'].fillna('')
    bodies = df['body'].fillna('')
    combined_texts = titles + " " + bodies
    
    for date, text in zip(df['date'], combined_texts):
        tickers = extract_tickers(text, valid_tickers)
        for ticker in tickers:
            rows.append({"date": date, "ticker": ticker})
            
    if not rows:
        return pd.DataFrame(columns=["date", "ticker", "mentions"])
        
    mentions_df = pd.DataFrame(rows)
    
    # Group by date and ticker, then count occurrences
    mentions_counts = (
        mentions_df.groupby(["date", "ticker"])
        .size()
        .reset_index(name="mentions")
    )
    
    return mentions_counts

def find_spikes(mentions, ratio=5, min_mentions=10, window=14):
    """
    Flags hype days where mentions exceed a rolling average baseline.
    """
    # Ensure mentions table is sorted chronologically by date per ticker
    mentions = mentions.sort_values(["ticker", "date"]).copy()
    
    # Calculate rolling average over the window, shifting by 1 to exclude today
    mentions["avg_before"] = (
        mentions.groupby("ticker")["mentions"]
        .transform(lambda x: x.shift(1).rolling(window=window, min_periods=1).mean())
        .fillna(0)
    )
    
    # A day is a spike if it meets minimum mentions and ratio criteria
    is_spike = (
        (mentions["mentions"] >= min_mentions) & 
        (mentions["mentions"] >= mentions["avg_before"] * ratio)
    )
    
    spike_rows = mentions[is_spike].copy()
    
    return spike_rows