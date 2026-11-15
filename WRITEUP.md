# WSB Hype Drop Warning

**Track:** Finance

*This project is a prototype and is not financial advice.*

## The problem

When a stock suddenly gets hyped on Reddit's r/wallstreetbets, beginners often buy in late, right before the price falls. A teenager with a new investing account has no easy way to tell which hyped stocks are dangerous. We built a tool that warns them before they buy into the hype.

## What we built

**In:** a Reddit hype spike (a stock suddenly getting at least 5 posts in a day and 5× its usual attention).
**Out:** the chance the stock falls 10% or more within the next 5 trading days, a warning if that chance is 40% or higher, and plain-language reasons compared with past spikes (for example, *"Very jumpy stock: it usually moves about 38% a day, more than any hype spike we studied"*).

A beginner who sees a stock trending on Reddit could check it first: a warning means "be careful", no warning means the risk looks lower.

## What we added

Our own idea. It sits in the Finance track's goal of helping a person make a safer money decision. We also asked our own question: once a stock is hyped, does the Reddit hype itself predict a drop, or is it just how volatile the stock already is?

## How it works

**Data:** 53,187 r/wallstreetbets posts from Jan 28 to Aug 16, 2021 (Kaggle, via the OpenML mirror), NASDAQ's list of 13,285 US stock symbols, and daily prices from Yahoo Finance.

- We found stock symbols in each post, filtering out slang and English words that match real tickers (`RH` = Robinhood, `HF` = hedge funds, `ALL`, `IP` = intellectual property…), and moved posts made after the 4 PM market close to the next trading day.
- We flagged 123 hype spikes, then kept one spike per stock per week (one hype wave = one example): **82 examples**.
- We removed fake spikes caused by the dataset starting on Jan 28, when every popular stock looked like it jumped from zero mentions.

**Model:** a random forest using 8 clues per spike: how sudden the hype was, post count, price change over 5 and 20 days, trading volume, volatility, share price and the S&P 500's move. We chose it because it handles a small dataset and mixed clues well. We trained on Feb–May and tested on Jun–Aug, never splitting randomly. We chose the 40% warning cutoff on the training months only, before looking at the test.

## Results

On the 24 test spikes (8 followed by a sharp drop):

| Method | Warnings | Drops caught | False alarms |
| --- | --- | --- | --- |
| Always warn (baseline) | 24 | 8 of 8 | 16 |
| Warn if the stock is volatile (baseline) | 7 | 6 of 8 | 1 |
| **Our model (warn at 40%+)** | 16 | **8 of 8** | 8 |

Our model caught every drop with half the false alarms of always warning. The best simple rule gave fewer false alarms but missed 2 drops. For a beginner, a missed drop costs real money while a false alarm only costs a missed gain, so we favour catching drops.

**Main finding:** how volatile the stock already is explains most drops after hype. Sorting spikes by volatility alone almost matches our model; adding the Reddit clues caught about one more drop out of eight. The result held across 10 random seeds, and a model trained on scrambled answers did far worse (PR-AUC 0.48 vs. 0.94), so it isn't leakage.

**Where it fails:** it relies heavily on volatility. It nearly missed ASO, a calm stock that fell just over 10% (43% risk), and gave false alarms on popular, moderately jumpy stocks like PLTR and AMD that didn't drop. On the training months it was only slightly better than always warning, so our test result is probably optimistic.

## What we'd do next

- Use live Reddit data from Reddit's API, so the tool can warn about new hype spikes as they happen.
- Test on other years and calmer markets to see whether the patterns hold outside the 2021 meme-stock mania.

## Sources

- Data: [Reddit WallStreetBets Posts](https://www.kaggle.com/datasets/gpreda/reddit-wallstreetsbets-posts) (Gabriel Preda, Kaggle), loaded from [OpenML, ID 43373](https://www.openml.org/d/43373) · [NASDAQ Trader symbol directory](https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt) · Yahoo Finance prices via [yfinance](https://github.com/ranaroussi/yfinance)
- Libraries: [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [scikit-learn](https://scikit-learn.org/), [Gradio](https://www.gradio.app/)
- AI tools: [Claude](https://claude.ai) (Anthropic), used to help write and debug code, check our pipeline for data leakage, and explain concepts. Our team reviewed and understands every part of the project.