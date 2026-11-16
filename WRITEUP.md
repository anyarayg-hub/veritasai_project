# WSB Hype Drop Warning

Track: Finance

This is a prototype and should not be construed as financial advice. All the details, tables and code are in the [README](README.md).

## The problem

Beginners buy stocks because they're suddenly all the rage on r/wallstreetbets. Then they end up watching them go down. The issue is they've got no quick way of working out which of the stocks that are all the rage are actually dangerous. That's the problem we are going to solve.

## What we built

We made a tool. You give it a hype spike and it tells you how likely that stock is to drop 10% or more in a week. It gives you a warning and the plain language reasons why. Pick a real spike, get the warning. We added a feature where you can see what actually happened to the stock afterwards, and whether our model predicted correctly.

## What we added

We went back to the bigger question of whether it's the Reddit hype that's causing the drop or whether it's just that the stock is already quite jumpy. We also looked at whether the model is more harsh on the cheap stocks.

## How it works

We took 53,187 r/wallstreetbets posts from 2021 and turned them into 80 hype spikes. Each spike got 8 clues from Reddit and price data. We trained a random forest on the earlier months, the later months were tested on (the model had never seen them). The warning cutoff was chosen blind, no peeking at the test results.

## Results

A simple rule worked okay (just check volatility and if it's high then issue a warning) and that picked up 6 of the 8 sharp drops in the test months. Our model picked up all 8. The catch is half of its warnings were false alarms. Volatility explains the majority of the drops. Reddit hype adds a bit, but not a great deal. The model is very much based on volatility so it will issue a lot of warnings on the popular stocks that are fairly volatile (e.g. PLTR). One other thing: the test months were easier than the training months.

## How we built it

1. Found the stocks in each post. Matched the capital words and $ tickers against NASDAQ's list of real symbols and filtered out the slang and words which are also tickers.
2. Counted posts per stock per day, with any posts made after the 4 PM market close or on a weekend being carried forward to the next trading day.
3. Flagged hype spikes: at least 5 posts and at least 5x the stock's normal level of attention over the previous two weeks.
4. Downloaded the prices and calculated 8 clues for each spike, plus whether it had fallen 10% or more in 5 trading days.
5. Split by date, scored simple rules and trained a logistic regression and a random forest.
6. Checked the results: 10 random seeds, scrambled answers, with and without the Reddit clues, and cheap vs. pricier stocks.
7. Chose the warning cutoff on the training months and then put together a small Gradio website which explains each warning.

## Challenges and what failed

- Words being treated as stocks. "RH" (Robinhood), "HF" (hedge funds), "IP" (intellectual property) and "AIN'T" were all treated as tickers initially. We found them by manually checking the most frequently mentioned symbols on several occasions.
- Fake spikes. Our initial run found 209 spikes, many of which were obviously fake. The data set only starts on 28th January 2021 so every single one of the popular stocks looked like they'd spiked from zero.
- Too few examples. The data plummets from around 4,200 posts a day in January to around 80 by summer. Our very strict first rule only picked up 46 spikes so we relaxed it.
- Too few crashes. Only 7 of the 80 spikes fell by 20%, too few to really test properly. We therefore used a 10% line (which we had chosen prior to training).
- Mistakes in our own pipeline. A cell running out of order trained the model on the wrong labels. An early version of our spike rule simply didn't account for quiet days. Both of these we caught by looking at results that looked wrong.
- Setup and teamwork: missing libraries, notebooks saved as the wrong file type, Git merge conflicts and the website failing inside Codespaces until we got the website connection sorted.

## What we'd improve with more time

- Live Reddit data so it can alert you to new spikes as they occur.
- More timeframes to see if the patterns hold outside of the 2021 meme stock madness.
- More examples so the results aren't so dependent on a few lucky or unlucky cases.
- Fewer false alarms, for example with clues about company size or news, and a model less dependent on volatility.
- A fairness check with more data to ensure the model isn't being unduly harsh on the cheap stocks.

## Sources

Listed in full in the [README](README.md). Data: [Reddit WallStreetBets Posts](https://www.kaggle.com/datasets/gpreda/reddit-wallstreetsbets-posts) (Kaggle / [OpenML 43373](https://www.openml.org/d/43373)), the [NASDAQ symbol directory](https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt) and Yahoo Finance via [yfinance](https://github.com/ranaroussi/yfinance). AI tool: [Claude](https://claude.ai) (Anthropic) used to assist with writing and debugging code and with explaining concepts.